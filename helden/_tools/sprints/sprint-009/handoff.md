# Sprint 009 Handoff — Manual-Test Polish (D-012 … D-017)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-012…D-017 → in-progress, plan.md anlegen)
- ✅ T1: D-012 Würfel-Panel Lesbarkeit — `.dice-panel` bekommt `background: var(--bg-card)` + explizites `color: var(--ink)`; dunkler Panel lesbar im Dark-Theme
- ✅ T2: D-013 Vitalia-Stepper — `flex-wrap: nowrap` auf `.vital-stepper`; Begleitfix `.vital { grid-template-columns: 60px 1fr auto }` damit 3. Spalte wächst
- ✅ T3: D-017 Sprachen Komplexitäts-Spalte — `text-align: right` auf `.lang-table .l-kompl` (beide Tabellen)
- ✅ T4: D-014 Footer-Layout — alle Footer-Buttons in `#footer-bar` (position:fixed, flex, gap:8px); `#save-group` gruppiert Commit-Feld + 💾; print-media-Regeln bereinigt
- ✅ T5: D-015 Inventar — `item.anmerkung[:40]` Truncation entfernt; `overflow-wrap:break-word` auf Span; Begleitfix `| e` Escaping auf `item.anmerkung`, `v.anmerkung`, `n.anmerkung`
- ✅ T6: D-016 Profil — `s.konsequenz[:60]` Truncation + Ellipsis-Conditional entfernt; `| e` Escaping hinzugefügt; multi-line Darstellung via vorhandenes `.vn-list li small { display:block }`
- ✅ T7: Verifikation (86/86 Tests, Static-Render, 11 strukturelle Checks)

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
  - LeP/AsP/AuP-Stepper nun in einer horizontalen Flucht (D-013)
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
  - Würfel-Panel Text jetzt dunkel lesbar im Dark-Theme (D-012)
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher-Slots
- ⭐ Steigern-Tab: AP-Übersicht, Eigenschaften/Talente/Zauber steigerbar; Komplexitätsgrenze-Warnung
- 🗣️ Sprachen-Tab: Sprachen + Schriften mit Komplexität/TaW; Komplexitäts-Zahlen jetzt rechts ausgerichtet (D-017)
- 🎒 Inventar-Tab: Münzbeutel (Stepper), Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung
  - Anmerkungstext vollständig (kein [:40]-Clipping mehr), bricht um (D-015)
- 📋 Profil-Tab: Vor/Nachteile, Schlechte Eigenschaften, Kampagne-Übersicht, Steigerungs-Log, Vorgeschichte
  - Konsequenz-Text vollständig (kein [:60]-Clipping mehr), mehrzeilig (D-016)
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/`; `## Verlauf` editierbar + Persistenz
- ⬆️ Stufen-Aufstieg: GM-Grant-Button im Steigern-Tab
- 💾 Commit-Button: Commit-Feld + 💾 Sichern als sichtbare Gruppe im Footer, kein Überlapp mehr (D-014)
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 86/86 Testfälle bestanden (Sprint-009-Baseline unverändernd)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **Strukturelle Checks (11/11):**
  - D-012: `--bg-card`-Token + `color: var(--ink)` auf `.dice-panel` ✓
  - D-013: `flex-wrap: nowrap` auf `.vital-stepper` ✓
  - D-017: `text-align: right` auf `.l-kompl` ✓
  - D-014: `#footer-bar` + `#save-group` im Template ✓
  - D-015: kein `anmerkung[:40]`, `overflow-wrap:break-word` vorhanden ✓
  - D-016: kein `konsequenz[:60]`, `konsequenz | e` vorhanden ✓
  - T5-Quality: `anmerkung | e` vorhanden ✓

## Als nächstes (Sprint 010)

- **D-019** (Steigern: Experiment-/Auswahl-Modus, L) — größte UX-Verbesserung am Steigern-Tab; Warenkorb-Modell zeigt Gesamtkosten vor Bestätigung
- **D-020** (Steigern: Steigerungsspalte in eigene Tabelle, M) — baut idealerweise auf D-019 auf oder danach; Vorlagemuster: `lang-table`
- **D-021** (Steigern: Session-Erfahrungs-Kostenmodifikator, M) — Session-State in localStorage; unabhängig von D-019 aber thematisch verwandt
- **D-018** (Zauber: Inline-Vorschau, L) — neuer Flask-Endpoint + Modal/Panel; Klick-Guard in dice.js beachten

Empfehlung: D-019+D-020 zusammen (D-020 nach D-019, da gekoppelt), dann D-021 oder D-018 je nach Spielbedarf.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **`.dp-result`-Statusfarben** — `.dp-result.success/fail/crit/patzer` verwenden hartcodierte dunkle Hex-Farben (`#1a6b2a`, `#1a4a7a`, …) die auf dem neuen dunklen `#131c28` Panel-Hintergrund (D-012-Fix) schlecht lesbar sind; pre-existing, kein eigenes EPIC; Nachbesserung S-Effort
- **`s.name` / `v.name` / `n.name` ohne `| e`** — Vor-/Nachteil- und Schlechte-Eigenschaften-Namen fehlt HTML-Escaping; Risiko gering (stripMarkdown-geparste Quelle), aber Muster-Inkonsistenz nach T5/T6-Escaping-Fixes; S-Nachbesserung
- **`kampagne_slug` hardcoded** — `server.py:27`; zweite Kampagne bräuchte manuelle Anpassung
- **Guided Stufen-Aufstieg** (LE/AE/AU beim Level-Up anheben) — Out-of-Scope, kein EPIC
- **D-018/D-019/D-020/D-021** — größere Umbau-Sprints, bewusst auf später verschoben
