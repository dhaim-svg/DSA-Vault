# Sprint 021 — Frontmatter-Reparatur, Footer-Fix, SF-Artikelvorschau

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`backlog.md` B-013 + `BACKLOG.md` D-049/D-050 → in-progress, plan.md anlegen) | ✅ done | backlog.md, BACKLOG.md, sprints/sprint-021/plan.md |
| T1 | **B-013a** — Frontmatter reparieren: 103 Zauber + 1 goetter-Datei quoten, Konvention dokumentieren, Verifizierer anlegen | ⬜ todo | wiki/dsa-4.1/zauber/*.md, wiki/dsa-4.1/goetter/bund-wahren-glaubens.md, raw/pdf-extracted/EXTRACTION-PLAN.md, raw/pdf-extracted/_tools/check-frontmatter.py, wiki-luecken.md |
| T2 | **B-013b** — Fallback-Parser + zugehörige Tests entfernen | ⬜ todo | parsers/wikiartikel.py, tests/test_wikiartikel.py |
| T3 | **D-049** — Desktop-Footer über dem offenen Würfelpanel | ⬜ todo | static/base.css, tests/test_rendering.py |
| T4 | **D-050** — Artikelvorschau für Sonderfertigkeiten (inkl. `WIKILINK_RE`-Fix für `[…]`-Anker) | ⬜ todo | parsers/wikiartikel.py, parsers/held.py, rendering.py, templates/partials/zauber.j2, templates/partials/_artikel.j2 (neu), static/*.css, tests/test_wikiartikel.py, tests/test_held.py, tests/test_rendering.py |
| T5 | Verifikation (Suite ×2 inkl. `-W error`, Static-Render, Browser-Runde, Gesamt-Review) + `/sprint-wrap` | ⬜ todo | sprints/sprint-021/verification.md, output/ |

**Reihenfolge:** T1 → T2 → T4 strikt sequenziell (T2 entfernt in `wikiartikel.py`, was T4 verallgemeinert; T1 muss vor T2 liegen, sonst verlieren 10 von 25 Helden-Zaubern zwischenzeitlich ihre Vorschau). **T3 ist unabhängig** (nur CSS + Test) und darf parallel zu T1/T2 laufen.

## Key Design Decisions

**Ausgangslage (gemessen 19.09.2026):** `wiki/dsa-4.1/zauber/` 268 mit Frontmatter, 165 gültig, **103 ungültig**; `goetter/bund-wahren-glaubens.md:7` 1 weiterer; `liturgien/` 267/267 gültig. 114 betroffene Zeilen (`kosten` 99, `wirkungsdauer` 9, `reichweite` 3, `zielobjekt` 2, `zauberdauer` 1) — alle einzeilige Top-Level-Skalare, keine Block-Scalars, keine Wikilinks, kein `#`.

**T1 — Reparatur**
- Rezept je Zeile im Frontmatter-Block: `^(key): (.+)$`, **nur** nicht eingerückte Zeilen (`merkmale:`-Liste und `repräsentationen:`-Map bleiben unberührt). Wert enthält `": "` und ist **nicht bereits quotiert** → in doppelte Quotes.
- **Hazard:** `zauber/destructibo.md:11` ist bereits quotiert und enthält intern `: ` — nicht doppelt quoten. Werte mit `"` im Inhalt: nach YAML-Regeln escapen (`\"`) oder Single-Quotes.
- **Pseudo-Maps bleiben Strings** (`hexenspeichel.md:9`, `manifesto-element.md:13`, `projektimago-ebenbild.md:12`): echte YAML-Maps würden `META_FIELDS`/`_text()` brechen (`wikiartikel.py:145` erwartet Skalare). *(User-Entscheidung 19.09.2026)*
- **Verifikation = Round-Trip-Diff:** für jede der 104 Dateien muss der per `yaml.safe_load` gelesene Wert stringgleich zur Ausgabe des alten `_fallback_frontmatter()` sein. `git diff --stat` darf nur die 114 erwarteten Zeilen zeigen (kein Body, keine Zeilenenden).
- Reparaturskript = Einweg-Werkzeug → **Scratchpad, nicht ins Repo.** Dauerhaft bleibt nur `raw/pdf-extracted/_tools/check-frontmatter.py` (read-only Verifizierer über `wiki/`, Exit ≠ 0 bei ungültigem YAML).
- Konvention in `EXTRACTION-PLAN.md`: „Frontmatter-Werte mit `: ` immer quoten." `wiki-luecken.md` **L22** auf erledigt.

**T2 — Entfernen**
- Weg: `_FALLBACK_KEY_RE` (`:23`), `_fallback_frontmatter()` (`:99–114`), `try/except yaml.YAMLError`-Umweg in `_read_article()` (`:121–127`). **Bleibt:** `_short()` (`:92`), wird auch von `_load_one()` gebraucht.
- Tests `test_wikiartikel.py:411–500` (9 Stück) entfallen; ersetzt durch **einen** Test: defektes YAML → kein Artikel + `log.warning` (bisher nur `log.debug`). Verhalten wird bewusst strenger.
- Testsuite arbeitet auf synthetischem Temp-Vault — keine Kopplung ans echte Wiki.

**T3 — D-049**
- Ursache ist eine Stacking-Kollision: `#footer-bar` (`base.css:733`, `fixed; bottom:28px; z-index:100`) liegt unter `.dice-panel` (`tabs.css:246`, `fixed; bottom:0; z-index:200`).
- Fix: `#footer-bar { bottom: calc(28px + var(--dice-panel-h, 0px)); }` — **keine JS-Änderung**, `dice.js:549` setzt `--dice-panel-h` schon media-query-unabhängig.
- Zwei Assertions ziehen mit: `test_rendering.py:750` (Footer-Block wörtlich) und `:903` (`--dice-panel-h` **ausschließlich** im ≤ 480-px-Block).
- ≤ 480 px unberührt (`position:static`, D-047); Druck unberührt (`.screen-only`).

**T4 — D-050**
- Wiederverwendung: `_resolve_article()` schneidet den Anker bereits ab (`wikiartikel.py:37`); für den Abschnittsschnitt taugt `split_sections(text, 2)` (`held.py:154`) direkt — Heading-Text **ist** der Ankertext.
- `load_zauber_artikel` → generisches `load_wiki_artikel`; bei `pfad#anker` nur den passenden `##`-Abschnitt laden. Anker nicht gefunden → kein Eintrag + Warnung.
- `<details class="artikel-details">`-Block (`zauber.j2:40–55`) → Makro `partials/_artikel.j2`, aufgerufen von Zauber- **und** SF-Liste. `{{ art.html }}` bleibt bewusst unescaped (mistune `escape=True`, Template-Env `autoescape=False`).
- **Mini-Bug mit erledigt:** `WIKILINK_RE` (`held.py:6`) matcht `sonderfertigkeiten.md:25/26` nicht (Anker `[einzelnes Merkmal]` enthält `]`) → `wiki_path = None`. Regex breit genutzt → eigene Tests in `test_held.py`.
- Erwartet: 15 von 17 SF-Zeilen mit Vorschau (Astrale Regeneration I/II haben keinen Link).

**Prozess:** SDD + zwei-stufige Review je Feature-Task; Briefs/Ledger von Hand unter `.superpowers/sdd/sprint-021/`; Reviewer: Verdikt zuoberst, < 3500 Zeichen, Vollbericht in Datei; Minors < 10 Zeilen inline (ein Polish-Commit, Mutationsprobe je Assert); nach Subagenten `git status`/`git show` prüfen, Controller-Commits pfadbegrenzt; geänderte Dateien auf Byte 0x08/0x0C scannen.

## Out of Scope

- **Ritual-Artikelvorschau** — L/blockiert: `rituale.md` liefert keine `wiki_path`-Links, `rituale/stabzauber.md` hat keine Heading je Stabzauber.
- **B-015** (Test-Helfer → `tests/jsfixtures.py`) — lohnt beim nächsten JS-Test.
- **B-016** (`.gitattributes` `* text=auto`) — bewusst verschoben *(User-Entscheidung 19.09.2026)*: Zeilenend-Normalisierung neben einem 104-Dateien-Wiki-Commit macht den Diff unlesbar.
- **Zustände: optionale LE-/AU-Mali** — vom User zweimal abgewählt.
- **Echter `PATCH`-Pfad / echte Druckvorschau** — Verifikation bleibt Static + `http.server` und `emulate_media: print`.
- Rituale haben generell **kein Frontmatter** (13 Dateien) — eigenes Thema, nicht B-013.
