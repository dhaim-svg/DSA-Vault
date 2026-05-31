"""Tests for structured geld frontmatter and inventar weight parsing (D-004)."""
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_geld_dict(geld_fm: dict) -> dict:
    """Replicate the held.py geld-parsing logic for unit testing."""
    if isinstance(geld_fm, dict):
        geld = {
            'dukaten': int(geld_fm.get('dukaten', 0)),
            'silbertaler': int(geld_fm.get('silbertaler', 0)),
            'heller': int(geld_fm.get('heller', 0)),
            'kreuzer': int(geld_fm.get('kreuzer', 0)),
        }
        geld['gesamt_kreuzer'] = (
            geld['dukaten'] * 1000 +
            geld['silbertaler'] * 100 +
            geld['heller'] * 10 +
            geld['kreuzer']
        )
        return geld
    return {'dukaten': 0, 'silbertaler': 0, 'heller': 0, 'kreuzer': 0, 'gesamt_kreuzer': 0}


# ---------------------------------------------------------------------------
# test_geld_structure
# ---------------------------------------------------------------------------

def test_geld_structure():
    """parse_frontmatter + geld logic yields all 5 expected keys with correct values."""
    from parsers.held import parse_frontmatter

    md = "---\ngeld: {dukaten: 10, silbertaler: 64, heller: 0, kreuzer: 0}\n---\n"
    fm, _ = parse_frontmatter(md)
    geld = _make_geld_dict(fm.get('geld', {}))

    assert set(geld.keys()) == {'dukaten', 'silbertaler', 'heller', 'kreuzer', 'gesamt_kreuzer'}, \
        f"Unexpected keys: {set(geld.keys())}"
    assert geld['dukaten'] == 10
    assert geld['silbertaler'] == 64
    assert geld['heller'] == 0
    assert geld['kreuzer'] == 0


# ---------------------------------------------------------------------------
# test_gesamt_kreuzer_math
# ---------------------------------------------------------------------------

def test_gesamt_kreuzer_math():
    """Conversion formula: 1D + 2ST + 3H + 4Kr = 1000+200+30+4 = 1234 Kreuzer."""
    geld = _make_geld_dict({'dukaten': 1, 'silbertaler': 2, 'heller': 3, 'kreuzer': 4})
    assert geld['gesamt_kreuzer'] == 1234, \
        f"Expected 1234, got {geld['gesamt_kreuzer']}"


# ---------------------------------------------------------------------------
# test_geld_fallback
# ---------------------------------------------------------------------------

def test_geld_fallback():
    """When frontmatter has no geld key, fallback dict has all 5 keys valued 0."""
    from parsers.held import parse_frontmatter

    md = "---\nname: Test\n---\n"
    fm, _ = parse_frontmatter(md)
    geld = _make_geld_dict(fm.get('geld', {}))

    assert set(geld.keys()) == {'dukaten', 'silbertaler', 'heller', 'kreuzer', 'gesamt_kreuzer'}
    assert all(v == 0 for v in geld.values()), f"Expected all zeros, got {geld}"


# ---------------------------------------------------------------------------
# test_inventar_gewicht
# ---------------------------------------------------------------------------

def test_inventar_gewicht():
    """parse_md_table extracts Gewicht (Unzen) and sums correctly."""
    from parsers.held import parse_md_table, strip_wikilink, safe_int

    table_md = (
        "| Gegenstand | Anzahl | Gewicht (Unzen) |\n"
        "|------------|--------|------------------|\n"
        "| Magierstab | 1 | 90 |\n"
        "| Umhängetasche | 1 | 30 |\n"
        "| Dolch | 1 | — |\n"
    )

    inventar: list[dict] = []
    inventar_gewicht_unzen = 0
    for row in parse_md_table(table_md):
        name = strip_wikilink(row.get('Gegenstand', ''))
        if name:
            gew_raw = row.get('Gewicht (Unzen)', '')
            gew = safe_int(gew_raw) if gew_raw.strip() not in ('—', '', '-') else 0
            inventar_gewicht_unzen += gew
            inventar.append({'name': name, 'anzahl': row.get('Anzahl', ''), 'gewicht': gew})

    assert len(inventar) == 3, f"Expected 3 items, got {len(inventar)}"
    assert inventar[0]['gewicht'] == 90
    assert inventar[1]['gewicht'] == 30
    assert inventar[2]['gewicht'] == 0, "— should map to 0"
    assert inventar_gewicht_unzen == 120, f"Expected 120 Unzen total, got {inventar_gewicht_unzen}"
    # Verify all items have the 'gewicht' key
    for item in inventar:
        assert 'gewicht' in item, f"Missing 'gewicht' in {item}"


# ---------------------------------------------------------------------------
# test_load_held_geld_integration
# ---------------------------------------------------------------------------

def test_load_held_geld_integration():
    """Integration: load_held returns structured geld dict from _illaen.md frontmatter."""
    from parsers.held import load_held

    vault_root = Path(__file__).parent.parent.parent.parent  # DSA-Vault root
    held = load_held(vault_root, 'illaen-baernhold')
    geld = held['ausruestung']['geld']
    # Illaen's frontmatter: {dukaten: 10, silbertaler: 64, heller: 0, kreuzer: 0}
    assert geld['dukaten'] == 10
    assert geld['silbertaler'] == 64
    assert geld['heller'] == 0
    assert geld['kreuzer'] == 0
    # gesamt_kreuzer = 10*1000 + 64*100 + 0 + 0 = 16400
    assert geld['gesamt_kreuzer'] == 16400
