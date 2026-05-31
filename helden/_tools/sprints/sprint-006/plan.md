# Sprint 006 — Journal (D-006) + Commit-Button (D-007)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-006+D-007 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-006/plan.md |
| T1 | D-006 Parser: `load_kampagne` → volle Body-Sektionen pro Session; Platzhalter-Session anlegen | ⬜ todo | parsers/kampagne.py, tests/test_kampagne.py, abenteuer/drachenchronik/ |
| T2 | D-006 Writer: neuer Locator-Kind `section_body` + `scope:'kampagne'` Datei-Auflösung | ⬜ todo | writers/held_writer.py, tests/test_held_writer.py |
| T3 | D-006 UI + Route: Journal-Tab, `PATCH /api/kampagne/<camp>/value`, `static/journal.js` | ⬜ todo | templates/dashboard.html.j2, server.py, static/journal.js |
| T4 | D-007 Commit-Button: `git_ops.py`, `POST /api/commit`, `static/commit.js`, Button im Template | ⬜ todo | git_ops.py, server.py, templates/dashboard.html.j2, static/commit.js, tests/test_commit.py |
| T5 | Verifikation (pytest grün, Browser-Smoke) + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **D-006 Writer minimal-invasiv:** Locator-`scope` (`'held'` default | `'kampagne'`);
  bei `kampagne` → Basis `vault_root/abenteuer/<locator['campaign']>`. Rückwärtskompatibel.
- **`section_body`-Kind:** Prosa-Block zwischen zwei Headings ersetzen via `_find_section_lines`.
  Atomic-Write + Per-File-Lock + etag-Concurrency aus `patch()` wiederverwendet.
  Nur `## Verlauf` editierbar im UI; andere Sektionen read-only.
- **Journal als eigener Tab:** `tabs.js` auto-wired per `data-tab` — keine tabs.js-Änderung.
- **D-007 Git in `git_ops.py`:** `commit_helden(vault_root, slug)` → subprocess, nur `helden/`,
  Auto-Message `dashboard: <slug> <ISO>`, kein push, „nothing to commit" → `{ok:True, committed:False}`.
- **Erster Route-Test** via `create_app(slug).test_client()` (neu im Testset).

## Out of Scope

- Push zum Remote, WYSIWYG-Editor, Commit ganzer Vault, neue Session-Dateien aus Dashboard,
  AsP/LeP-Sync, D-008/D-009.
