"""D-055: chronik.js print-time DOM adjustments (beforeprint/afterprint) run via node in a fake DOM.

Two independent problems share this file's beforeprint/afterprint pair: Chrome does not print the
body of a closed <details> (details.chronik-abend, pre-existing), and a <textarea> only prints its
scrolled viewport, not its full scrollable content (.journal-verlauf, D-055). Both use the same
"record the prior state under a dataset guard, then force the print-friendly state; on afterprint
restore exactly what was there before" idiom, so both are exercised through the same node runner.
"""
import json

from rendering import STATIC_DIR
from tests.jsfixtures import needs_node, run_node

CHRONIK_JS = STATIC_DIR / 'chronik.js'

_RUNNER = """
const fs = require('fs'), vm = require('vm');
const src = fs.readFileSync(process.argv[1], 'utf8');
const spec = JSON.parse(process.argv[2]);

const listeners = { beforeprint: [], afterprint: [] };
const details = spec.details.map((d) => ({ dataset: {}, open: d.open }));
const textareas = spec.textareas.map((t) => ({ dataset: {}, style: { height: t.height || '' }, scrollHeight: t.scrollHeight }));

const window = { addEventListener: (evt, fn) => { if (listeners[evt]) listeners[evt].push(fn); } };
const document = {
  addEventListener: () => {},
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
  textHeight: textareas.map((t) => t.style.height),
  textWasHeight: textareas.map((t) => (t.dataset.wasHeight === undefined ? null : t.dataset.wasHeight)),
}));
"""


def _run(events, details=(), textareas=()):
    spec = {'events': list(events), 'details': list(details), 'textareas': list(textareas)}
    return run_node(_RUNNER, CHRONIK_JS, json.dumps(spec))


# -- D-055: .journal-verlauf grows to scrollHeight for the print, then restores exactly ----------

@needs_node
def test_beforeprint_grows_textarea_to_its_own_scrollheight():
    out = _run(['beforeprint'], textareas=[
        {'height': '', 'scrollHeight': 1324},
        {'height': '', 'scrollHeight': 780},
    ])
    assert out['textHeight'] == ['1324px', '780px']


@needs_node
def test_afterprint_removes_inline_height_when_none_was_set_before():
    out = _run(['beforeprint', 'afterprint'], textareas=[{'height': '', 'scrollHeight': 900}])
    assert out['textHeight'] == ['']
    assert out['textWasHeight'] == [None]  # guard cleaned up, not left dangling


@needs_node
def test_afterprint_restores_a_pre_existing_inline_height():
    # e.g. the user dragged the resize handle before printing -> that height must come back, not ''.
    out = _run(['beforeprint', 'afterprint'], textareas=[{'height': '140px', 'scrollHeight': 900}])
    assert out['textHeight'] == ['140px']


@needs_node
def test_beforeprint_is_idempotent_across_repeated_print_events():
    # dispatched twice without an afterprint in between (e.g. two print dialogs) must not clobber
    # the recorded prior state with the already-grown scrollHeight value.
    out = _run(['beforeprint', 'beforeprint'], textareas=[{'height': '', 'scrollHeight': 900}])
    assert out['textHeight'] == ['900px']
    assert out['textWasHeight'] == ['']

    out = _run(['beforeprint', 'beforeprint', 'afterprint'], textareas=[{'height': '', 'scrollHeight': 900}])
    assert out['textHeight'] == ['']  # restores the ORIGINAL state, not the mid-print one


@needs_node
def test_multiple_textareas_are_independent():
    out = _run(['beforeprint', 'afterprint'], textareas=[
        {'height': '', 'scrollHeight': 1324},
        {'height': '140px', 'scrollHeight': 780},
    ])
    assert out['textHeight'] == ['', '140px']


# -- Regression: the pre-existing <details> toggle must keep working unchanged -------------------

@needs_node
def test_details_toggle_regression_unaffected_by_the_textarea_addition():
    out = _run(['beforeprint'], details=[{'open': True}, {'open': False}])
    assert out['detailOpen'] == [True, True]
    assert out['detailWasOpen'] == ['1', '']

    out = _run(['beforeprint', 'afterprint'], details=[{'open': True}, {'open': False}])
    assert out['detailOpen'] == [True, False]
    assert out['detailWasOpen'] == [None, None]


@needs_node
def test_details_and_textarea_fixes_apply_together_in_one_print_cycle():
    out = _run(['beforeprint', 'afterprint'],
                details=[{'open': False}],
                textareas=[{'height': '', 'scrollHeight': 1000}])
    assert out['detailOpen'] == [False]
    assert out['textHeight'] == ['']
