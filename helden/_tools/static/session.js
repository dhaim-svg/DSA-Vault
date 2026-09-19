/**
 * session.js — Tier-B transient state (Zustände, temp mods) in localStorage.
 * Key: dsa:<slug>:session  →  { zustaende: [...] }
 *
 * Wunden count persists to markdown via PATCH (Tier A).
 * This file manages the Wunden UI widget and the transient Zustände chips.
 */

(function () {
  const IS_SERVED = location.protocol === 'http:' || location.protocol === 'https:';
  if (IS_SERVED) initSession();

  function initSession() {
    const stpr = document.querySelector('.vital-stepper');
    const slug = stpr ? JSON.parse(stpr.dataset.locator).slug : 'illaen-baernhold';
    const STORAGE_KEY = `dsa:${slug}:session`;

    function loadState() {
      try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
      catch { return {}; }
    }

    function saveState(state) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }

    // Wunden: WdS S. 57 → wundregeln.js (DSAWundregeln) ist die einzige Quelle —
    // pro Wunde AT/PA/FK/INI/GE -2, GS -1, sonst nichts.
    // Zustände: Hausregel (kein fester Probenmalus im Regelwerk, s. wiki/dsa-4.1/grundregeln/zustaende.md).
    const Wund = window.DSAWundregeln;

    // ── Wunden widget ──────────────────────────────────────────────────
    function wundGeltungLabel(wunden) {
      return wunden > 0 ? '(' + Wund.geltungText(wunden) + ')' : '';
    }

    function renderWundenWidget() {
      if (document.getElementById('wunden-widget')) return;
      const anchor = document.querySelector('[data-wunden]');
      if (!anchor) return;

      const currentWunden = parseInt(anchor.dataset.wunden, 10) || 0;
      const widget = document.createElement('div');
      widget.id = 'wunden-widget';
      widget.className = 'wunden-counter';
      widget.innerHTML =
        '<span>Wunden:</span>' +
        '<button id="wunden-minus" type="button" aria-label="Wunde heilen">−</button>' +
        '<span id="wunden-count" style="font-weight:700;font-size:1.2rem">' + currentWunden + '</span>' +
        '<button id="wunden-plus" type="button" aria-label="Wunde erleiden">+</button>' +
        '<span id="wunden-penalty" style="opacity:0.7;font-size:0.9rem">' +
          wundGeltungLabel(currentWunden) +
        '</span>';
      anchor.insertAdjacentElement('afterend', widget);

      document.getElementById('wunden-minus').addEventListener('click', () => changeWunden(-1));
      document.getElementById('wunden-plus').addEventListener('click', () => changeWunden(+1));
    }

    function changeWunden(delta) {
      const anchor = document.querySelector('[data-wunden]');
      const countEl = document.getElementById('wunden-count');
      const penaltyEl = document.getElementById('wunden-penalty');
      if (!anchor || !countEl) return;

      const next = Math.max(0, (parseInt(countEl.textContent, 10) || 0) + delta);
      countEl.textContent = next;
      penaltyEl.textContent = wundGeltungLabel(next);
      anchor.dataset.wunden = next;
      updateEigLeisteBadge();

      const stpr2 = document.querySelector('.vital-stepper');
      if (!stpr2) return;
      const baseLocator = JSON.parse(stpr2.dataset.locator);
      fetch('/api/held/' + baseLocator.slug + '/value', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kind: 'frontmatter', file: '_illaen.md', key: 'wunden', value: String(next), slug: baseLocator.slug }),
      }).catch(console.error);
    }

    // ── Zustände chips (transient localStorage only) ───────────────────
    // hausregel/regel: Kennzeichnung im Tooltip + Badge (Wert und Wirkung unverändert).
    const ZUSTAENDE = [
      { key: 'schmerz',    label: 'Schmerz',   mod: -2, hausregel: true,
        regel: 'Regelwerk: nur optionale SB-Probe nach Wunde (WdS S. 82)' },
      { key: 'furcht',     label: 'Furcht',     mod: -2, hausregel: true,
        regel: 'Regelwerk: nur Ängste als Schlechte Eigenschaft (WdH S. 268)' },
      { key: 'betaeubt',   label: 'Betäubt',    mod: -4, hausregel: true,
        regel: 'Regelwerk: nur Betäubungsschlag/Bewusstlosigkeit (WdS S. 61, 86)' },
      { key: 'verwirrt',   label: 'Verwirrt',   mod: -2, hausregel: true,
        regel: 'Regelwerk: kein Zustand (nicht belegt)' },
      { key: 'erschoepft', label: 'Erschöpft',  mod: -2, hausregel: true,
        regel: 'Regelwerk: Überanstrengung wirkt über BE/KO/Wundschwelle (WdS S. 139)' },
    ];

    function renderZustandChips() {
      const container = document.getElementById('zustand-chips');
      if (!container) return;
      const active = new Set((loadState().zustaende) || []);
      container.innerHTML = ZUSTAENDE.map(z =>
        '<button class="zustand-chip' + (z.hausregel ? ' hausregel' : '') +
        (active.has(z.key) ? ' active' : '') + '" ' +
        'data-key="' + z.key + '" type="button" ' +
        'title="' + z.label + ': −' + Math.abs(z.mod) + ' auf Proben (Hausregel) — ' + z.regel + '">' +
        z.label + '</button>'
      ).join('');
      container.querySelectorAll('.zustand-chip').forEach(btn => {
        btn.addEventListener('click', () => toggleZustand(btn.dataset.key));
      });
      updateEigLeisteBadge();
    }

    // ── Eigenschafts-Leiste mod badge (Talente/Zauber tabs, D-025/D-026) ──
    // Note: the bar macro is rendered once per tab (Talente + Zauber), so the
    // hook is a class (not an id) — both instances are updated in lockstep.

    // Active mali (Wunden + Zustand-Chips), the single source of truth for the badge text,
    // the probe overlay (applyWundModsToProben), the base-value overlay
    // (applyWundModsToStats) and dice.js's panel modifier (probeMod).
    //
    // Effect shape — the "Geltungsbereich" is one of two fields:
    //   { label, mods: { ZIEL: <=0, ... }, wunden }  Wunden: nur die genannten Ziele
    //        (AT/PA/FK/INI/GE/GS, aus DSAWundregeln.wundMod). Wirkt auf Proben (AT, PA, GE)
    //        UND Basiswert-Anzeigen (AT/PA/FK/INI/GS).
    //   { label, alle: true, mod: <=0, hausregel: true }  Zustand (Hausregel): wirkt auf jede Probe,
    //        nie auf Basiswert-Anzeigen und nie auf Schadenswürfe.
    function computeActiveEffects() {
      const effects = [];
      const wundenAnchor = document.querySelector('[data-wunden]');
      const wunden = wundenAnchor ? parseInt(wundenAnchor.dataset.wunden, 10) || 0 : 0;
      if (wunden > 0) {
        const mods = {};
        Object.keys(Wund.JE_WUNDE).forEach(ziel => { mods[ziel] = Wund.wundMod(wunden, ziel); });
        effects.push({ label: 'Wunden', wunden: wunden, mods: mods });
      }

      const active = new Set((loadState().zustaende) || []);
      ZUSTAENDE.forEach(z => {
        if (active.has(z.key)) effects.push({ label: z.label, alle: true, mod: z.mod, hausregel: true });
      });
      return effects;
    }

    // Ziele einer Probe (Würfelpanel / Eigenschaftswert-Overlay) bzw. einer Basiswert-Anzeige.
    const PROBE_ZIELE = new Set(['AT', 'PA', 'MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK', 'talent', 'zauber']);
    const STAT_ZIELE = new Set(['AT', 'PA', 'FK', 'INI', 'GS']);

    // Summe <= 0 für eine PROBE auf `ziel`: Wunden nur, wo DSAWundregeln das Ziel kennt
    // (AT, PA, GE), Zustände (alle) für jedes Probenziel. Unbekanntes Ziel → 0.
    function probeMod(ziel, effects) {
      if (!PROBE_ZIELE.has(ziel)) return 0;
      return (effects || computeActiveEffects()).reduce((sum, e) => {
        if (e.alle) return sum + e.mod;
        return sum + (e.mods && e.mods[ziel] ? e.mods[ziel] : 0);
      }, 0);
    }

    // Summe <= 0 für eine BASISWERT-ANZEIGE (AT/PA/FK/INI/GS): nur Wunden, nie Zustände.
    function statMod(stat, effects) {
      if (!STAT_ZIELE.has(stat)) return 0;
      return (effects || computeActiveEffects()).reduce((sum, e) => {
        return sum + (!e.alle && e.mods && e.mods[stat] ? e.mods[stat] : 0);
      }, 0);
    }

    // Summe <= 0 für den WERT einer Eigenschaft (MU KL IN CH FF GE KO KK): nur Wunden (bei GE),
    // nie Zustände — die wirken über den Panel-Modifikator und würden hier doppelt zählen.
    // dice.js parseProbe: die Wunde senkt die GE selbst, also gilt der niedrigere Wert in jeder Probe.
    const ATTR_ZIELE = new Set(['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK']);
    function attrMod(abbr, effects) {
      if (!ATTR_ZIELE.has(abbr)) return 0;
      return (effects || computeActiveEffects()).reduce((sum, e) => {
        return sum + (!e.alle && e.mods && e.mods[abbr] ? e.mods[abbr] : 0);
      }, 0);
    }

    // Exposed so dice.js's getWundMod(cfg) can pre-fill the roll panel's modifier with the
    // same scoped values shown by the badge/overlays — wundregeln.js and session.js load
    // before dice.js (JS_FILES order).
    window.DSASession = {
      computeActiveEffects: computeActiveEffects, probeMod: probeMod, statMod: statMod, attrMod: attrMod,
    };

    function updateEigLeisteBadge() {
      const effects = computeActiveEffects();

      // Wunden wirken auf Talente/Zauber nur über die GE; Zustände auf alles.
      // e.g. "Wunden ×2: GE −4 · Schmerz −2 (Hausregel)"; leer ohne aktive Effekte.
      const text = effects.map(e => e.alle
        ? e.label + ' −' + Math.abs(e.mod) + (e.hausregel ? ' (Hausregel)' : '')
        : e.label + ' ×' + e.wunden + ': GE −' + Math.abs(e.mods.GE)
      ).join(' · ');
      document.querySelectorAll('.eig-leiste-mods').forEach(badge => { badge.textContent = text; });

      applyWundModsToProben(effects);
      applyWundModsToStats(effects);
    }

    // Annotates every rendered attribute value in probe_eig's output
    // (data-attr spans, Talent-/Zauber-/Spontane-Mod-Proben) with the
    // effective value when a malus applies to that attribute, e.g. "GE 13→11".
    // Wunden treffen nur die GE; reverts to the base value once the malus clears.
    function applyWundModsToProben(effects) {
      document.querySelectorAll('[data-attr]').forEach(el => {
        const abbr = el.dataset.attr;
        const base = parseInt(el.dataset.base, 10);
        if (isNaN(base)) return;
        const mod = probeMod(abbr, effects);
        el.textContent = mod !== 0 ? (abbr + ' ' + base + '→' + (base + mod)) : (abbr + ' ' + base);
      });
    }

    // Basiswert-Anzeigen im Kampf-Tab (data-wund-stat + data-wund-base): "14→10" bei
    // Wundabzug (statMod), sonst nur der Basiswert. Nicht numerische Basis ("—") bleibt unberührt.
    function applyWundModsToStats(effects) {
      document.querySelectorAll('[data-wund-stat]').forEach(el => {
        if (!/^-?\d+$/.test((el.dataset.wundBase || '').trim())) return;
        const base = parseInt(el.dataset.wundBase, 10);
        const mod = statMod(el.dataset.wundStat, effects);
        el.textContent = mod !== 0 ? (base + '→' + (base + mod)) : String(base);
      });
    }

    function toggleZustand(key) {
      const state = loadState();
      const active = new Set(state.zustaende || []);
      if (active.has(key)) active.delete(key); else active.add(key);
      state.zustaende = [...active];
      saveState(state);
      renderZustandChips();
    }

    // ── Session reset ──────────────────────────────────────────────────
    function resetSession() {
      if (!confirm('Transiente Zustände zurücksetzen?')) return;
      localStorage.removeItem(STORAGE_KEY);
      renderZustandChips();
    }

    // ── Init ───────────────────────────────────────────────────────────
    function init() {
      renderWundenWidget();
      renderZustandChips();
      const resetBtn = document.getElementById('session-reset-btn');
      if (resetBtn) resetBtn.addEventListener('click', resetSession);
    }

    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', init);
    } else {
      init();
    }
  }
})();
