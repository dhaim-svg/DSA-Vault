---
name: warn-checkout-revert
enabled: true
event: bash
pattern: git\s+checkout\s+--\s
action: warn
---

git checkout -- on a mutation probe?

Never reset a mutation probe (an assert deliberately broken to check a test goes red) with
`git checkout --` -- it can drag along committed work from other tasks. Instead copy the file
and prove the change with sha256sum before/after (see memory feedback_subagent_commit_check).
