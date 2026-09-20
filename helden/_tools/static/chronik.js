/* chronik.js — Roh/Kompiliert/Register view switcher for the Chronik tab */
(function () {
  'use strict';

  var STORAGE_KEY = 'dsa-chronik-view';
  var DEFAULT_VIEW = 'roh';
  var VIEWS = ['roh', 'kompiliert', 'register'];

  function switchView(view) {
    document.querySelectorAll('.chronik-view').forEach(function (el) {
      el.classList.toggle('chronik-view--active', el.dataset.view === view);
    });
    document.querySelectorAll('.chronik-switch-btn').forEach(function (btn) {
      var active = btn.dataset.view === view;
      btn.classList.toggle('chronik-switch-btn--active', active);
      btn.setAttribute('aria-selected', active ? 'true' : 'false');
    });
    try { sessionStorage.setItem(STORAGE_KEY, view); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.chronik-switch-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { switchView(btn.dataset.view); });
    });
    var saved;
    try { saved = sessionStorage.getItem(STORAGE_KEY); } catch (e) {}
    switchView(VIEWS.indexOf(saved) !== -1 ? saved : DEFAULT_VIEW);
  });

  // Chrome does not print the body of a closed <details>; open them for printing.
  // D-055: a <textarea> only prints its scrolled viewport, not its full scrollable content —
  // grow it to its own scrollHeight for the duration of the print, then restore. Resizing the
  // live element (instead of a server-rendered mirror) is correct by construction even for an
  // unsaved edit; see task-2-brief.md for why a mirror was rejected.
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('details.chronik-abend').forEach(function (d) {
      if (d.dataset.wasOpen === undefined) { d.dataset.wasOpen = d.open ? '1' : ''; }
      d.open = true;
    });
    document.querySelectorAll('.journal-verlauf').forEach(function (t) {
      if (t.dataset.wasHeight === undefined) { t.dataset.wasHeight = t.style.height || ''; }
      t.style.height = t.scrollHeight + 'px';
    });
  });

  window.addEventListener('afterprint', function () {
    document.querySelectorAll('details.chronik-abend').forEach(function (d) {
      if (d.dataset.wasOpen === undefined) { return; }
      d.open = (d.dataset.wasOpen === '1');
      delete d.dataset.wasOpen;
    });
    document.querySelectorAll('.journal-verlauf').forEach(function (t) {
      if (t.dataset.wasHeight === undefined) { return; }
      t.style.height = t.dataset.wasHeight;
      delete t.dataset.wasHeight;
    });
  });
}());
