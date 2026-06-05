# Sprint 011 Handoff — Steigern: Session-Erfahrungs-Modifikator (SKT-Spaltenverschiebung) + Status-Farb-Polish

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-021 → in-progress, plan.md anlegen)
- ✅ T1: **D-021** Erfahrungs-Modifikator als **SKT-Spaltenverschiebung** (WdS Kap. 6, S. 167) — neuer Helper `shiftSktColumn(skt, shift)` (Spaltenbuchstabe → Index ±shift, geklammert A…H, unbekannte Spalte unverändert); `calcApCost(skt, taw, shift)` bekam optionalen `shift`-Parameter (effektive Spalte VOR dem Bracket-Lookup, Bracket-Logik unangetastet, `calcEigCost` unverändert). Pro Zeile ein `<select class="sg-erf">` (`— / gut (−1 Sp.) / schlecht (+1 Sp.)`) **nur auf Talent- und Zauber-Zeilen** (nicht Eigenschaften — WdS: Eigenschaften immer Spalte H, keine Verschiebung). Change-Handler rechnet `item.cost` neu, frischt die Kosten-Zelle via neuem `setCostCell(cell, cost, canAfford)`-Helper auf und ruft `cartUpdate()`. `addSection` legt `skt` auf Talent-/Zauber-Items ab (`t.skt` / `z.lern`). Begleit-Quality-Fixes (inline): `setCostCell`-Dedup, `cartTotal` NaN-Guard (`e.item.cost || 0`), totes `item.erf` entfernt.
- ✅ T2: **Polish** Status-Farb-Kontrast — neues Token `--accent-fail: #e07a8a` für `.dp-result.fail` auf dem dunklen Würfel-Panel (Kontrast **2,62:1 → 5,98:1**, jetzt WCAG-AA-konform); toter Fallback `#8b1c2a` in `.dp-die-fehl` entfernt (`var(--accent-blood)`). `--accent-blood` bleibt für andere (helle) Kontexte (`.sg-error`, `.vn-grp.neg`, `.sg-cart-summary.over`) unverändert.
- ✅ T3: Verifikation (86/86 Tests, Static-Render exit 0, `node --check`, Logik-Check) + zweistufige Review (Spec ✅ + Code-Quality „Approved") für T1 + Schluss-Gesamtreview „Ready to merge".

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia (Stepper einreihig), Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
  - Würfel-Ergebnis-Status (`.dp-result`) farblich lesbar im Dark-Theme; **Fail-Status jetzt WCAG-AA** (T2)
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher-Slots
- ⭐ **Steigern-Tab:**
  - Einträge in echten Tabellen pro Sektion (Name / Wert / Kosten / Aktion), ausgerichtete Spalten (D-020)
  - **Warenkorb:** mehrere Steigerungen sektionsübergreifend per Checkbox auswählen, Gesamtkosten gegen AP-Vorrat, gesammelt bestätigen — ein Reload (D-019)
  - **Erfahrungs-Modifikator (neu, D-021):** pro Talent-/Zauber-Zeile `gut (−1 Spalte)` / `schlecht (+1 Spalte)` wählbar; verschiebt die SKT-Spalte (billiger/teurer), geklammert A…H; modifizierte Kosten fließen live in Kosten-Zelle, Warenkorb-Summe, Affordability-Guard und beim Commit in AP-Abzug + Steigerungs-Log. Transient: lebt auf den Item-Objekten, beim Reload (= nach Commit) verbraucht — kein localStorage. Eigenschaften ausgenommen.
  - Über-Budget-Auswahl rot signalisiert, Commit blockiert; Komplexitätsgrenze-Warnung pro Eintrag; Stufen-Aufstieg-Button unverändert
- 🗣️ Sprachen-Tab: Sprachen + Schriften mit Komplexität/TaW, rechtsbündig (D-017)
- 🎒 Inventar-Tab: Münzbeutel, Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung; Anmerkungen vollständig (D-015)
- 📋 Profil-Tab: Vor/Nachteile, Schlechte Eigenschaften (Konsequenz vollständig, D-016), Kampagne, Steigerungs-Log, Vorgeschichte; Namen HTML-escaped
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/`; `## Verlauf` editierbar + Persistenz
- ⬆️ Stufen-Aufstieg: GM-Grant-Button im Steigern-Tab
- 💾 Commit-Button: Commit-Feld + 💾 im Footer (D-014)
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 86/86 Testfälle bestanden (Baseline unverändert; D-021 ist JS-only, keine Regression in den Python-Daten/AP-Tests)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **`node --check static/steigern.js`:** ok
- **Logik-Check (node):** `shiftSktColumn('A',-1)→A`, `shiftSktColumn('H',+1)→H`, `shiftSktColumn('C',-1)→B`, `calcApCost('D',7,-1) == calcApCost('C',7,0) == 6` ✓
- **Struktur:** `--accent-fail` 2× im Output (Definition + `.dp-result.fail`), stale `#8b1c2a` = 0 Treffer ✓
- **Review:** Spec ✅ + Code-Quality „Approved with minor issues" (Minors inline gefixt) für T1; Schluss-Gesamtreview bestätigt korrekten Cost→Cart→Commit→Log-Pfad, Kontrast numerisch validiert → „Ready to merge"

## Als nächstes (Sprint 012)

- **D-018** (Zauber: Inline-Vorschau des Artikels, L) — der letzte offene Backlog-EPIC; eigenständiger Umbau: neuer Flask-Read-Endpoint liest Zauber-`.md` + rendert HTML, Inline-Panel/Modal im Zauber-Tab (`dashboard.html.j2:1311-1506`), Klick-Guard in `static/dice.js:520-532` beachten. `↗`-Obsidian-Link bleibt.
- (Reihenfolge = Empfehlung, nicht Pflicht)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Steigerungs-Log vermerkt den Erfahrungs-Modifikator nicht** — der Log-Eintrag zeigt nur die (bereits modifizierten) AP-Kosten, ohne `[gut]`/`[schlecht]`-Hinweis. Bewusst out-of-scope; nachrüstbar, indem der Shift auf dem Item gespeichert (`item.erfShift`) und in `doSteigern` an den `aktion`-String angehängt wird. S-Kandidat.
- **`.sg-erf` ist `display:block`** → Talent-/Zauber-Zeilen sind in der Aktion-Spalte etwas höher als Eigenschaften-Zeilen (Select über Checkbox gestapelt). Rein kosmetisch; `inline-block`/Flex-Wrapper wäre kompakter. Polish-Kandidat.
- **`.sg-action` hat keine eigene CSS-Regel** (vorbestehend, kein Regression) — Aktion-Spalte verlässt sich auf Tabellen-Auto-Layout.
- **Vereinfachtes lineares SKT-Modell** bleibt: `SKT_COSTS` nutzt Faktor = Spalten-Ordnungszahl (A=1…H=8), **kein echtes A*** und nicht die authentischen Faktoren (8/10/20 für F/G/H). Linke Klammerung daher auf A statt A*. Authentische SKT wäre ein eigener Backlog-Punkt.
- **Kein Vorrat/Zähler & GM-Grant** für Erfahrungen (freies Vertrauensmodell) und **keine Eigenschaften-Spaltenverschiebung** — bewusst weggelassen.
- **Cost-Cell `affordable`/`expensive` pro Zeile vs. Warenkorb**, **kein Rollback bei Teil-Commit**, **`kampagne_slug` hardcoded** (`server.py:27`), **Guided Stufen-Aufstieg** — bleiben offen wie zuvor.
