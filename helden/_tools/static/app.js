/**
 * app.js — Interactive dashboard: debounced PATCH to Flask server.
 * Runs when served via server.py (http://localhost:5500).
 * Degrades gracefully when opened as file:// (no interactive behaviour).
 */

const IS_SERVED = location.protocol === 'http:' || location.protocol === 'https:';
if (!IS_SERVED) {
  console.info('[dsa-dashboard] static mode — interactive features disabled');
} else {
  initDashboard();
}

function initDashboard() {
  const DEBOUNCE_MS = 1600;
  const POLL_INTERVAL_MS = 8000;

  const indicator = document.getElementById('save-indicator');
  let indicatorTimer = null;

  function showIndicator(text, isError) {
    if (!indicator) return;
    indicator.textContent = text;
    indicator.style.background = isError ? 'rgba(180,40,40,0.85)' : 'rgba(0,0,0,0.75)';
    indicator.classList.add('visible');
    clearTimeout(indicatorTimer);
    indicatorTimer = setTimeout(() => indicator.classList.remove('visible'), 2500);
  }

  async function sendPatch(locator) {
    showIndicator('speichern…', false);
    try {
      const resp = await fetch(`/api/held/${locator.slug}/value`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(locator),
      });
      const data = await resp.json();
      if (resp.status === 409) {
        showIndicator('Konflikt — Seite neu laden', true);
        if (confirm('Die Quelldatei wurde extern geändert. Seite neu laden?')) {
          location.reload();
        }
        return false;
      }
      if (!resp.ok || !data.ok) {
        showIndicator('Fehler: ' + (data.error || resp.status), true);
        return false;
      }
      showIndicator('gespeichert ✓', false);
      return true;
    } catch (err) {
      showIndicator('Netzwerkfehler', true);
      return false;
    }
  }

  const debounceTimers = new WeakMap();

  function schedulePatch(el, locator, value) {
    clearTimeout(debounceTimers.get(el));
    debounceTimers.set(el, setTimeout(() => {
      sendPatch({ ...locator, value: String(value) });
    }, DEBOUNCE_MS));
  }

  // Vital steppers
  document.querySelectorAll('.vital-stepper').forEach(stepper => {
    const rawLocator = JSON.parse(stepper.dataset.locator);
    const max = parseInt(stepper.dataset.max, 10);
    const barId = stepper.dataset.barId;
    const input = stepper.querySelector('.vital-input');
    const minusBtn = stepper.querySelector('.vital-btn--minus');
    const plusBtn = stepper.querySelector('.vital-btn--plus');

    if (!input) return;

    function clamp(v) { return Math.max(0, Math.min(max, v)); }

    function setValue(v, shouldPatch) {
      const clamped = clamp(v);
      input.value = clamped;
      const bar = barId ? document.getElementById(barId) : null;
      if (bar) bar.style.width = Math.round(clamped / max * 100) + '%';
      if (shouldPatch) schedulePatch(stepper, rawLocator, clamped);
    }

    minusBtn?.addEventListener('click', () => setValue(parseInt(input.value, 10) - 1, true));
    plusBtn?.addEventListener('click', () => setValue(parseInt(input.value, 10) + 1, true));
    input.addEventListener('change', () => setValue(parseInt(input.value, 10) || 0, true));
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') setValue(parseInt(input.value, 10) || 0, true);
    });
  });

  // Flush pending patches on page unload
  window.addEventListener('beforeunload', () => {
    document.querySelectorAll('.vital-stepper').forEach(el => {
      const timer = debounceTimers.get(el);
      if (timer) {
        clearTimeout(timer);
        const locator = JSON.parse(el.dataset.locator);
        const val = el.querySelector('.vital-input')?.value;
        if (val != null) {
          navigator.sendBeacon(
            `/api/held/${locator.slug}/value`,
            JSON.stringify({ ...locator, value: val })
          );
        }
      }
    });
  });

  // Poll for external file changes (e.g. Obsidian editing while dashboard is open)
  let lastMtimes = {};
  async function pollMtimes() {
    const stpr = document.querySelector('.vital-stepper');
    if (!stpr) return;
    const slug = JSON.parse(stpr.dataset.locator).slug || 'illaen-baernhold';
    try {
      const resp = await fetch(`/api/held/${slug}/mtime`);
      const mtimes = await resp.json();
      if (Object.keys(lastMtimes).length === 0) {
        lastMtimes = mtimes;
        return;
      }
      const changed = Object.entries(mtimes).some(([k, v]) => lastMtimes[k] && v > lastMtimes[k]);
      if (changed) {
        lastMtimes = mtimes;
        showIndicator('Quelldatei geändert — neu laden empfohlen', false);
      }
    } catch (_) {}
  }
  setInterval(pollMtimes, POLL_INTERVAL_MS);
}
