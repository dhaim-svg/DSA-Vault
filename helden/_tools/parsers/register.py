"""Deduplicated NSC/Orte register built from the 'Neue NSCs / Orte' session sections."""
import re
import unicodedata

from .held import split_sections, strip_wikilink

SECTION_KEY = 'neue nscs / orte'

_ENTRY_RE = re.compile(r'^-\s+\*\*(?P<name>.+?)\*\*(?P<rest>.*)$')
# Dashes are separators on their own; a hyphen only counts when followed by whitespace/end.
_SEP_RE = re.compile(r'^\s*(?:[—–]|-(?=\s|$))\s*')


def fold(s: str) -> str:
    """Case- and diacritics-insensitive form used for search text and sorting (ä→a, ß→ss)."""
    decomposed = unicodedata.normalize('NFKD', s.casefold())
    return ''.join(c for c in decomposed if not unicodedata.combining(c))


def _norm_key(s: str) -> str:
    """Normalize a heading for comparison: casefold, collapse whitespace, ' / ' spacing."""
    return re.sub(r'\s*/\s*', ' / ', ' '.join(s.casefold().split()))


def _read_group(rest: str) -> tuple[str, str] | None:
    """Split a leading balanced '(...)' group off rest; None if the parenthesis is never closed."""
    depth = 0
    for i, ch in enumerate(rest):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
            if depth == 0:
                return rest[1:i], rest[i + 1:]
    return None


def _parse_rest(rest: str) -> tuple[bool, str, str]:
    """Split the text behind the name into (unsicher, qualifier, description)."""
    unsicher = False
    qualifiers: list[str] = []
    rest = rest.lstrip()
    while rest.startswith('('):
        group = _read_group(rest)
        if group is None:
            break  # unclosed: leave the remainder to the description
        content, rest = group
        content = content.strip()
        rest = rest.lstrip()
        if content == '?':
            unsicher = True
        elif content:
            qualifiers.append(content)
            if '(?)' in content:
                unsicher = True
    text = strip_wikilink(_SEP_RE.sub('', rest, count=1))
    return unsicher, ', '.join(qualifiers), text


def _parse_entries(text: str) -> list[tuple[str, bool, str, str]]:
    """Parse top-level '- **Name** ...' bullets into (name, unsicher, qualifier, description)."""
    entries = []
    for line in text.splitlines():
        m = _ENTRY_RE.match(line)
        if not m:
            continue
        unsicher, qualifier, desc = _parse_rest(m.group('rest'))
        entries.append((strip_wikilink(m.group('name')), unsicher, qualifier, desc))
    return entries


def build_register(sessions: list[dict]) -> dict:
    """Aggregate the 'Neue NSCs / Orte' sections of all sessions into a deduplicated register."""
    buckets: dict[str, dict[str, dict]] = {'nscs': {}, 'orte': {}}
    for session in sessions:
        nr = session.get('nr')
        nr = '' if nr is None else str(nr).strip()
        sektionen = session.get('sektionen') or {}
        text = next((v for k, v in sektionen.items() if _norm_key(k) == SECTION_KEY), '')
        if not text or not text.strip():
            continue
        for heading, body in split_sections(text, 3).items():
            bucket = buckets.get(_norm_key(heading))
            if bucket is None:
                continue
            for name, unsicher, qualifier, desc in _parse_entries(body):
                key = unicodedata.normalize('NFC', name).casefold()
                entry = bucket.setdefault(key, {
                    'name': name, 'unsicher': False, 'qualifier': '',
                    'sessions': [], 'erwaehnungen': [],
                })
                entry['unsicher'] = entry['unsicher'] or unsicher
                entry['qualifier'] = entry['qualifier'] or qualifier
                if nr and nr not in entry['sessions']:
                    entry['sessions'].append(nr)
                entry['erwaehnungen'].append({'nr': nr, 'text': desc})

    register: dict[str, list[dict]] = {}
    for list_name, bucket in buckets.items():
        entries = sorted(bucket.values(), key=lambda e: fold(e['name']))
        for e in entries:
            parts = [e['name'], e['qualifier'], *(m['text'] for m in e['erwaehnungen'])]
            e['such'] = ' '.join(fold(p) for p in parts if p)
        register[list_name] = entries
    return register
