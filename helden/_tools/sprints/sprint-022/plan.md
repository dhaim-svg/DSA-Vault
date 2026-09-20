# Sprint 022 — Hygiene-Sprint: Regex-Härtung, Test-Fundament, Wiki-Vorbereitung, Repo-EOL

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`backlog.md` B-015…B-018 → In Progress, plan.md anlegen) | ✅ done (`cb4f966`) | backlog.md, sprints/sprint-022/plan.md |
| T1 | Push-Gate (Controller): `git push origin master` — 15 Altlast-Commits + T0 gesichert, bevor T5 Zeilenenden anfasst | ✅ done (`f1bf38e..cb4f966`) | — |
| T2 | **B-017** — `WIKILINK_RE` härten: `[[` im Pfad verbieten, 4 Tests | ✅ done (`be267ca`) | parsers/held.py, tests/test_held.py |
| T3 | **B-015** — `tests/jsfixtures.py` (`needs_node`, `js_function`, `js_function_body`, `run_node`) + SF-/Artikel-Render-Tests von der Live-Vault-Kopplung gelöst | ✅ done (`59aa45e`, `b8e6f14`) | tests/jsfixtures.py (neu), test_rendering.py, test_register.py, test_wundregeln.py |
| T4 | **B-018** — `stabzauber.md`: `##` je Stabzauber (11), Horriphobus-Sternchen, `wiki-luecken.md` L24/L25, 1 Test | ✅ done (`7dcc824`, `b03810f`, Review-Fix `ac91060`) | wiki/…/stabzauber.md, wiki/…/horriphobus-schreckgestalt.md, wiki-luecken.md, tests/test_wikiartikel.py, output/*.html |
| T5 | **B-016** — `.gitattributes` mit `* text=auto` (ohne `--renormalize`), `git status` sauber | ✅ done (`64095e0`) | .gitattributes (neu) |
| T5b | Polish: `test_jsfixtures.py` (7 Tests, Mutationsprobe je Assert), Wikilink-Test 3 beißt, Docstring-Vorbehalt | ✅ done (`5e329e2`) | tests/test_jsfixtures.py (neu), tests/jsfixtures.py, tests/test_held.py |
| T6 | Verifikation + `/sprint-wrap` | 🟡 Verifikation ✅ (`verification.md`), Wrap offen | sprints/sprint-022/verification.md, handoff.md |

## Key Design Decisions

- **User-Entscheidungen (2026-09-20):** alle vier Items rein · B-018 fasst nur `wiki/` an (`helden/…/rituale.md` unberührt) · die 15 lokalen Commits werden vor der EOL-Änderung gepusht.
- **T2:** Regex `(?:[^\]|\\\[]|\[(?!\[)|\](?!\]))+` — einzelnes `[` bleibt erlaubt (`[[b#X [y]|B]]`), nur `[[` terminiert.
- **T3:** reiner Test-Refactor, kein Produktionscode-Diff. `js_function`/`js_function_body` teilen eine Klammerzählung (`_locate_function`). Genau ein Live-Smoke-Test (`test_build_context_wiki_artikel_smoke_live_vault`) bleibt. `test_steigerbar.py` (7× `load_held` live) nur protokolliert.
- **T4:** `##` je Stabzauber (Loader kennt nur Level 2); die vier `### … — Vollständige Regeln` wanderten wortgleich in ihre `##`-Abschnitte.
- **T5:** zuletzt, isoliert, eigener Commit; Index war schon durchgängig LF → `git status` blieb sauber.
- **Prozess:** SDD mit Task-Reviews je T2–T4 (Sonnet), Gesamt-Review (Opus); SDD-Dateien unter `.superpowers/sdd/sprint-022/`.

## Out of Scope

- **Neue Dashboard-EPICs** — Backlog leer; Kandidaten (Footer-Einblenden glätten, echter PATCH-Pfad im Browser, LE-/AU-Mali) gehören in ein Brainstorming.
- **`helden/illaen-baernhold/rituale.md`** — User-Domäne, bewusst unberührt.
- **Ritual-Vorschau selbst** (M–L) — erst nach B-018 + Bogen-Anker möglich (L25).
- **`test_steigerbar.py`-Live-Kopplung**, **`###`-/Blockreferenz-Anker im Loader**, Wundschwellen/Zonenwunden, `.journal-readonly`-Kontrast, Sichtung der vier Sessions — offen aus Sprint 017–021.
- **Browser-Runde** — entfiel, kein UI-Diff.

## Ergebnis & Rulings

Rulings des Controllers (Kosten falls falsch: siehe Ledger `.superpowers/sdd/sprint-022/progress.md`):

- **R1** Arbeit direkt auf `master` statt Worktree (Projekt-Workflow seit Sprint 001).
- **R2** T3-Scope: die genannten Render-Tests entkoppelt; Tests, die nur die Existenz des Helden brauchen, bleiben live (Liste in `task-3-report.md`). Der Implementierer entkoppelte zwei weitere Tests mit derselben Kopplung — im Scope (Reviewer bestätigt).
- **R3** Modelle: Sonnet für T2–T4 + Task-Reviews, Opus für das Gesamt-Review; T1/T5 sowie die T4-Review-Fixes inline vom Controller.
- **R4** T3-Runner: der Backlog-Text nannte die drei node-Runner „fast identisch" — es sind drei verschiedene Skripte. Zusammengelegt wurden nur die echten Duplikate (Marker, Klammerzählung — 4 Kopien —, node-Aufruf — 6 Kopien). Weicht vom Plan-Wortlaut „gemeinsamer Fake-DOM-Runner" ab.
- **R5** T4-Akzeptanz präzisiert: Horriphobus ist ein Zauber des Helden mit Wiki-Link und wird als Vorschau eingebettet → Static-Render darf nur im Horriphobus-Block abweichen (8 Zeilen, `output/…html` mitcommittet). Vorher wurde `**1 ZfP***` als Rohtext ausgegeben, jetzt `<strong>1 ZfP*</strong>`.
- **R6** T4 nahm einen Test in `test_wikiartikel.py` auf (`##` je Stabzauber + Anker-Ladbarkeit).
- **R7** Weitere `**…ZfP***`-Fundstellen (odem-arcanum, alchimie-grundregeln, artefakt-herstellung) nicht Teil von B-018 → nur gemeldet.
- **R8** Zeilenenden: `grep -c $'\r'` lügt in dieser Shell (jede Zeile „CR"); gemessen per Python-Bytezählung, jede Datei behält ihr Ende. Briefs T2–T4 nannten teils falsche CRLF-Angaben und wurden berichtigt.
- **R9** T2-Korpusabweichung (nur ein Prosa-Handoff mit literalem `[[`) angenommen; T4-Brief-Widerspruch zum schließenden `---` zugunsten des Loaders entschieden.
- **R10** `.gitattributes` inline; Akzeptanz `git status` sauber + Index-EOL-Verteilung unverändert (984× `i/lf`).

Befunde für Sprint 023: siehe `handoff.md`.
