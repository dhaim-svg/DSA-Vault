# Phase 2: Würfelintegration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add full DSA 4.1 dice rolling to the dashboard — talent/spell probes (3W20+TaW/ZfW), attribute probes (1W20), and combat AT/PA+damage — all surfaced via a sticky floating panel that supports both auto-roll and manual entry.

**Architecture:** A new `dice.js` exposes pure math functions on `window.Dice` and a `openPanel(config)` controller. The template gains a `window.DSA` JSON data-blob (eigenschaft values, vitals, slug) and `data-*` trigger attributes on talent/spell/eigenschaft/combat rows. All dice logic is Tier B (client-only); PATCH to the server only fires when the user explicitly clicks "AsP/LeP abziehen".

**Tech Stack:** Vanilla JS (ES6, no framework), Python 3.10+ for test verification, existing Flask + Jinja2 pipeline.

---

## File Map

| Status | Path | Responsibility |
|--------|------|----------------|
| Create | `helden/_tools/static/dice.js` | Pure math functions (`window.Dice.*`) + floating panel controller + event binding |
| Create | `helden/_tools/tests/test_dice.py` | Python equivalents of the JS math functions, used as specification-by-example |
| Modify | `helden/_tools/templates/dashboard.html.j2` | `window.DSA` blob; `data-*` on talent/spell/hex/combat rows; panel HTML+CSS; `<script>` tag |

`held.py`, `server.py`, `held_writer.py`, `app.js`, `session.js` — **no changes**.

---

## Task 1: Write failing tests for dice calculation logic

**Files:**
- Create: `helden/_tools/tests/test_dice.py`

The JS math functions are purely deterministic given fixed dice inputs. These Python tests specify the exact expected behavior — implement them first, run them, confirm they fail, then use them to validate Task 2.

- [ ] **Step 1: Create test_dice.py**

```python
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
    # WY or 1WY
    m = re.fullmatch(r'(\d*)W(\d+)\s*([+-]\d+)?', s, re.IGNORECASE)
    if m:
        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
        bonus = int(m.group(3)) if m.group(3) else 0
        return {'count': count, 'sides': sides, 'bonus': bonus}
    # "1W+1" style (no explicit sides → W6)
    m = re.fullmatch(r'(\d*)W\s*([+-]\d+)', s, re.IGNORECASE)
    if m:
        count = int(m.group(1)) if m.group(1) else 1
        return {'count': count, 'sides': 6, 'bonus': int(m.group(2))}
    return None


def calc_talent_probe(eig3, taw, rolls, mod):
    """Calculate a 3W20 talent probe.

    eig3: list of 3 eigenschaft values (ints, may include None for ** slots)
    taw: Talentwert (int)
    rolls: list of 3 dice results (ints 1–20)
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
            # ** slot — shown but not counted
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
    """Calculate a 1W20 eigenschaft probe.

    wert: the eigenschaft value
    roll: the W20 result (1–20)
    mod: modifier applied to wert (negative = erschwerend)
    Returns dict with success, isCrit, isPatzer.
    """
    eff_wert = wert + mod
    return {
        'success': roll <= eff_wert or roll == 1,
        'isCrit': roll == 1,
        'isPatzer': roll == 20,
    }


def calc_kampf_probe(at_or_pa, roll, mod):
    """Calculate a 1W20 combat probe (AT or PA).

    at_or_pa: the AT-Basis or PA-Basis value
    roll: the W20 result (1–20)
    mod: modifier applied to value (negative = erschwerend)
    Returns dict with success, isCrit, isPatzer.
    """
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
    assert result['success'] is True  # overrides negative tap

def test_talent_probe_patzer():
    """Two 20s → Patzer."""
    result = calc_talent_probe([10, 10, 10], 10, [20, 20, 5], 0)
    assert result['isPatzer'] is True

def test_talent_probe_star_star_slot():
    """** slot (eig=None) is not counted in TaP* calculation."""
    result = calc_talent_probe([14, 13, None], 8, [10, 16, 18], 0)
    # fehl for slot 0: 0, slot 1: max(0,16-13)=3, slot 2 (None): 0
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
    r = calc_eigenschaft_probe(1, 1, -10)   # wert=1, mod=-10 → eff=-9, roll=1
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
```

- [ ] **Step 2: Run to confirm ALL tests fail (no implementation yet)**

```
python -m pytest helden/_tools/tests/test_dice.py -v 2>&1 | head -40
```

Expected: ImportErrors or NameErrors (functions not yet defined), all tests collected and failing. If they somehow pass, something is wrong.

- [ ] **Step 3: Commit the failing tests**

```
git add helden/_tools/tests/test_dice.py
git commit -m "test(dice): specify DSA 4.1 probe calculation via Python equivalents"
```

---

## Task 2: Implement dice.js — pure math functions

**Files:**
- Create: `helden/_tools/static/dice.js`

Implement the pure math side of `window.Dice`. No DOM access, no side effects. Every function must produce the same output as the Python equivalent in test_dice.py for identical inputs.

- [ ] **Step 1: Create dice.js with the core math functions**

```javascript
/**
 * dice.js — DSA 4.1 dice rolling: pure math + floating panel controller.
 *
 * Pure math on window.Dice.* — no DOM access, deterministic given fixed inputs.
 * Panel controller (openPanel, event binding) follows after the math section.
 *
 * Degrades gracefully when opened as file:// (no PATCH actions available).
 */
'use strict';

window.Dice = {};

// ---------------------------------------------------------------------------
// Pure math — mirrors test_dice.py exactly
// ---------------------------------------------------------------------------

/**
 * Roll n dice with the given number of sides.
 * Returns an array of n integers in [1, sides].
 */
window.Dice.roll = function(n, sides) {
  var result = [];
  for (var i = 0; i < n; i++) {
    result.push(Math.floor(Math.random() * sides) + 1);
  }
  return result;
};

/**
 * Parse a DSA dice string: "2W6+3", "1W+1", "W20", "3", etc.
 * Returns {count, sides, bonus} or null for unrecognised formats.
 * sides=null means a fixed value (pure integer string like "3").
 */
window.Dice.parseDiceString = function(s) {
  s = (s || '').trim();
  // Pure integer
  if (/^\d+$/.test(s)) {
    return { count: 1, sides: null, bonus: parseInt(s, 10) };
  }
  // WY or NWY with optional bonus: "2W6+3", "W20", "3W6-1"
  var m = s.match(/^(\d*)W(\d+)\s*([+-]\d+)?$/i);
  if (m) {
    return {
      count: m[1] ? parseInt(m[1], 10) : 1,
      sides: parseInt(m[2], 10),
      bonus: m[3] ? parseInt(m[3], 10) : 0,
    };
  }
  // "1W+1" style — implicit W6
  m = s.match(/^(\d*)W\s*([+-]\d+)$/i);
  if (m) {
    return {
      count: m[1] ? parseInt(m[1], 10) : 1,
      sides: 6,
      bonus: parseInt(m[2], 10),
    };
  }
  return null;
};

/**
 * Roll a parsed dice spec and return the total.
 * If sides is null (fixed value), return bonus directly.
 */
window.Dice.rollParsed = function(spec) {
  if (!spec) return null;
  if (spec.sides === null) return spec.bonus;
  var rolls = window.Dice.roll(spec.count, spec.sides);
  return rolls.reduce(function(a, b) { return a + b; }, 0) + spec.bonus;
};

/**
 * Calculate a 3W20 talent or spell probe.
 *
 * eig3: Array of 3 eigenschaft values (integers, or null for ** slots).
 * taw: Talentwert / ZfW (integer).
 * rolls: Array of 3 W20 results.
 * mod: Modifier on effTaW (negative = erschwerend).
 *
 * Returns { tap, success, isCrit, isPatzer, perSlot }
 */
window.Dice.calcTalentProbe = function(eig3, taw, rolls, mod) {
  var effTaw = taw + (mod || 0);
  var perSlot = [];
  var totalFehl = 0;
  for (var i = 0; i < 3; i++) {
    var roll = rolls[i];
    var eig = eig3[i];
    if (eig === null || eig === undefined) {
      perSlot.push({ roll: roll, eig: null, fehl: 0 });
    } else {
      var fehl = Math.max(0, roll - eig);
      totalFehl += fehl;
      perSlot.push({ roll: roll, eig: eig, fehl: fehl });
    }
  }
  var tap = effTaw - totalFehl;
  var ones = rolls.filter(function(r) { return r === 1; }).length;
  var twenties = rolls.filter(function(r) { return r === 20; }).length;
  var isCrit = ones >= 2;
  var isPatzer = twenties >= 2;
  return {
    tap: tap,
    success: tap >= 0 || isCrit,
    isCrit: isCrit,
    isPatzer: isPatzer,
    perSlot: perSlot,
  };
};

/**
 * Calculate a 1W20 eigenschaft probe.
 * Roll 1 is always critical success. Roll 20 is always patzer.
 */
window.Dice.calcEigProbe = function(wert, roll, mod) {
  var effWert = wert + (mod || 0);
  return {
    success: roll <= effWert || roll === 1,
    isCrit: roll === 1,
    isPatzer: roll === 20,
  };
};

/**
 * Calculate a 1W20 combat probe (AT or PA). Same rules as eigenschaft probe.
 */
window.Dice.calcKampfProbe = function(atOrPa, roll, mod) {
  var eff = atOrPa + (mod || 0);
  return {
    success: roll <= eff || roll === 1,
    isCrit: roll === 1,
    isPatzer: roll === 20,
  };
};

/**
 * Roll damage from a TP string and return {rolls, total, formula}.
 * Returns null if string cannot be parsed.
 */
window.Dice.calcSchaden = function(tpStr, bonusMod) {
  bonusMod = bonusMod || 0;
  var spec = window.Dice.parseDiceString(tpStr);
  if (!spec) return null;
  if (spec.sides === null) {
    return { rolls: [], total: spec.bonus + bonusMod, formula: tpStr };
  }
  var rolls = window.Dice.roll(spec.count, spec.sides);
  var total = rolls.reduce(function(a, b) { return a + b; }, 0) + spec.bonus + bonusMod;
  return { rolls: rolls, total: total, formula: tpStr };
};
```

- [ ] **Step 2: Run the Python tests — they should all pass now**

The Python functions in `test_dice.py` mirror the JS logic. If the logic is identical, all 22+ tests pass:

```
python -m pytest helden/_tools/tests/test_dice.py -v
```

Expected: **all tests PASS**. If any fail, fix the Python equivalent in test_dice.py to match the JS (or vice versa) until they agree.

- [ ] **Step 3: Verify dice.js syntax loads cleanly**

```
python helden/_tools/render-held.py illaen-baernhold
```

Expected: `Rendered -> output\...-dashboard.html` — no Jinja errors (the JS file isn't referenced in the template yet, so this just verifies nothing broke).

- [ ] **Step 4: Commit**

```
git add helden/_tools/static/dice.js
git commit -m "feat(dice): window.Dice math functions — parseDiceString, calcTalentProbe, calcEigProbe, calcKampfProbe, calcSchaden"
```

---

## Task 3: Template — window.DSA data blob + data-* trigger attributes

**Files:**
- Modify: `helden/_tools/templates/dashboard.html.j2`

Add the `window.DSA` JSON blob (so dice.js can read eigenschaft values without DOM scraping) and `data-*` trigger attributes on talent rows, spell rows, eigenschaft hexes, and combat values.

**Important context:** Read the template before editing. Key line numbers (as of Phase 1 commit):
- Line 811: `</style>` — CSS block goes just before here
- Line 985–997: Eigenschaft `.hex` loop
- Lines 1063–1074: Talent row loop (`{% for row in grp_rows %}`)
- Lines 1091–1116: Spell loop (`{% for z in held.zauber %}`)
- Lines 951–953: Kampfwerte `.minor` divs (AT-Basis, PA-Basis)
- Lines 1234–1246: Weapon card loop
- Lines 1366–1369: Bottom of body (script tags)

- [ ] **Step 1: Add window.DSA blob before `<script src="/static/app.js">`**

Find the line `<script src="/static/app.js"></script>` (around line 1368). Insert the `window.DSA` block BEFORE it:

```html
<script>
/* DSA character data for dice.js — regenerated on each render */
window.DSA = {
  eig: {
    MU: {{ held.eigenschaften.MU.aktuell }},
    KL: {{ held.eigenschaften.KL.aktuell }},
    IN: {{ held.eigenschaften.IN.aktuell }},
    CH: {{ held.eigenschaften.CH.aktuell }},
    FF: {{ held.eigenschaften.FF.aktuell }},
    GE: {{ held.eigenschaften.GE.aktuell }},
    KO: {{ held.eigenschaften.KO.aktuell }},
    KK: {{ held.eigenschaften.KK.aktuell }}
  },
  vitals: {
    LE: { current: {{ le.current }}, max: {{ le.max }} },
    AE: { current: {{ ae.current }}, max: {{ ae.max }} },
    AU: { current: {{ au.current }}, max: {{ au.max }} }
  },
  slug: "{{ slug }}"
};
</script>
```

Note: `le`, `ae`, `au` are already set as Jinja variables at lines 776–778.

- [ ] **Step 2: Add `data-eigenschaft` and `data-wert` to eigenschaft hex divs**

Find the `.hex` div (around line 988):
```html
    <div class="hex">
```

Change it to:
```html
    <div class="hex" data-eigenschaft="{{ abbr }}" data-wert="{{ e.get('aktuell', 0) }}">
```

This is one line change inside the `{% for abbr in eig_order %}` loop.

- [ ] **Step 3: Add `data-probe`/`data-taw`/`data-name` to talent rows**

Find the talent-row div (around line 1065):
```html
      <div class="talent-row {{ cls }}">
```

Change it to (guard: only on rows with a real 3-eigenschaft probe):
```html
      <div class="talent-row {{ cls }}"{% if not is_kampf and '/' in (row.probe or '') %} data-probe="{{ row.probe }}" data-taw="{{ row.taw }}" data-name="{{ row.name }}"{% endif %}>
```

- [ ] **Step 4: Add `data-*` to spell rows**

Find the spell data-div (around line 1095):
```html
  <div class="spell">
```

Change it to (the header `.spell` at line 1087 has an inline style — target only the data rows):
```html
  <div class="spell"{% if '/' in (z.probe or '') %} data-probe="{{ z.probe }}" data-zfw="{{ z.zfw }}" data-name="{{ z.name }}" data-kosten="{{ z.kosten }}"{% endif %}>
```

- [ ] **Step 5: Add `data-at`/`data-pa` to Kampfwerte minor divs**

Find lines 952–953 in the Kampfwerte card:
```html
      <div class="minor"><span class="v" style="color:var(--accent-gold)">{{ at_bw.aktuell }}</span><span class="k">AT-Basis</span></div>
      <div class="minor"><span class="v" style="color:var(--accent-gold)">{{ pa_bw.aktuell }}</span><span class="k">PA-Basis</span></div>
```

Change to:
```html
      <div class="minor" data-at="{{ at_bw.aktuell }}"><span class="v" style="color:var(--accent-gold)">{{ at_bw.aktuell }}</span><span class="k">AT-Basis</span></div>
      <div class="minor" data-pa="{{ pa_bw.aktuell }}"><span class="v" style="color:var(--accent-gold)">{{ pa_bw.aktuell }}</span><span class="k">PA-Basis</span></div>
```

- [ ] **Step 6: Add `data-tp` to weapon card TP value**

Find the weapon-grid TP div (around line 1240):
```html
        <div><span class="k">TP</span><span class="v">{{ w.tp }}</span></div>
```

Change to:
```html
        <div data-tp="{{ w.tp }}"><span class="k">TP</span><span class="v">{{ w.tp }}</span></div>
```

- [ ] **Step 7: Verify render still works**

```
python helden/_tools/render-held.py illaen-baernhold
```

Expected: no errors. Then spot-check the rendered HTML:
```
grep -n "data-eigenschaft\|data-probe\|data-at\|data-tp\|window.DSA" output/illaen-baernhold-dashboard.html | head -20
```

Expected: lines showing `data-eigenschaft="MU"`, `data-probe="MU/..."`, `data-at="7"`, `data-tp="1W+1"`, and `window.DSA = {`.

- [ ] **Step 8: Commit**

```
git add helden/_tools/templates/dashboard.html.j2
git commit -m "feat(template): window.DSA data blob + data-* trigger attributes for dice.js"
```

---

## Task 4: Template — #dice-panel HTML + CSS

**Files:**
- Modify: `helden/_tools/templates/dashboard.html.j2`

Add the floating panel HTML structure and its CSS block. No JS yet — just the inert DOM structure that the controller will wire up in Task 5.

- [ ] **Step 1: Add dice panel CSS before `</style>` (line 811)**

Find `</style>` at line 811. Insert this CSS block immediately before it:

```css
/* ── Dice Panel ────────────────────────────────────────── */
.dice-panel {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: var(--card-bg, #f5ebd8);
  border-top: 2px solid var(--accent, #8b7355);
  padding: 12px 16px 14px;
  z-index: 200;
  box-shadow: 0 -4px 20px rgba(0,0,0,.18);
  font-family: var(--body, serif);
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: transform 0.2s ease;
}
.dice-panel.hidden { transform: translateY(100%); pointer-events: none; }
.dice-panel-header {
  display: flex;
  align-items: center;
  gap: 8px;
}
#dp-title {
  flex: 1;
  font-family: var(--display, serif);
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: .04em;
}
.dp-mode-btns { display: flex; gap: 4px; }
.dp-btn {
  padding: 6px 12px;
  min-width: 44px; min-height: 44px;
  border: 1.5px solid var(--accent, #8b7355);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 0.9rem;
  touch-action: manipulation;
  transition: background 0.12s;
}
.dp-btn.active, .dp-btn.primary {
  background: var(--accent, #8b7355);
  color: var(--bg, #fdf6e3);
}
.dp-btn:active { opacity: 0.75; }
.dp-eig-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 0.9rem;
  opacity: 0.85;
}
.dp-eig-slot { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.dp-eig-slot .dp-eig-abbr { font-size: 0.75rem; opacity: 0.7; }
.dp-eig-slot .dp-eig-val { font-weight: 700; }
.dp-dice-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
.dp-die {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.dp-die input[type=number] {
  width: 52px; height: 48px;
  text-align: center;
  font-size: 1.3rem;
  font-weight: 700;
  border: 1.5px solid var(--accent, #8b7355);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  -moz-appearance: textfield;
}
.dp-die input[type=number]::-webkit-inner-spin-button,
.dp-die input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
.dp-die-label { font-size: 0.7rem; opacity: 0.65; }
.dp-die-fehl { font-size: 0.8rem; color: var(--accent-blood, #8b1c2a); font-weight: 700; }
.dp-result {
  font-size: 1.1rem;
  font-weight: 700;
  padding: 6px 10px;
  border-radius: 6px;
  min-height: 2.2rem;
}
.dp-result.success { background: rgba(40,140,60,.15); color: #1a6b2a; }
.dp-result.fail    { background: rgba(180,30,30,.12); color: #8b1c2a; }
.dp-result.crit    { background: rgba(80,180,255,.15); color: #1a4a7a; }
.dp-result.patzer  { background: rgba(180,120,30,.15); color: #6b4010; }
.dp-controls {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.dp-controls label { font-size: 0.9rem; display: flex; align-items: center; gap: 6px; }
.dp-controls input[type=number] {
  width: 56px;
  padding: 4px;
  text-align: center;
  border: 1.5px solid var(--accent, #8b7355);
  border-radius: 4px;
  background: transparent;
  color: inherit;
  font-size: 1rem;
  -moz-appearance: textfield;
}
.dp-controls input[type=number]::-webkit-inner-spin-button,
.dp-controls input[type=number]::-webkit-outer-spin-button { -webkit-appearance: none; }
.dp-action { display: flex; gap: 8px; flex-wrap: wrap; }
/* Clickable rows */
.talent-row[data-probe], .spell[data-probe], .hex[data-eigenschaft],
.minor[data-at], .minor[data-pa], [data-tp] {
  cursor: pointer;
  transition: background 0.1s;
}
.talent-row[data-probe]:hover, .spell[data-probe]:hover,
.hex[data-eigenschaft]:hover, .minor[data-at]:hover, .minor[data-pa]:hover,
[data-tp]:hover { background: rgba(139,115,85,.1); border-radius: 4px; }
@media print { .dice-panel { display: none !important; } }
```

- [ ] **Step 2: Add #dice-panel HTML before `</body>`**

Find `<div id="save-indicator"></div>` near the bottom of the file (around line 1367). Insert the dice panel HTML BEFORE it:

```html
<div id="dice-panel" class="dice-panel hidden">
  <div class="dice-panel-header">
    <span id="dp-title">🎲 Probe</span>
    <span class="dp-mode-btns">
      <button id="dp-auto" class="dp-btn active" type="button">Auto</button>
      <button id="dp-manual" class="dp-btn" type="button">Manuell</button>
    </span>
    <button id="dp-close" class="dp-btn" type="button" aria-label="Panel schließen">✕</button>
  </div>
  <div id="dp-eig-row" class="dp-eig-row"></div>
  <div id="dp-dice-row" class="dp-dice-row"></div>
  <div id="dp-result" class="dp-result"></div>
  <div class="dp-controls">
    <label>Erschwernis&thinsp;<input id="dp-mod" type="number" value="0" min="-20" max="20"></label>
    <button id="dp-roll" class="dp-btn primary" type="button">🔁 Neu würfeln</button>
  </div>
  <div id="dp-action" class="dp-action"></div>
</div>
```

- [ ] **Step 3: Add script tag for dice.js after session.js**

Find `<script src="/static/session.js"></script>` near end of file. Add on the next line:

```html
<script src="/static/dice.js"></script>
```

- [ ] **Step 4: Verify render + panel structure is in output**

```
python helden/_tools/render-held.py illaen-baernhold
```
```
grep -n "dice-panel\|dp-title\|dp-roll" output/illaen-baernhold-dashboard.html | head -10
```

Expected: lines showing the panel structure.

- [ ] **Step 5: Commit**

```
git add helden/_tools/templates/dashboard.html.j2
git commit -m "feat(template): #dice-panel HTML + CSS + dice.js script tag"
```

---

## Task 5: dice.js — panel controller + event binding

**Files:**
- Modify: `helden/_tools/static/dice.js` (append controller code after existing math functions)

Wire up the `openPanel(config)` function and all event listeners. After this task, the full dice experience works in the browser.

- [ ] **Step 1: Append the panel controller to dice.js**

Open `helden/_tools/static/dice.js`. After the last line (the closing of `window.Dice.calcSchaden`), append:

```javascript

// ---------------------------------------------------------------------------
// Panel controller
// ---------------------------------------------------------------------------

(function () {
  'use strict';

  var panel = null;       // set on DOMContentLoaded
  var currentConfig = {}; // the last openPanel config
  var isManual = false;

  // ------------------------------------------------------------------
  // Parse probe string "MU/GE/KK" → [eig1value, eig2value, eig3value]
  // eig may be null for "**" slots.
  // Returns null if the probe is not a 3-eigenschaft formula.
  // ------------------------------------------------------------------
  function parseProbe(probeStr) {
    if (!probeStr || probeStr.indexOf('/') === -1) return null;
    var parts = probeStr.split('/');
    if (parts.length !== 3) return null;
    return parts.map(function (abbr) {
      abbr = abbr.trim().toUpperCase();
      if (abbr === '**') return null;
      var v = window.DSA && window.DSA.eig && window.DSA.eig[abbr];
      return (v !== undefined) ? v : null;
    });
  }

  // ------------------------------------------------------------------
  // Get current Wunden penalty from the DOM
  // ------------------------------------------------------------------
  function getWundMod() {
    // Read wunden count from DOM anchor set by session.js/template.
    // DSA 4.1 simplified rule: each wound = -2 on all checks.
    var el = document.querySelector('[data-wunden]');
    var w = el ? parseInt(el.dataset.wunden, 10) : 0;
    return w > 0 ? -(w * 2) : 0;
  }

  // ------------------------------------------------------------------
  // PATCH helper (independent of app.js)
  // ------------------------------------------------------------------
  function patchValue(locator) {
    if (location.protocol === 'file:') return;
    fetch('/api/held/' + locator.slug + '/value', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locator),
    }).catch(console.error);
  }

  // ------------------------------------------------------------------
  // Render panel content for current state
  // ------------------------------------------------------------------
  function render(rolls) {
    var cfg = currentConfig;
    var mod = parseInt(document.getElementById('dp-mod').value, 10) || 0;
    var eigRow = document.getElementById('dp-eig-row');
    var diceRow = document.getElementById('dp-dice-row');
    var resultEl = document.getElementById('dp-result');
    var actionEl = document.getElementById('dp-action');

    eigRow.innerHTML = '';
    diceRow.innerHTML = '';
    resultEl.innerHTML = '';
    resultEl.className = 'dp-result';
    actionEl.innerHTML = '';

    if (cfg.type === 'talent' || cfg.type === 'zauber') {
      var eig3 = parseProbe(cfg.probe);
      if (!eig3) { resultEl.textContent = 'Keine auswürfelbare Probe (fehlende Eigenschaft)'; return; }
      var taw = cfg.type === 'zauber' ? cfg.zfw : cfg.taw;
      var probeAbbrs = cfg.probe.split('/');

      // Eigenschaft display
      probeAbbrs.forEach(function (abbr, i) {
        abbr = abbr.trim().toUpperCase();
        var val = eig3[i];
        var slot = document.createElement('div');
        slot.className = 'dp-eig-slot';
        slot.innerHTML = '<span class="dp-eig-abbr">' + abbr + '</span>' +
          '<span class="dp-eig-val">' + (val !== null ? val : '?') + '</span>';
        eigRow.appendChild(slot);
      });

      // Dice display
      var res = window.Dice.calcTalentProbe(eig3, taw, rolls, mod);
      for (var i = 0; i < 3; i++) {
        var die = document.createElement('div');
        die.className = 'dp-die';
        var inp = document.createElement('input');
        inp.type = 'number'; inp.min = 1; inp.max = 20;
        inp.value = rolls[i];
        inp.readOnly = !isManual;
        if (!isManual) inp.setAttribute('readonly', 'readonly');
        inp.dataset.idx = i;
        inp.addEventListener('input', function () {
          if (!isManual) return;
          var newRolls = currentRolls.slice();
          newRolls[parseInt(this.dataset.idx, 10)] = parseInt(this.value, 10) || 1;
          render(newRolls);
        });
        die.appendChild(inp);
        var fehlEl = document.createElement('span');
        fehlEl.className = 'dp-die-label';
        var eig = eig3[i];
        if (eig !== null) {
          var fehl = res.perSlot[i].fehl;
          fehlEl.textContent = fehl > 0 ? '−' + fehl : '✓';
          fehlEl.className = fehl > 0 ? 'dp-die-fehl' : 'dp-die-label';
        } else {
          fehlEl.textContent = '**';
        }
        die.appendChild(fehlEl);
        diceRow.appendChild(die);
      }
      currentRolls = rolls.slice();

      // Result
      var label = cfg.type === 'zauber' ? 'ZfP*' : 'TaP*';
      if (res.isPatzer) {
        resultEl.textContent = '⚠️ Patzer! Zwei 20en (' + label + ' ignoriert)';
        resultEl.classList.add('patzer');
      } else if (res.isCrit) {
        resultEl.textContent = '⭐ Kritisch! ' + label + '* = ' + res.tap + ' (automatischer Erfolg)';
        resultEl.classList.add('crit');
      } else if (res.success) {
        resultEl.textContent = '✅ Erfolg — ' + label + '* = ' + res.tap;
        resultEl.classList.add('success');
      } else {
        resultEl.textContent = '❌ Misserfolg — ' + label + '* = ' + res.tap;
        resultEl.classList.add('fail');
      }

      // Action: AsP abziehen after Zauber success
      if (cfg.type === 'zauber' && res.success && !res.isPatzer && cfg.kosten) {
        var aspCost = parseInt(cfg.kosten, 10) || 0;
        if (aspCost > 0) {
          var slug = (window.DSA && window.DSA.slug) || 'illaen-baernhold';
          var curAe = window.DSA && window.DSA.vitals && window.DSA.vitals.AE.current;
          var newAe = Math.max(0, (curAe || 0) - aspCost);
          var btn = document.createElement('button');
          btn.className = 'dp-btn';
          btn.type = 'button';
          btn.textContent = aspCost + ' AsP abziehen (' + curAe + '→' + newAe + ')';
          btn.onclick = function () {
            patchValue({
              kind: 'table_cell', file: '_illaen.md',
              section_path: ['Eigenschaften & Basiswerte', 'Basiswerte'],
              row_key: { column: 'Basiswert', match: 'Astralenergie (AE)' },
              column: 'Akt.', value: String(newAe), slug: slug,
            });
            if (window.DSA && window.DSA.vitals) window.DSA.vitals.AE.current = newAe;
            btn.disabled = true;
            btn.textContent = '✓ AsP abgezogen';
          };
          actionEl.appendChild(btn);
        }
      }

    } else if (cfg.type === 'eigenschaft') {
      var roll = rolls[0];
      var res = window.Dice.calcEigProbe(cfg.wert, roll, mod);
      var inp = document.createElement('input');
      inp.type = 'number'; inp.min = 1; inp.max = 20; inp.value = roll;
      inp.readOnly = !isManual;
      if (!isManual) inp.setAttribute('readonly', 'readonly');
      inp.addEventListener('input', function () {
        if (!isManual) return;
        render([parseInt(this.value, 10) || 1]);
      });
      diceRow.appendChild(inp);
      currentRolls = [roll];
      eigRow.innerHTML = '<span>' + cfg.abbr + '(' + cfg.wert + ')</span>';

      if (res.isPatzer) { resultEl.textContent = '⚠️ Patzer! (20)'; resultEl.classList.add('patzer'); }
      else if (res.isCrit) { resultEl.textContent = '⭐ Kritisch! (1) — immer Erfolg'; resultEl.classList.add('crit'); }
      else if (res.success) { resultEl.textContent = '✅ Erfolg (' + roll + ' ≤ ' + cfg.wert + ')'; resultEl.classList.add('success'); }
      else { resultEl.textContent = '❌ Misserfolg (' + roll + ' > ' + cfg.wert + ')'; resultEl.classList.add('fail'); }

    } else if (cfg.type === 'at' || cfg.type === 'pa') {
      var roll = rolls[0];
      var label = cfg.type === 'at' ? 'AT' : 'PA';
      var res = window.Dice.calcKampfProbe(cfg.atOrPa, roll, mod);
      var inp = document.createElement('input');
      inp.type = 'number'; inp.min = 1; inp.max = 20; inp.value = roll;
      inp.readOnly = !isManual;
      if (!isManual) inp.setAttribute('readonly', 'readonly');
      inp.addEventListener('input', function () {
        if (!isManual) return;
        render([parseInt(this.value, 10) || 1]);
      });
      diceRow.appendChild(inp);
      currentRolls = [roll];
      eigRow.innerHTML = '<span>' + label + '-Basis: ' + cfg.atOrPa + '</span>';

      if (res.isPatzer) { resultEl.textContent = '⚠️ Patzer! (20)'; resultEl.classList.add('patzer'); }
      else if (res.isCrit) { resultEl.textContent = '⭐ Kritisch! (1)'; resultEl.classList.add('crit'); }
      else if (res.success) {
        resultEl.textContent = '✅ ' + (cfg.type === 'at' ? 'Treffer' : 'Pariert') + '! (' + roll + ' ≤ ' + cfg.atOrPa + ')';
        resultEl.classList.add('success');
        if (cfg.type === 'at' && cfg.tpStr) {
          var btn = document.createElement('button');
          btn.className = 'dp-btn';
          btn.type = 'button';
          btn.textContent = 'Schaden würfeln (' + cfg.tpStr + ')';
          btn.onclick = function () {
            window.Dice.openPanel({ type: 'schaden', name: 'Schaden', tpStr: cfg.tpStr, slug: cfg.slug });
          };
          actionEl.appendChild(btn);
        }
      } else {
        resultEl.textContent = '❌ ' + (cfg.type === 'at' ? 'Verfehlt' : 'Nicht pariert') + '! (' + roll + ' > ' + cfg.atOrPa + ')';
        resultEl.classList.add('fail');
        if (cfg.type === 'pa') {
          // Offer LeP deduction — damage unknown, let user enter
          var btn = document.createElement('button');
          btn.className = 'dp-btn';
          btn.type = 'button';
          btn.textContent = 'SP kassiert — LeP abziehen…';
          btn.onclick = function () {
            var sp = parseInt(prompt('Wie viele SP (Schaden nach RS)?', '0'), 10) || 0;
            if (sp <= 0) return;
            var slug = (window.DSA && window.DSA.slug) || 'illaen-baernhold';
            var cur = window.DSA && window.DSA.vitals && window.DSA.vitals.LE.current;
            var newLe = Math.max(0, (cur || 0) - sp);
            patchValue({
              kind: 'table_cell', file: '_illaen.md',
              section_path: ['Eigenschaften & Basiswerte', 'Basiswerte'],
              row_key: { column: 'Basiswert', match: 'Lebensenergie (LE)' },
              column: 'Akt.', value: String(newLe), slug: slug,
            });
            if (window.DSA && window.DSA.vitals) window.DSA.vitals.LE.current = newLe;
            btn.disabled = true;
            btn.textContent = '✓ LeP abgezogen (' + cur + '→' + newLe + ')';
          };
          actionEl.appendChild(btn);
        }
      }

    } else if (cfg.type === 'schaden') {
      // Use the `rolls` parameter (set by autoRoll() on first open; by currentRolls on re-render).
      var spec = window.Dice.parseDiceString(cfg.tpStr || '0');
      if (spec && spec.sides) {
        // rolls is already fresh from autoRoll() on open, or currentRolls on manual re-render
        currentRolls = rolls.slice();
        var total = rolls.reduce(function (a, b) { return a + b; }, 0) + (spec.bonus || 0);
        rolls.forEach(function (r, idx) {
          var inp = document.createElement('input');
          inp.type = 'number'; inp.min = 1; inp.max = spec.sides; inp.value = r;
          inp.readOnly = !isManual;
          if (!isManual) inp.setAttribute('readonly', 'readonly');
          inp.dataset.idx = idx;
          inp.addEventListener('input', function () {
            if (!isManual) return;
            var newRolls = currentRolls.slice();
            newRolls[parseInt(this.dataset.idx, 10)] = parseInt(this.value, 10) || 1;
            render(newRolls);
          });
          diceRow.appendChild(inp);
        });
        resultEl.textContent = 'Schaden: ' + total + ' TP (' + cfg.tpStr + ')';
        resultEl.classList.add('success');
      } else if (spec) {
        // Fixed numeric value — no dice to show
        currentRolls = [];
        resultEl.textContent = 'Schaden: ' + spec.bonus + ' TP (fix)';
        resultEl.classList.add('success');
      } else {
        currentRolls = [];
        resultEl.textContent = 'Unbekanntes TP-Format: ' + cfg.tpStr;
        resultEl.classList.add('fail');
      }
    }
  }

  var currentRolls = [];

  function autoRoll() {
    var cfg = currentConfig;
    if (cfg.type === 'talent' || cfg.type === 'zauber') {
      return window.Dice.roll(3, 20);
    } else if (cfg.type === 'eigenschaft' || cfg.type === 'at' || cfg.type === 'pa') {
      return window.Dice.roll(1, 20);
    } else if (cfg.type === 'schaden') {
      var spec = window.Dice.parseDiceString(cfg.tpStr || '0');
      if (spec && spec.sides) return window.Dice.roll(spec.count, spec.sides);
      return [];
    }
    return [];
  }

  // ------------------------------------------------------------------
  // Public API
  // ------------------------------------------------------------------
  window.Dice.openPanel = function (config) {
    currentConfig = config;
    isManual = false;

    if (!panel) return; // DOM not ready

    document.getElementById('dp-title').textContent = '🎲 ' + (config.name || 'Probe');
    document.getElementById('dp-mod').value = getWundMod();
    document.getElementById('dp-auto').classList.add('active');
    document.getElementById('dp-manual').classList.remove('active');

    var rolls = autoRoll();
    render(rolls);
    panel.classList.remove('hidden');
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };

  // ------------------------------------------------------------------
  // Event binding (runs once on DOMContentLoaded)
  // ------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    panel = document.getElementById('dice-panel');
    if (!panel) return;

    document.getElementById('dp-close').addEventListener('click', function () {
      panel.classList.add('hidden');
    });

    document.getElementById('dp-auto').addEventListener('click', function () {
      isManual = false;
      this.classList.add('active');
      document.getElementById('dp-manual').classList.remove('active');
      render(autoRoll());
    });

    document.getElementById('dp-manual').addEventListener('click', function () {
      isManual = true;
      this.classList.add('active');
      document.getElementById('dp-auto').classList.remove('active');
      render(currentRolls);
    });

    document.getElementById('dp-roll').addEventListener('click', function () {
      if (isManual) return; // "Neu würfeln" disabled in manual mode (user controls the dice)
      render(autoRoll());
    });

    document.getElementById('dp-mod').addEventListener('change', function () {
      render(currentRolls);
    });

    // Talent rows
    document.querySelectorAll('.talent-row[data-probe]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.Dice.openPanel({
          type: 'talent',
          name: el.dataset.name,
          probe: el.dataset.probe,
          taw: parseInt(el.dataset.taw, 10) || 0,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // Spell rows
    document.querySelectorAll('.spell[data-probe]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        // Don't trigger on details/summary clicks
        if (e.target.closest('details') || e.target.closest('a')) return;
        window.Dice.openPanel({
          type: 'zauber',
          name: el.dataset.name,
          probe: el.dataset.probe,
          zfw: parseInt(el.dataset.zfw, 10) || 0,
          kosten: el.dataset.kosten,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // Eigenschaft hexes
    document.querySelectorAll('.hex[data-eigenschaft]').forEach(function (el) {
      el.addEventListener('click', function () {
        var abbr = el.dataset.eigenschaft;
        window.Dice.openPanel({
          type: 'eigenschaft',
          name: abbr + '-Probe',
          abbr: abbr,
          wert: parseInt(el.dataset.wert, 10) || 0,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // AT-Basis
    document.querySelectorAll('.minor[data-at]').forEach(function (el) {
      el.addEventListener('click', function () {
        // Find first weapon TP for the Schaden follow-up
        var wpTp = (document.querySelector('[data-tp]') || {}).dataset.tp || '';
        window.Dice.openPanel({
          type: 'at',
          name: 'Attacke',
          atOrPa: parseInt(el.dataset.at, 10) || 0,
          tpStr: wpTp,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // PA-Basis
    document.querySelectorAll('.minor[data-pa]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.Dice.openPanel({
          type: 'pa',
          name: 'Parade',
          atOrPa: parseInt(el.dataset.pa, 10) || 0,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // Weapon TP
    document.querySelectorAll('[data-tp]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.Dice.openPanel({
          type: 'schaden',
          name: 'Schaden',
          tpStr: el.dataset.tp,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });
  });

}());
```

- [ ] **Step 2: Run all Python tests — confirm still passing**

```
python -m pytest helden/_tools/tests/ -v
```

Expected: all 9 held_writer tests + all dice tests pass.

- [ ] **Step 3: Verify the template still renders**

```
python helden/_tools/render-held.py illaen-baernhold
```

Expected: no errors.

- [ ] **Step 4: Commit**

```
git add helden/_tools/static/dice.js
git commit -m "feat(dice): panel controller — openPanel, event binding, AsP/LeP PATCH actions"
```

---

## Task 6: Integration verification + final commit

- [ ] **Step 1: Run all tests**

```
python -m pytest helden/_tools/tests/ -v
```

Expected: all tests PASS (9 writer + dice tests).

- [ ] **Step 2: Start server and verify dice panel in browser**

```
python helden/_tools/render-held.py serve illaen-baernhold --open
```

Manual checks in the browser:

- [ ] Click a talent row (e.g. Körperbeherrschung) → panel opens, shows probe (GE/GE/KK), 3 dice values, TaP* result
- [ ] Click "Manuell" → input fields become editable, changing a value recalculates result
- [ ] Click "Auto" → new random roll, inputs lock again
- [ ] Click a spell row (e.g. Armatrutz) → probe loads, ZfW shown; after success → "AsP abziehen" button appears
- [ ] Click AsP button → `git diff _illaen.md` shows AE Akt. decreased; button shows "✓ abgezogen"
- [ ] Click an eigenschaft hex (e.g. MU) → 1W20 panel opens
- [ ] Click AT-Basis in Kampfwerte card → AT probe; on Treffer → "Schaden würfeln" button → opens damage panel
- [ ] Click PA-Basis → PA probe; on Nicht-pariert → "SP kassiert" button → prompt → `git diff _illaen.md` shows LE Akt. decreased
- [ ] Click weapon card TP div → Schaden panel with correct format
- [ ] Wunden set to 1 (tap "Wunden +" in session widget) → open talent panel → Erschwernis pre-filled at -2
- [ ] Print preview: panel hidden (print CSS)
- [ ] `Ctrl-C` server, open `output/illaen-baernhold-dashboard.html` as file:// → panel absent (no serve mode), no JS errors

- [ ] **Step 3: Reset any test changes to _illaen.md**

```
git checkout helden/illaen-baernhold/_illaen.md
```

- [ ] **Step 4: Final commit**

```
git add -A
git status   # verify only expected files (dice.js, template, tests)
git commit -m "feat(phase-2): Würfelintegration complete — talent/spell/eigenschaft/combat probes + floating dice panel"
```

- [ ] **Step 5: Push**

```
git push origin master
```

---

## Summary

After Task 6:
- Floating dice panel at bottom of dashboard (visible on demand, hidden in print)
- Talent probes: click any talent row with a `/`-separated probe → 3W20 + TaP*
- Spell probes: click any spell row → ZfW-based, AsP-abziehen button after success
- Eigenschaft probes: click any eigenschaft hex → 1W20
- Combat: AT-Basis → attack probe → damage on hit; PA-Basis → defense probe → LeP deduction on fail
- Auto-roll + manual entry (toggle in panel)
- Erschwernis pre-filled from current Wunden, editable
- All dice logic is Tier B (client-only); PATCH fires only on explicit user action
- 9 writer tests + all dice calculation tests green
