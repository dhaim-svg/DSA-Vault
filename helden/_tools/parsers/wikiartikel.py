"""Wiki articles/sections rendered to safe HTML for the Zauber tab (read at render time)."""
import logging
import re
from pathlib import Path, PureWindowsPath
from typing import Callable, Iterable

import mistune
import yaml

from .held import WIKILINK_RE, parse_frontmatter, split_sections, strip_wikilink

log = logging.getLogger(__name__)

# Whitelist root below the vault: only DSA rule articles are ever read.
WIKI_ROOT = ('wiki', 'dsa-4.1')

META_FIELDS = [('probe', 'Probe'), ('kosten', 'Kosten'),
               ('zauberdauer', 'Zauberdauer'), ('wirkungsdauer', 'Wirkungsdauer')]

_H1_RE = re.compile(r'^#[ \t]+(?P<titel>.+?)(?:[ \t]+#+)?[ \t]*$', re.M)
_QUELLE_LINE_RE = re.compile(r'\s*>\s*\*\*Quelle')
_QUELLE_TEXT_RE = re.compile(r'\s*>\s*\*\*Quelle:?\*\*:?(?P<text>.*)')

# escape=True is mandatory: templates run with autoescape=False, so raw wiki HTML must not pass through.
_MARKDOWN = mistune.create_markdown(escape=True, plugins=['table'])


def _text(v) -> str:
    return '' if v is None else str(v).strip()


def _resolve_article(vault_root: Path, wiki_path: str) -> Path | None:
    """Map a wiki_path to an existing .md file inside wiki/dsa-4.1/, else None."""
    if not wiki_path or '\\' in wiki_path:
        return None
    path = wiki_path.partition('#')[0]
    if PureWindowsPath(path).anchor:  # '/x', 'C:/x', 'C:x' — vault-relative paths only
        return None
    try:
        allowed = vault_root.joinpath(*WIKI_ROOT).resolve()
        candidate = (vault_root / (path + '.md')).resolve()
        if candidate.is_relative_to(allowed) and candidate.is_file():
            return candidate
    except (OSError, ValueError):
        pass
    return None


def _split_title(body: str) -> tuple[str | None, str]:
    """Cut the first H1 and the '> **Quelle:**' block right behind it out of body."""
    m = _H1_RE.search(body)
    if not m:
        return None, body
    lines = body[m.end():].split('\n')
    i = 1  # lines[0] is the rest of the H1 line
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and _QUELLE_LINE_RE.match(lines[i]):
        while i < len(lines) and lines[i].lstrip().startswith('>'):
            i += 1
    else:
        i = 1
    return m.group('titel'), body[:m.start()] + '\n'.join(lines[i:])


def _link_wikilinks(body: str, link_fn: Callable[[str], str]) -> str:
    """[[pfad#anker|Text]] -> Markdown link; the URL goes in <...> so parentheses are harmless."""
    def repl(m):
        path, display = m.group(1).strip(), m.group(2)
        text = display.strip() if display else path.partition('#')[0].split('/')[-1].replace('-', ' ')
        text = re.sub(r'([\\\[\]])', r'\\\1', text)
        url = link_fn(path).replace('<', '%3C').replace('>', '%3E')
        return f'[{text}](<{url}>)'
    return WIKILINK_RE.sub(repl, body)


def _head_quelle(body: str) -> str:
    """Text of the first '> **Quelle:** …' line before the first '## ' heading, else ''.

    Only the head block counts (the quote under the H1); a Quelle line inside a later section is ordinary text.
    The line is cleaned for display: wikilinks reduced to their text, markdown asterisks and backticks removed.
    """
    for line in body.split('\n'):
        if line.startswith('## '):
            break
        m = _QUELLE_TEXT_RE.match(line)
        if m:
            return re.sub(r'[*`]', '', strip_wikilink(m.group('text'))).strip()
    return ''


def _quelle(fm: dict, body: str) -> str:
    """Frontmatter quelle (+ seite) wins; without one, the head-block line (which carries its page itself)."""
    quelle, seite = _text(fm.get('quelle')), _text(fm.get('seite'))
    if not quelle:
        return _head_quelle(body)
    return f'{quelle} S. {seite}' if seite else quelle


def _fallback_title(fm: dict, wiki_path: str) -> str:
    name, alt = _text(fm.get('name')), _text(fm.get('alternativname'))
    if name:
        return f'{name} ({alt})' if alt else name
    return wiki_path.partition('#')[0].split('/')[-1]


def _short(exc: Exception) -> str:
    """One-line error text; YAML errors otherwise span several lines with a source excerpt."""
    mark = getattr(exc, 'problem_mark', None)
    detail = getattr(exc, 'problem', None) or str(exc)
    return f'{detail} (Zeile {mark.line + 1})' if mark else detail


def _read_article(file: Path) -> tuple[dict, str]:
    text = file.read_text(encoding='utf-8')
    if text.startswith('---') and len(text.split('---', 2)) < 3:
        raise ValueError('frontmatter is not closed')
    fm, body = parse_frontmatter(text)
    if not isinstance(fm, dict):
        raise ValueError('frontmatter is not a mapping')
    return fm, body


def _section(body: str, anchor: str) -> str | None:
    """Content of the '## <anchor>' section (heading line and closing '---' rule cut off), else None.

    The anchor is only a dict key here, never part of a file path.
    Limits inherited from split_sections: a '## ' line inside a fenced code block also splits,
    and repeated headings are concatenated (neither occurs in the SF group articles).
    """
    for title, content in split_sections(body, 2).items():
        if title != '__pre__' and title == anchor:
            lines = content.split('\n')
            while lines and not lines[-1].strip():
                lines.pop()
            if lines and lines[-1].strip() == '---':  # separator to the next heading, not part of the section
                lines.pop()
            return '\n'.join(lines).strip('\n')
    return None


def _load_one(file: Path, wiki_path: str, link_fn: Callable[[str], str]) -> dict | None:
    try:
        fm, body = _read_article(file)
    except (OSError, UnicodeDecodeError, ValueError, yaml.YAMLError) as exc:
        log.warning('Wiki-Artikel %s nicht lesbar: %s', wiki_path, _short(exc))
        return None
    quelle = _quelle(fm, body)  # before the section cut: the source sits in the head block, not in the section
    anchor = wiki_path.partition('#')[2].strip()
    if anchor:
        section = _section(body, anchor)
        if not section:  # None = heading missing, '' = heading without content
            log.warning('Wiki-Artikel %s: Abschnitt %r nicht gefunden oder leer', wiki_path, anchor)
            return None
        titel, body = anchor, section
    else:
        titel, body = _split_title(body)
    try:
        html = _MARKDOWN(_link_wikilinks(body, link_fn))
    except Exception as exc:  # one broken article must not take the whole dashboard down
        log.warning('Wiki-Artikel %s nicht renderbar: %s', wiki_path, _short(exc))
        return None
    if anchor:  # section of a group file: no per-section meta
        meta = []
    else:
        meta = [{'label': label, 'wert': _text(fm.get(key))}
                for key, label in META_FIELDS if _text(fm.get(key))]
    return {
        'titel': _text(titel) or _fallback_title(fm, wiki_path),
        'quelle': quelle,
        'meta': meta,
        'html': html,
    }


def load_wiki_artikel(vault_root: Path, wiki_paths: Iterable[str],
                      link_fn: Callable[[str], str]) -> dict[str, dict]:
    """Map each wiki_path (unchanged) to {'titel','quelle','meta','html'}; unreadable/missing paths get no entry.

    'pfad#anker' loads only the '## anker' section (titel = anchor, meta empty); a missing section gets no entry.
    Text fields are raw (the template escapes them); only 'html' is already HTML.
    link_fn(path[#anker]) builds the URL for [[wikilinks]] (injected: rendering imports this module).
    """
    result: dict[str, dict] = {}
    for wiki_path in wiki_paths:
        if wiki_path in result:
            continue
        file = _resolve_article(vault_root, wiki_path)
        if file is None:
            continue
        article = _load_one(file, wiki_path, link_fn)
        if article is not None:
            result[wiki_path] = article
    return result
