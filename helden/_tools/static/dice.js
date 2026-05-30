/**
 * dice.js — DSA 4.1 dice rolling: pure math + floating panel controller.
 *
 * Pure math on window.Dice.* — no DOM access, deterministic given fixed inputs.
 * Panel controller (openPanel, event binding) follows in Task 5.
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
