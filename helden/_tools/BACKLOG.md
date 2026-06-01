# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-012 | Würfel-Panel Lesbarkeit (tab-übergreifend) | S | in-progress | Manual-Test 01.06.2026 |
| D-013 | Vitalia-Stepper in einer Reihe | S | in-progress | Manual-Test 01.06.2026 |
| D-014 | Footer-Layout: Session/Sichern-Überlappung + Commit-Feld gruppieren | S | in-progress | Manual-Test 01.06.2026 |
| D-015 | Inventar: Formatierung & abgeschnittener Text | S | in-progress | Manual-Test 01.06.2026 |
| D-016 | Profil: Schlechte Eigenschaften / Prinzipientreue ohne Truncation | S | in-progress | Manual-Test 01.06.2026 |
| D-017 | Sprachen: Komplexitäts-Spalte ausrichten | S | in-progress | Manual-Test 01.06.2026 |

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-018 | Zauber: Inline-Vorschau des Artikels (Obsidian-Link bleibt) | L | ready | Manual-Test 01.06.2026 |
| D-019 | Steigern: Experiment-/Auswahl-Modus mit Gesamtkosten vor Bestätigung | L | ready | Manual-Test 01.06.2026 |
| D-020 | Steigern: Steigerungsspalte in eigene Tabelle | M | ready | Manual-Test 01.06.2026 |
| D-021 | Steigern: Session-Erfahrungs-Kostenmodifikator | M | ready | Manual-Test 01.06.2026 |

### Beschreibungen

**D-012 — Würfel-Panel Lesbarkeit**
Betrifft alle Tabs (Kampf, Talente, …). `.dice-panel` (`templates/dashboard.html.j2:834`) nutzt hellen Fallback-Hintergrund (`--card-bg` undefiniert → `#f5ebd8`) ohne eigenes `color` → Text erbt das helle `--ink` des Dark-Themes → hell-auf-hell unlesbar. Fix: dunkles `color` auf `.dice-panel` + Kinder; oder Panel an `:root`-Dark-Tokens angleichen. Style-Block 833–957.

**D-013 — Vitalia-Stepper in einer Reihe**
LEP/ASP/AuP −/+ Stepper sehen komisch aus. Markup `.vital`/`.vital-stepper` (`dashboard.html.j2:1161-1215`). Fix: Stepper-Elemente (−, Wert, /, Max, +) horizontal in einer Flucht ausrichten.

**D-014 — Footer-Layout: Überlappung + Commit-Feld-Gruppierung**
Unten rechts überlagern sich „Session zurücksetzen" und „Sichern". Das Commit-Feld (`#commit-msg`) gehört zu Sichern (schickt Git-Commit-Message via `static/commit.js` → `POST /api/commit`) — visuell unklar. Markup `dashboard.html.j2:1860-1862`. Fix: Flex/Gap statt Inline-Styles; Commit-Feld + 💾 Sichern als sichtbare Gruppe, getrennt von „Session zurücksetzen".

**D-015 — Inventar: Formatierung & Text-Clipping**
Text teils abgeschnitten (z. B. „Reiseproviant"). Ursachen: (1) feste Grid-Spalten ohne Umbruch (`#inventar-list li` `dashboard.html.j2:1042`, `.inv-*` 1028-1041); (2) harte Kürzung der Anmerkung auf 40 Zeichen `item.anmerkung[:40]` (Reiseausrüstung, Zeile 1603). Fix: Umbruch erlauben, Hart-Truncation entfernen.

**D-016 — Profil: Schlechte Eigenschaften / Prinzipientreue**
Konsequenz-Text auf 60 Zeichen gekürzt (`dashboard.html.j2:1646` `s.konsequenz[:60]`); Prinzipientreue rendert data-getrieben in der Vorteils-/Nachteilsliste. Fix: Truncation entfernen, mehrzeilige Darstellung (`.vn-grp.bad` Grid 1640-1652).

**D-017 — Sprachen: Komplexitäts-Spalte**
Beide Tabellen (Sprachen + Schriften) haben die mittlere Komplexitäts-Spalte (`.l-kompl`, mono) linksbündig, TaW rechtsbündig → Zahlen stehen nicht in einer Flucht. Fix: `text-align: right` / `text-align: center` auf `.l-kompl` (`dashboard.html.j2:1059-1067`).

**D-018 — Zauber: Inline-Vorschau**
Klick auf Link öffnet Obsidian (gut). Gewünscht: kleine Ansicht im Dashboard, die den Artikel direkt anzeigt; `↗`-Obsidian-Link bleibt. Heute: nur `obsidian://`-URI via `rendering.py:obsidian_uri()`; kein Read-Endpoint. Umfang: neuer Flask-Endpoint liest Zauber-`.md` + rendert HTML; Inline-Panel/Modal im Zauber-Tab (`dashboard.html.j2:1311-1506`); Klick-Guard in `static/dice.js:520-532` beachten.

**D-019 — Steigern: Experiment-/Auswahl-Modus**
Statt pro Zeile sofort zu steigern: erst Auswahl treffen, Gesamtkosten gegen AP-Vorrat sehen, dann gesammelt bestätigen. Heute: jede Zeile committet sofort (`steigern.js:doSteigern:52` → 4× PATCH + reload). Umfang: Auswahl-/Warenkorb-Modell in `steigern.js` gegen `window.DSA.steigern.ap.verfuegbar`, laufende AP-Summe, finaler Commit-Button.

**D-020 — Steigern: Steigerungsspalte in eigene Tabelle**
Steigerungsspalte separieren. Heute Flex-Zeilen (`steigern.js:renderRow:119`, CSS `.sg-row:1005`). Vorlage: `<table class="lang-table">` (Sprachen-Tab 1799-1850). Hinweis: überlappt mit D-019; idealerweise zusammen oder nach D-019 umsetzen.

**D-021 — Steigern: Session-Erfahrungs-Kostenmodifikator**
Besondere/schlechte Erfahrung in einer Session senkt/erhöht Steigerungskosten einer Spalte einmalig. Heute nicht vorhanden (Kosten rein `calcApCost`/`calcEigCost` in `steigern.js`). Umfang: Session-State analog `static/session.js` (localStorage `dsa:<slug>:session`), UI-Steuerung per Tab, Anwendung in `calcApCost`/`renderRow`.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-011 | showIndicator-Dedup | S | 008 |
| D-010 | Commit-Message-Input | S | 008 |
| D-009 | Stufen-Aufstieg | M | 007 |
| D-008 | Sprachen mit Komplexitäts-Grenze | S | 007 |
| D-007 | Session-Commit-Button | S | 006 |
| D-006 | Session-Notizen → Journal | M | 006 |
| D-005 | Zauberspeicher im Stab | M | 005 |
| D-004 | Inventar / Geld / Verbrauch | M | 004 |
| D-003 | Tab-Navigation + AP & Steigerung | L | 003 |
| D-001 | Flask-Server + Vitalia Write-back + Wunden + Zustände | L | 001 |
| D-002 | Würfelintegration (3W20 Proben, Schaden, Panel) | L | 002 |
