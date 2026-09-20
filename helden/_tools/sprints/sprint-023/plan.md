# Sprint 023 — Wiki-Genauigkeit, Quellen-Fallback & Test-Härtung

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`backlog.md` B-019…B-021 → In Progress, B-022 neu, plan.md anlegen) | ✅ done | backlog.md, sprints/sprint-023/plan.md |
| T1 | **B-019a** — `stabzauber.md` Gerüst gegen WdZ S. 106–111: 12 Rituale in vier Gruppen (Meta/profan/arkan/esoterisch), **Apport** ergänzen, Fehlwerte korrigieren (Doppeltes Maß, Schuppenhaut, Bindung), Fassungsvermögen statt „Vol je Holzart“, Fettwert-Blöcke als Liste, L25(c)-Namensabgleich bestätigen | ⬜ todo | wiki/dsa-4.1/rituale/stabzauber.md, wiki/dsa-4.1/rituale/_rituale.md, wiki-luecken.md (L24) |
| T2 | **B-019b** — Detailregeln für die sieben knappen `##`-Abschnitte (WdZ S. 108–111) inkl. Flammenschwert-Misslingenstabelle (**L10**) und Schuppenhaut-Risikomechanik (**L9**); Testliste `STABZAUBER_NAMEN` um Apport erweitern | ⬜ todo | wiki/dsa-4.1/rituale/stabzauber.md, wiki-luecken.md (L9/L10/L25a), tests/test_wikiartikel.py |
| T3 | **B-020** — `**… ZfP***` escapen (Muster Horriphobus: `**… ZfP\***`) in 4 Dateien; Render-Diff prüfen (Odem Arcanum im Bogen verlinkt → erwarteter Diff) | ⬜ todo | wiki/dsa-4.1/zauber/odem-arcanum.md, alchimie/alchimie-grundregeln.md, alchimie/artefakt-herstellung.md, magie/metamagie.md |
| T4 | **B-022** — Quelle-Fallback im Artikelparser: fehlt `quelle` im Frontmatter, wird die `> **Quelle:** …`-Zeile des Artikels genutzt (wirkt für alle Anker-Vorschauen von Kapitelartikeln) + Tests | ⬜ todo | parsers/wikiartikel.py, tests/test_wikiartikel.py |
| T5 | **B-021** — Test-Härtung: 4 live gekoppelte Stellen entkoppeln/robust machen, `WIKILINK_RE`-Anzeigetext-Gruppe | ⬜ todo | tests/test_rendering.py, tests/test_steigerbar.py, tests/test_wikiartikel.py, parsers/held.py |
| T6 | **L25(b)** — Anker-Links in `helden/illaen-baernhold/rituale.md` (User-Domäne, für diesen Sprint freigegeben) + Konsistenztest Held-Anker ↔ Wiki-Abschnitte | ⬜ todo | helden/illaen-baernhold/rituale.md, tests/test_wikiartikel.py |
| T7 | Verifikation + `/sprint-wrap` | ⬜ todo | sprints/sprint-023/verification.md, handoff.md, backlog.md, CLAUDE.md |

## Key Design Decisions

- **User-Rulings (2026-09-20):** Scope = B-019 + B-020 + B-021 (kein neues Dashboard-Feature) · B-019 in voller Tiefe (Werte **und** Detailregeln → schließt L9/L10/L24/L25a) · Anker-Links in `helden/illaen-baernhold/rituale.md` freigegeben (einmalig, eigener Task nach B-019).
- **Rohquelle dreispaltig:** `raw/pdf-extracted/wege-der-zauberei/kapitel-09-rituale.txt` (Stabzauber ≈ Z. 185–540), Spaltenoffsets wechseln je Seite (gemessen 0 / 48–52 / 93–100). Kein Fixed-Offset-Parsing; jede übernommene Zahl mit Zeilennummer belegen; Nicht-Auffindbares nicht schreiben, sondern melden.
- **Die elf `##`-Überschriften bleiben wortgleich** (`STABZAUBER_NAMEN`, Anker-Ladbarkeit, ab T6 die Held-Links). Apport kommt als 12. Abschnitt dazu, Regeltext bleibt in `rituale-grundregeln.md#Apport` (Zeiger statt Doppelpflege).
- **Kein Frontmatter für `stabzauber.md`** (Ordner-Konvention: Kapitelartikel = Zitatblock). Stattdessen T4: `> **Quelle:**`-Zeile als Fallback für `_quelle(fm)` — behebt die leere Quelle für alle Kapitelartikel-Anker (auch die 15 SF-Vorschauen), nicht nur Stabzauber.
- **Render-Erwartung je Task** (Golden-Baseline vor T1 ziehen): T1/T2 kein Diff · T3 Diff nur im Odem-Arcanum-Block (4 Zeilen fett statt roh) · T4 Diff = Quellenzeile in Anker-Vorschauen (Umfang vorher messen) · T6 **kein** Diff (`strip_wikilink()` führt Anzeigetext identisch; ein Diff wäre ein Fehler).
- **T6 fasst keine Spielwerte an:** nur die Namensspalte wird `[[wiki/dsa-4.1/rituale/stabzauber#<Wiki-Name>\|<Heldenbezeichnung>]]`; leere Zellen der Zeile „Stabverlängerung“ bleiben leer; Hinweis-Absätze nur nachziehen, wenn T1 „Doppeltes Maß“ am Buch bestätigt.
- **Prozess:** SDD mit Task-Reviews (spec + quality), Briefs/Ledger von Hand unter `.superpowers/sdd/sprint-023/` (Basename-Kollision `plan.md`); Reviewer-Verdikt zuoberst, < 3500 Zeichen; Controller-Commits pfadbegrenzt; nach jedem Commit `git show --stat HEAD` gegen erwartete Dateizahl.

## Out of Scope

- **D-051 Ritual-Artikelvorschau** im Dashboard (Zauber-Tab, analog D-050) — eigener Sprint, nach T6 startklar.
- **Kugelzauber-Detailregeln** (WdZ S. 112 ff.) und der Rest der Holzarten-Tabelle über das Fassungsvermögen hinaus.
- **Spielwerte im Heldenbogen** (Erschaffungsprobe/AsP „Stabverlängerung“, gewähltes Merkmal des Merkmalsfokus) — User-Entscheidung.
- Footer-Transition (Sprint 021), echter `PATCH`-Pfad im Browser, optionale LE-/AU-Mali (zweimal abgewählt).

## Verifikation (Kurzfassung — Details im Freigabe-Plan)

Volle Suite grün (Stand 464 + neue) auch mit `-W error` nach `__pycache__`-Löschen · Anker-Ladbarkeit aller 12 Namen inkl. nicht-leerer Quelle · Render-Diff gegen Golden-Baseline je Erwartung · `check-frontmatter.py` 0 Fehler, kein unescaptes `**… ZfP***` mehr (7 Fundstellen vorher) · `wiki-luecken.md` L9/L10/L24/L25 geschlossen · Steuerbyte-Scan · Browser-Runde (Static über `http.server`) wegen T4.
