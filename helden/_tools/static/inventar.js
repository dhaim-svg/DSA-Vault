/* inventar.js — Inventar-Tab write-back controller
   Handles three PATCH operations:
     1. Coin steppers   → frontmatter key 'geld' on _illaen.md
     2. Item qty        → table_cell on ausruestung.md ## Inventar
     3. Add item        → table_append_row on ausruestung.md ## Inventar
*/
(function () {
  'use strict';

  /* DSA 4.1 coin conversion table (in Kreuzer) */
  var COIN_KR = { dukaten: 1000, silbertaler: 100, heller: 10, kreuzer: 1 };

  /* makeChange(geld, coin, delta) → new geld object
     Throws a string error message on invalid input. */
  function makeChange(geld, coin, delta) {
    var coinKr = COIN_KR[coin];
    if (!coinKr) throw 'Unbekannte Münze: ' + coin;

    var totalKr = geld.dukaten * 1000
                + geld.silbertaler * 100
                + geld.heller * 10
                + geld.kreuzer;

    totalKr += delta * coinKr;

    if (totalKr < 0) throw 'Nicht genug Münzen';

    var d = Math.floor(totalKr / 1000);
    totalKr -= d * 1000;
    var s = Math.floor(totalKr / 100);
    totalKr -= s * 100;
    var h = Math.floor(totalKr / 10);
    var k = totalKr - h * 10;

    return { dukaten: d, silbertaler: s, heller: h, kreuzer: k };
  }

  /* ── PATCH helper ─────────────────────────────────────────────────────── */
  /* Identical copy from steigern.js — handles file: protocol gracefully. */
  function patchLocator(locator) {
    if (window.location.protocol === 'file:') return Promise.resolve({ ok: true });
    return fetch('/api/held/' + window.DSA.slug + '/value', {
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

  /* ── Error display helper ─────────────────────────────────────────────── */
  function showError(container, message) {
    var prev = container.querySelector('.sg-error');
    if (prev) prev.remove();
    var errEl = document.createElement('span');
    errEl.className = 'sg-error';
    errEl.textContent = '⚠ ' + message;
    container.appendChild(errEl);
  }

  function clearError(container) {
    var prev = container.querySelector('.sg-error');
    if (prev) prev.remove();
  }

  /* ── Coin stepper handler ─────────────────────────────────────────────── */
  function coinButtonHandler(btn) {
    var coin  = btn.dataset.coin;
    var delta = parseInt(btn.dataset.delta, 10);
    if (!coin || isNaN(delta)) return;

    /* Compute new coin balance — reject early without network call */
    var newGeld;
    try {
      newGeld = makeChange(window.DSA.inventar.geld, coin, delta);
    } catch (e) {
      var row = btn.closest('.inv-coin-grid') || btn.parentNode;
      showError(row, e);
      return;
    }

    /* Disable all coin buttons while the PATCH is in flight */
    var allCoinBtns = document.querySelectorAll('.inv-stepper-btn[data-coin]');
    allCoinBtns.forEach(function (b) { b.disabled = true; });

    var yamlValue = '{dukaten: ' + newGeld.dukaten
                  + ', silbertaler: ' + newGeld.silbertaler
                  + ', heller: ' + newGeld.heller
                  + ', kreuzer: ' + newGeld.kreuzer + '}';

    patchLocator({
      kind:  'frontmatter',
      file:  '_illaen.md',
      key:   'geld',
      value: yamlValue
    }).then(function () {
      window.location.reload();
    }).catch(function (err) {
      allCoinBtns.forEach(function (b) { b.disabled = false; });
      var row = btn.closest('.inv-coin-grid') || btn.parentNode;
      showError(row, err.message || 'PATCH fehlgeschlagen');
    });
  }

  /* ── Item quantity stepper handler ───────────────────────────────────── */
  function itemButtonHandler(btn) {
    var itemName = btn.dataset.item;
    var delta    = parseInt(btn.dataset.delta, 10);
    if (!itemName || isNaN(delta)) return;

    /* Find current anzahl from window.DSA */
    var items = window.DSA.inventar.items;
    var item  = null;
    for (var i = 0; i < items.length; i++) {
      if (items[i].name === itemName) { item = items[i]; break; }
    }

    var row = btn.closest('li') || btn.parentNode;

    if (!item) {
      showError(row, 'Gegenstand nicht gefunden: ' + itemName);
      return;
    }

    var currentQty = parseInt(item.anzahl, 10);
    if (isNaN(currentQty)) {
      showError(row, 'Ungültige Menge: ' + item.anzahl);
      return;
    }

    var newQty = currentQty + delta;
    if (newQty < 0) {
      showError(row, 'Anzahl kann nicht negativ sein');
      return;
    }

    clearError(row);
    btn.disabled = true;
    var origText = btn.textContent;
    btn.textContent = '…';

    patchLocator({
      kind:         'table_cell',
      file:         'ausruestung.md',
      section_path: ['Inventar'],
      row_key:      { column: 'Gegenstand', match: itemName },
      column:       'Anzahl',
      value:        String(newQty)
    }).then(function () {
      window.location.reload();
    }).catch(function (err) {
      btn.disabled = false;
      btn.textContent = origText;
      showError(row, err.message || 'PATCH fehlgeschlagen');
    });
  }

  /* ── Add item handler ────────────────────────────────────────────────── */
  function addItemHandler() {
    var nameInput   = document.getElementById('inv-add-name');
    var anzahlInput = document.getElementById('inv-add-anzahl');
    var addBtn      = document.getElementById('inv-add-submit');
    var form        = addBtn ? addBtn.closest('.inv-add-form') || addBtn.parentNode : document.body;

    if (!nameInput || !anzahlInput || !addBtn) return;

    var itemName = nameInput.value.trim();
    var anzahlRaw = anzahlInput.value.trim();

    if (!itemName) {
      showError(form, 'Bitte einen Gegenstandsnamen eingeben');
      return;
    }

    var anzahl = parseInt(anzahlRaw, 10);
    if (!anzahlRaw || isNaN(anzahl) || anzahl < 0) {
      showError(form, 'Bitte eine gültige Anzahl eingeben (≥ 0)');
      return;
    }

    clearError(form);
    addBtn.disabled = true;
    var origText = addBtn.textContent;
    addBtn.textContent = '…';

    patchLocator({
      kind:         'table_append_row',
      file:         'ausruestung.md',
      section_path: ['Inventar'],
      cells:        [itemName, String(anzahl), '0']
    }).then(function () {
      window.location.reload();
    }).catch(function (err) {
      addBtn.disabled = false;
      addBtn.textContent = origText;
      showError(form, err.message || 'PATCH fehlgeschlagen');
    });
  }

  /* ── DOMContentLoaded: wire up all event listeners ───────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    /* Coin steppers */
    document.querySelectorAll('.inv-stepper-btn[data-coin]').forEach(function (btn) {
      btn.addEventListener('click', function () { coinButtonHandler(btn); });
    });

    /* Item qty steppers */
    document.querySelectorAll('.inv-stepper-btn[data-item]').forEach(function (btn) {
      btn.addEventListener('click', function () { itemButtonHandler(btn); });
    });

    /* Add item */
    var addBtn = document.getElementById('inv-add-submit');
    if (addBtn) addBtn.addEventListener('click', addItemHandler);
  });
}());
