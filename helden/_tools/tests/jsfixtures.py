"""Gemeinsame Helfer fuer Tests, die static/*.js per node ausfuehren oder Funktionen daraus herausloesen.

Nur die echten Duplikate leben hier (Marker, Funktionsextraktion, node-Aufruf). Die JS-Runner-Skripte selbst
(Fake-DOMs, vm-Kontexte) unterscheiden sich pro Testdatei und bleiben dort."""
import json
import re
import shutil
import subprocess

import pytest

needs_node = pytest.mark.skipif(shutil.which('node') is None, reason='node nicht installiert')


def _locate_function(src, name):
    """(Match der Kopfzeile, Endindex hinter der schliessenden Klammer) von 'function <name>(...) { ... }'.

    Klammer-Zaehlung: nur fuer Funktionskoerper ohne '{'/'}' in Strings, Kommentaren oder Regex-Literalen;
    die Parameterliste darf kein ')' enthalten (z. B. keinen Default-Wert mit Aufruf)."""
    m = re.search(r'function\s+' + re.escape(name) + r'\s*\(([^)]*)\)\s*\{', src)
    assert m, f'{name} fehlt'
    depth, i = 1, m.end()
    while depth:
        assert i < len(src), f'{name}: Klammern nicht ausgeglichen'
        depth += {'{': 1, '}': -1}.get(src[i], 0)
        i += 1
    return m, i


def js_function(src, name):
    """Ganzer Quelltext von 'function <name>(...) { ... }'."""
    m, end = _locate_function(src, name)
    return src[m.start():end]


def js_function_body(src, name):
    """(Parameterliste, Koerper) der Funktion <name>."""
    m, end = _locate_function(src, name)
    return m.group(1), src[m.end():end - 1]


def run_node(script, *args):
    """Fuehrt `node -e <script> <args...>` aus (Exit-Code 0 erwartet, sonst stderr als Meldung) und liefert das geparste JSON von stdout."""
    proc = subprocess.run(
        ['node', '-e', script, *map(str, args)],
        capture_output=True, text=True, encoding='utf-8', timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)
