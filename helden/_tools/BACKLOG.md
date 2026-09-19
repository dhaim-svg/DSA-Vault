# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

| EPIC | Title | Effort | State | Sprint |
|------|-------|--------|-------|--------|
| D-045 | Chronik-Druck: Ansichten-Konsistenz + Register-Filter im Druck — **Entscheidung 19.09.2026: nur aktive Ansicht drucken, aktiver Filter als Druck-Kopfzeile benannt** | S | in-progress | 020 |
| D-047 | Touch-Ziele & Mobile-Restposten bei 400 px: Inventar-Eingaben/„+ Hinzufügen" 30 px, Zustands-Chips 25 px, `.codex`-Padding bei offenem Würfelpanel, Scroll-Hinweis nur bei Überlauf | S | in-progress | 020 |
| D-048 | Zustands-Chips: Overlay und Panel-Vorbelegung vereinheitlichen — **Entscheidung 19.09.2026: nur Panel-Vorbelegung (Overlay für Chips entfällt), Chip-Werte bleiben Hausregel** | S | in-progress | 020 |

## Backlog

_(keine — Dashboard-Backlog leer; offen bleibt B-013 im Vault-`backlog.md`)_

### Gestrichen

| EPIC | Title | Gestrichen am | Grund |
|------|-------|----------------|-------|
| D-033 | Quick-Capture in Footer-Bar | 19.09.2026 | Kein Live-Schreibpfad mehr (D-030-Fallback: Drive bleibt Quelle) |
| D-034 | Ereignis-Auto-Log | 19.09.2026 | Dito — hätte auf demselben Live-Schreibpfad wie D-033 aufgebaut |

Details siehe Beschreibung unten (D-033/D-034 wurden nicht einfach vergessen — bewusst gestrichen, s. D-030).

### Beschreibungen

**D-033 / D-034 — Quick-Capture & Ereignis-Auto-Log — *entfallen 19.09.2026***
Beide Live-Editing-Features setzten eine synchron beschreibbare Chronik-Datei im Vault voraus. Da Drive Quelle bleibt (D-030-Fallback, Junction-Ansatz gescheitert), gibt es keinen Live-Schreibpfad mehr, in den das Dashboard schreiben könnte, ohne beim nächsten Import überschrieben zu werden. Ersatzlos gestrichen — der User schreibt weiterhin direkt in Google Drive, keine Dashboard-Interaktion während des Spiels vorgesehen.

**D-045 — Chronik-Druck**
Der Print-Block in `static/chronik.css` druckt Roh und Kompiliert immer (`.chronik-view{display:block !important}`), das Register nur wenn es aktiv ist. Ein aktiver Register-Filter bleibt im Druck bestehen (`entry.hidden`), während Suchfeld und Umschalter ausgeblendet sind — der Ausdruck zeigt still eine Teilmenge. Zu klären: nur die aktive Ansicht drucken oder alle drei; Filter bei `beforeprint` zurücksetzen (analog zum `<details>`-Handling in `chronik.js`).

**D-047 — Touch-Ziele & Mobile-Restposten bei 400 px**
Beim Browser-Check zu D-044 (Sprint 019) gemessen, aber nicht Teil von D-044: (1) Inventar-Formular `.inv-add-input--name` / `--anzahl` und „+ Hinzufügen" je **30 px** hoch (< 44 px); (2) Zustands-Chips `.zustand-chip` **25 px** hoch; (3) `.codex{padding-bottom:36px}` (≤ 480 px, seit D-044 statischer Footer): das fixe Würfelpanel (`.dice-panel`, `position:fixed; bottom:0`, ≈ 150 px) kann bei geöffnetem Panel die letzten Inhaltszeilen verdecken — bei 400 px mit offenem Panel ungemessen (vorher 120 px Reserve); (4) Steigern: der Scroll-Hinweis `.sg-scroll-hint` erscheint ≤ 600 px auch, wenn die Tabelle passt, und je Abschnitt einmal; jede Tabelle bringt einen zusätzlichen Tab-Stop — Hinweis/`tabindex` nur bei echtem Überlauf (`scrollWidth > clientWidth`); (5) `.zfw-num` im Print-Block ist unscoped (`.spell .zfw-num` wäre konsistent zu den Geschwister-Selektoren, dann `PRINT_SPELL_SELECTORS` in `test_rendering.py` anpassen). Messmethode wie D-040/D-044: Rect-Vergleich bei verifiziertem `innerWidth === 400`, Static-Render über `http.server` (nur lesend).

**D-048 — Zustands-Chips: doppelte Darstellung + Regelbasis**
Aus der Gesamt-Review zu D-041 (Sprint 019), vorbestehend: Bei aktivem Chip zeigt das Overlay **alle** `[data-attr]`-Werte reduziert (`MU 12→10`, 203 Spans) **und** das Würfelpanel füllt `dp-mod` mit dem Chip-Wert vor — gewürfelt wird korrekt, wer von Hand würfelt, kann den Chip aber doppelt anrechnen. Zu entscheiden (User): nur eine Darstellung (Overlay **oder** Panel) bzw. Overlay klar als „Hausregel-Erschwernis" kennzeichnen; außerdem, ob die frei erfundenen Chip-Werte (Schmerz −2, Furcht −2, Betäubt −4, Verwirrt −2, Erschöpft −2) durch die belegten Mechaniken ersetzt werden sollen — optionale LE-Probenmali (WdS S. 57: < ½ +1/+3, < ⅓ +2/+6, < ¼ +3/+9), optionale AU-Mali (WdS S. 83), optionale Schmerz-Probe (WdS S. 82), Ängste als Schlechte Eigenschaft (WdH S. 268). Regelbasis: `wiki/dsa-4.1/grundregeln/zustaende.md`, `wiki-luecken.md` L23.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-046 | Zauberliste: Druck-Kontrast (Name-Link, ZfW, ZD, Kosten, Wirkung, Submeta, Kopfzeile, Modifikations-Details) 1,1:1 → 14,62:1 gemessen; Grid-Minima gesenkt (Summe 978 → 878 px), Überstand 0 px bei 1071/1100/1130/1280; toter `.merk`-Selektor entfernt | S | 019 |
| D-044 | Mobile/Touch: Banner ≤ 600 px einspaltig (Titel `clamp`), Footer ≤ 480 px statisch + 44 px, Steigern-Scrollbereich als `div.steiger-scroll` (fokussierbar, `role=region`, Scroll-Hinweis), Inventar-Modifier-Klassen, Artikel-Summary 44 px im Kompaktlayout | S | 019 |
| D-041 | Wund-/Zustände-Audit: Wund-Malus regelkonform (WdS S. 57: AT/PA/FK/INI/GE −2, GS −1 je Wunde; TP/Talent/Zauber unberührt) über neue `static/wundregeln.js` + `DSASession.{probeMod,statMod,attrMod}`, GE-Abzug pro Attribut auch in Talent-/Zauberproben, Basiswert-Overlay im Kampf-Tab; Zustands-Chips als Hausregel gekennzeichnet + Legende; Wiki-Artikel `grundregeln/zustaende.md`, `wiki-luecken.md` L23; erste JS-Verhaltenstests (`test_wundregeln.py`, node) | M | 019 |
| D-043 | Zauber: ZfW-Sortierung im Kompaktlayout erreichbar — Toolbar-Button (Standard → ZfW ↓ → ↑, Tastatur/ARIA, ≥ 44 px), `static/zauber-sort.js` statt Inline-Skript, Zeilen-Wrapper `[data-spell-list]` (Legende bleibt hinter der Liste) | S | 018 |
| D-018 | Zauber: Artikelvorschau als `<details>` in der Zauberzeile — 25 Artikel zur Render-Zeit eingebettet (`parsers/wikiartikel.py`, mistune `escape=True`, Wikilinks → `obsidian://`), Fallback-Parser für 103/268 Artikel mit ungültigem Frontmatter-YAML; Static-Render 379 → 434 KB | L | 018 |
| D-042 | Chronik-Parser erkennt `Datum: 13. Phex -> Start` als IG-Datum (`13. Phex (Start)`), 5 Tests | S | 017 |
| D-040 | Mobile 400 px: Überlauf in Zauber/Steigern/Inventar/Profil beseitigt — alle 8 Tabs ≤ 400 px, Zauber-Kompaktlayout ≤ 1070 px, Footer-Leiste umbricht | S | 017 |
| D-036 | NSC-/Orts-Register: `parsers/register.py`, 3. Ansicht „Register" im Chronik-Tab (55 Einträge), clientseitige Suche, zur Render-Zeit generiert | M | 017 |
| D-039 | Static-Render interaktiv: JS wird eingebettet (`JS_FILES`/`js_files()`/`inline_js`), Hinweis-Banner `#static-hinweis`, README — Tabs/Würfel unter `file://` | S | 016 |
| D-038 | Bug: `session.js` lief nie (`IS_SERVED`-Kollision) → IIFE + Top-Level-Kollisionstest, Browser-Gegenprüfung 9/9 | S | 016 |
| D-035 | `/session-compile`-Kommando + 4 Spielabende kompiliert (Session 1–4), Platzhalter-Session entfernt | M | 016 |
| D-037 | dashboard.html.j2 in Partials + eigenes CSS zerlegen (CSS → static/*.css, zur Render-Zeit eingebettet; 8 Tab-Partials; geteilter Render-Kontext) | L | 015 |
| D-032 | Chronik-Tab (📜, Roh/Kompiliert-Umschalter, read-only Roh-Ansicht, /chronik-bild-Route, Parser-Fix Bild+Text) | M | 015 |
| D-031 | parsers/chronik.py (Spielabend/IG-Tag/Szenen-Parser, verifiziert gegen echte Chronik) | M | 014 |
| D-030 | Chronik-Import-Skript (Drive → Vault, einseitig — Junction-Ansatz verworfen, s. Sprint-014-Handoff) | S | 014 |
| D-029 | Aussehen vervollständigen (Gewicht-Feld, offene Felder visuell markiert, Portrait-Plumbing) | S | 013 |
| D-028 | Erschaffungsprobe + AsP je Stabzauber (Nachschlage-Info) | S | 013 |
| D-027 | Zauberspeicher-Auslöseprobe (MU/IN/KL, würfelbar, +1 Erschwernis/Slot) | M | 013 |
| D-026 | Inline-Eigenschaftswerte vervollständigen (Kampftechniken, Wundabzug; `.mod-probe` bewusst ausgenommen — Modifikator-Formeln, keine Attribut-Proben) | M | 013 |
| D-025 | Eigenschafts-Leiste über Talente-/Zauber-Tab (sticky, mit Wund-/Zustandsbadge) | M | 013 |
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
