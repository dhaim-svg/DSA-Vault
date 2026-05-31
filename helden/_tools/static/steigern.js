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

  /* ── Steigern: 3 sequential PATCHes ──────────────────────────────────── */
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

  /* ── Row renderer ─────────────────────────────────────────────────────── */
  function renderRow(item) {
    var ap = window.DSA.steigern.ap.verfuegbar;
    var canAfford = item.cost !== null && ap >= item.cost;

    var row = document.createElement('div');
    row.className = 'sg-row';

    var nameEl = document.createElement('span');
    nameEl.className = 'sg-name';
    nameEl.textContent = item.displayName;

    var valEl = document.createElement('span');
    valEl.className = 'sg-val';
    valEl.textContent = item.currentVal + ' → ' + (item.currentVal + 1);

    var costEl = document.createElement('span');
    costEl.className = 'sg-cost ' + (canAfford ? 'affordable' : 'expensive');
    costEl.textContent = item.cost !== null ? item.cost + ' AP' : '—';

    row.appendChild(nameEl);
    row.appendChild(valEl);
    row.appendChild(costEl);

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
          var errEl = document.createElement('span');
          errEl.className = 'sg-error';
          errEl.textContent = '⚠ ' + err;
          row.appendChild(errEl);
          confirm.classList.add('hidden');
          steigBtn.classList.remove('hidden');
          steigBtn.disabled = false;
        });
      });

      btnArea.appendChild(steigBtn);
      btnArea.appendChild(confirm);
      row.appendChild(btnArea);
    }

    return row;
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
    }

    /* Steigerungsliste */
    var list = document.getElementById('steigern-list');
    if (!list) return;
    list.innerHTML = '';

    function addSection(title) {
      var h = document.createElement('h4');
      h.className = 'sg-section-head';
      h.textContent = title;
      list.appendChild(h);
    }

    /* Eigenschaften */
    addSection('Eigenschaften (Zielwert × 15 AP)');
    EIG_ORDER.forEach(function (abbr) {
      var val = dsa.eig[abbr];
      list.appendChild(renderRow({
        kind: 'eigenschaft', abbr: abbr,
        displayName: abbr + ' · ' + EIG_FULL[abbr],
        currentVal: val, cost: calcEigCost(val),
        eigFull: EIG_FULL[abbr] + ' (' + abbr + ')'
      }));
    });

    /* Talente & Kampftechniken */
    addSection('Talente & Kampftechniken');
    dsa.steigern.talente.forEach(function (t) {
      list.appendChild(renderRow({
        kind: 'talent', name: t.name,
        displayName: t.name + ' · SKT ' + t.skt,
        currentVal: t.taw, cost: calcApCost(t.skt, t.taw),
        section: t.section, file: t.file, rowKeyCol: t.row_key_column
      }));
    });

    /* Zauber */
    addSection('Zauber');
    dsa.steigern.zauber.forEach(function (z) {
      list.appendChild(renderRow({
        kind: 'zauber', name: z.name,
        displayName: z.name + ' · Lern ' + z.lern,
        currentVal: z.zfw, cost: calcApCost(z.lern, z.zfw),
        file: z.file
      }));
    });
  }

  document.addEventListener('DOMContentLoaded', renderSteigernTab);
}());
