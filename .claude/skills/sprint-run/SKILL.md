---
name: sprint-run
description: Setzt die Feature-Tasks eines freigegebenen Dashboard-Sprint-Plans (helden/_tools/sprints/sprint-NNN/plan.md) via Subagent-Driven Development um -- eigene Projekt-Agents, zwei-stufige Review. Nutzen bei "/sprint-run", nach Freigabe von /sprint-plan.
disable-model-invocation: true
---

# /sprint-run

Setzt einen bereits freigegebenen Sprint-Plan (`helden/_tools/sprints/sprint-NNN/plan.md`) um.
Dies ist die Controller-Checkliste dieses Vaults, aufgesetzt auf `superpowers:subagent-driven-development`
(SDD) — lies zuerst deren aktuelle `SKILL.md` (Setup, Model Selection, Review-Loop), dann diese
projektspezifischen Ergänzungen.

## Vor dem Start

- **Kein Worktree.** Dieses Projekt arbeitet direkt auf `master`, ohne Push — das ist die dauerhafte
  Freigabe aus `CLAUDE.md`. Die generische SDD-Skill verlangt sonst einen Worktree oder ausdrückliche
  Zustimmung; hier gilt die CLAUDE.md-Regel als diese Zustimmung, kein erneutes Nachfragen.
- `ToolSearch("select:SendMessage")` sofort laden — Nachfragen und Fix-Runden an benannte Agenten
  brauchen es.
- Workspace: `bash <superpowers-plugin-root>/skills/subagent-driven-development/scripts/sdd-workspace helden/_tools/sprints/sprint-NNN/plan.md`
  (seit superpowers 6.4.1 kollisionsfrei über einen Plan-Pfad-Marker — keine Sonderbehandlung mehr nötig).
- Briefs: `task-brief PLAN_FILE N` funktioniert automatisch, **sofern** `plan.md` die
  `### Task N`-Abschnitte aus `.claude/skills/sprint-plan/templates/plan.md` enthält. Fehlen sie
  (älterer Plan): Brief von Hand aus der Tabellenzeile + Kontext schreiben.

## Pro Feature-Task (T1 … TN-1)

1. Brief erzeugen, Implementierer dispatchen: `subagent_type: "sprint-implementer"`, **mit `name`**
   (z. B. `s0NN-tN-impl`) — das macht Nachfragen und Fix-Runden per `SendMessage` möglich.
2. Nach Rückkehr: `git status --short` **und** `git show --stat HEAD` gegen die im Brief erwartete
   Dateizahl prüfen, bevor der Task als erledigt gilt. Implementierer committen nicht immer selbst
   und editieren gelegentlich Dateien außerhalb ihres Scopes.
3. Review-Package bauen: `review-package PLAN BASE HEAD .superpowers/sdd/sprint-NNN/task-N-review-package.diff`.
   Enthält der Commit `output/*.html`: das Paket **ohne** den generierten Output bauen
   (`git diff -U10 BASE..HEAD -- . ':!output'`) und im Reviewer-Brief vermerken; den Render-Vergleich
   macht der Controller separat (Golden-Baseline bei reinen Refactorings, siehe
   `references/golden-baseline.md`).
4. Reviewer dispatchen: `subagent_type: "sprint-task-reviewer"`, mit `name`. Im Prompt trotz fest
   codiertem Ausgabeformat im Agent **noch einmal explizit** an die Zeichen-Grenze erinnern — reines
   Wissen um die Regel reichte in der Vergangenheit nicht, wenn sie nicht auch im Dispatch-Text stand.
5. Findings unter 10 Zeilen Umfang **direkt selbst fixen** (kein eigener Subagent, kein Fix-Runden-
   Verbrauch) — das gilt auch für Funde aus Fix-Runden und der Gesamtreview.
6. Ansonsten: SDD-Fix-Loop (max. 5 Runden, ab Runde 4 stärkeres Modell/frischer Agent) wie in der
   generischen Skill beschrieben.

## Abschluss des Sprints

1. Gesamt-Diff seit Sprint-Start bauen, `sprint-final-reviewer` dispatchen (mit `name`).
2. Volle Test-Suite selbst noch einmal laufen lassen (nicht nur dem Reviewer-Bericht vertrauen):
   `__pycache__` löschen, dann `python -m pytest tests/ -q -W error` in `helden/_tools`.
3. Ist die Gesamtreview sauber (0 Critical/Important): `.superpowers/sdd/sprint-NNN/` löschen.
   Bei offenen, ungeparkten Findings: Workspace für die nächste Session behalten.
4. **Nie** `superpowers:finishing-a-development-branch` aufrufen (auf Feature-Branches/PRs/Merges
   ausgelegt, passt nicht zu diesem direkt-auf-master-Workflow). Stattdessen den User auf
   **`/sprint-wrap`** verweisen — das ist der eigentliche Abschluss-Schritt dieses Projekts.

## Browser-Verifikation (falls der Sprint UI-Änderungen enthält)

Siehe `references/browser-verify.md` für die sichere, rein lesende Verifikationsmethode
(Static-Render per `python -m http.server`, kein Rückschreiben).
