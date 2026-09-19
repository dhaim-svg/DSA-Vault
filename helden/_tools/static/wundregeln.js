/**
 * wundregeln.js — DSA 4.1 Wundregel (WdS S. 57), einzige Quelle der Regel.
 *
 * Pro Wunde sinken AT-, PA-, FK- und INI-Basiswert sowie die GE um je 2 Punkte, die GS um 1.
 * Wunden sind kumulativ. Nichts anderes wird gesenkt: Talent-, Zauber- und sonstige
 * Eigenschaftsproben (außer GE) sowie Schadenswürfe bekommen keinen Wundabzug.
 *
 * Rein (kein DOM, kein Storage) — wird von session.js UND dice.js benutzt, auch unter
 * file://, wo session.js nichts initialisiert. Muss daher vor beiden geladen werden.
 */
(function () {
  // Abzug je Wunde (WdS S. 57). Reihenfolge = Reihenfolge im Geltungsbereich-Text.
  var JE_WUNDE = { AT: -2, PA: -2, FK: -2, INI: -2, GE: -2, GS: -1 };

  // Zahl <= 0: Gesamtabzug von `wunden` Wunden auf `ziel`; 0 bei unbekanntem Ziel (kein -0).
  function wundMod(wunden, ziel) {
    if (!(wunden > 0) || !Object.prototype.hasOwnProperty.call(JE_WUNDE, ziel)) return 0;
    return wunden * JE_WUNDE[ziel];
  }

  // Kurzer Geltungsbereich fuer Widget/Badge, z. B. "AT/PA/FK/INI/GE −4, GS −2"; '' ohne Wunden.
  function geltungText(wunden) {
    if (!(wunden > 0)) return '';
    var gruppen = [];   // [{ abzug, ziele: [...] }] — Ziele mit gleichem Abzug zusammengefasst
    Object.keys(JE_WUNDE).forEach(function (ziel) {
      var abzug = wundMod(wunden, ziel);
      var g = gruppen.find(function (x) { return x.abzug === abzug; });
      if (g) g.ziele.push(ziel); else gruppen.push({ abzug: abzug, ziele: [ziel] });
    });
    return gruppen.map(function (g) {
      return g.ziele.join('/') + ' −' + Math.abs(g.abzug);
    }).join(', ');
  }

  window.DSAWundregeln = { JE_WUNDE: JE_WUNDE, wundMod: wundMod, geltungText: geltungText };
})();
