/**
 * util.js — Shared UI utilities for the DSA dashboard.
 * Must be loaded before app.js and commit.js.
 */
(function () {
  'use strict';
  var indicatorTimer = null;
  window.dsaShowIndicator = function (text, isError) {
    var indicator = document.getElementById('save-indicator');
    if (!indicator) return;
    indicator.textContent = text;
    indicator.style.background = isError ? 'rgba(180,40,40,0.85)' : 'rgba(0,0,0,0.75)';
    indicator.classList.add('visible');
    clearTimeout(indicatorTimer);
    indicatorTimer = setTimeout(function () {
      indicator.classList.remove('visible');
    }, 2500);
  };
}());
