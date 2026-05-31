# /sprint-wrap

Schließt den laufenden Dashboard-Sprint ab:
Verifikation → BACKLOG.md updaten → handoff.md schreiben → Sprint-Nr. erhöhen.

---

## Phase 1: Laufende Sprint-Nr. ermitteln

```bash
ls helden/_tools/sprints/
```

Höchsten `sprint-NNN`-Ordner mit vorhandener `plan.md` → das ist der **aktive Sprint**.
Lies `helden/_tools/sprints/sprint-{NNN}/plan.md`, um zu sehen welche EPICs und Tasks
enthalten sind.

---

## Phase 2: Verifikation — zuerst, vor allem anderen

**Keine Erfolgsmeldung ohne Evidenz.**

1. **Test-Suite** ausführen:
   ```bash
   cd helden/_tools && python -m pytest tests/ -v 2>&1 | tail -20
   ```
   Ergebnis (Anzahl bestanden / Anzahl gesamt) notieren — geht ins Handoff.

2. **Static-Render** prüfen:
   ```bash
   cd helden/_tools && python render-held.py 2>&1
   ```
   Exit-Code 0 = ok. Fehlermeldungen notieren und melden.

Falls Verifikation fehlschlägt → User informieren. Wrap-up kann trotzdem
fortgesetzt werden, aber Handoff muss den Fehlstatus dokumentieren.

---

## Phase 3: BACKLOG.md aktualisieren

Bearbeite `helden/_tools/BACKLOG.md`:

### 3a. Erledigte EPICs umziehen

Für jeden in diesem Sprint abgeschlossenen EPIC:
- Zeile aus `## Backlog` entfernen
- Zeile in `## Done`-Tabelle eintragen:
  `| D-NNN | [Title] | [Effort] | {NNN} |`

### 3b. In-Progress zurücksetzen

```
## In Progress

_(keine)_
```

Falls ein EPIC unfertig geblieben ist: **in `## Backlog` belassen** (State = `ready`),
nicht nach Done verschieben. Im Handoff unter „Als nächstes" und „Bekannte Einschränkungen"
erwähnen.

### 3c. Veraltete „Blocked by"-Refs räumen

Alle Zeilen in `## Backlog` durchgehen:
- Wenn `Blocked by` auf einen **soeben erledigten EPIC** zeigt → `Blocked by` auf `—` setzen.
- Beispiel: War `D-005 | Blocked by D-004` und D-004 ist jetzt done → `Blocked by = —`.

---

## Phase 4: `handoff.md` schreiben

Schreibe `helden/_tools/sprints/sprint-{NNN}/handoff.md` in diesem Format
(exakt wie sprint-004/handoff.md):

```
# Sprint {NNN} Handoff — [Ziel-Titel aus plan.md]

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (...)
- ✅ T1: [Task-Beschreibung] — [ein Satz Ergebnis]
- ...

## Was funktioniert

- [Tab/Feature]: [kurze Beschreibung des aktuellen Standes]
- ... (vollständige Liste aller funktionierenden Bereiche des Dashboards)

## Verifikation

- **Test Suite:** [X/Y] Testfälle bestanden ([breakdown wenn sinnvoll])
- **Static Render:** [Dateiname].html erfolgreich generiert (exit 0) ✓
- [weitere spezifische Checks aus dem Plan, z. B. bestimmte IDs im HTML]

## Als nächstes (Sprint {NNN+1})

- **D-NNN**: [EPIC-Titel] — [ein Satz warum das als nächstes sinnvoll ist]
- **D-NNN**: [weiterer Kandidat]
- (Reihenfolge = Empfehlung, nicht Pflicht)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- [Feature/Edge-Case]: [warum ausgeklammert, ob in Zukunft relevant]
```

**Der „Als nächstes"-Abschnitt ist der primäre Input für den nächsten `/sprint-plan`.**
Er wird dort als erstes gelesen und als vorrangige Kandidaten behandelt.

---

## Phase 5: CLAUDE.md — Sprint-Nr. erhöhen

In `CLAUDE.md` die Zeile:
```
- **Laufende Sprint-Nr.:** {NNN}
```
auf:
```
- **Laufende Sprint-Nr.:** {NNN+1}
```
ändern.

---

## Phase 6: Abschlussreport

```bash
git status --short
```

Melde dem User:
- Erledigte EPICs (mit D-NNN-IDs)
- Neue/geänderte Dateien (`git status --short`)
- Verifikations-Ergebnis (Test-Suite, Static-Render)
- Offene Punkte (unfertige Tasks, bekannte Einschränkungen)
- Empfehlung: „Sprint-{NNN+1} mit `/sprint-plan` einleiten."

**Optional (nicht Teil dieses Kommandos):** Memory `project_dashboard_sprint_state.md`
kann mit `/learn` am Session-Ende aktualisiert werden.
