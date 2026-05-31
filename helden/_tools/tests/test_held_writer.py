"""Tests for held_writer — format-preserving surgical markdown write-back."""
import sys
from pathlib import Path
import pytest

# Add tools dir to path
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import parse_md_table, parse_frontmatter, split_sections
from writers.held_writer import (
    _patch_frontmatter,
    _patch_table_cell,
    _find_section_lines,
    _find_first_table,
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
