# Sprint 017 — Chronik-Block: NSC-/Orts-Register, Parser-Datum, Mobile-Überlauf

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-036/D-040/D-042 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-017/plan.md |
| T1 | **D-042** `Datum:`-Zeile als IG-Datum erkennen (`13. Phex -> Start` → `13. Phex (Start)`) | ✅ done | parsers/chronik.py, tests/test_chronik.py |
| T2 | **D-036a** Register-Parser: Session-Sektionen → dedupliziertes NSC-/Orts-Modell (`build_register`, reine Funktion, balancierter Klammer-Scan); `register` als Top-Level-Key in `build_context` | ✅ done | parsers/register.py (neu), rendering.py, tests/test_register.py (neu), tests/test_rendering.py |
| T3 | **D-036b** Register-Ansicht im Chronik-Tab (3. Umschalt-Button, `partials/register.j2`, `static/register.js` in IIFE, clientseitige Suche, Styles in `chronik.css`). **Vorab:** `roh_view()`/`kompiliert_view()`-Helper in `test_chronik_tab.py` auf Ende-Marker umstellen | ✅ done | templates/partials/chronik.j2, templates/partials/register.j2 (neu), static/register.js (neu), static/chronik.js, static/chronik.css, rendering.py (`JS_FILES`), tests/test_chronik_tab.py, tests/test_rendering.py |
| T4 | **D-040** Mobile 400 px: Überlauf in Zauber/Steigern/Inventar/Profil beseitigen (Media-Query nach `.talent-grid`-Muster, `.spell`-Header ausblenden, Tabellen in `overflow-x:auto`); Abnahme `scrollWidth ≤ 400` für alle 8 Tabs | ✅ done | static/base.css, static/tabs.css, templates/partials/profil.j2 |
| T5 | Verifikation (pytest inkl. `-W error`, Static-Render, Headless-Chrome 400 px, Domänen-Grenze `abenteuer/`) + Final-Review + `/sprint-wrap` | ✅ done (Verifikation + Review; `/sprint-wrap` steht aus) | — |

**Reihenfolge:** T1 → T2 → T3 sequenziell (T3 braucht T2s Datenmodell); T4 unabhängig (disjunkte Dateien: nur CSS + `profil.j2`) und parallel zu T2 möglich.

## Key Design Decisions

- **T1 — zusätzliches Muster, kein Umbau.** `_parse_spielabend_body()` prüft IG-Daten nur im `BOLD_LINE_RE`-Zweig; die `Datum:`-Zeile ist unfett. Neues `DATUM_PREFIX_RE` (wiederverwendet `DSA_MONATE`), geprüft vor dem `_text_block()`-Fallback; Suffix nach `->` wird als `(Suffix)` angehängt. `Datum:` kommt in der echten `chronik.md` genau einmal vor (Zeile 26). `flush()`-Verwerfen leerer IG-Tage bleibt unangetastet.
- **T2 — eigener Parser, reine Funktion.** `build_register(sessions)` nimmt die von `load_kampagne()` bereits geparsten Sessions (`sektionen['Neue NSCs / Orte']`); kein zweiter Plattenzugriff, `kampagne['sessions']`-Kontrakt unverändert. `register` als eigener Top-Level-Key in `build_context` (sonst müssten alle `kampagne={'sessions': …}`-Test-Stubs nachgezogen werden).
- **T2 — Parsing.** H3 `### NSCs` / `### Orte` mit normalisiertem Key-Match; Top-Level-Bullet `- **Name**…`; Klammer-Zusatz (`(?)`-Marker → `unsicher`, sonst `qualifier`) per **balanciertem Klammer-Scan** — verschachtelte Klammern kommen real vor (2 Zeilen); Separator `—`/`–`/`-` optional; Dedup über NFC + `casefold()`, erster Vorkommensname gewinnt, `unsicher` = OR; pro Eintrag `erwaehnungen`, `sessions`, vorberechnetes `such`-Feld; fehlende `nr` → kein leerer Chip.
- **T3 — dritte Ansicht, kein neuer Tab.** `VIEWS = ['roh', 'kompiliert', 'register']`; Suche rein clientseitig (Static-Render hat unter `file://` kein Backend) → keine Änderung an `server.py`. Neues `register.js` in einer IIFE (Bug-Klasse aus D-038), in `JS_FILES` nach `chronik.js`. Styles in die vorhandene `chronik.css` (kein `CSS_FILES`-Eintrag).
- **T3 — Escaping.** `autoescape=False`: `| e` auf **jedem** Wert inkl. `data-such`; Escaping-Test mit `<script>` in Name/Text. Defensiver `default(...)` für `register` im Template, weil der Render-Helper in `test_chronik_tab.py` es nicht übergibt.
- **T4 — Media-Query nach vorhandenem Muster.** `.spell` (6-Spalten-Grid, ≈ 968 px Minimum, `base.css:368`) → `1fr` bei `max-width:700px`; Header-Div und Datenzeilen teilen die Klasse `.spell` → Header in der Schmalansicht ausblenden. Steigern/Profil-Tabellen in `overflow-x:auto`-Container; Inventar: `.inv-add-btn`-`nowrap` und `.inv-coin-grid` entschärfen. Mitnehmen: feste Fußleiste überdeckt bei 400 px den Banner-Titel.

## Out of Scope

- **D-018 (Zauber-Inline-Vorschau, L)** — trotz Spitzenposition in `BACKLOG.md` vom User auf Sprint 018 verschoben.
- **D-041 (Wundregel-/Zustände-Audit, M)** — Regelarbeit, unabhängig vom Chronik-Block; zusammen mit D-036 zu viel für einen Sprint.
- **`nsc.md`/`orte.md` in `abenteuer/`** — bewusst verworfen (User-Entscheidung 19.09.2026): `abenteuer/` ist User-Domäne, das Register wird zur Render-Zeit generiert.
- **Automatische Wiki-Verlinkung** der NSC-/Orts-Namen — erst wenn das Register steht.
- Chronik-Meta-Markdown-Rendering, `chronik_import.py`-Härtung, zurückgestellte Sprint-015-Minors — unverändert offen.

## Verifikation

1. `pytest` aus `helden/_tools/` — Baseline **196 grün**, neue Tests additiv, auch mit `-W error`.
2. Static-Render (`render-held.py illaen-baernhold`) → exit 0, JS eingebettet.
3. Headless-Chrome 400 px: `scrollWidth ≤ 400` für **alle acht** Tabs.
4. Browser (served): Register listet NSCs/Orte aller vier Sessions, Suche filtert live, Ansicht überlebt Reload; Roh-Ansicht zeigt beim 04.06.-Abend `13. Phex (Start)`; Konsole ohne neue Fehler.
5. `git status --short` zeigt **keine** Änderung unter `abenteuer/`.
6. Druckansicht: Register-View erscheint nicht zusätzlich zur aktiven Ansicht.

## Stand am Sprint-Ende

- **T1–T5 fertig, 243/243 Tests** (Baseline 196, `-W error` sauber). Commits ab `9dc5600`: T1 `9b33b36`, T2 `414cb53`, T3 `c278f8f`/`ea6c873`/`cdb7c2f`, T4 `47f755b`, Breakpoint-Fix `0695750`, Static-Render neu generiert. **Nichts gepusht** (`origin/master` steht bei `0351829`).
- **Gesamt-Review (Opus): Ready to merge**, 0 Critical/Important. Browser-Verifikation (Playwright, served): alle 8 Tabs bei verifiziertem 400 px ohne Überlauf (Zauber 1019→385, Steigern 442→385, Inventar 485→385, Profil 450→385), Register 55 Einträge (24 NSCs + 31 Orte), Suche/Escape/Umlaut-Faltung/Reload ok, Roh-Ansicht `13. Phex (Start)`. Nachmessung fand den Zauber-Breakpoint 1040 px zu niedrig (Grid ragte 1041–1061 px bis 21 px aus der Karte, `scrollWidth` sieht das nicht) → 1070 px, engster Punkt 1071 px mit 9 px Reserve.
- **Abweichungen von der Planskizze:** Profil-Überlauf kam nicht von der Tabelle, sondern vom Kampagnen-Status-Text in `.c-head`; Zauber hatte zusätzlich einen Überlauf in `.mod-table` (≤ 600 px); Footer-Leiste war bei 400 px 671 px breit (Kodex-Druck-Button außerhalb) → umbrechend, bleibt `position: fixed`; Steigern-Tabelle scrollt ≤ 600 px seitlich im Container.
- **Für `/sprint-wrap` vormerken:** D-036 + D-040 + D-042 → Done (Sprint 017). Neue Kandidaten:
  - **Zauber-ZfW-Sortierung im Kompaktlayout unerreichbar** — die Sortierung hängt an der Kopfzeile (Inline-JS in `dashboard.html.j2:158-168`), die ≤ 1070 px ausgeblendet ist; das betrifft jetzt auch kleine Laptop-Fenster, nicht nur Handys.
  - **Banner-Titel „ILLAEN BAERNHOLD" bei 400 px rechts abgeschnitten** (nicht angefasst).
  - **Touch/A11y:** Footer-Leisten-Buttons ~33 px hoch (< 44 px), Leiste verdeckt ~82 px; Steigern-Scroll-Container ohne `tabindex`.
  - **Print:** Roh + Kompiliert drucken immer, Register nur wenn aktiv; ein aktiver Register-Filter bleibt im Druck bestehen (Suchfeld ausgeblendet → stille Teilmenge).
  - **Parser-Kleinigkeiten:** `Datum: 1. Namenloser Tag` matcht nicht (Asymmetrie zum Fett-Zweig), `Datum:`-Zusatz ohne `strip_wikilink`, `Datum: 13. Phex ->` (leerer Zusatz) fällt in den Text-Fallback; `build_register` stürzt bei Nicht-String-`sektionen` ab (`load_kampagne` liefert nur Strings), Name aus Leerzeichen ergäbe leeren Eintrag.
  - Untracked `.playwright-mcp/` taucht bei Playwright-Läufen im Vault-Root auf (Verifikations-Agent hat es jeweils gelöscht) — ggf. `.gitignore`-Zeile.
- **Unverändert offen (Out of Scope):** D-018 (Sprint 018), D-041 (Wundregel-Audit), automatische Wiki-Verlinkung der Register-Namen.
- **Rulings dieses Sprints** (Master statt Worktree; Sortierung nach gefaltetem Namen; Schnittstelle `register`; kein Gruppen-Toggle; Qualifier verbatim; gemeinsame `fold()`; Implementer sequenziell) stehen im Ledger-Auszug der Abschluss-Nachricht; Controller-Fixes ohne Subagent: `register.js`-Unicode-Escape, `register.j2`-Trim-Guard, Breakpoint 1070, `:empty`-Regel, Testpolitur.

