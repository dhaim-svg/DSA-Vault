"""Tests for steigerbar_talente and steigerbar_zauber parser output."""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))
VAULT_ROOT = Path(__file__).parent.parent.parent.parent  # DSA-Vault root


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
# Integration tests: load_held steigerbar fields
# ---------------------------------------------------------------------------

def test_steigerbar_talente_has_required_fields():
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    items = held['steigerbar_talente']
    assert len(items) > 0
    for item in items:
        assert 'name' in item, f"Missing 'name' in {item}"
        assert 'taw' in item
        assert 'skt' in item
        assert item['skt'] in list('ABCDEFGH'), f"Invalid skt '{item['skt']}'"
        assert 'section' in item
        assert 'file' in item
        assert item['file'] == 'talente.md'
        assert 'row_key_column' in item


def test_steigerbar_kampftechniken_use_stk_column():
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    kampf = [i for i in held['steigerbar_talente'] if 'Kampftechnik' in i['section']]
    assert len(kampf) > 0
    for item in kampf:
        assert item['row_key_column'] == 'Kampftechnik'
    # Stäbe (Illaen's main combat technique) is SKT D
    staebe = next((i for i in kampf if i['name'] == 'Stäbe'), None)
    assert staebe is not None, "Stäbe not found in Kampftechniken"
    assert staebe['skt'] == 'D'


def test_steigerbar_zauber_has_required_fields():
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    items = held['steigerbar_zauber']
    assert len(items) > 0
    for item in items:
        assert 'name' in item
        assert 'zfw' in item
        assert 'lern' in item
        assert '+' not in item['lern'], f"A+ not normalized in {item}"
        assert item['lern'] in list('ABCDEFGH'), f"Invalid lern '{item['lern']}'"
        assert 'file' in item
        assert item['file'] == 'zauber.md'


def test_steigerbar_zauber_normalizes_hauszeichen():
    """A+ (Hauszauber) should be normalized to 'A'."""
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    items = held['steigerbar_zauber']
    # Armatrutz has Lern 'A' (Hauszauber — listed as A+)
    armatrutz = next((i for i in items if i['name'] == 'Armatrutz'), None)
    assert armatrutz is not None, "Armatrutz not found in steigerbar_zauber"
    assert armatrutz['lern'] == 'A'
