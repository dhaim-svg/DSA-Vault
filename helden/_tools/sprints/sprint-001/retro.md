# Sprint 1 Retro — Flask Server + Interactive Dashboard

## Completed
- Flask dev server with live-render (no stale state)
- Locator-based surgical Markdown write-back (`held_writer.py`)
- Interactive LeP/AsP/AuP steppers with debounced PATCH
- Wunden widget (persistent, frontmatter-backed)
- Zustände chips (transient, localStorage)
- Etag-based optimistic concurrency (409 on conflict)

## Process
- Subagent-Driven Development worked well
- Two-stage review caught BOM handling + mtime ordering bugs before merge
