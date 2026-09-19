# Sprint 017 Handoff — Chronik-Block: NSC-/Orts-Register, Parser-Datum, Mobile-Überlauf

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-036/D-040/D-042 → in-progress, plan.md) — `9dc5600`
- ✅ T1 (**D-042**): `parsers/chronik.py` erkennt die unfette Zeile `Datum: 13. Phex -> Start` als IG-Datum (`DATUM_PREFIX_RE`, Zusatz wird `13. Phex (Start)`); 5 neue Tests, gegen die echte Chronik bestätigt (04.06.-Abend: `13. Phex (Start)`, `17. Phex`, `18. Phex`) — `9b33b36`
- ✅ T2 (**D-036a**): `parsers/register.py::build_register()` — reine Funktion über die von `load_kampagne()` geparsten Sessions (`sektionen['Neue NSCs / Orte']`), dedupliziert NSCs/Orte über alle Sessions, balancierter Klammer-Scan für `(?)`-Marker und Qualifier (auch verschachtelt), gemeinsame `fold()` für Sortierung und Suchfeld; `build_context()['register']` als eigener Top-Level-Key; 26 neue Tests — `414cb53`
- ✅ T3 (**D-036b**): dritte Ansicht „Register" im Chronik-Tab (`partials/register.j2`, `static/register.js` in IIFE, Styles in `chronik.css`), rein clientseitige Suche (Static-Render hat kein Backend); Test-Helper `kompiliert_view()` vorab gegen das Durchsickern der neuen View abgesichert — `c278f8f`, `ea6c873`, Review-Minors `cdb7c2f`
- ✅ T4 (**D-040**): Mobile 400 px — alle 8 Tabs ohne horizontalen Überlauf (Zauber 1019→385, Steigern 442→385, Inventar 485→385, Profil 450→385; 385 = 400 minus 15 px Scrollbar) — `47f755b`; Zauber-Breakpoint nach Browser-Nachmessung 1040→1070 px — `0695750`
- ✅ T5: Verifikation (Tests, Browser-Check im served-Modus, Domänen-Grenze) + Gesamt-Review (Opus: Ready to merge, 0 Critical/Important); Static-Render neu — `301bdf4`; `plan.md` Stand — `e3b94dd`
- Commits liegen **lokal** auf `master`, **nichts gepusht** (`origin/master` steht bei `0351829`).

## Was funktioniert

- **Chronik-Tab, Ansicht „Register"** (neu): 55 Einträge (24 NSCs + 31 Orte) aus den vier Sessions, je Eintrag Name, `(?)`-Badge bei unsicherer Lesart, Qualifier, Session-Chips `S1…S4`, Erwähnungsliste. Suche: mehrere Wörter UND-verknüpft, Umlaut-/Akzent-tolerant (`verschworer` findet `Verschwörer`), Zähler `N Treffer` / `sichtbar/gesamt`, `Escape` leert. Ansicht überlebt Reload (`sessionStorage`). Register entsteht bei jedem Render aus den Session-Dateien — **keine** Dateien in `abenteuer/`.
- **Chronik-Tab, Roh-Ansicht:** der 04.06.-Abend zeigt jetzt drei IG-Tage mit Datum (`3 IG-Tage · 13. Phex (Start) – 18. Phex`) statt eines datumlosen ersten Tags.
- **Mobile 400 px:** alle 8 Tabs ohne Seiten-Scroll. Zauber: unterhalb von 1070 px Kompaktlayout (Name volle Breite, Probe/ZfW/ZD/Kosten als umbrechende Zeile, Wirkung volle Breite; leere Zellen ausgeblendet; Spaltenkopf ausgeblendet); `.mod-table` reflowt ≤ 600 px; Steigern-Tabelle scrollt ≤ 600 px seitlich im Container; Profil-Kopf (`.c-head`) und Footer-Leiste umbrechen ≤ 480 px (Leiste bleibt `position: fixed`).
- Alle Features aus Sprint 013–016 unverändert (Eigenschafts-Leiste, Inline-Werte, Zauberspeicher, Aussehen, Würfel, Steigern, Inventar, Sprachen, Zustände/Wunden, Chronik Roh/Kompiliert, Static-Render mit eingebettetem JS).
- Desktop-Layout (≥ 1071 px) unverändert: alle neuen Regeln liegen in `@media screen`-Queries (einzige Ausnahme `.inv-add-input{min-width:0}`, auf Desktop wirkungslos, weil `flex:1` weiter wächst).

## Verifikation

- **Test Suite:** 243/243 bestanden, auch mit `-W error` (Baseline 196 → +47: T1 +5, T2 +26, T3 +14, T4 +1, Nacharbeit +1).
- **Static Render:** `output/illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0), identisch zum committeten Stand; 1× `chronik-view-register`, 55 Register-Einträge, 0 `<script src>`, 1 Hinweis-Banner.
- **Browser (served, Playwright, `innerWidth === 400` verifiziert):** 8/8 Tabs `scrollWidth == clientWidth`; Chronik in allen drei Ansichten, die drei Umschalt-Buttons liegen vollständig im `.chronik-switch`; Register-Suche (`Richesa`, `bolongaro richesa`, `punin`, `xyzzy`, `Escape`, Umlaut-Faltung), `[hidden]`-Override, Reload merkt die Ansicht; Konsole nur `favicon.ico 404`.
- **Zauber-Breakpoint** bei 1041/1050/1061/1062/1069/1070/1071/1100/1280 px gemessen: nichts ragt aus der Karte, kein Seiten-Überlauf; engster Punkt 1071 px mit 9 px Reserve. (Erste Fassung mit 1040 px fiel hier durch: Grid ragte 1041–1061 px bis 21 px aus der Karte — `scrollWidth` sieht das nicht, nur ein Rect-Vergleich.)
- **Domänen-Grenze:** `git diff --name-only bdc53dc..HEAD` berührt nur `helden/_tools/` und `output/`; nichts unter `abenteuer/`.
- **Print** (Emulation): Roh + Kompiliert drucken immer, Register nur wenn aktiv; Suchfeld und Umschalter sind im Druck ausgeblendet (→ D-045).

## Als nächstes (Sprint 018)

- **D-018** (Zauber-Inline-Vorschau, L) — steht seit Sprint 016 unverändert an der Backlog-Spitze und wurde in Sprint 017 bewusst zurückgestellt; füllt einen Sprint allein. Beim Anfassen von `zauber.j2`/Zauber-CSS D-043 mitdenken.
- **D-041** (Wundregel-/Zustände-Audit, M) — Regelarbeit gegen DSA 4.1; `session.js:29` trägt seit Mai 2026 ein offenes TODO, der Code läuft seit D-038 im Browser, die Werte sind nie geprüft.
- **D-043** (Zauber-ZfW-Sortierung im Kompaktlayout, S) — die Sortierung hängt an der Kopfzeile, die ≤ 1070 px ausgeblendet ist; betrifft jetzt auch kleine Laptop-Fenster. Passt fachlich zu D-018 (gleicher Tab).
- **D-044** (Mobile/Touch-Feinschliff, S) — Banner-Titel bei 400 px abgeschnitten, Footer-Leisten-Buttons ~33 px hoch, Steigern-Scroll-Container ohne `tabindex`.
- **D-045** (Chronik-Druck, S) — Ansichten-Konsistenz und Register-Filter im Druck.
- (Reihenfolge = Empfehlung, nicht Pflicht; BACKLOG.md-Reihenfolge ist die Priorität.)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Zauber-Breakpoint 1070 px ist gemessen, nicht berechnet:** er ergibt sich aus 1019 px Grid-Bedarf + ~43 px Seitenrand rechts der Karte (Karte hat `overflow: visible`, ein Überlauf ist für `scrollWidth` unsichtbar). Ändern sich Karten-/Seiten-Padding oder die Grid-Spalten in `base.css`, neu messen (Rect des Zeilen-Kindes gegen Rect der Karte, nicht `scrollWidth`); 1071 px ist der engste Punkt.
- **Profil-Überlauf hatte eine andere Ursache als im Backlog vermutet** (Kampagnen-Status-Text in `.c-head`, nicht die Tabelle), Zauber hatte zusätzlich `.mod-table` — die Backlog-Beschreibungen sind bei Überlauf-Tickets nur Startpunkt, vorab messen.
- **Register hängt am Session-Format:** Sektion `## Neue NSCs / Orte` mit `### NSCs` / `### Orte` und Zeilen `- **Name** — Beschreibung` (Überschriften normalisiert, Trennzeichen `—`/`–`/`-` tolerant). Zeilen in anderer Form (Fließtext, eingerückte Unter-Bullets) tauchen im Register **nicht** auf, ohne Warnung. Nach dem nächsten `/session-compile` Zähler im Register-Button gegen die Session-Dateien gegenprüfen. Namen sind nicht mit dem Wiki verlinkt (bewusst ausgeklammert).
- **Register-Filter bleibt im Druck** (Suchfeld ausgeblendet → stille Teilmenge) — D-045.
- **Zauber-Kompaktlayout:** ZfW-Sortierung unerreichbar (D-043); im Kompaktlayout gibt es keine Spaltenköpfe, ZfW/ZD sind per Label-Präfix beschriftet.
- **Chronik-Parser-Kleinigkeiten (alle ohne Fehlerbild in den echten Daten):** `Datum: 1. Namenloser Tag` matcht nicht (Asymmetrie zum Fett-Zweig), der `Datum:`-Zusatz läuft nicht durch `strip_wikilink`, `Datum: 13. Phex ->` (leerer Zusatz) fällt in den Text-Fallback. `build_register` stürzt bei Nicht-String-`sektionen` ab (`load_kampagne` liefert ausschließlich Strings) und legt bei einem Namen nur aus Leerzeichen einen leeren Eintrag an; `build_context` nutzt `kampagne.get('sessions', [])`, weil ein bestehender Test `load_kampagne` mit `{}` stubbt.
- **Teststrategie:** Register-/Chronik-Tab-Tests laufen mit synthetischen Fixtures, nur `test_rendering.py` koppelt (wie bisher) an den Live-Vault (`illaen-baernhold`, mindestens 1 NSC und 1 Ort). Es gibt weiterhin keine JS-Testinfrastruktur: `register.js` wurde per `node --check`, Python/JS-`fold`-Paritätscheck und Browser-Check geprüft, nicht per Test. Die JS-Faltung deckt nur U+0300–U+036F ab (Python: alle kombinierenden Zeichen) — für deutsche DSA-Daten ohne Unterschied.
- **Mobile Einzelheiten:** Footer-Leiste verdeckt ~82 px Viewport; die „auswählen"-Spalte der Steigern-Tabelle ist ≤ 600 px erst nach seitlichem Scrollen sichtbar; `.inv-add-input:first-child` hängt an der DOM-Reihenfolge — D-044.
- **`.playwright-mcp/`** entsteht bei Playwright-Läufen im Vault-Root (untracked; der Verifikations-Agent hat es jeweils gelöscht) — ggf. `.gitignore`-Zeile; ebenso bleibt `.claude/settings.json` untracked (Playwright-Plugin), User entscheidet. Playwright-MCP blockt `file:` — nur der served-Modus ist im Browser prüfbar.
- **Aus Sprint 016 unverändert offen:** `Verlauf`-Speichern in der Kompiliert-Ansicht nie im Browser angeklickt (schreibt in `abenteuer/`); inhaltliche Sichtung der vier Sessions durch den User steht aus (47 `(?)`-Stellen, deren Einträge im Register mit `(?)`-Badge erscheinen, wenn direkt hinter dem Namen); Kommando-Mängel #5/#6/#8/#9/#11/#12 von `/session-compile`; Static-Render-Schreibaktionen liefern unter `file:` Fake-Erfolg, `session.js` ist dort inert; Scanner-Grenzen von `test_static_js.py`; `.journal-readonly`-Kontrast ~3,3:1; Chronik-Meta-Sektionen ohne Markdown-Rendering, `chronik_import.py` ohne Schutz gegen leeren Quell-Read, Bild-Änderungserkennung nur per mtime, zurückgestellte Sprint-015-Minors; Sprint-013-Erbe (Kampf-Header-Wortlaut, AT/PA ohne Wund-Overlay, `.talent-row`-Grid, Portrait-Plumbing, Python/JS-Würfel-Mathe-Mirror ohne Drift-Check — D-041 berührt den Mirror).
