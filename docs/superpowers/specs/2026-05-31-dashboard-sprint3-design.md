# Dashboard Sprint 3: Tab-Navigation + AP & Steigerung — Design Spec

> Status: Draft — awaiting user review

---

## Goal

Transform the single-page scrolling dashboard into a 5-tab layout, and add a full Steigern-Tab where the player can spend AP to raise talents, spells, and attributes — with write-back to Markdown source files and an automatic steigerungs-log entry.

## Context

- Sprint 1 (Phase 0+1): Flask server, surgical Markdown write-back, interactive vitals (LeP/AsP/AuP), Wunden, Zustände
- Sprint 2 (Phase 2): Floating dice panel, 3W20 talent/spell probes, 1W20 attribute/combat probes, damage rolls
- Sprint 3 (this spec): Tab navigation + AP & Steigerung

---

## Architecture

### Tab Navigation

**5 tabs, client-side only — no server round-trip on tab switch.**

| Tab | Inhalt |
|-----|--------|
| ⚔️ Kampf | Vitalia (LeP/AsP/AuP Stepper), Wunden, Zustände, Eigenschaften (Hexagone), Basiswerte, AT/PA, Waffen |
| 🎯 Talente | Kampftechniken, Körperliche / Gesellschaftliche / Natur / Wissens / Sprach / Schrift / Handwerkliche Talente |
| ✨ Zauber | Zauberliste, Rituale, Stabzauber |
| ⭐ Steigern | AP-Übersicht, Steigerungsliste (Eigenschaften, Talente & Kampftechniken, Zauber) |
| 📋 Profil | Personendaten, Sonderfertigkeiten, Vorteile & Nachteile |

**Tab switching:**
- Sticky tab-bar at top of page (fixed position, body gets `padding-top` to compensate)
- JS toggles `tab-content--active` CSS class on the content divs
- Active tab persisted in `sessionStorage` key `dsa-active-tab`; default = `kampf`
- All existing widgets (Vitalia stepper, Würfel-Trigger, Wunden, dice.js) are wrapped into their tab div unchanged — no logic changes

**New file:** `helden/_tools/static/tabs.js` — minimal, self-contained tab controller (~50 lines). No changes to `app.js`, `session.js`, or `dice.js`.

**Template change:** `dashboard.html.j2` — existing content wrapped in `<div class="tab-content" id="tab-kampf">` etc. Tab-bar HTML + CSS added.

---

### Steigern-Tab

#### Content Structure

Three sections inside the Steigern-Tab:

**1. AP-Übersicht** (read-only display at top)
```
AP verfügbar: 5  |  AP eingesetzt: 3.845  |  AP gesamt: 3.850
Nächste Stufe (Stufe 4): 4.200 AP gesamt — fehlen 350 AP
```

**2. Eigenschaften** — `Zielwert × 15 AP` pro Punkt
- 8 Eigenschaften: MU, KL, IN, CH, FF, GE, KO, KK
- Zeigt: Name · aktuell → aktuell+1 · Kosten · [Steigern]-Button (grau = nicht leistbar)

**3. Talente & Kampftechniken**
- Grouped by section (Kampftechniken / Körperliche Talente / …)
- Kosten aus SKT-Tabelle (s.u.)
- Zeigt: Name · TaW · TaW+1 · Kosten · [Steigern]-Button

**4. Zauber**
- Kosten aus `Lern`-Spalte in `zauber.md`
- A+ (Hauszauber) treated as A
- Zeigt: Name · ZfW · ZfW+1 · Kosten · [Steigern]-Button

#### SKT Mapping

SKT-Kategorie pro Talent-Sektion:

| Sektion (Heading) | SKT |
|-------------------|-----|
| Kampftechniken | Per-row `Stk` column |
| Körperliche Talente | D |
| Gesellschaftliche Talente | B |
| Natur-Talente | B |
| Wissenstalente | B |
| Sprachen | A |
| Schriften | A |
| Handwerkliche Talente | B |

SKT-Kosten-Tabelle (embedded in JS and in parser):

| TaW-Bereich | A | B | C | D | E | F | G | H |
|-------------|---|---|---|---|---|---|---|---|
| 1–5 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| 6–10 | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 |
| 11–15 | 3 | 6 | 9 | 12 | 15 | 18 | 21 | 24 |
| 16–20 | 4 | 8 | 12 | 16 | 20 | 24 | 28 | 32 |

Parser extracts SKT from section heading via regex `\(SKT ([A-H])\)`. Falls back to section→SKT map above.

#### Steigern Interaction

1. User clicks [Steigern] → inline confirmation appears in the row:
   `"Klettern TaW 4→5 für 6 AP steigern? [Ja] [Nein]"`
2. On [Ja]: 3 sequential PATCH calls (abort chain on first 409)
3. On success: AP-Übersicht updates, button disables if AP now insufficient, log entry added
4. On 409 conflict: error message shown inline, no log written

**Not in Sprint 3:**
- Sprachen mit Komplexitäts-Grenze (TaW ≤ Komplexität)
- Ritual-Steigerung
- Neue Zauber lernen
- Stufen-Aufstieg

---

### Write-back Flow

**Per Steigerung: 3 PATCH calls in sequence**

**PATCH 1 — TaW/ZfW/Eigenschaft +1:**

Talent (talente.md) — row_key column is `"Talent"` for most sections, `"Kampftechnik"` for Kampftechniken:
```json
{ "kind": "table_cell",
  "file": "talente.md",
  "section_path": ["Körperliche Talente"],
  "row_key": { "column": "Talent", "match": "Klettern" },
  "column": "TaW",
  "value": "5",
  "slug": "illaen-baernhold" }
```
Parser emits `row_key_column` per item so JS constructs the correct locator automatically.

Eigenschaft (_illaen.md):
```json
{ "kind": "table_cell",
  "file": "_illaen.md",
  "section_path": ["Eigenschaften & Basiswerte", "Eigenschaften"],
  "row_key": { "column": "Eigenschaft", "match": "Klugheit (KL)" },
  "column": "Aktuell",
  "value": "15",
  "slug": "illaen-baernhold" }
```

**PATCH 2 — AP-Felder in Frontmatter (_illaen.md):** Two sequential PATCH calls.
```json
{ "kind": "frontmatter", "file": "_illaen.md",
  "key": "ap_verfuegbar", "value": "4", "slug": "..." }
{ "kind": "frontmatter", "file": "_illaen.md",
  "key": "ap_eingesetzt", "value": "3851", "slug": "..." }
```

**PATCH 3 — Steigerungs-Log Zeile anhängen:**
```json
{ "kind": "table_append_row",
  "file": "steigerungs-log.md",
  "section_path": ["Protokoll"],
  "cells": ["2026-05-31", "4 verf.", "Klettern TaW 4→5", "6", "Steigerung im Dashboard"],
  "slug": "illaen-baernhold" }
```

**New `held_writer.py` locator kind: `table_append_row`**
- Finds section via `_find_section_lines()`
- Finds first table via `_find_first_table()`
- Inserts new `| cell1 | cell2 | ... |` row after the last data row (before any blank line following the table)
- Atomic write (temp file + os.replace)
- Returns `PatchResult(ok=True, old=None, new=<row_text>)`

---

### Parser Changes (held.py)

New output fields added to `build_context()`:

```python
held['steigerbar_talente'] = [
    { 'name': 'Klettern', 'taw': 4, 'skt': 'D',
      'section': 'Körperliche Talente', 'file': 'talente.md' },
    ...
]
held['steigerbar_zauber'] = [
    { 'name': 'Armatrutz', 'zfw': 10, 'lern': 'B',
      'file': 'zauber.md' },
    ...
]
# Eigenschaften already in held['eigenschaften'] — reuse
```

`window.DSA` in template extended:
```javascript
window.DSA.steigern = {
  talente: [...],   // from held.steigerbar_talente
  zauber:  [...],   // from held.steigerbar_zauber
  // eigenschaften reuse window.DSA.eig
};
```

---

### New Files

| File | Purpose |
|------|---------|
| `helden/_tools/static/tabs.js` | Tab controller — switching, sessionStorage |
| `helden/_tools/static/steigern.js` | Steigern-Tab: cost calc, render, PATCH |
| `helden/_tools/BACKLOG.md` | Dashboard EPIC tracker (D-NNN format) |
| `helden/_tools/sprints/sprint-001/` | Retrospective for Sprint 1 (Phase 0+1) |
| `helden/_tools/sprints/sprint-002/` | Retrospective for Sprint 2 (Phase 2) |
| `helden/_tools/sprints/sprint-003/plan.md` | Sprint 3 plan (created by writing-plans skill) |

### Modified Files

| File | Change |
|------|--------|
| `helden/_tools/templates/dashboard.html.j2` | Tab-bar HTML+CSS, wrap sections in tab divs, extend `window.DSA.steigern`, include tabs.js + steigern.js |
| `helden/_tools/parsers/held.py` | Parse SKT per talent section, parse Lern per spell, new steigerbar_* fields |
| `helden/_tools/writers/held_writer.py` | New `table_append_row` locator kind |
| `CLAUDE.md` | Add "Dashboard Development" section: sprint workflow, BACKLOG.md pointer |

---

## Project Management Structure

### `helden/_tools/BACKLOG.md`

Format mirrors `docs/backlog.md` from HowlOnTheRedMoon, lighter variant:

```markdown
| EPIC | Title | Effort | State | Blocked by |
|------|-------|--------|-------|------------|
| D-003 | Tab-Navigation + Steigern (Sprint 3) | L | in-progress | — |
| D-004 | Inventar/Geld/Verbrauch | M | ready | — |
| D-005 | Session-Notizen → Journal | M | ready | D-004 |
| D-006 | Session-Commit-Button | S | ready | — |
```

### Sprint Folder Convention

```
helden/_tools/sprints/
  sprint-001/  retro.md
  sprint-002/  retro.md
  sprint-003/  plan.md       ← written by writing-plans
               handoff.md    ← written at session end (what's done, what's next, blockers)
```

### CLAUDE.md Addition

Short section added under `# Helden und Abenteuer`:

```markdown
## Dashboard Sprint-Workflow

Dashboard-Entwicklung läuft in Sprint-Sessions.
- EPIC-Tracker: `helden/_tools/BACKLOG.md` (D-NNN-IDs)
- Sprint-Pläne: `helden/_tools/sprints/sprint-NNN/plan.md`
- Am Session-Ende: `handoff.md` schreiben (fertig / als nächstes / Blocker)
- Laufende Sprint-Nr.: 3
```

---

## Out of Scope (Future Sprints)

| EPIC | Sprint |
|------|--------|
| D-004: Inventar/Geld/Verbrauch | 4 |
| D-005: Zauberspeicher im Stab | 4 |
| D-006: Session-Notizen → Journal | 5 |
| D-007: Session-Commit-Button | 5 |
| D-008: Sprachen mit Komplexitäts-Grenze | 3+ |
| D-009: Stufen-Aufstieg | 6 |
