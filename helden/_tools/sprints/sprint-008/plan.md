# Sprint 008 — Commit-Message-Input + showIndicator-Dedup

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-010+D-011 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-008/plan.md |
| T1 | D-010 Commit-Message-Input | ✅ done | git_ops.py, server.py, static/commit.js, templates/dashboard.html.j2 |
| T2 | D-011 showIndicator-Dedup | ✅ done | static/util.js (neu), static/app.js, static/commit.js, templates/dashboard.html.j2 |
| T3 | Verifikation + /sprint-wrap | ✅ done | — |

## Key Design Decisions

- **Custom-Commit-Message-Format:** `dashboard: {slug} — {message}` bei Custom-Eingabe; bei leerem Input weiterhin Auto-Message `dashboard: {slug} {timestamp}`.
- **Shared-Helper:** `window.dsaShowIndicator(text, isError)` in neuem `static/util.js` (vor app.js geladen), da app.js closure-scoped ist und kein Build-Step existiert.
- **Backwards-Compat:** `commit_helden(vault_root, slug, message=None)` — additiv, bestehende Tests/Pfade unberührt.
- **journal.js bleibt unberührt:** nutzt eigenes okSpan-Muster, kein showIndicator.

## Out of Scope

- `kampagne_slug` enthardcoden (braucht Held→Kampagne-Mapping, größer als S)
- Harte Komplexitätsgrenze-Sperre (bewusst warn-only, User-Entscheid Sprint 7)
- Guided Stufen-Aufstieg / LE-AE-AU anheben (Out-of-Scope Sprint 7)
