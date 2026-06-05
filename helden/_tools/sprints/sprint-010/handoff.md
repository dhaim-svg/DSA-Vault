# Sprint 010 Handoff — Steigern-Tab Umbau (Warenkorb-Modus + eigene Tabelle)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-019+D-020 → in-progress, plan.md anlegen)
- ✅ T1: **D-020** Steigerungsspalte als eigene Tabelle — `.sg-row`-Flex-Zeilen → `<table class="steiger-table">` (eine Tabelle pro Sektion: Eigenschaften / Talente+KT / Zauber), Vorbild `.lang-table`; `renderRow` liefert `<tr>` mit 4 `<td>` (Name / Wert / Kosten / Aktion), `addSection(title, items)` baut thead+tbody. Begleitfix: dead `flex-shrink:0` auf `.sg-cap-warn` entfernt.
- ✅ T2: **D-019** Warenkorb-Modus — Checkbox-Auswahl pro Zeile statt Sofort-Commit; sticky Cart-Leiste (`.sg-cart`) unter den Tabellen zeigt laufende AP-Gesamtsumme „N Einträge · X / Y AP" gegen `window.DSA.steigern.ap.verfuegbar`; Übersteigt die Auswahl den Vorrat → Summe rot (`.over`) + Commit-Button disabled; Sammel-Commit (`cartCommit`) führt die unveränderte `doSteigern`-4×-PATCH-Sequenz **sequentiell** pro Eintrag aus (`doSteigernAsync`-Promise-Wrapper) mit genau **einem** Reload am Ende. Begleitfix: `ERR_RELOAD_DELAY_MS`-Konstante benannt, orphaned `.sg-btn-area`-CSS entfernt.
- ✅ T3: **Polish** `.dp-result`-Statusfarben — dunkle Hex-Farben (`#1a6b2a`, `#8b1c2a`, …) durch Theme-Accent-Tokens ersetzt (`--accent-aup` success, `--accent-blood` fail, `--accent-cold` crit, `--accent-gold` patzer); lesbar auf dem dunklen `#131c28`-Würfel-Panel (D-012); transluzente Hintergründe bleiben.
- ✅ T4: **Polish** `| e` HTML-Escaping auf `s.name` / `v.name` / `n.name` (Vor-/Nachteile, Schlechte Eigenschaften) ergänzt — Muster-Konsistenz mit den `anmerkung`/`konsequenz`-Feldern aus Sprint 009.
- ✅ T5: Verifikation (86/86 Tests, Static-Render exit 0, `node --check`, Strukturchecks) + zweistufige Review (Spec + Code-Quality) pro Feature-Task + Schluss-Gesamtreview „Ready to merge".

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia (Stepper einreihig), Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
  - Würfel-Ergebnis-Status (`.dp-result`) jetzt farblich lesbar im Dark-Theme (D-012 + T3)
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher-Slots
- ⭐ **Steigern-Tab (neu umgebaut):**
  - Einträge in echten Tabellen pro Sektion (Name / Wert / Kosten / Aktion), ausgerichtete Spalten (D-020)
  - **Warenkorb:** mehrere Steigerungen (auch sektionsübergreifend) per Checkbox auswählen, Gesamtkosten gegen AP-Vorrat sehen, gesammelt bestätigen — ein Reload (D-019)
  - Über-Budget-Auswahl wird rot signalisiert, Commit blockiert
  - Komplexitätsgrenze-Warnung pro Eintrag bleibt; Stufen-Aufstieg-Button unverändert
- 🗣️ Sprachen-Tab: Sprachen + Schriften mit Komplexität/TaW, rechtsbündig (D-017)
- 🎒 Inventar-Tab: Münzbeutel, Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung; Anmerkungen vollständig (D-015)
- 📋 Profil-Tab: Vor/Nachteile, Schlechte Eigenschaften (Konsequenz vollständig, D-016), Kampagne, Steigerungs-Log, Vorgeschichte; Namen jetzt HTML-escaped (T4)
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/`; `## Verlauf` editierbar + Persistenz
- ⬆️ Stufen-Aufstieg: GM-Grant-Button im Steigern-Tab
- 💾 Commit-Button: Commit-Feld + 💾 im Footer (D-014)
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 86/86 Testfälle bestanden (Baseline unverändert; Steigern-Tests `test_steigerbar.py`/`test_stufen.py`/`test_commit.py` grün — sie prüfen Daten/AP-Logik, nicht das DOM)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **`node --check static/steigern.js`:** ok
- **Strukturelle Checks:**
  - D-020: `steiger-table`-CSS im HTML (4 Treffer) ✓
  - D-019: `sg-cart` (7 Treffer), `sg-select` (4 Treffer) ✓
  - T3: `.dp-result.success/fail/crit/patzer` nutzen `var(--accent-*)` ✓
  - T4: `s/v/n.name | e` im Template (8 `| e`-Treffer gesamt) ✓
- **Review:** Spec ✅ + Code-Quality ✅ pro Task; Schluss-Gesamtreview bestätigt: T1+T2-Interaktion sauber, kumulativer Affordability-Guard + sequentieller Commit ohne Double-Spend/State-Sync-Gefahr → „Ready to merge"

## Als nächstes (Sprint 011)

- **D-021** (Steigern: Session-Erfahrungs-Kostenmodifikator, M) — baut thematisch direkt auf dem jetzt umgebauten Steigern-Tab auf; Session-State analog `static/session.js` (localStorage `dsa:<slug>:session`), Anwendung in `calcApCost`/`renderRow`. Naheliegendster nächster Schritt, solange der Steigern-Code frisch im Kopf ist.
- **D-018** (Zauber: Inline-Vorschau des Artikels, L) — unabhängiger Umbau; neuer Flask-Read-Endpoint liest Zauber-`.md` + rendert HTML, Inline-Panel/Modal im Zauber-Tab; Klick-Guard in `static/dice.js` beachten.
- (Reihenfolge = Empfehlung, nicht Pflicht)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **`.dp-result.fail` Kontrast grenzwertig** — nutzt `--accent-blood` (#a83246), Kontrast ~2,7:1 auf dem dunklen `#131c28`-Panel; die dunkelste der vier Status-Farben, knapp unter WCAG. Bewusst token-konsistent belassen (ein neues helleres Rot-Token wäre die saubere Nachbesserung statt eines One-off-Hex). S-Nachbesserungskandidat fürs Backlog.
- **Stale Fallback `#8b1c2a`** in `.dp-die-fehl { color: var(--accent-blood, #8b1c2a) }` — toter Fallback (Var ist immer definiert), selbe Alt-Status-Hex-Familie wie T3. Trivialer Cleanup bei Gelegenheit.
- **Cost-Cell `affordable`/`expensive`** im Steigern-Tab prüft weiterhin pro Zeile gegen den vollen AP-Vorrat (nicht gegen die kumulierte Warenkorb-Auswahl) — die `.sg-cart-summary.over`-Summe ist der maßgebliche Guard. Kosmetisch; ggf. bei künftigem Polish vereinheitlichen.
- **Kein Rollback bei Teil-Commit** — schlägt mitten im Sammel-Commit ein PATCH fehl (z.B. 409), stoppt der Batch beim ersten Fehler, meldet „K von N gesteigert" und reloadet (Disk-Stand übernehmen). Bestehende, dokumentierte `doSteigern`-Limitierung, unverändert.
- **`kampagne_slug` hardcoded** (`server.py:27`) und **Guided Stufen-Aufstieg** — bleiben offen wie zuvor.
- **D-018/D-021** — bewusst auf spätere Sprints verschoben.
