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

  /* Cost to raise currentTaw → currentTaw+1.
     Bracket is determined by the TARGET value (currentTaw + 1). */
  function calcApCost(skt, currentTaw) {
    var costs = SKT_COSTS[skt];
    if (!costs) return null;
    var targetTaw = currentTaw + 1;
    var bracket = targetTaw <= 5 ? 0 : targetTaw <= 10 ? 1 : targetTaw <= 15 ? 2 : 3;
    return costs[bracket];
  }

  /* Cost to raise eigenschaft → eigenschaft+1 = (currentVal + 1) * 15 */
  function calcEigCost(currentVal) {
    return (currentVal + 1) * 15;
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
    costCell.className = 'sg-cost ' + (canAfford ? 'affordable' : 'expensive');
    costCell.textContent = item.cost !== null ? item.cost + ' AP' : '—';

    /* Aktion cell */
    var actionCell = document.createElement('td');
    actionCell.className = 'sg-action';

    row.appendChild(nameCell);
    row.appendChild(valCell);
    row.appendChild(costCell);
    row.appendChild(actionCell);

    if (item.cost !== null && canAfford) {
      var btnArea = document.createElement('span');
      btnArea.className = 'sg-btn-area';

      var steigBtn = document.createElement('button');
      steigBtn.type = 'button';
      steigBtn.className = 'sg-btn';
      steigBtn.textContent = 'Steigern';

      var confirm = document.createElement('div');
      confirm.className = 'sg-confirm hidden';
      confirm.textContent = item.displayName + ' für ' + item.cost + ' AP?';

      var jaBtn = document.createElement('button');
      jaBtn.type = 'button';
      jaBtn.className = 'sg-btn sg-btn--ok';
      jaBtn.textContent = 'Ja';

      var neinBtn = document.createElement('button');
      neinBtn.type = 'button';
      neinBtn.className = 'sg-btn';
      neinBtn.textContent = 'Nein';

      confirm.appendChild(jaBtn);
      confirm.appendChild(neinBtn);

      steigBtn.addEventListener('click', function () {
        steigBtn.classList.add('hidden');
        confirm.classList.remove('hidden');
      });
      neinBtn.addEventListener('click', function () {
        confirm.classList.add('hidden');
        steigBtn.classList.remove('hidden');
      });
      jaBtn.addEventListener('click', function () {
        jaBtn.disabled = true;
        jaBtn.textContent = '…';
        doSteigern(item, function () {
          window.location.reload();
        }, function (err) {
          jaBtn.disabled = false;
          jaBtn.textContent = 'Ja';
          var prev = actionCell.querySelector('.sg-error');
          if (prev) prev.remove();
          var errEl = document.createElement('span');
          errEl.className = 'sg-error';
          errEl.textContent = '⚠ ' + err;
          actionCell.appendChild(errEl);
          confirm.classList.add('hidden');
          steigBtn.classList.remove('hidden');
          steigBtn.disabled = false;
        });
      });

      btnArea.appendChild(steigBtn);
      btnArea.appendChild(confirm);
      actionCell.appendChild(btnArea);
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
        file: z.file
      };
    }));
  }

  document.addEventListener('DOMContentLoaded', renderSteigernTab);
}());
