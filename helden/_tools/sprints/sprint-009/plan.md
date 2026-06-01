# Sprint 009 — Manual-Test Polish (D-012 … D-017)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-012…D-017 → in-progress, plan.md anlegen) | ⬜ todo | BACKLOG.md, sprints/sprint-009/plan.md |
| T1 | D-012 Würfel-Panel Lesbarkeit: `.dice-panel` dunkles `color` + Kinder, an Dark-Tokens angleichen | ⬜ todo | dashboard.html.j2 (`:834-957`) |
| T2 | D-013 Vitalia-Stepper in einer Reihe: `.vital-stepper`-Elemente horizontal in einer Flucht | ⬜ todo | dashboard.html.j2 (`:728`, `:1167-1215`) |
| T3 | D-017 Sprachen Komplexitäts-Spalte: `.l-kompl` rechts-/zentriert ausrichten (beide Tabellen) | ⬜ todo | dashboard.html.j2 (`:1063`) |
| T4 | D-014 Footer-Layout: Überlappung „Session zurücksetzen"/„Sichern" auflösen; Commit-Feld + 💾 als sichtbare Gruppe via Flex/Gap statt Inline-Styles | ⬜ todo | dashboard.html.j2 (`:1862`, Footer-Markup) |
| T5 | D-015 Inventar: Hart-Truncation `item.anmerkung[:40]` entfernen + `#inventar-list li`/`.inv-*` Umbruch erlauben | ⬜ todo | dashboard.html.j2 (`:1042`, `:1603`) |
| T6 | D-016 Profil: `s.konsequenz[:60]` Truncation entfernen, mehrzeilige Darstellung in `.vn-grp.bad` | ⬜ todo | dashboard.html.j2 (`:1641-1652`, `:1646`) |
| T7 | Verifikation (Test-Suite + Static-Render + Sicht-Check) + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- D-012: `--card-bg` undefiniert im Dark-Theme → Fallback hell (#f5ebd8) + geerbtes helles `--ink` → hell-auf-hell. Fix: explizites dunkles `color` (vorhandene `:root`-Dark-Tokens verwenden, kein neues Token raten). Style-Block `:834-957`.
- D-013: Stepper-Elemente (−, Wert, /, Max, +) müssen horizontal in einer Flucht stehen. `.vital-stepper` `:728`, Markup `:1167-1215`.
- D-017: `.l-kompl` auf `text-align: right` oder `center` — beide Tabellen (Sprachen + Schriften). `:1063`.
- D-014: Inline-Styles am Footer (`#commit-msg`/`#commit-btn` `:1862`) → CSS-Klassen + Flex-Container; `.screen-only`/`print-hidden` und Commit-Kette (commit.js → POST /api/commit) nicht brechen.
- D-015: `item.anmerkung[:40]` `:1603` raus; `#inventar-list li` `:1042` + `.inv-*` `:1028-1041` Umbruch erlauben.
- D-016: `s.konsequenz[:60]` `:1646` raus; `.vn-grp.bad` Grid `:1641-1652` mehrzeilig.
- Alle Tasks in `dashboard.html.j2` — sequenziell, Commit pro Task.

## Out of Scope

D-018 (Zauber Inline-Vorschau, L), D-019 (Steigern Auswahl-Modus, L), D-020 (Steigerungsspalte, M), D-021 (Session-Kostenmodifikator, M) — größere Umbau-Sprints später.
