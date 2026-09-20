# Sprint 024 — Ritual-Artikelvorschau (D-051) & Test-Restkopplung II (B-024)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-051 → in-progress, Vault-backlog.md B-024 → In Progress, plan.md anlegen) | ⬜ todo | BACKLOG.md, backlog.md, sprints/sprint-024/plan.md |
| T1 | **Bogen-Edit (User-Domäne, freigegeben):** Namenszelle der Apport-Zeile → `[[wiki/dsa-4.1/rituale/stabzauber#Apport\|Apport]]`; Beleg per Diff + `load_held(...)['rituale']['andere']` vorher/nachher (`name` bleibt „Apport“) | ⬜ todo | helden/illaen-baernhold/rituale.md |
| T2 | **Parser:** `wiki_path` für Ritual-Zeilen (`extract_wiki_path(row['Stabzauber'])` bzw. `row['Ritual']`), `name` weiter über `strip_wikilink`; Tests über synthetischen Mini-Helden | ⬜ todo | parsers/held.py (~Z. 392–431), tests/test_held.py, ggf. tests/heldfixtures.py |
| T3 | **Render-Kontext:** `artikel_eintraege` um `held['rituale']['stabzauber']` + `['andere']` erweitern; Test: 10 Pfade landen in `wiki_artikel`, jeder Abschnitt nicht leer | ⬜ todo | rendering.py (~Z. 89), tests/test_rendering.py |
| T4 | **Template:** Ritual-Schleifen analog SF — Name als Obsidian-Link bei `wiki_path`, `artikel_details(art, …)` nach dem Text-`<span>`; Layout gegen die Sprint-021-Falle prüfen (nur `>`-gescopte CSS-Regeln, falls überhaupt nötig) | ⬜ todo | templates/partials/zauber.j2 (~Z. 96–103), ggf. static/base.css, tests/test_rendering.py |
| T5 | **B-024 Restkopplung II:** `test_load_held_geld_integration` auf synthetischen Helden, Waffenkarten-Fall der Kampf-Wund-Hooks per `write_mini_held(ausruestung=…)`, rohe `.index`-Stellen in `test_rendering.py` härten | ⬜ todo | tests/test_inventar_model.py, tests/test_rendering.py, tests/heldfixtures.py |
| T6 | **Browser-Runde (nur lesend):** Static-Render über `python -m http.server --directory output` auf freiem Port, sha256 der servierten Datei prüfen, Tabellen-Vorschauen (Flammenschwert, Schuppenhaut, Hammer) + lange `.artikel-quelle` bei 1280/400 px messen, Druck-Emulation, eigene PID beenden | ⬜ todo | — (nur Messung; Fixes ggf. static/base.css) |
| T7 | Verifikation + `verification.md` + `/sprint-wrap` | ⬜ todo | sprints/sprint-024/verification.md, Tracker |

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
