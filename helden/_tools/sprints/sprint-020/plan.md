# Sprint 020 — Druck-Konsistenz, Touch-Ziele, Chip-Entflechtung (D-045, D-047, D-048, B-014)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-045/D-047/D-048 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-020/plan.md |
| T1 | **D-045** Chronik-Druck: nur aktive Ansicht drucken, Register-Sonderregel streichen, Filter-Kopfzeile im Druck (`textContent`) | ✅ done | static/chronik.css, static/register.js, templates/partials/register.j2, tests/test_rendering.py, tests/test_register.py |
| T2 | **D-047** Touch-Ziele & Mobile-Restposten bei 400 px: Inventar-Eingaben/Button + Zustands-Chips ≥ 44 px (nur ≤ 480 px), `.codex`-Reserve bei offenem Würfelpanel (erst messen), Scroll-Hinweis/`tabindex` nur bei Überlauf, `.zfw-num` → `.spell .zfw-num` (+ `PRINT_SPELL_SELECTORS` im selben Commit) | ✅ done | static/tabs.css, static/base.css, static/steigern.js, tests/test_rendering.py |
| T3 | **D-048** Zustands-Chip-Overlay entfernen: Basiswert-Overlay nur aus Wund-Effekten, Chips wirken nur über Panel-Vorbelegung (`probeMod`); Legende anpassen | ✅ done | static/session.js, static/tabs.css / templates/partials/kampf.j2 (Legende), tests/test_wundregeln.py |
| T4 | **B-014** `/sprint-wrap`-Kommando reparieren (Render-Slug, Sprint-Nr.-Wortlaut) — inline, kein Subagent | ✅ done | .claude/commands/sprint-wrap.md, backlog.md |
| T5 | Verifikation (pytest inkl. `-W error`, Static-Render, Playwright @400 px + Druck-Emulation, Steuerzeichen-Scan, Domänen-Grenze) + Gesamt-Review, danach `/sprint-wrap` | ✅ done (Verifikation + Review + Wrap) | sprints/sprint-020/verification.md, output/ |

**Stand am Sprint-Ende (19.09.2026):** T0–T5 ✅. Commits `f7cc6a7` (T0), `bc2f3a9` (T1), `0284330` (T2), `d63a00b` (T3), `05a0cfa` + `30f2064` (T4), `ad1685a` (Review-Minors inline). 403/403 Tests (auch `-W error`), Browser 7 PASS / 0 FAIL, Gesamt-Review „Ready to merge: Yes“. Abweichung vom Plan: T3-Ursache korrigiert (`applyWundModsToProben`: `probeMod`→`attrMod`, statt „Overlay nach Effekt-Art filtern“); ungescopter Druck-Selektor `.zfw-num` stand in `tabs.css`, nicht `base.css`. Details: `verification.md`, `handoff.md`.

**Reihenfolge:** T1 → T2 → T3 sequenziell (T1/T2 fassen beide `tests/test_rendering.py` an, T2/T3
beide `tabs.css`). T4 ist unabhängig und läuft inline (Controller), z. B. vor oder nach T3.

## Key Design Decisions

Vom User entschieden (19.09.2026): Scope = D-045 + D-047 + D-048 + B-014 · Chronik-Druck =
**nur aktive Ansicht**, aktiver Register-Filter bleibt und wird im Ausdruck als Kopfzeile benannt ·
Zustands-Chips = **nur Panel-Vorbelegung** (Overlay entfällt, Wund-Overlay bleibt) · Chip-Werte
(−2/−2/−4/−2/−2) bleiben Hausregel.

- **Druck = WYSIWYG (T1).** Print-Block `chronik.css` Z. 67–84: `.chronik-view{display:block !important}`
  → `.chronik-view--active{…}`; Register-Sonderregel Z. 76 entfällt. Kopfzeile in `register.j2`
  **außerhalb** `.register-tools`, Text per `textContent` (nie `innerHTML`). `beforeprint`/`afterprint`
  in `chronik.js` bleiben unverändert — kein Filter-Reset.
- **Touch-Ziele nur im ≤ 480-px-Block (T2).** Kein globales `min-height:44px`; Desktop-Layout aus
  D-040/D-044 ist vermessen.
- **Erst messen, dann fixen (T2 Punkt 3).** `.dice-panel` hat keine feste Höhe; die 36-px-Reserve
  (`base.css` Z. 752) war geraten. Messung @400 px mit offenem Panel, dann CSS-Klasse oder
  `ResizeObserver` → CSS-Variable.
- **`.zfw-num`-Rescoping und `PRINT_SPELL_SELECTORS` (Z. 400–405) im selben Commit** — der Test
  vergleicht Selektor-Strings exakt.
- **Overlay = belegte Regel, Panel = alles (T3).** `probeMod` bleibt unverändert (Wunden + Chips);
  nur der Overlay-Pfad filtert nach Effekt-Art (`{label, wunden, mods}` vs. `{label, alle, mod}`).
  Hausregel-Kennzeichnung, Chip-Werte und `attrMod` (GE in Talent-/Zauberproben) bleiben.
- **Subagent-Driven Development** für T1–T3, zwei-stufige Review (spec + code quality). SDD-Pfade
  wegen Basename-Kollision (`plan.md`) manuell `sprint-020`-qualifiziert; Briefs/Ledger unter
  `.superpowers/sdd/sprint-020/` (git-ignoriert). Tracker-Änderungen vor Dispatch committen;
  Briefings mit explizitem `git add <Liste>` (`.obsidian/workspace.json`, `Welcome.md` bleiben dirty).
- **Nach jedem Task:** geänderte Dateien auf Bytes `0x08`/`0x0C` scannen; Reviewer-Berichte < 3500
  Zeichen mit Verdikt-Zeile zuoberst, Vollbericht in Datei.

## Out of Scope

- **B-013** (Zauberartikel-Frontmatter, 103/268 ungültiges YAML, wiki, M) — Sprint 021.
- **Optionale LE-/AU-Probenmali, Schmerz-Probe, Ängste als Schlechte Eigenschaft** (WdS S. 57/83/82,
  WdH S. 268) — vom User erneut abgewählt; dokumentiert in `wiki/dsa-4.1/grundregeln/zustaende.md`.
- **Wundschwellen-Berechnung, Zonenwunden, „Wunden ignorieren"** — weiter außerhalb des Dashboards.
- **`file://`-Direktprüfung** des Static-Renders — Playwright blockt `file:`; Verifikation über
  `python -m http.server --directory output`, nur lesend.
- **Push nach `origin`** (41+ lokale Commits) sowie `.gitignore`-Zeile für `.playwright-mcp/` und
  `.claude/settings.json` (untracked) — bleiben User-Entscheidungen.
