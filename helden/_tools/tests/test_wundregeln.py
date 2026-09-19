"""D-041b: Wundlogik (WdS S. 57) — Regeltabelle per node ausgefuehrt, plus Struktur-Scans.

Pro Wunde: AT/PA/FK/INI/GE -2, GS -1; Talent-/Zauber-/sonstige Eigenschaftsproben und
Schadenswuerfe bekommen keinen Wundabzug. Einzige Regelquelle: static/wundregeln.js."""
import json
import re
import shutil
import subprocess

import pytest

from rendering import JS_FILES, STATIC_DIR

WUNDREGELN_JS = STATIC_DIR / 'wundregeln.js'
SESSION_JS = STATIC_DIR / 'session.js'
DICE_JS = STATIC_DIR / 'dice.js'

needs_node = pytest.mark.skipif(shutil.which('node') is None, reason='node nicht installiert')

# -0 wird als String '-0' ausgegeben (JSON.stringify(-0) waere '0').
_NODE_RUNNER = """
const fs = require('fs'), vm = require('vm');
const ctx = { window: {} };
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), ctx);
const W = ctx.window.DSAWundregeln;
const calls = JSON.parse(process.argv[2]);
const out = calls.map(([fn, ...args]) => {
  const r = W[fn](...args);
  return Object.is(r, -0) ? '-0' : r;
});
process.stdout.write(JSON.stringify(out));
"""


def _run(*calls):
    """Ruft window.DSAWundregeln[fn](*args) fuer jedes (fn, *args) in node (ohne DOM) auf."""
    proc = subprocess.run(
        ['node', '-e', _NODE_RUNNER, str(WUNDREGELN_JS), json.dumps(calls)],
        capture_output=True, text=True, encoding='utf-8', timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


# -- Verhalten der Regeltabelle (node) ------------------------------------

@needs_node
def test_wund_mod_per_wunde_table():
    res = _run(
        ['wundMod', 0, 'AT'], ['wundMod', 1, 'AT'], ['wundMod', 1, 'PA'], ['wundMod', 2, 'GE'],
        ['wundMod', 2, 'GS'], ['wundMod', 3, 'FK'], ['wundMod', 2, 'INI'],
    )
    assert res == [0, -2, -2, -4, -2, -6, -4]


@needs_node
def test_wund_mod_ignores_everything_but_the_six_wound_targets():
    res = _run(
        ['wundMod', 2, 'MU'], ['wundMod', 2, 'KK'], ['wundMod', 5, 'talent'],
        ['wundMod', 5, 'zauber'], ['wundMod', 5, 'schaden'], ['wundMod', 5, None],
    )
    assert res == [0] * 6


@needs_node
def test_wund_mod_never_positive_and_never_negative_zero():
    res = _run(['wundMod', -3, 'AT'], ['wundMod', 0, 'AT'], ['wundMod', 2, 'MU'], ['wundMod', 0, 'GE'])
    assert res == [0, 0, 0, 0]  # '-0' (String) wuerde hier auffallen


@needs_node
def test_geltung_text_names_scope_only_when_wounded():
    leer, eins, zwei = _run(['geltungText', 0], ['geltungText', 1], ['geltungText', 2])
    assert leer == ''
    assert 'AT/PA/FK/INI/GE −2' in eins and 'GS −1' in eins
    assert 'AT/PA/FK/INI/GE −4' in zwei and 'GS −2' in zwei


# -- Struktur-Scans -------------------------------------------------------

def test_wundregeln_js_is_listed_before_its_consumers():
    assert 'wundregeln.js' in JS_FILES
    assert JS_FILES.index('wundregeln.js') < JS_FILES.index('session.js')
    assert JS_FILES.index('wundregeln.js') < JS_FILES.index('dice.js')


def test_wundregeln_js_is_a_pure_iife_exporting_dsawundregeln():
    src = WUNDREGELN_JS.read_text(encoding='utf-8')
    assert re.search(r'^\(function\s*\(\)\s*\{', src, re.M)
    assert re.search(r'window\.DSAWundregeln\s*=', src)
    assert 'document.' not in src and 'localStorage' not in src


@pytest.mark.parametrize('path', [SESSION_JS, DICE_JS], ids=lambda p: p.name)
def test_no_flat_wound_penalty_left(path):
    src = path.read_text(encoding='utf-8')
    assert 'computeWundPenalty' not in src
    assert not re.search(r'\b(?:wunden|w)\s*\*\s*2\b', src), 'pauschales Wunden*2 darf nicht mehr vorkommen'


def _function_body(src, name):
    m = re.search(r'function\s+' + name + r'\s*\(([^)]*)\)\s*\{', src)
    assert m, f'{name} fehlt'
    depth, i = 1, m.end()
    while depth:
        depth += {'{': 1, '}': -1}.get(src[i], 0)
        i += 1
    return m.group(1), src[m.end():i - 1]


def test_dice_get_wund_mod_is_scoped_by_probe_type():
    src = DICE_JS.read_text(encoding='utf-8')
    params, body = _function_body(src, 'getWundMod')
    assert params.strip(), 'getWundMod muss die Probenkonfiguration bekommen'
    assert 'probeMod(' in body and 'DSAWundregeln.wundMod(' in body
    for probe_type in ('at', 'pa', 'eigenschaft', 'talent', 'zauber'):
        assert f"'{probe_type}'" in body, f'{probe_type} nicht zugeordnet'
    call = re.search(r"getWundMod\(([^)]*)\)\s*\+\s*\(currentConfig", src)
    assert call and call.group(1).strip(), 'openPanel muss config an getWundMod uebergeben'


def test_session_exposes_scoped_queries():
    src = SESSION_JS.read_text(encoding='utf-8')
    m = re.search(r'window\.DSASession\s*=\s*\{([^}]*)\}', src)
    assert m
    for name in ('computeActiveEffects', 'probeMod', 'statMod'):
        assert name in m.group(1)


# -- dice.js getWundMod: Zuordnung Probenart -> Wundabzug (node, Funktion extrahiert) --

_DICE_RUNNER = """
const fs = require('fs'), vm = require('vm');
const wr = fs.readFileSync(process.argv[1], 'utf8');
const fn = process.argv[2];                       // Quelltext von getWundMod
const cfgs = JSON.parse(process.argv[3]);
const withSession = process.argv[4] === 'session';
const seen = [];
const window = {};
vm.runInNewContext(wr, { window });
const ctx = {
  window,
  document: { querySelector: () => ({ dataset: { wunden: '2' } }) },
};
if (withSession) {
  ctx.window.DSASession = { probeMod: (z) => { seen.push(z); return -7; } };
}
vm.createContext(ctx);
const run = vm.runInContext('(function(){' + fn + '; return getWundMod;})()', ctx);
process.stdout.write(JSON.stringify({ res: cfgs.map(c => { const r = run(c); return Object.is(r, -0) ? '-0' : r; }), seen }));
"""


def _get_wund_mod(cfgs, session):
    src = DICE_JS.read_text(encoding='utf-8')
    m = re.search(r'function getWundMod\s*\(', src)
    params, body = _function_body(src, 'getWundMod')
    fn = src[m.start():src.index(body, m.start()) + len(body) + 1]
    proc = subprocess.run(
        ['node', '-e', _DICE_RUNNER, str(WUNDREGELN_JS), fn, json.dumps(cfgs), 'session' if session else 'file'],
        capture_output=True, text=True, encoding='utf-8', timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


_PROBEN = [
    {'type': 'at'}, {'type': 'pa'}, {'type': 'eigenschaft', 'abbr': 'GE'}, {'type': 'eigenschaft', 'abbr': 'MU'},
    {'type': 'talent'}, {'type': 'zauber'}, {'type': 'schaden'}, {'type': 'unbekannt'}, {},
]


@needs_node
def test_dice_get_wund_mod_file_fallback_uses_wundregeln_with_2_wunden():
    out = _get_wund_mod(_PROBEN, session=False)
    assert out['res'] == [-4, -4, -4, 0, 0, 0, 0, 0, 0]


@needs_node
def test_dice_get_wund_mod_delegates_to_session_probe_mod_except_schaden():
    out = _get_wund_mod(_PROBEN, session=True)
    assert out['seen'] == ['AT', 'PA', 'GE', 'MU', 'talent', 'zauber']
    assert out['res'] == [-7] * 6 + [0, 0, 0]
