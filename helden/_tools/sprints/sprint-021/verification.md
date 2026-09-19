# Sprint 021 — Verifikation (B-013 · D-049 · D-050)

Stand: 19.09.2026, HEAD `1055b6c` (+ Wrap-Commits). Alles unten wurde gemessen bzw. ausgeführt; „nicht messbar" ist als solches markiert.

## Test-Suite

- `python -m pytest tests/ -v`: **429 passed** · `python -m pytest tests/ -q -W error`: **429 passed** (Baseline 403 → +26), beide Läufe **nach Löschen aller `__pycache__`** (frischer Compile).
- Aufschlüsselung: T2 −9 gelöschte Fallback-Tests +3 (2 neue Parametrize-Fälle, 1 Diagnose-Test) = 397 · T3 +1 = 398 · T4a +10 (`tests/test_held.py` neu) = 408 · T4b ±0 (Refactoring) · T4c +19 = 427 · Polish +1 (Leer-Abschnitt) = 428 · T4d +1 (Invariante `.sf-list > li`) = 429.
- **Negativproben:** jeder neue Test gegen den Vorzustand rot (Reports `.superpowers/sdd/sprint-021/task-{1..4}-report.md`); Mutationsproben je Task (T2 `yaml.YAMLError` aus dem `except`, T3 `calc(…)`/Panel-`bottom`, T4 Regex zurück/Abschnittsschnitt/Warnung/Makro-Aufruf, Polish 4×, T4d 2×) — alle rot, Dateien byte-genau zurück.
- **Latenter Fehler gefunden:** `parsers/held.py` `_split_table_row`-Docstring mit `\|` in normalem String → frischer Compile unter `-W error` = `SyntaxError`, vorbestehend; bisher nur vom gecachten `.pyc` verdeckt (die `-W error`-Gates früherer Sprints waren für `held.py` wirkungslos). Behoben (`r"""`, `4af7715`); zusätzlich `compile()` aller `.py` unter `helden/_tools` + `raw/pdf-extracted/_tools` mit `-W error`: sauber.
- Steuerzeichen-Scan (Bytes 0x08/0x0C) über alle geänderten Dateien: 0/0. Zeilenenden je Datei erhalten (`git diff --stat` zeigt nur Inhaltszeilen).

## Wiki (B-013)

- `python raw/pdf-extracted/_tools/check-frontmatter.py` → **828 Dateien geprüft, 682 mit Frontmatter, 0 fehlerhaft** (vorher 104 fehlerhaft: 103 `zauber/` + 1 `goetter/`), Exit 0.
- Reparatur-Commit `e715685`: 104 Wiki-Dateien, **114 Zeilen** (`kosten` 98 · `wirkungsdauer` 9 · `reichweite` 3 · `zielobjekt` 2 · `zauberdauer` 1 · `kirchenstruktur` 1), byte-genauer Vergleich: nur diese Zeilen, keine Zeilenend-Änderung, Bodies identisch; `destructibo.md` (bereits quotiert) unberührt.
- **Round-Trip** (`yaml.safe_load` neu == alter Fallback-Parser): 0 Abweichungen auf den 114 quotierten Zeilen; 2 Abweichungen an unveränderten Zeilen in `goetter/bund-wahren-glaubens.md` (`aspekte`, `farben` sind YAML-Flow-Listen, der Fallback las Strings) — das Dashboard liest beide nie; in `wiki-luecken.md` L22 ehrlich vermerkt.
- Echt-Korpus nach T2: `load_wiki_artikel` liefert 25 Zauber-Artikel, **0 Warnungen** (10 davon kamen vorher über den Fallback).

## Static-Render

- `python helden/_tools/render-held.py illaen-baernhold` → exit 0, `output/illaen-baernhold-dashboard.html` **481 537 B** (Sprint 020: 450 002 B → +31 535 B, im Wesentlichen 15 eingebettete SF-Abschnitte).
- Zählwerte: **40×** `<details class="artikel-details` (25 Zauber + 15 SF; vorher 25), 0× `<script src>`, 7× `data-wund-stat=` (unverändert), 4× `register-druckfilter`, `.sf-list > li`-Regeln im eingebetteten CSS vorhanden (7 Zeilen).
- Golden-Vergleich T4b (Rename + Makro): `cmp` vor/nach **byte-identisch**; T4c: alle 14 anderen SF-Zeilen unverändert bis auf den angehängten `<details>`-Block.

## Browser (Playwright/Chromium, Static über `python -m http.server`, nur lesend; sha256 der servierten Datei == lokal geprüft; `innerWidth` je Messreihe geprüft; Details `.superpowers/sdd/sprint-021/t5-browser-report.md`)

**Runde 1: 18 PASS / 0 FAIL nach Brief — dazu ein schwerwiegender Zusatzbefund (siehe unten). Runde 2 (nach Fix `e16d175`): 8 PASS / 0 FAIL / 0 nicht messbar.**

| Check | Gemessen |
|-------|----------|
| D-049 Footer, Panel offen @ 1280 | `--dice-panel-h` 303 px = Panelhöhe; Footer 416–469, Panel-Oberkante 497,2 → **Lücke 28,2 px** (Sprint 020: −277 px Überdeckung); `elementFromPoint` trifft alle 4 Bedienelemente im Footer. MU-Probe-Modus (237 px): Lücke 28,0 px; geschlossen: 28 px / `0px` |
| D-049 Einblenden | Footer springt bei t = 0 sofort um 303 px, das Panel gleitet ~0,2 s nach: Lücke 331 → 197 (66 ms) → 108 (101 ms) → 28 px (259 ms), **keine Überlappung** (nur ein kurzer Leerraum, kosmetisch) |
| D-049 @ 400 px | Footer statisch, Panel 237 px = `body`-padding-bottom, Footer nach Scrollen erreichbar (445–547 vs. Panel 563); alle Tabs `scrollWidth` 385 ≤ 400 |
| D-050 Inhalt | „Merkmalskenntnis: Eigenschaften/Schaden": Titel `Merkmalskenntnis [einzelnes Merkmal]`, Quelle WdZ, Stufen-Tabelle, **keine Fremdabschnitte**, Obsidian-Link mit Anker; 15 `details` als direkte `li`-Kinder (17 SF-Zeilen, „Astrale Regeneration I/II" ohne) |
| D-050 Reparierte Zauber | Kosten-Metafeld zeigt den Wert **mit** Doppelpunkt-Text unverändert |
| D-050 Layout | `<details>` in der Textspalte (x = `.sf-desc`), Abstand Beschreibung → Summary 4,0 px; Summary 44 px @ 400; Zeilen ohne/mit Vorschau `grid 14px …`, Padding 9 px, Höhen unverändert (58,3 / 82,3 px) |
| Druck-Emulation | Textfarbe rgb(26,18,8) auf Weiß **18,5:1**; Obsidian-Link/geschlossene `details` `display:none`; Zeile mit offenem Artikel `break-inside:auto`, sonst `avoid`; verschachtelte `li` `auto` |
| Konsole | nur erwartete 404 (favicon, `/mtime`), 0 JS-Fehler |

### Zusatzbefund aus Runde 1 — von Unit-Tests und allen Reviews verpasst

`.sf-list li{display:grid;grid-template-columns:14px 1fr;padding:9px 0;…}` traf auch die `<li>` der Aufzählungen **im** Artikeltext (`.artikel-body li`): der Text landete in der 14-px-Spalte und brach ~2 Zeichen pro Zeile um („Al / le / V / ol / lz…"). **14 von 15 SF-Vorschauen unlesbar**, längster Artikel (Ritualkenntnis: Gildenmagie) 7 841 px = 9,8 Viewporthöhen (1 206 Zeichen); Druckregeln gleich betroffen. Der T4-Implementierer hatte das als „schmale Karte" fehlgedeutet, alle Task-/Gesamt-Reviews prüften nur strukturell.
- **Fix** (`e16d175`, Fix-Runde 1/5): alle Zeilenregeln auf `.sf-list > li` (base.css + Druckblock tabs.css); klassenspezifische Nachfahrenregeln (`.ico`, `.sf-name`, `.sf-desc`) bleiben. Neue Invariante `test_css_sf_row_rules_only_hit_direct_li_children` (erfasst Basis-, Media- und Druckblock, seit `1055b6c` auch `::before/::after`).
- **Recheck (Runde 2, neuer Render, sha256-Präfix `32664c64`):** 97 von 97 verschachtelten `li` `display:list-item`, `grid-template-columns:none`, `padding:0`, Breite ≥ 242 px; **längster Artikel 808 px = 1,01 Viewports** (Ritualkenntnis: Gildenmagie 639 px); @ 400 px 933 px, `scrollWidth` 385, kleinste `li`-Breite 196 px; 25 Zauber-Vorschauen unverändert `list-item`; Stabzauber-Liste (`ul.sf-list`, 10 Zeilen) unverändert `grid 14px …`; Screenshot gelesen: Fließtext und Aufzählungen normal.

## Reviews

- **Task-Reviews (spec + Qualität, Sonnet):** T1, T2, T3, T4 je **Spec ✅ · Quality Approved**, 0 Critical / 0 Important; Minors je Task im Ledger gebucht → gesammelter Polish-Commit `4af7715` (inkl. `held.py`-Docstring); übrige bewusst akzeptiert (s. Handoff).
- **Fix-Runde 1 (T4d) — Re-Review (Sonnet):** **ADDRESSED · new breakage: none**; Minor (`::before/::after` in der Invariante) inline in `1055b6c` behoben, Regex-Probe 8 geflaggt / 4 ignoriert.
- **Gesamt-Review (Opus):** **Ready to merge: Yes**, 0 Critical / 0 Important, 3 Minors (→ Handoff: `WIKILINK_RE`-Härtung, Live-Vault-Kopplung der Tests, harmlos). *Läuft vor dem Browser-Fund — der Layout-Fehler entzog sich auch diesem Review (rein struktureller Diff-Review).*
- **Rulings** (Ledger `.superpowers/sdd/sprint-021/progress.md`): R1 Verifizierer-Soll 682 statt 415 · R2 Aufschlüsselung 98 + 1 · R3 T3 nicht parallel · R4 Verifizierer-Scope ganzes `wiki/` · **R5 Anker-Abschnitt: Titel = Anker, Body = Abschnitt, meta leer, kein `_split_title`** · R6 Round-Trip-Abweichung `aspekte`/`farben` akzeptiert · R7 `wiki_path`-Parameter aus `_read_article` entfernt · R8 Test `…_including_anchor` inhaltlich angepasst (Anker = Abschnitt) · R9 Final-Review-Minors nicht nachgezogen.
- **Domänen-Grenze:** Änderungen nur in `helden/_tools/`, `wiki/` (104 Dateien, B-013), `raw/pdf-extracted/` (`_tools/check-frontmatter.py`, `EXTRACTION-PLAN.md`), `wiki-luecken.md`, `backlog.md`, `output/` — **nichts** unter `abenteuer/` oder `helden/illaen-baernhold/`.

## Nicht geprüft / Grenzen

- Echter Druckdialog/PDF (Chronik- und SF-Druck nur per `emulate_media: print`, computed styles); `file://` nicht direkt; echter `PATCH`-Pfad (Static-Server, kein Flask).
- Beim Öffnen des Würfelpanels löst `dice.js` konstruktionsbedingt einen clientseitigen Auto-Wurf im Speicher aus (kein Schreibzugriff) — Panel-Messung deshalb nicht komplett „passiv".
- Kosmetik im Wiki-Inhalt: Der Horriphobus-Artikel zeigt Roh-Sternchen (`**1 ZfP***`) — Quelltext-Eigenheit, nicht Dashboard.
