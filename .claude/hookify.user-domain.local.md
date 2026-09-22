---
name: warn-user-domain
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: (^|[\\/])(abenteuer[\\/]|helden[\\/](?!_tools[\\/]))
---

User domain

`helden/` (except `_tools/`) and `abenteuer/` are player domain (see CLAUDE.md). Only write here
on the user's explicit request -- never automatically while compiling or cleaning up the wiki.
