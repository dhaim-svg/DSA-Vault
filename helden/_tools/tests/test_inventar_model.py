"""Tests for structured geld frontmatter (load_held) and inventar weight parsing (D-004, B-025, B-026)."""
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

GELD_KEYS = {'dukaten', 'silbertaler', 'heller', 'kreuzer', 'gesamt_kreuzer'}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _geld(tmp_path, illaen: str) -> dict:
    """Ruft den echten Parser: load_held auf einem Mini-Helden mit dem gegebenen _illaen.md-Text."""
    from parsers.held import load_held
    from tests.heldfixtures import MINI_SLUG, write_mini_held

    root = write_mini_held(tmp_path, illaen=illaen)
    return load_held(root, MINI_SLUG)['ausruestung']['geld']


def _frontmatter(body: str) -> str:
    return f'---\n{body}\n---\n'


# ---------------------------------------------------------------------------
# test_geld_structure
# ---------------------------------------------------------------------------

def test_geld_structure(tmp_path):
    """load_held liefert genau die 5 Geld-Schluessel mit den Frontmatter-Werten."""
    geld = _geld(tmp_path, _frontmatter('geld: {dukaten: 10, silbertaler: 64, heller: 0, kreuzer: 0}'))

    assert set(geld.keys()) == GELD_KEYS, f"Unexpected keys: {set(geld.keys())}"
    assert geld['dukaten'] == 10
    assert geld['silbertaler'] == 64
    assert geld['heller'] == 0
    assert geld['kreuzer'] == 0
    assert geld['gesamt_kreuzer'] == 16400


# ---------------------------------------------------------------------------
# test_gesamt_kreuzer_math
# ---------------------------------------------------------------------------

def test_gesamt_kreuzer_math(tmp_path):
    """Kurs: 1D + 2ST + 3H + 4Kr = 1000+200+30+4 = 1234 Kreuzer (jede Sorte anders gewichtet)."""
    geld = _geld(tmp_path, _frontmatter('geld: {dukaten: 1, silbertaler: 2, heller: 3, kreuzer: 4}'))
    assert geld['gesamt_kreuzer'] == 1234, \
        f"Expected 1234, got {geld['gesamt_kreuzer']}"


# ---------------------------------------------------------------------------
# test_geld_fallback
# ---------------------------------------------------------------------------

# kein-geld-schluessel und kein-frontmatter laufen durch den ersten Zweig (fm.get('geld', {}) ist ein dict);
# nur geld-null, geld-skalar und geld-liste erreichen den else-Zweig (geld ist kein dict).
@pytest.mark.parametrize('illaen', [
    pytest.param(_frontmatter('name: Test'), id='kein-geld-schluessel'),
    pytest.param('Nur Text, kein Frontmatter.\n', id='kein-frontmatter'),
    pytest.param(_frontmatter('geld:'), id='geld-null'),
    pytest.param(_frontmatter('geld: 5'), id='geld-skalar'),
    pytest.param(_frontmatter('geld: [1, 2]'), id='geld-liste'),
])
def test_geld_fallback(tmp_path, illaen):
    """Fehlt das geld-Dict (in jeder Form), liefert load_held alle 5 Schluessel mit Wert 0."""
    geld = _geld(tmp_path, illaen)

    assert set(geld.keys()) == GELD_KEYS
    assert all(v == 0 for v in geld.values()), f"Expected all zeros, got {geld}"


# ---------------------------------------------------------------------------
# test_geld_krumme_werte
# ---------------------------------------------------------------------------

def test_geld_krumme_werte(tmp_path):
    """Unbrauchbare Werte fallen auf 0 (safe_int), gueltige Strings werden zahlenwertig gelesen."""
    geld = _geld(tmp_path, _frontmatter('geld: {dukaten: abc, silbertaler: "12", heller: , kreuzer: 7}'))

    assert geld['dukaten'] == 0
    assert geld['silbertaler'] == 12
    assert geld['heller'] == 0
    assert geld['kreuzer'] == 7
    assert geld['gesamt_kreuzer'] == 1207


# ---------------------------------------------------------------------------
# test_inventar_*
# ---------------------------------------------------------------------------

INVENTAR_HEADER = (
    "| Gegenstand | Anzahl | Gewicht (Unzen) |\n"
    "|------------|--------|------------------|\n"
)


def _inventar(tmp_path, tabelle: str) -> dict:
    """Ruft den echten Parser: load_held auf einem Mini-Helden mit einer ## Inventar-Tabelle in ausruestung.md."""
    from parsers.held import load_held
    from tests.heldfixtures import MINI_SLUG, write_mini_held

    root = write_mini_held(tmp_path, ausruestung=f'## Inventar\n{tabelle}')
    return load_held(root, MINI_SLUG)['ausruestung']


def test_inventar_structure(tmp_path):
    """load_held liefert Inventar-Eintraege mit Schluessel 'gewicht'; '—' wird zu 0, Summe stimmt."""
    tabelle = (
        INVENTAR_HEADER +
        "| Magierstab | 1 | 90 |\n"
        "| Umhängetasche | 1 | 30 |\n"
        "| Dolch | 1 | — |\n"
    )
    aus = _inventar(tmp_path, tabelle)
    inventar = aus['inventar']

    assert len(inventar) == 3, f"Expected 3 items, got {len(inventar)}"
    assert inventar[0]['gewicht'] == 90
    assert inventar[1]['gewicht'] == 30
    assert inventar[2]['gewicht'] == 0, "— should map to 0"
    assert aus['inventar_gewicht_unzen'] == 120, f"Expected 120 Unzen total, got {aus['inventar_gewicht_unzen']}"
    # Verify all items have the 'gewicht' key
    for item in inventar:
        assert 'gewicht' in item, f"Missing 'gewicht' in {item}"


@pytest.mark.parametrize('wert', [
    pytest.param('', id='leer'),
    pytest.param('-', id='bindestrich'),
])
def test_inventar_leerer_und_bindestrich_wert(tmp_path, wert):
    """Leerer Gewichtswert und '-' fallen durch safe_int auf 0."""
    tabelle = INVENTAR_HEADER + f"| Ohne Gewicht | 1 | {wert} |\n"
    aus = _inventar(tmp_path, tabelle)
    assert aus['inventar'][0]['gewicht'] == 0
    assert aus['inventar_gewicht_unzen'] == 0


def test_inventar_nicht_numerischer_wert(tmp_path):
    """Ein nicht-numerischer Gewichtswert (nicht —/leer/-) laeuft durch safe_int und wird 0."""
    tabelle = INVENTAR_HEADER + "| Amulett | 1 | abc |\n"
    aus = _inventar(tmp_path, tabelle)
    assert aus['inventar'][0]['gewicht'] == 0
    assert aus['inventar_gewicht_unzen'] == 0


@pytest.mark.parametrize('wert,erwartet', [
    pytest.param('—', 0, id='em-dash'),
    pytest.param('', 0, id='leer'),
    pytest.param('-', 0, id='bindestrich'),
])
def test_safe_int_edge_cases_mutation_probe(wert, erwartet):
    """safe_int selbst bildet Leerwerte und Bindestrich auf 0 ab -- Mutation-Probe gegen Regression."""
    from parsers.held import safe_int
    assert safe_int(wert) == erwartet


# ---------------------------------------------------------------------------
# test_load_held_geld_integration
# ---------------------------------------------------------------------------

def test_load_held_geld_integration(tmp_path):
    """Integration: load_held liefert das strukturierte geld-Dict aus dem Frontmatter von _illaen.md.

    Synthetisch statt live (B-024): Der Test las vorher den echten Live-Bogen und pinnte dessen
    Geldstand -- er brach, sobald der User Geld ausgab. Jetzt liefert ein Mini-Held den Frontmatter-Block; die Werte
    sind bewusst krumm und in allen vier Muenzsorten != 0, damit eine vertauschte Sorte auffaellt.
    Randfaelle (fehlender geld-Block, Kurs 1234) decken test_geld_fallback / test_gesamt_kreuzer_math ab."""
    from parsers.held import load_held
    from tests.heldfixtures import MINI_SLUG, write_mini_held

    illaen = '---\ngeld: {dukaten: 3, silbertaler: 7, heller: 5, kreuzer: 9}\n---\n'
    root = write_mini_held(tmp_path, illaen=illaen)
    geld = load_held(root, MINI_SLUG)['ausruestung']['geld']
    assert geld['dukaten'] == 3
    assert geld['silbertaler'] == 7
    assert geld['heller'] == 5
    assert geld['kreuzer'] == 9
    # Kurs (parsers/held.py): 1 Dukat = 1000, 1 Silbertaler = 100, 1 Heller = 10 Kreuzer
    # gesamt_kreuzer = 3*1000 + 7*100 + 5*10 + 9 = 3759
    assert geld['gesamt_kreuzer'] == 3759
