"""Tests for load_chronik — Drachenchronik markdown parsing (synthetic fixtures only)."""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.chronik import load_chronik


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_chronik(vault_root: Path, content: str) -> None:
    chronik_dir = vault_root / 'abenteuer' / 'drachenchronik'
    chronik_dir.mkdir(parents=True, exist_ok=True)
    (chronik_dir / 'chronik.md').write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# Test 1: Spielabend (date heading) separated from Meta-Sektion (non-date)
# ---------------------------------------------------------------------------

def test_spielabend_and_meta_separated(tmp_path):
    content = (
        '# Testchronik\n\n'
        '## Nützliche Links\n'
        '- https://example.test/\n\n'
        '## 01.01.2026\n'
        '- Ein Testeintrag\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)

    assert len(result['spielabende']) == 1
    assert result['spielabende'][0]['datum'] == '01.01.2026'
    assert 'Nützliche Links' in result['meta']
    assert 'example.test' in result['meta']['Nützliche Links']


# ---------------------------------------------------------------------------
# Test 2: IG-Datum marker starts a new ig_tage entry
# ---------------------------------------------------------------------------

def test_ig_datum_marker_starts_new_entry(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**18. Phex**\n'
        '- Erster Eintrag\n'
        '**19. Phex**\n'
        '- Zweiter Eintrag\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    ig_tage = result['spielabende'][0]['ig_tage']

    assert len(ig_tage) == 2
    assert ig_tage[0]['ig_datum'] == '18. Phex'
    assert ig_tage[1]['ig_datum'] == '19. Phex'
    assert ig_tage[0]['bloecke'][0]['text'] == 'Erster Eintrag'
    assert ig_tage[1]['bloecke'][0]['text'] == 'Zweiter Eintrag'


# ---------------------------------------------------------------------------
# Test 3: Szenen-Marker (bold or italic standalone line) is not confused
# with an IG-Datum marker
# ---------------------------------------------------------------------------

def test_szenen_marker_not_confused_with_ig_datum(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**18. Phex**\n'
        '*Suche nach Nachtwache*\n'
        '- Ein Detail\n'
        '**Ein weiterer Marker**\n'
        '- Noch ein Detail\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    ig_tage = result['spielabende'][0]['ig_tage']

    assert len(ig_tage) == 1
    bloecke = ig_tage[0]['bloecke']
    typen = [b['typ'] for b in bloecke]
    assert typen == ['szene', 'bullet', 'szene', 'bullet']
    assert bloecke[0]['text'] == 'Suche nach Nachtwache'
    assert bloecke[2]['text'] == 'Ein weiterer Marker'


# ---------------------------------------------------------------------------
# Test 4: nested bullets preserve depth
# ---------------------------------------------------------------------------

def test_nested_bullets_preserve_depth(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**18. Phex**\n'
        '- Ebene 0\n'
        '  - Ebene 1\n'
        '    - Ebene 2\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    bloecke = result['spielabende'][0]['ig_tage'][0]['bloecke']

    assert [b['tiefe'] for b in bloecke] == [0, 1, 2]
    assert [b['text'] for b in bloecke] == ['Ebene 0', 'Ebene 1', 'Ebene 2']


# ---------------------------------------------------------------------------
# Test 5: <img src="..."> line becomes a bild block with src extracted
# ---------------------------------------------------------------------------

def test_img_tag_becomes_bild_block(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**18. Phex**\n'
        '- <img src="testordner\\testbild.png">\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    bloecke = result['spielabende'][0]['ig_tage'][0]['bloecke']

    assert len(bloecke) == 1
    assert bloecke[0]['typ'] == 'bild'
    assert bloecke[0]['src'] == 'testordner\\testbild.png'


# ---------------------------------------------------------------------------
# Test 6: content before the first IG-Datum marker doesn't crash and gets
# ig_datum: None
# ---------------------------------------------------------------------------

def test_content_before_first_ig_datum_gets_none(tmp_path):
    content = (
        '## 01.01.2026\n'
        '- Vorbemerkung ohne IG-Datum\n'
        '**18. Phex**\n'
        '- Danach mit IG-Datum\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    ig_tage = result['spielabende'][0]['ig_tage']

    assert len(ig_tage) == 2
    assert ig_tage[0]['ig_datum'] is None
    assert ig_tage[0]['bloecke'][0]['text'] == 'Vorbemerkung ohne IG-Datum'
    assert ig_tage[1]['ig_datum'] == '18. Phex'


# ---------------------------------------------------------------------------
# Test 7: missing chronicle file / folder returns empty structure, no crash
# ---------------------------------------------------------------------------

def test_missing_chronik_file_returns_empty_structure(tmp_path):
    result = load_chronik(tmp_path)

    assert result == {'spielabende': [], 'meta': {}}


def test_missing_drachenchronik_folder_returns_empty_structure(tmp_path):
    # No abenteuer/ directory at all
    result = load_chronik(tmp_path, filename='chronik.md')

    assert result == {'spielabende': [], 'meta': {}}


# ---------------------------------------------------------------------------
# Test 8: plain paragraph text lands as a 'text' block
# ---------------------------------------------------------------------------

def test_plain_text_becomes_text_block(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**18. Phex**\n'
        'Ein normaler Absatz ohne Formatierung.\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    bloecke = result['spielabende'][0]['ig_tage'][0]['bloecke']

    assert bloecke[0]['typ'] == 'text'
    assert bloecke[0]['text'] == 'Ein normaler Absatz ohne Formatierung.'


# ---------------------------------------------------------------------------
# Test 10: bare month name without a day number is a Szenen-Marker, not
# an IG-Datum boundary (the disambiguation case the brief specifically
# called out)
# ---------------------------------------------------------------------------

def test_bare_month_without_day_is_szene_not_ig_datum(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**18. Phex**\n'
        '- Ein Eintrag\n'
        '**Phex**\n'
        '- Noch ein Eintrag\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    ig_tage = result['spielabende'][0]['ig_tage']

    # "**Phex**" alone has no day number, so it must NOT start a second
    # ig_tage entry — it's a Szenen-Marker within the same IG-Tag.
    assert len(ig_tage) == 1
    typen = [b['typ'] for b in ig_tage[0]['bloecke']]
    assert typen == ['bullet', 'szene', 'bullet']


# ---------------------------------------------------------------------------
# Test 11: "N. Namenloser Tag" (the real DSA 4.1 naming convention for the
# five intercalary days, per wiki/dsa-4.1/goetter/religiöse-feste.md) is
# recognized as an IG-Datum boundary
# ---------------------------------------------------------------------------

def test_namenloser_tag_is_ig_datum(tmp_path):
    content = (
        '## 01.01.2026\n'
        '**1. Namenloser Tag**\n'
        '- Ein besonderer Tag\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    ig_tage = result['spielabende'][0]['ig_tage']

    assert len(ig_tage) == 1
    assert ig_tage[0]['ig_datum'] == '1. Namenloser Tag'


# ---------------------------------------------------------------------------
# Test 9: multiple spielabende preserve document order (not sorted)
# ---------------------------------------------------------------------------

def test_spielabende_preserve_document_order(tmp_path):
    content = (
        '## 15.02.2026\n'
        '- Zweiter im Dokument, aber späteres Datum\n'
        '## 01.01.2026\n'
        '- Erster im Dokument, früheres Datum\n'
    )
    _write_chronik(tmp_path, content)

    result = load_chronik(tmp_path)
    datums = [s['datum'] for s in result['spielabende']]

    assert datums == ['15.02.2026', '01.01.2026']
