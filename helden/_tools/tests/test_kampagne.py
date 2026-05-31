"""Tests for load_kampagne — session file parsing with sektionen + datei fields."""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.kampagne import load_kampagne


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_index(camp_dir: Path, slug: str, sessions_table: str = '') -> None:
    """Write a minimal campaign index file."""
    table = sessions_table or (
        '| # | Datum | Kurzinhalt |\n'
        '|---|-------|------------|\n'
    )
    (camp_dir / f'_{slug}.md').write_text(
        f'# Testkampagne\n\n🟢 Laufend\n\n## Sessions\n\n{table}\n',
        encoding='utf-8',
    )


def _make_session_file(camp_dir: Path, filename: str, session_nr: int, datum: str,
                       sections: dict[str, str] | None = None) -> None:
    """Write a session markdown file with frontmatter and H2 sections."""
    body_sections = sections or {
        'Zusammenfassung': 'Kurze Zusammenfassung.',
        'Verlauf': 'Detaillierter Verlauf.',
        'AsP/LeP-Verlauf': 'LeP 30 → 28.',
        'Neue NSCs / Orte': 'NSC Testperson.',
        'Offene Fäden / Cliffhanger': 'Offener Faden.',
        'Loot / AP-Vergabe': '10 AP.',
    }
    body = '\n'.join(
        f'## {heading}\n\n{text}\n'
        for heading, text in body_sections.items()
    )
    content = (
        f'---\ntyp: session\nabenteuer: Testkampagne\n'
        f'session: {session_nr}\ndatum: {datum}\nhelden: []\n---\n\n'
        f'# Session {session_nr:02d}\n\n{body}'
    )
    (camp_dir / filename).write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# Test 1: empty state — no session files, no index table entries
# ---------------------------------------------------------------------------

def test_load_kampagne_no_session_files(tmp_path):
    """load_kampagne with no session files returns empty sessions list."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)
    _make_index(camp_dir, slug)

    result = load_kampagne(tmp_path, slug)

    assert result['sessions'] == []


# ---------------------------------------------------------------------------
# Test 2: one session file — sektionen present, datei set, inhalt works
# ---------------------------------------------------------------------------

def test_load_kampagne_one_session_file(tmp_path):
    """Session file parsed: nr, datum, inhalt, datei, sektionen all populated."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)
    _make_index(camp_dir, slug)

    filename = '2025-10-04-session-01.md'
    _make_session_file(camp_dir, filename, session_nr=1, datum='2025-10-04')

    result = load_kampagne(tmp_path, slug)
    sessions = result['sessions']

    assert len(sessions) == 1
    s = sessions[0]
    assert s['nr'] == '1'
    assert s['datum'] == '2025-10-04'
    assert s['inhalt'] != ''           # extracted from body
    assert s['datei'] == filename
    assert isinstance(s['sektionen'], dict)
    assert len(s['sektionen']) > 0


# ---------------------------------------------------------------------------
# Test 3: sektionen dict keys match heading names
# ---------------------------------------------------------------------------

def test_load_kampagne_sektionen_keys(tmp_path):
    """sektionen keys are exactly the H2 heading texts from the session file."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)
    _make_index(camp_dir, slug)

    sections = {
        'Zusammenfassung': 'Text A.',
        'Verlauf': 'Text B.',
        'AsP/LeP-Verlauf': 'Text C.',
        'Neue NSCs / Orte': 'Text D.',
        'Offene Fäden / Cliffhanger': 'Text E.',
        'Loot / AP-Vergabe': 'Text F.',
    }
    _make_session_file(camp_dir, '2025-10-04-session-01.md', 1, '2025-10-04', sections)

    result = load_kampagne(tmp_path, slug)
    sektionen = result['sessions'][0]['sektionen']

    for heading in sections:
        assert heading in sektionen, f'Expected heading "{heading}" in sektionen'


# ---------------------------------------------------------------------------
# Test 4: empty section body handled gracefully
# ---------------------------------------------------------------------------

def test_load_kampagne_empty_section_body(tmp_path):
    """Empty section body results in empty string value, not KeyError or missing key."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)
    _make_index(camp_dir, slug)

    sections = {
        'Zusammenfassung': '',          # deliberately empty
        'Verlauf': 'Etwas passierte.',
        'Offene Fäden / Cliffhanger': '',  # also empty
    }
    _make_session_file(camp_dir, '2025-10-04-session-01.md', 1, '2025-10-04', sections)

    result = load_kampagne(tmp_path, slug)
    sektionen = result['sessions'][0]['sektionen']

    assert 'Zusammenfassung' in sektionen
    assert sektionen['Zusammenfassung'] == ''
    assert 'Offene Fäden / Cliffhanger' in sektionen
    assert sektionen['Offene Fäden / Cliffhanger'] == ''
    assert sektionen['Verlauf'] == 'Etwas passierte.'


# ---------------------------------------------------------------------------
# Test 5: index-table sessions do NOT get datei/sektionen
# ---------------------------------------------------------------------------

def test_load_kampagne_index_table_sessions_no_sektionen(tmp_path):
    """Sessions from index table do not have datei or sektionen keys."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)

    # Index with a real Sessions table row, no session files on disk
    table = (
        '| # | Datum | Kurzinhalt |\n'
        '|---|-------|------------|\n'
        '| 1 | 2025-10-04 | Erster Ausflug nach Kuslik |\n'
    )
    _make_index(camp_dir, slug, sessions_table=table)
    # No session files written — index table path is used

    result = load_kampagne(tmp_path, slug)
    sessions = result['sessions']

    assert len(sessions) == 1
    s = sessions[0]
    assert s['nr'] == '1'
    assert s['datum'] == '2025-10-04'
    assert 'datei' not in s
    assert 'sektionen' not in s


# ---------------------------------------------------------------------------
# Test 6: datei value is filename only, not full path
# ---------------------------------------------------------------------------

def test_load_kampagne_datei_is_filename_only(tmp_path):
    """datei field contains only the filename (e.g. '2025-10-04-session-01.md'), not full path."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)
    _make_index(camp_dir, slug)

    filename = '2025-10-04-session-01.md'
    _make_session_file(camp_dir, filename, session_nr=1, datum='2025-10-04')

    result = load_kampagne(tmp_path, slug)
    s = result['sessions'][0]

    assert s['datei'] == filename
    assert '/' not in s['datei']
    assert '\\' not in s['datei']


# ---------------------------------------------------------------------------
# Test 7: sektionen body text is stripped of leading/trailing whitespace
# ---------------------------------------------------------------------------

def test_load_kampagne_sektionen_values_stripped(tmp_path):
    """sektionen values are stripped of leading/trailing whitespace."""
    slug = 'testkampagne'
    camp_dir = tmp_path / 'abenteuer' / slug
    camp_dir.mkdir(parents=True)
    _make_index(camp_dir, slug)

    sections = {'Zusammenfassung': 'Komprimierter Text ohne Leerzeichen.'}
    _make_session_file(camp_dir, '2025-10-04-session-01.md', 1, '2025-10-04', sections)

    result = load_kampagne(tmp_path, slug)
    val = result['sessions'][0]['sektionen']['Zusammenfassung']

    assert val == val.strip()
    assert 'Komprimierter Text' in val
