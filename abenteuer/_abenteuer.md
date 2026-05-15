# Abenteuer

Spielerdaten-Bereich des Vaults — Kampagnen und Spielsitzungen. **User-Domäne.**

## Kampagnen

| Kampagne | System | SL | Held(en) | Sessions | Status |
|----------|--------|-----|----------|----------|--------|
| [[abenteuer/drachenchronik/_drachenchronik\|Drachenchronik]] | DSA 4.1 | — | [[helden/illaen-baernhold/_illaen\|Illaen]] | 0 | in Vorbereitung |

---

## Konventionen

### Kampagnen-Ordner

Jede Kampagne bekommt einen Unterordner `abenteuer/<kampagne>/`:

| Datei | Inhalt |
|-------|--------|
| `_<kampagne>.md` | Kampagnen-Überblick: Helden-Liste, SL, Status, Kurz-Synopse, offene Fäden |
| `YYYY-MM-DD-session-NN.md` | Eine Datei pro Spielabend |

### Session-Datei-Format

Dateiname-Schema: `YYYY-MM-DD-session-NN.md` (z.B. `2026-05-22-session-01.md`)

**Frontmatter:**
```yaml
---
typ: session
abenteuer: Drachenchronik
session: 1
datum: 2026-05-22
helden:
  - "[[helden/illaen-baernhold/_illaen|Illaen]]"
---
```

**Body-Sections:**
- `## Zusammenfassung` — 2-5 Sätze für späteres Nachschlagen
- `## Verlauf` — freie Mitschrift während des Spiels (Verlinkungen mit `[[...]]` erlaubt)
- `## AsP/LeP-Verlauf` — aktuelle Ressourcen der Helden tracken (z.B. `Illaen: AsP 38 → 24 → 30 (Reg)`)
- `## Neue NSCs / Orte` — inline, keine eigenen Dateien
- `## Offene Fäden / Cliffhanger`
- `## Loot / AP-Vergabe`

### Was in Sessions gehört vs. Charakterbogen

- **Session**: aktuelle LeP/AsP-Werte, Verlauf, NSCs, Notizen
- **Charakterbogen**: Max-Werte, Stammdaten, Sonderfertigkeiten (unveränderlich bis Steigerung)
- **Steigerungs-Log** (`helden/.../steigerungs-log.md`): AP-Ausgaben zwischen Sessions
