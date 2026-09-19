# Sprint 020 — Verifikation (D-045 · D-047 · D-048 · B-014)

Stand: 19.09.2026, HEAD `30f2064` (+ Wrap-Commits). Alles unten wurde gemessen bzw. ausgeführt; „nicht messbar" ist als solches markiert.

## Test-Suite

- `python -m pytest tests/ -v`: **403 passed** · `python -m pytest tests/ -q -W error`: **403 passed** (Baseline 379 → +24).
- Aufschlüsselung je Task: T1 +10 (`test_rendering.py` CSS-Print-Scans/Render-Position, `test_register.py` node-Fake-DOM für `register.js`), T2 +8 (`test_rendering.py`: Touch-Ziele nur im ≤ 480-px-Block, `--dice-panel-h`, Steigern-Überlauf inkl. node-Test von `syncScrollOverflow`, `PRINT_SPELL_SELECTORS`), T3 +6 (`test_wundregeln.py` 4 node-Overlay-Tests + Struktur-Test, `test_rendering.py` Legende). Node lief real (v24.13.1, kein Skip).
- **Negativproben:** jeder neue Test gegen den Vorzustand rot (Reports `.superpowers/sdd/sprint-020/task-{1,2,3}-report.md`); die vom Controller inline nachgezogenen Assertions (Commit `ad1685a`) per Mutation gegengeprüft (Leerzeichen der Legende entfernt / `observe(document.body)` / Resize-Fallback entfernt → jeweils rot).
- Steuerzeichen-Scan (Bytes 0x08/0x0C) über alle geänderten Dateien und das Render: leer.

## Static-Render

- `python render-held.py illaen-baernhold` → exit 0, `output/illaen-baernhold-dashboard.html` **450 002 B** (Sprint 019: 446 203 B → +3 799 B durch `register.js`/`chronik.css`/`dice.js`/`steigern.js`/`tabs.css`/Legende).
- Zählwerte identisch zum vorherigen Render: 25× `<details class="artikel-details`, 7× `data-wund-stat="`, 0× `computeWundPenalty`, 0× `<script src>`; neu: 4× `register-druckfilter`, 2× `sg-scroll-hint--on`, 5× `dice-panel-h`.
- Zum Wrap-Zeitpunkt: In-Memory-Render == Datei auf Platte (identisch nach Zeilenende-Normalisierung).

## Browser (Playwright/Chromium, Static über `python -m http.server --directory output`, nur lesend; `innerWidth` je Messung geprüft; Details `.superpowers/sdd/sprint-020/verification-browser.md`)

**7 PASS / 0 FAIL / 0 nicht messbar (Checks A–G).**

| Check | Gemessen |
|-------|----------|
| A Touch-Ziele @ 400 px | `.inv-add-input--name`/`--anzahl`/`.inv-add-btn` **44 px**, alle 5 `.zustand-chip` **44 px**; `scrollWidth` 385 ≤ 400 (Inventar und Kampf). @ 1280 px: 30 / 30 / 30 / 25 px → Änderung auf ≤ 480 px begrenzt |
| B Würfelpanel @ 400 px (Klettern) | `--dice-panel-h` 303 px = `body`-padding-bottom; Footer-Unterkante 581,4 px, Panel-Oberkante 597,2 px → **Lücke +15,8 px** (Vorzustand laut T2-Implementer-Messung: −175 px, Footer zu 100 % verdeckt — nach dem Fix nicht erneut messbar); Schließen → `0px`. Info @ 1280: Footer liegt 277 px **unter** dem offenen Panel (vorbestehend, nicht Teil von D-047) |
| C Steigern | @ 400 px: alle 3 `.steiger-scroll` laufen über (340/391/370 vs 283), alle mit `tabindex`/`role`/`aria-label` + sichtbarem Hinweis. @ 1280: kein Überlauf → nichts davon. Resize 1280→400→1280 folgt in beide Richtungen. *Lücke:* bei 400 px gab es keine nicht-überlaufende Tabelle (Negativfall dort nur über 1280 + node-Test belegt) |
| D Chronik-Druck (`print`-Emulation) | Genau die aktive Ansicht `block`, die beiden anderen `none` (Roh / Kompiliert / Register). Filter „Baronins": `Gefiltert nach: "Baronins" — 1/55 Einträge` (sichtbar 1, gesamt 55), `.register-tools` `none`; Filter leer → Kopfzeile `none`; auf dem Bildschirm nie sichtbar |
| E D-048 Chips | 0 Wunden + Schmerz: 0 von 203 `[data-attr]` mit `→`, `#dp-mod` −2 (Klettern). 2 Wunden (im Speicher simuliert): nur `GE 13→9` (14 Spans), 0 Pfeile auf MU/KL/IN/CH/FF/KO/KK, AT-Basis 7→3; `#dp-mod`: GE-Probe −6, MU-Probe −2, Selbstbeherrschung −2, Klettern −2 (GE dort effektiv 9) — kein Doppelzählen. Legende trägt den neuen Satz |
| F Druck-Kontrast `.spell .zfw-num` | rgb(26,18,8) auf rgb(236,228,208) = **14,62:1** |
| G Konsole | nur 39× `/api/…/mtime` 404 + 1× `favicon.ico` 404 (erwartet), 0 Warnungen, kein `PATCH` |

Randnotiz Messsetup: Auf Port 8765 lief parallel ein fremder `http.server` (PID 32384, seit 19:58, Überbleibsel der T2-Messung). Die gemessene Seite trug die Sprint-020-Merkmale und stimmte mit der Datei auf der Platte überein (Hash-Vergleich des Verifiers via `localhost`).

## Reviews

- **Task-Reviews (spec + Qualität, Sonnet):** T1, T2, T3 je **✅ Approved**, 0 Critical / 0 Important; 6 Minors → in `ad1685a` behoben.
- **Gesamt-Review (Opus):** **Ready to merge: Yes**, 0 Critical / 0 Important, 5 Minors (Disposition: 1× inline behoben `sprint-wrap.md` `-W error`; 4× → `backlog.md` B-015/B-016 bzw. Wrap-Commit).
- **Ruling 2 (Preflight):** Plan-Formulierung zu T3 („Overlay-Pfad nach Effekt-Art filtern") war unpräzise — `statMod`/`attrMod` waren schon nur-Wunden, die Doppelzählung entstand allein in `applyWundModsToProben` (`probeMod`→`attrMod`). Vom Final-Reviewer am Code bestätigt.
- **Domänen-Grenze:** Änderungen nur in `helden/_tools/`, `output/`, `.claude/commands/`, `backlog.md` — nichts unter `abenteuer/`, `helden/illaen-baernhold/`, `wiki/`, `raw/`.
