# Backlog — DSA-Vault

> Übergreifender Aufgaben-Tracker. Priorität = Reihenfolge innerhalb Backlog (oben = höher).
> Spezialisierte Tracker bleiben separat: `wiki-luecken.md` (Wiki-Mängel mit Buchquelle) · `DSA-STATUS.md` (Buch-Extraktion).

---

## In Progress

_(keine)_

---

## Backlog

| ID    | Kat.  | Titel                                                                                                   | Effort |
|-------|-------|---------------------------------------------------------------------------------------------------------|--------|
| B-019 | wiki | `wiki/dsa-4.1/rituale/stabzauber.md` gegen WdZ S. 106–111 neu aufsetzen (`wiki-luecken.md` L24, Final-Review Sprint 022): Apport ergänzen (12 Rituale, Gruppen Meta/profan/arkan/esoterisch; „13“ ist nicht belegt — auch in `rituale/_rituale.md`), Doppeltes Maß / Schuppenhaut / Bindung des Stabes korrigieren (Fassungsvermögen statt „Vol je Holzart“), die 7 knappen `##`-Abschnitte auf Buchwerte + Detailregeln nachziehen (L9/L10/L25), Frontmatter mit `quelle` ergänzen (sonst leere Quelle in Anker-Vorschauen), Fettwert-Zeilen als Liste; Voraussetzung der Ritual-Vorschau (L25) | M |
| B-020 | wiki | Rohsternchen `**…ZfP***` in `zauber/odem-arcanum.md` (Z. 35–38), `alchimie/alchimie-grundregeln.md` (Z. 123), `alchimie/artefakt-herstellung.md` (Z. 89) escapen (Muster wie Horriphobus, Sprint 022: `**N ZfP\***`); danach Static-Render auf erwarteten Render-Diff prüfen, falls der Artikel im Bogen verlinkt ist | S |
| B-021 | tooling | Test-Härtung / Restkopplung (Final-Review Sprint 022): `test_render_kampf_tab_has_wund_stat_hooks_for_wound_stats` pinnt genau 1 Waffenkarte im echten Bogen, `test_steigerbar.py` 7× `load_held` live, `test_rendering.py` (~Z. 583) hängt an der Reihenfolge Zauberliste→SF-Karte (`ValueError` bei Umbau), `test_wikiartikel.py` (~Z. 868) `'---' not in lines[:-1]` lässt ein Rest-`---` als letzte Zeile durch; dazu `WIKILINK_RE`-Anzeigetext-Gruppe `([^\]]+)` akzeptiert weiterhin `[[` (im Korpus kein Fall) | S |

*Session 2026-05-16: Alle ursprünglichen Backlog-Items abgearbeitet.*

---

## Done

| ID    | Kat.      | Titel                                                                                | Effort | Erledigt   |
|-------|-----------|--------------------------------------------------------------------------------------|--------|------------|
| B-001 | dashboard | Talent-Tabelle: Eigenschafts-Kürzel kontrastreicher                                  | S      | 2026-05-16 |
| B-002 | held      | zauber.md: Spalten ZD/Kosten/Wirkung/Mods für alle Zauber                           | M      | 2026-05-16 |
| B-003 | dashboard | Zauber-Tabelle: neue Spalten im Parser + Template                                    | S      | 2026-05-16 |
| B-004 | held      | rituale.md: Volumen-Spalte + Zauberspeicher-Inhalt                                   | S      | 2026-05-16 |
| B-005 | dashboard | Stabzauber: Volumen-Badge + Zauberspeicher-Card                                      | S      | 2026-05-16 |
| B-006 | held      | sonderfertigkeiten.md: Per-Zeile-Wikilinks                                           | S      | 2026-05-16 |
| B-007 | dashboard | SF-Liste: Wikilinks klickbar (obsidian://)                                           | S      | 2026-05-16 |
| B-008 | wiki      | Magische SF: Anker-Links einführen (broken Anchors gefixt)                           | M      | 2026-05-16 |
| B-009 | dashboard | Wiki-Links auf obsidian://-URLs umschreiben                                          | S      | 2026-05-16 |
| B-010 | meta      | Backlog-System einführen: backlog.md + CLAUDE.md                                     | S      | 2026-05-16 |
| B-011 | held+dash | Spontane Modifikationen: Referenztabelle + Dashboard-Card                            | S      | 2026-05-16 |
| B-012 | dashboard | Interaktives Dashboard Phase 1: Flask-Server, PATCH-API, LeP/AsP/AuP-Steppers, session.js | L | 2026-05-30 |
| B-014 | tooling   | `/sprint-wrap` repariert: Render-Aufruf mit Helden-Slug, Sprint-Nr.-Wortlaut („= zuletzt abgeschlossener Sprint“, nicht erhöhen), Phase 3a entfernt EPICs aus `## In Progress` | S | 2026-09-19 |
| B-013 | wiki | Zauberartikel-Frontmatter repariert: 104 Artikel (103 Zauber + `goetter/bund-wahren-glaubens.md`, 114 Zeilen) quotiert, Round-Trip gegen den Fallback-Parser 0 Abweichungen auf den Zeilen; `raw/pdf-extracted/_tools/check-frontmatter.py` (wiki/ 682 Artikel, 0 Fehler), Konvention in `EXTRACTION-PLAN.md`, `wiki-luecken.md` L22 ✅; Fallback-Parser im Dashboard samt 9 Tests entfernt (Sprint 021) | M | 2026-09-19 |
| B-015 | tooling   | Test-Helfer dedupliziert: `tests/jsfixtures.py` (`needs_node`, `js_function`/`js_function_body`, `run_node`; 4 Kopien Funktionsextraktion + 6 node-Aufrufe — die drei Runner-Skripte unterscheiden sich echt und bleiben) + SF-/Artikel-Render-Tests auf synthetischen Vault umgestellt (ein Live-Smoke-Test bleibt); `test_jsfixtures.py` 7 Tests, Mutationsprobe je Assert (Sprint 022) | S | 2026-09-20 |
| B-016 | tooling   | `.gitattributes` `* text=auto` (ohne `--renormalize`; Index war schon durchgängig LF, `git status` blieb sauber) — Repo-Hygiene damit abgeschlossen (Sprint 022) | S | 2026-09-20 |
| B-017 | tooling   | `WIKILINK_RE` verbietet `[[` im Pfad (einzelnes `[` bleibt erlaubt); 4 Tests, Korpus-Gegenprobe 3718 = 3718 Matches (einzige Abweichung: ein Prosa-Handoff mit literalem `[[`) (Sprint 022) | S | 2026-09-20 |
| B-018 | wiki      | `stabzauber.md`: `##`-Abschnitt je Stabzauber (11) + Test als Voraussetzung der Ritual-Vorschau; Horriphobus-Stern escaped (Vorschau zeigte Rohtext); `wiki-luecken.md` L24 (Tabelle weicht vom Buch ab, Apport fehlt, „13“ nicht belegt) + L25 (Voraussetzungen, Namensabgleich Held↔Wiki); `helden/…/rituale.md` unberührt (Sprint 022) | S | 2026-09-20 |

---

## Icebox

_(keine)_
