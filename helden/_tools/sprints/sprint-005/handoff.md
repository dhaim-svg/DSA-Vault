# Sprint 5 Handoff — D-005 Zauberspeicher im Stab

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-005 → in-progress, sprints/sprint-005/plan.md)
- ✅ T1: Writer — neuer `table_row`-Locator in `held_writer.py` + `_locate_row` Helper-Refactor + 6 Tests
- ✅ T2: Template UI — interaktive Befüllen/Entleeren-Controls im Zauber-Tab (5 Spalten, CSS, `window.DSA.zauberspeicher`)
- ✅ T3: `static/zauberspeicher.js` — Befüllen-Form (validate + PATCH) + Entleeren-Button + IIFE-Wrap
- ✅ T4: Verifikation (63/63 Tests, Static-Render sauber, BACKLOG D-005 → Done, CLAUDE.md Sprint → 5)

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten
  - **NEU:** Zauberspeicher-Slots interaktiv (Befüllen via Form, Entleeren via Button, belegt-Anzeige)
- ⭐ Steigern-Tab: AP-Übersicht, Eigenschaften/Talente/Zauber steigerbar
- 🎒 Inventar-Tab: Münzbeutel (Stepper), Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung
- 📋 Profil-Tab: Vor/Nachteile, Vorgeschichte
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 63/63 Testfälle bestanden (57 bestehend + 6 neue `table_row`-Tests)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0)
- **Zauberspeicher-Slots:** `data-slot`-Attribute auf allen 3 Slots vorhanden ✓
- **window.DSA.zauberspeicher:** 3-Slot-JSON korrekt serialisiert ✓
- **Script-Include:** `zauberspeicher.js` im Template vorhanden ✓

## Als nächstes (Sprint 6)

- **D-006**: Session-Notizen → Journal — Notizen aus Abenteuer-Dateien im Dashboard anzeigen/bearbeiten
- **D-007**: Session-Commit-Button — schnelles Committen von Dashboard-Änderungen direkt im Browser (S, gut für einen kurzen Sprint zusammen mit D-006)
- Alternativ: **D-009** (Stufen-Aufstieg, M) falls ein fokussierter Character-Progression-Sprint gewünscht ist

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **`(9 Rituale)`-Heading ist ein Literal** in `SECTION_PATH` (`zauberspeicher.js:36`) — Kommentar vorhanden; bei Ritual-Ergänzungen ist der JS-Pfad manuell zu aktualisieren
- **AsP-Obergrenze (20) wird nicht erzwungen** — Befüllen-Form hat `max=20` HTML-Attribut, aber kein JS-Check; ein Benutzer könnte > 20 AsP eintragen (play-time ignorierbar)
- **`— AsP` auf leeren Slots** leicht unintuitiv (Anzeige `— AsP` statt nur `—`) — kosmetisch, kein Daten-Bug
- **Keine etag-Konflikt-Prüfung** im JS (konsistent mit `inventar.js` — projektweit so)
- **Kapazitäts-Enforcement** (Summe aller Slots ≤ 20 AsP) bewusst out-of-scope
