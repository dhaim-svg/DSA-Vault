"""Regression guard: classic <script> tags share one global lexical scope, so the same
top-level name declared in two static/*.js files is a SyntaxError (const/let/class) or a
silent overwrite (var/function). Pure-Python scan, no JS engine needed."""
import re
from collections import defaultdict
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
STATIC_DIR = TOOLS_DIR / 'static'

_REGEX_PREV = set('(,=:[!&|?{};+-*%<>~^') | {''}
_IDENT = r'[A-Za-z_$][\w$]*'
_DECL_FN = re.compile(r'^\s*(?:async\s+)?function\s*\*?\s*(' + _IDENT + r')')
_DECL_VAR = re.compile(r'^\s*(?:const|let|var)\s+(.*)$', re.S)
_DECL_CLASS = re.compile(r'^\s*class\s+(' + _IDENT + r')')


def strip_js(src):
    """Blank out comments, strings, template literals and regex literals (keeps newlines)."""
    out = []
    i, n = 0, len(src)
    last_sig = ''
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ''
        if c == '/' and nxt == '/':
            while i < n and src[i] != '\n':
                i += 1
        elif c == '/' and nxt == '*':
            end = src.find('*/', i + 2)
            end = n if end == -1 else end + 2
            out.append('\n' * src.count('\n', i, end))
            i = end
        elif c in '\'"':
            i += 1
            while i < n and src[i] != c and src[i] != '\n':
                i += 2 if src[i] == '\\' else 1
            i += 1
            out.append('""')
            last_sig = '"'
        elif c == '`':
            i, nl = _skip_template(src, i)
            out.append('""' + '\n' * nl)
            last_sig = '"'
        elif c == '/' and last_sig in _REGEX_PREV:
            i += 1
            in_class = False
            while i < n and src[i] != '\n':
                if src[i] == '\\':
                    i += 2
                    continue
                if src[i] == '[':
                    in_class = True
                elif src[i] == ']':
                    in_class = False
                elif src[i] == '/' and not in_class:
                    break
                i += 1
            i += 1
            out.append('""')
            last_sig = '"'
        else:
            out.append(c)
            if not c.isspace():
                last_sig = c
            i += 1
    return ''.join(out)


def _skip_template(src, i):
    """Return (index after closing backtick, newline count); handles nested ${ ... }."""
    n = len(src)
    start = i
    i += 1
    while i < n and src[i] != '`':
        if src[i] == '\\':
            i += 2
        elif src[i] == '$' and src[i + 1:i + 2] == '{':
            depth = 1
            i += 2
            while i < n and depth:
                if src[i] == '`':
                    i, _ = _skip_template(src, i)
                    continue
                depth += (src[i] == '{') - (src[i] == '}')
                i += 1
        else:
            i += 1
    i += 1
    return i, src.count('\n', start, i)


def _pattern_names(pattern):
    """Bound names of a destructuring pattern: 'x', 'k: y' -> y, 'z = 1' -> z, nested ok."""
    names = []
    for m in re.finditer(r'(' + _IDENT + r')\s*(:\s*(' + _IDENT + r'))?\s*(?=[,}\]=]|$)', pattern):
        names.append(m.group(3) or m.group(1))
    return names


def _declarator_names(rest):
    """Names from 'a = 1, b, {c, d: e} = x;' (top-level declarators; destructuring included)."""
    pieces, piece, depth = [], [], 0
    for ch in rest:
        if ch in '{[(':
            depth += 1
        elif ch in '}])':
            depth -= 1
        if depth == 0 and ch in ';\n':
            break
        if depth == 0 and ch == ',':
            pieces.append(''.join(piece))
            piece = []
        else:
            piece.append(ch)
    pieces.append(''.join(piece))
    names = []
    for p in pieces:
        p = p.strip()
        if p[:1] in '{[':
            close = max(p.rfind('}'), p.rfind(']'))
            names.extend(_pattern_names(p[1:close]))
        else:
            m = re.match(_IDENT, p)
            if m:
                names.append(m.group(0))
    return names


def top_level_declarations(src):
    """Set of names declared at script scope (brace depth 0) in JS source."""
    text = strip_js(src)
    names = set()
    depth = 0
    for line in text.split('\n'):
        if depth == 0:
            m = _DECL_FN.match(line) or _DECL_CLASS.match(line)
            if m:
                names.add(m.group(1))
            else:
                m = _DECL_VAR.match(line)
                if m:
                    names.update(_declarator_names(m.group(1)))
        depth += line.count('{') - line.count('}')
    return names


def find_collisions(files):
    """files: {label: source}. Returns {name: sorted labels} for names declared in >1 file."""
    owners = defaultdict(set)
    for label, src in files.items():
        for name in top_level_declarations(src):
            owners[name].add(label)
    return {name: sorted(labels) for name, labels in owners.items() if len(labels) > 1}


def test_no_top_level_name_collisions_across_static_js():
    files = {p.name: p.read_text(encoding='utf-8') for p in sorted(STATIC_DIR.glob('*.js'))}
    assert files, 'no static/*.js found'
    collisions = find_collisions(files)
    msg = '\n'.join(
        f'  {name!r} declared at top level in: {", ".join(labels)}'
        for name, labels in sorted(collisions.items())
    )
    assert not collisions, (
        'Top-level names shared across classic <script> files '
        '(wrap one in an IIFE or rename):\n' + msg
    )


def test_scanner_finds_collisions_and_respects_iife():
    colliding = {
        'a.js': "const IS_SERVED = true;\nfunction helper() {}\nlet a = 1, b = 2;\nclass Foo {}\n",
        'b.js': "// const IS_SERVED = commented out\nconst IS_SERVED = false;\n"
                "async function helper() {}\nvar b;\nclass Foo { x() { const inner = 1; } }\n",
    }
    assert find_collisions(colliding) == {
        'IS_SERVED': ['a.js', 'b.js'],
        'helper': ['a.js', 'b.js'],
        'b': ['a.js', 'b.js'],
        'Foo': ['a.js', 'b.js'],
    }

    encapsulated = {
        'a.js': "const IS_SERVED = true;\nfunction helper() {}\n",
        'b.js': "(function () {\n  const IS_SERVED = false;\n  function helper() {}\n"
                "  var s = \"const IS_SERVED = 1;\";\n})();\n",
        'c.js': "const t = `const IS_SERVED = ${1 + 1}\nfunction helper() {}`;\n"
                "const re = /const IS_SERVED = {/;\nfoo(function () { var IS_SERVED; });\n",
    }
    assert find_collisions(encapsulated) == {}
