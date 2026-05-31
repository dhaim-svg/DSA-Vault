(function () {
  'use strict';

  // ---------- PATCH helper (same pattern as inventar.js) ----------

  function patchLocator(locator) {
    if (window.location.protocol === 'file:') return Promise.resolve({ ok: true });
    return fetch('/api/held/' + window.DSA.slug + '/value', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locator)
    }).then(function(r) {
      if (r.status === 409) return Promise.reject(new Error('Konflikt — Datei wurde extern geändert'));
      if (!r.ok) return r.json().then(function(d) {
        return Promise.reject(new Error(d.error || 'PATCH fehlgeschlagen'));
      });
      return r.json();
    });
  }

  // ---------- Error display helper ----------

  function showSlotError(slotEl, msg) {
    var existing = slotEl.querySelector('.sg-error');
    if (existing) existing.remove();
    var span = document.createElement('span');
    span.className = 'sg-error';
    span.textContent = '⚠ ' + msg;
    slotEl.appendChild(span);
  }

  // ---------- The common PATCH locator shape for Zauberspeicher ----------
  // section_path MUST be ['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt']
  // row_key: {column: 'Slot', match: <slot number as string>}
  // FRAGILITY: '(9 Rituale)' in the H2 heading is a literal that the writer matches
  // exactly. If a ritual is ever added/removed, the heading count changes and every
  // PATCH will silently fail with "cell not found". The render (parser uses substring
  // match) would still work, masking the break. Update both here and rituale.md if needed.

  var SECTION_PATH = ['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'];

  // ---------- Entleeren ----------

  function handleEntleeren(btn) {
    var slot = btn.dataset.slot;
    var slotEl = btn.closest('.speicher-slot');
    if (slotEl) { var old = slotEl.querySelector('.sg-error'); if (old) old.remove(); }
    btn.disabled = true;
    btn.textContent = '…';

    patchLocator({
      kind: 'table_row',
      file: 'rituale.md',
      section_path: SECTION_PATH,
      row_key: { column: 'Slot', match: slot },
      cells: {
        'AsP': '—',
        'Gespeicherter Zauber': '— frei —',
        'Erschwernis-Mods': '—',
        'Letzte Erneuerung': '—'
      }
    }).then(function() {
      window.location.reload();
    }).catch(function(err) {
      btn.disabled = false;
      btn.textContent = 'Entleeren';
      if (slotEl) showSlotError(slotEl, err.message || 'PATCH fehlgeschlagen');
    });
  }

  // ---------- Befüllen toggle ----------

  function handleBefuellenToggle(btn) {
    var slot = btn.dataset.slot;
    var area = btn.closest('.slot-befuellen-area');
    if (!area) return;
    var form = area.querySelector('.slot-befuellen-form[data-slot="' + slot + '"]');
    if (!form) return;
    var isHidden = form.classList.contains('hidden');
    form.classList.toggle('hidden', !isHidden);
    btn.textContent = isHidden ? '× Abbrechen' : '+ Befüllen';
  }

  // ---------- Befüllen cancel ----------

  function handleBefuellenCancel(btn) {
    var slot = btn.dataset.slot;
    var area = btn.closest('.slot-befuellen-area');
    if (!area) return;
    var form = area.querySelector('.slot-befuellen-form[data-slot="' + slot + '"]');
    var toggleBtn = area.querySelector('.slot-befuellen-toggle[data-slot="' + slot + '"]');
    if (form) form.classList.add('hidden');
    if (toggleBtn) toggleBtn.textContent = '+ Befüllen';
  }

  // ---------- Befüllen submit ----------

  function handleBefuellenSubmit(btn) {
    var slot = btn.dataset.slot;
    var area = btn.closest('.slot-befuellen-area');
    if (!area) return;

    var zauberInput = area.querySelector('.slot-form-zauber[data-slot="' + slot + '"]');
    var aspInput    = area.querySelector('.slot-form-asp[data-slot="'    + slot + '"]');
    var modsInput   = area.querySelector('.slot-form-mods[data-slot="'   + slot + '"]');
    var ernInput    = area.querySelector('.slot-form-erneuerung[data-slot="' + slot + '"]');

    var zauber = zauberInput ? zauberInput.value.trim() : '';
    var asp    = aspInput    ? aspInput.value.trim()    : '';
    var mods   = modsInput   ? modsInput.value.trim()   : '—';
    var ern    = ernInput     ? ernInput.value.trim()    : '—';

    var slotEl = btn.closest('.speicher-slot');
    if (slotEl) { var old = slotEl.querySelector('.sg-error'); if (old) old.remove(); }

    btn.disabled = true;
    btn.textContent = '…';

    // Validation
    if (!zauber) {
      btn.disabled = false;
      btn.textContent = 'Speichern';
      if (slotEl) showSlotError(slotEl, 'Zauber-Name darf nicht leer sein.');
      return;
    }
    if (!asp || isNaN(Number(asp)) || Number(asp) < 0) {
      btn.disabled = false;
      btn.textContent = 'Speichern';
      if (slotEl) showSlotError(slotEl, 'AsP muss eine nicht-negative Zahl sein.');
      return;
    }

    // Defaults for optional fields
    if (!mods) mods = '—';
    if (!ern)  ern  = '—';

    patchLocator({
      kind: 'table_row',
      file: 'rituale.md',
      section_path: SECTION_PATH,
      row_key: { column: 'Slot', match: slot },
      cells: {
        'AsP': asp,
        'Gespeicherter Zauber': zauber,
        'Erschwernis-Mods': mods,
        'Letzte Erneuerung': ern
      }
    }).then(function() {
      window.location.reload();
    }).catch(function(err) {
      btn.disabled = false;
      btn.textContent = 'Speichern';
      if (slotEl) showSlotError(slotEl, err.message || 'PATCH fehlgeschlagen');
    });
  }

  // ---------- Wire listeners ----------

  document.addEventListener('DOMContentLoaded', function() {
    // Guard: no zauberspeicher data (hero without Stab)
    if (!window.DSA || !(window.DSA.zauberspeicher || []).length) return;

    document.querySelectorAll('.slot-entleeren-btn').forEach(function(btn) {
      btn.addEventListener('click', function() { handleEntleeren(btn); });
    });

    document.querySelectorAll('.slot-befuellen-toggle').forEach(function(btn) {
      btn.addEventListener('click', function() { handleBefuellenToggle(btn); });
    });

    document.querySelectorAll('.slot-befuellen-cancel').forEach(function(btn) {
      btn.addEventListener('click', function() { handleBefuellenCancel(btn); });
    });

    document.querySelectorAll('.slot-befuellen-submit').forEach(function(btn) {
      btn.addEventListener('click', function() { handleBefuellenSubmit(btn); });
    });
  });
}());
