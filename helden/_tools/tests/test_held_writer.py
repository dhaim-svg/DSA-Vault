"""Tests for held_writer — format-preserving surgical markdown write-back."""
import re
import sys
from pathlib import Path
import pytest

# Add tools dir to path
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import parse_md_table, parse_frontmatter, split_sections, strip_wikilink
from writers.held_writer import (
    _patch_frontmatter,
    _patch_table_cell,
    _find_section_lines,
    _find_first_table,
    _set_table_row,
    _patch_section_body,
    patch,
    etag_for,
    mtime_map,
)

# ---------------------------------------------------------------------------
# Fixtures — minimal markdown fragments (not real vault files)
# ---------------------------------------------------------------------------

FM_TEXT = """\
---
wunden: 0
ap_verfuegbar: 5
---

## Eigenschaften & Basiswerte

### Basiswerte

| Basiswert | Formel | Mod. | Start | Max | Akt. | Gekauft | Rest |
|-----------|--------|------|-------|-----|------|---------|------|
| Lebensenergie (LE) | (KO+KO+KK)/2 | +9 | 19 | 28 | 28 | 0 | 7 |
| Ausdauer (AU) | (MU+KO+GE)/2 | +12 | 19 | 31 | 31 | 0 | 13 |
| Astralenergie (AE) | (MU+IN+CH)/2 | +18 | 20 | 38 | 38 | 0 | 13 |
"""

MULTI_TABLE_TEXT = """\
## Stabzauber (9 Rituale)

| Stabzauber | Vol | Effekt (Kurzform) |
|---|---|---|
| Bindung | 3 | Stab binden |

### Zauberspeicher-Inhalt

| Slot | AsP | Gespeicherter Zauber | Erschwernis-Mods | Letzte Erneuerung |
|------|-----|---------------------|------------------|-------------------|
| 1 | 5 | Armatrutz | — | 2024-01-01 |
| 2 | 0 | — | — | — |
"""

STABZAUBER_WITH_INTRO_TEXT = """\
## Stabzauber (9 Rituale)

Alle Stabzauber sind an Illaens gebundenen Magierstab geknüpft. Aktivierung = freie Aktion. Details → [[wiki/dsa-4.1/rituale/stabzauber|Stabzauber & Kugelzauber]].

| Stabzauber | Vol | Effekt (Kurzform) |
|---|---|---|
| Bindung | 1 pAsP | Grundbindung |
"""


def _extract_stabzauber_regel(sec_content: str) -> str:
    """Mirror of the extraction logic in held.py load_held()."""
    intro_lines = []
    for line in sec_content.splitlines():
        if re.match(r'\s*\|', line):
            break
        stripped = line.strip()
        if stripped:
            intro_lines.append(strip_wikilink(stripped))
    return ' '.join(intro_lines)


# ---------------------------------------------------------------------------
# Parser tests — stabzauber_regel extraction (D-024)
# ---------------------------------------------------------------------------

def test_stabzauber_regel_extracted_from_intro():
    secs = split_sections(STABZAUBER_WITH_INTRO_TEXT, 2)
    sec_name = next(k for k in secs if 'Stabzauber' in k)
    regel = _extract_stabzauber_regel(secs[sec_name])
    assert 'Magierstab' in regel
    assert 'freie Aktion' in regel


def test_stabzauber_regel_strips_wikilinks():
    secs = split_sections(STABZAUBER_WITH_INTRO_TEXT, 2)
    sec_name = next(k for k in secs if 'Stabzauber' in k)
    regel = _extract_stabzauber_regel(secs[sec_name])
    assert '[[' not in regel


def test_stabzauber_regel_empty_when_no_intro():
    secs = split_sections(MULTI_TABLE_TEXT, 2)
    sec_name = next(k for k in secs if 'Stabzauber' in k)
    regel = _extract_stabzauber_regel(secs[sec_name])
    assert regel == ''


# ---------------------------------------------------------------------------
# Frontmatter tests
# ---------------------------------------------------------------------------

def test_patch_frontmatter_integer():
    new_text, old = _patch_frontmatter(FM_TEXT, 'wunden', '2')
    assert old == '0'
    fm, _ = parse_frontmatter(new_text)
    assert fm['wunden'] == 2


def test_patch_frontmatter_preserves_other_keys():
    new_text, _ = _patch_frontmatter(FM_TEXT, 'wunden', '1')
    fm, _ = parse_frontmatter(new_text)
    assert fm['ap_verfuegbar'] == 5


def test_patch_frontmatter_key_not_found_returns_none():
    result, _ = _patch_frontmatter(FM_TEXT, 'nonexistent_key', '99')
    assert result is None


def test_patch_frontmatter_only_one_line_changes():
    new_text, _ = _patch_frontmatter(FM_TEXT, 'wunden', '3')
    orig_lines = FM_TEXT.splitlines()
    new_lines = new_text.splitlines()
    assert len(orig_lines) == len(new_lines), "Line count must not change"
    changed = [i for i, (a, b) in enumerate(zip(orig_lines, new_lines)) if a != b]
    assert len(changed) == 1, f"Exactly one line should change; changed: {changed}"


# ---------------------------------------------------------------------------
# Table cell tests
# ---------------------------------------------------------------------------

def test_patch_table_cell_le_aktuell():
    new_text, old = _patch_table_cell(
        FM_TEXT,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Lebensenergie (LE)'},
        column='Akt.',
        value='21',
    )
    assert old == '28'
    assert new_text is not None
    # Re-parse and verify
    _, body = parse_frontmatter(new_text)
    h2 = split_sections(body, 2)
    h3 = split_sections(h2['Eigenschaften & Basiswerte'], 3)
    rows = parse_md_table(h3['Basiswerte'])
    le_row = next(r for r in rows if 'Lebensenergie' in r.get('Basiswert', ''))
    assert le_row['Akt.'] == '21'


def test_patch_table_cell_only_one_line_changes():
    new_text, _ = _patch_table_cell(
        FM_TEXT,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Ausdauer (AU)'},
        column='Akt.',
        value='15',
    )
    assert new_text is not None
    orig_lines = FM_TEXT.splitlines()
    new_lines = new_text.splitlines()
    assert len(orig_lines) == len(new_lines)
    changed = [i for i, (a, b) in enumerate(zip(orig_lines, new_lines)) if a != b]
    assert len(changed) == 1


def test_patch_table_cell_nested_h3():
    """Targeting a cell in a H3 sub-table (Zauberspeicher-Inhalt)."""
    new_text, old = _patch_table_cell(
        MULTI_TABLE_TEXT,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '1'},
        column='AsP',
        value='3',
    )
    assert old == '5'
    assert new_text is not None
    h2 = split_sections(new_text, 2)
    h3 = split_sections(h2['Stabzauber (9 Rituale)'], 3)
    rows = parse_md_table(h3['Zauberspeicher-Inhalt'])
    assert rows[0]['AsP'] == '3'


def test_patch_table_cell_row_not_found_returns_none():
    result, _ = _patch_table_cell(
        FM_TEXT,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Nonexistent Row'},
        column='Akt.',
        value='99',
    )
    assert result is None


def test_patch_table_cell_crlf_preserved():
    crlf_text = FM_TEXT.replace('\n', '\r\n')
    new_text, _ = _patch_table_cell(
        crlf_text,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Lebensenergie (LE)'},
        column='Akt.',
        value='20',
    )
    assert new_text is not None
    assert '\r\n' in new_text, "CRLF line endings must be preserved"


# ---------------------------------------------------------------------------
# Fixtures for table_append_row
# ---------------------------------------------------------------------------

STEIGERUNGS_LOG_TEXT = """\
---
typ: held-section
held: Test Held
---

# Steigerungs-Log

## Protokoll

| Datum | AP danach (verf.) | Aktion | Kosten | Begründung |
|-------|-------------------|--------|--------|------------|
| 2026-05-15 | 5 verf. | Initialstand | — | Übernahme |
"""


# ---------------------------------------------------------------------------
# table_append_row tests
# ---------------------------------------------------------------------------

def test_table_append_row_adds_new_row():
    from writers.held_writer import _append_table_row
    new_text, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['Protokoll'],
        cells=['2026-05-31', '4 verf.', 'Klettern TaW 4→5', '4', 'Test'],
    )
    assert new_text is not None
    assert '2026-05-31' in new_text
    assert 'Klettern TaW 4→5' in new_text


def test_table_append_row_increases_row_count():
    from writers.held_writer import _append_table_row
    from parsers.held import parse_frontmatter, split_sections, parse_md_table
    new_text, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['Protokoll'],
        cells=['2026-05-31', '4 verf.', 'Klettern TaW 4→5', '4', 'Test'],
    )
    _, body = parse_frontmatter(new_text)
    h2 = split_sections(body, 2)
    rows = parse_md_table(h2['Protokoll'])
    assert len(rows) == 2  # original 1 + new 1


def test_table_append_row_section_not_found_returns_none():
    from writers.held_writer import _append_table_row
    result, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['NonExistent'],
        cells=['x'],
    )
    assert result is None


def test_table_append_row_empty_cells_returns_none():
    from writers.held_writer import _append_table_row
    result, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['Protokoll'],
        cells=[],
    )
    assert result is None


def test_table_append_row_via_patch_api(tmp_path):
    """End-to-end: patch() dispatches table_append_row correctly."""
    from writers.held_writer import patch
    slug = 'test-held'
    hero_dir = tmp_path / 'helden' / slug
    hero_dir.mkdir(parents=True)
    log_file = hero_dir / 'steigerungs-log.md'
    log_file.write_text(STEIGERUNGS_LOG_TEXT, encoding='utf-8')

    result = patch(tmp_path, slug, {
        'kind': 'table_append_row',
        'file': 'steigerungs-log.md',
        'section_path': ['Protokoll'],
        'cells': ['2026-05-31', '4 verf.', 'Klettern TaW 4→5', '4', 'Test'],
    })
    assert result.ok
    updated = log_file.read_text(encoding='utf-8')
    assert '2026-05-31' in updated
    assert 'Klettern TaW 4→5' in updated


# ---------------------------------------------------------------------------
# table_row tests
# ---------------------------------------------------------------------------

def test_set_table_row_fills_slot():
    """Fill slot 1: all 4 columns updated in one call, slot 2 unchanged."""
    new_text, old_row = _set_table_row(
        MULTI_TABLE_TEXT,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '1'},
        cells={
            'AsP': '15',
            'Gespeicherter Zauber': 'Ignifaxius',
            'Erschwernis-Mods': '—',
            'Letzte Erneuerung': '2026-05-31',
        },
    )
    assert new_text is not None
    # old_row is the original slot-1 line (stripped of line ending)
    assert '5' in old_row
    assert 'Armatrutz' in old_row

    # Re-parse and check all 4 columns updated
    h2 = split_sections(new_text, 2)
    h3 = split_sections(h2['Stabzauber (9 Rituale)'], 3)
    rows = parse_md_table(h3['Zauberspeicher-Inhalt'])
    slot1 = next(r for r in rows if r['Slot'] == '1')
    assert slot1['AsP'] == '15'
    assert slot1['Gespeicherter Zauber'] == 'Ignifaxius'
    assert slot1['Erschwernis-Mods'] == '—'
    assert slot1['Letzte Erneuerung'] == '2026-05-31'

    # Slot 2 must be untouched
    slot2 = next(r for r in rows if r['Slot'] == '2')
    assert slot2['AsP'] == '0'
    assert slot2['Gespeicherter Zauber'] == '—'


def test_set_table_row_clears_slot():
    """Clear slot 1 back to sentinel values; slot 2 unchanged."""
    new_text, _ = _set_table_row(
        MULTI_TABLE_TEXT,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '1'},
        cells={
            'AsP': '—',
            'Gespeicherter Zauber': '— frei —',
            'Erschwernis-Mods': '—',
            'Letzte Erneuerung': '—',
        },
    )
    assert new_text is not None
    h2 = split_sections(new_text, 2)
    h3 = split_sections(h2['Stabzauber (9 Rituale)'], 3)
    rows = parse_md_table(h3['Zauberspeicher-Inhalt'])
    slot1 = next(r for r in rows if r['Slot'] == '1')
    assert slot1['AsP'] == '—'
    assert slot1['Gespeicherter Zauber'] == '— frei —'
    assert slot1['Erschwernis-Mods'] == '—'
    assert slot1['Letzte Erneuerung'] == '—'

    # Slot 2 must remain unchanged
    slot2 = next(r for r in rows if r['Slot'] == '2')
    assert slot2['AsP'] == '0'


def test_set_table_row_not_found_row():
    """row_key match doesn't exist → returns (None, '')."""
    result, old = _set_table_row(
        MULTI_TABLE_TEXT,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '99'},
        cells={'AsP': '5'},
    )
    assert result is None
    assert old == ''


def test_set_table_row_unknown_column():
    """cells contains a column not in table headers → returns (None, '')."""
    result, old = _set_table_row(
        MULTI_TABLE_TEXT,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '1'},
        cells={'AsP': '5', 'NonexistentColumn': 'x'},
    )
    assert result is None
    assert old == ''


def test_set_table_row_crlf_preserved():
    """CRLF text in → CRLF text out."""
    crlf_text = MULTI_TABLE_TEXT.replace('\n', '\r\n')
    new_text, _ = _set_table_row(
        crlf_text,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '1'},
        cells={'AsP': '15', 'Gespeicherter Zauber': 'Ignifaxius'},
    )
    assert new_text is not None
    assert '\r\n' in new_text, "CRLF line endings must be preserved"


def test_set_table_row_via_patch_api(tmp_path):
    """End-to-end: patch() dispatches table_row correctly."""
    from writers.held_writer import patch
    slug = 'test-held'
    hero_dir = tmp_path / 'helden' / slug
    hero_dir.mkdir(parents=True)
    ritual_file = hero_dir / 'rituale.md'
    ritual_file.write_text(MULTI_TABLE_TEXT, encoding='utf-8')

    result = patch(tmp_path, slug, {
        'kind': 'table_row',
        'file': 'rituale.md',
        'section_path': ['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        'row_key': {'column': 'Slot', 'match': '1'},
        'cells': {
            'AsP': '15',
            'Gespeicherter Zauber': 'Ignifaxius',
            'Erschwernis-Mods': '—',
            'Letzte Erneuerung': '2026-05-31',
        },
    })
    assert result.ok
    updated = ritual_file.read_text(encoding='utf-8')
    assert 'Ignifaxius' in updated
    assert '15' in updated
    assert '2026-05-31' in updated


# ---------------------------------------------------------------------------
# Fixtures for section_body and kampagne scope tests
# ---------------------------------------------------------------------------

SECTION_BODY_TEXT = """\
## Hintergrund

Illaen wurde in Waldungen erzogen.

## Verlauf

Hier steht der alte Verlauf.
Mehrere Zeilen.

## Notizen

Verschiedene Notizen.
"""


# ---------------------------------------------------------------------------
# section_body tests
# ---------------------------------------------------------------------------

def test_section_body_replaces_content():
    """Basic replace: old_value is old text, new body is written, heading preserved."""
    new_text, old_value = _patch_section_body(
        SECTION_BODY_TEXT,
        section='Verlauf',
        value='Neuer Verlaufstext.\nZweite Zeile.',
    )
    assert new_text is not None
    assert old_value == 'Hier steht der alte Verlauf.\nMehrere Zeilen.'
    assert '## Verlauf' in new_text
    assert 'Neuer Verlaufstext.' in new_text
    assert 'Zweite Zeile.' in new_text
    # Old content must be gone
    assert 'Hier steht der alte Verlauf.' not in new_text


def test_section_body_section_not_found():
    """Unknown heading → returns (None, ''), patch() reports error='section not found'."""
    result, old = _patch_section_body(
        SECTION_BODY_TEXT,
        section='NichtVorhanden',
        value='irgendwas',
    )
    assert result is None
    assert old == ''


def test_section_body_preserves_surrounding_headings():
    """Neighbouring H2 sections are fully untouched after replace."""
    new_text, _ = _patch_section_body(
        SECTION_BODY_TEXT,
        section='Verlauf',
        value='Neuer Text.',
    )
    assert new_text is not None
    # Both neighbouring sections still present with their content
    assert '## Hintergrund' in new_text
    assert 'Illaen wurde in Waldungen erzogen.' in new_text
    assert '## Notizen' in new_text
    assert 'Verschiedene Notizen.' in new_text


def test_section_body_via_patch_api_error_message(tmp_path):
    """patch() with section_body + missing section → ok=False, error='section not found'."""
    slug = 'test-held'
    hero_dir = tmp_path / 'helden' / slug
    hero_dir.mkdir(parents=True)
    md_file = hero_dir / 'abenteuer.md'
    md_file.write_text(SECTION_BODY_TEXT, encoding='utf-8')

    result = patch(tmp_path, slug, {
        'kind': 'section_body',
        'file': 'abenteuer.md',
        'section': 'NichtVorhanden',
        'value': 'x',
    })
    assert not result.ok
    assert result.error == 'section not found'


# ---------------------------------------------------------------------------
# scope='kampagne' tests
# ---------------------------------------------------------------------------

def test_patch_kampagne_scope(tmp_path):
    """patch() with scope='kampagne' resolves to abenteuer/<campaign>/file.md."""
    campaign = 'drachenchronik'
    kampagne_dir = tmp_path / 'abenteuer' / campaign
    kampagne_dir.mkdir(parents=True)
    md_file = kampagne_dir / 'session.md'
    md_file.write_text(SECTION_BODY_TEXT, encoding='utf-8')

    result = patch(tmp_path, 'any-slug', {
        'kind': 'section_body',
        'file': 'session.md',
        'section': 'Verlauf',
        'value': 'Neue Session-Notizen.',
        'scope': 'kampagne',
        'campaign': campaign,
    })
    assert result.ok
    updated = md_file.read_text(encoding='utf-8')
    assert 'Neue Session-Notizen.' in updated
    # Heading preserved
    assert '## Verlauf' in updated


def test_etag_for_kampagne_scope(tmp_path):
    """etag_for with scope='kampagne' reads from abenteuer/<campaign>/<file>."""
    campaign = 'drachenchronik'
    kampagne_dir = tmp_path / 'abenteuer' / campaign
    kampagne_dir.mkdir(parents=True)
    md_file = kampagne_dir / 'session.md'
    content = b'hello kampagne'
    md_file.write_bytes(content)

    import hashlib
    expected = hashlib.md5(content).hexdigest()
    actual = etag_for(tmp_path, 'any-slug', 'session.md', scope='kampagne', campaign=campaign)
    assert actual == expected


def test_mtime_map_kampagne_scope(tmp_path):
    """mtime_map with scope='kampagne' lists .md files from abenteuer/<campaign>/."""
    campaign = 'drachenchronik'
    kampagne_dir = tmp_path / 'abenteuer' / campaign
    kampagne_dir.mkdir(parents=True)
    md_file = kampagne_dir / 'session.md'
    md_file.write_text('content', encoding='utf-8')

    result = mtime_map(tmp_path, 'any-slug', scope='kampagne', campaign=campaign)
    assert 'session.md' in result
    assert result['session.md'] == pytest.approx(md_file.stat().st_mtime)
