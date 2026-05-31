(function () {
  'use strict';

  var IS_SERVED = window.location.protocol !== 'file:';
  if (!IS_SERVED) return;

  var INDICATOR_TIMEOUT_MS = 2500;

  function showIndicator(text, isError) {
    var indicator = document.getElementById('save-indicator');
    if (!indicator) return;
    indicator.textContent = text;
    indicator.style.background = isError
      ? 'rgba(180,40,40,0.85)'
      : 'rgba(0,0,0,0.75)';
    indicator.classList.add('visible');
    setTimeout(function () {
      indicator.classList.remove('visible');
    }, INDICATOR_TIMEOUT_MS);
  }

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('commit-btn');
    if (!btn) return;

    btn.addEventListener('click', function () {
      btn.disabled = true;
      btn.textContent = '…';

      var msgInput = document.getElementById('commit-msg');
      var msgValue = msgInput ? msgInput.value : '';

      fetch('/api/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msgValue }),
      })
        .then(function (resp) {
          return resp.json().then(function (data) {
            return { ok: resp.ok, data: data };
          });
        })
        .then(function (result) {
          var data = result.data;
          if (!result.ok || !data.ok) {
            showIndicator('Git-Fehler: ' + (data.error || 'unbekannt'), true);
          } else if (data.committed === false) {
            showIndicator('nichts zu sichern', false);
          } else {
            showIndicator('committed ✓', false);
            if (msgInput) msgInput.value = '';
          }
        })
        .catch(function (err) {
          showIndicator('Netzwerkfehler: ' + (err.message || 'unbekannt'), true);
        })
        .finally(function () {
          btn.disabled = false;
          btn.textContent = '💾 Sichern';
        });
    });
  });
}());
