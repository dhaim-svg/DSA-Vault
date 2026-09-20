"""D-055: chronik.js print-time DOM adjustments (beforeprint/afterprint) run via node in a fake DOM.

Two independent problems share this file's beforeprint/afterprint pair: Chrome does not print the
body of a closed <details> (details.chronik-abend, pre-existing), and a <textarea> only prints its
scrolled viewport, not its full scrollable content (.journal-verlauf, D-055).

v1 grew the live textarea to its own scrollHeight, but scrollHeight is measured at the screen
layout width, which mismatches the narrower real print width (Final-Review Important: 48 missing
lines measured between a 1280px and a 718px browser window's real page.pdf() output). v2 (this
file) instead hides the textarea in print and shows a plain flowed <pre class="journal-verlauf-print">
snapshot of the live (possibly-unsaved) t.value, so the browser's own print layout wraps/sizes it
correctly regardless of width, with no manual measurement.
"""
import json

from rendering import STATIC_DIR
from tests.jsfixtures import needs_node, run_node
from tests.test_static_js import strip_js

CHRONIK_JS = STATIC_DIR / 'chronik.js'

_RUNNER = """
const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync(process.argv[1], 'utf8');
const spec = JSON.parse(process.argv[2]);

const listeners = { beforeprint: [], afterprint: [] };
const details = spec.details.map((d) => ({ dataset: {}, open: d.open }));

function makeEl(tag) {
  const el = { tagName: tag, className: '', textContent: '' };
  el.classList = { contains: (c) => (' ' + el.className + ' ').indexOf(' ' + c + ' ') !== -1 };
  return el;
}

const textareas = spec.textareas.map((t) => {
  const el = { value: t.value, nextElementSibling: null };
  if (t.seedMirror !== undefined) {
    const mirror = makeEl('pre');
    mirror.className = 'journal-verlauf-print';
    mirror.textContent = t.seedMirror;
    mirror.__seed = true;  // marks this exact object so tests can tell reuse from recreation
    el.nextElementSibling = mirror;
  }
  el.insertAdjacentElement = (where, node) => { el.nextElementSibling = node; };
  return el;
});

let created = 0;
const window = { addEventListener: (evt, fn) => { if (listeners[evt]) listeners[evt].push(fn); } };
const document = {
  addEventListener: () => {},
  createElement: (tag) => { created += 1; return makeEl(tag); },
  querySelectorAll: (sel) => {
    if (sel === 'details.chronik-abend') return details;
    if (sel === '.journal-verlauf') return textareas;
    return [];
  },
};
const ctx = { window, document };
vm.createContext(ctx);
vm.runInContext(src, ctx);

spec.events.forEach((evt) => listeners[evt].forEach((fn) => fn()));

process.stdout.write(JSON.stringify({
  detailOpen: details.map((d) => d.open),
  detailWasOpen: details.map((d) => (d.dataset.wasOpen === undefined ? null : d.dataset.wasOpen)),
  mirrors: textareas.map((t) => {
    const m = t.nextElementSibling;
    return m ? { className: m.className, textContent: m.textContent, reused: !!m.__seed } : null;
  }),
  created,
}));
"""


def _run(events, details=(), textareas=()):
    spec = {'events': list(events), 'details': list(details), 'textareas': list(textareas)}
    return run_node(_RUNNER, CHRONIK_JS, json.dumps(spec))


# -- D-055 v2: beforeprint snapshots t.value into a plain flowed <pre> mirror, afterprint clears it --

@needs_node
def test_beforeprint_creates_a_print_mirror_with_the_live_value():
    out = _run(['beforeprint'], textareas=[{'value': 'Zeile 1\nZeile 2'}])
    assert out['mirrors'] == [{'className': 'journal-verlauf-print', 'textContent': 'Zeile 1\nZeile 2', 'reused': False}]
    assert out['created'] == 1


@needs_node
def test_mirror_captures_the_current_possibly_unsaved_value_not_a_stale_copy():
    # Same staleness constraint as D-054/R2: whatever is in the box right now is what must print,
    # unsaved or not — there is no server-rendered copy to go stale in the first place.
    out = _run(['beforeprint'], textareas=[{'value': 'noch nicht gespeichert'}])
    assert out['mirrors'][0]['textContent'] == 'noch nicht gespeichert'


@needs_node
def test_afterprint_clears_the_mirror_but_leaves_it_in_the_dom():
    out = _run(['beforeprint', 'afterprint'], textareas=[{'value': 'Text'}])
    assert out['mirrors'] == [{'className': 'journal-verlauf-print', 'textContent': '', 'reused': False}]


@needs_node
def test_beforeprint_reuses_an_existing_mirror_instead_of_creating_a_duplicate():
    # Repeated print cycles (two print dialogs, or a re-render of the same page) must not pile up
    # sibling <pre> elements after every beforeprint.
    out = _run(['beforeprint'], textareas=[{'value': 'neu', 'seedMirror': 'alt'}])
    assert out['mirrors'] == [{'className': 'journal-verlauf-print', 'textContent': 'neu', 'reused': True}]
    assert out['created'] == 0


@needs_node
def test_beforeprint_after_afterprint_repopulates_the_cleared_mirror():
    out = _run(['beforeprint', 'afterprint', 'beforeprint'], textareas=[{'value': 'zweiter Druck'}])
    assert out['mirrors'][0]['textContent'] == 'zweiter Druck'
    assert out['created'] == 1  # only the very first beforeprint created it; the 2nd reused the sibling


@needs_node
def test_afterprint_is_a_noop_without_a_prior_beforeprint():
    out = _run(['afterprint'], textareas=[{'value': 'irrelevant'}])
    assert out['mirrors'] == [None]


@needs_node
def test_multiple_textareas_get_independent_mirrors():
    out = _run(['beforeprint'], textareas=[{'value': 'Session A'}, {'value': 'Session B'}])
    assert [m['textContent'] for m in out['mirrors']] == ['Session A', 'Session B']
    assert out['created'] == 2


def test_mirror_content_is_set_via_textcontent_never_innerhtml():
    # Session text is untrusted user input; textContent auto-escapes, innerHTML would not.
    # strip_js blanks comments/strings first — the code's own explanatory comment names the
    # rejected innerHTML alternative, which would otherwise false-positive a raw substring check.
    src = CHRONIK_JS.read_text(encoding='utf-8')
    assert 'innerHTML' not in strip_js(src)
    assert 'mirror.textContent = t.value' in src


def test_v1_scrollheight_resize_approach_was_fully_removed():
    # Final-Review Important: the v1 approach (resize the live textarea to its own scrollHeight)
    # measured at the wrong layout width and still lost ~17% of the text — must not linger as
    # dead/half-removed code alongside the v2 mirror. Comments discussing v1 for context are fine
    # (and expected — strip_js blanks them out before this check).
    src = strip_js(CHRONIK_JS.read_text(encoding='utf-8'))
    assert 'scrollHeight' not in src
    assert 'wasHeight' not in src


# -- Regression: the pre-existing <details> toggle must keep working unchanged -------------------

@needs_node
def test_details_toggle_regression_unaffected_by_the_mirror_addition():
    out = _run(['beforeprint'], details=[{'open': True}, {'open': False}])
    assert out['detailOpen'] == [True, True]
    assert out['detailWasOpen'] == ['1', '']

    out = _run(['beforeprint', 'afterprint'], details=[{'open': True}, {'open': False}])
    assert out['detailOpen'] == [True, False]
    assert out['detailWasOpen'] == [None, None]


@needs_node
def test_details_and_mirror_fixes_apply_together_in_one_print_cycle():
    out = _run(['beforeprint', 'afterprint'],
                details=[{'open': False}],
                textareas=[{'value': 'Verlauf'}])
    assert out['detailOpen'] == [False]
    assert out['mirrors'] == [{'className': 'journal-verlauf-print', 'textContent': '', 'reused': False}]
