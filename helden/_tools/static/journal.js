(function () {
  'use strict';

  var IS_SERVED = window.location.protocol !== 'file:';

  // Guard: only run when served and kampagne data is present
  if (!IS_SERVED || !window.DSA || !window.DSA.kampagne) return;

  // ---------- PATCH helper for kampagne section bodies ----------

  function patchKampagne(camp, locator) {
    return fetch('/api/kampagne/' + camp + '/value', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locator)
    }).then(function (r) {
      if (r.status === 409) return Promise.reject(new Error('Konflikt — Datei wurde extern geändert'));
      if (!r.ok) return r.json().then(function (d) {
        return Promise.reject(new Error(d.error || 'PATCH fehlgeschlagen'));
      });
      return r.json();
    });
  }

  // ---------- Save handler ----------

  function handleSave(btn) {
    var datei = btn.dataset.datei;
    var card = btn.closest('.journal-session');
    if (!card) return;

    var textarea = card.querySelector('.journal-verlauf[data-datei="' + datei + '"]');
    var errorSpan = card.querySelector('.journal-save-error');
    var okSpan = card.querySelector('.journal-save-ok');

    if (!textarea) return;

    // Clear previous feedback
    if (errorSpan) { errorSpan.textContent = ''; errorSpan.style.display = 'none'; }
    if (okSpan) okSpan.style.display = 'none';

    btn.disabled = true;
    btn.textContent = '…';

    patchKampagne(window.DSA.kampagne_slug, {
      kind: 'section_body',
      file: datei,
      section: 'Verlauf',
      value: textarea.value
    }).then(function () {
      btn.disabled = false;
      btn.textContent = 'Speichern';
      if (okSpan) {
        okSpan.style.display = 'inline';
        setTimeout(function () { okSpan.style.display = 'none'; }, 3000);
      }
    }).catch(function (err) {
      btn.disabled = false;
      btn.textContent = 'Speichern';
      if (errorSpan) {
        errorSpan.textContent = '⚠ ' + (err.message || 'PATCH fehlgeschlagen');
        errorSpan.style.display = 'inline';
      }
    });
  }

  // ---------- Wire listeners ----------

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.journal-save-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { handleSave(btn); });
    });
  });
}());
