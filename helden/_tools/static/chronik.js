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
  // D-055 (v2, Final-Review Important): a <textarea> only prints its scrolled viewport. v1 grew the live
  // element to its own scrollHeight, but scrollHeight was measured at the SCREEN layout width — narrower
  // at real print width, the same text wraps to more lines, so v1 still lost ~17% of the text at normal
  // desktop windows (measured: 48 missing lines comparing a 1280px vs. 718px browser window's real
  // page.pdf() output; only 718px happens to make print width equal screen width, hiding the bug there).
  // Fix: snapshot the live (possibly-unsaved) t.value into a plain flowed <pre> mirror and print that
  // instead of the textarea — a normal block element that the browser's own print layout wraps/sizes
  // correctly at whatever width actually applies, with no manual measurement.
  window.addEventListener('beforeprint', function () {
    document.querySelectorAll('details.chronik-abend').forEach(function (d) {
      if (d.dataset.wasOpen === undefined) { d.dataset.wasOpen = d.open ? '1' : ''; }
      d.open = true;
    });
    document.querySelectorAll('.journal-verlauf').forEach(function (t) {
      var mirror = t.nextElementSibling;
      if (!mirror || !mirror.classList.contains('journal-verlauf-print')) {
        mirror = document.createElement('pre');
        mirror.className = 'journal-verlauf-print';
        t.insertAdjacentElement('afterend', mirror);
      }
      mirror.textContent = t.value; // textContent, never innerHTML — session text is untrusted user input
    });
  });

  window.addEventListener('afterprint', function () {
    document.querySelectorAll('details.chronik-abend').forEach(function (d) {
      if (d.dataset.wasOpen === undefined) { return; }
      d.open = (d.dataset.wasOpen === '1');
      delete d.dataset.wasOpen;
    });
    document.querySelectorAll('.journal-verlauf').forEach(function (t) {
      var mirror = t.nextElementSibling;
      if (mirror && mirror.classList.contains('journal-verlauf-print')) { mirror.textContent = ''; }
    });
  });
}());
