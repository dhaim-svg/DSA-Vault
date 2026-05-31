# Sprint 007 — D-008 Sprachen-Tab + D-009 Stufen-Aufstieg

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-008+D-009 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-007/plan.md |
| T1 | D-008 Parser — Komplexität als numerisches Feld in `talente` + `steigerbar_talente` | ✅ done | parsers/held.py, tests/ |
| T2 | D-008 UI — neuer 🗣️ Sprachen-Tab (Name · Komplexität · TaW · Warn-Badge) | ✅ done | templates/dashboard.html.j2 |
| T3 | D-008 Steigern — warn-only Komplexitätsgrenze in Steigern-Tab | ✅ done | static/steigern.js |
| T4 | D-009 Stufen-Aufstieg — GM-Grant-Button, 3 PATCHes, Protokoll-Eintrag | ✅ done | static/steigern.js, templates/dashboard.html.j2 |
| T5 | Verifikation + `/sprint-wrap` | ✅ done | — |

## Key Design Decisions

- **Komplexität als numerisches Zweitfeld**: `entry['komplexitaet']` wird zusätzlich zu `entry['probe'] = 'K {n}'` gesetzt; bestehender Talente-Tab bleibt unverändert
- **D-008 warn-only**: Steigern-Button bleibt aktiv; Warnung „⚠ Komplexitätsgrenze K{n}" nur wenn TaW ≥ Komplexität
- **D-009 GM-Grant**: Stufe ist in DSA 4.1 GM-vergeben — kein AP-Gate; Button zeigt Schwellen-Hinweis; flow = frontmatter stufe+1 → AP-Anzeige-Tabelle sync → Protokoll
- **Keine neuen Routen / Writer-Kinds**: alles via `PATCH /api/held/<slug>/value` + vorhandene Locator-Kinds (`frontmatter`, `table_cell`, `table_append_row`)
- Sonder-Caps (Errata) und Eigenschafts-/Basiswert-Anhebungen explizit Out-of-Scope

## Out of Scope

- Harte Cap-Sperre (User wählte warn-only)
- Eigenschafts-/Basiswert-Änderungen beim Stufenaufstieg (geführte Variante)
- Sonder-Caps einzelner Sprachen (Errata in sprachen-schriften.md)
- Stufe-Schwellen-Datenkonflikt (code vs. steigerungs-log-Notiz) → in wiki-luecken.md notieren
