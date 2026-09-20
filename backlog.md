# Backlog — DSA-Vault

> Übergreifender Aufgaben-Tracker. Priorität = Reihenfolge innerhalb Backlog (oben = höher).
> Spezialisierte Tracker bleiben separat: `wiki-luecken.md` (Wiki-Mängel mit Buchquelle) · `DSA-STATUS.md` (Buch-Extraktion).

---

## In Progress

| ID    | Kat.    | Titel | Effort |
|-------|---------|-------|--------|
| B-023 | wiki    | Freistehende Buch-Sternchen (`ZfP*`, `LkP*`, `RkP*`, `TaP*`) werden von mistune zu `<em>` gepaart und rendern die Artikelvorschau falsch (Fund Sprint 023 T3). **Sprint-025-Pre-flight am Korpus:** real 123 render-relevante Zeilen in 85 Wiki-Dateien (Roh-Stern-Zeilen gesamt 1542 in 508 Dateien, der Rest rendert korrekt); im heutigen Static-Render stehen 2 falsch gepaarte `<em>` (Artikel `metamagie`, `zauberer-steigerung`, `flim-flam`, `gardianum`) — also nicht nur präventiv. Lösungsweg (User, 20.09.2026): Parser-Vorbehandlung in `parsers/wikiartikel.py` (mistune-Inline-Regel), Wiki bleibt buchtreu unberührt | M |
| B-025 | tooling | Unit-Tests gegen Replik statt Parser (Review Sprint 024 T5): `test_inventar_model.py` `test_geld_structure`/`test_geld_fallback`/`test_gesamt_kreuzer_math` prüfen die Test-Replik `_make_geld_dict`, nicht den Parser `load_held` — nur `test_load_held_geld_integration` (seit Sprint 024 synthetisch) trifft den echten Geld-Code; vorbestehend. Umstellung auf `load_held` (Mini-Held per `write_mini_held(illaen=…)`), Replik streichen; dabei den echten `else`-Zweig (`geld` nicht-dict) und `safe_int` mit krummen Werten abdecken | S |

---

## Backlog

_(leer — B-023 und B-025 laufen in Sprint 025)_

*Session 2026-05-16: Alle ursprünglichen Backlog-Items abgearbeitet.*

---

## Done

| ID    | Kat.      | Titel                                                                                | Effort | Erledigt   |
|-------|-----------|--------------------------------------------------------------------------------------|--------|------------|
| B-024 | tooling | Test-Restkopplung II: `test_load_held_geld_integration` auf synthetischen Mini-Helden (krumme Werte, Kurs 1000/100/10/1 aus dem Parser), Kampf-Wund-Hooks Fall „mit Waffe“ synthetisch und nicht-vakuös (`_weapon_cards == 1`; die drei Live-Tests bleiben, waren aber bei 0 Waffen vakuös), rohe `.index` an den zwei benannten Stellen durch `_pos()` mit lesbarer Meldung ersetzt (übrige ~14 `.index` bewusst unverändert); +4 Tests (Sprint 024) | S | 2026-09-20 |
| B-019 | wiki | `stabzauber.md` buchgenau neu aufgesetzt (WdZ S. 105–115): 12 Rituale in 4 Gruppen inkl. Apport, Fehlwerte korrigiert (Doppeltes Maß, Schuppenhaut, Bindung, Hammer des Magus), Fassungsvermögen 24/18/15/27 statt „Vol je Holzart“, Detailregeln der 7 knappen Abschnitte inkl. Flammenschwert-Misslingens-Tabelle (L10) und Schuppenhaut-Risiko (L9), Zauberspeicher-Komplexität, Kopfblöcke als Listen; L9/L10/L24/L25 geschlossen; > 100 Werte gegen das Buch geprüft (Quelle bewusst per Parser-Fallback B-022 statt Frontmatter) (Sprint 023) | M | 2026-09-20 |
| B-020 | wiki | Rohsternchen `**…ZfP***` in 10 Artikeln escaped (39 Zeilen; Backlog nannte 3 Dateien) + 26 Tests gegen die echten Wiki-Dateien; Render-Diff = die 4 Odem-Arcanum-Zeilen; verwandtes Muster (freistehende Sterne → `<em>`) → B-023 (Sprint 023) | S | 2026-09-20 |
| B-021 | tooling | Test-Härtung: `test_steigerbar.py` auf synthetischen Mini-Helden (`tests/heldfixtures.py`), Kampf-Wund-Hooks unabhängig von der Waffenzahl, `.index`-Stellen der SF-/Zauberlisten-Tests robust, `WIKILINK_RE`-Anzeigetext verbietet `[[` (Korpus 3760 = 3760 Matches); Teil „`'---' not in lines[:-1]` lässt Rest-`---` durch“ **nicht reproduzierbar** (2× unabhängig belegt) und gestrichen; Restkopplung → B-024 (Sprint 023) | S | 2026-09-20 |
| B-022 | tooling | Quelle-Fallback im Artikelparser: fehlt `quelle` im Frontmatter, nutzt `_quelle(fm, body)` die `> **Quelle:**`-Zeile des Kopfblocks (vor dem Anker-Schnitt); 809 Wiki-Artikel geprüft, 129 mit vorher leerer Quelle jetzt gefüllt, kein bisher gefüllter Wert geändert; heute nur Vorbau (alle 40 eingebetteten Vorschauen hatten schon Frontmatter-`quelle`), Voraussetzung der Ritual-Vorschau (Sprint 023) | S | 2026-09-20 |
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
