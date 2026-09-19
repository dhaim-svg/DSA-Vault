# Sprint 020 Handoff — Druck-Konsistenz, Touch-Ziele, Chip-Entflechtung (D-045, D-047, D-048, B-014)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-045/D-047/D-048 → in-progress, plan.md) — `f7cc6a7`
- ✅ T1 (**D-045**): Chronik-Druck — nur die **aktive** Ansicht wird gedruckt (`.chronik-view--active` im Print-Block, Register-Sonderregel entfällt); ein aktiver Register-Filter erscheint im Ausdruck als Kopfzeile `Gefiltert nach: "…" — n/N Einträge` (`.register-druckfilter`, `textContent`, `:not([hidden])`); `beforeprint`/`afterprint` unverändert — `bc2f3a9`
- ✅ T2 (**D-047**): Touch-Ziele @ 400 px — Inventar-Eingaben/„+ Hinzufügen“ und Zustands-Chips ≥ 44 px (nur im ≤ 480-px-Block); offenes Würfelpanel reserviert seine Höhe über `--dice-panel-h` (`dice.js` schreibt, `base.css` `body{padding-bottom}` ≤ 480 px); Steigern: Scroll-Hinweis, `tabindex`/`role`/`aria-label` nur bei `scrollWidth > clientWidth` (`syncScrollOverflow`/`watchScrollOverflow`, `ResizeObserver`); Druck-Selektor `.spell .zfw-num` gescopt (+ `PRINT_SPELL_SELECTORS`) — `0284330`
- ✅ T3 (**D-048**): Zustands-Chips wirken nur noch über die Panel-Vorbelegung — `applyWundModsToProben` nutzt `attrMod` statt `probeMod` (kein Overlay mehr auf den 203 `[data-attr]`-Spans; Wund-Overlay bleibt), Legende sagt „ändern nur die Probe (Würfelpanel-Modifikator), nicht die angezeigten Attribut- und Basiswerte“, führendes Leerzeichen im Wund-Satz entfernt — `d63a00b`
- ✅ T4 (**B-014**): `/sprint-wrap` repariert — `render-held.py <slug>`, Sprint-Nr.-Wortlaut („= zuletzt abgeschlossener Sprint, nicht erhöhen“), Phase 3a entfernt EPICs aus `## In Progress`, Phase 2 läuft zusätzlich mit `-W error` — `05a0cfa`, `30f2064`
- ✅ T5: Verifikation (Suite ×2, Static-Render, Playwright-Runde, Task- + Gesamt-Review) — Review-Minors inline `ad1685a`, `verification.md`, Static-Render, Wrap
- Commits liegen **lokal** auf `master`, **nichts gepusht** (`origin/master` weiter bei `0351829`, 52 Commits davor: Sprint 018–020).

## Was funktioniert

- **Chronik-Druck:** Roh, Kompiliert und Register drucken jeweils nur, wenn sie aktiv sind; Register-Filter bleibt im Ausdruck bestehen und wird in der Kopfzeile benannt (nie am Bildschirm sichtbar). `<details>`-Aufklappen im Druck wie zuvor.
- **Zustands-Chips (Hausregel):** Schmerz/Furcht/Betäubt/Verwirrt/Erschöpft (−2/−2/−4/−2/−2) wirken **ausschließlich** als Vorbelegung des Würfelpanel-Modifikators (`probeMod`); kein Attributwert-Overlay, keine Basiswert-Anzeige, nie auf Schaden. Badge nennt sie zur Information.
- **Wunden (unverändert aus Sprint 019):** AT/PA/FK/INI/GE −2, GS −1 je Wunde (WdS S. 57); Overlay nur `GE 13→9` auf den Attributspans und `base→eff` auf den Kampf-Basiswerten; Talent-/Zauberproben nutzen den reduzierten GE-Wert (Panel-Modifikator bleibt dort 0 bzw. nur der Chip).
- **Mobile 400 px:** Touch-Ziele Inventar-Formular und Zustands-Chips 44 px; offenes Würfelpanel verdeckt den statischen Footer nicht mehr (Lücke +15,8 px); Steigern-Scrollbereiche nur bei Überlauf fokussierbar/mit Hinweis, folgt dem Resize in beide Richtungen; alle Tabs ohne horizontalen Überlauf (`scrollWidth 385 ≤ 400`).
- **Zauber-Druck:** alle Textfarben dunkel auf Papier (`.spell .zfw-num` jetzt gescopt, 14,62:1).
- Alle Features aus Sprint 013–019 unverändert (Chronik Roh/Kompiliert/Register + Suche, Eigenschafts-Leiste, Inline-Werte, Zauberspeicher, Aussehen, Würfel, Steigern, Inventar, Sprachen, Artikelvorschau, ZfW-Sortierung, Static-Render mit eingebettetem JS).
- **Tooling:** `/sprint-plan` und `/sprint-wrap` sind konsistent (CLAUDE.md-Sprint-Nr. = zuletzt abgeschlossener Sprint; Wrap 020 → `20`).

## Verifikation

- **Test Suite:** 403/403 bestanden, auch mit `-W error` (Baseline 379 → +24: T1 +10, T2 +8, T3 +6). Jeder neue Test mit belegter Negativprobe; die inline nachgezogenen Assertions (`ad1685a`) per Mutation gegengeprüft. Node-Tests liefen real (v24.13.1).
- **Static Render:** `output/illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0), 450 002 B (Sprint 019: 446 203 B, +3 799 B); 0× `<script src>`, 25× `<details class="artikel-details`, 7× `data-wund-stat=`, neu 4× `register-druckfilter`, 2× `sg-scroll-hint--on`, 5× `dice-panel-h`.
- **Browser (Playwright, Static über `http.server`, nur lesend, `innerWidth` je Messung verifiziert; Details `verification.md`):** **7 PASS / 0 FAIL / 0 nicht messbar.** Touch-Ziele @ 400 = 44 px (@ 1280 unverändert 30/25 px); Panel-Lücke +15,8 px; Steigern Hinweis/`tabindex` nur bei Überlauf, folgt Resize; Chronik-Druck je Ansicht genau die aktive, Filter „Baronins“ → `1/55 Einträge`; Chips: 0 Pfeile auf 203 Spans, `#dp-mod` −2; 2 Wunden: nur `GE 13→9`; Kontrast 14,62:1; Konsole nur erwartete 404er.
- **Reviews:** Task-Reviews T1–T3 je Approved (0 Critical/Important, 6 Minors → `ad1685a`); Gesamt-Review (Opus) **Ready to merge: Yes**, 5 Minors disponiert (→ B-015/B-016, `-W error` im Wrap-Kommando inline).
- **Domänen-Grenze:** nur `helden/_tools/`, `output/`, `.claude/commands/`, `backlog.md`; nichts unter `abenteuer/`, `helden/illaen-baernhold/`, `wiki/`, `raw/`.
- **Ruling (Preflight):** Die Plan-Formulierung zu D-048 („Overlay-Pfad nach Effekt-Art filtern“) war ungenau — `statMod`/`attrMod` waren schon nur-Wunden; die Doppelzählung entstand allein in `applyWundModsToProben` (`probeMod`→`attrMod`). Am Code vom Final-Reviewer bestätigt. Zweite Korrektur: der ungescopte Druck-Selektor `.zfw-num` stand in `tabs.css`, nicht (wie im Backlog notiert) in `base.css`.

## Als nächstes (Sprint 021)

- **Dashboard-Backlog ist leer** (`BACKLOG.md`: In Progress und Backlog leer) — Sprint 021 braucht neue EPICs oder Wiki-/Tooling-Arbeit.
- **B-013** (Vault-`backlog.md`, wiki, M) — Frontmatter der Zauberartikel reparieren (103/268 ungültiges YAML, `wiki-luecken.md` L22), danach Fallback-Parser in `parsers/wikiartikel.py` entfernen. Steht an der Spitze des Vault-Backlogs.
- **B-016** (tooling, S) — Repo-Hygiene: `.playwright-mcp/` in `.gitignore`, `.gitattributes` (`* text=auto`), Entscheidung über `.claude/settings.json` (untracked) — **braucht eine User-Entscheidung**.
- **B-015** (tooling, S) — Test-Helfer (`needs_node`, `_js_function`/`_function_body`, node-Fake-DOM-Runner) in ein gemeinsames `tests/jsfixtures.py`. Sinnvoll, sobald das nächste Mal JS aus pytest getestet wird.
- **Kandidaten für neue EPICs (aus „Bekannte Einschränkungen“, noch nicht im BACKLOG):** Desktop-Footer unter dem offenen Würfelpanel; echter PATCH-Pfad im Browser; Vorschau auch für Rituale/SF; Zustände: optionale LE-/AU-Mali (vom User zweimal abgewählt — nicht ohne neue Anfrage).
- (Reihenfolge = Empfehlung, nicht Pflicht.)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Desktop (> 480 px): Footer-Leiste unter dem offenen Würfelpanel** — gemessen −277 px @ 1280 (Footer 819–872, Panel-Oberkante 594,8). Vorbestehend; D-047 reserviert nur ≤ 480 px (dort ist der Footer statisch).
- **Zustands-Chips = Hausregel, Werte unverändert** (User-Entscheidung 19.09.2026): weiterhin ohne feste Regelquelle in WdS/WdH/WdE (`wiki-luecken.md` L23); die belegten optionalen Mechaniken (LE-/AU-Mali WdS S. 57/83, Schmerz-Probe S. 82, Ängste WdH S. 268) stehen im Wiki-Artikel `grundregeln/zustaende.md`, sind aber nicht im Dashboard.
- **Nicht im echten Druckdialog geprüft:** Der Chronik-Druck wurde mit `emulate_media: print` (computed styles) gemessen, nicht mit einer echten Browser-Druckvorschau/PDF; `file://` weiterhin nicht direkt im Browser geprüft (Playwright blockt `file:`).
- **Steigern-Negativfall @ 400 px:** bei 400 px überliefen alle drei Steigern-Tabellen — der Fall „Tabelle passt, kein Hinweis/`tabindex`“ ist im Browser nur bei 1280 px und im node-Test belegt.
- **Echter `PATCH`-Pfad ungeprüft** (Static über `http.server`, Flask nicht beteiligt); Wund-Simulation im Browser nur im Speicher (`dataset.wunden`).
- **Wund-Regeln unverändert ausgeklammert:** Wundschwellen-Berechnung, Zonenwunden (WdS S. 107), „Wunden ignorieren“ (S. 82); Python-Würfel-Mathe-Mirror kennt weiterhin keine Wunden.
- **Bekannte Minors (Gesamt-Review):** Test-Helfer dupliziert (→ B-015); gemischte Zeilenenden (`core.autocrlf=true`, kein `.gitattributes`; `chronik.css`/`register.js`/`register.j2` LF, Nachbarn CRLF; → B-016); die drei node-Fake-DOM-Runner sind nahezu identisch.
- **Process-Notizen:**
  - Briefs/Ledger von Hand unter `.superpowers/sdd/sprint-020/` (git-ignoriert; `sdd-workspace`/`task-brief` kollidieren mit dem Basename `plan`); Reviewer-Berichte > ~3500 Zeichen werden abgeschnitten — Verdikt zuoberst, Rest per `SendMessage` nachfordern.
  - T4 (B-014) und die Review-Minors wurden vom Controller inline erledigt (Regel `feedback_quality_fix_inline`); pfadbegrenzte Commits (`git commit -- <pfade>`) schützen vor fremd gestagten Dateien.
  - **Streuner:** Ein `python -m http.server 8765 --bind 127.0.0.1` (PID 32384, seit 19:58, per `nohup` gestartet) ist ein Überbleibsel der T2-Messung und lief zum Wrap-Zeitpunkt noch (Stoppen wurde vom Permission-Klassifizierer verweigert) — bei Bedarf `taskkill /PID 32384 /F`. Er blockiert Port 8765 für spätere Browser-Checks (freien Port wählen).
  - `.claude/settings.json` bleibt untracked (User entscheidet, B-016); `.obsidian/workspace.json` + `Welcome.md` dauerhaft dirty.
- **Aus Sprint 017–019 unverändert offen:** Register hängt am Session-Format; `Verlauf`-Speichern in der Kompiliert-Ansicht nie im Browser angeklickt; inhaltliche Sichtung der vier Sessions (47 `(?)`-Stellen); Kommando-Mängel von `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://` Fake-Erfolg; Chronik-Parser-Kleinigkeiten; `.journal-readonly`-Kontrast ~3,3:1; Sprint-013-Erbe (Kampf-Header-Wortlaut, `.talent-row`-Grid, Portrait-Plumbing); Tooltips auf Touch nicht sichtbar (Legende + Badge sind der einzige Hausregel-Hinweis). *(Erledigt in Sprint 020: der zusätzliche Tab-Stop je Steigern-Tabelle und der immer sichtbare Scroll-Hinweis, s. D-047.)*
