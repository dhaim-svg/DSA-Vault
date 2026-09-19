/* register.js — client-side search for the Register view of the Chronik tab (no backend: works under file://) */
(function () {
  'use strict';

  // Must fold exactly like fold() in parsers/register.py (casefold + NFKD, combining marks dropped),
  // otherwise "müller" would not be found in the pre-folded data-such attribute.
  function fold(s) {
    return String(s).toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/ß/g, 'ss');
  }

  function init() {
    var input = document.querySelector('.register-suche');
    if (!input) { return; }  // empty register: nothing to search
    var counter = document.querySelector('.register-zaehler');
    var empty = document.querySelector('.register-leer');
    var druckfilter = document.querySelector('.register-druckfilter');  // print-only header naming the active filter
    var groups = document.querySelectorAll('.register-gruppe');

    function apply() {
      var tokens = fold(input.value).split(/\s+/).filter(Boolean);
      var active = tokens.length > 0;
      var total = 0;
      var all = 0;
      groups.forEach(function (group) {
        var entries = group.querySelectorAll('.register-eintrag');
        var visible = 0;
        entries.forEach(function (entry) {
          var such = entry.dataset.such || '';
          var match = tokens.every(function (t) { return such.indexOf(t) !== -1; });
          entry.hidden = !match;
          if (match) { visible++; }
        });
        group.hidden = visible === 0;
        var count = group.querySelector('.register-count');
        if (count) { count.textContent = active ? visible + '/' + entries.length : String(entries.length); }
        total += visible;
        all += entries.length;
      });
      if (counter) { counter.textContent = active ? total + ' Treffer' : ''; }
      if (empty) { empty.hidden = !(active && total === 0); }
      if (druckfilter) {
        druckfilter.hidden = !active;
        druckfilter.textContent = active ? 'Gefiltert nach: "' + input.value.trim() + '" — ' + total + '/' + all + ' Einträge' : '';
      }
    }

    input.addEventListener('input', apply);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        input.value = '';
        apply();
      }
    });
    apply();
  }

  document.addEventListener('DOMContentLoaded', init);
}());
