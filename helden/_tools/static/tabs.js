/* tabs.js — client-side tab controller for DSA dashboard */
(function () {
  'use strict';

  var STORAGE_KEY = 'dsa-active-tab';
  var DEFAULT_TAB = 'kampf';

  function switchTab(id) {
    document.querySelectorAll('.tab-content').forEach(function (el) {
      el.classList.toggle('tab-content--active', el.id === 'tab-' + id);
    });
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
      btn.classList.toggle('tab-btn--active', btn.dataset.tab === id);
    });
    try { sessionStorage.setItem(STORAGE_KEY, id); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { switchTab(btn.dataset.tab); });
    });
    var saved;
    try { saved = sessionStorage.getItem(STORAGE_KEY); } catch (e) {}
    switchTab(saved || DEFAULT_TAB);
  });
}());
