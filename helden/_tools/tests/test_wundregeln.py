"""D-041b: Wundlogik (WdS S. 57) — Regeltabelle per node ausgefuehrt, plus Struktur-Scans.

Pro Wunde: AT/PA/FK/INI/GE -2, GS -1; Talent-/Zauber-/sonstige Eigenschaftsproben und
Schadenswuerfe bekommen keinen Wundabzug. Einzige Regelquelle: static/wundregeln.js."""
import json
import re

import pytest

from rendering import JS_FILES, STATIC_DIR
from tests.jsfixtures import js_function, js_function_body, needs_node, run_node

WUNDREGELN_JS = STATIC_DIR / 'wundregeln.js'
SESSION_JS = STATIC_DIR / 'session.js'
DICE_JS = STATIC_DIR / 'dice.js'

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
    return run_node(_NODE_RUNNER, WUNDREGELN_JS, json.dumps(calls))


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


def test_dice_get_wund_mod_is_scoped_by_probe_type():
    src = DICE_JS.read_text(encoding='utf-8')
    params, body = js_function_body(src, 'getWundMod')
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
    for name in ('computeActiveEffects', 'probeMod', 'statMod', 'attrMod'):
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
    return run_node(_DICE_RUNNER, WUNDREGELN_JS, js_function(src, 'getWundMod'), json.dumps(cfgs),
                    'session' if session else 'file')


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


# -- Zustands-Chips: Hausregel-Kennzeichnung (D-041c) --

def _zustaende_block(src):
    m = re.search(r'const ZUSTAENDE = \[(.*?)\n\s*\];', src, re.S)
    assert m, 'ZUSTAENDE fehlt'
    return m.group(1)


def test_all_five_zustaende_are_marked_hausregel_with_regel_text():
    entries = re.findall(r'\{[^{}]*\}', _zustaende_block(SESSION_JS.read_text(encoding='utf-8')))
    assert [re.search(r"key: '(\w+)'", e).group(1) for e in entries] == [
        'schmerz', 'furcht', 'betaeubt', 'verwirrt', 'erschoepft']
    for e in entries:
        assert 'hausregel: true' in e, e
        regel = re.search(r"regel: '([^']+)'", e)
        assert regel, e
        assert regel.group(1).startswith('Regelwerk:') and len(regel.group(1)) <= 90
    # Werte unveraendert
    assert re.findall(r'mod: (-\d)', _zustaende_block(SESSION_JS.read_text(encoding='utf-8'))) == [
        '-2', '-2', '-4', '-2', '-2']


def test_zustand_chip_title_and_class_carry_hausregel():
    src = SESSION_JS.read_text(encoding='utf-8')
    _, body = js_function_body(src, 'renderZustandChips')
    assert "'hausregel'" in body or "' hausregel'" in body
    assert 'z.hausregel' in body
    assert "(Hausregel) — '" in body and 'z.regel' in body


def test_badge_marks_hausregel_only_on_zustand_branch():
    src = SESSION_JS.read_text(encoding='utf-8')
    _, body = js_function_body(src, 'updateEigLeisteBadge')
    body = re.sub(r'//[^\n]*', '', body)  # Kommentare zaehlen nicht
    assert body.count('(Hausregel)') == 1
    zustand_branch, wunden_branch = body.split("' ×'")
    assert '(Hausregel)' in zustand_branch and 'e.hausregel' in zustand_branch
    assert 'Hausregel' not in wunden_branch


def test_zustand_effects_carry_hausregel_flag_wunden_do_not():
    src = SESSION_JS.read_text(encoding='utf-8')
    _, body = js_function_body(src, 'computeActiveEffects')
    assert re.search(r"label: z\.label, alle: true, mod: z\.mod, hausregel: true", body)
    assert 'hausregel' not in body.split('ZUSTAENDE.forEach')[0]


def test_session_has_no_stale_verify_rules_comment():
    src = SESSION_JS.read_text(encoding='utf-8')
    assert not re.search(r'verify exact|TODO|FIXME', src, re.I)
    assert 'Hausregel' in src.split('function initSession')[1].split('const ZUSTAENDE')[0]


# -- Final-Review: GE-Abzug der Wunden auch in Talent-/Zauberproben (dice.js parseProbe) --
# Regel (WdS S. 57): eine Wunde senkt die Eigenschaft GE -> der niedrigere Wert gilt in JEDER Probe mit GE.
# parseProbe wendet daher nur den Wund-Abzug pro Eigenschaft an; Hausregel-Chips wirken weiter nur ueber dp-mod.

_PARSE_RUNNER = """
const fs = require('fs'), vm = require('vm');
const ST = process.argv[1];
const spec = JSON.parse(process.argv[2]);
const fns = process.argv[3];
const store = {};
if (spec.zustaende.length) store['dsa:illaen-baernhold:session'] = JSON.stringify({ zustaende: spec.zustaende });
const anchor = { dataset: { wunden: String(spec.wunden) }, textContent: '', insertAdjacentElement() {} };
const noop = { dataset: {}, textContent: '', innerHTML: '', addEventListener() {}, querySelectorAll() { return []; }, insertAdjacentElement() {} };
const document = {
  readyState: 'complete',
  querySelector: (sel) => (sel === '[data-wunden]' ? anchor : null),
  querySelectorAll: () => [],
  getElementById: (id) => (id === 'wunden-widget' ? null : noop),
  createElement: () => noop,
  addEventListener() {},
};
const window = { DSA: { eig: spec.eig } };
const ctx = {
  window, document, console, confirm: () => true, fetch: () => Promise.resolve({}),
  location: { protocol: spec.proto },
  localStorage: { getItem: (k) => store[k] || null, setItem() {}, removeItem() {} },
};
vm.createContext(ctx);
for (const f of ['wundregeln.js', 'session.js']) vm.runInContext(fs.readFileSync(ST + f, 'utf8'), ctx);
const api = vm.runInContext('(function(){' + fns + '; return { parseProbe: parseProbe };})()', ctx);
const S = window.DSASession;
process.stdout.write(JSON.stringify({
  probes: spec.probes.map((p) => api.parseProbe(p)),
  session: !!S,
  attr: S ? spec.attrs.map((a) => S.attrMod(a)) : null,
}));
"""

_EIG = {'MU': 12, 'KL': 13, 'IN': 14, 'CH': 11, 'FF': 10, 'GE': 13, 'KO': 12, 'KK': 15}
_ALL_PROBES = ['MU/KL/GE', 'IN/CH/FF', 'KO/KK/GE', 'MU/**/GE', 'KL/IN/CH', 'KK/KO/FF']


def _parse_probe(proto, wunden, zustaende=(), probes=_ALL_PROBES, attrs=()):
    src = DICE_JS.read_text(encoding='utf-8')
    fns = js_function(src, 'parseProbe') + '\n' + js_function(src, 'wundAttrMod')
    spec = {'proto': proto, 'wunden': wunden, 'zustaende': list(zustaende), 'eig': _EIG,
            'probes': list(probes), 'attrs': list(attrs)}
    return run_node(_PARSE_RUNNER, str(STATIC_DIR) + '/', json.dumps(spec), fns)


_EXPECT_2_WUNDEN = [[12, 13, 9], [14, 11, 10], [12, 15, 9], [12, None, 9], [13, 14, 11], [15, 12, 10]]
_EXPECT_UNVERAENDERT = [[12, 13, 13], [14, 11, 10], [12, 15, 13], [12, None, 13], [13, 14, 11], [15, 12, 10]]


@needs_node
@pytest.mark.parametrize('proto', ['http:', 'file:'])
def test_parse_probe_reduces_only_ge_by_wunden(proto):
    assert _parse_probe(proto, 2)['probes'] == _EXPECT_2_WUNDEN


@needs_node
@pytest.mark.parametrize('proto', ['http:', 'file:'])
def test_parse_probe_unchanged_without_wunden(proto):
    assert _parse_probe(proto, 0)['probes'] == _EXPECT_UNVERAENDERT


@needs_node
def test_parse_probe_ignores_hausregel_chips_but_keeps_wound_reduction():
    # Chips wirken nur ueber dp-mod (sonst doppelt gezaehlt) -> Attributwerte bleiben unberuehrt.
    chips = ['schmerz', 'furcht', 'betaeubt', 'verwirrt', 'erschoepft']
    out = _parse_probe('http:', 0, chips)
    assert out['session'] is True
    assert out['probes'] == _EXPECT_UNVERAENDERT
    assert _parse_probe('http:', 2, chips)['probes'] == _EXPECT_2_WUNDEN


@needs_node
def test_parse_probe_file_fallback_matches_session_branch():
    for wunden in (0, 1, 2, 5):
        served = _parse_probe('http:', wunden)
        offline = _parse_probe('file:', wunden)
        assert served['session'] is True and offline['session'] is False
        assert served['probes'] == offline['probes']


@needs_node
def test_session_attr_mod_is_wounds_only_and_attribute_scoped():
    abbrs = ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK', 'AT', 'PA', 'FK', 'INI', 'GS', 'talent']
    wunden = _parse_probe('http:', 2, ['schmerz', 'betaeubt'], probes=[], attrs=abbrs)['attr']
    assert wunden == [0, 0, 0, 0, 0, -4, 0, 0, 0, 0, 0, 0, 0, 0]
    chips_only = _parse_probe('http:', 0, ['schmerz', 'betaeubt'], probes=[], attrs=abbrs)['attr']
    assert chips_only == [0] * len(abbrs)


def test_parse_probe_is_only_used_by_talent_and_zauber_probes():
    # 'eigenschaft' (Einzel-GE-Probe) bekommt den Wundabzug schon ueber getWundMod -> darf parseProbe nie durchlaufen.
    src = DICE_JS.read_text(encoding='utf-8')
    calls = [m.start() for m in re.finditer(r'parseProbe\(', src)]
    assert len(calls) == 2, 'Definition + genau ein Aufruf'
    render_talent = src.index("if (cfg.type === 'talent' || cfg.type === 'zauber') {", src.index('function render('))
    render_eig = src.index("} else if (cfg.type === 'eigenschaft') {", render_talent)
    assert render_talent < calls[1] < render_eig


# -- D-048: Zustands-Chips wirken nur ueber die Panel-Vorbelegung, nie als Attributwert-Overlay --
# Vorher senkte applyWundModsToProben (probeMod = Wunden + Chips) ALLE [data-attr]-Spans ("MU 12→10"), und das
# Wuerfelpanel fuellte dp-mod zusaetzlich mit dem Chip-Wert vor -> von Hand gewuerfelt zaehlte der Malus doppelt.
# Diese Tests laden die echte session.js in einem Fake-DOM mit den Eigenschafts-Spans der Talent-/Zauberproben.

_OVERLAY_RUNNER = """
const fs = require('fs'), vm = require('vm');
const ST = process.argv[1];
const spec = JSON.parse(process.argv[2]);
const store = {};
if (spec.zustaende.length) store['dsa:illaen-baernhold:session'] = JSON.stringify({ zustaende: spec.zustaende });
const anchor = { dataset: { wunden: String(spec.wunden) }, textContent: '', insertAdjacentElement() {} };
const noop = { dataset: {}, textContent: '', innerHTML: '', addEventListener() {}, querySelectorAll() { return []; }, insertAdjacentElement() {} };
const spans = Object.keys(spec.eig).map((k) => ({ dataset: { attr: k, base: String(spec.eig[k]) }, textContent: k + ' ' + spec.eig[k] }));
const badges = [{ textContent: '' }];
const document = {
  readyState: 'complete',
  querySelector: (sel) => (sel === '[data-wunden]' ? anchor : null),
  querySelectorAll: (sel) => (sel === '[data-attr]' ? spans : sel === '.eig-leiste-mods' ? badges : []),
  getElementById: (id) => (id === 'wunden-widget' ? null : noop),
  createElement: () => noop,
  addEventListener() {},
};
const window = {};
const ctx = {
  window, document, console, confirm: () => true, fetch: () => Promise.resolve({}),
  location: { protocol: 'http:' },
  localStorage: { getItem: (k) => store[k] || null, setItem() {}, removeItem() {} },
};
vm.createContext(ctx);
for (const f of ['wundregeln.js', 'session.js']) vm.runInContext(fs.readFileSync(ST + f, 'utf8'), ctx);
const S = window.DSASession;
process.stdout.write(JSON.stringify({
  spans: spans.map((s) => s.textContent),
  badge: badges[0].textContent,
  probe: S ? spec.probes.map((p) => S.probeMod(p)) : null,
}));
"""

_ALL_CHIPS = ['schmerz', 'furcht', 'betaeubt', 'verwirrt', 'erschoepft']
_BASE_SPANS = [f'{k} {v}' for k, v in _EIG.items()]


def _overlay(wunden, zustaende=(), probes=()):
    spec = {'wunden': wunden, 'zustaende': list(zustaende), 'eig': _EIG, 'probes': list(probes)}
    return run_node(_OVERLAY_RUNNER, str(STATIC_DIR) + '/', json.dumps(spec))


@needs_node
def test_chips_alone_leave_every_attribute_span_untouched_but_keep_the_panel_prefill():
    out = _overlay(0, ['schmerz'], probes=['MU', 'AT', 'GE'])
    assert out['spans'] == _BASE_SPANS
    assert not any('→' in t for t in out['spans'])
    assert out['probe'] == [-2, -2, -2]  # Panel-Vorbelegung (dice.js -> probeMod) bleibt
    assert 'Schmerz' in out['badge'] and 'Hausregel' in out['badge']  # Badge informiert weiter, ohne Zahlen-Overlay


@needs_node
def test_all_chips_together_still_touch_no_attribute_span():
    out = _overlay(0, _ALL_CHIPS, probes=['MU'])
    assert out['spans'] == _BASE_SPANS
    assert out['probe'] == [-2 - 2 - 4 - 2 - 2]


@needs_node
def test_wounds_plus_chip_overlay_only_ge_and_panel_prefill_sums_both():
    out = _overlay(2, ['schmerz'], probes=['GE', 'MU', 'AT'])
    expected = [f'{k} {v}' for k, v in _EIG.items()]
    expected[list(_EIG).index('GE')] = 'GE 13→9'
    assert out['spans'] == expected
    assert [t for t in out['spans'] if '→' in t] == ['GE 13→9']
    assert out['probe'] == [-4 - 2, -2, -4 - 2]  # Panel: Wunde (GE -4 / AT -4) + Chip (-2)


@needs_node
def test_wounds_alone_still_overlay_ge_span():
    out = _overlay(1, probes=['GE'])
    assert [t for t in out['spans'] if '→' in t] == ['GE 13→11']
    assert out['probe'] == [-2]


def test_apply_wund_mods_to_proben_uses_wounds_only_attr_mod():
    src = SESSION_JS.read_text(encoding='utf-8')
    _params, body = js_function_body(src, 'applyWundModsToProben')
    assert 'attrMod(' in body and 'probeMod(' not in body
