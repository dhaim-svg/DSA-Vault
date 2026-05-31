(function () {
  'use strict';

  var IS_SERVED = window.location.protocol !== 'file:';
  if (!IS_SERVED) return;

  var showIndicator = window.dsaShowIndicator;

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('commit-btn');
    if (!btn) return;

    btn.addEventListener('click', function () {
      btn.disabled = true;
      btn.textContent = '…';

      var msgInput = document.getElementById('commit-msg');
      var msgValue = msgInput ? msgInput.value.trim() : '';

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
