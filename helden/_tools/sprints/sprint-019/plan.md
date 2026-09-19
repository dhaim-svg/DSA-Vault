# Sprint 019 — Wund-/Zustände-Audit + Zauber-Feinschliff (D-041, D-046, D-044)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-041/D-044/D-046 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-019/plan.md |
| T1 | **D-041a** Regelrecherche in den PDFs + Wiki-Artikel `grundregeln/zustaende.md` (Wundauswirkungen verlinkt, Zustände belegt oder als unbelegt markiert), `_grundregeln.md` + `_master-index.md` + `wiki-luecken.md` (L23) | ⬜ todo | wiki/dsa-4.1/grundregeln/zustaende.md (neu), wiki/dsa-4.1/grundregeln/_grundregeln.md, wiki/_master-index.md, wiki-luecken.md |
| T2 | **D-041b** Wundlogik regelkonform: Skopus-Modell statt Einzelzahl (`session.js`), `getWundMod(cfg)` nach Probenart (`dice.js`), Badge-Text nennt den Geltungsbereich, Overlay nur noch auf GE | ⬜ todo | static/session.js, static/dice.js, templates/partials/kampf.j2, tests/test_static_js.py |
| T3 | **D-041c** Zustände an T1 angleichen: belegte Zustände mit Quellwerten, unbelegte sichtbar als Hausregel, getrennt vom Wund-Malus | ⬜ todo | static/session.js, static/tabs.css, templates/partials/kampf.j2, tests/test_static_js.py |
| T4 | **D-046** Zauberliste: Print-Farben für `.nlink`/`.zfw-num`/`.zd`/`.kosten`/`.wirkung`, Grid-Überstand bei 1071–1130 px (`minmax`) | ⬜ todo | static/base.css, static/tabs.css, tests/test_rendering.py |
| T5 | **D-044** Mobile/Touch: Banner ≤ 400 px, Footer-Leiste (44 px + `position:static`), Steigern-Scroll `tabindex`, `.inv-add-input`-Klasse, Summary „▸ Artikel" 44 px | ⬜ todo | static/base.css, static/tabs.css, templates/partials/inventar.j2, tests/test_rendering.py |
| T6 | Verifikation (pytest inkl. `-W error`, Static-Render, **eine** Playwright-Runde 400/1071/1280 px + Print-Emulation, Domänen-Grenze) + Gesamt-Review, danach `/sprint-wrap` | ⬜ todo | — |

**Reihenfolge:** T1 → T2 → T3 strikt sequenziell (T3 braucht T1s Ergebnis; T2/T3 fassen beide
`session.js` an). T4 → T5 sequenziell (beide `base.css`). T4/T5 sind inhaltlich unabhängig von
T1–T3, laufen aber wegen `tests/test_rendering.py` nach ihnen, nicht parallel.

## Key Design Decisions

Vom User entschieden (19.09.2026): Scope = D-041 + D-046 + D-044 · Zustände per PDF-Recherche
belegen und Wiki-Artikel anlegen · Wund-Malus **strikt regelkonform** (keine Talent-/Zauberabzüge,
keine optionalen LE-Schwellen).

**Ausgangsbefund (belegt):** WdS S. 57 (`raw/pdf-extracted/wege-des-schwertes/kapitel-04-kampf.txt:927-931`):
„AT-, PA-, FK- und INI-Basiswert sowie die GE sinken sofort um je 2 Punkte pro Wunde, die GS um 1."
Wiki stimmt (`wiki/dsa-4.1/kampf/kampfregeln.md:93`). Code (`session.js:30`, `computeWundPenalty` =
`wunden * 2`) zieht pauschal von allen 8 Eigenschaften und jeder Probenart ab (`dice.js:532`).
Zustands-Chips (Schmerz/Furcht/Betäubt/Verwirrt/Erschöpft) haben keine Quelle. Testabdeckung: null.

- **T1 — Recherche mit hartem Deckel.** Kartierung liegt vor: Erschöpfung/Überanstrengung
  `wege-des-schwertes/kapitel-05-umfassend.txt:69-95` (schon im Wiki: `grundregeln/bewegung-reisen.md:201-229`),
  Betäubung nur als Kampfmanöver in `kapitel-04-kampf.txt` (Bewusstlosigkeit, kein Probenmalus).
  **Furcht und Verwirrung haben in den extrahierten Büchern keine allgemeine Zustandsregel** (Treffer
  sind Zauber-/Dämonen-Wirkungen). Regel: **maximal je ein gezielter Suchlauf pro Zustand**; was nicht
  belegt ist, wird als „nicht belegt" dokumentiert. Kein neues Buchkapitel extrahieren.
- **T1 — Artikel verlinkt, statt zu duplizieren.** `grundregeln/zustaende.md` fasst zusammen und
  verweist per `[[wiki link]]` auf `kampf/kampfregeln.md` und `grundregeln/bewegung-reisen.md`. Kein
  Regeltext-Kopieren. Format nach CLAUDE.md: Zitatblock Quelle+Seite, `## Key Takeaways`,
  `## Verwandte Artikel`. Unbelegtes zusätzlich als **L23** in `wiki-luecken.md`.
- **⚠️ `raw/pdf-extracted/` ist gitignored — `Grep` auf den Ordner liefert 0 Treffer** (Ordner-Grep
  nach `Betäub` = 0, dieselbe Datei direkt = 22). Recherche mit **explizitem Dateipfad** oder
  `Select-String`; muss im T1-Briefing stehen.
- **T2 — Skopus statt Einzelzahl.** `computeWundPenalty` wird durch ein Effektmodell mit
  Geltungsbereich je Effekt ersetzt (AT/PA/FK, INI, GE, GS). `computeActiveEffects()` (`session.js:113`)
  bleibt einzige Quelle der Wahrheit für Badge, Overlay und Würfelpanel. `window.DSASession` ist die
  Schnittstelle zu `dice.js`: rückwärtskompatibel halten oder in **beiden** Dateien im selben Commit umstellen.
- **T2 — `dice.js` kennt die Probenart.** `openPanel({type})` mit `talent|zauber|eigenschaft|at|pa|schaden`
  (`dice.js:579-665`). `getWundMod()` (`:204`) → `getWundMod(cfg)`: voller Malus bei `at`/`pa`, bei
  `eigenschaft` nur für `GE`, **0** bei `talent`/`zauber`/`schaden`. Offen (im Kampf-Tab prüfen, nicht
  raten): ob die `eigenschaft`-Config das Kürzel mitführt (sonst aus `el.dataset.attr`) und ob FK ein
  eigener Typ ist oder über `talent` läuft.
- **T2 — Overlay nur noch GE.** `applyWundModsToProben` (`session.js:153`) filtert auf
  `el.dataset.attr === 'GE'`; die übrigen `[data-attr]`-Spans bleiben unverändert. Badge
  (`.eig-leiste-mods`) zeigt keine nackte Summe mehr, sondern den Geltungsbereich
  (z. B. „−2 AT/PA/FK/INI/GE · GS −1"), sonst wirkt die Leiste über dem Talente-Tab, als gälte der Abzug dort.
- **T2 — GS/INI sind Anzeige, keine Probe.** GS −1 und INI −2 werden angezeigt, nicht in die Würfelmathe
  verdrahtet (das Würfelpanel kennt keine INI-Probe).
- **T3 — Trennung im UI.** Wund-Malus (belegt) und Zustände (teils Hausregel) verschwinden nicht mehr
  in einer Summe. Unbelegte Chips behalten ihren Wert, werden aber sichtbar als Hausregel gekennzeichnet.
- **T2/T3 — Testrealität: kein JS-Runner.** Python-Tests können nur Struktur scannen
  (`tests/test_static_js.py`-Muster). Der Korrektheitsnachweis ist die Browser-Runde in T6 mit
  **abgelesenen Werten**. Struktur-Scans halten fest, dass kein globaler Abzug zurückkehrt (Negativprobe).
- **T4 — kein Umbau.** Es gibt **keinen** Print-Block für `.nlink`/`.zfw-num`/`.zd`/`.kosten`/`.wirkung`;
  Farben fallen ungefiltert aus `base.css:386-402` durch. Vorhandener Print-Block `tabs.css:82-86`
  überschreibt nur `.spell .merk, .spell .probe` — `.merk` gibt es im Markup nicht mehr (heute `.submeta`,
  `zauber.j2:24`): toter Selektor, mitziehen. Grid `base.css:366-372` (feste `240px 38px 80px`) auf `minmax`;
  Breakpoint (`base.css:449`, 1070 px) **per Rect-Vergleich** nachmessen, nicht per `scrollWidth`.
- **T5 — fünf unabhängige Mini-Fixes.** (1) Banner `base.css:197-206` hat keine Screen-Query unter
  900 px → neue Query. (2) `base.css:736-742` verkleinert Footer-Buttons unter 480 px auf ~33 px → dort
  `min-height:44px` + `position:static`. (3) Container ist `.steiger-table` selbst (`tabs.css:431-433`,
  `overflow-x`, **kein** `max-height`) → `tabindex="0"` + `role`/`aria-label`; der „auswählen"-Hinweis
  entsteht in `steigern.js:337`. (4) `.inv-add-input:first-child` (`tabs.css:447-450`) → Klasse,
  Markup `inventar.j2:72-75`. (5) Summary `base.css:405-411` (10 px, `padding:2px 0`) im Kompaktlayout auf
  44 px — Muster: `.spell-sort-btn` (`base.css:452`, Test `test_rendering.py:422`).
- **Process:** Briefs von Hand unter `.superpowers/sdd/sprint-019/` (sdd-Workspace leitet den Pfad aus dem
  Basename `plan` ab → Kollision zwischen Sprints). Subagenten committen nicht zuverlässig und fassen
  Tracker an → nach jedem Task `git status`/`git show`; Briefs mit expliziter `git add`-Liste
  (`.obsidian/workspace.json`, `Welcome.md` sind dauerhaft dirty). Verifikations-Agenten: **Nur-Lesen-Liste**
  (served-Modus schreibt in den Vault zurück).

## Out of Scope

- **D-045** (Chronik-Druck) — bleibt im Backlog, unverändert.
- **Optionale LE-Schwellen** (`kampfregeln.md:78-81`) — vom User abgewählt; Talent-/Zauberproben bleiben
  bei schwerer Verletzung bewusst unmodifiziert.
- **Wundschwellen-Berechnung im Dashboard** (WS = KO/2, Staffelung, Eisern/Glasknochen/TP(A)/Gezielter
  Stich) — das Dashboard zählt Wunden, berechnet sie nicht. Notiz in der Handoff.
- **Zonenwunden / Trefferlokalisierung** (WdS S. 107 ff.) und die optionale Schmerz-Regel
  (`kampfregeln.md:260-261`).
- **B-013** (Zauberartikel-Frontmatter, 103/268) — eigener Wiki-Sprint.
- **Vorschau für Rituale/SF**, `.playwright-mcp/`-Gitignore-Zeile, übrige Punkte aus Sprint-017/018-Handoff.

## Verifikation

1. `pytest` aus `helden/_tools/` — Baseline **333 grün**, neue Tests additiv, auch mit `-W error`.
2. `python render-held.py illaen-baernhold` → exit 0; Größe gegen 434 KB (erwartet ±0).
3. **Browser, eine Runde für alle drei EPICs** (Playwright, served + Static über `http.server`):
   - **D-041:** 0 → 2 Wunden. Abgelesen: GE-Span ändert sich (`GE 13→9`), MU/KL/IN/CH/KO/FF/KK
     **unverändert**; Würfelpanel AT/PA −4, Talent- und Zauberprobe **0**, Eigenschaftsprobe nur bei GE −4;
     Badge nennt Geltungsbereich; Zustands-Chip an/aus wirkt nur wie in T1/T3 festgelegt. Werte als Tabelle in die Handoff.
   - **D-046:** Print-Emulation — die fünf Selektoren dunkel auf Papier (Kontrast ≥ 4,5:1 **gemessen**);
     Grid bei 1071/1100/1130 px per `getBoundingClientRect`-Vergleich Zelle vs. `.spell`-Box: kein Überstand.
   - **D-044:** bei verifiziertem `innerWidth === 400`: Banner-Titel vollständig, Footer-Buttons ≥ 44 px und
     nicht mehr über dem Inhalt, Summary „▸ Artikel" ≥ 44 px, Steigern-Container per Tab fokussierbar und mit
     Pfeiltasten scrollbar; alle 8 Tabs weiterhin `scrollWidth == clientWidth`.
4. `git status --short`: **keine** Änderung unter `abenteuer/` oder `helden/illaen-baernhold/`; `wiki/` nur T1
   (`grundregeln/zustaende.md`, `_grundregeln.md`, `_master-index.md`).
5. Gesamt-Review (Opus) über den Sprint-Diff; triviale Funde direkt vom Controller fixen.
