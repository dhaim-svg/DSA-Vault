# Interactive Dashboard — Phase 0+1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the read-only DSA-4.1 hero dashboard into a live interactive app where LeP/AsP/AuP (and Wunden) are tracked in the browser and written back to the source markdown files, persisting across sessions via git.

**Architecture:** A Flask server (`server.py`) serves the dashboard live-rendered from markdown via the existing Jinja2 pipeline and exposes a single `PATCH /api/held/<slug>/value` endpoint as the *only* write path. A new `writers/held_writer.py` performs surgical, line-precise, format-preserving cell/frontmatter updates on the raw markdown (not through the lossy parsed model). The template grows interactive stepper controls for vitals; `static/app.js` sends debounced PATCHes; `static/session.js` holds transient browser-only state (Zustände, temp mods).

**Tech Stack:** Python 3.11+, Flask, Jinja2 (existing), watchdog (existing), vanilla JS (no framework, no build step). All deps in `requirements.txt`.

**Scope of this plan:** Phase 0 (plumbing refactor, no behavior change) + Phase 1 (write-back foundation + current/max vitals + Wunden overlay). Phases 2–5 (dice, AP/Steigerung, inventory, journal) are separate follow-up plans.

---

## File Map

| Status | Path | Responsibility |
|--------|------|----------------|
| modify | `helden/_tools/render-held.py` | Split `render()` into `build_context` + `render_html`; add `serve` subcommand; import from rendering.py |
| create | `helden/_tools/rendering.py` | Shared Jinja helpers (obsidian_uri, roman, format_ap, _make_env) — imported by both render-held.py and server.py |
| modify | `helden/_tools/watcher.py` | Replace livereload server with mtime-token increment |
| modify | `helden/_tools/parsers/held.py` | Read `Max`/`Akt.` columns + `wunden` frontmatter |
| modify | `helden/_tools/templates/dashboard.html.j2` | Interactive vitals, `data-locator` attrs, externalized JS, touch targets |
| modify | `helden/illaen-baernhold/_illaen.md` | Rename `Aktuell`→`Max`, add `Akt.` column; add `wunden` frontmatter |
| create | `helden/_tools/server.py` | Flask app + JSON API endpoints |
| create | `helden/_tools/writers/__init__.py` | Empty package marker |
| create | `helden/_tools/writers/held_writer.py` | Format-preserving surgical markdown writer (core of write-back) |
| create | `helden/_tools/static/app.js` | Debounced PATCH, mtime polling, conflict handling |
| create | `helden/_tools/static/session.js` | Tier-B transient state (Zustände, buffs) in localStorage |
| create | `helden/_tools/tests/test_held_writer.py` | Round-trip + edge-case tests for the writer |
| modify | `requirements.txt` | Add `flask` |

---

## Task 1: Add Flask to requirements and install

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Add flask to requirements.txt**

Replace the entire file contents with:
```
jinja2>=3.1
pyyaml>=6.0
watchdog>=4.0
livereload>=2.6
flask>=3.0
```

- [ ] **Step 2: Install dependencies**

```
pip install -r requirements.txt
```

Expected: flask installed, no errors.

- [ ] **Step 3: Verify import**

```
python -c "import flask; print(flask.__version__)"
```

Expected: version string like `3.x.x` printed.

- [ ] **Step 4: Commit**

```
git add requirements.txt
git commit -m "deps: add flask for interactive dashboard server"
```

---

## Task 2: Split render() into build_context + render_html (Phase 0 refactor)

**Files:**
- Modify: `helden/_tools/render-held.py`

This is a pure refactor — no behavior changes. All existing `render` + `--watch` + `--open` behavior must keep working after this task.

- [ ] **Step 1: Create rendering.py — shared Jinja helpers (DRY)**

Create `helden/_tools/rendering.py` with the helpers that both `render-held.py` and `server.py` need:

```python
"""Shared Jinja2 rendering helpers for the DSA hero dashboard."""
from pathlib import Path
from urllib.parse import quote
import jinja2

TOOLS_DIR = Path(__file__).parent
TEMPLATES_DIR = TOOLS_DIR / 'templates'


def obsidian_uri(wiki_path: str, vault_name: str = 'DSA-Vault') -> str:
    if not wiki_path:
        return ''
    path, _, anker = wiki_path.partition('#')
    file_part = quote(path + '.md', safe='/')
    anker_part = f'#{quote(anker)}' if anker else ''
    return f'obsidian://open?vault={quote(vault_name)}&file={file_part}{anker_part}'


def roman(n: int) -> str:
    vals = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),
            (50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
    result = ''
    for v, s in vals:
        while n >= v:
            result += s
            n -= v
    return result


def format_ap(n: int) -> str:
    """Format AP integer as narrow-space-separated thousands: 3850 → '3 850'."""
    s = str(int(n))
    if len(s) > 3:
        return ' '.join([s[:-3], s[-3:]])
    return s


def make_env() -> jinja2.Environment:
    loader = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
    env = jinja2.Environment(loader=loader, autoescape=False,
                             trim_blocks=True, lstrip_blocks=True)
    env.filters['roman'] = roman
    env.filters['format_ap'] = format_ap
    env.filters['obsidian'] = obsidian_uri
    return env
```

- [ ] **Step 2: Replace render-held.py with the refactored version**

```python
#!/usr/bin/env python3
"""Render a DSA 4.1 hero dashboard to output/illaen-dashboard.html."""
import argparse
import sys
import webbrowser
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
OUTPUT_DIR = VAULT_ROOT / 'output'

sys.path.insert(0, str(TOOLS_DIR))
from parsers.held import load_held
from parsers.kampagne import load_kampagne
from rendering import make_env


def build_context(slug: str) -> dict:
    """Load hero + campaign data, return the Jinja template context dict."""
    return {
        'held': load_held(VAULT_ROOT, slug),
        'kampagne': load_kampagne(VAULT_ROOT, 'drachenchronik'),
        'slug': slug,
    }


def render_html(context: dict) -> str:
    """Render dashboard HTML from a pre-built context dict."""
    env = make_env()
    return env.get_template('dashboard.html.j2').render(**context)


def render(slug: str) -> Path:
    """Full pipeline: load → render → write file. Returns the output path."""
    html = render_html(build_context(slug))
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f'{slug}-dashboard.html'
    out_path.write_text(html, encoding='utf-8')
    return out_path


def main() -> None:
    # Manual dispatch: detect 'serve' as first arg to avoid subparser backward-compat issues
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        parser = argparse.ArgumentParser(description='Run interactive Flask server.')
        parser.add_argument('cmd')           # 'serve' — consumed to shift positionals
        parser.add_argument('slug', help='Hero slug, e.g. illaen-baernhold')
        parser.add_argument('--port', type=int, default=5500)
        parser.add_argument('--open', action='store_true', dest='do_open')
        args = parser.parse_args()
        from server import run_server
        run_server(args.slug, port=args.port, open_browser=args.do_open)
    else:
        # Legacy render mode — backward-compatible with existing usage
        parser = argparse.ArgumentParser(description='Render DSA hero dashboard.')
        parser.add_argument('slug', help='Hero slug, e.g. illaen-baernhold')
        parser.add_argument('--open', action='store_true', dest='do_open',
                            help='Open in browser after render')
        parser.add_argument('--watch', action='store_true',
                            help='Watch for changes and auto-reload')
        args = parser.parse_args()
        out_path = render(args.slug)
        print(f'Rendered -> {out_path}')
        if args.watch:
            from watcher import start_watch
            start_watch(args.slug, render_fn=lambda: render(args.slug),
                        open_browser=args.do_open)
        elif args.do_open:
            webbrowser.open(out_path.as_uri())


if __name__ == '__main__':
    main()
```

- [ ] **Step 3: Verify existing render still works**

```
python helden/_tools/render-held.py illaen-baernhold
```

Expected: `Rendered -> output\illaen-baernhold-dashboard.html` (no errors, file exists and is non-empty).

- [ ] **Step 4: Commit**

```
git add helden/_tools/rendering.py helden/_tools/render-held.py
git commit -m "refactor: extract rendering helpers, split render() into build_context + render_html, add serve subcommand"
```

---

## Task 3: Update _illaen.md — Aktuell→Max + new Akt. column

**Files:**
- Modify: `helden/illaen-baernhold/_illaen.md`

This is a data-model change. After this task the Basiswerte table has columns `Max` and `Akt.` instead of a single `Aktuell`. The `Akt.` value starts equal to `Max` for all vital rows.

- [ ] **Step 1: Add `wunden` to frontmatter**

Change the frontmatter block from:
```yaml
---
typ: held
name: Illaen Baernhold
rasse: Nivese
kultur: Mittelländische Städte
profession: Magischer Leibwächter (Stoerrebrandt-Kolleg zu Riva)
tradition: Gildenmagier
stufe: 3
ap_gesamt: 3850
ap_eingesetzt: 3845
ap_verfuegbar: 5
spieler: David
---
```
to:
```yaml
---
typ: held
name: Illaen Baernhold
rasse: Nivese
kultur: Mittelländische Städte
profession: Magischer Leibwächter (Stoerrebrandt-Kolleg zu Riva)
tradition: Gildenmagier
stufe: 3
ap_gesamt: 3850
ap_eingesetzt: 3845
ap_verfuegbar: 5
spieler: David
wunden: 0
---
```

- [ ] **Step 2: Replace Basiswerte table header and data rows**

Find the Basiswerte table (under `### Basiswerte`). Replace the entire table with:

```markdown
| Basiswert | Formel | Mod. | Start | Max | Akt. | Gekauft | Rest |
|-----------|--------|------|-------|-----|------|---------|------|
| Lebensenergie (LE) | (KO+KO+KK)/2 | +9 | 19 | 28 | 28 | 0 | 7 |
| Ausdauer (AU) | (MU+KO+GE)/2 | +12 | 19 | 31 | 31 | 0 | 13 |
| Astralenergie (AE) | (MU+IN+CH)/2 | +18 | 20 | 38 | 38 | 0 | 13 |
| Karmaenergie (KE) | — | — | — | — | — | — | — |
| Magieresistenz (MR) | (MU+KL+KO)/5 | −3 | 8 | 5 | — | — | — |
| Initiative (INI) | (MU+MU+IN+GE)/5 | 0 | 10 | 10 | — | — | — |
| Attacke (AT) | (MU+GE+KK)/5 | 0 | 7 | 7 | — | — | — |
| Parade (PA) | (IN+GE+KK)/5 | 0 | 8 | 8 | — | — | — |
| Fernkampf-Basis (FK) | (IN+FF+KK)/5 | 0 | 8 | 8 | — | — | — |
```

- [ ] **Step 3: Commit**

```
git add helden/illaen-baernhold/_illaen.md
git commit -m "data: Basiswerte Aktuell->Max + Akt. column; wunden frontmatter"
```

---

## Task 4: Update parser (held.py) to read Max/Akt./wunden

**Files:**
- Modify: `helden/_tools/parsers/held.py`

The parser must now read `Max` + `Akt.` instead of `Aktuell`, and expose `max`, `current`, `aktuell` (alias) per basiswert, plus `wunden` from frontmatter. All other parser behavior is unchanged.

- [ ] **Step 1: Update the basiswerte parsing loop**

Find the block that reads basiswerte (lines ~137–149 in the original file). Replace it with:

```python
    basiswerte: dict[str, dict] = {}
    for row in parse_md_table(h3.get('Basiswerte', '')):
        raw = strip_wikilink(row.get('Basiswert', ''))
        m = re.search(r'\(([A-Z]{1,3})\)', raw)
        if m:
            abbr = m.group(1)
        else:
            abbr = next((v for k, v in BASISWERT_MAP.items() if k in raw), raw)
        max_raw = row.get('Max', '') or row.get('Aktuell', '') or ''
        akt_raw = row.get('Akt.', '') or max_raw
        max_val = safe_int(max_raw)
        akt_val = safe_int(akt_raw) if (akt_raw and akt_raw.strip() not in ('—', '', '-')) else max_val
        basiswerte[abbr] = {
            'max': max_val,
            'current': akt_val,
            'aktuell': max_val,   # backward-compat alias used by template
            'formel': row.get('Formel', ''),
        }
```

- [ ] **Step 2: Read wunden from frontmatter — update the `return` block**

Find the `return { 'meta': { ... } }` dict near end of `load_held`. Add `wunden` to `meta`:

```python
        'meta': {
            'name': fm.get('name', slug),
            'rasse': fm.get('rasse', ''),
            'kultur': fm.get('kultur', ''),
            'profession': profession_raw,
            'profession_short': profession_short,
            'kolleg': kolleg,
            'tradition': fm.get('tradition', ''),
            'stufe': stufe,
            'ap_gesamt': ap_gesamt,
            'ap_eingesetzt': fm.get('ap_eingesetzt', 0),
            'ap_verfuegbar': fm.get('ap_verfuegbar', 0),
            'wahrer_name': wahrer_name,
            'wahrer_name_bedeutung': wahrer_name_bedeutung,
            'stigma': stigma,
            'wunden': int(fm.get('wunden', 0)),
        },
```

- [ ] **Step 3: Verify render still works**

```
python helden/_tools/render-held.py illaen-baernhold
```

Expected: `Rendered -> output\illaen-baernhold-dashboard.html` (no errors).

- [ ] **Step 4: Commit**

```
git add helden/_tools/parsers/held.py
git commit -m "feat(parser): read Max/Akt. columns and wunden frontmatter"
```

---

## Task 5: Build held_writer.py — the format-preserving markdown writer

**Files:**
- Create: `helden/_tools/writers/__init__.py`
- Create: `helden/_tools/writers/held_writer.py`

This is the core of Phase 1. The writer operates on raw file text, locates cells surgically using the same section-walk + table-parse semantics as the parser, and writes back only the changed cell.

**Design:** A `Locator` is a dict with two `kind`s:
- `table_cell`: `{kind, file, section_path: [H2, H3?], row_key: {column, match}, column, value}`
- `frontmatter`: `{kind, file, key, value}`

`patch(vault_root, slug, locator)` → `PatchResult(ok, old_value, new_value, mtime_before, mtime_after, error?)`.

- [ ] **Step 1: Create the writers package marker**

Create `helden/_tools/writers/__init__.py` as an empty file.

- [ ] **Step 2: Create held_writer.py**

```python
"""Format-preserving surgical writer for DSA 4.1 hero markdown files.

All markdown mutations for the interactive dashboard flow through patch().
The writer never reformats anything it doesn't touch:
 - CRLF/LF line endings are preserved
 - Column padding is best-effort preserved (no reflow)
 - Only the targeted cell's text changes; all other bytes are identical
"""
import hashlib
import os
import re
import threading
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Import the same helpers the parser uses, so locator semantics stay consistent
import sys
_HERE = Path(__file__).parent.parent
sys.path.insert(0, str(_HERE))
from parsers.held import (
    split_sections, _split_table_row, strip_wikilink, safe_int
)

# Per-file lock to serialise concurrent PATCHes from the debounced client
_FILE_LOCKS: dict[str, threading.Lock] = {}
_LOCKS_MUTEX = threading.Lock()


def _get_lock(path: Path) -> threading.Lock:
    key = str(path.resolve())
    with _LOCKS_MUTEX:
        if key not in _FILE_LOCKS:
            _FILE_LOCKS[key] = threading.Lock()
        return _FILE_LOCKS[key]


@dataclass
class PatchResult:
    ok: bool
    old_value: str
    new_value: str
    mtime_before: float
    mtime_after: float
    error: str = ''


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def patch(vault_root: Path, slug: str, locator: dict) -> PatchResult:
    """Apply a single-field patch described by locator.

    locator kinds:
      table_cell:  {kind, file, section_path, row_key: {column, match}, column, value}
      frontmatter: {kind, file, key, value}

    Includes optimistic-concurrency check: if the caller supplies
    locator['etag'] (md5 of file content at read time), we reject with
    error='conflict' if the file changed since then.
    """
    base = vault_root / 'helden' / slug
    rel_file = locator.get('file', '')
    target = base / rel_file
    if not target.exists():
        return PatchResult(ok=False, old_value='', new_value='',
                           mtime_before=0, mtime_after=0,
                           error=f'file not found: {rel_file}')

    lock = _get_lock(target)
    with lock:
        raw = target.read_bytes()
        mtime_before = target.stat().st_mtime
        text = raw.decode('utf-8-sig')  # handle optional BOM

        # Detect line ending style; we write it back unchanged
        lf = '\r\n' if '\r\n' in text else '\n'

        # Optimistic concurrency: check etag if caller provided one
        etag = locator.get('etag', '')
        if etag:
            actual_etag = hashlib.md5(raw).hexdigest()
            if actual_etag != etag:
                return PatchResult(ok=False, old_value='', new_value='',
                                   mtime_before=mtime_before, mtime_after=mtime_before,
                                   error='conflict')

        kind = locator.get('kind')
        if kind == 'frontmatter':
            new_text, old_value = _patch_frontmatter(text, locator['key'], str(locator['value']))
        elif kind == 'table_cell':
            new_text, old_value = _patch_table_cell(
                text,
                section_path=locator.get('section_path', []),
                row_key=locator['row_key'],
                column=locator['column'],
                value=str(locator['value']),
            )
        else:
            return PatchResult(ok=False, old_value='', new_value='',
                               mtime_before=mtime_before, mtime_after=mtime_before,
                               error=f'unknown locator kind: {kind}')

        if new_text is None:
            return PatchResult(ok=False, old_value=old_value, new_value=str(locator['value']),
                               mtime_before=mtime_before, mtime_after=mtime_before,
                               error='cell not found')

        # Atomic write: temp file in same dir + os.replace
        tmp = target.with_suffix('.tmp_patch')
        tmp.write_bytes(new_text.encode('utf-8'))
        os.replace(tmp, target)

        mtime_after = target.stat().st_mtime
        return PatchResult(ok=True, old_value=old_value,
                           new_value=str(locator['value']),
                           mtime_before=mtime_before, mtime_after=mtime_after)


def etag_for(vault_root: Path, slug: str, rel_file: str) -> str:
    """Return md5 hex of file content — used as optimistic-concurrency token."""
    path = vault_root / 'helden' / slug / rel_file
    return hashlib.md5(path.read_bytes()).hexdigest()


def mtime_map(vault_root: Path, slug: str) -> dict[str, float]:
    """Return {filename: mtime} for all .md files in the hero folder."""
    base = vault_root / 'helden' / slug
    return {p.name: p.stat().st_mtime for p in base.glob('*.md')}


# ---------------------------------------------------------------------------
# Frontmatter patcher
# ---------------------------------------------------------------------------

def _patch_frontmatter(text: str, key: str, value: str) -> tuple[str | None, str]:
    """Replace a scalar value in YAML frontmatter. Returns (new_text, old_value)."""
    if not text.startswith('---'):
        return None, ''
    parts = text.split('---', 2)
    if len(parts) < 3:
        return None, ''
    fm_block = parts[1]
    old_value = ''

    # Find and replace only the matching key line, preserving all other whitespace
    lines = fm_block.splitlines(keepends=True)
    new_lines = []
    found = False
    for line in lines:
        m = re.match(r'^(\s*' + re.escape(key) + r'\s*:\s*)(.+?)(\s*)$', line.rstrip('\r\n'))
        if m and not found:
            old_value = m.group(2).strip()
            lend = '\r\n' if line.endswith('\r\n') else '\n'
            new_lines.append(f'{m.group(1)}{value}{m.group(3)}{lend}')
            found = True
        else:
            new_lines.append(line)

    if not found:
        return None, ''

    new_fm = ''.join(new_lines)
    return '---' + new_fm + '---' + parts[2], old_value


# ---------------------------------------------------------------------------
# Table cell patcher
# ---------------------------------------------------------------------------

def _patch_table_cell(
    text: str,
    section_path: list[str],
    row_key: dict,
    column: str,
    value: str,
) -> tuple[str | None, str]:
    """Patch one cell in a markdown table identified by section_path + row_key.

    section_path is a list of heading names, outermost first:
      ['Eigenschaften & Basiswerte', 'Basiswerte']  → H2 then H3
      ['Zauberliste']                                → H2 only

    row_key = {'column': 'Basiswert', 'match': 'Lebensenergie (LE)'}
    The row whose row_key.column cell (after strip_wikilink) == row_key.match is targeted.
    """
    # Split text into lines, preserving line endings
    all_lines = text.splitlines(keepends=True)

    # Locate the contiguous line range for the section
    start, end = _find_section_lines(all_lines, section_path)
    if start is None:
        return None, ''

    section_lines = all_lines[start:end]

    # Find the first table within the section
    tbl_start, tbl_end = _find_first_table(section_lines)
    if tbl_start is None:
        return None, ''

    table_lines = section_lines[tbl_start:tbl_end]

    # Parse header row to get column indices
    if not table_lines:
        return None, ''
    headers = _split_table_row(table_lines[0].rstrip('\r\n'))

    try:
        key_col_idx = next(i for i, h in enumerate(headers) if h.strip() == row_key['column'])
        val_col_idx = next(i for i, h in enumerate(headers) if h.strip() == column)
    except StopIteration:
        return None, ''

    # Find data row (skip header + separator = indices 0 and 1)
    target_line_in_table = None
    old_value = ''
    for i, line in enumerate(table_lines[2:], start=2):
        cells = _split_table_row(line.rstrip('\r\n'))
        if key_col_idx >= len(cells):
            continue
        cell_display = strip_wikilink(cells[key_col_idx])
        if cell_display == row_key['match']:
            target_line_in_table = i
            old_value = cells[val_col_idx] if val_col_idx < len(cells) else ''
            break

    if target_line_in_table is None:
        return None, ''

    # Rebuild the target line with only the one cell changed
    abs_line_idx = start + tbl_start + target_line_in_table
    original_line = all_lines[abs_line_idx]
    new_line = _replace_cell_in_line(original_line, val_col_idx, value)
    new_lines = all_lines[:abs_line_idx] + [new_line] + all_lines[abs_line_idx + 1:]
    return ''.join(new_lines), old_value.strip()


def _find_section_lines(lines: list[str], section_path: list[str]) -> tuple[int | None, int | None]:
    """Return (start, end) line indices for the innermost section in section_path.

    Traverses heading levels 2, 3, ... matching each name in section_path in order.
    Returns the content block (lines after the heading, up to the next sibling heading).
    """
    if not section_path:
        return 0, len(lines)

    current_start = 0
    current_end = len(lines)

    for depth, name in enumerate(section_path, start=2):
        prefix = '#' * depth + ' '
        found = False
        for i in range(current_start, current_end):
            line = lines[i].rstrip('\r\n')
            if line.startswith(prefix) and line[depth + 1:].strip() == name:
                # Content starts after this heading line
                sec_start = i + 1
                # Content ends at next heading of same or higher level
                sec_end = current_end
                for j in range(sec_start, current_end):
                    candidate = lines[j].rstrip('\r\n')
                    if re.match(r'^#{1,' + str(depth) + r'} ', candidate):
                        sec_end = j
                        break
                current_start = sec_start
                current_end = sec_end
                found = True
                break
        if not found:
            return None, None

    return current_start, current_end


def _find_first_table(lines: list[str]) -> tuple[int | None, int | None]:
    """Return (start, end) of the first contiguous block of | lines."""
    start = None
    for i, line in enumerate(lines):
        if re.match(r'\s*\|', line):
            if start is None:
                start = i
        elif start is not None:
            return start, i
    if start is not None:
        return start, len(lines)
    return None, None


def _replace_cell_in_line(line: str, col_idx: int, new_value: str) -> str:
    """Replace cell at col_idx in a markdown table line, preserving padding."""
    PLACEHOLDER = '\x00PIPE\x00'
    lend = ''
    if line.endswith('\r\n'):
        lend = '\r\n'
        line = line[:-2]
    elif line.endswith('\n'):
        lend = '\n'
        line = line[:-1]

    escaped = line.replace(r'\|', PLACEHOLDER)
    parts = escaped.split('|')
    # parts[0] is before the first |, parts[-1] is after the last |
    # The actual cell indices are parts[1], parts[2], ...
    cell_idx = col_idx + 1  # offset by the leading empty/whitespace part
    if cell_idx >= len(parts):
        return line + lend  # can't locate; return unchanged

    old_cell = parts[cell_idx]
    # Preserve left/right padding (spaces around content)
    lpad = len(old_cell) - len(old_cell.lstrip(' '))
    rpad = len(old_cell) - len(old_cell.rstrip(' '))
    padded = ' ' * lpad + new_value + ' ' * rpad
    # If new value is wider, accept it (don't truncate)
    parts[cell_idx] = padded
    result = '|'.join(parts).replace(PLACEHOLDER, r'\|')
    return result + lend
```

- [ ] **Step 3: Verify import**

```
python -c "import sys; sys.path.insert(0,'helden/_tools'); from writers.held_writer import patch, etag_for; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Commit**

```
git add helden/_tools/writers/__init__.py helden/_tools/writers/held_writer.py
git commit -m "feat: held_writer.py — format-preserving surgical markdown write-back"
```

---

## Task 6: Tests for held_writer.py

**Files:**
- Create: `helden/_tools/tests/__init__.py`
- Create: `helden/_tools/tests/test_held_writer.py`

Tests prove the writer is correct before we wire it into the API. Each test patches a cell, re-parses, checks the value changed AND all other lines are byte-identical.

- [ ] **Step 1: Create the tests package**

Create `helden/_tools/tests/__init__.py` as an empty file.

- [ ] **Step 2: Create test_held_writer.py**

```python
"""Tests for held_writer — format-preserving surgical markdown write-back."""
import sys
from pathlib import Path
import pytest

# Add tools dir to path
TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import parse_md_table, parse_frontmatter, split_sections
from writers.held_writer import (
    _patch_frontmatter,
    _patch_table_cell,
    _find_section_lines,
    _find_first_table,
)

# ---------------------------------------------------------------------------
# Fixtures — minimal markdown fragments (not real vault files)
# ---------------------------------------------------------------------------

FM_TEXT = """\
---
wunden: 0
ap_verfuegbar: 5
---

## Eigenschaften & Basiswerte

### Basiswerte

| Basiswert | Formel | Mod. | Start | Max | Akt. | Gekauft | Rest |
|-----------|--------|------|-------|-----|------|---------|------|
| Lebensenergie (LE) | (KO+KO+KK)/2 | +9 | 19 | 28 | 28 | 0 | 7 |
| Ausdauer (AU) | (MU+KO+GE)/2 | +12 | 19 | 31 | 31 | 0 | 13 |
| Astralenergie (AE) | (MU+IN+CH)/2 | +18 | 20 | 38 | 38 | 0 | 13 |
"""

MULTI_TABLE_TEXT = """\
## Stabzauber (9 Rituale)

| Stabzauber | Vol | Effekt (Kurzform) |
|---|---|---|
| Bindung | 3 | Stab binden |

### Zauberspeicher-Inhalt

| Slot | AsP | Gespeicherter Zauber | Erschwernis-Mods | Letzte Erneuerung |
|------|-----|---------------------|------------------|-------------------|
| 1 | 5 | Armatrutz | — | 2024-01-01 |
| 2 | 0 | — | — | — |
"""


# ---------------------------------------------------------------------------
# Frontmatter tests
# ---------------------------------------------------------------------------

def test_patch_frontmatter_integer():
    new_text, old = _patch_frontmatter(FM_TEXT, 'wunden', '2')
    assert old == '0'
    fm, _ = parse_frontmatter(new_text)
    assert fm['wunden'] == 2


def test_patch_frontmatter_preserves_other_keys():
    new_text, _ = _patch_frontmatter(FM_TEXT, 'wunden', '1')
    fm, _ = parse_frontmatter(new_text)
    assert fm['ap_verfuegbar'] == 5


def test_patch_frontmatter_key_not_found_returns_none():
    result, _ = _patch_frontmatter(FM_TEXT, 'nonexistent_key', '99')
    assert result is None


def test_patch_frontmatter_only_one_line_changes():
    new_text, _ = _patch_frontmatter(FM_TEXT, 'wunden', '3')
    orig_lines = FM_TEXT.splitlines()
    new_lines = new_text.splitlines()
    assert len(orig_lines) == len(new_lines), "Line count must not change"
    changed = [i for i, (a, b) in enumerate(zip(orig_lines, new_lines)) if a != b]
    assert len(changed) == 1, f"Exactly one line should change; changed: {changed}"


# ---------------------------------------------------------------------------
# Table cell tests
# ---------------------------------------------------------------------------

def test_patch_table_cell_le_aktuell():
    new_text, old = _patch_table_cell(
        FM_TEXT,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Lebensenergie (LE)'},
        column='Akt.',
        value='21',
    )
    assert old == '28'
    assert new_text is not None
    # Re-parse and verify
    _, body = parse_frontmatter(new_text)
    h2 = split_sections(body, 2)
    h3 = split_sections(h2['Eigenschaften & Basiswerte'], 3)
    rows = parse_md_table(h3['Basiswerte'])
    le_row = next(r for r in rows if 'Lebensenergie' in r.get('Basiswert', ''))
    assert le_row['Akt.'] == '21'


def test_patch_table_cell_only_one_line_changes():
    new_text, _ = _patch_table_cell(
        FM_TEXT,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Ausdauer (AU)'},
        column='Akt.',
        value='15',
    )
    assert new_text is not None
    orig_lines = FM_TEXT.splitlines()
    new_lines = new_text.splitlines()
    assert len(orig_lines) == len(new_lines)
    changed = [i for i, (a, b) in enumerate(zip(orig_lines, new_lines)) if a != b]
    assert len(changed) == 1


def test_patch_table_cell_nested_h3():
    """Targeting a cell in a H3 sub-table (Zauberspeicher-Inhalt)."""
    new_text, old = _patch_table_cell(
        MULTI_TABLE_TEXT,
        section_path=['Stabzauber (9 Rituale)', 'Zauberspeicher-Inhalt'],
        row_key={'column': 'Slot', 'match': '1'},
        column='AsP',
        value='3',
    )
    assert old == '5'
    assert new_text is not None
    h2 = split_sections(new_text, 2)
    h3 = split_sections(h2['Stabzauber (9 Rituale)'], 3)
    rows = parse_md_table(h3['Zauberspeicher-Inhalt'])
    assert rows[0]['AsP'] == '3'


def test_patch_table_cell_row_not_found_returns_none():
    result, _ = _patch_table_cell(
        FM_TEXT,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Nonexistent Row'},
        column='Akt.',
        value='99',
    )
    assert result is None


def test_patch_table_cell_crlf_preserved():
    crlf_text = FM_TEXT.replace('\n', '\r\n')
    new_text, _ = _patch_table_cell(
        crlf_text,
        section_path=['Eigenschaften & Basiswerte', 'Basiswerte'],
        row_key={'column': 'Basiswert', 'match': 'Lebensenergie (LE)'},
        column='Akt.',
        value='20',
    )
    assert new_text is not None
    assert '\r\n' in new_text, "CRLF line endings must be preserved"
```

- [ ] **Step 3: Run all writer tests**

```
python -m pytest helden/_tools/tests/test_held_writer.py -v
```

Expected: all 8 tests PASS. If any fail, fix `held_writer.py` before continuing.

- [ ] **Step 4: Commit**

```
git add helden/_tools/tests/__init__.py helden/_tools/tests/test_held_writer.py
git commit -m "test: held_writer round-trip and edge-case tests"
```

---

## Task 7: Build the Flask server (server.py)

**Files:**
- Create: `helden/_tools/server.py`

The server live-renders `GET /` from markdown, exposes the JSON API, and watches .md files for external changes (replacing the old livereload approach).

- [ ] **Step 1: Create server.py**

```python
"""Flask server for the interactive DSA hero dashboard.

Serves the dashboard live-rendered from markdown and exposes a
PATCH /api/held/<slug>/value endpoint as the single write path.
"""
import sys
import threading
import webbrowser
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
STATIC_DIR = TOOLS_DIR / 'static'
sys.path.insert(0, str(TOOLS_DIR))

from flask import Flask, jsonify, request
from parsers.held import load_held
from parsers.kampagne import load_kampagne
from rendering import make_env           # shared Jinja helpers — no duplication
from writers.held_writer import patch, etag_for, mtime_map


def _render_dashboard(slug: str) -> str:
    held = load_held(VAULT_ROOT, slug)
    kampagne = load_kampagne(VAULT_ROOT, 'drachenchronik')
    env = make_env()
    return env.get_template('dashboard.html.j2').render(
        held=held, kampagne=kampagne, slug=slug
    )


def create_app(slug: str) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path='/static')

    # ------------------------------------------------------------------ #
    # Page routes
    # ------------------------------------------------------------------ #

    @app.route('/')
    def index():
        return _render_dashboard(slug)

    @app.route('/held/<path:s>')
    def held_page(s):
        return _render_dashboard(s)

    # ------------------------------------------------------------------ #
    # API: read
    # ------------------------------------------------------------------ #

    @app.route('/api/held/<slug_param>')
    def api_held(slug_param):
        try:
            held = load_held(VAULT_ROOT, slug_param)
            kampagne = load_kampagne(VAULT_ROOT, 'drachenchronik')
            return jsonify({'held': held, 'kampagne': kampagne})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500

    @app.route('/api/held/<slug_param>/mtime')
    def api_mtime(slug_param):
        return jsonify(mtime_map(VAULT_ROOT, slug_param))

    @app.route('/api/held/<slug_param>/etag')
    def api_etag(slug_param):
        rel_file = request.args.get('file', '_illaen.md')
        try:
            return jsonify({'etag': etag_for(VAULT_ROOT, slug_param, rel_file)})
        except FileNotFoundError:
            return jsonify({'error': 'not found'}), 404

    # ------------------------------------------------------------------ #
    # API: write (THE single mutation path)
    # ------------------------------------------------------------------ #

    @app.route('/api/held/<slug_param>/value', methods=['PATCH'])
    def api_patch_value(slug_param):
        locator = request.get_json(force=True)
        if not locator:
            return jsonify({'error': 'missing JSON body'}), 400
        result = patch(VAULT_ROOT, slug_param, locator)
        if not result.ok:
            status = 409 if result.error == 'conflict' else 400
            return jsonify({
                'ok': False,
                'error': result.error,
                'current_value': result.old_value,
            }), status
        return jsonify({
            'ok': True,
            'old': result.old_value,
            'new': result.new_value,
            'mtime': result.mtime_after,
        })

    return app


def run_server(slug: str, port: int = 5500, open_browser: bool = False) -> None:
    app = create_app(slug)
    if open_browser:
        def _open():
            import time
            time.sleep(0.8)
            webbrowser.open(f'http://localhost:{port}/')
        threading.Thread(target=_open, daemon=True).start()
    print(f'[server] DSA Dashboard at http://localhost:{port}/ — Ctrl-C to stop')
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
```

- [ ] **Step 2: Run the server and verify it starts**

```
python helden/_tools/render-held.py serve illaen-baernhold
```

Expected: prints `[server] DSA Dashboard at http://localhost:5500/ — Ctrl-C to stop`. Open `http://localhost:5500/` in a browser — the full dashboard loads (same visual as the static file). Stop with Ctrl-C.

- [ ] **Step 3: Verify API endpoints with curl**

```
curl -s http://localhost:5500/api/held/illaen-baernhold/mtime
```

Expected: JSON object with filename → mtime float entries, e.g. `{"_illaen.md": 1748600000.0, ...}`.

```
curl -s http://localhost:5500/api/held/illaen-baernhold/etag?file=_illaen.md
```

Expected: `{"etag": "<32-char hex string>"}`.

(Run server in background for curl tests, then stop it.)

- [ ] **Step 4: Commit**

```
git add helden/_tools/server.py
git commit -m "feat: Flask server with live render and PATCH write-back API"
```

---

## Task 8: Test the PATCH endpoint end-to-end

- [ ] **Step 1: Run server in background and send a PATCH**

Start the server in one terminal:
```
python helden/_tools/render-held.py serve illaen-baernhold
```

In a second terminal, send a PATCH to change current LeP from 28 to 21:
```
curl -s -X PATCH http://localhost:5500/api/held/illaen-baernhold/value \
  -H "Content-Type: application/json" \
  -d "{\"kind\":\"table_cell\",\"file\":\"_illaen.md\",\"section_path\":[\"Eigenschaften & Basiswerte\",\"Basiswerte\"],\"row_key\":{\"column\":\"Basiswert\",\"match\":\"Lebensenergie (LE)\"},\"column\":\"Akt.\",\"value\":\"21\"}"
```

Expected response: `{"ok": true, "old": "28", "new": "21", "mtime": <float>}`

- [ ] **Step 2: Verify markdown changed**

```
git diff helden/illaen-baernhold/_illaen.md
```

Expected: exactly one line changed — the `Lebensenergie (LE)` row, only the `Akt.` cell shows `21` instead of `28`. No other changes.

- [ ] **Step 3: Verify reload shows new value**

Reload `http://localhost:5500/` in the browser. The LeP current value should be 21 (the bar shows 21/28).

- [ ] **Step 4: Reset the value**

```
curl -s -X PATCH http://localhost:5500/api/held/illaen-baernhold/value \
  -H "Content-Type: application/json" \
  -d "{\"kind\":\"table_cell\",\"file\":\"_illaen.md\",\"section_path\":[\"Eigenschaften & Basiswerte\",\"Basiswerte\"],\"row_key\":{\"column\":\"Basiswert\",\"match\":\"Lebensenergie (LE)\"},\"column\":\"Akt.\",\"value\":\"28\"}"
```

- [ ] **Step 5: Test the conflict (409) path**

Send a PATCH with a fake etag:
```
curl -s -X PATCH http://localhost:5500/api/held/illaen-baernhold/value \
  -H "Content-Type: application/json" \
  -d "{\"kind\":\"frontmatter\",\"file\":\"_illaen.md\",\"key\":\"wunden\",\"value\":\"1\",\"etag\":\"deadbeefdeadbeefdeadbeefdeadbeef\"}"
```

Expected: `{"ok": false, "error": "conflict", ...}` with HTTP 409.

- [ ] **Step 6: Commit (if markdown was changed, reset first)**

```
git checkout helden/illaen-baernhold/_illaen.md
git add helden/_tools/server.py
git commit -m "test: PATCH endpoint end-to-end verified"
```

---

## Task 9: Add interactive vitals to the dashboard template

**Files:**
- Modify: `helden/_tools/templates/dashboard.html.j2`
- Create: `helden/_tools/static/app.js`

This task makes LeP/AsP/AuP interactive steppers in the browser that PATCH the server on change. The existing visual design is preserved; we only change the vitals widget markup and add a CSS block + the `app.js` script tag.

First, read the vitals section of the template to understand the current markup (the widget that renders LE/AE/AU bars — search for `le.aktuell` or `Lebensenergie` in the template).

- [ ] **Step 1: Read the current vitals markup in the template**

Open `helden/_tools/templates/dashboard.html.j2` and find the section that renders LeP/AsP/AuP bars (search for `le.aktuell`). Note the exact line numbers and surrounding HTML structure.

- [ ] **Step 2: Replace vitals bar inner content with interactive steppers**

For **each** of the three vitals (LE, AE, AU), the existing static text like:
```html
<b>{{ bw.aktuell }}</b> / {{ bw.aktuell }}
```
…and the bar's static `width` style must be replaced. The exact markup will differ by template; the pattern to apply is:

For each vital widget (use the real variable names from the template, e.g. `held.basiswerte.LE`):
1. Replace the static number display with a stepper control:
```html
<div class="vital-stepper" 
     data-locator='{"kind":"table_cell","file":"_illaen.md","section_path":["Eigenschaften &amp; Basiswerte","Basiswerte"],"row_key":{"column":"Basiswert","match":"Lebensenergie (LE)"},"column":"Akt.","slug":"{{ held.meta.name | lower | replace(' ','-') }}"}'
     data-max="{{ held.basiswerte.LE.max }}"
     data-current="{{ held.basiswerte.LE.current }}">
  <button class="vital-btn vital-btn--minus" aria-label="LeP verringern">−</button>
  <input class="vital-input" type="number"
         value="{{ held.basiswerte.LE.current }}"
         min="0" max="{{ held.basiswerte.LE.max }}"
         aria-label="Aktuelle Lebensenergie">
  <span class="vital-sep">/</span>
  <span class="vital-max">{{ held.basiswerte.LE.max }}</span>
  <button class="vital-btn vital-btn--plus" aria-label="LeP erhöhen">+</button>
</div>
```
2. Update the bar's `width` style from `100%` to use a Jinja expression:
```html
style="width: {{ (held.basiswerte.LE.current / held.basiswerte.LE.max * 100) | round | int }}%"
```

Do the same substitution for `AE` (Astralenergie) and `AU` (Ausdauer), adjusting the `data-locator` `match` field to `"Astralenergie (AE)"` and `"Ausdauer (AU)"` respectively, and the `aria-label` texts.

Note: The `slug` value in `data-locator` should be `illaen-baernhold` hardcoded or derived from `held.meta.name`. It's safer to hardcode it in the template as the Jinja `{{ slug }}` variable passed from the render context — add `slug=slug` to the `template.render()` call in both `render-held.py` and `server.py` (pass the slug string that was used to load the hero).

- [ ] **Step 3: Add interactive CSS block to the template's `<style>` section**

Append the following block just before the closing `</style>` tag:

```css
/* ── Interactive vitals ──────────────────────────────────── */
.vital-stepper {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
}
.vital-btn {
  width: 44px;
  height: 44px;
  font-size: 1.4rem;
  line-height: 1;
  border: 1.5px solid var(--accent, #8b7355);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  touch-action: manipulation;
  transition: background 0.15s;
}
.vital-btn:active { background: rgba(139,115,85,0.2); }
.vital-input {
  width: 52px;
  font-size: 1.2rem;
  font-weight: 700;
  text-align: center;
  border: 1.5px solid var(--accent, #8b7355);
  border-radius: 4px;
  background: transparent;
  color: inherit;
  padding: 4px 2px;
  -moz-appearance: textfield;
}
.vital-input::-webkit-inner-spin-button,
.vital-input::-webkit-outer-spin-button { -webkit-appearance: none; }
.vital-sep, .vital-max { opacity: 0.7; font-size: 1rem; }
/* Save indicator */
#save-indicator {
  position: fixed;
  bottom: 16px;
  right: 16px;
  background: rgba(0,0,0,0.75);
  color: #fff;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  opacity: 0;
  transition: opacity 0.3s;
  pointer-events: none;
  z-index: 9999;
}
#save-indicator.visible { opacity: 1; }
/* Wunden counter */
.wunden-counter {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}
.wunden-counter button {
  width: 44px; height: 44px;
  border: 1.5px solid var(--accent, #8b7355);
  border-radius: 6px;
  background: transparent;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
  touch-action: manipulation;
}
/* Sticky mini-vitals on small screens */
@media (max-width: 900px) {
  .vitals-sticky {
    position: sticky;
    top: 0;
    background: var(--bg, #fdf6e3);
    z-index: 100;
    padding: 6px 12px;
    border-bottom: 1px solid var(--accent, #8b7355);
    display: flex;
    gap: 16px;
    font-weight: 700;
    font-size: 0.95rem;
  }
}
@media (min-width: 901px) { .vitals-sticky { display: none; } }
@media print {
  .vital-btn, .vital-input, #save-indicator, .vitals-sticky { display: none !important; }
  .vital-max { font-weight: 700; }
}
```

- [ ] **Step 4: Add save-indicator div and app.js script tag before closing </body>**

Just before `</body>`:
```html
<div id="save-indicator">gespeichert ✓</div>
<script src="/static/app.js"></script>
```

(Keep the existing inline spell-sort `<script>` block above it — don't remove it.)

- [ ] **Step 5: Create static/app.js**

```javascript
/**
 * app.js — Interactive dashboard: debounced PATCH to Flask server.
 * Runs when served via server.py (http://localhost:5500).
 * Degrades gracefully when opened as file:// (no interactive behaviour).
 */

const IS_SERVED = location.protocol === 'http:' || location.protocol === 'https:';
if (!IS_SERVED) {
  // Static file — bail out, everything is read-only
  console.info('[dsa-dashboard] static mode — interactive features disabled');
} else {
  initDashboard();
}

function initDashboard() {
  const DEBOUNCE_MS = 1600;
  const POLL_INTERVAL_MS = 8000;  // check for external Obsidian edits

  const indicator = document.getElementById('save-indicator');
  let indicatorTimer = null;

  // ── Save indicator ──────────────────────────────────────────────────
  function showIndicator(text, isError) {
    if (!indicator) return;
    indicator.textContent = text;
    indicator.style.background = isError ? 'rgba(180,40,40,0.85)' : 'rgba(0,0,0,0.75)';
    indicator.classList.add('visible');
    clearTimeout(indicatorTimer);
    indicatorTimer = setTimeout(() => indicator.classList.remove('visible'), 2500);
  }

  // ── PATCH helper ───────────────────────────────────────────────────
  async function sendPatch(locator) {
    showIndicator('speichern…', false);
    try {
      const resp = await fetch(`/api/held/${locator.slug}/value`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(locator),
      });
      const data = await resp.json();
      if (resp.status === 409) {
        showIndicator('Konflikt — Seite neu laden', true);
        if (confirm('Die Quelldatei wurde extern geändert. Seite neu laden?')) {
          location.reload();
        }
        return false;
      }
      if (!resp.ok || !data.ok) {
        showIndicator('Fehler: ' + (data.error || resp.status), true);
        return false;
      }
      showIndicator('gespeichert ✓', false);
      return true;
    } catch (err) {
      showIndicator('Netzwerkfehler', true);
      return false;
    }
  }

  // ── Debounced PATCH per element ────────────────────────────────────
  const debounceTimers = new WeakMap();

  function schedulePatch(el, locator, value) {
    clearTimeout(debounceTimers.get(el));
    debounceTimers.set(el, setTimeout(() => {
      sendPatch({ ...locator, value: String(value) });
    }, DEBOUNCE_MS));
  }

  // ── Vital steppers ─────────────────────────────────────────────────
  document.querySelectorAll('.vital-stepper').forEach(stepper => {
    const rawLocator = JSON.parse(stepper.dataset.locator);
    const max = parseInt(stepper.dataset.max, 10);
    const input = stepper.querySelector('.vital-input');
    const minusBtn = stepper.querySelector('.vital-btn--minus');
    const plusBtn = stepper.querySelector('.vital-btn--plus');

    if (!input) return;

    function clamp(v) { return Math.max(0, Math.min(max, v)); }

    function setValue(v, patch = true) {
      const clamped = clamp(v);
      input.value = clamped;
      // Update bar width
      const bar = stepper.closest('.vital-card, .vital-block, [class*="vitalia"]')
        ?.querySelector('[class*="bar"], .bar, .hp-bar, .ap-bar, .au-bar');
      if (bar) bar.style.width = Math.round(clamped / max * 100) + '%';
      if (patch) schedulePatch(stepper, rawLocator, clamped);
    }

    minusBtn?.addEventListener('click', () => setValue(parseInt(input.value, 10) - 1));
    plusBtn?.addEventListener('click', () => setValue(parseInt(input.value, 10) + 1));
    input.addEventListener('change', () => setValue(parseInt(input.value, 10) || 0));
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') setValue(parseInt(input.value, 10) || 0);
    });
  });

  // ── Flush on page unload ───────────────────────────────────────────
  window.addEventListener('beforeunload', () => {
    // Fire any pending patches immediately (best-effort)
    document.querySelectorAll('.vital-stepper').forEach(el => {
      const timer = debounceTimers.get(el);
      if (timer) {
        clearTimeout(timer);
        const locator = JSON.parse(el.dataset.locator);
        const val = el.querySelector('.vital-input')?.value;
        if (val != null) {
          navigator.sendBeacon(
            `/api/held/${locator.slug}/value`,
            JSON.stringify({ ...locator, value: val })
          );
        }
      }
    });
  });

  // ── Mtime polling: detect external Obsidian edits ─────────────────
  let lastMtimes = {};
  async function pollMtimes() {
    // Determine slug from a stepper's locator or from the URL
    const stpr = document.querySelector('.vital-stepper');
    if (!stpr) return;
    const slug = JSON.parse(stpr.dataset.locator).slug || 'illaen-baernhold';
    try {
      const resp = await fetch(`/api/held/${slug}/mtime`);
      const mtimes = await resp.json();
      if (Object.keys(lastMtimes).length === 0) {
        lastMtimes = mtimes;
        return;
      }
      const changed = Object.entries(mtimes).some(([k, v]) => lastMtimes[k] && v > lastMtimes[k]);
      if (changed) {
        lastMtimes = mtimes;
        showIndicator('Quelldatei geändert — neu laden empfohlen', false);
      }
    } catch (_) { /* server not reachable — ignore */ }
  }
  setInterval(pollMtimes, POLL_INTERVAL_MS);
}
```

- [ ] **Step 6: Ensure the static directory is served by Flask**

The `create_app` in `server.py` already sets `static_folder=str(STATIC_DIR)`. Create the static dir if it doesn't exist:

```
mkdir helden/_tools/static
```

- [ ] **Step 7: Start server and verify interactive vitals**

```
python helden/_tools/render-held.py serve illaen-baernhold --open
```

In the browser:
- Click the `−` button next to LeP → value decrements by 1, bar narrows.
- After ~1.5s quiet, "gespeichert ✓" appears bottom-right.
- Check `git diff helden/illaen-baernhold/_illaen.md` — only the `Akt.` cell of the LE row changed.
- Type a value directly into the LeP input field → change is saved.

- [ ] **Step 8: Commit**

```
git add helden/_tools/templates/dashboard.html.j2 helden/_tools/static/app.js
git commit -m "feat: interactive vitals steppers (LeP/AsP/AuP) with PATCH write-back"
```

---

## Task 10: Session-state module (Zustände, Wunden overlay)

**Files:**
- Create: `helden/_tools/static/session.js`

This module handles Tier-B transient state: Zustände chips, temp mods. Wunden persist to markdown (Tier A via PATCH) but the *effect overlay* is computed client-side from the persisted wunden count.

- [ ] **Step 1: Create session.js**

```javascript
/**
 * session.js — Tier-B transient state (Zustände, temp mods) in localStorage.
 * Key: dsa:<slug>:session  →  { zustaende: [...], tempMods: [] }
 *
 * Wunden count persists to markdown (see app.js). This file only manages
 * the *overlay display* of wunden effects (AT/PA penalties etc.).
 */

const IS_SERVED = location.protocol === 'http:' || location.protocol === 'https:';
if (IS_SERVED) initSession();

function initSession() {
  // Derive slug from a vital-stepper or fall back
  const stpr = document.querySelector('.vital-stepper');
  const slug = stpr ? JSON.parse(stpr.dataset.locator).slug : 'illaen-baernhold';
  const STORAGE_KEY = `dsa:${slug}:session`;

  function loadState() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); }
    catch { return {}; }
  }

  function saveState(state) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  // DSA 4.1 Wundregeln overlay
  // Wundschwelle = KO/2 (round up). Each wound beyond threshold = -2 to all skill checks.
  // Source: DSA4.1 Regelwerk. Verify exact thresholds in wiki/dsa-4.1/ before shipping.
  const KO_EL = document.querySelector('[data-eigenschaft="KO"]');
  const KO_VAL = KO_EL ? parseInt(KO_EL.dataset.wert, 10) : 13;  // Illaen's KO=13
  const WUNDSCHWELLE = Math.ceil(KO_VAL / 2);  // = 7 for KO 13

  function computeWundPenalty(wunden) {
    if (wunden <= 0) return 0;
    // Each wound beyond threshold inflicts -2 cumulative
    // First wound: penalty if wunden >= 1 AND damage >= Wundschwelle
    // Simplified: 1 wound = -2, 2 wounds = -4, 3 wounds = -6
    // TODO: verify exact DSA 4.1 rules in wiki before shipping
    return wunden * 2;
  }

  // Render Wunden widget (injected into the vitals area)
  function renderWundenWidget() {
    const existing = document.getElementById('wunden-widget');
    if (existing) return;  // already rendered

    const wundenEl = document.querySelector('[data-wunden]');
    if (!wundenEl) return;
    const currentWunden = parseInt(wundenEl.dataset.wunden, 10) || 0;

    const widget = document.createElement('div');
    widget.id = 'wunden-widget';
    widget.className = 'wunden-counter';
    widget.innerHTML = `
      <span>Wunden:</span>
      <button id="wunden-minus" aria-label="Wunde heilen">−</button>
      <span id="wunden-count" style="font-weight:700;font-size:1.2rem">${currentWunden}</span>
      <button id="wunden-plus" aria-label="Wunde erleiden">+</button>
      <span id="wunden-penalty" style="opacity:0.7;font-size:0.9rem">(−${computeWundPenalty(currentWunden)} auf Proben)</span>
    `;
    wundenEl.insertAdjacentElement('afterend', widget);

    document.getElementById('wunden-minus')?.addEventListener('click', () => changeWunden(-1));
    document.getElementById('wunden-plus')?.addEventListener('click', () => changeWunden(+1));
  }

  function changeWunden(delta) {
    const countEl = document.getElementById('wunden-count');
    const penaltyEl = document.getElementById('wunden-penalty');
    const wundenEl = document.querySelector('[data-wunden]');
    if (!countEl || !wundenEl) return;

    const current = parseInt(countEl.textContent, 10);
    const next = Math.max(0, current + delta);
    countEl.textContent = next;
    if (penaltyEl) penaltyEl.textContent = `(−${computeWundPenalty(next)} auf Proben)`;
    wundenEl.dataset.wunden = next;

    // Persist wunden to markdown via PATCH
    const stpr2 = document.querySelector('.vital-stepper');
    if (!stpr2) return;
    const baseLocator = JSON.parse(stpr2.dataset.locator);
    fetch(`/api/held/${baseLocator.slug}/value`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        kind: 'frontmatter',
        file: '_illaen.md',
        key: 'wunden',
        value: String(next),
        slug: baseLocator.slug,
      }),
    }).catch(console.error);
  }

  // Zustände (transient overlay only — never persisted to markdown)
  const ZUSTAENDE = [
    { key: 'schmerz', label: 'Schmerz', mod: -2 },
    { key: 'furcht', label: 'Furcht', mod: -2 },
    { key: 'betaeubt', label: 'Betäubt', mod: -4 },
    { key: 'verwirrt', label: 'Verwirrt', mod: -2 },
    { key: 'erschoepft', label: 'Erschöpft', mod: -2 },
  ];

  function renderZustandChips() {
    const state = loadState();
    const active = new Set(state.zustaende || []);
    const container = document.getElementById('zustand-chips');
    if (!container) return;
    container.innerHTML = ZUSTAENDE.map(z => `
      <button class="zustand-chip ${active.has(z.key) ? 'active' : ''}"
              data-key="${z.key}" data-mod="${z.mod}"
              title="${z.label}: ${z.mod} auf Proben">
        ${z.label}
      </button>
    `).join('');
    container.querySelectorAll('.zustand-chip').forEach(btn => {
      btn.addEventListener('click', () => toggleZustand(btn.dataset.key));
    });
  }

  function toggleZustand(key) {
    const state = loadState();
    const active = new Set(state.zustaende || []);
    if (active.has(key)) active.delete(key); else active.add(key);
    state.zustaende = [...active];
    saveState(state);
    renderZustandChips();
  }

  // Session reset
  function resetSession() {
    if (!confirm('Transiente Zustände zurücksetzen? (Zustände, Temp-Mods)')) return;
    localStorage.removeItem(STORAGE_KEY);
    renderZustandChips();
  }

  // Init
  document.addEventListener('DOMContentLoaded', () => {
    renderWundenWidget();
    renderZustandChips();
    document.getElementById('session-reset-btn')?.addEventListener('click', resetSession);
  });
  if (document.readyState !== 'loading') {
    renderWundenWidget();
    renderZustandChips();
  }
}
```

- [ ] **Step 2: Add required HTML anchors to the template**

In `dashboard.html.j2`, find the vitals section. Add:
1. A `data-wunden` attribute to an element near the vitals:
   ```html
   <div data-wunden="{{ held.meta.wunden }}"></div>
   ```
2. A `<div id="zustand-chips"></div>` container somewhere visible (below vitals, e.g. in a "Zustände" subsection of the combat area).
3. A reset button:
   ```html
   <button id="session-reset-btn" class="print-btn" style="margin-left:8px">Session zurücksetzen</button>
   ```

- [ ] **Step 3: Add session.js script tag to the template**

After the `app.js` script tag:
```html
<script src="/static/session.js"></script>
```

- [ ] **Step 4: Verify Wunden widget and Zustände chips appear**

Start server. Load dashboard. Verify:
- A Wunden counter (−/count/+) appears below the vitals.
- 5 Zustand chips appear; clicking one toggles it active (CSS highlight).
- Clicking Wunden + sends a PATCH; `git diff _illaen.md` shows `wunden: 1` in frontmatter.
- "Session zurücksetzen" clears chip state; Wunden value stays (it's markdown-persisted).

- [ ] **Step 5: Commit**

```
git add helden/_tools/static/session.js helden/_tools/templates/dashboard.html.j2
git commit -m "feat: session.js — Zustaende chips (transient) + Wunden overlay (persistent)"
```

---

## Task 11: Update watcher.py — replace livereload with mtime token

**Files:**
- Modify: `helden/_tools/watcher.py`

The old `start_watch` used livereload, which triggers a full page reload and destroys transient session state. Replace with: on `.md` change, increment a global version token exposed at `/api/held/<slug>/mtime`. The client polls this endpoint (done in `app.js`) and shows a banner.

- [ ] **Step 1: Rewrite watcher.py**

```python
"""File-watcher for the DSA hero dashboard.

In serve mode: watching is handled implicitly (each GET / re-reads from disk).
The mtime endpoint serves as the change signal; app.js polls it.

In render mode (--watch): still triggers a full re-render to the output file.
"""
import sys
import threading
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent

_WATCH_DIRS = [
    VAULT_ROOT / 'helden',
    VAULT_ROOT / 'abenteuer',
]


class _RenderHandler(FileSystemEventHandler):
    def __init__(self, render_fn: Callable) -> None:
        self._render_fn = render_fn
        self._debounce_timer: threading.Timer | None = None

    def on_any_event(self, event):
        if event.is_directory:
            return
        path = getattr(event, 'src_path', '')
        if not path.endswith('.md'):
            return
        if self._debounce_timer:
            self._debounce_timer.cancel()
        self._debounce_timer = threading.Timer(0.3, self._do_render)
        self._debounce_timer.start()

    def _do_render(self):
        try:
            out = self._render_fn()
            print(f'[watcher] re-rendered → {out}')
        except Exception as exc:
            print(f'[watcher] render error: {exc}', file=sys.stderr)


def start_watch(slug: str, render_fn: Callable, open_browser: bool = False) -> None:
    """Start file watcher for render --watch mode (static HTML re-render on change)."""
    import webbrowser, time

    if open_browser:
        out = VAULT_ROOT / 'output' / f'{slug}-dashboard.html'
        webbrowser.open(out.as_uri())
        print(f'[watcher] opened {out.as_uri()}')

    handler = _RenderHandler(render_fn)
    observer = Observer()
    for watch_dir in _WATCH_DIRS:
        if watch_dir.exists():
            observer.schedule(handler, str(watch_dir), recursive=True)
            print(f'[watcher] watching {watch_dir}')

    observer.start()
    print('[watcher] press Ctrl-C to stop')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print('[watcher] stopped')
```

- [ ] **Step 2: Verify render --watch still works**

```
python helden/_tools/render-held.py illaen-baernhold --watch
```

Expected: starts watching, `Ctrl-C` stops cleanly. (Test by touching a `.md` file — re-render should trigger.)

- [ ] **Step 3: Commit**

```
git add helden/_tools/watcher.py
git commit -m "refactor: watcher — remove livereload dependency for serve mode"
```

---

## Task 12: Final integration verification

- [ ] **Step 1: Run all writer tests**

```
python -m pytest helden/_tools/tests/ -v
```

Expected: all tests PASS.

- [ ] **Step 2: Full end-to-end test**

Start server:
```
python helden/_tools/render-held.py serve illaen-baernhold --open
```

Go through this checklist manually in the browser:
- [ ] LeP `−` button: decrements, bar narrows, "gespeichert ✓" appears
- [ ] LeP direct input (type a value + Enter): saves, bar updates
- [ ] AuP `+` button: increments, but not above max
- [ ] AE `−` then reload page: value is still at the decremented level (persisted)
- [ ] Wunden `+`: wunden count increments, penalty text updates, `git diff _illaen.md` shows frontmatter changed
- [ ] Schmerz Zustand chip: toggled, orange/highlighted; survives tab switch
- [ ] "Session zurücksetzen": clears Zustände chip state; Wunden value unchanged
- [ ] `git diff` overview: only `_illaen.md` has changes

- [ ] **Step 3: Verify static output still works (graceful degrade)**

```
python helden/_tools/render-held.py illaen-baernhold --open
```

Open `output/illaen-baernhold-dashboard.html` as file://. Dashboard loads visually intact; no JS errors; no interactive controls visible (print-only mode).

- [ ] **Step 4: Reset test values**

```
git checkout helden/illaen-baernhold/_illaen.md
```

- [ ] **Step 5: Final commit**

```
git add -A
git status  # verify only expected files
git commit -m "feat(phase-1): interactive dashboard complete — live vitals, Wunden, Zustände"
```

---

## Summary

After these 12 tasks, you have:
- A Flask server (`python helden/_tools/render-held.py serve illaen-baernhold`) that live-renders the dashboard
- LeP, AsP, AuP as interactive steppers that write back surgically to `_illaen.md`
- Wunden counter persisted to frontmatter; Zustände as transient browser chips
- Conflict protection (409) if Obsidian modifies the file concurrently
- All existing functionality preserved: `render` subcommand, `--watch`, print stylesheet, static output

**Next plans (separate):**
- `2026-XX-XX-dice-integration.md` — Phase 2: 3W20 auto-roll + manual entry
- `2026-XX-XX-ap-steigerung.md` — Phase 3: AP spend + Steigerungs-Log
- `2026-XX-XX-inventory.md` — Phase 4: Inventar/Geld/Stab-Zauberspeicher
