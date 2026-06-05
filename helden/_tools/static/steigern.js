/* steigern.js — AP cost calculation and Steigern-Tab controller */
(function () {
  'use strict';

  /* DSA 4.1 SKT cost table
     SKT_COSTS[skt][bracket] — bracket 0 = target TaW 1-5, 1 = 6-10, 2 = 11-15, 3 = 16-20 */
  var SKT_COSTS = {
    A: [1, 2, 3, 4],
    B: [2, 4, 6, 8],
    C: [3, 6, 9, 12],
    D: [4, 8, 12, 16],
    E: [5, 10, 15, 20],
    F: [6, 12, 18, 24],
    G: [7, 14, 21, 28],
    H: [8, 16, 24, 32]
  };

  /* Shift a SKT column left (negative) or right (positive), clamped to [A, H]. */
  var SKT_ORDER = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'];
  function shiftSktColumn(skt, shift) {
    var idx = SKT_ORDER.indexOf(skt);
    if (idx === -1) return skt;
    var newIdx = idx + shift;
    if (newIdx < 0) newIdx = 0;
    if (newIdx > SKT_ORDER.length - 1) newIdx = SKT_ORDER.length - 1;
    return SKT_ORDER[newIdx];
  }

  /* Cost to raise currentTaw → currentTaw+1.
     Bracket is determined by the TARGET value (currentTaw + 1).
     Optional shift: applied via shiftSktColumn before bracket lookup. */
  function calcApCost(skt, currentTaw, shift) {
    var effectiveSkt = shift ? shiftSktColumn(skt, shift) : skt;
    var costs = SKT_COSTS[effectiveSkt];
    if (!costs) return null;
    var targetTaw = currentTaw + 1;
    var bracket = targetTaw <= 5 ? 0 : targetTaw <= 10 ? 1 : targetTaw <= 15 ? 2 : 3;
    return costs[bracket];
  }

  /* Cost to raise eigenschaft → eigenschaft+1 = (currentVal + 1) * 15 */
  function calcEigCost(currentVal) {
    return (currentVal + 1) * 15;
  }

  /* Render a Kosten-Zelle einheitlich (Initial-Render + Erfahrungs-Wechsel). */
  function setCostCell(cell, cost, canAfford) {
    cell.textContent = cost !== null ? cost + ' AP' : '—';
    cell.className = 'sg-cost ' + (canAfford ? 'affordable' : 'expensive');
  }

  /* ── PATCH helper ─────────────────────────────────────────────────────── */
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

  /* ── Steigern: 4 sequential PATCHes ──────────────────────────────────── */
  /* Known limitation: no rollback on partial failure. If PATCH 1 (stat) succeeds
     but a later PATCH fails, the stat on disk is already raised. Recovery: git revert. */
  function doSteigern(item, onSuccess, onError) {
    var slug = window.DSA.slug;
    var ap = window.DSA.steigern.ap;
    var newVal = item.currentVal + 1;
    var newAvail = ap.verfuegbar - item.cost;
    var newEinges = ap.eingesetzt + item.cost;

    /* PATCH 1: raise the stat */
    var patch1;
    if (item.kind === 'eigenschaft') {
      patch1 = {
        kind: 'table_cell', file: '_illaen.md', slug: slug,
        section_path: ['Eigenschaften & Basiswerte', 'Eigenschaften'],
        row_key: { column: 'Eigenschaft', match: item.eigFull },
        column: 'Aktuell', value: String(newVal)
      };
    } else if (item.kind === 'talent') {
      patch1 = {
        kind: 'table_cell', file: item.file, slug: slug,
        section_path: [item.section],
        row_key: { column: item.rowKeyCol, match: item.name },
        column: 'TaW', value: String(newVal)
      };
    } else { /* zauber */
      patch1 = {
        kind: 'table_cell', file: item.file, slug: slug,
        section_path: ['Zauberliste'],
        row_key: { column: 'Zauber', match: item.name },
        column: 'ZfW', value: String(newVal)
      };
    }

    patchLocator(patch1)
      .then(function () {
        return patchLocator({
          kind: 'frontmatter', file: '_illaen.md', slug: slug,
          key: 'ap_verfuegbar', value: String(newAvail)
        });
      })
      .then(function () {
        return patchLocator({
          kind: 'frontmatter', file: '_illaen.md', slug: slug,
          key: 'ap_eingesetzt', value: String(newEinges)
        });
      })
      .then(function () {
        var today = new Date().toISOString().slice(0, 10);
        var aktion = item.kind === 'eigenschaft'
          ? (item.abbr + ' ' + item.currentVal + '→' + newVal)
          : item.kind === 'talent'
          ? (item.name + ' TaW ' + item.currentVal + '→' + newVal)
          : (item.name + ' ZfW ' + item.currentVal + '→' + newVal);
        return patchLocator({
          kind: 'table_append_row', file: 'steigerungs-log.md', slug: slug,
          section_path: ['Protokoll'],
          cells: [today, newAvail + ' verf.', aktion, String(item.cost), 'Steigerung im Dashboard']
        });
      })
      .then(function () {
        window.DSA.steigern.ap.verfuegbar = newAvail;
        window.DSA.steigern.ap.eingesetzt = newEinges;
        onSuccess();
      })
      .catch(function (err) { onError(err.message || 'Fehler'); });
  }

  /* Promise-Wrapper um doSteigern — additiv, ändert die PATCH-Logik nicht.
     Erlaubt sequentielles await im Sammel-Commit. */
  function doSteigernAsync(item) {
    return new Promise(function (resolve, reject) {
      doSteigern(item, resolve, function (msg) { reject(new Error(msg)); });
    });
  }

  /* ── Warenkorb (cart) ─────────────────────────────────────────────────
     Sammelt ausgewählte Items über alle 3 Sektionen, zeigt laufende
     AP-Summe gegen den Vorrat, committet sequentiell mit EINEM reload. */
  var cart = {
    selected: [],          /* {item, row} */
    bar: null,             /* footer DOM-Leiste */
    summaryEl: null,       /* Summen-/Zähler-Anzeige */
    commitBtn: null,       /* Sammel-Bestätigen-Button */
    statusEl: null,        /* Fehler-/Fortschritts-Meldung */
    committing: false
  };

  function cartTotal() {
    return cart.selected.reduce(function (sum, e) { return sum + (e.item.cost || 0); }, 0);
  }

  function cartUpdate() {
    if (!cart.bar) return;
    var n = cart.selected.length;
    var total = cartTotal();
    var avail = window.DSA.steigern.ap.verfuegbar;
    var over = total > avail;

    cart.summaryEl.textContent = n === 0
      ? 'Keine Auswahl'
      : n + (n === 1 ? ' Eintrag' : ' Einträge') + ' · ' + total + ' / ' + avail + ' AP';
    cart.summaryEl.classList.toggle('over', over && n > 0);

    cart.commitBtn.textContent = n === 0
      ? 'Steigern'
      : 'Steigern (' + n + ', ' + total + ' AP)';
    cart.commitBtn.disabled = cart.committing || n === 0 || over;
  }

  function cartToggle(item, row, on) {
    if (on) {
      cart.selected.push({ item: item, row: row });
      row.classList.add('sg-selected');
    } else {
      cart.selected = cart.selected.filter(function (e) { return e.item !== item; });
      row.classList.remove('sg-selected');
    }
    cartUpdate();
  }

  /* Sequentieller Sammel-Commit: pro Eintrag die volle doSteigern-Sequenz,
     await zwischen den Einträgen (jeder PATCH schreibt ap_* fort).
     Beim ersten Fehler: stoppen, melden was durchlief, dann reload. */
  function cartCommit() {
    if (cart.committing || cart.selected.length === 0) return;
    cart.committing = true;
    cart.commitBtn.disabled = true;
    cart.statusEl.classList.remove('over');
    cart.statusEl.textContent = 'Steigere …';

    var queue = cart.selected.slice();
    var done = 0;
    var ERR_RELOAD_DELAY_MS = 2500; // Fehlertext lesbar lassen, bevor neu geladen wird

    function step(i) {
      if (i >= queue.length) {
        cart.statusEl.textContent = 'Fertig — Seite wird neu geladen …';
        window.location.reload();
        return;
      }
      var entry = queue[i];
      cart.statusEl.textContent = 'Steigere ' + entry.item.displayName +
        ' (' + (i + 1) + '/' + queue.length + ') …';
      doSteigernAsync(entry.item).then(function () {
        done += 1;
        step(i + 1);
      }).catch(function (err) {
        /* Beim ersten Fehler stoppen. Melden, was bis hier durchlief, dann reload. */
        cart.statusEl.classList.add('over');
        cart.statusEl.textContent = '⚠ ' + err.message + ' — ' + done +
          ' von ' + queue.length + ' gesteigert. Seite wird neu geladen …';
        setTimeout(function () { window.location.reload(); }, ERR_RELOAD_DELAY_MS);
      });
    }
    step(0);
  }

  function buildCartBar() {
    var bar = document.createElement('div');
    bar.className = 'sg-cart';

    var summary = document.createElement('div');
    summary.className = 'sg-cart-summary';
    summary.textContent = 'Keine Auswahl';

    var status = document.createElement('div');
    status.className = 'sg-cart-status';

    var commit = document.createElement('button');
    commit.type = 'button';
    commit.className = 'sg-btn sg-btn--ok sg-cart-commit';
    commit.textContent = 'Steigern';
    commit.disabled = true;
    commit.addEventListener('click', cartCommit);

    bar.appendChild(summary);
    bar.appendChild(status);
    bar.appendChild(commit);

    cart.bar = bar;
    cart.summaryEl = summary;
    cart.statusEl = status;
    cart.commitBtn = commit;
    return bar;
  }

  /* ── Row renderer (one <tr> for the steiger-table) ───────────────────── */
  function renderRow(item) {
    var ap = window.DSA.steigern.ap.verfuegbar;
    var canAfford = item.cost !== null && ap >= item.cost;

    var row = document.createElement('tr');
    row.className = 'sg-row';

    /* Name cell */
    var nameCell = document.createElement('td');
    nameCell.className = 'sg-name';

    var nameLabel = document.createElement('span');
    nameLabel.textContent = item.displayName;
    nameCell.appendChild(nameLabel);

    /* Komplexitätsgrenze warning (Sprachen/Schriften only) */
    if (item.komplexitaet != null && item.currentVal >= item.komplexitaet) {
      var warnEl = document.createElement('span');
      warnEl.className = 'sg-cap-warn';
      warnEl.textContent = '⚠ Komplexitätsgrenze K' + item.komplexitaet;
      nameCell.appendChild(warnEl);
    }

    /* Wert cell (aktuell → nächster) */
    var valCell = document.createElement('td');
    valCell.className = 'sg-val';
    valCell.textContent = item.currentVal + ' → ' + (item.currentVal + 1);

    /* Kosten cell */
    var costCell = document.createElement('td');
    setCostCell(costCell, item.cost, canAfford);

    /* Aktion cell */
    var actionCell = document.createElement('td');
    actionCell.className = 'sg-action';

    row.appendChild(nameCell);
    row.appendChild(valCell);
    row.appendChild(costCell);
    row.appendChild(actionCell);

    /* Erfahrungs-Selektor (nur talent + zauber, nicht eigenschaft) */
    if (item.skt) {
      var erfSel = document.createElement('select');
      erfSel.className = 'sg-erf';
      erfSel.setAttribute('aria-label', 'Erfahrung: ' + item.displayName);
      [
        { label: '—', value: '0' },
        { label: 'gut (−1 Sp.)', value: '-1' },
        { label: 'schlecht (+1 Sp.)', value: '1' }
      ].forEach(function (opt) {
        var o = document.createElement('option');
        o.value = opt.value;
        o.textContent = opt.label;
        erfSel.appendChild(o);
      });

      erfSel.addEventListener('change', function () {
        var shift = parseInt(erfSel.value, 10);
        item.cost = calcApCost(item.skt, item.currentVal, shift);
        var canAffordNow = item.cost !== null &&
          window.DSA.steigern.ap.verfuegbar >= item.cost;
        setCostCell(costCell, item.cost, canAffordNow);
        cartUpdate();
      });

      actionCell.appendChild(erfSel);
    }

    /* Warenkorb-Auswahl: Checkbox statt Einzel-Steigern-Button.
       Nur für Items mit bekannten Kosten (cost !== null). */
    if (item.cost !== null) {
      var label = document.createElement('label');
      label.className = 'sg-select';

      var box = document.createElement('input');
      box.type = 'checkbox';
      box.className = 'sg-select-box';
      box.setAttribute('aria-label', 'In Warenkorb: ' + item.displayName);

      var hint = document.createElement('span');
      hint.className = 'sg-select-hint';
      hint.textContent = 'auswählen';

      box.addEventListener('change', function () {
        cartToggle(item, row, box.checked);
      });

      label.appendChild(box);
      label.appendChild(hint);
      actionCell.appendChild(label);
    } else {
      actionCell.textContent = '—';
    }

    return row;
  }

  /* ── Stufenaufstieg: 3 sequential PATCHes ─────────────────────────────── */
  /* Known limitation: no rollback on partial failure. Recovery: git revert. */
  function doStufenaufstieg(onSuccess, onError) {
    var slug = window.DSA.slug;
    var ap = window.DSA.steigern.ap;
    var oldStufe = ap.stufe;
    var newStufe = oldStufe + 1;

    /* PATCH 1: frontmatter stufe +1 */
    patchLocator({
      kind: 'frontmatter', file: '_illaen.md', slug: slug,
      key: 'stufe', value: String(newStufe)
    })
    .then(function () {
      /* PATCH 2: sync ## Abenteuerpunkte display table */
      return patchLocator({
        kind: 'table_cell', file: '_illaen.md', slug: slug,
        section_path: ['Abenteuerpunkte'],
        row_key: { column: 'Stufe', match: String(oldStufe) },
        column: 'Stufe', value: String(newStufe)
      });
    })
    .then(function () {
      /* PATCH 3: log to steigerungs-log.md */
      var today = new Date().toISOString().slice(0, 10);
      return patchLocator({
        kind: 'table_append_row', file: 'steigerungs-log.md', slug: slug,
        section_path: ['Protokoll'],
        cells: [today, ap.verfuegbar + ' verf.',
                'Stufe ' + oldStufe + '→' + newStufe + ' (GM)', '—',
                'Stufenaufstieg im Dashboard']
      });
    })
    .then(function () { ap.stufe = newStufe; onSuccess(); })
    .catch(function (err) { onError(err.message || 'Fehler'); });
  }

  /* ── Tab renderer ─────────────────────────────────────────────────────── */
  var EIG_ORDER = ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK'];
  var EIG_FULL = {
    MU: 'Mut', KL: 'Klugheit', IN: 'Intuition', CH: 'Charisma',
    FF: 'Fingerfertigkeit', GE: 'Gewandtheit', KO: 'Konstitution', KK: 'Körperkraft'
  };

  function renderSteigernTab() {
    var dsa = window.DSA;
    if (!dsa || !dsa.steigern) return;
    var ap = dsa.steigern.ap;

    /* AP overview */
    var overview = document.getElementById('steigern-ap-overview');
    if (overview) {
      var availStr = '<span class="sg-ap-label">AP verfügbar<\/span><span class="sg-ap-val avail">' + ap.verfuegbar + '<\/span>';
      var einsStr  = '<span class="sg-ap-label">AP eingesetzt<\/span><span class="sg-ap-val">' + ap.eingesetzt + '<\/span>';
      var gesStr   = '<span class="sg-ap-label">AP gesamt<\/span><span class="sg-ap-val">' + ap.gesamt + '<\/span>';
      var stufeStr = (ap.bis_naechste !== null && ap.bis_naechste > 0)
        ? '<div class="sg-stufe">Nächste Stufe (Stufe ' + (ap.stufe + 1) + '): noch ' + ap.bis_naechste + ' AP<\/div>'
        : '';
      overview.innerHTML = '<div class="sg-ap-row">' + availStr + einsStr + gesStr + '<\/div>' + stufeStr;

      /* Stufen-Aufstieg button (DSA 4.1 max Stufe = 10) */
      if (ap.stufe >= 10) return;
      var stufeBox = document.createElement('div');
      stufeBox.style.marginTop = '12px';

      var stufeBtn = document.createElement('button');
      stufeBtn.type = 'button';
      stufeBtn.className = 'sg-btn';
      stufeBtn.textContent = '⬆ Stufe aufsteigen (GM)';

      var stufeConfirm = document.createElement('div');
      stufeConfirm.className = 'sg-confirm hidden';

      var stufeJa = document.createElement('button');
      stufeJa.type = 'button';
      stufeJa.className = 'sg-btn sg-btn--ok';
      stufeJa.textContent = 'Ja';

      var stufeNein = document.createElement('button');
      stufeNein.type = 'button';
      stufeNein.className = 'sg-btn';
      stufeNein.textContent = 'Nein';

      var stufeErr = document.createElement('span');
      stufeErr.className = 'sg-error';
      stufeErr.style.display = 'none';

      stufeConfirm.appendChild(
        document.createTextNode('Stufe ' + ap.stufe + ' → ' + (ap.stufe + 1) + ' bestätigen? ')
      );
      stufeConfirm.appendChild(stufeJa);
      stufeConfirm.appendChild(stufeNein);

      stufeBtn.addEventListener('click', function () {
        stufeBtn.classList.add('hidden');
        stufeConfirm.classList.remove('hidden');
      });
      stufeNein.addEventListener('click', function () {
        stufeConfirm.classList.add('hidden');
        stufeBtn.classList.remove('hidden');
        stufeErr.style.display = 'none';
      });
      stufeJa.addEventListener('click', function () {
        stufeJa.disabled = true;
        stufeJa.textContent = '…';
        doStufenaufstieg(function () {
          window.location.reload();
        }, function (err) {
          stufeJa.disabled = false;
          stufeJa.textContent = 'Ja';
          stufeConfirm.classList.add('hidden');
          stufeBtn.classList.remove('hidden');
          stufeErr.textContent = '⚠ ' + err;
          stufeErr.style.display = '';
        });
      });

      stufeBox.appendChild(stufeBtn);
      stufeBox.appendChild(stufeConfirm);
      stufeBox.appendChild(stufeErr);
      overview.appendChild(stufeBox);
    }

    /* Steigerungsliste */
    var list = document.getElementById('steigern-list');
    if (!list) return;
    list.innerHTML = '';
    cart.selected = [];   /* frischer Warenkorb pro Render */

    /* Build one <table class="steiger-table"> per section with its own heading.
       `items` are pre-mapped objects ready for renderRow(). */
    function addSection(title, items) {
      var h = document.createElement('h4');
      h.className = 'sg-section-head';
      h.textContent = title;
      list.appendChild(h);

      var table = document.createElement('table');
      table.className = 'steiger-table';

      var thead = document.createElement('thead');
      var headRow = document.createElement('tr');
      ['Name', 'Wert', 'Kosten', 'Aktion'].forEach(function (label) {
        var th = document.createElement('th');
        th.textContent = label;
        headRow.appendChild(th);
      });
      thead.appendChild(headRow);
      table.appendChild(thead);

      var tbody = document.createElement('tbody');
      items.forEach(function (item) {
        tbody.appendChild(renderRow(item));
      });
      table.appendChild(tbody);

      list.appendChild(table);
    }

    /* Eigenschaften */
    addSection('Eigenschaften (Zielwert × 15 AP)', EIG_ORDER.map(function (abbr) {
      var val = dsa.eig[abbr];
      return {
        kind: 'eigenschaft', abbr: abbr,
        displayName: abbr + ' · ' + EIG_FULL[abbr],
        currentVal: val, cost: calcEigCost(val),
        eigFull: EIG_FULL[abbr] + ' (' + abbr + ')'
      };
    }));

    /* Talente & Kampftechniken */
    addSection('Talente & Kampftechniken', dsa.steigern.talente.map(function (t) {
      return {
        kind: 'talent', name: t.name,
        displayName: t.name + ' · SKT ' + t.skt,
        currentVal: t.taw, cost: calcApCost(t.skt, t.taw),
        skt: t.skt,
        section: t.section, file: t.file, rowKeyCol: t.row_key_column,
        komplexitaet: t.komplexitaet
      };
    }));

    /* Zauber */
    addSection('Zauber', dsa.steigern.zauber.map(function (z) {
      return {
        kind: 'zauber', name: z.name,
        displayName: z.name + ' · Lern ' + z.lern,
        currentVal: z.zfw, cost: calcApCost(z.lern, z.zfw),
        skt: z.lern,
        file: z.file
      };
    }));

    /* Warenkorb-Leiste (Summe + Sammel-Commit) unter den Tabellen */
    list.appendChild(buildCartBar());
    cartUpdate();
  }

  document.addEventListener('DOMContentLoaded', renderSteigernTab);
}());
