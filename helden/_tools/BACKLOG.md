# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

_(keine)_

## Backlog

| EPIC | Title | Effort | State | Blocked by |
|------|-------|--------|-------|------------|
| D-067 | **DNS-Rebinding umgeht den Sprint-033-Origin-Check auf allen schreibenden Routen — Host- und Origin-Header stammen beim Rebinding von derselben angreifer-kontrollierten Hostname, der String-Vergleich besteht daher.** Die Sprint-033-Gesamtreview bestätigte den Angriff empirisch (Szenario N, echter Server): `POST /api/commit` mit `Host: Origin: rebind.evil.example:<port>` → 200, echter Commit; eine ebenso adressierte `PATCH .../value` überschrieb real eine Datei. Nach dem Rebind sind auch GETs (z. B. `/api/held/<slug>`) same-origin lesbar — Impact daher Lese- **und** Schreibzugriff, nicht nur Schreiben. Fix-Vorschlag der Gesamtreview: Host-Allowlist (`{'127.0.0.1:<port>', 'localhost:<port>'}`) im selben `before_request`-Hook, angewandt auf **alle** Methoden inkl. GET, Ablehnung mit 403/421. Optional im selben Zug: ein Test, der `%r`-Escaping eines Origin-Headers mit eingebettetem CR/LF in den neuen D-066-Logzeilen pinnt (aktuell nicht durch einen Test gesichert, in der Praxis aber sicher — Sprint-033-Gesamtreview-Minor). Bewusst aus Sprint 033 ausgeklammert (User-Entscheidung in der Sprint-Planung: CSRF-Fix = JSON-Pflicht + Origin-Check, Host-Allowlist separates EPIC). **Zusatz (User-Entscheidung 24.09.2026): im selben Sprint ein kurzes Bedrohungsmodell `helden/_tools/SECURITY.md` schreiben (Angreifer = fremde Webseite im selben Browser; Schutzschichten Host-Allowlist, Origin, JSON-Pflicht, Slug-/Pfad-Guards, Fehler-Sanitizing) und die Gesamtreview gegen dieses Modell prüfen lassen — Nachbarfunde innerhalb des Modells werden im Sprint behoben, nicht als neue EPICs gefiled; danach gilt die Traversal-/CSRF-Serie (D-061…D-067) als abgeschlossen.** | S–M | ready | — |
| D-068 | **Design-Audit des Dashboards mit dem Skill `/design-audit`** (Diagnose-Checkliste aus taste-skill/redesign-skill, gefiltert durch Papier-Optik, Druck-Kontraste und Dichte-Entscheidungen). Nur Befundliste nach `output/design-audit-YYYY-MM-DD.md`, danach entscheidet der User, welche Funde eigene EPICs werden. Kein Code im Audit selbst. | S–M | ready | — |
| D-069 | **`tests/conftest.py` einführen** — jede neue Testdatei macht heute `sys.path.insert(TOOLS_DIR)` selbst; zentralisieren, Bestand migrieren (698 Tests, per Golden-Lauf vorher/nachher verifizieren). | S | ready | — |
| D-070 | **Kampf-Tab: Header „AT / PA · TaW“ ist mehrdeutig; AT/PA-Zeilen zeigen kein Wund-Overlay.** Wortlaut klären, Overlay analog zum Basiswert-Overlay (D-041) ergänzen. | S | ready | — |
| D-071 | **Python-/JS-Würfel-Mathe-Mirror ohne Drift-Check; der Python-Mirror kennt Wunden nicht.** Drift-Test (node) ergänzen, JS-Seite über die Wundlogik hinaus verhaltensgetestet. | M | ready | — |
| D-072 | **Chronik-Robustheit:** leerer IG-Tag wird beim Parsen verworfen (Design-Frage klären), `chronik_import.py` ohne Schutz gegen leeren Quell-Read, Bild-Vergleich nur per mtime. | S | ready | — |
| D-073 | **Steigern-Nachzug:** Steigerungs-Log vermerkt den Erfahrungs-Modifikator nicht, `.sg-erf` hat `display:block`, lineares SKT-Modell prüfen. | S–M | ready | — |
| D-074 | **Portrait-Plumbing ist inert** (laut Sprint-013-Stand angelegt, ohne Wirkung) — erst den Ist-Zustand im Code prüfen, dann anbinden oder entfernen; Entscheidung des Users nötig. | S | ready | User-Entscheidung |

_(Vault-`backlog.md`: nur User-Todos B-029…B-031 (Push, Token), kein Dashboard-Bezug.)_

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
| D-066 | Verschluckte Fehler an 4 Stellen loggen den vollen Grund ins Server-Log, Antworten unverändert; 5 `caplog`-Tests. 693 → 698 Tests — [[sprints/sprint-033/handoff.md]] | S | 033 |
| D-065 | `POST /api/commit` verlangt `application/json` (415) und ein app-weiter `before_request`-Hook lehnt fremde `Origin`-Header auf allen schreibenden Routen ab (403); Gesamtreview reproduzierte den CSRF-Exploit empirisch und fand D-067. 688 → 693 Tests — [[sprints/sprint-033/handoff.md]] | S | 033 |
| D-064 | `api_commit` leakt keinen rohen Git-Stderr mehr (feste Meldung `git operation failed`), Fix nur an der HTTP-Grenze. 687 → 688 Tests — [[sprints/sprint-032/handoff.md]] | S | 032 |
| D-063 | `api_held` leakt keine absoluten Dateisystempfade mehr (`FileNotFoundError` → 404 statt blankem `except Exception`); Dual-Assertion-Testkonvention etabliert. 684 → 687 Tests — [[sprints/sprint-031/handoff.md]] | S | 031 |
| D-062 | `slug_param` und `/held/<path:s>` per Allowlist-Regex gegen Path-Traversal gesichert (auch `%5C`-Vektor unter Windows). 671 → 684 Tests — [[sprints/sprint-030/handoff.md]] | S | 030 |
| D-061 | PATCH-Routen validieren `file` (`_safe_join`) und `campaign` (Regex) gegen Path-Traversal; alle neuen Tests diskriminieren gegen den ungefixten Stand. 662 → 671 Tests — [[sprints/sprint-029/handoff.md]] | S | 029 |
| D-060 | Footer gleitet synchron mit dem Würfelpanel (`transition:bottom 0.2s ease`), Test liest die Panel-Dauer relational. 661 → 662 Tests — [[sprints/sprint-028/handoff.md]] | S | 028 |
| D-059 | Automatisierte Tests für PATCH „Verlauf speichern“ (Routen-Wiring, `camp`-Guard, JSON-Body); das `file`-Feld blieb bewusst offen → D-061. 656 → 661 Tests — [[sprints/sprint-028/handoff.md]] | S | 028 |
| D-058 | Probe-Spalte im Zauber-Tab-Druck einzeilig (Grid-fr-Anteile) und Ritual-/SF-Karten-Stretch per `.grid.align-top` behoben; Nebenwirkung +4,5 % Zeilenhöhe dokumentiert. 653 → 656 Tests — [[sprints/sprint-028/handoff.md]] | S–M | 028 |
| D-057 | `#tab-profil table *`-Flächenschlag entschärft (`.sessions-table`), Golden-Render-Diff bestätigt reines Refactoring. 652 → 653 Tests — [[sprints/sprint-028/handoff.md]] | S | 028 |
| D-055 | Verlaufstext druckt vollständig (`<pre class="journal-verlauf-print">`-Mirror bei `beforeprint`); Methodenbefund: Breitenabhängige Messungen brauchen ≥ 2 Fensterbreiten. 648 → 652 Tests — [[sprints/sprint-027/handoff.md]] | S–M | 027 |
| D-054 | LeP/AsP/AuP-Zahlen sind im Ausdruck sichtbar (`.vital-input` bleibt sichtbar, Druckfarben 14,62 : 1, per echtem PDF-Pfad verifiziert). 633 → 638 Tests — [[sprints/sprint-027/handoff.md]] | S–M | 027 |
| D-056 | Ruling: getönte Papieroptik druckt weiß, das bleibt Zielzustand (`print-color-adjust:exact` nicht setzen); reine Dokumentationsentscheidung — [[sprints/sprint-027/handoff.md]] | S | 027 |
| D-053 | Druck-Kontrast der übrigen 7 Tabs: 37 Gruppen / 495 Elemente gemessen und auf 0 Restgruppen gefixt, Wächter gegen `sticky`/`fixed` im Druck; Methodenbefund: Print-Emulation ≠ echter PDF-Druck. 615 → 633 Tests — [[sprints/sprint-026/handoff.md]] | S–M | 026 |
| D-052 | Druck des Zauber-Tabs: Überlauf kam aus dem `.spell`-Grid (nicht aus „Spontane Modifikationen“), 20 Kontrastgruppen auf 14,62 : 1, überlaufsicheres Druck-Grid; übrige Tabs → D-053 — [[sprints/sprint-025/handoff.md]] | S | 025 |
| D-051 | Ritual-Artikelvorschau: Stabzauber- (9) und Apport-Zeile im Zauber-Tab zeigen ihren `##`-Abschnitt aus `stabzauber.md` als `<details>` (Makro `partials/_artikel.j2`, geteilt mit SF/Zauber); Parser liefert `wiki_path` je Ritual-Zeile (nur Namensspalte), `build_context` bettet die 10 Artikel ein, Apport-Namenszelle im Bogen als Anker-Link (einmalige User-Freigabe); Browser-Fund: Namenslink im Druck 1,07 : 1 (eigene Bildschirm-`color` erbt die Druckfarbe von `.sf-name` nicht) → `tabs.css` 14,62 : 1, bessert auch die 15 SF-Links; Static-Render 481 641 → 508 457 B, 40 → 50 Vorschauen, längster Artikel 962 px @1280 | M | 024 |
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
