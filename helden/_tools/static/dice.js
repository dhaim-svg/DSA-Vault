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
  // Negative effective TaW (talentregeln.md:24): the overflow is applied as
  // a per-die Erschwernis on each attribute check, not subtracted wholesale
  // from tap — otherwise tap = effTaw - totalFehl is negative for every
  // possible roll and the probe becomes unwinnable. When effTaw >= 0 this
  // is 0 and the formula below is identical to the original.
  var overflow = Math.min(effTaw, 0);
  var perSlot = [];
  var totalFehl = 0;
  for (var i = 0; i < 3; i++) {
    var roll = rolls[i];
    var eig = eig3[i];
    if (eig === null || eig === undefined) {
      perSlot.push({ roll: roll, eig: null, fehl: 0 });
    } else {
      var fehl = Math.max(0, roll - (eig + overflow));
      totalFehl += fehl;
      perSlot.push({ roll: roll, eig: eig, fehl: fehl });
    }
  }
  var ones = rolls.filter(function(r) { return r === 1; }).length;
  var twenties = rolls.filter(function(r) { return r === 20; }).length;
  var isCrit = ones >= 2;
  var isPatzer = twenties >= 2;
  var tap, success;
  if (effTaw >= 0) {
    tap = effTaw - totalFehl;
    success = tap >= 0 || isCrit;
  } else {
    // All three (non-**) attribute checks passed → probe besteht, but
    // TaP* mirrors the negative effective TaW rather than going positive.
    tap = totalFehl === 0 ? effTaw : effTaw - totalFehl;
    success = totalFehl === 0 || isCrit;
  }
  return {
    tap: tap,
    success: success,
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

// ---------------------------------------------------------------------------
// Panel controller
// ---------------------------------------------------------------------------

(function () {
  'use strict';

  var panel = null;       // set on DOMContentLoaded
  var currentConfig = {}; // the last openPanel config
  var currentRolls = [];  // rolls from the last render call
  var isManual = false;

  // ------------------------------------------------------------------
  // Wound reduction of one Eigenschaft VALUE (negative number or 0). WdS S. 57: a wound
  // lowers the attribute GE itself, so the lower value applies in every probe that uses
  // GE (Talente/Zauber) — same as the "GE 13→9" overlay. Wounds only, never the Zustand
  // chips (those act via the panel modifier dp-mod and would count twice). Without
  // session.js (file://) the same wound rule is read from [data-wunden].
  // ------------------------------------------------------------------
  function wundAttrMod(abbr) {
    if (window.DSASession && window.DSASession.attrMod) return window.DSASession.attrMod(abbr);
    if (!/^(MU|KL|IN|CH|FF|GE|KO|KK)$/.test(abbr)) return 0;
    var el = document.querySelector('[data-wunden]');
    var w = el ? parseInt(el.dataset.wunden, 10) || 0 : 0;
    return window.DSAWundregeln.wundMod(w, abbr);
  }

  // ------------------------------------------------------------------
  // Parse probe string "MU/GE/KK" → [eig1value, eig2value, eig3value]
  // (wound-reduced, see wundAttrMod). eig may be null for "**" slots or
  // missing entries in window.DSA.eig.
  // Returns null if not a 3-eigenschaft formula.
  // ------------------------------------------------------------------
  function parseProbe(probeStr) {
    if (!probeStr || probeStr.indexOf('/') === -1) return null;
    var parts = probeStr.split('/');
    if (parts.length !== 3) return null;
    return parts.map(function (abbr) {
      abbr = abbr.trim().toUpperCase();
      if (abbr === '**') return null;
      var v = window.DSA && window.DSA.eig && window.DSA.eig[abbr];
      if (v === undefined || v === null) return null;
      return v + wundAttrMod(abbr);
    });
  }

  // ------------------------------------------------------------------
  // Wound/Zustand modifier for a probe, as a negative number or 0 (dp-mod adds
  // baseMod on top). Scoped by probe type (WdS S. 57 — see wundregeln.js):
  //   at -> 'AT', pa -> 'PA', eigenschaft -> cfg.abbr, talent -> 'talent',
  //   zauber -> 'zauber'; schaden and anything unknown -> 0 (Wunden senken keine TP).
  // Delegates to session.js's probeMod() (wounds + Zustand chips). Without
  // session.js (file://) only the wound rule applies, read from [data-wunden].
  // ------------------------------------------------------------------
  function getWundMod(cfg) {
    var ziel;
    switch (cfg && cfg.type) {
      case 'at': ziel = 'AT'; break;
      case 'pa': ziel = 'PA'; break;
      case 'eigenschaft': ziel = cfg.abbr; break;
      case 'talent': ziel = 'talent'; break;
      case 'zauber': ziel = 'zauber'; break;
      default: return 0;
    }
    if (window.DSASession && window.DSASession.probeMod) {
      return window.DSASession.probeMod(ziel);
    }
    var el = document.querySelector('[data-wunden]');
    var w = el ? parseInt(el.dataset.wunden, 10) || 0 : 0;
    return window.DSAWundregeln.wundMod(w, ziel);
  }

  // ------------------------------------------------------------------
  // PATCH helper — independent of app.js
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
  // Determine rolls for current config in auto mode
  // ------------------------------------------------------------------
  function autoRoll() {
    var cfg = currentConfig;
    if (cfg.type === 'talent' || cfg.type === 'zauber') {
      return window.Dice.roll(3, 20);
    }
    if (cfg.type === 'eigenschaft' || cfg.type === 'at' || cfg.type === 'pa') {
      return window.Dice.roll(1, 20);
    }
    if (cfg.type === 'schaden') {
      var spec = window.Dice.parseDiceString(cfg.tpStr || '0');
      if (spec && spec.sides) return window.Dice.roll(spec.count, spec.sides);
    }
    return [];
  }

  // ------------------------------------------------------------------
  // Render panel content for a given set of rolls
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
      if (!eig3) {
        resultEl.textContent = 'Keine auswürfelbare Probe (fehlende Eigenschaft)';
        return;
      }
      var taw = cfg.type === 'zauber' ? (cfg.zfw || 0) : (cfg.taw || 0);
      var probeAbbrs = cfg.probe.split('/');
      var res = window.Dice.calcTalentProbe(eig3, taw, rolls, mod);

      // Eigenschaft display row
      probeAbbrs.forEach(function (abbr, i) {
        abbr = abbr.trim().toUpperCase();
        var val = eig3[i];
        var slot = document.createElement('div');
        slot.className = 'dp-eig-slot';
        slot.innerHTML =
          '<span class="dp-eig-abbr">' + abbr + '</span>' +
          '<span class="dp-eig-val">' + (val !== null && val !== undefined ? val : '?') + '</span>';
        eigRow.appendChild(slot);
      });

      // Dice inputs
      for (var i = 0; i < 3; i++) {
        (function (idx) {
          var die = document.createElement('div');
          die.className = 'dp-die';
          var inp = document.createElement('input');
          inp.type = 'number'; inp.min = 1; inp.max = 20;
          inp.value = rolls[idx];
          if (!isManual) inp.setAttribute('readonly', 'readonly');
          inp.addEventListener('input', function () {
            if (!isManual) return;
            var newRolls = currentRolls.slice();
            newRolls[idx] = Math.max(1, Math.min(20, parseInt(this.value, 10) || 1));
            render(newRolls);
          });
          die.appendChild(inp);
          var fehlEl = document.createElement('span');
          var eig = eig3[idx];
          if (eig !== null && eig !== undefined) {
            var fehl = res.perSlot[idx].fehl;
            fehlEl.className = fehl > 0 ? 'dp-die-fehl' : 'dp-die-label';
            fehlEl.textContent = fehl > 0 ? '−' + fehl : '✓';
          } else {
            fehlEl.className = 'dp-die-label';
            fehlEl.textContent = '**';
          }
          die.appendChild(fehlEl);
          diceRow.appendChild(die);
        })(i);
      }
      currentRolls = rolls.slice();

      // Result line
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
          var slug = (window.DSA && window.DSA.slug) || '';
          var curAe = (window.DSA && window.DSA.vitals && window.DSA.vitals.AE && window.DSA.vitals.AE.current) || 0;
          var newAe = Math.max(0, curAe - aspCost);
          var aspBtn = document.createElement('button');
          aspBtn.className = 'dp-btn';
          aspBtn.type = 'button';
          aspBtn.textContent = aspCost + ' AsP abziehen (' + curAe + '→' + newAe + ')';
          aspBtn.onclick = function () {
            patchValue({
              kind: 'table_cell', file: '_illaen.md',
              section_path: ['Eigenschaften & Basiswerte', 'Basiswerte'],
              row_key: { column: 'Basiswert', match: 'Astralenergie (AE)' },
              column: 'Akt.', value: String(newAe), slug: slug,
            });
            if (window.DSA && window.DSA.vitals && window.DSA.vitals.AE) {
              window.DSA.vitals.AE.current = newAe;
            }
            aspBtn.disabled = true;
            aspBtn.textContent = '✓ AsP abgezogen';
          };
          actionEl.appendChild(aspBtn);
        }
      }

      // Action: Zauberspeicher-Auslöseprobe result handling.
      // Reuses window.Zauberspeicher.handleEntleeren (zauberspeicher.js) — the
      // same PATCH flow as the manual "Entleeren" button — instead of a
      // second PATCH call. Plain Misslingen (not Patzer) does nothing further:
      // per the wiki source the stored spell "verpufft wirkungslos" but the
      // slot itself isn't described as cleared by this action alone.
      if (cfg.type === 'talent' && cfg.speicherSlot) {
        if (res.isPatzer) {
          var patzerBtn = document.createElement('button');
          patzerBtn.className = 'dp-btn';
          patzerBtn.type = 'button';
          patzerBtn.textContent = 'Patzer — alle Speicher entleeren…';
          patzerBtn.onclick = function () {
            if (!confirm('Patzer! Alle gespeicherten Zauber lösen sich ebenfalls aus. Alle Slots entleeren?')) return;
            if (!window.Zauberspeicher) return;
            patzerBtn.disabled = true;
            patzerBtn.textContent = '…';
            var btns = Array.prototype.slice.call(document.querySelectorAll('.slot-entleeren-btn'));
            // skipReload on every call — each PATCH runs independently, and a
            // per-call reload would navigate away and abort the others still
            // in flight (see zauberspeicher.js handleEntleeren). Wait for all
            // to settle, then reload exactly once.
            Promise.all(btns.map(function (btn) {
              return window.Zauberspeicher.handleEntleeren(btn, { skipReload: true });
            })).then(function () {
              window.location.reload();
            });
          };
          actionEl.appendChild(patzerBtn);
        } else if (res.success) {
          var slotNum = cfg.speicherSlot;
          var ausloesenBtn = document.createElement('button');
          ausloesenBtn.className = 'dp-btn';
          ausloesenBtn.type = 'button';
          ausloesenBtn.textContent = 'Zauber ausgelöst — Slot ' + slotNum + ' entleeren';
          ausloesenBtn.onclick = function () {
            var entleerenBtn = document.querySelector('.slot-entleeren-btn[data-slot="' + slotNum + '"]');
            if (entleerenBtn && window.Zauberspeicher) {
              ausloesenBtn.disabled = true;
              window.Zauberspeicher.handleEntleeren(entleerenBtn);
            }
          };
          actionEl.appendChild(ausloesenBtn);
        }
      }

    } else if (cfg.type === 'eigenschaft') {
      var roll = rolls[0];
      var res = window.Dice.calcEigProbe(cfg.wert || 0, roll, mod);
      var inp = document.createElement('input');
      inp.type = 'number'; inp.min = 1; inp.max = 20; inp.value = roll;
      if (!isManual) inp.setAttribute('readonly', 'readonly');
      inp.addEventListener('input', function () {
        if (!isManual) return;
        render([Math.max(1, Math.min(20, parseInt(this.value, 10) || 1))]);
      });
      diceRow.appendChild(inp);
      currentRolls = [roll];
      eigRow.innerHTML = '<span>' + (cfg.abbr || '') + '(' + (cfg.wert || 0) + ')</span>';
      if (res.isPatzer) {
        resultEl.textContent = '⚠️ Patzer! (20)'; resultEl.classList.add('patzer');
      } else if (res.isCrit) {
        resultEl.textContent = '⭐ Kritisch! (1) — immer Erfolg'; resultEl.classList.add('crit');
      } else if (res.success) {
        resultEl.textContent = '✅ Erfolg (' + roll + ' ≤ ' + (cfg.wert || 0) + ')'; resultEl.classList.add('success');
      } else {
        resultEl.textContent = '❌ Misserfolg (' + roll + ' > ' + (cfg.wert || 0) + ')'; resultEl.classList.add('fail');
      }

    } else if (cfg.type === 'at' || cfg.type === 'pa') {
      var roll = rolls[0];
      var lbl = cfg.type === 'at' ? 'AT' : 'PA';
      var res = window.Dice.calcKampfProbe(cfg.atOrPa || 0, roll, mod);
      var inp = document.createElement('input');
      inp.type = 'number'; inp.min = 1; inp.max = 20; inp.value = roll;
      if (!isManual) inp.setAttribute('readonly', 'readonly');
      inp.addEventListener('input', function () {
        if (!isManual) return;
        render([Math.max(1, Math.min(20, parseInt(this.value, 10) || 1))]);
      });
      diceRow.appendChild(inp);
      currentRolls = [roll];
      eigRow.innerHTML = '<span>' + lbl + '-Basis: ' + (cfg.atOrPa || 0) + '</span>';
      if (res.isPatzer) {
        resultEl.textContent = '⚠️ Patzer! (20)'; resultEl.classList.add('patzer');
      } else if (res.isCrit) {
        resultEl.textContent = '⭐ Kritisch! (1)'; resultEl.classList.add('crit');
      } else if (res.success) {
        resultEl.textContent = '✅ ' + (cfg.type === 'at' ? 'Treffer!' : 'Pariert!') + ' (' + roll + ' ≤ ' + (cfg.atOrPa || 0) + ')';
        resultEl.classList.add('success');
        if (cfg.type === 'at' && cfg.tpStr) {
          var schadenBtn = document.createElement('button');
          schadenBtn.className = 'dp-btn';
          schadenBtn.type = 'button';
          schadenBtn.textContent = 'Schaden würfeln (' + cfg.tpStr + ')';
          schadenBtn.onclick = function () {
            window.Dice.openPanel({ type: 'schaden', name: 'Schaden', tpStr: cfg.tpStr, slug: cfg.slug });
          };
          actionEl.appendChild(schadenBtn);
        }
      } else {
        resultEl.textContent = '❌ ' + (cfg.type === 'at' ? 'Verfehlt!' : 'Nicht pariert!') + ' (' + roll + ' > ' + (cfg.atOrPa || 0) + ')';
        resultEl.classList.add('fail');
        if (cfg.type === 'pa') {
          var leBtn = document.createElement('button');
          leBtn.className = 'dp-btn';
          leBtn.type = 'button';
          leBtn.textContent = 'SP kassiert — LeP abziehen…';
          leBtn.onclick = function () {
            var sp = parseInt(prompt('Wie viele SP (nach RS)?', '0'), 10) || 0;
            if (sp <= 0) return;
            var slug = (window.DSA && window.DSA.slug) || '';
            var curLe = (window.DSA && window.DSA.vitals && window.DSA.vitals.LE && window.DSA.vitals.LE.current) || 0;
            var newLe = Math.max(0, curLe - sp);
            patchValue({
              kind: 'table_cell', file: '_illaen.md',
              section_path: ['Eigenschaften & Basiswerte', 'Basiswerte'],
              row_key: { column: 'Basiswert', match: 'Lebensenergie (LE)' },
              column: 'Akt.', value: String(newLe), slug: slug,
            });
            if (window.DSA && window.DSA.vitals && window.DSA.vitals.LE) {
              window.DSA.vitals.LE.current = newLe;
            }
            leBtn.disabled = true;
            leBtn.textContent = '✓ LeP abgezogen (' + curLe + '→' + newLe + ')';
          };
          actionEl.appendChild(leBtn);
        }
      }

    } else if (cfg.type === 'schaden') {
      // Use the rolls parameter — set by autoRoll() on open, by currentRolls on re-render
      var spec = window.Dice.parseDiceString(cfg.tpStr || '0');
      if (spec && spec.sides) {
        currentRolls = rolls.slice();
        var total = rolls.reduce(function (a, b) { return a + b; }, 0) + (spec.bonus || 0);
        rolls.forEach(function (r, idx) {
          var inp = document.createElement('input');
          inp.type = 'number'; inp.min = 1; inp.max = spec.sides; inp.value = r;
          if (!isManual) inp.setAttribute('readonly', 'readonly');
          inp.dataset.idx = idx;
          inp.addEventListener('input', function () {
            if (!isManual) return;
            var newRolls = currentRolls.slice();
            newRolls[parseInt(this.dataset.idx, 10)] = Math.max(1, Math.min(spec.sides, parseInt(this.value, 10) || 1));
            render(newRolls);
          });
          diceRow.appendChild(inp);
        });
        resultEl.textContent = 'Schaden: ' + total + ' TP (' + cfg.tpStr + ')';
        resultEl.classList.add('success');
      } else if (spec) {
        currentRolls = [];
        resultEl.textContent = 'Schaden: ' + spec.bonus + ' TP (fix)';
        resultEl.classList.add('success');
      } else {
        currentRolls = [];
        resultEl.textContent = 'Unbekanntes TP-Format: ' + (cfg.tpStr || '');
        resultEl.classList.add('fail');
      }
    }
  }

  // D-047: das Panel ist position:fixed (Hoehe variiert mit Modus/Ergebnis) -> die offene Hoehe steht als --dice-panel-h auf <html>;
  // base.css reserviert sie bei <= 480 px als body-padding-bottom, damit Footer-Leiste und letzte Zeilen erreichbar bleiben.
  function syncPanelReserve() {
    if (!panel) return;
    var open = !panel.classList.contains('hidden');
    document.documentElement.style.setProperty('--dice-panel-h', open ? panel.offsetHeight + 'px' : '0px');
  }

  // ------------------------------------------------------------------
  // Public API
  // ------------------------------------------------------------------
  window.Dice.openPanel = function (config) {
    currentConfig = config;
    isManual = false;
    if (!panel) return;

    document.getElementById('dp-title').textContent = '🎲 ' + (config.name || 'Probe');
    document.getElementById('dp-mod').value = getWundMod(config) + (currentConfig.baseMod || 0);
    document.getElementById('dp-auto').classList.add('active');
    document.getElementById('dp-manual').classList.remove('active');

    var rolls = autoRoll();
    render(rolls);
    panel.classList.remove('hidden');
    syncPanelReserve();
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  };

  // ------------------------------------------------------------------
  // Event binding — runs once on DOMContentLoaded
  // ------------------------------------------------------------------
  document.addEventListener('DOMContentLoaded', function () {
    panel = document.getElementById('dice-panel');
    if (!panel) return;

    document.getElementById('dp-close').addEventListener('click', function () {
      panel.classList.add('hidden');
      syncPanelReserve();
    });
    if (typeof ResizeObserver === 'function') new ResizeObserver(syncPanelReserve).observe(panel);

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
      if (isManual) return;
      render(autoRoll());
    });

    document.getElementById('dp-mod').addEventListener('change', function () {
      render(currentRolls.length ? currentRolls : autoRoll());
    });

    // Talent rows (3W20 + TaW)
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

    // Spell rows (3W20 + ZfW)
    document.querySelectorAll('.spell[data-probe]').forEach(function (el) {
      el.addEventListener('click', function (e) {
        if (e.target.closest('details') || e.target.closest('a')) return;
        window.Dice.openPanel({
          type: 'zauber',
          name: el.dataset.name,
          probe: el.dataset.probe,
          zfw: parseInt(el.dataset.zfw, 10) || 0,
          kosten: el.dataset.kosten || '',
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // Eigenschaft hexes (1W20)
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
        var tpEl = document.querySelector('[data-tp]');
        window.Dice.openPanel({
          type: 'at',
          name: 'Attacke',
          atOrPa: parseInt(el.dataset.at, 10) || 0,
          tpStr: tpEl ? tpEl.dataset.tp : '',
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

    // Zauberspeicher-Auslöseprobe (3W20 pure attribute probe, no TaW buffer)
    document.querySelectorAll('.slot-ausloesen-btn[data-probe]').forEach(function (el) {
      el.addEventListener('click', function () {
        window.Dice.openPanel({
          type: 'talent',
          name: 'Zauberspeicher auslösen (Slot ' + el.dataset.slot + ')',
          probe: el.dataset.probe,
          taw: 0,
          baseMod: -parseInt(el.dataset.erschwernis, 10) || 0,
          speicherSlot: el.dataset.slot,
          slug: window.DSA && window.DSA.slug,
        });
      });
    });

    // Weapon TP (Schaden)
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
