# Sprint 025 — Buch-Sternchen, Druck-Restposten, Test-Entkopplung

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-052 → in-progress, Vault-backlog.md B-023/B-025 → In Progress, plan.md anlegen) | ✅ done | BACKLOG.md, backlog.md, sprints/sprint-025/plan.md |
| T1 | **B-023** — Buch-Notation (`ZfP*`, `LkP*`, `RkP*`, `TaP*`) im Artikelparser per Platzhalter (U+E000) neutralisieren, Funktion `render_markdown`, Tests + Korpus-Gegenprobe | ⬜ todo | parsers/wikiartikel.py, tests/test_wikiartikel.py |
| T2 | **D-052 Vermessung** — Browser-Agent misst in der Print-Emulation Ist-Kontraste und die echte Überlauf-Quelle, liefert die Selektorliste für T3 (nur lesend) | ⬜ todo | — |
| T3 | **D-052 Fix** — Druck-Regeln im `@media print`-Block nach Befund aus T2 | ⬜ todo | static/tabs.css (ggf. static/base.css), tests/test_rendering.py |
| T4 | **B-025** — Geld-Unittests auf `load_held` umstellen, Replik `_make_geld_dict` streichen | ⬜ todo | tests/test_inventar_model.py |
| T5 | Browser-Nachmessung — Druck-Emulation + Bildschirm-Regression (1280/400 px), nur lesend | ⬜ todo | — |
| T6 | Verifikation + `/sprint-wrap` | ⬜ todo | sprints/sprint-025/verification.md, Tracker |

## Key Design Decisions

- **B-023 ist nicht präventiv (Pre-flight):** der Static-Render enthält heute 2 falsch gepaarte `<em>` in den Vorschauen (`<em>/2, FK/Talent/Zauberproben um ZfP</em>`, `<em>) &gt; ZfP</em>`; Quellen: `magie/metamagie`, `magie/zauberer-steigerung`, `zauber/flim-flam`, `zauber/gardianum`). Umfang real **123 render-relevante Zeilen in 85 Dateien** (Backlog: 113/81; Roh-Stern-Zeilen gesamt 1542 in 508 Dateien — Rest rendert korrekt).
- **B-023-Lösungsweg (User-Entscheidung): Parser-Vorbehandlung**, Wiki bleibt unberührt und buchtreu. **Korrektur nach Prototyp (Ruling R2):** nicht die mistune-Inline-Regel, sondern ein **Platzhalter** — `ZfP*` (auch `LkP*`, `RkP*`, `TaP*`) wird vor dem Rendern zu `ZfP` + U+E000, nach dem Rendern U+E000 → `*`. Grund: die Inline-Regel scheitert an Zeilen mit umschließendem `*…*` (mistune konsumiert die Kursivspanne ab dem öffnenden Stern; `hindernisse.md`, `orientierung.md`). Der Platzhalter braucht keine Sonderbehandlung für Code-Spans/Fences (Rückersetzung greift dort ebenfalls); U+E000 kommt im Wiki nirgends vor (Korpus-Test sichert das).
- **Vorbehandlung als eigene Funktion `render_markdown` (Ruling R3):** die B-020-Tests (`ROHSTERN_*`) rufen bisher `_MARKDOWN` direkt auf und würden die Vorbehandlung umgehen → auf die neue Funktion umstellen (dieselbe Renderer-Konfiguration wie der Loader).
- **B-023-Abnahme am Korpus (Ruling R4):** Stern-Bilanz je Ganzdatei (Quelle: Notation mit/ohne `\` vor `*` == literale `…*` im HTML): heute **82 Dateien falsch → 0**; `<em>` im Static-Render 10 → 8, keines mit Buch-Notation; legitime Kursivschrift bleibt unverändert. Die Pflegelisten `ROHSTERN_DATEIEN`/`ROHSTERN_ZEILEN` (B-020) bleiben inhaltlich gültig (Sterne bleiben literal), nur die Aufrufstelle ändert sich.
- **D-052 — messen, dann fixen (User-Entscheidung):** die Backlog-Zuordnung des Überlaufs (881 vs. 779 px) zur Karte „Spontane Modifikationen“ ist vermutlich falsch — `.spell`-Grid-Minima summieren sich auf 878 px (`base.css:380`). T2 misst die echte Quelle vor jedem Eingriff (Static über `http.server`, freier Port, sha256, eigene PID beenden, Nur-Lesen-Liste).
- **D-052-Fix nur im `@media print`-Block** von `tabs.css`; Selektor-Falle aus D-046/D-051 (eigene Bildschirm-`color` erbt die Druckfarbe nicht, `!important` auf dem Elternselektor vererbt sich nicht auf Kind/`::after`). Ziel ≥ 4,5 : 1, realistisch `--paper-ink` 14,62 : 1. Bildschirmdarstellung bleibt unverändert (Golden-Render).
- **B-025:** `test_geld_structure`/`test_gesamt_kreuzer_math`/`test_geld_fallback` auf `load_held` via `write_mini_held(tmp_path, illaen=…)`; Replik ersatzlos streichen. Deckt zwei Lücken auf: Parser nutzt `safe_int` (Replik `int`) → Fall mit nicht-numerischem Wert; der echte `else`-Zweig (`parsers/held.py:575`) greift nur bei nicht-dict `geld` (z. B. `geld: 5`), `test_geld_fallback` läuft heute durch den ersten Zweig.
- **Prozess:** SDD, ein Implementierer je Task, zwei-stufige Review (Spec + Quality), Gesamt-Review Opus am Ende; Reviewer-Verdikt zuoberst, < 3500 Zeichen; Subagenten mit `name`; nach jedem Commit `git show --stat HEAD` gegen erwartete Dateizahl; Briefe mit expliziter `git add <Liste>` (`.obsidian/workspace.json` + `Welcome.md` dauerhaft dirty); Mutationsproben per Kopie + Hash, nie `git checkout --`; Review-Paket bei `output/*.html` von Hand ohne Render-Diff; Patchskripte mit Backslashes per Write-Datei, Byte-8/12-Scan nach jedem Task; sprint-025-qualifizierte SDD-Pfade (`.superpowers/sdd/sprint-025/`); kein Worktree, kein Push.
- **Domänen-Grenze:** Wiki, `helden/illaen-baernhold/` und `abenteuer/` bleiben unberührt (`git diff --numstat <T0> HEAD -- wiki helden/illaen-baernhold abenteuer` muss leer sein).

## Out of Scope

- **Grid-Stretch der Ritual-/SF-Karte** — in D-052 als optional geführt, Einzelöffnen ist unauffällig.
- **Wiki-Massenedit der Buch-Sternchen** — bewusst abgewählt, der Parser löst es.
- **Echter Druckdialog, `file://`, echter `PATCH`-Pfad** — weiter ungeprüft; Messungen sind Print-Emulation.
- **Deferred Minors aus Sprint 024** (Testhygiene `test_held.py`/`test_rendering.py`, ~14 rohe `.index`) — bleiben deferred.
- **Neue EPIC-Kandidaten aus dem Handoff** (Footer-Einblenden glätten, PATCH-Pfad im Browser, optionale LE-/AU-Mali) — nicht im Backlog, kein Auftrag.
- **Push nach `origin`** — 34 Commits liegen lokal, kein Auftrag.
