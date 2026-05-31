# Sprint 004 — D-004 Inventar / Geld / Verbrauch + AP_STUFEN Bugfix

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold | ✅ done | BACKLOG.md, sprints/sprint-004/plan.md |
| T1 | AP_STUFEN bugfix | ⬜ todo | parsers/held.py, tests/ |
| T2 | D-004 data model (money + weight) | ⬜ todo | parsers/held.py, helden/illaen-baernhold/_illaen.md |
| T3 | D-004 UI (dedicated Inventar tab) | ⬜ todo | templates/dashboard.html.j2 |
| T4 | D-004 write-back | ⬜ todo | static/inventar.js, templates/dashboard.html.j2 |
| T5 | Verification + wrap-up | ⬜ todo | BACKLOG.md, sprints/sprint-004/handoff.md |

## Key Design Decisions

- Money moves to `_illaen.md` frontmatter as structured `geld:` mapping (Dukaten/Silbertaler/Heller/Kreuzer) for PATCH-ability
- Weight (Gewicht in Unzen) partial total from `## Inventar` section only — other sections lack weight column; labeled as partial
- Write-back reuses existing locator kinds: `frontmatter` for money, `table_cell` for item qty, `table_append_row` for add-item
- Reiseausrüstung (non-numeric Menge like "5 Tage") is display-only this sprint (no write-back)
- AP_STUFEN fix: thresholds are CUMULATIVE AP totals per Stufe level, not per-level deltas

## Out of Scope

D-005 (Zauberspeicher interactive), D-006..D-009
