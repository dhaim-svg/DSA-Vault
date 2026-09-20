"""Tests for steigerbar_talente and steigerbar_zauber parser output (synthetic mini hero, no live character sheet)."""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from tests.heldfixtures import MINI_SLUG, write_mini_held


# ---------------------------------------------------------------------------
# Unit tests: _skt_for_section
# ---------------------------------------------------------------------------

def test_skt_for_section_parses_heading():
    from parsers.held import _skt_for_section
    assert _skt_for_section('Körperliche Talente (SKT D)') == 'D'
    assert _skt_for_section('Gesellschaftliche Talente (SKT B)') == 'B'
    assert _skt_for_section('Handwerkliche Talente (SKT B)') == 'B'


def test_skt_for_section_fallback_map():
    from parsers.held import _skt_for_section
    assert _skt_for_section('Körperliche Talente') == 'D'
    assert _skt_for_section('Wissenstalente') == 'B'
    assert _skt_for_section('Sprachen') == 'A'


def test_skt_for_section_unknown_defaults_to_b():
    from parsers.held import _skt_for_section
    assert _skt_for_section('Unbekannte Sektion') == 'B'


# ---------------------------------------------------------------------------
# Fixture: synthetic mini hero, formats as in the live sheet's talente.md / zauber.md
# ---------------------------------------------------------------------------

# Stäbe has the same Stk as the parser's fallback ('D'), Dolche does not: only the latter proves that Stk is read.
# 'Handwerkliche Talente (SKT C)' differs from the section fallback ('B'): only it proves that the heading wins.
MINI_TALENTE = """## Kampftechniken

| Kampftechnik | Stk | BE | AT | PA | TaW |
|---|---|---|---|---|---|
| Stäbe | D | BE−2 | 14 | 10 | 9 |
| Dolche | C | BE−1 | 8 | 6 | 3 |

## Körperliche Talente (SKT D)

| Talent | Probe | BE | TaW |
|---|---|---|---|
| Klettern | MU/GE/KK | BE×2 | 4 |

## Gesellschaftliche Talente (SKT B)

| Talent | Probe | TaW |
|---|---|---|
| Überreden | MU/IN/CH | 5 |

## Sprachen (SKT A)

| Sprache | Komplexität | TaW |
|---|---|---|
| Garethi | 18 | 15 |
| Bosparano | 21 | 8 |

## Schriften (SKT A)

| Schrift | Komplexität | TaW |
|---|---|---|
| Kusliker Zeichen | 5 | 3 |

## Handwerkliche Talente (SKT C)

| Talent | Probe | TaW |
|---|---|---|
| Holzbearbeitung | KL/FF/KK | 2 |
"""

# Armatrutz: Hauszauber, Lern 'A+' as written in the live sheet's table; Balsam: plain 'B'.
MINI_ZAUBER = r"""## Zauberliste

| Zauber | Probe | ZfW | Merkmale | Haus | Komp | Lern | ZD | Kosten | Wirkung | Modifikationen | Notizen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| [[wiki/dsa-4.1/zauber/armatrutz\|Armatrutz]] | IN/GE/KO | 10 | Eign | × | B | A+ | 3 A | 4 AsP | Wirkung A | — | |
| [[wiki/dsa-4.1/zauber/balsam\|Balsam]] | KL/IN/FF | 6 | Heil | | C | B | 5 A | 2 AsP | Wirkung B | — | |
"""


@pytest.fixture(scope='module')
def mini_held(tmp_path_factory):
    from parsers.held import load_held
    root = write_mini_held(tmp_path_factory.mktemp('mini_held'), talente=MINI_TALENTE, zauber=MINI_ZAUBER)
    return load_held(root, MINI_SLUG)


# ---------------------------------------------------------------------------
# Integration tests: load_held steigerbar fields
# ---------------------------------------------------------------------------

def test_steigerbar_talente_has_required_fields(mini_held):
    items = mini_held['steigerbar_talente']
    assert [i['name'] for i in items] == [
        'Stäbe', 'Dolche', 'Klettern', 'Überreden', 'Garethi', 'Bosparano', 'Kusliker Zeichen', 'Holzbearbeitung',
    ]
    for item in items:
        assert 'name' in item, f"Missing 'name' in {item}"
        assert 'taw' in item
        assert 'skt' in item
        assert item['skt'] in list('ABCDEFGH'), f"Invalid skt '{item['skt']}'"
        assert 'section' in item
        assert 'file' in item
        assert item['file'] == 'talente.md'
        assert 'row_key_column' in item


def test_steigerbar_talente_skt_comes_from_section_heading(mini_held):
    skt = {i['name']: i['skt'] for i in mini_held['steigerbar_talente']}
    assert skt['Klettern'] == 'D'
    assert skt['Überreden'] == 'B'
    assert skt['Garethi'] == 'A'
    assert skt['Holzbearbeitung'] == 'C'  # heading (SKT C), not the section fallback 'B'


def test_steigerbar_kampftechniken_use_stk_column(mini_held):
    kampf = [i for i in mini_held['steigerbar_talente'] if 'Kampftechnik' in i['section']]
    assert [i['name'] for i in kampf] == ['Stäbe', 'Dolche']
    for item in kampf:
        assert item['row_key_column'] == 'Kampftechnik'
    # SKT of a Kampftechnik is its Stk column, not a section heading
    assert {i['name']: i['skt'] for i in kampf} == {'Stäbe': 'D', 'Dolche': 'C'}


def test_steigerbar_row_key_column_follows_section_kind(mini_held):
    keys = {i['name']: i['row_key_column'] for i in mini_held['steigerbar_talente']}
    assert keys['Klettern'] == 'Talent'
    assert keys['Garethi'] == 'Sprache'
    assert keys['Kusliker Zeichen'] == 'Schrift'


def test_steigerbar_zauber_has_required_fields(mini_held):
    items = mini_held['steigerbar_zauber']
    assert [i['name'] for i in items] == ['Armatrutz', 'Balsam']
    for item in items:
        assert 'name' in item
        assert 'zfw' in item
        assert 'lern' in item
        assert '+' not in item['lern'], f"A+ not normalized in {item}"
        assert item['lern'] in list('ABCDEFGH'), f"Invalid lern '{item['lern']}'"
        assert 'file' in item
        assert item['file'] == 'zauber.md'


def test_steigerbar_zauber_normalizes_hauszeichen(mini_held):
    """A+ (Hauszauber) should be normalized to 'A'."""
    # precondition: the table really says 'A+' (otherwise the normalization is not exercised)
    armatrutz_roh = next(z for z in mini_held['zauber'] if z['name'] == 'Armatrutz')
    assert armatrutz_roh['lern'] == 'A+'
    items = {i['name']: i for i in mini_held['steigerbar_zauber']}
    assert items['Armatrutz']['lern'] == 'A'
    assert items['Balsam']['lern'] == 'B'


# ---------------------------------------------------------------------------
# Integration tests: Sprachen Komplexität field
# ---------------------------------------------------------------------------

def test_sprachen_have_komplexitaet_in_talente(mini_held):
    """Sprachen entries in talente dict carry numeric komplexitaet and correct probe string."""
    sprachen = mini_held['talente']['Sprachen (SKT A)']
    bosparano = next((e for e in sprachen if e['name'] == 'Bosparano'), None)
    garethi = next((e for e in sprachen if e['name'] == 'Garethi'), None)
    assert bosparano is not None, "Bosparano not found in Sprachen (SKT A)"
    assert garethi is not None, "Garethi not found in Sprachen (SKT A)"
    assert bosparano['komplexitaet'] == 21
    assert garethi['komplexitaet'] == 18
    # No regression on existing probe string
    assert bosparano['probe'] == 'K 21'
    assert garethi['probe'] == 'K 18'


def test_sprachen_have_komplexitaet_in_steigerbar(mini_held):
    """Sprachen and Schriften entries in steigerbar_talente carry numeric komplexitaet."""
    items = mini_held['steigerbar_talente']
    garethi = next((i for i in items if i['name'] == 'Garethi'), None)
    bosparano = next((i for i in items if i['name'] == 'Bosparano'), None)
    kusliker = next((i for i in items if i['name'] == 'Kusliker Zeichen'), None)
    assert garethi is not None, "Garethi not found in steigerbar_talente"
    assert bosparano is not None, "Bosparano not found in steigerbar_talente"
    assert kusliker is not None, "Kusliker Zeichen not found in steigerbar_talente"
    assert garethi['komplexitaet'] == 18
    assert bosparano['komplexitaet'] == 21
    assert kusliker['komplexitaet'] == 5


def test_non_sprachen_have_none_komplexitaet(mini_held):
    """Non-Sprachen/Schriften entries in steigerbar_talente have komplexitaet == None."""
    items = mini_held['steigerbar_talente']
    klettern = next((i for i in items if i['name'] == 'Klettern'), None)
    assert klettern is not None, "Klettern not found in steigerbar_talente"
    assert klettern['komplexitaet'] is None
    staebe = next((i for i in items if i['name'] == 'Stäbe'), None)
    assert staebe is not None, "Stäbe not found in steigerbar_talente"
    assert staebe['komplexitaet'] is None
