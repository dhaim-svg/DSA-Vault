"""Wiki spell articles rendered to safe HTML for the Zauber tab (read at render time)."""
import logging
import re
from pathlib import Path, PureWindowsPath
from typing import Callable, Iterable

import mistune
import yaml

from .held import WIKILINK_RE, parse_frontmatter

log = logging.getLogger(__name__)

# Whitelist root below the vault: only DSA rule articles are ever read.
WIKI_ROOT = ('wiki', 'dsa-4.1')

META_FIELDS = [('probe', 'Probe'), ('kosten', 'Kosten'),
               ('zauberdauer', 'Zauberdauer'), ('wirkungsdauer', 'Wirkungsdauer')]

_H1_RE = re.compile(r'^#[ \t]+(?P<titel>.+?)(?:[ \t]+#+)?[ \t]*$', re.M)
_QUELLE_LINE_RE = re.compile(r'\s*>\s*\*\*Quelle')

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


def _quelle(fm: dict) -> str:
    quelle, seite = _text(fm.get('quelle')), _text(fm.get('seite'))
    if not quelle:
        return ''
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


def _load_one(file: Path, wiki_path: str, link_fn: Callable[[str], str]) -> dict | None:
    try:
        fm, body = parse_frontmatter(file.read_text(encoding='utf-8'))
        if not isinstance(fm, dict):
            raise ValueError('frontmatter is not a mapping')
    except (OSError, UnicodeDecodeError, yaml.YAMLError, ValueError) as exc:
        log.warning('Wiki-Artikel %s nicht lesbar: %s', wiki_path, _short(exc))
        return None
    titel, body = _split_title(body)
    return {
        'titel': _text(titel) or _fallback_title(fm, wiki_path),
        'quelle': _quelle(fm),
        'meta': [{'label': label, 'wert': _text(fm.get(key))}
                 for key, label in META_FIELDS if _text(fm.get(key))],
        'html': _MARKDOWN(_link_wikilinks(body, link_fn)),
    }


def load_zauber_artikel(vault_root: Path, wiki_paths: Iterable[str],
                        link_fn: Callable[[str], str]) -> dict[str, dict]:
    """Map each wiki_path (unchanged) to {'titel','quelle','meta','html'}; unreadable/missing paths get no entry.

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
