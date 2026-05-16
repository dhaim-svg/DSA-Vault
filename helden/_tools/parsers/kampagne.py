"""Parser for DSA 4.1 campaign files."""
import re
from pathlib import Path

from .held import parse_frontmatter, parse_md_table, split_sections, strip_wikilink


def load_kampagne(vault_root: Path, slug: str) -> dict:
    """Load a campaign from abenteuer/<slug>/_<slug>.md."""
    camp_dir = vault_root / 'abenteuer' / slug
    # Find the index file (_<slug>.md or first file starting with _)
    index_file = camp_dir / f'_{slug}.md'
    if not index_file.exists():
        candidates = sorted(camp_dir.glob('_*.md'))
        if not candidates:
            return {'name': slug, 'status_icon': '', 'status_text': '', 'sessions': []}
        index_file = candidates[0]

    text = index_file.read_text(encoding='utf-8')
    fm, rest = parse_frontmatter(text)

    # Extract campaign name from first heading
    name = slug
    for line in rest.splitlines():
        if line.startswith('# '):
            name = line[2:].strip()
            break

    # Extract status line (contains 🟡/🟢/🔴/✅ + text)
    status_icon = ''
    status_text = ''
    status_re = re.compile(r'(🟡|🟢|🔴|✅|🟠)\s+(.*)')
    for line in rest.splitlines():
        m = status_re.search(line)
        if m:
            status_icon = m.group(1)
            status_text = m.group(2).strip()
            break

    # Extract sessions table
    h2 = split_sections(rest, 2)
    sessions: list[dict] = []
    for row in parse_md_table(h2.get('Sessions', '')):
        nr = row.get('#', '') or row.get('Nr', '')
        datum = row.get('Datum', '')
        inhalt = strip_wikilink(row.get('Kurzinhalt', '') or '')
        if nr and nr != '—':
            sessions.append({'nr': nr, 'datum': datum, 'inhalt': inhalt})

    # Also scan for session files
    session_files = sorted(camp_dir.glob('[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]-session-*.md'))
    file_sessions: list[dict] = []
    for sf in session_files:
        sf_text = sf.read_text(encoding='utf-8')
        sf_fm, sf_rest = parse_frontmatter(sf_text)
        nr = sf_fm.get('session', '')
        datum = sf_fm.get('datum', sf.stem[:10])
        # First non-empty line after headings
        inhalt = ''
        for line in sf_rest.splitlines():
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('→'):
                inhalt = strip_wikilink(line)
                break
        file_sessions.append({'nr': str(nr), 'datum': str(datum), 'inhalt': inhalt})

    if file_sessions:
        sessions = file_sessions

    return {
        'name': name,
        'status_icon': status_icon,
        'status_text': status_text,
        'sessions': sessions,
    }
