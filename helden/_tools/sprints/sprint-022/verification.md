# Sprint 022 — Verifikation

Stand: HEAD `5e329e2` (vor den Sprint-Doku-Commits), 2026-09-20.

## Tests

- **464 passed** (Sprint-021-Stand 429: +4 T2 Wikilink-Tests, +24 T4 `stabzauber.md`-Test (parametrisiert), +7 Polish `test_jsfixtures.py`; T3 neutral).
- Lauf 1 normal, Lauf 2 `python -m pytest -W error` — **beide nach Löschen aller `__pycache__`** (`-W error` ist nur mit frischem Bytecode aussagekräftig). Beide 464 passed, ~12 s.
- **Mutationsproben (Datei danach per Hash byte-genau zurück):**
  - T2: alte Regex → neue Wikilink-Tests rot (Tests 1, 2, 4 und der geschärfte Test 3).
  - T3: Klammerzählung (Off-by-one, Tiefe) → Aufrufer rot; Artikel-Template mutiert → entkoppelte Render-Tests rot (`task-3-report.md`).
  - T4: `##` → `###`, Überschrift umbenannt, `---` eingefügt → Test rot (`task-4-report.md`).
  - Polish: 7 Mutationen (Body off-by-one, kein returncode-Assert, kein `map(str)`, Namenspräfix trifft, unbalanced ohne Assert, `fehlt`-Assert weg, alte Wikilink-Regex) → jeweils rot.

## Wiki / Render

- `python raw/pdf-extracted/_tools/check-frontmatter.py` → 828 Dateien, 682 mit Frontmatter, **0 fehlerhaft**.
- **Static-Render** (`render-held.py illaen-baernhold`): vor T4 byte-identisch zum getrackten `output/…html`; nach T4 unterscheiden sich genau die **8 Zeilen** des Horriphobus-Blocks (`**1 ZfP***` als Rohtext → `<strong>1 ZfP*</strong>`); nach den T4-Review-Fixes/Polish erneut gerendert: unverändert (`git status` leer).
- Abschnittsliste `stabzauber.md`: 11 `##` je Stabzauber; `load_wiki_artikel(…/stabzauber#<Name>)` liefert je Anker genau einen Abschnitt ohne Warnung, ohne `<hr`.

## Repo

- `git status --short` sauber nach `.gitattributes` (Index 984× `i/lf`, 5× `i/none`, 1× `i/-text` — unverändert; Working-Tree 65× crlf / 919× lf / 1× mixed bleibt, kein `--renormalize`).
- Steuerbytes 0x08/0x0C in allen Dateien seit `81f79d7`: keine.
- **Domänen-Grenze:** nichts unter `helden/illaen-baernhold/` oder `abenteuer/`; Änderungen in `helden/_tools/tests|parsers`, `wiki/`, `wiki-luecken.md`, `output/`, `.gitattributes`, `backlog.md`.
- Push: T1 hat 16 Commits gepusht (`origin/master` = `cb4f966`); die Sprint-022-Arbeit danach liegt **lokal**.

## Browser-Runde

Entfällt bewusst: kein UI-, Template-, CSS- oder JS-Diff in diesem Sprint; einziger Render-Effekt ist die Horriphobus-Vorschau (8 Zeilen, im HTML-Diff geprüft).
