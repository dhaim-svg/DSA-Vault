# Sprint 024 — Ritual-Artikelvorschau (D-051) & Test-Restkopplung II (B-024)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-051 → in-progress, Vault-backlog.md B-024 → In Progress, plan.md anlegen) | ✅ done (`fd6f593`) | BACKLOG.md, backlog.md, sprints/sprint-024/plan.md |
| T1 | **Bogen-Edit (User-Domäne, freigegeben):** Namenszelle der Apport-Zeile → `[[wiki/dsa-4.1/rituale/stabzauber#Apport\|Apport]]`; Beleg per Diff + `load_held(...)['rituale']['andere']` vorher/nachher (`name` bleibt „Apport“) | ✅ done (`9b04c9d`) | helden/illaen-baernhold/rituale.md |
| T2 | **Parser:** `wiki_path` für Ritual-Zeilen (`extract_wiki_path(row['Stabzauber'])` bzw. `row['Ritual']`), `name` weiter über `strip_wikilink`; Tests über synthetischen Mini-Helden | ✅ done (`82a8654`) | parsers/held.py (~Z. 392–431), tests/test_held.py, ggf. tests/heldfixtures.py |
| T3 | **Render-Kontext:** `artikel_eintraege` um `held['rituale']['stabzauber']` + `['andere']` erweitern; Test: 10 Pfade landen in `wiki_artikel`, jeder Abschnitt nicht leer | ✅ done (`6fe96a6`) | rendering.py (~Z. 89), tests/test_rendering.py |
| T4 | **Template:** Ritual-Schleifen analog SF — Name als Obsidian-Link bei `wiki_path`, `artikel_details(art, …)` nach dem Text-`<span>`; Layout gegen die Sprint-021-Falle prüfen (nur `>`-gescopte CSS-Regeln, falls überhaupt nötig) | ✅ done (`209cbc9` + Fix-Runde 1 `8b522e5`) | templates/partials/zauber.j2 (~Z. 96–103), ggf. static/base.css, tests/test_rendering.py |
| T5 | **B-024 Restkopplung II:** `test_load_held_geld_integration` auf synthetischen Helden, Waffenkarten-Fall der Kampf-Wund-Hooks per `write_mini_held(ausruestung=…)`, rohe `.index`-Stellen in `test_rendering.py` härten | ✅ done (`ed0a51a`) | tests/test_inventar_model.py, tests/test_rendering.py, tests/heldfixtures.py |
| T6 | **Browser-Runde (nur lesend):** Static-Render über `python -m http.server --directory output` auf freiem Port, sha256 der servierten Datei prüfen, Tabellen-Vorschauen (Flammenschwert, Schuppenhaut, Hammer) + lange `.artikel-quelle` bei 1280/400 px messen, Druck-Emulation, eigene PID beenden | ✅ done (Browser-Runde; Befund → Fix `8b522e5`, Nachmessung bestanden) | — (nur Messung; Fixes ggf. static/base.css) |
| T7 | Verifikation + `verification.md` + `/sprint-wrap` | ✅ done (`verification.md`, dieser Stand, Vault-`backlog.md`) | sprints/sprint-024/verification.md, Tracker |

## Key Design Decisions

- **Wiederverwenden statt neu bauen:** Makro `partials/_artikel.j2::artikel_details` (seit D-050 mit Zauber geteilt), `load_wiki_artikel(vault_root, pfade, link_fn=obsidian_uri)` inkl. Anker-Schnitt, `extract_wiki_path`/`strip_wikilink` (`parsers/held.py` Z. 70–83). Kein neuer Lade- oder Renderpfad.
- **Ritual-Liste ist bereits eine `.sf-list`** (gleiche Grid-Struktur `ico` + Text-`span`) → `.sf-list > li > .artikel-details{grid-column:2}` und `.sf-list > li:has(> .artikel-details){row-gap:4px}` (base.css Z. 419–420) greifen unverändert. Erwartung: kein neues CSS; T6 verifiziert das, statt es anzunehmen.
- **Namenslink konsistent zu den SF:** Ritualnamen mit `wiki_path` werden zu `<a href="obsidian://…">`; Anzeigetext bleibt der Bogen-Name („Stabzauber: Fackel“, „Stabverlängerung“).
- **Erwartete Menge:** 9 Stabzauber + Apport = 10 neue Vorschauen; `class="artikel-details` 40 → **50**; Static-Render ~481 641 B → ~510 KB.
- **Bogen-Grenze:** In `helden/` wird genau **eine Tabellenzelle** angefasst (T1, einmalige User-Freigabe). Alles andere unter `helden/illaen-baernhold/` und `abenteuer/` bleibt unberührt — Nachweis im Sprint-Diff.
- **Am Korpus gemessen (Vorab):** `stabzauber.md` hat 0 problematische freistehende Sterne (18× `\*` escaped) → B-023 blockiert D-051 nicht; `rituale-grundregeln.md` hat genau einen einzelnen `RkP*` (Z. 35), keine `<em>`-Paarung.
- **Subagent-Driven Development** mit zweistufiger Review (Spec + Code-Qualität) je Task; Reviewer-Verdikt zuoberst, Bericht < 3500 Zeichen; triviale Minor-Funde inline vom Controller in einen Polish-Commit.

## Out of Scope

- **B-023** (freistehende Buch-Sternchen, wiki, M) — trifft keinen der neu eingebetteten Artikel (s. o.); bleibt im Vault-Backlog.
- **Lange Vorschau-Kopfzeile kürzen** — die Quelle `WdZ S. 105–115 (Apport S. 106, …)` ist korrekt; ` · ` trennt im Korpus legitime Zweitquellen. T6 misst nur, ob der Umbruch trägt.
- **„Stabverlängerung“ = „Doppeltes Maß“** bleibt die semantisch bestätigte Zuordnung aus Sprint 023 (R10); Probe/AsP/Vol der Zeile bleiben bewusst offen.
- Footer-Einblenden glätten, echter `PATCH`-Pfad im Browser, LE-/AU-Mali — weiter ohne EPIC.

## Rulings (Controller, SDD-Ledger `.superpowers/sdd/sprint-024/progress.md`)

- R1: Umsetzung auf `master` im Hauptarbeitsbaum, ohne Worktree — bewährte Praxis der Sprints 001–023 (CLAUDE.md-Workflow), Commits lokal, kein Push — bei Fehlschlag: `git reset` auf `fd6f593`.
- R2: T3 passt die Live-Smoke-Assertion an (Ritual-Pfade zugelassen) — sonst rot nach T3 — Kosten: keine (Test bleibt live, pinnt weiter keine Werte).
- R3: T5 adressiert Testzeilen per Inhalt — Zeilennummern verschieben sich durch T3/T4 — Kosten: keine.
- R4: T5 härtet nur die drei im Backlog benannten `.index`-Stellen — Scope = B-024-Text; die übrigen ~14 `.index`-Vorkommen gehören zu Struktur-/Reihenfolge-Tests, deren ValueError ohnehin laut fehlschlägt — Kosten: kosmetisch, ggf. später.
- R5: Apport-Bogen-Edit (T1) unter der User-Freigabe dieser Planung (AskUserQuestion „Apport dazu, mit Bogen-Edit“) — genau eine Zelle — Kosten: Zelle zurücksetzen.
- R6: T2 passt die zwei bestehenden Sprint-023-Tests (`test_stabzauber_anchor_link_*`, test_held.py ~Z. 155–168) an — „Anker-Link ändert das Dict nicht“ wird durch D-051 bewusst aufgehoben (Link speist die Vorschau), gilt weiter bis auf `wiki_path` — Kosten: keine. `wiki_path` kommt NUR aus der Namensspalte (Apport-Effektzelle hat eigenen Link auf rituale-grundregeln).
- R7: T5 Teil B: die drei Live-Kampf-Wund-Tests bleiben UNVERÄNDERT (schon waffenzahl-unabhängig); ergänzt wird ein synthetischer Fall mit genau einer Waffe (Nicht-Vakuität: _weapon_cards == 1) — der Backlog-Text 'hängt nur am Live-Bogen' meint die Vakuität bei 0 Waffen, nicht eine harte Zahl — Kosten: keine.
- R8: T6-Messfokus korrigiert — der Plan nannte Flammenschwert/Schuppenhaut/Hammer-Tabellen, aber die 10 eingebetteten Artikel (nur die im Bogen verlinkten) enthalten 0 Tabellen; sie bestehen aus verschachtelten Listen (1–4 ul, 6–20 li) + 105 Zeichen langer quelle. T6 misst daher Listen-Layout (Sprint-021-Falle .sf-list li), quelle-Umbruch, Überlauf, Druck — Kosten: keine (Tabellen-Einbettung wäre ohnehin erst mit weiteren Bogen-Zeilen relevant).
- R9: Fix-Scope nach T6 — NUR der Druck-Kontrast des Namenslinks (.sf-list li .sf-name a, 1,07:1 im Druck; für die 10 Ritualzeilen neue Regression durch T4, weil die Namen vorher Text waren; dieselbe Regel bessert nebenbei die 15 SF-Links, vorbestehend seit D-050). NICHT im Fix (vorbestehend, nicht durch D-051 verursacht → D-052 im Backlog): .meta 1,95:1 und .vol-badge 4,12:1 im Druck, .speicher-box 1,04:1 (seit Sprint 005), Druck-Überlauf docScrollWidth 881 vs 779 (Karte 'Spontane Modifikationen', wirkung-cell/mods-details), Grid-Stretch der SF-Karte bei offenen Ritual-Artikeln (Ritual-Karte ~7 123 px bei allen 10 offen), Konsolen-404 favicon/mtime-Poll der Static-Seite — Kosten: Druck der Ritual-Karte bleibt in Meta/Badge blass (wie vor dem Sprint).

## Ergebnis

- 586 Tests (Sprint-023-Stand 563: +6 T2, +5 T3, +7 T4, +4 T5, +1 Fix-Runde); Static-Render 481 641 → 508 457 B, `artikel-details` 40 → 50, 0× `<script src>`; Domänen-Grenze: `helden/illaen-baernhold/` genau `rituale.md` (1 Zeile), `abenteuer/` und `wiki/` unberührt.
- Browser-Runde fand den Druck-Kontrastfehler des Namenslinks (1,07 → 14,62 : 1, neue Regression für die 10 Ritualzeilen); Fix-Runde 1 + Nachmessung bestanden. Übrige Auffälligkeiten (vorbestehend) → D-052.
