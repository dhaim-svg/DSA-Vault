# Dashboard Sprint 3: Tab-Navigation + AP & Steigerung — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the scrolling dashboard into a 5-tab layout (Kampf / Talente / Zauber / Steigern / Profil) and add a Steigern-Tab where the player can spend AP to raise talents, spells, and attributes with write-back to Markdown files.

**Architecture:** Client-side tab controller (`tabs.js`) wraps existing sections; a new `steigern.js` renders the Steigern-Tab from `window.DSA.steigern` and chains 3 sequential PATCH calls per upgrade. `held_writer.py` gains a `table_append_row` locator kind for appending log entries atomically. `held.py` emits `steigerbar_talente` and `steigerbar_zauber` lists consumed by the template and JS.

**Tech Stack:** Python 3 / Flask, Jinja2, vanilla ES5 JS, `held_writer.py` locator-based surgical Markdown write-back.

---

## Codebase Context

All paths relative to vault root `D:/Projects/KnowledgeBase/DSA-Vault/`.

Key existing files:
- `helden/_tools/parsers/held.py` — `load_held(vault_root, slug)` reads all hero markdown files; returns a dict accessed as `held.*` in templates
- `helden/_tools/writers/held_writer.py` — `patch(vault_root, slug, locator)` → `PatchResult`; currently supports `table_cell` and `frontmatter` locator kinds
- `helden/_tools/templates/dashboard.html.j2` — Jinja2 template (~1537 lines); bottom of `<body>` has `window.DSA` JS blob and `<script>` tags for `app.js`, `session.js`, `dice.js`
- `helden/_tools/tests/test_held_writer.py` — existing unit tests for `held_writer.py`
- `helden/illaen-baernhold/talente.md` — talent sections headed `## Kampftechniken`, `## Körperliche Talente (SKT D)`, `## Gesellschaftliche Talente (SKT B)`, etc.
- `helden/illaen-baernhold/zauber.md` — has `## Zauberliste` with columns: Zauber, Probe, ZfW, Lern, …
- `helden/illaen-baernhold/steigerungs-log.md` — has `## Protokoll` table

**Template structure summary** (for tab-wrapping task):
```
<body>
  <div class="codex">
    [Jinja2 set blocks]
    <header class="banner"> … </header>          ← always visible (outside tabs)
    <!-- VITALS + KAMPFWERTE -->                  ← Kampf tab start
    <div class="grid cols-2"> … </div>            ← Vitalia + Kampfwerte cards
    <!-- Eigenschaften -->
    <section class="card attr-card"> … </section> ← Kampf tab end
    <!-- Vor- & Nachteile -->                      ← needs to move → Profil tab
    <section class="card"> … </section>
    <!-- SEITE 2 — TALENTE -->                     ← Talente tab
    <section class="card"> … </section>
    <!-- SEITE 3 — ZAUBER + RITUALE + SF -->       ← Zauber tab
    <section class="card"> … </section>            ← Zauberliste
    <section class="card"> … </section>            ← Spontane Mods (conditional)
    <div class="grid cols-2"> … </div>             ← Rituale + Sonderfertigkeiten
    <!-- SEITE 4 — AUSRÜSTUNG + KAMPAGNE + VORGESCHICHTE --> ← Profil tab
    …
```

---

## File Map

| Action | File | What changes |
|--------|------|-------------|
| Modify | `helden/_tools/writers/held_writer.py` | Add `_append_table_row()` + `table_append_row` branch in `patch()` |
| Modify | `helden/_tools/tests/test_held_writer.py` | Add 4 tests for `table_append_row` |
| Modify | `helden/_tools/parsers/held.py` | Add `SECTION_SKT_MAP`, `_skt_for_section()`, `steigerbar_talente`, `steigerbar_zauber` in `load_held()` |
| Create | `helden/_tools/tests/test_steigerbar.py` | Unit + integration tests for new parser fields |
| Create | `helden/_tools/static/tabs.js` | Tab controller (~50 lines) |
| Modify | `helden/_tools/templates/dashboard.html.j2` | Tab-bar + wrapping + `window.DSA.steigern` + script tags |
| Create | `helden/_tools/static/steigern.js` | Cost math + render + PATCH chain |
| Create | `helden/_tools/BACKLOG.md` | Dashboard EPIC tracker |
| Create | `helden/_tools/sprints/sprint-001/retro.md` | Sprint 1 retrospective |
| Create | `helden/_tools/sprints/sprint-002/retro.md` | Sprint 2 retrospective |
| Create | `helden/_tools/sprints/sprint-003/plan.md` | Symlink/copy of this plan |
| Modify | `CLAUDE.md` | Add Dashboard Sprint-Workflow section |

---

## Task 1: Project Management Scaffold

**Files:**
- Create: `helden/_tools/BACKLOG.md`
- Create: `helden/_tools/sprints/sprint-001/retro.md`
- Create: `helden/_tools/sprints/sprint-002/retro.md`
- Create: `helden/_tools/sprints/sprint-003/plan.md`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Create `helden/_tools/BACKLOG.md`**

```markdown
# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

| EPIC | Title | Effort | State | Blocked by |
|------|-------|--------|-------|------------|
| D-003 | Tab-Navigation + AP & Steigerung | L | in-progress | — |

## Backlog

| EPIC | Title | Effort | State | Blocked by |
|------|-------|--------|-------|------------|
| D-004 | Inventar / Geld / Verbrauch | M | ready | — |
| D-005 | Zauberspeicher im Stab | M | ready | D-004 |
| D-006 | Session-Notizen → Journal | M | ready | — |
| D-007 | Session-Commit-Button | S | ready | — |
| D-008 | Sprachen mit Komplexitäts-Grenze | S | ready | D-003 |
| D-009 | Stufen-Aufstieg | M | ready | D-003 |

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-001 | Flask-Server + Vitalia Write-back + Wunden + Zustände | L | 001 |
| D-002 | Würfelintegration (3W20 Proben, Schaden, Panel) | L | 002 |
```

- [ ] **Step 2: Create sprint retros (brief placeholders)**

`helden/_tools/sprints/sprint-001/retro.md`:
```markdown
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
```

`helden/_tools/sprints/sprint-002/retro.md`:
```markdown
# Sprint 2 Retro — Würfelintegration

## Completed
- Floating dice panel (sticky, bottom of screen)
- Talent probes (3W20+TaW), Zauber probes (3W20+ZfW), Eigenschaft (1W20), Kampf AT/PA (1W20), Schaden (XWY+Z)
- Auto-roll (RNG) + Manuell-Modus (3 inputs)
- Erschwernis prefilled from Wunden, editable
- AsP-deduct button after Zauber success (PATCH)
- LeP-deduct after PA fail (PATCH with prompt)
- 23 Python spec tests passing

## Process
- JS closure bug caught in self-review before subagent dispatch
- Schaden re-roll bug in render caught before implementation
```

- [ ] **Step 3: Add Dashboard Sprint-Workflow section to `CLAUDE.md`**

Add this block directly under `# Helden und Abenteuer` (before `## Grundregel`):

```markdown
## Dashboard Sprint-Workflow

Dashboard-Entwicklung (`helden/_tools/`) läuft in Sprint-Sessions.
- **EPIC-Tracker:** `helden/_tools/BACKLOG.md` (D-NNN-IDs, State, Effort)
- **Sprint-Pläne:** `helden/_tools/sprints/sprint-NNN/plan.md`
- **Handoff-Notes:** am Session-Ende `sprints/sprint-NNN/handoff.md` schreiben (fertig / als nächstes / Blocker)
- **Laufende Sprint-Nr.:** 3
- **Subagent-Driven Development** + zwei-stufige Review (spec + code quality) pro Task

```

- [ ] **Step 4: Copy this plan to sprint-003**

```bash
cp docs/superpowers/plans/2026-05-31-dashboard-sprint3.md helden/_tools/sprints/sprint-003/plan.md
```

- [ ] **Step 5: Commit**

```bash
git add helden/_tools/BACKLOG.md helden/_tools/sprints/ CLAUDE.md
git commit -m "chore: dashboard sprint project management scaffold"
```

Expected output: `master ... 1 commit`

---

## Task 2: `held_writer.py` — `table_append_row` Locator

**Files:**
- Modify: `helden/_tools/writers/held_writer.py`
- Modify: `helden/_tools/tests/test_held_writer.py`

### Step 1: Write failing tests

Add to `helden/_tools/tests/test_held_writer.py` (after existing fixtures):

```python
# ---------------------------------------------------------------------------
# Fixtures for table_append_row
# ---------------------------------------------------------------------------

STEIGERUNGS_LOG_TEXT = """\
---
typ: held-section
held: Test Held
---

# Steigerungs-Log

## Protokoll

| Datum | AP danach (verf.) | Aktion | Kosten | Begründung |
|-------|-------------------|--------|--------|------------|
| 2026-05-15 | 5 verf. | Initialstand | — | Übernahme |
"""


# ---------------------------------------------------------------------------
# table_append_row tests
# ---------------------------------------------------------------------------

def test_table_append_row_adds_new_row():
    from writers.held_writer import _append_table_row
    new_text, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['Protokoll'],
        cells=['2026-05-31', '4 verf.', 'Klettern TaW 4→5', '4', 'Test'],
    )
    assert new_text is not None
    assert '2026-05-31' in new_text
    assert 'Klettern TaW 4→5' in new_text


def test_table_append_row_increases_row_count():
    from writers.held_writer import _append_table_row
    from parsers.held import parse_frontmatter, split_sections, parse_md_table
    new_text, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['Protokoll'],
        cells=['2026-05-31', '4 verf.', 'Klettern TaW 4→5', '4', 'Test'],
    )
    _, body = parse_frontmatter(new_text)
    h2 = split_sections(body, 2)
    rows = parse_md_table(h2['Protokoll'])
    assert len(rows) == 2  # original 1 + new 1


def test_table_append_row_section_not_found_returns_none():
    from writers.held_writer import _append_table_row
    result, _ = _append_table_row(
        STEIGERUNGS_LOG_TEXT,
        section_path=['NonExistent'],
        cells=['x'],
    )
    assert result is None


def test_table_append_row_via_patch_api(tmp_path):
    """End-to-end: patch() dispatches table_append_row correctly."""
    from writers.held_writer import patch
    slug = 'test-held'
    hero_dir = tmp_path / 'helden' / slug
    hero_dir.mkdir(parents=True)
    log_file = hero_dir / 'steigerungs-log.md'
    log_file.write_text(STEIGERUNGS_LOG_TEXT, encoding='utf-8')

    result = patch(tmp_path, slug, {
        'kind': 'table_append_row',
        'file': 'steigerungs-log.md',
        'section_path': ['Protokoll'],
        'cells': ['2026-05-31', '4 verf.', 'Klettern TaW 4→5', '4', 'Test'],
    })
    assert result.ok
    updated = log_file.read_text(encoding='utf-8')
    assert '2026-05-31' in updated
    assert 'Klettern TaW 4→5' in updated
```

- [ ] **Step 2: Run tests — confirm 4 new failures**

```bash
cd D:/Projects/KnowledgeBase/DSA-Vault
python -m pytest helden/_tools/tests/test_held_writer.py -v -k "append"
```

Expected: 4 FAILED (ImportError or AttributeError — `_append_table_row` not defined yet)

- [ ] **Step 3: Implement `_append_table_row` in `held_writer.py`**

Add this function after `_find_first_table` (around line 287):

```python
def _append_table_row(
    text: str,
    section_path: list[str],
    cells: list[str],
) -> tuple[str | None, str]:
    """Append a new data row to the first table found in section_path.

    Returns (new_text, '') on success, (None, '') if section or table not found.
    """
    all_lines = text.splitlines(keepends=True)
    start, end = _find_section_lines(all_lines, section_path)
    if start is None:
        return None, ''
    section_lines = all_lines[start:end]
    tbl_start, tbl_end = _find_first_table(section_lines)
    if tbl_start is None:
        return None, ''

    abs_tbl_end = start + tbl_end  # absolute index of first line AFTER the table
    # Detect line ending from the last table line
    last_line = all_lines[abs_tbl_end - 1] if abs_tbl_end > 0 else ''
    lend = '\r\n' if last_line.endswith('\r\n') else '\n'
    new_row = '| ' + ' | '.join(str(c) for c in cells) + ' |' + lend

    new_lines = all_lines[:abs_tbl_end] + [new_row] + all_lines[abs_tbl_end:]
    return ''.join(new_lines), ''
```

Then add the `table_append_row` branch in `patch()`. In the `try:` block, after the `elif kind == 'table_cell':` branch, add:

```python
            elif kind == 'table_append_row':
                new_text, old_value = _append_table_row(
                    text,
                    section_path=locator.get('section_path', []),
                    cells=locator.get('cells', []),
                )
```

- [ ] **Step 4: Run all writer tests — confirm all pass**

```bash
python -m pytest helden/_tools/tests/test_held_writer.py -v
```

Expected: All tests PASS (existing + 4 new)

- [ ] **Step 5: Commit**

```bash
git add helden/_tools/writers/held_writer.py helden/_tools/tests/test_held_writer.py
git commit -m "feat(writer): table_append_row locator kind for steigerungs-log"
```

---

## Task 3: `held.py` — `steigerbar_*` Parser Fields

**Files:**
- Modify: `helden/_tools/parsers/held.py`
- Create: `helden/_tools/tests/test_steigerbar.py`

### Step 1: Write failing tests

Create `helden/_tools/tests/test_steigerbar.py`:

```python
"""Tests for steigerbar_talente and steigerbar_zauber parser output."""
import sys
from pathlib import Path
import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))
VAULT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # DSA-Vault root


# ---------------------------------------------------------------------------
# Unit tests: _skt_for_section
# ---------------------------------------------------------------------------

def test_skt_for_section_parses_heading():
    from parsers.held import _skt_for_section
    assert _skt_for_section('Körperliche Talente (SKT D)') == 'D'
    assert _skt_for_section('Gesellschaftliche Talente (SKT B)') == 'B'
    assert _skt_for_section('Handwerkliche Talente (SKT B)') == 'B'


def test_skt_for_section_fallback_map():
    from parsers.held import _skt_for_section
    assert _skt_for_section('Körperliche Talente') == 'D'
    assert _skt_for_section('Wissenstalente') == 'B'
    assert _skt_for_section('Sprachen') == 'A'


def test_skt_for_section_unknown_defaults_to_b():
    from parsers.held import _skt_for_section
    assert _skt_for_section('Unbekannte Sektion') == 'B'


# ---------------------------------------------------------------------------
# Integration tests: load_held steigerbar fields
# ---------------------------------------------------------------------------

def test_steigerbar_talente_has_required_fields():
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    items = held['steigerbar_talente']
    assert len(items) > 0
    for item in items:
        assert 'name' in item, f"Missing 'name' in {item}"
        assert 'taw' in item
        assert 'skt' in item
        assert item['skt'] in list('ABCDEFGH'), f"Invalid skt '{item['skt']}'"
        assert 'section' in item
        assert 'file' in item
        assert item['file'] == 'talente.md'
        assert 'row_key_column' in item


def test_steigerbar_kampftechniken_use_stk_column():
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    kampf = [i for i in held['steigerbar_talente'] if 'Kampftechnik' in i['section']]
    assert len(kampf) > 0
    for item in kampf:
        assert item['row_key_column'] == 'Kampftechnik'
    # Stäbe (Illaen's main combat technique) is SKT D
    staebe = next((i for i in kampf if i['name'] == 'Stäbe'), None)
    assert staebe is not None, "Stäbe not found in Kampftechniken"
    assert staebe['skt'] == 'D'


def test_steigerbar_zauber_has_required_fields():
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    items = held['steigerbar_zauber']
    assert len(items) > 0
    for item in items:
        assert 'name' in item
        assert 'zfw' in item
        assert 'lern' in item
        assert '+' not in item['lern'], f"A+ not normalized in {item}"
        assert item['lern'] in list('ABCDEFGH'), f"Invalid lern '{item['lern']}'"
        assert 'file' in item
        assert item['file'] == 'zauber.md'


def test_steigerbar_zauber_normalizes_hauszeichen():
    """A+ (Hauszauber) should be normalized to 'A'."""
    from parsers.held import load_held
    held = load_held(VAULT_ROOT, 'illaen-baernhold')
    items = held['steigerbar_zauber']
    # Armatrutz has Lern 'A' (Hauszauber — listed as A+)
    armatrutz = next((i for i in items if i['name'] == 'Armatrutz'), None)
    assert armatrutz is not None, "Armatrutz not found in steigerbar_zauber"
    assert armatrutz['lern'] == 'A'
```

- [ ] **Step 2: Run tests — confirm failures**

```bash
python -m pytest helden/_tools/tests/test_steigerbar.py -v
```

Expected: ImportError (no `_skt_for_section`) + AttributeError (no `steigerbar_talente` key)

- [ ] **Step 3: Add `SECTION_SKT_MAP` and `_skt_for_section()` to `held.py`**

Add near the top of `held.py`, after the `HAUPTEIGENSCHAFTEN` list:

```python
SECTION_SKT_MAP = {
    'Körperliche Talente': 'D',
    'Gesellschaftliche Talente': 'B',
    'Natur-Talente': 'B',
    'Wissenstalente': 'B',
    'Sprachen': 'A',
    'Schriften': 'A',
    'Handwerkliche Talente': 'B',
}


def _skt_for_section(sec_name: str) -> str:
    """Return DSA 4.1 SKT category for a talent section heading.

    Tries to extract from heading like 'Körperliche Talente (SKT D)'.
    Falls back to SECTION_SKT_MAP. Defaults to 'B' for unknown sections.
    """
    m = re.search(r'\(SKT ([A-H])\)', sec_name)
    if m:
        return m.group(1)
    base = re.sub(r'\s*\(.*?\)', '', sec_name).strip()
    return SECTION_SKT_MAP.get(base, 'B')
```

- [ ] **Step 4: Add `steigerbar_talente` and `steigerbar_zauber` to `load_held()`**

In `load_held()`, add this block immediately after the `talente` dict is fully built (after the `if grp: talente[sec_name] = grp` block, around line 197):

```python
    # Build steigerbar_talente — one entry per talent, with SKT and locator info
    steigerbar_talente: list[dict] = []
    for sec_name, grp in talente.items():
        is_kampf = 'Kampftechnik' in sec_name
        if 'Sprach' in sec_name:
            row_key_column = 'Sprache'
        elif 'Schrift' in sec_name:
            row_key_column = 'Schrift'
        elif is_kampf:
            row_key_column = 'Kampftechnik'
        else:
            row_key_column = 'Talent'
        for entry in grp:
            skt = entry.get('stk', 'D') if is_kampf else _skt_for_section(sec_name)
            if not skt:
                skt = 'B'
            steigerbar_talente.append({
                'name': entry['name'],
                'taw': entry['taw'],
                'skt': skt,
                'section': sec_name,
                'file': 'talente.md',
                'row_key_column': row_key_column,
            })
```

Add this block immediately after the `zauber` list is fully built (after the `zauber.append({...})` block, around line 255):

```python
    # Build steigerbar_zauber — normalize lern (A+ → A)
    steigerbar_zauber: list[dict] = []
    for z in zauber:
        lern = (z.get('lern') or '').strip().replace('+', '')
        if not lern:
            continue
        steigerbar_zauber.append({
            'name': z['name'],
            'zfw': z['zfw'],
            'lern': lern,
            'file': 'zauber.md',
        })
```

Add to the `return {}` dict at the end of `load_held()` (inside the existing return block):

```python
        'steigerbar_talente': steigerbar_talente,
        'steigerbar_zauber': steigerbar_zauber,
```

- [ ] **Step 5: Run all tests**

```bash
python -m pytest helden/_tools/tests/ -v
```

Expected: All tests PASS (existing writer + new steigerbar tests)

- [ ] **Step 6: Commit**

```bash
git add helden/_tools/parsers/held.py helden/_tools/tests/test_steigerbar.py
git commit -m "feat(parser): steigerbar_talente + steigerbar_zauber fields with SKT"
```

---

## Task 4: `tabs.js` — Tab Controller

**Files:**
- Create: `helden/_tools/static/tabs.js`

- [ ] **Step 1: Create `tabs.js`**

```javascript
/* tabs.js — client-side tab controller for DSA dashboard */
(function () {
  'use strict';

  var STORAGE_KEY = 'dsa-active-tab';
  var DEFAULT_TAB = 'kampf';

  function switchTab(id) {
    document.querySelectorAll('.tab-content').forEach(function (el) {
      el.classList.toggle('tab-content--active', el.id === 'tab-' + id);
    });
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
      btn.classList.toggle('tab-btn--active', btn.dataset.tab === id);
    });
    try { sessionStorage.setItem(STORAGE_KEY, id); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
      btn.addEventListener('click', function () { switchTab(btn.dataset.tab); });
    });
    var saved;
    try { saved = sessionStorage.getItem(STORAGE_KEY); } catch (e) {}
    switchTab(saved || DEFAULT_TAB);
  });
}());
```

- [ ] **Step 2: Commit**

```bash
git add helden/_tools/static/tabs.js
git commit -m "feat(tabs): client-side tab controller with sessionStorage persistence"
```

---

## Task 5: `dashboard.html.j2` — Tab Structure

**Files:**
- Modify: `helden/_tools/templates/dashboard.html.j2`

This task restructures the template into 5 tab content divs. The banner stays outside all tabs.

- [ ] **Step 1: Add tab CSS to `<style>` block**

Find the comment `@media print { .dice-panel { display: none !important; } }` near the end of the `<style>` block (around line 935). Add the following CSS **before** it:

```css
/* ─── Tab Navigation ─────────────────────────────────────────── */
.tab-bar {
  position: fixed;
  top: 0; left: 0; right: 0;
  z-index: 200;
  display: flex;
  gap: 2px;
  background: var(--bg-deep);
  border-bottom: 1px solid var(--rule);
  padding: 6px 14px 0;
  overflow-x: auto;
}
.tab-bar::-webkit-scrollbar { display: none; }
.tab-btn {
  padding: 8px 16px;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 6px 6px 0 0;
  background: transparent;
  color: var(--ink-mute);
  font-family: var(--display);
  font-size: 11px;
  letter-spacing: .1em;
  cursor: pointer;
  white-space: nowrap;
  transition: color .15s, background .15s;
}
.tab-btn:hover { color: var(--ink); background: rgba(95,195,228,.07); }
.tab-btn--active {
  color: var(--accent-cold);
  background: var(--bg-elev);
  border-color: var(--rule);
}
.tab-content { display: none; }
.tab-content--active { display: block; }
body { padding-top: 46px; }
@media print {
  .tab-bar { display: none !important; }
  .tab-content { display: block !important; }
  body { padding-top: 0 !important; }
}
/* Steigern Tab */
.sg-section-head { font-family: var(--display); font-size: 11px; letter-spacing: .18em;
  text-transform: uppercase; color: var(--accent-cold); margin: 20px 0 8px; }
.sg-row { display: flex; align-items: center; gap: 10px; padding: 5px 0;
  border-bottom: 1px solid var(--rule-soft); font-size: 13px; }
.sg-row:last-child { border-bottom: none; }
.sg-name { flex: 1; color: var(--ink); }
.sg-val { color: var(--ink-mute); font-family: var(--mono); font-size: 12px; min-width: 60px; }
.sg-cost { font-family: var(--mono); font-size: 12px; min-width: 52px; font-weight: bold; }
.sg-cost.affordable { color: var(--accent-aup); }
.sg-cost.expensive { color: var(--ink-dim); }
.sg-btn-area { display: flex; align-items: center; gap: 6px; }
.sg-btn { padding: 4px 10px; border: 1px solid var(--rule); border-radius: 4px;
  background: var(--bg-inset); color: var(--ink); cursor: pointer; font-size: 12px; }
.sg-btn:hover { background: var(--bg-elev); }
.sg-btn.disabled { opacity: .4; cursor: default; }
.sg-btn--ok { background: rgba(40,120,60,.3); color: #7fe8a0; border-color: #4a8a60; }
.sg-confirm { display: flex; align-items: center; gap: 6px; font-size: 12px; color: var(--ink-mute); }
.sg-confirm.hidden, .sg-btn.hidden { display: none; }
.sg-error { font-size: 11px; color: var(--accent-blood); margin-left: 8px; }
.sg-ap-row { display: flex; gap: 20px; flex-wrap: wrap; align-items: baseline; margin-bottom: 8px; }
.sg-ap-label { font-size: 11px; color: var(--ink-mute); text-transform: uppercase; letter-spacing: .1em; }
.sg-ap-val { font-family: var(--mono); font-size: 18px; font-weight: bold; color: var(--ink); margin-left: 4px; }
.sg-ap-val.avail { color: var(--accent-gold); }
.sg-stufe { font-size: 12px; color: var(--ink-mute); }
```

- [ ] **Step 2: Add tab-bar HTML after `<div class="codex">`**

Find the line `<div class="codex">` (around line 939). Insert the tab-bar HTML immediately after it, before the `{% set name_parts ... %}` Jinja2 line:

```html
<nav class="tab-bar" role="tablist" aria-label="Dashboard-Bereiche">
  <button class="tab-btn" data-tab="kampf"    type="button">⚔️ Kampf</button>
  <button class="tab-btn" data-tab="talente"  type="button">🎯 Talente</button>
  <button class="tab-btn" data-tab="zauber"   type="button">✨ Zauber</button>
  <button class="tab-btn" data-tab="steigern" type="button">⭐ Steigern</button>
  <button class="tab-btn" data-tab="profil"   type="button">📋 Profil</button>
</nav>
```

- [ ] **Step 3: Wrap sections in tab content divs**

The current template order (after the banner) is:
1. `<!-- VITALS + KAMPFWERTE -->` … Eigenschaften section
2. `<!-- Vor- & Nachteile -->` section
3. `<!-- SEITE 2 — TALENTE -->` section
4. `<!-- SEITE 3 — ZAUBER … -->` section + Rituale+SF grid
5. `<!-- SEITE 4 — AUSRÜSTUNG … -->` section

The new order wraps each group in a `<div class="tab-content" id="tab-X">`:

**After the closing `</header>` tag of the identity banner**, add:
```html
<div class="tab-content" id="tab-kampf">
```

**After the closing `</section>` of the Eigenschaften card** (the `<section class="card attr-card">` block, identified by `hex-grid`), add:
```html
</div><!-- end tab-kampf -->
<div class="tab-content" id="tab-talente">
```

**The `<!-- Vor- & Nachteile -->` section** (currently between Eigenschaften and Talente) must be **moved** inside the Profil tab. Cut it from its current position and place it inside the Profil tab div (see step 4).

**After the closing `</section>` of the Talente card** (identified by closing `</div>` after `{% endfor %}` of the talent-grid), add:
```html
</div><!-- end tab-talente -->
<div class="tab-content" id="tab-zauber">
```

**After the closing `</div>` of the Rituale+Sonderfertigkeiten `<div class="grid cols-2">` block** (the cols-2 grid that contains both Rituale and Sonderfertigkeiten cards), add:
```html
</div><!-- end tab-zauber -->

<div class="tab-content" id="tab-steigern">
  <div class="sec-head"><h2>AP &amp; Steigerung</h2><span class="rule"></span></div>
  <section class="card" id="steigern-ap-overview"></section>
  <section class="card" id="steigern-list" style="margin-top:var(--gap)"></section>
</div><!-- end tab-steigern -->

<div class="tab-content" id="tab-profil">
```
Then paste the `<!-- Vor- & Nachteile -->` section here (moved from above).

**After the last section of SEITE 4** (end of Vorgeschichte section, just before the `#dice-panel` div), add:
```html
</div><!-- end tab-profil -->
```

- [ ] **Step 4: Extend `window.DSA` with `steigern` data**

Find the existing `window.DSA = { ... };` block (around line 1511). Add the `steigern` key to it:

```javascript
window.DSA = {
  eig: {
    MU: {{ held.eigenschaften.MU.aktuell }},
    KL: {{ held.eigenschaften.KL.aktuell }},
    IN: {{ held.eigenschaften.IN.aktuell }},
    CH: {{ held.eigenschaften.CH.aktuell }},
    FF: {{ held.eigenschaften.FF.aktuell }},
    GE: {{ held.eigenschaften.GE.aktuell }},
    KO: {{ held.eigenschaften.KO.aktuell }},
    KK: {{ held.eigenschaften.KK.aktuell }}
  },
  vitals: {
    LE: { current: {{ le.current }}, max: {{ le.max }} },
    AE: { current: {{ ae.current }}, max: {{ ae.max }} },
    AU: { current: {{ au.current }}, max: {{ au.max }} }
  },
  steigern: {
    talente: {{ held.steigerbar_talente | tojson }},
    zauber:  {{ held.steigerbar_zauber  | tojson }},
    ap: {
      verfuegbar:   {{ held.meta.ap_verfuegbar }},
      eingesetzt:   {{ held.meta.ap_eingesetzt }},
      gesamt:       {{ held.meta.ap_gesamt }},
      stufe:        {{ held.meta.stufe }},
      bis_naechste: {{ held.get('_ap_bis_naechste_stufe') | tojson }}
    }
  },
  slug: "{{ slug }}"
};
```

- [ ] **Step 5: Add `tabs.js` and `steigern.js` script tags**

Find the existing script tags at the bottom:
```html
<script src="/static/app.js"></script>
<script src="/static/session.js"></script>
<script src="/static/dice.js"></script>
```

Add `tabs.js` and `steigern.js`:
```html
<script src="/static/app.js"></script>
<script src="/static/session.js"></script>
<script src="/static/dice.js"></script>
<script src="/static/tabs.js"></script>
<script src="/static/steigern.js"></script>
```

- [ ] **Step 6: Smoke test — render without errors**

```bash
cd D:/Projects/KnowledgeBase/DSA-Vault
python helden/_tools/render-held.py illaen-baernhold
```

Expected: No errors, `output/illaen-baernhold-dashboard.html` created. Open in browser (file://) — should see 5 tabs in the nav, tab switching works.

- [ ] **Step 7: Commit**

```bash
git add helden/_tools/templates/dashboard.html.j2
git commit -m "feat(template): 5-tab layout — tab-bar + content wrapping + window.DSA.steigern"
```

---

## Task 6: `steigern.js` — Cost Math + Render

**Files:**
- Create: `helden/_tools/static/steigern.js`

- [ ] **Step 1: Create `steigern.js` with cost math and render**

```javascript
/* steigern.js — AP cost calculation and Steigern-Tab controller */
(function () {
  'use strict';

  /* DSA 4.1 SKT cost table
     Index: 0 = TaW target 1-5, 1 = 6-10, 2 = 11-15, 3 = 16-20 */
  var SKT_COSTS = {
    A: [1, 2, 3, 4],
    B: [2, 4, 6, 8],
    C: [3, 6, 9, 12],
    D: [4, 8, 12, 16],
    E: [5, 10, 15, 20],
    F: [6, 12, 18, 24],
    G: [7, 14, 21, 28],
    H: [8, 16, 24, 32]
  };

  /* Cost to raise currentTaw → currentTaw+1 */
  function calcApCost(skt, currentTaw) {
    var costs = SKT_COSTS[skt];
    if (!costs) return null;
    var targetTaw = currentTaw + 1;
    var bracket = targetTaw <= 5 ? 0 : targetTaw <= 10 ? 1 : targetTaw <= 15 ? 2 : 3;
    return costs[bracket];
  }

  /* Cost to raise eigenschaft → eigenschaft+1 */
  function calcEigCost(currentVal) {
    return (currentVal + 1) * 15;
  }

  /* ── PATCH helper ─────────────────────────────────────────────────────── */
  function patchLocator(locator) {
    if (window.location.protocol === 'file:') return Promise.resolve({ ok: true });
    return fetch('/api/held/' + window.DSA.slug + '/value', {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(locator)
    }).then(function (r) {
      if (r.status === 409) return Promise.reject(new Error('Konflikt — Datei wurde extern geändert'));
      if (!r.ok) return r.json().then(function (d) {
        return Promise.reject(new Error(d.error || 'PATCH fehlgeschlagen'));
      });
      return r.json();
    });
  }

  /* ── Steigern: 3 sequential PATCHes ──────────────────────────────────── */
  function doSteigern(item, onSuccess, onError) {
    var slug = window.DSA.slug;
    var ap = window.DSA.steigern.ap;
    var newVal = item.currentVal + 1;
    var newAvail = ap.verfuegbar - item.cost;
    var newEinges = ap.eingesetzt + item.cost;

    // PATCH 1: raise the stat
    var patch1;
    if (item.kind === 'eigenschaft') {
      patch1 = {
        kind: 'table_cell', file: '_illaen.md', slug: slug,
        section_path: ['Eigenschaften & Basiswerte', 'Eigenschaften'],
        row_key: { column: 'Eigenschaft', match: item.eigFull },
        column: 'Aktuell', value: String(newVal)
      };
    } else if (item.kind === 'talent') {
      patch1 = {
        kind: 'table_cell', file: item.file, slug: slug,
        section_path: [item.section],
        row_key: { column: item.rowKeyCol, match: item.name },
        column: 'TaW', value: String(newVal)
      };
    } else { // zauber
      patch1 = {
        kind: 'table_cell', file: item.file, slug: slug,
        section_path: ['Zauberliste'],
        row_key: { column: 'Zauber', match: item.name },
        column: 'ZfW', value: String(newVal)
      };
    }

    patchLocator(patch1)
      .then(function () {
        return patchLocator({
          kind: 'frontmatter', file: '_illaen.md', slug: slug,
          key: 'ap_verfuegbar', value: String(newAvail)
        });
      })
      .then(function () {
        return patchLocator({
          kind: 'frontmatter', file: '_illaen.md', slug: slug,
          key: 'ap_eingesetzt', value: String(newEinges)
        });
      })
      .then(function () {
        var today = new Date().toISOString().slice(0, 10);
        var aktion = item.kind === 'eigenschaft'
          ? (item.abbr + ' ' + item.currentVal + '→' + newVal)
          : item.kind === 'talent'
          ? (item.name + ' TaW ' + item.currentVal + '→' + newVal)
          : (item.name + ' ZfW ' + item.currentVal + '→' + newVal);
        return patchLocator({
          kind: 'table_append_row', file: 'steigerungs-log.md', slug: slug,
          section_path: ['Protokoll'],
          cells: [today, newAvail + ' verf.', aktion, String(item.cost), 'Steigerung im Dashboard']
        });
      })
      .then(function () {
        window.DSA.steigern.ap.verfuegbar = newAvail;
        window.DSA.steigern.ap.eingesetzt = newEinges;
        onSuccess();
      })
      .catch(function (err) { onError(err.message || 'Fehler'); });
  }

  /* ── Row renderer ─────────────────────────────────────────────────────── */
  function renderRow(item) {
    var ap = window.DSA.steigern.ap.verfuegbar;
    var canAfford = item.cost !== null && ap >= item.cost;

    var row = document.createElement('div');
    row.className = 'sg-row';

    var nameEl = document.createElement('span');
    nameEl.className = 'sg-name';
    nameEl.textContent = item.displayName;

    var valEl = document.createElement('span');
    valEl.className = 'sg-val';
    valEl.textContent = item.currentVal + ' → ' + (item.currentVal + 1);

    var costEl = document.createElement('span');
    costEl.className = 'sg-cost ' + (canAfford ? 'affordable' : 'expensive');
    costEl.textContent = item.cost !== null ? item.cost + ' AP' : '—';

    row.appendChild(nameEl);
    row.appendChild(valEl);
    row.appendChild(costEl);

    if (item.cost !== null && canAfford) {
      var btnArea = document.createElement('span');
      btnArea.className = 'sg-btn-area';

      var steigBtn = document.createElement('button');
      steigBtn.type = 'button';
      steigBtn.className = 'sg-btn';
      steigBtn.textContent = 'Steigern';

      var confirm = document.createElement('div');
      confirm.className = 'sg-confirm hidden';
      confirm.textContent = item.displayName + ' für ' + item.cost + ' AP?';

      var jaBtn = document.createElement('button');
      jaBtn.type = 'button';
      jaBtn.className = 'sg-btn sg-btn--ok';
      jaBtn.textContent = 'Ja';

      var neinBtn = document.createElement('button');
      neinBtn.type = 'button';
      neinBtn.className = 'sg-btn';
      neinBtn.textContent = 'Nein';

      confirm.appendChild(jaBtn);
      confirm.appendChild(neinBtn);

      steigBtn.addEventListener('click', function () {
        steigBtn.classList.add('hidden');
        confirm.classList.remove('hidden');
      });
      neinBtn.addEventListener('click', function () {
        confirm.classList.add('hidden');
        steigBtn.classList.remove('hidden');
      });
      jaBtn.addEventListener('click', function () {
        jaBtn.disabled = true;
        jaBtn.textContent = '…';
        doSteigern(item, function () {
          window.location.reload();
        }, function (err) {
          var errEl = document.createElement('span');
          errEl.className = 'sg-error';
          errEl.textContent = '⚠ ' + err;
          row.appendChild(errEl);
          confirm.classList.add('hidden');
          steigBtn.classList.remove('hidden');
          steigBtn.disabled = false;
        });
      });

      btnArea.appendChild(steigBtn);
      btnArea.appendChild(confirm);
      row.appendChild(btnArea);
    }

    return row;
  }

  /* ── Tab renderer ─────────────────────────────────────────────────────── */
  var EIG_ORDER = ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK'];
  var EIG_FULL = {
    MU: 'Mut', KL: 'Klugheit', IN: 'Intuition', CH: 'Charisma',
    FF: 'Fingerfertigkeit', GE: 'Gewandtheit', KO: 'Konstitution', KK: 'Körperkraft'
  };

  function renderSteigernTab() {
    var dsa = window.DSA;
    if (!dsa || !dsa.steigern) return;
    var ap = dsa.steigern.ap;

    // AP overview
    var overview = document.getElementById('steigern-ap-overview');
    if (overview) {
      var availStr = '<span class="sg-ap-label">AP verfügbar<\/span><span class="sg-ap-val avail">' + ap.verfuegbar + '<\/span>';
      var einsStr  = '<span class="sg-ap-label">AP eingesetzt<\/span><span class="sg-ap-val">' + ap.eingesetzt + '<\/span>';
      var gesStr   = '<span class="sg-ap-label">AP gesamt<\/span><span class="sg-ap-val">' + ap.gesamt + '<\/span>';
      var stufeStr = ap.bis_naechste !== null
        ? '<div class="sg-stufe">Nächste Stufe (Stufe ' + (ap.stufe + 1) + '): noch ' + ap.bis_naechste + ' AP<\/div>'
        : '';
      overview.innerHTML = '<div class="sg-ap-row">' + availStr + einsStr + gesStr + '<\/div>' + stufeStr;
    }

    // Steigerungsliste
    var list = document.getElementById('steigern-list');
    if (!list) return;
    list.innerHTML = '';

    function addSection(title) {
      var h = document.createElement('h4');
      h.className = 'sg-section-head';
      h.textContent = title;
      list.appendChild(h);
    }

    // Eigenschaften
    addSection('Eigenschaften (Zielwert × 15 AP)');
    EIG_ORDER.forEach(function (abbr) {
      var val = dsa.eig[abbr];
      list.appendChild(renderRow({
        kind: 'eigenschaft', abbr: abbr,
        displayName: abbr + ' · ' + EIG_FULL[abbr],
        currentVal: val, cost: calcEigCost(val),
        eigFull: EIG_FULL[abbr] + ' (' + abbr + ')'
      }));
    });

    // Talente & Kampftechniken
    addSection('Talente & Kampftechniken');
    dsa.steigern.talente.forEach(function (t) {
      list.appendChild(renderRow({
        kind: 'talent', name: t.name,
        displayName: t.name + ' · SKT ' + t.skt,
        currentVal: t.taw, cost: calcApCost(t.skt, t.taw),
        section: t.section, file: t.file, rowKeyCol: t.row_key_column
      }));
    });

    // Zauber
    addSection('Zauber');
    dsa.steigern.zauber.forEach(function (z) {
      list.appendChild(renderRow({
        kind: 'zauber', name: z.name,
        displayName: z.name + ' · Lern ' + z.lern,
        currentVal: z.zfw, cost: calcApCost(z.lern, z.zfw),
        file: z.file
      }));
    });
  }

  document.addEventListener('DOMContentLoaded', renderSteigernTab);
}());
```

- [ ] **Step 2: Smoke test — server mode**

```bash
python helden/_tools/render-held.py serve illaen-baernhold --open
```

Open browser → click ⭐ Steigern tab → should see:
- AP-Übersicht (5 verf. / 3845 eingesetzt / 3850 gesamt)
- Eigenschaften section with 8 rows (MU, KL, IN, …)
- Talente section with all talents
- Zauber section with all spells
- "Steigern" button appears on affordable items (only Etikette TaW 5→6 costs 4 AP with SKT B = leistbar)

- [ ] **Step 3: Verify Etikette costs 4 AP**

Etikette: TaW 5, SKT B. Target TaW = 6 → bracket 6-10 → B[1] = 4 AP. ✓

- [ ] **Step 4: Commit**

```bash
git add helden/_tools/static/steigern.js
git commit -m "feat(steigern): AP cost math + Steigern-Tab render + PATCH chain"
```

---

## Task 7: Integration Verification

**Files:** Read-only smoke test — no code changes.

- [ ] **Step 1: Run full test suite**

```bash
python -m pytest helden/_tools/tests/ -v
```

Expected: All tests PASS. Check count — should be 32 (prior) + 4 (writer) + 7 (steigerbar) = 43+ tests.

- [ ] **Step 2: Static render check**

```bash
python helden/_tools/render-held.py illaen-baernhold
```

Expected: No errors, `output/illaen-baernhold-dashboard.html` regenerated.

- [ ] **Step 3: Server smoke test — tab switching**

```bash
python helden/_tools/render-held.py serve illaen-baernhold --open
```

Verify:
- [ ] Tab-bar is fixed at top, body has padding-top so content isn't hidden
- [ ] Clicking each tab shows/hides correct content
- [ ] Kampf tab: Vitalia steppers, Eigenschaften hexagons, AT/PA all visible
- [ ] Talente tab: all talent groups visible with probe dice triggers still working
- [ ] Zauber tab: Zauberliste + Rituale + Sonderfertigkeiten visible
- [ ] Steigern tab: AP overview + all 3 sections rendered; affordable items have [Steigern] button
- [ ] Profil tab: Vor/Nachteile + Ausrüstung + Vorgeschichte visible
- [ ] sessionStorage persists active tab across page reload (F5)

- [ ] **Step 4: Test Steigern end-to-end**

With server running, note current `ap_verfuegbar` in `_illaen.md` (should be 5).

Find Etikette (Gesellschaftliche Talente, TaW 5, SKT B, cost 4 AP):
- Click [Steigern] → confirmation appears
- Click [Ja] → page reloads
- Verify:
  - Etikette TaW is now 6 in the Talente tab
  - AP verfügbar is now 1 in the Steigern tab
  - `helden/illaen-baernhold/talente.md` line for Etikette shows TaW 6
  - `helden/illaen-baernhold/_illaen.md` frontmatter: `ap_verfuegbar: 1`, `ap_eingesetzt: 3849`
  - `helden/illaen-baernhold/steigerungs-log.md` has a new row with today's date

```bash
git diff helden/illaen-baernhold/talente.md
git diff helden/illaen-baernhold/_illaen.md
git diff helden/illaen-baernhold/steigerungs-log.md
```

- [ ] **Step 5: Revert test Steigerung** (to keep character at original state)

```bash
git checkout helden/illaen-baernhold/talente.md helden/illaen-baernhold/_illaen.md helden/illaen-baernhold/steigerungs-log.md
```

- [ ] **Step 6: Create sprint-003 handoff note**

Create `helden/_tools/sprints/sprint-003/handoff.md`:

```markdown
# Sprint 3 Handoff

## Fertig
- [ ] Task 1: Project management scaffold
- [ ] Task 2: table_append_row in held_writer.py
- [ ] Task 3: steigerbar_* parser fields
- [ ] Task 4: tabs.js
- [ ] Task 5: dashboard.html.j2 tab structure
- [ ] Task 6: steigern.js
- [ ] Task 7: Integration verification

## Als nächstes (Sprint 4)
- D-004: Inventar / Geld / Verbrauch
- D-005: Zauberspeicher im Stab

## Offene Punkte
- Sprachen mit Komplexitäts-Grenze (TaW ≤ Komplexität) noch nicht implementiert (D-008)
- Stufen-Aufstieg erfordert separaten Sprint (D-009)
```

- [ ] **Step 7: Final commit**

```bash
git add helden/_tools/sprints/sprint-003/handoff.md
git commit -m "chore: sprint-003 handoff notes"
```

- [ ] **Step 8: Update BACKLOG.md — D-003 auf done**

Update `helden/_tools/BACKLOG.md`: move D-003 from "In Progress" to "Done" table.

```bash
git add helden/_tools/BACKLOG.md
git commit -m "chore: D-003 done — Tab-Navigation + Steigern complete"
```

---

## Verification Checklist

Before marking Sprint 3 complete:

- [ ] `python -m pytest helden/_tools/tests/ -v` → all green
- [ ] `python helden/_tools/render-held.py illaen-baernhold` → no errors
- [ ] Server: 5 tabs present and switchable
- [ ] Steigern tab: AP overview correct, cost math correct (Etikette = 4 AP, Klettern = 4 AP)
- [ ] End-to-end steigern: 3 PATCHes fire in sequence, page reloads correctly
- [ ] After steigern: talente.md, _illaen.md frontmatter, steigerungs-log.md all updated
- [ ] `git log --oneline -8` shows clean commits for each task
- [ ] `git push origin master` — pushed

---

## DSA 4.1 Reference: AP Cost Table

| Zielwert | A | B | C | D | E | F | G | H |
|----------|---|---|---|---|---|---|---|---|
| 1–5 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| 6–10 | 2 | 4 | 6 | 8 | 10 | 12 | 14 | 16 |
| 11–15 | 3 | 6 | 9 | 12 | 15 | 18 | 21 | 24 |
| 16–20 | 4 | 8 | 12 | 16 | 20 | 24 | 28 | 32 |

Eigenschaft: Zielwert × 15 AP (d.h. Wert 12→13 = 13×15 = 195 AP)
