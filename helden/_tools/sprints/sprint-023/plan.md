# Sprint 023 — Wiki-Genauigkeit, Quellen-Fallback & Test-Härtung

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`backlog.md` B-019…B-021 → In Progress, B-022 neu, plan.md anlegen) | ✅ done (`bd4f364`, Plan-Korrektur `78a9e1c`) | backlog.md, sprints/sprint-023/plan.md |
| T1 | **B-019a** — `stabzauber.md` Gerüst gegen WdZ S. 106–111: 12 Rituale in vier Gruppen (Meta/profan/arkan/esoterisch), **Apport** ergänzen, Fehlwerte korrigieren (Doppeltes Maß, Schuppenhaut, Bindung), Fassungsvermögen statt „Vol je Holzart“, Fettwert-Blöcke als Liste, L25(c)-Namensabgleich bestätigen | ✅ done (`8cd44de`) | wiki/dsa-4.1/rituale/stabzauber.md, wiki/dsa-4.1/rituale/_rituale.md, wiki-luecken.md (L24), tests/test_wikiartikel.py |
| T2 | **B-019b** — Detailregeln für die sieben knappen `##`-Abschnitte inkl. Flammenschwert-Misslingenstabelle (**L10**) und Schuppenhaut-Risikomechanik (**L9**), Minor-Funde M1–M4 des T1-Reviews | ✅ done (`87119f9`) | wiki/dsa-4.1/rituale/stabzauber.md, wiki-luecken.md (L9/L10/L25), tests/test_wikiartikel.py |
| T3 | **B-020** — `**… ZfP***` escapen (Muster Horriphobus: `**… ZfP\***`) in **10** Dateien (39 Zeilen); Render-Diff = 4 Odem-Arcanum-Zeilen | ✅ done (`8cd062f`) | wiki/dsa-4.1/… (10 Dateien), tests/test_wikiartikel.py, output/*.html |
| T4 | **B-022** — Quelle-Fallback im Artikelparser (Kopfblock-Zitatzeile bei leerem Frontmatter-`quelle`, vor dem Anker-Schnitt) + 23 Tests; Render byte-identisch | ✅ done (`2556bd4`) | parsers/wikiartikel.py, tests/test_wikiartikel.py |
| T5 | **B-021** — Test-Härtung: `test_steigerbar.py` synthetisch (`tests/heldfixtures.py`), Kampf-Wund-Hooks waffenzahl-unabhängig, `.index`-Härtung, `WIKILINK_RE`-Anzeigetext; Teil „Rest-`---`“ nicht reproduzierbar | ✅ done (`270bae4`, `939ca0e`, `75f9312`) | tests/test_rendering.py, tests/test_steigerbar.py, tests/heldfixtures.py (neu), tests/test_held.py, parsers/held.py |
| T6 | **L25(b)** — 9 Anker-Links in `helden/illaen-baernhold/rituale.md` (User-Domäne, für diesen Sprint freigegeben) + Konsistenztests (synthetisch + ein bewusst live gekoppelter) | ✅ done (`4f289aa`) | helden/illaen-baernhold/rituale.md, tests/test_held.py, tests/test_wikiartikel.py |
| T6b | Polish (Controller inline): 9 Minor-Funde der Task-Reviews T1–T4/T6 | ✅ done (`7fa707e`) | stabzauber.md, wiki-luecken.md, rituale.md, tests/test_wikiartikel.py |
| T7 | Verifikation (`verification.md`), Gesamt-Review + Fixes (`4698da1`), Tracker (`backlog.md`); `/sprint-wrap` (handoff.md, CLAUDE.md → 23) | 🟡 Verifikation ✅, Wrap offen | sprints/sprint-023/verification.md, handoff.md, backlog.md, CLAUDE.md |

## Key Design Decisions

- **User-Rulings (2026-09-20):** Scope = B-019 + B-020 + B-021 (kein neues Dashboard-Feature) · B-019 in voller Tiefe (Werte **und** Detailregeln → schließt L9/L10/L24/L25a) · Anker-Links in `helden/illaen-baernhold/rituale.md` freigegeben (einmalig, eigener Task nach B-019).
- **Rohquelle dreispaltig:** `raw/pdf-extracted/wege-der-zauberei/kapitel-09-rituale.txt` (Stabzauber ≈ Z. 185–540), Spaltenoffsets wechseln je Seite (gemessen 0 / 48–52 / 93–100). Kein Fixed-Offset-Parsing; T1 erzeugte ein spaltenrekonstruiertes Transkript (git-ignoriert, `.superpowers/sdd/sprint-023/wdz-stabzauber-transkript.txt`), das T2 und alle Reviewer als Grundlage nutzten; jede übernommene Zahl mit Rohzeile belegt.
- **Die elf `##`-Überschriften blieben wortgleich** (`STABZAUBER_NAMEN`, Anker-Ladbarkeit, Held-Links); Apport kam als 12. Abschnitt dazu, Regeltext bleibt in `rituale-grundregeln.md#Apport` (Zeiger statt Doppelpflege).
- **Kein Frontmatter für `stabzauber.md`** (Ordner-Konvention: Kapitelartikel = Zitatblock). Stattdessen T4: `> **Quelle:**`-Zeile als Fallback für `_quelle(fm, body)`.
- **Korrektur nach Messung (Sprint 023 Start):** Die Plan-Aussage „behebt die leere Quelle auch für die 15 SF-Anker“ war falsch — 40/40 Vorschauböcke der Golden-Baseline trugen `artikel-quelle` (die SF-Gruppenartikel haben Frontmatter `quelle: WdZ`). T4 blieb (User-freigegeben; 129 von 809 Wiki-Artikeln haben leere Frontmatter-Quelle, darunter alle `rituale/*` — Voraussetzung der Ritual-Vorschau D-051), ist aber ein reiner Parser-Vorbau ohne Render-Wirkung.
- **Render-Erwartung je Task (Golden-Baseline `bd4f364`):** T1/T2 kein Diff · T3 Diff nur Odem-Arcanum-Block (4 Zeilen) — **eingetreten** · T4 kein Diff — **eingetreten** · T5, T6 kein Diff — **eingetreten** (T6: `load_held(...)['rituale']` vorher/nachher identisch).
- **T6 fasst keine Spielwerte an:** nur die Namensspalte wurde `[[wiki/dsa-4.1/rituale/stabzauber#<Wiki-Name>\|<Heldenbezeichnung>]]`; leere Zellen der Zeile „Stabverlängerung“ blieben leer.
- **Prozess:** SDD mit Task-Reviews (spec + quality, Sonnet), Gesamt-Review Opus; Briefs/Ledger von Hand unter `.superpowers/sdd/sprint-023/` (Basename-Kollision `plan.md`); Reviewer-Verdikt zuoberst, < 3500 Zeichen; Controller-Commits pfadbegrenzt; nach jedem Commit `git show --stat HEAD` gegen erwartete Dateizahl.

## Out of Scope

- **D-051 Ritual-Artikelvorschau** im Dashboard (Zauber-Tab, analog D-050) — eigener Sprint, technisch startklar (L25 ✅).
- **Kugelzauber-Detailregeln** (WdZ S. 111 ff.) und der Rest der Kristallkugel-Abschnitte.
- **Spielwerte im Heldenbogen** (Erschaffungsprobe/AsP „Stabverlängerung“, gewähltes Merkmal des Merkmalsfokus) — User-Entscheidung.
- Footer-Transition (Sprint 021), echter `PATCH`-Pfad im Browser, optionale LE-/AU-Mali (zweimal abgewählt).

## Ergebnis & Rulings

Suite **563/563** (auch `-W error`), Static-Render nur 4 Zeilen gegenüber der Baseline, Gesamt-Review „Ready to merge: With fixes“ (alle Funde behoben). Rulings des Controllers (Ledger `.superpowers/sdd/sprint-023/progress.md`):

- **R1** Arbeit auf `master` im Hauptarbeitsbaum, kein Worktree, kein Push. **R2** T1 erweitert `STABZAUBER_NAMEN` um Apport. **R3** T1 legt das Buch-Transkript an. **R4** Render-Baseline nach jedem render-verändernden Commit neu ziehen.
- **R5/R12** T3 scannt korpusweit und fixt alle 10 Dateien (Backlog nannte 3, Plan 4) — Kosten: größerer Diff, revertierbar. **R6** T4-Fallback liest die Quelle vor dem Anker-Schnitt.
- **R8** T4 bleibt trotz falscher Plan-Prämisse (s. o.). **R9** Browser-Runde entfällt (kein Template-/CSS-/JS-Diff). **R10** „Stabverlängerung“ → `#Doppeltes Maß` verlinkt (semantische Zuordnung, dem User zur Bestätigung vorgelegt). **R11** Brief-Punkt 12 (Minor-Funde) hat Vorrang vor älteren Verboten im T2-Brief. **R13** `<em>`-Paarung freistehender Buch-Sternchen → B-023, nicht in diesem Sprint.
- Backlog-Behauptungen, die sich beim Prüfen als falsch/anders erwiesen: „Kampf-Hooks pinnt 1 Waffenkarte“ (`kampf.j2` rendert nur die erste Waffe; rot wäre nur bei 0 Waffen), „`'---' lines[:-1]` lässt Rest durch“ (nicht reproduzierbar), „3 Rohsternchen-Dateien“ (10), „15 SF-Anker mit leerer Quelle“ (0), Alt-Regel „Erschaffungsproben um Zahl vorhandener Stabzauber erschwert“ (Ring des Lebens der Geoden, nicht Stabzauber).
