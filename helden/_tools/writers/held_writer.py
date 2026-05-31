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
from dataclasses import dataclass
from pathlib import Path

# Import the same helpers the parser uses, so locator semantics stay consistent
import sys
_HERE = Path(__file__).parent.parent
sys.path.insert(0, str(_HERE))
from parsers.held import (_split_table_row, strip_wikilink)

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
        mtime_before = target.stat().st_mtime
        raw = target.read_bytes()
        text = raw.decode('utf-8-sig')  # handle optional BOM

        # Optimistic concurrency: check etag if caller provided one
        etag = locator.get('etag', '')
        if etag:
            actual_etag = hashlib.md5(raw).hexdigest()
            if actual_etag != etag:
                return PatchResult(ok=False, old_value='', new_value='',
                                   mtime_before=mtime_before, mtime_after=mtime_before,
                                   error='conflict')

        try:
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
            elif kind == 'table_append_row':
                new_text, old_value = _append_table_row(
                    text,
                    section_path=locator.get('section_path', []),
                    cells=locator.get('cells', []),
                )
            else:
                return PatchResult(ok=False, old_value='', new_value='',
                                   mtime_before=mtime_before, mtime_after=mtime_before,
                                   error=f'unknown locator kind: {kind}')
        except (KeyError, TypeError) as exc:
            return PatchResult(ok=False, old_value='', new_value='',
                               mtime_before=mtime_before, mtime_after=mtime_before,
                               error=f'bad locator: {exc}')

        new_value_str = str(locator.get('value', ''))
        if new_text is None:
            return PatchResult(ok=False, old_value=old_value, new_value=new_value_str,
                               mtime_before=mtime_before, mtime_after=mtime_before,
                               error='cell not found')

        # Atomic write: temp file in same dir + os.replace
        tmp = target.with_suffix('.tmp_patch')
        tmp.write_bytes(new_text.encode('utf-8'))
        os.replace(tmp, target)

        mtime_after = target.stat().st_mtime
        return PatchResult(ok=True, old_value=old_value,
                           new_value=new_value_str,
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


def _append_table_row(
    text: str,
    section_path: list[str],
    cells: list[str],
) -> tuple[str | None, str]:
    """Append a new data row to the first table found in section_path.

    Returns (new_text, '') on success, (None, '') if section or table not found.
    """
    if not cells:
        return None, ''
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
