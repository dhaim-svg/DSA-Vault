"""Tests for build_register — deduplicated NSC/Orte register from session sections."""
import json
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.register import build_register, fold
from rendering import STATIC_DIR
from tests.jsfixtures import needs_node, run_node

SEKTION = 'Neue NSCs / Orte'


def _session(nr, nscs='', orte='', key=SEKTION):
    """Synthetic session dict with a 'Neue NSCs / Orte' section."""
    parts = []
    if nscs is not None:
        parts.append('### NSCs\n' + nscs)
    if orte is not None:
        parts.append('### Orte\n' + orte)
    return {'nr': nr, 'datum': '2026-01-01', 'sektionen': {key: '\n'.join(parts)}}


def _nsc(text, nr='1'):
    """Register entries of a single-NSC session."""
    return build_register([_session(nr, nscs=text)])['nscs']


def test_fold_strips_diacritics_and_case():
    assert fold('Ärmel Öl Übung Café Straße') == 'armel ol ubung cafe strasse'


def test_empty_inputs_yield_empty_register():
    empty = {'nscs': [], 'orte': []}
    assert build_register([]) == empty
    assert build_register([{'nr': '1', 'sektionen': {}}]) == empty
    assert build_register([{'nr': '1'}]) == empty
    assert build_register([{'nr': '1', 'sektionen': {SEKTION: ''}}]) == empty
    assert build_register([{'nr': '1', 'sektionen': {SEKTION: '   \n'}}]) == empty


def test_section_heading_matched_normalized():
    for key in ('neue nscs  /  orte', 'neue nscs/orte', '  NEUE NSCs   /  ORTE ', 'Neue\tNSCs / Orte'):
        reg = build_register([_session('1', nscs='- **Alrik** — Held', key=key)])
        assert [e['name'] for e in reg['nscs']] == ['Alrik'], key


def test_other_h3_headings_ignored():
    text = '### Sonstiges\n- **Fremd** — nein\n### NSCs\n- **Alrik** — ja\n### Orte\n- **Punin** — ja'
    reg = build_register([{'nr': '1', 'sektionen': {SEKTION: text}}])
    assert [e['name'] for e in reg['nscs']] == ['Alrik']
    assert [e['name'] for e in reg['orte']] == ['Punin']


def test_dedup_across_sessions_case_insensitive():
    reg = build_register([
        _session('1', nscs='- **Richesa Bolongaro** — Draconiterin'),
        _session('3', nscs='- **richesa bolongaro** — taucht wieder auf'),
    ])
    assert len(reg['nscs']) == 1
    e = reg['nscs'][0]
    assert e['name'] == 'Richesa Bolongaro'
    assert e['sessions'] == ['1', '3']
    assert e['erwaehnungen'] == [
        {'nr': '1', 'text': 'Draconiterin'},
        {'nr': '3', 'text': 'taucht wieder auf'},
    ]


def test_dedup_same_session_twice_keeps_both_mentions():
    reg = build_register([_session('2', nscs='- **Alrik** — eins\n- **Alrik** — zwei')])
    e = reg['nscs'][0]
    assert e['sessions'] == ['2']
    assert [m['text'] for m in e['erwaehnungen']] == ['eins', 'zwei']


def test_unsicher_marker_after_name():
    e = _nsc('- **Parinor Aldebruch** (?) — „der werte“; bekam Nachfrage')[0]
    assert e['name'] == 'Parinor Aldebruch'
    assert e['unsicher'] is True
    assert e['qualifier'] == ''
    assert e['erwaehnungen'][0]['text'] == '„der werte“; bekam Nachfrage'


def test_unsicher_marker_only_in_description_does_not_count():
    e = _nsc('- **Cumrat** — kaiserliche Pfalz (?); Lage unklar')[0]
    assert e['unsicher'] is False
    assert e['qualifier'] == ''
    assert e['erwaehnungen'][0]['text'] == 'kaiserliche Pfalz (?); Lage unklar'


def test_unsicher_is_or_over_all_mentions():
    reg = build_register([
        _session('1', nscs='- **Alrik** — sicher'),
        _session('2', nscs='- **Alrik** (?) — unsicher'),
        _session('3', nscs='- **Alrik** — wieder sicher'),
    ])
    assert reg['nscs'][0]['unsicher'] is True


def test_qualifier_plain():
    e = _nsc('- **Magister** (Punin Akademie, Übersetzung) — Name nicht genannt')[0]
    assert e['name'] == 'Magister'
    assert e['qualifier'] == 'Punin Akademie, Übersetzung'
    assert e['unsicher'] is False
    assert e['erwaehnungen'][0]['text'] == 'Name nicht genannt'


def test_qualifier_first_non_empty_wins():
    reg = build_register([
        _session('1', nscs='- **Magister** — ohne'),
        _session('2', nscs='- **Magister** (Punin) — mit'),
        _session('3', nscs='- **Magister** (Gareth) — anders'),
    ])
    assert reg['nscs'][0]['qualifier'] == 'Punin'


def test_nested_parentheses_qualifier():
    e = _nsc('- **Reichsmarschall** (auch „Reichserzmarshall“ (?)) — Anrede „Eure Excellenz“; hoch')[0]
    assert e['name'] == 'Reichsmarschall'
    assert e['qualifier'] == 'auch „Reichserzmarshall“ (?)'
    assert e['unsicher'] is True
    assert e['erwaehnungen'][0]['text'] == 'Anrede „Eure Excellenz“; hoch'


def test_multiple_groups_joined_and_unsicher_group_dropped():
    e = _nsc('- **Alrik** (Ritter) (?) (vom Berg) — Held')[0]
    assert e['qualifier'] == 'Ritter, vom Berg'
    assert e['unsicher'] is True
    assert e['erwaehnungen'][0]['text'] == 'Held'


def test_unclosed_parenthesis_no_crash_no_qualifier():
    e = _nsc('- **Alrik** (Ritter — Held ohne Ende')[0]
    assert e['name'] == 'Alrik'
    assert e['qualifier'] == ''
    assert e['unsicher'] is False
    assert 'Held ohne Ende' in e['erwaehnungen'][0]['text']


def test_unclosed_after_valid_group_keeps_earlier_qualifier():
    e = _nsc('- **Alrik** (Ritter) (offen — Held')[0]
    assert e['qualifier'] == 'Ritter'
    assert 'Held' in e['erwaehnungen'][0]['text']


def test_no_separator_rest_is_description():
    e = _nsc('- **Alrik** einfach ein Held')[0]
    assert e['erwaehnungen'][0]['text'] == 'einfach ein Held'


def test_entry_without_description_is_kept():
    reg = build_register([_session('1', nscs='- **Alrik**\n- **Borbarad** (?)\n- **Cuano** (Gott) —')])
    assert [e['name'] for e in reg['nscs']] == ['Alrik', 'Borbarad', 'Cuano']
    assert all(e['erwaehnungen'][0]['text'] == '' for e in reg['nscs'])
    assert len(reg['nscs'][0]['erwaehnungen']) == 1


def test_alternative_separators():
    reg = build_register([_session('1', nscs='- **Alrik** – Halbstrich\n- **Borbarad** - Bindestrich')])
    assert [e['erwaehnungen'][0]['text'] for e in reg['nscs']] == ['Halbstrich', 'Bindestrich']


def test_wikilink_stripped_in_description_and_name():
    reg = build_register([_session('1', nscs='- **[[Alrik]]** — Diener von [[wiki/goetter/praios|Praios]]')])
    e = reg['nscs'][0]
    assert e['name'] == 'Alrik'
    assert e['erwaehnungen'][0]['text'] == 'Diener von Praios'


def test_non_bullet_and_indented_lines_ignored():
    text = (
        'Fließtext ohne Bullet\n'
        '- **Alrik** — Held\n'
        '  - **Unter** — eingerückt\n'
        '\n'
        '- kein fetter Name\n'
        '* **Stern** — anderer Bullet\n'
    )
    assert [e['name'] for e in _nsc(text)] == ['Alrik']


def test_sorted_folded_and_independent_of_occurrence_order():
    a = build_register([_session('1', nscs='- **Zebra** — z\n- **Ärmel** — ä\n- **Bar** — b')])
    b = build_register([_session('1', nscs='- **Bar** — b\n- **Zebra** — z'), _session('2', nscs='- **Ärmel** — ä')])
    expected = ['Ärmel', 'Bar', 'Zebra']
    assert [e['name'] for e in a['nscs']] == expected
    assert [e['name'] for e in b['nscs']] == expected


def test_nr_int_none_missing_are_robust():
    reg = build_register([
        {'nr': 3, 'sektionen': {SEKTION: '### NSCs\n- **Alrik** — int'}},
        {'nr': None, 'sektionen': {SEKTION: '### NSCs\n- **Alrik** — none'}},
        {'sektionen': {SEKTION: '### NSCs\n- **Alrik** — fehlt'}},
        {'nr': '', 'sektionen': {SEKTION: '### NSCs\n- **Alrik** — leer'}},
    ])
    e = reg['nscs'][0]
    assert e['sessions'] == ['3']
    assert [m['nr'] for m in e['erwaehnungen']] == ['3', '', '', '']
    assert all(isinstance(m['nr'], str) for m in e['erwaehnungen'])


def test_such_contains_folded_name_qualifier_and_all_texts():
    reg = build_register([
        _session('1', nscs='- **Ärmel** (Über Schneider) — Erster Text'),
        _session('2', nscs='- **ärmel** — Zweiter Text'),
    ])
    such = reg['nscs'][0]['such']
    assert such == fold('Ärmel') + ' ' + fold('Über Schneider') + ' ' + fold('Erster Text') + ' ' + fold('Zweiter Text')
    assert 'armel' in such and 'uber schneider' in such
    assert 'erster text' in such and 'zweiter text' in such


def test_nsc_and_ort_same_name_stay_separate():
    reg = build_register([_session('1', nscs='- **Punin** — Person', orte='- **Punin** — Stadt')])
    assert [e['name'] for e in reg['nscs']] == ['Punin']
    assert [e['name'] for e in reg['orte']] == ['Punin']
    assert reg['nscs'][0]['erwaehnungen'][0]['text'] == 'Person'
    assert reg['orte'][0]['erwaehnungen'][0]['text'] == 'Stadt'


def test_orte_parsed_like_nscs():
    reg = build_register([_session('1', orte='- **Yaquir** (Fluss) — Dörfer\n- **Cumrat** (?) — Pfalz')])
    names = {e['name']: e for e in reg['orte']}
    assert names['Yaquir']['qualifier'] == 'Fluss'
    assert names['Cumrat']['unsicher'] is True


# -- D-045: Filter-Kopfzeile fuer den Druck (static/register.js) -------------
REGISTER_JS = STATIC_DIR / 'register.js'

# Minimales Fake-DOM: 2 Gruppen, 3 Eintraege (such: alrik held / borbarad / cumrat stadt); innerHTML wirft.
_NODE_RUNNER = """
const fs = require('fs'), vm = require('vm');
const steps = JSON.parse(process.argv[2]);
const noDruck = process.argv[3] === 'nodruck';
function el(extra) {
  const e = { hidden: false, textContent: '', dataset: {} };
  Object.defineProperty(e, 'innerHTML', { get() { return ''; }, set() { throw new Error('innerHTML verboten'); } });
  return Object.assign(e, extra || {});
}
function entry(such) { return el({ dataset: { such } }); }
function group(entries) {
  const count = el();
  return { hidden: false, querySelectorAll: () => entries, querySelector: () => count };
}
const input = { value: '', l: {}, addEventListener(t, f) { (this.l[t] = this.l[t] || []).push(f); } };
const counter = el(), empty = el(), druck = el(), dom = {};
druck.hidden = false;  // Startzustand bewusst 'sichtbar': der Initial-apply() muss selbst verstecken
const els = { '.register-suche': input, '.register-zaehler': counter, '.register-leer': empty,
              '.register-druckfilter': noDruck ? null : druck };
const groups = [group([entry('alrik held'), entry('borbarad')]), group([entry('cumrat stadt')])];
const document = {
  querySelector: (s) => els[s] || null,
  querySelectorAll: (s) => (s === '.register-gruppe' ? groups : []),
  addEventListener: (t, f) => { dom[t] = f; },
};
vm.runInNewContext(fs.readFileSync(process.argv[1], 'utf8'), { document });
dom.DOMContentLoaded();
const out = [{ hidden: druck.hidden, text: druck.textContent }];
for (const s of steps) {
  if (s.value !== undefined) { input.value = s.value; }
  (input.l[s.type] || []).forEach((f) => f(s.key ? { key: s.key } : {}));
  out.push({ hidden: druck.hidden, text: druck.textContent });
}
process.stdout.write(JSON.stringify(out));
"""


def _run_register(steps, *flags):
    return run_node(_NODE_RUNNER, REGISTER_JS, json.dumps(steps), *flags)


@needs_node
def test_register_js_druckfilter_initially_hidden():
    assert _run_register([]) == [{'hidden': True, 'text': ''}]


@needs_node
def test_register_js_druckfilter_shows_term_and_counts():
    out = _run_register([{'type': 'input', 'value': 'alrik'}])
    assert out[1] == {'hidden': False, 'text': 'Gefiltert nach: "alrik" — 1/3 Einträge'}


@needs_node
def test_register_js_druckfilter_trims_term_and_hides_on_blank():
    out = _run_register([
        {'type': 'input', 'value': '  cumrat  '},
        {'type': 'input', 'value': '   '},
    ])
    assert out[1] == {'hidden': False, 'text': 'Gefiltert nach: "cumrat" — 1/3 Einträge'}
    assert out[2] == {'hidden': True, 'text': ''}


@needs_node
def test_register_js_druckfilter_hides_on_escape_reset():
    out = _run_register([
        {'type': 'input', 'value': 'stadt'},
        {'type': 'keydown', 'key': 'Escape'},
    ])
    assert out[1]['hidden'] is False
    assert out[2] == {'hidden': True, 'text': ''}


@needs_node
def test_register_js_druckfilter_counts_zero_matches_and_keeps_markup_as_text():
    term = '<img src=x onerror=alert(1)>'  # Fake-innerHTML wirft -> nur textContent erlaubt
    out = _run_register([{'type': 'input', 'value': term}])
    assert out[1] == {'hidden': False, 'text': f'Gefiltert nach: "{term}" — 0/3 Einträge'}


@needs_node
def test_register_js_works_without_druckfilter_element():
    out = _run_register([{'type': 'input', 'value': 'alrik'}], 'nodruck')
    assert out[1] == {'hidden': False, 'text': ''}  # Fake bleibt unberuehrt, kein Absturz


def test_register_js_druckfilter_uses_textcontent_not_innerhtml():
    src = REGISTER_JS.read_text(encoding='utf-8')
    assert 'innerHTML' not in src
    assert re.search(r"querySelector\('\.register-druckfilter'\)", src)
    assert re.search(r'druckfilter\.textContent\s*=', src)
