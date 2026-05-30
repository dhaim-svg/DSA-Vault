"""Specification tests for DSA 4.1 dice calculation logic.

These Python functions mirror the JS implementations in dice.js exactly.
If the Python tests pass, the JS is correct if it follows the same logic.
"""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))


# ---------------------------------------------------------------------------
# Python mirror of dice.js math — paste these into dice.js as JS equivalents
# ---------------------------------------------------------------------------

def parse_dice_string(s):
    """Parse "2W6+3", "1W+1", "W20", "W6", "3" → dict or None."""
    import re
    s = s.strip()
    # Pure integer
    if re.fullmatch(r'\d+', s):
        return {'count': 1, 'sides': None, 'bonus': int(s)}
    # WY or NWY with optional bonus: "2W6+3", "W20", "3W6-1"
    m = re.fullmatch(r'(\d*)W(\d+)\s*([+-]\d+)?', s, re.IGNORECASE)
    if m:
        return {
            'count': int(m.group(1)) if m.group(1) else 1,
            'sides': int(m.group(2)),
            'bonus': int(m.group(3)) if m.group(3) else 0,
        }
    # "1W+1" style — implicit W6
    m = re.fullmatch(r'(\d*)W\s*([+-]\d+)', s, re.IGNORECASE)
    if m:
        return {
            'count': int(m.group(1)) if m.group(1) else 1,
            'sides': 6,
            'bonus': int(m.group(2)),
        }
    return None


def calc_talent_probe(eig3, taw, rolls, mod):
    """Calculate a 3W20 talent probe.

    eig3: list of 3 eigenschaft values (ints, may include None for ** slots)
    taw: Talentwert (int)
    rolls: list of 3 dice results (ints 1-20)
    mod: modifier applied to effTaW (negative = erschwerend)
    Returns dict with tap (int), success (bool), isCrit (bool), isPatzer (bool),
    perSlot (list of dicts with roll, eig, fehl).
    """
    eff_taw = taw + mod
    per_slot = []
    total_fehl = 0
    for i in range(3):
        roll = rolls[i]
        eig = eig3[i]
        if eig is None:
            per_slot.append({'roll': roll, 'eig': None, 'fehl': 0})
        else:
            fehl = max(0, roll - eig)
            total_fehl += fehl
            per_slot.append({'roll': roll, 'eig': eig, 'fehl': fehl})
    tap = eff_taw - total_fehl
    ones = sum(1 for r in rolls if r == 1)
    twenties = sum(1 for r in rolls if r == 20)
    is_crit = ones >= 2
    is_patzer = twenties >= 2
    return {
        'tap': tap,
        'success': tap >= 0 or is_crit,
        'isCrit': is_crit,
        'isPatzer': is_patzer,
        'perSlot': per_slot,
    }


def calc_eigenschaft_probe(wert, roll, mod):
    """Calculate a 1W20 eigenschaft probe."""
    eff_wert = wert + mod
    return {
        'success': roll <= eff_wert or roll == 1,
        'isCrit': roll == 1,
        'isPatzer': roll == 20,
    }


def calc_kampf_probe(at_or_pa, roll, mod):
    """Calculate a 1W20 combat probe (AT or PA)."""
    eff = at_or_pa + mod
    return {
        'success': roll <= eff or roll == 1,
        'isCrit': roll == 1,
        'isPatzer': roll == 20,
    }


# ---------------------------------------------------------------------------
# Tests for parse_dice_string
# ---------------------------------------------------------------------------

def test_parse_2w6_plus_3():
    r = parse_dice_string('2W6+3')
    assert r == {'count': 2, 'sides': 6, 'bonus': 3}

def test_parse_1w_plus_1():
    """'1W+1' means 1d6+1 (implicit sides=6)."""
    r = parse_dice_string('1W+1')
    assert r == {'count': 1, 'sides': 6, 'bonus': 1}

def test_parse_w20():
    r = parse_dice_string('W20')
    assert r == {'count': 1, 'sides': 20, 'bonus': 0}

def test_parse_w6():
    r = parse_dice_string('W6')
    assert r == {'count': 1, 'sides': 6, 'bonus': 0}

def test_parse_pure_integer():
    r = parse_dice_string('3')
    assert r == {'count': 1, 'sides': None, 'bonus': 3}

def test_parse_3w6_minus_1():
    r = parse_dice_string('3W6-1')
    assert r == {'count': 3, 'sides': 6, 'bonus': -1}

def test_parse_invalid_returns_none():
    assert parse_dice_string('ZfW*2') is None
    assert parse_dice_string('') is None

def test_parse_lowercase_w():
    r = parse_dice_string('2w6+3')
    assert r == {'count': 2, 'sides': 6, 'bonus': 3}


# ---------------------------------------------------------------------------
# Tests for calc_talent_probe
# ---------------------------------------------------------------------------

def test_talent_probe_success_no_fehl():
    """Körperbeherrschung GE13/GE13/KK11, TaW7, dice 8/11/4 → TaP*=7."""
    result = calc_talent_probe([13, 13, 11], 7, [8, 11, 4], 0)
    assert result['tap'] == 7
    assert result['success'] is True
    assert result['isCrit'] is False
    assert result['isPatzer'] is False
    assert result['perSlot'] == [
        {'roll': 8, 'eig': 13, 'fehl': 0},
        {'roll': 11, 'eig': 13, 'fehl': 0},
        {'roll': 4, 'eig': 11, 'fehl': 0},
    ]

def test_talent_probe_partial_fehl():
    """MU12/GE13/KK11, TaW5, dice 15/10/13 → TaP*=0 (barely success)."""
    result = calc_talent_probe([12, 13, 11], 5, [15, 10, 13], 0)
    assert result['tap'] == 0
    assert result['success'] is True
    assert result['perSlot'][0]['fehl'] == 3   # 15-12
    assert result['perSlot'][1]['fehl'] == 0
    assert result['perSlot'][2]['fehl'] == 2   # 13-11

def test_talent_probe_failure():
    """Same as above but erschwernis -3 → TaP*=-3."""
    result = calc_talent_probe([12, 13, 11], 5, [15, 10, 13], -3)
    assert result['tap'] == -3
    assert result['success'] is False

def test_talent_probe_kritisch():
    """Two 1s → Kritisch, success even with negative tap."""
    result = calc_talent_probe([10, 10, 10], 0, [1, 1, 15], -5)
    assert result['isCrit'] is True
    assert result['success'] is True

def test_talent_probe_patzer():
    """Two 20s → Patzer."""
    result = calc_talent_probe([10, 10, 10], 10, [20, 20, 5], 0)
    assert result['isPatzer'] is True

def test_talent_probe_star_star_slot():
    """** slot (eig=None) is not counted in TaP* calculation."""
    result = calc_talent_probe([14, 13, None], 8, [10, 16, 18], 0)
    assert result['perSlot'][2] == {'roll': 18, 'eig': None, 'fehl': 0}
    assert result['tap'] == 8 - 3  # 5
    assert result['success'] is True


# ---------------------------------------------------------------------------
# Tests for calc_eigenschaft_probe
# ---------------------------------------------------------------------------

def test_eigenschaft_success():
    assert calc_eigenschaft_probe(14, 10, 0)['success'] is True

def test_eigenschaft_failure():
    r = calc_eigenschaft_probe(10, 15, 0)
    assert r['success'] is False
    assert r['isCrit'] is False
    assert r['isPatzer'] is False

def test_eigenschaft_kritisch_always_succeeds():
    """Roll of 1 is always a critical success."""
    r = calc_eigenschaft_probe(1, 1, -10)
    assert r['isCrit'] is True
    assert r['success'] is True

def test_eigenschaft_patzer():
    r = calc_eigenschaft_probe(14, 20, 0)
    assert r['isPatzer'] is True

def test_eigenschaft_with_negative_mod():
    """Erschwernis -3 applied to wert before comparison."""
    r = calc_eigenschaft_probe(12, 10, -3)   # eff=9, roll=10 → fail
    assert r['success'] is False


# ---------------------------------------------------------------------------
# Tests for calc_kampf_probe
# ---------------------------------------------------------------------------

def test_kampf_success():
    assert calc_kampf_probe(7, 5, 0)['success'] is True

def test_kampf_failure():
    assert calc_kampf_probe(7, 10, 0)['success'] is False

def test_kampf_kritisch():
    r = calc_kampf_probe(7, 1, 0)
    assert r['isCrit'] is True
    assert r['success'] is True

def test_kampf_patzer():
    r = calc_kampf_probe(7, 20, 0)
    assert r['isPatzer'] is True
