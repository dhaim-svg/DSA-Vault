# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

_(keine)_

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-018 | Zauber: Inline-Vorschau des Artikels (Obsidian-Link bleibt) | L | ready | Manual-Test 01.06.2026 |

### Beschreibungen

**D-024 — Stabzauber: allgemeine Aktivierungsregel anzeigen**
Stabzauber-Liste zeigt nur Name + Vol + Effekt (`parsers/held.py:351-362`, Template `dashboard.html.j2:1430-1432`). Die allgemeine Aktivierungsregel („Alle Stabzauber an Illaens gebundenen Magierstab geknüpft; Aktivierung = freie Aktion", `rituale.md` ~Z.16) wird nicht angezeigt. Gewünscht: diese allgemeine Regel prominent im Stabzauber-Abschnitt (Hinweiszeile unter dem Header `dashboard.html.j2:1428`). Keine Probe pro Einzelzauber. Umfang: Intro-Zeile aus `rituale.md` parsen (oder im Template ergänzen) + Render. Effort S.

**D-023 — Talente/Zauber: Eigenschaftswerte inline + prominenter**
Talent- und Zauberzeilen zeigen nur die Probe-Kürzel (z.B. `MU/GE/KK`), nicht die tatsächlichen Eigenschaftswerte des Helden. Gewünscht: Werte inline anzeigen (z.B. „MU 14 / GE 13 / KK 12") **und** die Probe-Anzeige etwas prominenter gestalten. Werte sind client-seitig über `window.DSA.eig` (`static/dice.js` `parseProbe`) bzw. server-seitig aus `held.eigenschaften` verfügbar. Umfang: Talent-Zeile (`dashboard.html.j2:1325-1335`, `.t-probe`) und Zauber-Zeile (`1359-1380`, `.probe`) um Werte ergänzen (server-seitig im Template oder kleine JS-Annotation beim Laden), CSS für Lesbarkeit/Prominenz. Kampftechniken (AT/PA) ausgenommen. Effort M.

**D-022 — Profil: Aussehen & Kleidung**
Profil-Tab zeigt keine Infos zu Aussehen/Kleidung. Heute existieren Daten nur verstreut (Haar/Augen in `vorgeschichte.md`, silberne Strähne als Stigma in `vor-nachteile.md`, Kleidungsstücke in `ausruestung.md`). Lösung: neue strukturierte Sektion (z.B. `## Aussehen` mit Tabelle/Feldern: Haarfarbe, Augenfarbe, Größe, Statur, besondere Merkmale, typische Kleidung) in einer Helden-Datei; `parsers/held.py` parst sie (analog bestehender Section-Split/`parse_md_table`-Loader) und liefert sie ins `held.meta`/eigenes Dict; neue Profil-Karte im Template (`dashboard.html.j2:1645-1757`). Umfang: Datenschema + Parser + Template. Effort M.

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
| D-024 | Stabzauber: allgemeine Aktivierungsregel als Hinweiszeile | S | 012 |
| D-023 | Talente/Zauber: Eigenschaftswerte inline + Probe prominenter | M | 012 |
| D-022 | Profil: Aussehen & Kleidung als strukturierte Sektion | M | 012 |
| D-021 | Steigern: Session-Erfahrungs-Modifikator (SKT-Spaltenverschiebung) | M | 011 |
| D-020 | Steigern: Steigerungsspalte in eigene Tabelle (steiger-table) | M | 010 |
| D-019 | Steigern: Experiment-/Auswahl-Modus (Warenkorb) | L | 010 |
| D-017 | Sprachen: Komplexitäts-Spalte ausrichten | S | 009 |
| D-016 | Profil: Schlechte Eigenschaften / Prinzipientreue ohne Truncation | S | 009 |
| D-015 | Inventar: Formatierung & abgeschnittener Text | S | 009 |
| D-014 | Footer-Layout: Session/Sichern-Überlappung + Commit-Feld gruppieren | S | 009 |
| D-013 | Vitalia-Stepper in einer Reihe | S | 009 |
| D-012 | Würfel-Panel Lesbarkeit (tab-übergreifend) | S | 009 |
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
