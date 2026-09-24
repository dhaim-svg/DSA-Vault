---
name: sprint-plan
description: Plant den nächsten Dashboard-Sprint (helden/_tools/) aus BACKLOG.md und dem Handoff des Vorgänger-Sprints, schreibt plan.md und wartet auf Freigabe. Nutzen bei "/sprint-plan", "nächsten Sprint planen".
disable-model-invocation: true
---

# /sprint-plan

Plant den nächsten Dashboard-Sprint aus `helden/_tools/BACKLOG.md`.

Liest Backlog, vorheriges Handoff und Git-Status, entwirft `plan.md` und wartet
auf Freigabe — erst dann wird die Umsetzung angestoßen.

---

## Phase 1: Nächste Sprint-Nr. ermitteln

```bash
ls helden/_tools/sprints/
```

Höchsten `sprint-NNN`-Ordner finden → +1 (zero-padded auf 3 Stellen, z. B. `005`).
Alle folgenden Pfade verwenden diese Nummern:
- **Vorgänger**: `helden/_tools/sprints/sprint-{NNN-1}/`
- **Neuer Sprint**: `helden/_tools/sprints/sprint-{NNN}/`

---

## Phase 2: Kontext lesen (alle vier parallel)

### 2a. Vorgänger-Handoff — PFLICHT-GATE

**Lies zuerst**: `helden/_tools/sprints/sprint-{NNN-1}/handoff.md`

→ Extrahiere:
- Abschnitt `## Als nächstes (Sprint {NNN})` — das sind die **vorrangigen Kandidaten**
- Abschnitt `## Bekannte Einschränkungen` — bewusste Auslassungen, die ggf. nun fällig sind

**⛔ FEHLT die Datei** → sofort stoppen und dem User melden:
> „Sprint-{NNN-1}-Handoff fehlt (`sprints/sprint-{NNN-1}/handoff.md`). Ohne Handoff
> kann nicht sicher geplant werden — bitte Datei erstellen oder mit `/sprint-wrap`
> Sprint-{NNN-1} abschließen, bevor wir weitermachen."

### 2b. BACKLOG.md

Lies `helden/_tools/BACKLOG.md`:
- `## In Progress` — gibt es Carry-forward-Arbeit (Items, die noch laufen)?
- `## Backlog` — Zeilen mit `Blocked by = —` sind **sofort startbar**.
  Reihenfolge = Priorität — **nicht umordnen ohne Rückfrage**.
  Blockierte EPICs nur aufnehmen, wenn ihr Blocker in diesem Sprint mit erledigt wird.

### 2c. Git-Status

```bash
git status --short
git log --oneline -10
```

Uncommittete Änderungen in `helden/_tools/` → signalisiert in-progress Arbeit.

### 2d. CLAUDE.md — Quervalidierung

Zeile `**Laufende Sprint-Nr.:** N` in CLAUDE.md lesen. Sollte N = {NNN-1} sein —
wenn nicht, Abweichung erwähnen, aber nicht blockieren.

---

## Phase 3: Scope festlegen

Denke durch (intern, vor dem Schreiben):

1. **Handoff-Kandidaten zuerst**: Was steht im „Als nächstes"-Abschnitt des Vorgängers?
   Das sind die höchstpriorisierten EPICs.
2. **Carry-forward**: Laufende Items aus `## In Progress` mitnehmen.
3. **Backlog-Reihenfolge**: nach Handoff-Kandidaten, dann Zeile-für-Zeile aus `## Backlog`,
   nur sofort startbare EPICs (Blocked by = —).
4. **Realistischer Umfang**: Effort-Key S/M/L aus dem Backlog nutzen.
   Typisch 1–2 M-EPICs oder 1 L-EPIC pro Sprint (plus kleinere S-Tasks).

---

## Phase 4: `plan.md` entwerfen

Schreibe `helden/_tools/sprints/sprint-{NNN}/plan.md` nach der Vorlage
`.claude/skills/sprint-plan/templates/plan.md` (Tabelle **und** die `### Task N`-Abschnitte
darunter — letztere sind Pflicht, `superpowers`' `task-brief`-Skript extrahiert Briefs per
`^#+ Task N`-Regex daraus; ohne sie müssen Briefs von Hand geschrieben werden).

**Proportionalität:** Mehrere S-EPICs derselben Fläche in **einen** Sprint bündeln, statt pro
S-EPIC einen Sprint zu fahren. Ein Sprint mit genau einem Task braucht keine eigene Opus-
Gesamtreview zusätzlich zum Task-Review, außer der User verlangt sie (Security-Sprints:
Gesamtreview bleibt).

**Security-/Härtungs-Sprints:** Nur gegen ein festgehaltenes Bedrohungsmodell
(`helden/_tools/SECURITY.md`) planen. Die Gesamtreview prüft **gegen dieses Modell**; Funde
innerhalb des Modells werden im Sprint behoben, nur Funde **außerhalb** des Modells kommen
als neues EPIC ins Backlog. So entsteht keine Kette aus Nachbar-EPICs (D-061…D-067).

Effort-Referenz (für eigene Einschätzung, nicht in plan.md-Tabelle):
S = wenige Stunden, M = halber bis ganzer Tag, L = mehrere Tage

---

## Phase 5: Vorstellen & auf Freigabe warten

Fasse den Entwurf für den User zusammen:

- Sprint-Nummer und Ziel
- Tasks (Bullet-Liste)
- Offene Fragen oder Trade-offs, bei denen User-Input nötig ist

**Dann stoppen.** Kein Schreiben außer `plan.md`, keine weitere Ausführung,
bis der User explizit „OK" / „Freigabe" / ähnliches sagt.

---

## Phase 6: Nach Freigabe — Umsetzung anstoßen

Erst nach expliziter Freigabe:

1. **T0-Scaffold ausführen**:
   - BACKLOG.md: die in diesem Sprint angegangenen EPIC(s) von `## Backlog` nach
     `## In Progress` verschieben (State = `in-progress`).
   - Ordner `helden/_tools/sprints/sprint-{NNN}/` existiert bereits (plan.md wurde
     geschrieben); kein weiterer Setup-Schritt.

2. Den User auf **`/sprint-run`** verweisen, um die Feature-Tasks (T1 … TN-1) via
   Subagent-Driven Development umzusetzen (Projekt-Agents `sprint-implementer`,
   `sprint-task-reviewer`, `sprint-final-reviewer` in `.claude/agents/`).

3. **Nach dem letzten Feature-Task**:
   Den User darauf hinweisen, `/sprint-wrap` auszuführen, um Sprint-{NNN}
   ordentlich abzuschließen.
