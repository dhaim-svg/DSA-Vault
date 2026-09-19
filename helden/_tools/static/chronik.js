/* chronik.js — Roh/Kompiliert view switcher for the Chronik tab */
(function () {
  'use strict';

  var STORAGE_KEY = 'dsa-chronik-view';
  var DEFAULT_VIEW = 'roh';
  var VIEWS = ['roh', 'kompiliert'];

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
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('details.chronik-abend').forEach(function (d) {
      if (d.dataset.wasOpen === undefined) { d.dataset.wasOpen = d.open ? '1' : ''; }
      d.open = true;
    });
  });

  window.addEventListener('afterprint', function () {
    document.querySelectorAll('details.chronik-abend').forEach(function (d) {
      if (d.dataset.wasOpen === undefined) { return; }
      d.open = (d.dataset.wasOpen === '1');
      delete d.dataset.wasOpen;
    });
  });
}());
