# Sprint 022 — Hygiene-Sprint: Regex-Härtung, Test-Fundament, Wiki-Vorbereitung, Repo-EOL

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`backlog.md` B-015…B-018 → In Progress, plan.md anlegen) | ⬜ todo | backlog.md, sprints/sprint-022/plan.md |
| T1 | Push-Gate (Controller): `git push origin master` — 15 Altlast-Commits sichern, bevor T5 Zeilenenden anfasst | ⬜ todo | — |
| T2 | **B-017** — `WIKILINK_RE` härten: `[[` im Pfad verbieten, Tests für unabgeschlossenes `[[` vor einem echten Link | ⬜ todo | parsers/held.py, tests/test_held.py |
| T3 | **B-015** — `tests/jsfixtures.py` (`needs_node`, `js_function`, Fake-DOM-Runner) + Live-Vault-Kopplung der Render-Tests auf synthetische Fixtures | ⬜ todo | tests/jsfixtures.py (neu), tests/test_rendering.py, tests/test_register.py, tests/test_wundregeln.py |
| T4 | **B-018** — `stabzauber.md`: `##` je Stabzauber; Horriphobus-Sternchen entschärft; `wiki-luecken.md`-Einträge | ⬜ todo | wiki/dsa-4.1/rituale/stabzauber.md, wiki/dsa-4.1/zauber/horriphobus-schreckgestalt.md, wiki-luecken.md |
| T5 | **B-016** — `.gitattributes` mit `* text=auto` (ohne `--renormalize`), danach `git status` sauber | ⬜ todo | .gitattributes (neu, Vault-Root) |
| T6 | Verifikation + `/sprint-wrap` | ⬜ todo | sprints/sprint-022/verification.md, handoff.md |

## Key Design Decisions

- **User-Entscheidungen (2026-09-20):** alle vier Items rein · B-018 fasst nur `wiki/` an (`helden/…/rituale.md` unberührt) · die 15 lokalen Commits werden vor der EOL-Änderung gepusht.
- **T2:** Regex `(?:[^\]|\\\[]|\[(?!\[)|\](?!\]))+` — einzelnes `[` bleibt erlaubt (`[[b#X [y]|B]]`), nur `[[` terminiert. Regex-Literale nicht per Bash-Heredoc übergeben (Write-Tool); EOL von `held.py`/`test_held.py` vorher prüfen (CRLF-Bestand).
- **T3:** reiner Test-Refactor, kein Produktionscode-Diff. `js_function` ersetzt `_js_function` und `_function_body`. Render-Tests gegen synthetische Fixtures; **genau ein** Live-Smoke-Test (`test_build_context_has_wiki_artikel_from_live_vault`) bleibt, ohne Zusicherungen über einzelne SF-Zeilen. `test_steigerbar.py` (7× `load_held` live) wird nur protokolliert.
- **T4:** `##` je Stabzauber (Loader kennt nur Level 2); Übersichtstabelle bleibt, die vier `### … — Vollständige Regeln` wandern in ihre `##`-Abschnitte. Widerspruch „13 Rituale" vs. 11 Namen + Doppelzeile → `wiki-luecken.md` mit Buchquelle, nicht raten. Horriphobus: `**1 ZfP***` → Sternchen escapen. Static-Render muss vor/nachher byte-identisch bleiben (`cmp`).
- **T5:** zuletzt, isoliert, eigener Commit. Schreibt `text=auto` unerwartet Dateien um → Commit verwerfen, Befund ins Handoff.
- **Prozess:** SDD mit zwei-stufiger Review je T2–T5; T1 + triviale Minors macht der Controller. SDD-Dateien von Hand unter `.superpowers/sdd/sprint-022/`; Reviewer-Verdikt zuoberst, < 3500 Zeichen; nach jedem Implementierer `git show --stat HEAD` prüfen.

## Out of Scope

- **Neue Dashboard-EPICs** — Backlog leer; Kandidaten (Footer-Einblenden glätten, echter PATCH-Pfad im Browser, LE-/AU-Mali) gehören in ein Brainstorming.
- **`helden/illaen-baernhold/rituale.md`** — User-Domäne, bewusst unberührt.
- **Ritual-Vorschau selbst** (M–L) — erst nach B-018 + Bogen-Anker möglich.
- **`test_steigerbar.py`-Live-Kopplung** — nur protokolliert.
- **`###`-/Blockreferenz-Anker im Loader**, Wundschwellen/Zonenwunden, `.journal-readonly`-Kontrast, Sichtung der vier Sessions — offen aus Sprint 017–021.
- **Browser-Runde** — entfällt, kein UI-Diff.
