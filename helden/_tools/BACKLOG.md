# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

_(keine)_

## Backlog

_(keine — Dashboard-Backlog leer; offen im Vault-`backlog.md`: B-015/B-016/B-017/B-018)_

### Gestrichen

| EPIC | Title | Gestrichen am | Grund |
|------|-------|----------------|-------|
| D-033 | Quick-Capture in Footer-Bar | 19.09.2026 | Kein Live-Schreibpfad mehr (D-030-Fallback: Drive bleibt Quelle) |
| D-034 | Ereignis-Auto-Log | 19.09.2026 | Dito — hätte auf demselben Live-Schreibpfad wie D-033 aufgebaut |

Details siehe Beschreibung unten (D-033/D-034 wurden nicht einfach vergessen — bewusst gestrichen, s. D-030).

### Beschreibungen

**D-033 / D-034 — Quick-Capture & Ereignis-Auto-Log — *entfallen 19.09.2026***
Beide Live-Editing-Features setzten eine synchron beschreibbare Chronik-Datei im Vault voraus. Da Drive Quelle bleibt (D-030-Fallback, Junction-Ansatz gescheitert), gibt es keinen Live-Schreibpfad mehr, in den das Dashboard schreiben könnte, ohne beim nächsten Import überschrieben zu werden. Ersatzlos gestrichen — der User schreibt weiterhin direkt in Google Drive, keine Dashboard-Interaktion während des Spiels vorgesehen.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-050 | Artikelvorschau für Sonderfertigkeiten: 15 von 17 SF-Zeilen zeigen nur ihren `##`-Abschnitt (`load_wiki_artikel`, Anker → `split_sections`, Warnung bei fehlendem/leerem Abschnitt), `<details>`-Block als Makro `partials/_artikel.j2` geteilt mit Zauber, `WIKILINK_RE` erlaubt einzelnes `]` (Merkmalskenntnis-Anker); Browser-Fund: SF-Zeilenregeln trafen auch `li` im Artikeltext → `.sf-list > li` + Invariante (längster Artikel 7 841 → 808 px); Static-Render 450 → 481 KB, 40 Vorschauen | M | 021 |
| D-049 | Desktop-Footer über dem offenen Würfelpanel: `#footer-bar{bottom:calc(28px + var(--dice-panel-h,0px))}` (Panel z-index 200 verdeckte die Leiste, −277 px @ 1280 → Abstand 28 px); ≤ 480 px unberührt | S | 021 |
| D-048 | Zustands-Chips wirken nur noch über die Panel-Vorbelegung: `applyWundModsToProben` nutzt `attrMod` statt `probeMod` (kein Attribut-Overlay mehr auf 203 `[data-attr]`-Spans, Wund-Overlay bleibt), Legende präzisiert; Chip-Werte bleiben Hausregel (User-Entscheidung 19.09.2026) | S | 020 |
| D-047 | Touch-Ziele & Mobile-Restposten @ 400 px: Inventar-Eingaben/„+ Hinzufügen“ (30 px) und Zustands-Chips (25 px) → 44 px nur ≤ 480 px; offenes Würfelpanel reserviert per `--dice-panel-h` (`dice.js` + `body`-Padding, Lücke Footer↔Panel +15,8 px); Steigern-Scroll-Hinweis/`tabindex` nur bei echtem Überlauf (`ResizeObserver`); Druck-Selektor `.spell .zfw-num` gescopt | S | 020 |
| D-045 | Chronik-Druck: nur die aktive Ansicht (Roh/Kompiliert/Register) wird gedruckt, Register-Sonderregel entfällt; aktiver Register-Filter als Druck-Kopfzeile „Gefiltert nach: „…“ — n/N Einträge“ (`textContent`); mit Print-Emulation im Browser gemessen | S | 020 |
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
