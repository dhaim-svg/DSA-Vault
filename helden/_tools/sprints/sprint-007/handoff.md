# Sprint 007 Handoff — Sprachen-Tab (D-008) + Stufen-Aufstieg (D-009)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-008+D-009 → in-progress, sprints/sprint-007/plan.md)
- ✅ T1: Parser — `entry['komplexitaet'] = safe_int(...)` in Talente-Schleife für Sprachen/Schriften; Feld in `steigerbar_talente` propagiert; 3 neue Tests (84 gesamt)
- ✅ T2: UI — neuer 🗣️ Sprachen-Tab (`data-tab="sprachen"`, `#tab-sprachen`) mit Name·Komplexität·TaW-Tabellen für Sprachen + Schriften; `.lang-cap-warn`-Badge wenn TaW ≥ Komplexität; `| e`-Escaping auf allen user-content-Feldern
- ✅ T3: Steigern — `.sg-cap-warn`-Inline-Warnung in Steigern-Tab wenn TaW ≥ Komplexität; warn-only (Steigern-Button bleibt aktiv); `komplexitaet`-Feld durch Item-Objekt durchgereicht
- ✅ T4: Stufen-Aufstieg — `doStufenaufstieg()` mit 3 sequenziellen PATCHes (frontmatter `stufe+1` → `table_cell` AP-Anzeige-Tabelle → `table_append_row` Protokoll); GM-Grant-Button in AP-Übersicht; Stufe-10-Guard; `ap.stufe` In-Memory-Update nach Erfolg
- ✅ T5: Verifikation (84/84 Tests, Static-Render sauber, HTML-Checks bestanden); wiki-luecken.md L15 (Stufe/AP-Schwellen-Gap)

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher-Slots (Befüllen/Entleeren)
- ⭐ Steigern-Tab: AP-Übersicht, Eigenschaften/Talente/Zauber steigerbar; ⚠ Komplexitätsgrenze-Warnung für Sprachen
- 🗣️ **Sprachen-Tab (NEU):** Sprachen + Schriften mit Komplexität/TaW; Warn-Badge wenn TaW ≥ Komplexität
- 🎒 Inventar-Tab: Münzbeutel (Stepper), Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung
- 📋 Profil-Tab: Vor/Nachteile, Kampagne-Übersicht, Steigerungs-Log, Vorgeschichte
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/` anzeigen; `## Verlauf` editierbar + Persistenz
- ⬆️ **Stufen-Aufstieg (NEU):** GM-Grant-Button im Steigern-Tab; schreibt `stufe`, AP-Anzeige-Tabelle und Protokoll-Log
- 💾 Commit-Button: Dashboard-Änderungen direkt aus dem Browser in Git sichern (nur `helden/`, kein push)
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 84/84 Testfälle bestanden (81 Sprint-006-Baseline + 3 neue Komplexität-Tests)
  - +3 `test_steigerbar.py` (komplexitaet in `talente`, in `steigerbar_talente`, None für Nicht-Sprachen)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **Sprachen-Tab:** `data-tab="sprachen"`, `#tab-sprachen`, Bosparano/Garethi/Tulamidya/Kusliker gerendert ✓
- **Warn-Badge:** `.lang-cap-warn` nur als CSS-Regel (keine Badges, da Illaens TaW < Komplexität) ✓
- **Steigern-Tab:** `.sg-cap-warn` CSS vorhanden; Warn-Logik in `steigern.js` ✓
- **Stufen-Aufstieg:** `doStufenaufstieg` in `steigern.js`, Stufe-10-Guard, `ap.stufe`-In-Memory-Update ✓
- **Sicherheit:** `| e` auf allen user-content-Feldern in `#tab-sprachen` ✓

## Als nächstes (Sprint 8)

- **D-007-Erweiterung** (S): Commit-Message im Browser eintippen — war bewusst Out-of-Scope in Sprint 6; einfach nachzurüsten (Input-Feld in `commit.js` + `POST /api/commit` body erweitern)
- Alternativ: nächstes Backlog-EPIC nach Bedarf — Backlog ist aktuell leer; User kann neue EPICs einpflegen.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Harte Komplexitätsgrenze-Sperre**: User wählte warn-only; Steigern über die Grenze hinaus bleibt möglich
- **Sonder-Caps einzelner Sprachen** (Errata, z. B. „bis K15 ohne Vorteil"): Sprint nutzt nur TaW ≤ Komplexität; Errata-Fälle in `wiki/dsa-4.1/talente/sprachen-schriften.md` vorhanden
- **AP-Schwellen-Datenkonflikt**: `AP_STUFEN` in `held.py` (Stufe 4 = 1500 AP) vs. handgeschriebene Notiz in `steigerungs-log.md` Z. 31 (nennt 4200 AP) — in `wiki-luecken.md` L15 dokumentiert; GM-Grant-Flow nicht betroffen
- **Stufen-Aufstieg ohne Basiswert-/Eigenschaftsanhebungen**: Stufe ist reines Label; geführter Aufstieg (LE/AE/AU etc. anheben) bewusst Out-of-Scope
- **`kampagne_slug` hardcoded als `"drachenchronik"`** — in `server.py:25`; zweite Kampagne würde manuelle Anpassung brauchen (seit Sprint 6 bekannt)
- **`showIndicator` dupliziert** in `commit.js` und `journal.js` — keine funktionale Regression, aber Wartungs-Divergenz (seit Sprint 6 bekannt)
