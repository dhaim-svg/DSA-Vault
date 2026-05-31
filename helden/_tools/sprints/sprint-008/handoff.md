# Sprint 008 Handoff — Commit-Message-Input (D-010) + showIndicator-Dedup (D-011)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-010+D-011 → in-progress, plan.md anlegen)
- ✅ T1: D-010 Commit-Message-Input — `#commit-msg`-Eingabefeld neben 💾-Button; Kette: commit.js → POST JSON → server.py → git_ops.py(`message=None`); Format `dashboard: {slug} — {message}`; 2 neue Tests
- ✅ T2: D-011 showIndicator-Dedup — `static/util.js` mit `window.dsaShowIndicator`; Duplikate aus app.js + commit.js entfernt; clearTimeout-Bug in commit.js mit behoben; Load-Order-Kommentar im Template
- ✅ T3: Verifikation (86/86 Tests, Static-Render sauber, HTML-Checks bestanden)

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher-Slots (Befüllen/Entleeren)
- ⭐ Steigern-Tab: AP-Übersicht, Eigenschaften/Talente/Zauber steigerbar; ⚠ Komplexitätsgrenze-Warnung für Sprachen
- 🗣️ Sprachen-Tab: Sprachen + Schriften mit Komplexität/TaW; Warn-Badge wenn TaW ≥ Komplexität
- 🎒 Inventar-Tab: Münzbeutel (Stepper), Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung
- 📋 Profil-Tab: Vor/Nachteile, Kampagne-Übersicht, Steigerungs-Log, Vorgeschichte
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/` anzeigen; `## Verlauf` editierbar + Persistenz
- ⬆️ Stufen-Aufstieg: GM-Grant-Button im Steigern-Tab; schreibt `stufe`, AP-Anzeige-Tabelle und Protokoll-Log
- 💾 **Commit-Button (verbessert):** optionales Freitext-Eingabefeld für Commit-Message; Custom-Format `dashboard: {slug} — {message}`; leeres Feld → Auto-Timestamp wie zuvor
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 86/86 Testfälle bestanden (84 Sprint-007-Baseline + 2 neue git_ops-Tests)
  - +2 `test_git_ops.py` (custom message mit Em-Dash-Format; auto-message bei leerem/None input)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **Commit-Message-Input:** `#commit-msg`-Input im HTML vorhanden, neben `#commit-btn`, in `.screen-only` (print-hidden) ✓
- **util.js Load-Order:** `<!-- util.js must remain first …>`-Kommentar + `<script src="/static/util.js">` vor app.js ✓
- **showIndicator dedup:** keine `function showIndicator`-Definition mehr in app.js oder commit.js ✓
- **clearTimeout-Fix:** util.js verwendet clearTimeout; alter commit.js-Bug behoben ✓

## Als nächstes (Sprint 9)

- **Neues Feature nach Bedarf** — Backlog ist leer; User kann neue EPICs einpflegen.
- **Technische Kandidaten aus Code-Review-Beobachtungen (kein eigenes EPIC, eher Hinweis):**
  - `kampagne_slug` enthardcoden (`server.py:27`) — braucht Held→Kampagne-Mapping, Effort M; relevant sobald eine zweite Kampagne entsteht
  - Guided Stufen-Aufstieg (LE/AE/AU beim Level-Up anheben) — Effort M–L, braucht Design

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **`kampagne_slug` hardcoded als `"drachenchronik"`** — `server.py:27`; zweite Kampagne bräuchte manuelle Anpassung
- **Harte Komplexitätsgrenze-Sperre** — User wählte warn-only; Steigern über Grenze bleibt möglich
- **Guided Stufen-Aufstieg** (LE/AE/AU anheben) — Stufe ist reines Label; geführter Aufstieg Out-of-Scope
- **`showIndicator` in journal.js** — journal.js nutzt eigenes `okSpan/errorSpan`-Muster; bewusst nicht in util.js migriert (anderes UX-Pattern)
- **`window.dsaShowIndicator`-Alias in app.js/commit.js** — wird bei Script-Parse-Zeit aufgelöst; funktioniert korrekt mit synchronen `<script>`-Tags; würde brechen wenn util.js per `async`/`defer` geladen würde (kein Plan dafür)
