/* Sortierung Zauberliste: Toolbar-Button [data-spell-sort] und Klick auf die Kopfzeile
   durchlaufen Standard -> ZfW absteigend -> ZfW aufsteigend -> Standard. */
(function () {
  'use strict';

  var list = document.querySelector('[data-spell-list]');
  var btn = document.querySelector('[data-spell-sort]');
  if (!list || !btn) return;

  var rows = Array.prototype.filter.call(list.children, function (el) {
    return el.classList.contains('spell');
  });
  var original = rows.slice();
  var head = document.querySelector('.spell-head');

  var STATES = ['none', 'desc', 'asc'];
  var LABEL = { none: 'Standard', desc: 'ZfW ↓', asc: 'ZfW ↑' };
  var ARIA_STATE = { none: 'Standard', desc: 'ZfW absteigend', asc: 'ZfW aufsteigend' };
  var ARIA_NEXT = { none: 'absteigend', desc: 'aufsteigend', asc: 'Standardreihenfolge' };
  var state = 'none';

  function zfw(row) {
    var cell = row.querySelector('.zfw-num');
    return (cell && parseInt(cell.textContent, 10)) || 0;
  }

  function sorted() {
    if (state === 'none') return original;
    var dir = state === 'asc' ? 1 : -1;
    return original
      .map(function (row, i) { return { row: row, i: i, z: zfw(row) }; })
      .sort(function (a, b) { return (a.z - b.z) * dir || a.i - b.i; })
      .map(function (x) { return x.row; });
  }

  function render() {
    sorted().forEach(function (row) { list.appendChild(row); });
    btn.textContent = 'Sortierung: ' + LABEL[state];
    btn.setAttribute('data-sort-state', state);
    btn.setAttribute('aria-label', 'Zauber sortieren, aktuell: ' + ARIA_STATE[state] +
      '. Klicken für ' + ARIA_NEXT[state] + '.');
  }

  function cycle() {
    state = STATES[(STATES.indexOf(state) + 1) % STATES.length];
    render();
  }

  btn.addEventListener('click', cycle);
  if (head) head.addEventListener('click', cycle);
})();
