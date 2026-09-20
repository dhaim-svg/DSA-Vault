# Backlog — DSA-Vault

> Übergreifender Aufgaben-Tracker. Priorität = Reihenfolge innerhalb Backlog (oben = höher).
> Spezialisierte Tracker bleiben separat: `wiki-luecken.md` (Wiki-Mängel mit Buchquelle) · `DSA-STATUS.md` (Buch-Extraktion).

---

## In Progress

_Sprint 022 (Hygiene-Sprint) — B-015…B-018, Plan: `helden/_tools/sprints/sprint-022/plan.md`_

| ID    | Kat.  | Titel                                                                                                   | Effort |
|-------|-------|---------------------------------------------------------------------------------------------------------|--------|
| B-015 | tooling | Test-Helfer deduplizieren + Live-Vault-Kopplung lösen (Final-Review Sprint 020/021; Rendertests `test_render_wiki_artikel_details…`, `test_build_context_has_wiki_artikel_from_live_vault`, `_sf_context` lesen den echten Heldenbogen → synthetische Fixtures): `needs_node` (test_register/test_rendering/test_wundregeln), `_js_function` == `_function_body`, drei fast identische node-Fake-DOM-Runner → gemeinsames `helden/_tools/tests/jsfixtures.py` | S |
| B-016 | tooling | Repo-Hygiene (Final-Review Sprint 020, Sprint-019-Erbe): nur noch `.gitattributes` mit `* text=auto` offen (gemischte LF/CRLF-Working-Copies, `core.autocrlf=true`; ohne `--renormalize`, danach `git status` prüfen). Erledigt 2026-09-19: `.playwright-mcp/` in `.gitignore`, `.claude/settings.json` versioniert, `.obsidian/workspace.json` untracked + ignoriert | S |
| B-017 | tooling | `WIKILINK_RE` härten (Final-Review Sprint 021): seit dem `]`-Fix kann ein ungeschlossenes `[[` im Wiki-Body bis zum nächsten `]]` schlucken (`[[` im Pfad verbieten; Vorschlag im Sprint-021-Handoff) + Test für ein unabgeschlossenes `[[` vor einem echten Link; im Korpus aktuell kein Fall | S |
| B-018 | wiki | Ritual-Artikelvorschau vorbereiten (Sprint 021, D-050 ausgeklammert): `wiki/dsa-4.1/rituale/stabzauber.md` braucht `##`-Überschrift je Stabzauber, `helden/…/rituale.md` (User-Domäne) bräuchte Wikilinks mit Anker — als `wiki-luecken.md`-Eintrag anlegen; nebenbei Horriphobus-Artikel: Roh-Sternchen `**1 ZfP***` im Text prüfen | S |

---

## Backlog

_(keine)_

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

---

## Icebox

_(keine)_
