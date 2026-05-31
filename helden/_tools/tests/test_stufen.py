"""Tests for _compute_ap_bis_naechste — AP threshold logic for Stufenaufstieg."""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import _compute_ap_bis_naechste


# ---------------------------------------------------------------------------
# Unit tests: _compute_ap_bis_naechste
# ---------------------------------------------------------------------------

def test_illaen_exact_numbers_returns_none():
    """Illaen: stufe=3, ap_gesamt=3850 — far exceeds threshold 1500 → None."""
    result = _compute_ap_bis_naechste(stufe=3, ap_gesamt=3850)
    assert result is None, f"Expected None, got {result!r} (must not be negative)"


def test_normal_case_returns_remaining_ap():
    """Normal progression: stufe=3, ap_gesamt=600 → needs 900 more to reach Stufe 4 (1500)."""
    result = _compute_ap_bis_naechste(stufe=3, ap_gesamt=600)
    assert result == 900


def test_exactly_at_threshold_returns_none():
    """Exactly at threshold: stufe=3, ap_gesamt=1500 → AP requirement met → None."""
    result = _compute_ap_bis_naechste(stufe=3, ap_gesamt=1500)
    assert result is None


def test_max_stufe_returns_none():
    """Max Stufe (10): no next Stufe exists → None."""
    result = _compute_ap_bis_naechste(stufe=10, ap_gesamt=20000)
    assert result is None


# ---------------------------------------------------------------------------
# Additional edge cases
# ---------------------------------------------------------------------------

def test_one_ap_below_threshold_returns_one():
    """One AP short of threshold: stufe=3, ap_gesamt=1499 → 1 AP remaining."""
    result = _compute_ap_bis_naechste(stufe=3, ap_gesamt=1499)
    assert result == 1


def test_stufe_1_to_2_normal():
    """Low-level character: stufe=1, ap_gesamt=100 → needs 200 more for Stufe 2 (300)."""
    result = _compute_ap_bis_naechste(stufe=1, ap_gesamt=100)
    assert result == 200


def test_stufe_9_to_10_normal():
    """Near max: stufe=9, ap_gesamt=14000 → needs 4900 more for Stufe 10 (18900)."""
    result = _compute_ap_bis_naechste(stufe=9, ap_gesamt=14000)
    assert result == 4900


def test_result_never_negative():
    """Invariant: the function must never return a negative number."""
    test_cases = [
        (3, 3850),   # Illaen
        (4, 5000),   # past next threshold
        (2, 400),    # slightly over Stufe 2 threshold
        (1, 999),    # way over Stufe 2 threshold
    ]
    for stufe, ap in test_cases:
        result = _compute_ap_bis_naechste(stufe=stufe, ap_gesamt=ap)
        assert result is None or result > 0, (
            f"stufe={stufe}, ap={ap}: got {result!r} — must be None or positive"
        )
