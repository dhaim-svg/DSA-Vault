# Sprint 005 — D-005 Zauberspeicher im Stab

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-005 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-005/plan.md |
| T1 | Writer: new `table_row` locator kind + tests | ✅ done | writers/held_writer.py, tests/ |
| T2 | Template UI: Befüllen/Entleeren controls per slot (all 5 cols), CSS, window.DSA expose | ✅ done | templates/dashboard.html.j2 |
| T3 | Client JS: build `table_row` PATCH on befüllen + clear-to-sentinel on entleeren | ✅ done | static/zauberspeicher.js, templates/dashboard.html.j2 |
| T4 | Verifikation + `/sprint-wrap` | ✅ done | BACKLOG.md, sprints/sprint-005/handoff.md |

## Key Design Decisions

- One PATCH per slot via new `table_row` locator — writer gains one `elif` branch + refactored `_locate_row` helper; no server/route change
- Independent register — no coupling to hero AE bar; AsP debit stays manual
- `section_path: ['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt']` — must descend to H3 to avoid hitting the Stabzauber feature table (H2-first table)
- Granular `data-slot` + build-in-JS wiring (inventar.js style, not embedded data-locator)
- On success: full page reload (consistent with inventar.js)
- `(9 Rituale)` in heading is a literal — brittle if ritual count ever changes; noted as known fragility

## Out of Scope

AE/AsP coupling between Zauberspeicher and hero AstralEnergie; capacity enforcement (> 20 AsP);
adding/removing slot rows (fixed at 3); D-006, D-007, D-008, D-009.
