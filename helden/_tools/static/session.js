/**
 * session.js — Tier-B transient state (Zustände, temp mods) in localStorage.
 * Key: dsa:<slug>:session  →  { zustaende: [...] }
 *
 * Wunden count persists to markdown via PATCH (Tier A).
 * This file manages the Wunden UI widget and the transient Zustände chips.
 */

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

  // DSA 4.1 Wundregeln: simplified penalty overlay.
  // Wundschwelle = ceil(KO/2). Each wound = -2 cumulative on all checks.
  // TODO: verify exact rules in wiki/dsa-4.1/ (zones, thresholds) before shipping.
  function computeWundPenalty(wunden) {
    if (wunden <= 0) return 0;
    return wunden * 2;
  }

  // ── Wunden widget ──────────────────────────────────────────────────
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
        (currentWunden > 0 ? '(−' + computeWundPenalty(currentWunden) + ' auf Proben)' : '') +
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
    penaltyEl.textContent = next > 0 ? '(−' + computeWundPenalty(next) + ' auf Proben)' : '';
    anchor.dataset.wunden = next;

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
  const ZUSTAENDE = [
    { key: 'schmerz',    label: 'Schmerz',   mod: -2 },
    { key: 'furcht',     label: 'Furcht',     mod: -2 },
    { key: 'betaeubt',   label: 'Betäubt',    mod: -4 },
    { key: 'verwirrt',   label: 'Verwirrt',   mod: -2 },
    { key: 'erschoepft', label: 'Erschöpft',  mod: -2 },
  ];

  function renderZustandChips() {
    const container = document.getElementById('zustand-chips');
    if (!container) return;
    const active = new Set((loadState().zustaende) || []);
    container.innerHTML = ZUSTAENDE.map(z =>
      '<button class="zustand-chip' + (active.has(z.key) ? ' active' : '') + '" ' +
      'data-key="' + z.key + '" type="button" ' +
      'title="' + z.label + ': ' + z.mod + ' auf Proben">' +
      z.label + '</button>'
    ).join('');
    container.querySelectorAll('.zustand-chip').forEach(btn => {
      btn.addEventListener('click', () => toggleZustand(btn.dataset.key));
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
