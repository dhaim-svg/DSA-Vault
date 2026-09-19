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
| B-013 | wiki  | Zauberartikel-Frontmatter reparieren: 103/268 mit ungültigem YAML (unquotiertes `: `), s. `wiki-luecken.md` L22; danach Fallback-Parser im Dashboard entfernen | M |
| B-014 | tooling | `/sprint-wrap`-Kommando (`.claude/commands/sprint-wrap.md`) reparieren: (1) Phase 2 ruft `render-held.py` ohne Slug auf (Z. 32) und bricht mit Usage-Fehler ab — `python render-held.py <slug>`; (2) Phase 5 „Sprint-Nr. erhöhen“ (`{NNN}` → `{NNN+1}`) ist mehrdeutig und widerspricht `/sprint-plan` Phase 2d (N = NNN−1) und der Praxis: CLAUDE.md-Sprint-Nr. = zuletzt abgeschlossener Sprint (Wrap 019 → 19); Wortlaut klären | S |

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

---

## Icebox

_(keine)_
