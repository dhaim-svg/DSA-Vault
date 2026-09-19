# /sprint-wrap

Schließt den laufenden Dashboard-Sprint ab:
Verifikation → BACKLOG.md updaten → handoff.md schreiben → CLAUDE.md-Sprint-Nr. auf den
soeben abgeschlossenen Sprint setzen.

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
   find helden/_tools -name __pycache__ -type d -prune -exec rm -rf {} +
   cd helden/_tools && python -m pytest tests/ -v 2>&1 | tail -20
   cd helden/_tools && python -m pytest tests/ -q -W error 2>&1 | tail -3
   ```
   Beide Läufe müssen grün sein (der zweite deckt Warnungen als Fehler ab — Standard seit
   Sprint 019). Ergebnis (Anzahl bestanden / Anzahl gesamt) notieren — geht ins Handoff.
   Die erste Zeile löscht den Bytecode-Cache: bei gecachtem `.pyc` greift `-W error` nicht auf
   Compile-Warnungen (Sprint 021: ein ungültiges `\|`-Escape in `held.py` blieb so unbemerkt).
   `-W error` als pytest-Option lassen, **nicht** als `python -W error` (trifft Plugin-Importe).

2. **Static-Render** prüfen — `render-held.py` braucht den Helden-Slug als Pflichtargument
   (Ordnername unter `helden/`, ohne `_tools`; aktuell nur `illaen-baernhold`), sonst bricht
   es mit einem Usage-Fehler ab:
   ```bash
   cd helden/_tools && python render-held.py illaen-baernhold 2>&1
   ```
   Exit-Code 0 = ok; erzeugt `output/illaen-baernhold-dashboard.html`. Fehlermeldungen
   notieren und melden.

Falls Verifikation fehlschlägt → User informieren. Wrap-up kann trotzdem
fortgesetzt werden, aber Handoff muss den Fehlstatus dokumentieren.

---

## Phase 3: BACKLOG.md aktualisieren

Bearbeite `helden/_tools/BACKLOG.md`:

### 3a. Erledigte EPICs umziehen

Für jeden in diesem Sprint abgeschlossenen EPIC:
- Zeile aus `## In Progress` entfernen (dorthin verschiebt `/sprint-plan` Phase 6 die
  Sprint-EPICs; ein EPIC, der nie umgezogen wurde, steht noch in `## Backlog`)
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

## Phase 5: CLAUDE.md — Sprint-Nr. auf den abgeschlossenen Sprint setzen

Die Zeile `**Laufende Sprint-Nr.:**` in `CLAUDE.md` führt den **zuletzt abgeschlossenen**
Sprint (nicht den nächsten). `/sprint-plan` Phase 2d erwartet dort `N = NNN−1` und plant
dann Sprint `N+1`. Setze sie deshalb auf die Nummer des Sprints, den du **gerade abschließt**
(ohne führende Nullen):
```
- **Laufende Sprint-Nr.:** {NNN}
```
Beispiel: Wrap von Sprint 019 → `19` (Sprint 020 wird danach mit `/sprint-plan` geplant).
**Nicht** um 1 erhöhen.

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
