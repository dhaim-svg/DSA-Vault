"""Tests for parsers.wikiartikel — wiki article/section loader (synthetic vault only)."""
import logging
import re
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import split_sections
from parsers.wikiartikel import load_wiki_artikel
from rendering import VAULT_ROOT, obsidian_uri

ZAUBER = 'wiki/dsa-4.1/zauber'

ADLERAUGE = """---
typ: zauber
name: ADLERAUGE
alternativname: LUCHSENOHR
probe: KL/IN/FF
komplexität: B
kosten: 4 AsP
zauberdauer: 2 Aktionen
wirkungsdauer: ''
quelle: LC
seite: 15
---

# ADLERAUGE (LUCHSENOHR)

> **Quelle:** LC S. 15

## Wirkung

Schärft den **Blick** des Zaubernden.

- Erste Variante
- Zweite Variante

## Reversalis

Keine Wirkung.
"""


def _write(vault: Path, rel: str, text: str) -> Path:
    p = vault / (rel + '.md')
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')
    return p


def _link(path: str) -> str:
    return f'test-link://{path}'


def _load(vault, paths, link_fn=_link):
    return load_wiki_artikel(vault, paths, link_fn)


@pytest.fixture
def vault(tmp_path):
    return tmp_path


# --- Happy path -----------------------------------------------------------

def test_happy_path_model(vault):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    res = _load(vault, [f'{ZAUBER}/adlerauge'])
    assert list(res) == [f'{ZAUBER}/adlerauge']
    art = res[f'{ZAUBER}/adlerauge']
    assert set(art) == {'titel', 'quelle', 'meta', 'html'}
    assert art['titel'] == 'ADLERAUGE (LUCHSENOHR)'
    assert art['quelle'] == 'LC S. 15'
    assert art['meta'] == [
        {'label': 'Probe', 'wert': 'KL/IN/FF'},
        {'label': 'Kosten', 'wert': '4 AsP'},
        {'label': 'Zauberdauer', 'wert': '2 Aktionen'},
    ]


def test_html_has_sections_and_lists_but_no_h1_or_quelle(vault):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    html = _load(vault, [f'{ZAUBER}/adlerauge'])[f'{ZAUBER}/adlerauge']['html']
    assert '<h2>Wirkung</h2>' in html
    assert '<h2>Reversalis</h2>' in html
    assert '<li>Erste Variante</li>' in html
    assert '<strong>Blick</strong>' in html
    assert '<h1' not in html
    assert 'ADLERAUGE' not in html
    assert 'Quelle' not in html


def test_meta_order_is_fixed_regardless_of_frontmatter_order(vault):
    _write(vault, f'{ZAUBER}/x',
           '---\nwirkungsdauer: 1 SR\nzauberdauer: 1 Aktion\nkosten: 2 AsP\nprobe: MU/MU/MU\n---\n# X\n')
    meta = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['meta']
    assert [m['label'] for m in meta] == ['Probe', 'Kosten', 'Zauberdauer', 'Wirkungsdauer']


def test_tables_are_rendered(vault):
    _write(vault, f'{ZAUBER}/t',
           '---\nname: T\n---\n# T\n\n## Wirkung\n\n| ZfP* | Wirkung |\n|------|---------|\n| 1 | Eins |\n')
    html = _load(vault, [f'{ZAUBER}/t'])[f'{ZAUBER}/t']['html']
    assert '<table>' in html
    assert '<td>Eins</td>' in html


def test_only_quelle_block_after_h1_is_removed(vault):
    _write(vault, f'{ZAUBER}/x',
           '---\nname: X\n---\n# X\n\n> **Quelle:** LC S. 1\n> zweite Zeile\n\n> Anmerkung bleibt\n\nText.\n')
    html = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['html']
    assert 'Quelle' not in html
    assert 'zweite Zeile' not in html
    assert 'Anmerkung bleibt' in html
    assert 'Text.' in html


def test_other_blockquote_after_h1_is_kept(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\n---\n# X\n\n> Hinweis\n\nText.\n')
    html = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['html']
    assert '<blockquote>' in html
    assert 'Hinweis' in html


# --- Titel / Quelle fallbacks --------------------------------------------

def test_title_falls_back_to_name_and_alternativname(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: ADLERAUGE\nalternativname: LUCHSENOHR\n---\n\n## Wirkung\n\nText.\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['titel'] == 'ADLERAUGE (LUCHSENOHR)'


def test_title_falls_back_to_name_only(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: ANALYS\n---\nText.\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['titel'] == 'ANALYS'


def test_title_falls_back_to_last_path_part(vault):
    _write(vault, f'{ZAUBER}/blick-aufs-wesen', 'Nur Text.\n')
    assert _load(vault, [f'{ZAUBER}/blick-aufs-wesen'])[f'{ZAUBER}/blick-aufs-wesen']['titel'] == 'blick-aufs-wesen'


def test_no_h1_removes_nothing(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\n---\n> **Quelle:** LC S. 1\n\n## Wirkung\n\nText.\n')
    html = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['html']
    assert 'Quelle' in html
    assert '<h2>Wirkung</h2>' in html


def test_h1_title_keeps_trailing_hash_of_word(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\n---\n# Lerne C#\n\nText.\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['titel'] == 'Lerne C#'


def test_quelle_only_without_seite(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\nquelle: LC\n---\n# X\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == 'LC'


def test_quelle_missing_gives_empty_string(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\nseite: 12\n---\n# X\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == ''


def test_seite_as_int_and_string(vault):
    _write(vault, f'{ZAUBER}/a', '---\nquelle: LC\nseite: 15\n---\n# A\n')
    _write(vault, f'{ZAUBER}/b', '---\nquelle: LC\nseite: "15f."\n---\n# B\n')
    res = _load(vault, [f'{ZAUBER}/a', f'{ZAUBER}/b'])
    assert res[f'{ZAUBER}/a']['quelle'] == 'LC S. 15'
    assert res[f'{ZAUBER}/b']['quelle'] == 'LC S. 15f.'


def test_no_frontmatter_still_loads(vault):
    _write(vault, f'{ZAUBER}/x', '# X\n\nText.\n')
    art = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']
    assert art['titel'] == 'X'
    assert art['quelle'] == ''
    assert art['meta'] == []


def test_text_values_are_raw_not_escaped(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\nprobe: "KL<IN & FF"\n---\n# A & B <c>\n')
    art = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']
    assert art['titel'] == 'A & B <c>'
    assert art['meta'] == [{'label': 'Probe', 'wert': 'KL<IN & FF'}]


# --- Wikilinks ------------------------------------------------------------

def test_wikilink_with_text_uses_link_fn(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\nSiehe [[{ZAUBER}/y|Text]] dort.\n')
    html = _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['html']
    assert f'<a href="test-link://{ZAUBER}/y">Text</a>' in html


def test_wikilink_calls_link_fn_with_path(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\n[[{ZAUBER}/y|A]] und [[{ZAUBER}/z#Abschnitt|B]]\n')
    calls = []

    def spy(path):
        calls.append(path)
        return 'https://example.org/' + path.replace('#', '-')

    _load(vault, [f'{ZAUBER}/x'], spy)
    assert calls == [f'{ZAUBER}/y', f'{ZAUBER}/z#Abschnitt']


def test_wikilink_with_real_obsidian_uri(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\nSiehe [[{ZAUBER}/y|Text]].\n')
    html = _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']
    assert (f'<a href="obsidian://open?vault=DSA-Vault&amp;file={ZAUBER}/y.md">Text</a>') in html


def test_wikilink_without_text_uses_last_path_part(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\nSiehe [[{ZAUBER}/blick-aufs-wesen]].\n')
    html = _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']
    assert '>blick aufs wesen</a>' in html


def test_wikilink_with_anchor(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\n[[{ZAUBER}/y#Wirkung|Text]]\n')
    html = _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']
    assert f'file={ZAUBER}/y.md#Wirkung">Text</a>' in html


def test_wikilink_with_parentheses_in_path_does_not_break_markdown(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\nVor [[{ZAUBER}/y (alt)|Text]] nach.\n')
    html = _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']
    assert '>Text</a> nach.' in html
    assert '%28alt%29' in html
    assert '[[' not in html


def test_wikilink_with_parentheses_from_a_naive_link_fn(vault):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\nVor [[a/(b) c|Text]] nach.\n')
    html = _load(vault, [f'{ZAUBER}/x'], lambda p: f'/x/{p}')[f'{ZAUBER}/x']['html']
    assert '>Text</a> nach.' in html


def test_wikilink_in_table_cell_with_escaped_pipe(vault):
    _write(vault, f'{ZAUBER}/x',
           f'---\nname: X\n---\n# X\n\n| A | B |\n|---|---|\n| [[{ZAUBER}/y\\|Text]] | zwei |\n')
    html = _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']
    assert '>Text</a></td>' in html
    assert '<td>zwei</td>' in html


def test_wikilink_with_quote_or_angle_bracket_cannot_break_attribute(vault):
    _write(vault, f'{ZAUBER}/x',
           f'---\nname: X\n---\n# X\n\n[[a/b"onmouseover="alert(1)|T"x]] [[a/<b>|<i>T</i>]]\n')
    html = _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']
    assert '"onmouseover=' not in html
    assert '<i>' not in html
    assert '<b>' not in html
    assert '&lt;i&gt;T&lt;/i&gt;' in html


# --- Key / path handling --------------------------------------------------

def test_key_is_original_wiki_path_including_anchor(vault):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    key = f'{ZAUBER}/adlerauge#Wirkung'
    res = _load(vault, [key])
    assert list(res) == [key]
    # D-050: the anchor now selects the '## Wirkung' section (it used to load the whole file)
    assert res[key]['titel'] == 'Wirkung'
    assert 'Blick' in res[key]['html'] and 'Keine Wirkung' not in res[key]['html']


def test_empty_paths_give_empty_dict(vault):
    assert _load(vault, []) == {}


def test_duplicate_paths_give_one_entry(vault):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    res = _load(vault, [f'{ZAUBER}/adlerauge'] * 3)
    assert list(res) == [f'{ZAUBER}/adlerauge']


def test_missing_file_is_skipped_silently(vault, caplog):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    with caplog.at_level(logging.DEBUG):
        res = _load(vault, [f'{ZAUBER}/fehlt', f'{ZAUBER}/adlerauge'])
    assert list(res) == [f'{ZAUBER}/adlerauge']
    assert caplog.records == []


def test_render_failure_skips_only_that_article(vault, caplog):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    _write(vault, f'{ZAUBER}/kaputt', '---\nname: KAPUTT\n---\n# KAPUTT\n\n[[wiki/dsa-4.1/zauber/kaputt|x]]\n')

    def link(path):
        if path.endswith('kaputt'):
            raise RuntimeError('link_fn kaputt')
        return _link(path)

    with caplog.at_level(logging.WARNING):
        res = _load(vault, [f'{ZAUBER}/kaputt', f'{ZAUBER}/adlerauge'], link)
    assert list(res) == [f'{ZAUBER}/adlerauge']
    assert [r.levelno for r in caplog.records] == [logging.WARNING]
    assert 'kaputt' in caplog.records[0].getMessage()


@pytest.mark.parametrize('path', ['', None])
def test_empty_or_none_path_is_skipped(vault, path):
    assert _load(vault, [path]) == {}


def test_directory_is_skipped(vault):
    (vault / ZAUBER / 'ordner.md').mkdir(parents=True)
    assert _load(vault, [f'{ZAUBER}/ordner']) == {}


@pytest.fixture
def secret_vault(vault):
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    _write(vault, 'helden/illaen-baernhold/zauber', '---\nname: GEHEIM\n---\n# Geheim\n')
    _write(vault, 'wiki/dsa-4.1x/zauber/fake', '---\nname: FAKE\n---\n# Fake\n')
    _write(vault, 'wiki/andere/artikel', '---\nname: ANDERE\n---\n# Andere\n')
    _write(vault, 'wiki/dsa-4.1/_regeln', '---\nname: REGELN\n---\n# Regeln\n')
    return vault


@pytest.mark.parametrize('path', [
    f'{ZAUBER}/../../../../helden/illaen-baernhold/zauber',
    '../secret',
    f'{ZAUBER}/../../../../../etc/passwd',
    'helden/illaen-baernhold/zauber',
    'wiki/andere/artikel',
    'wiki/dsa-4.1x/zauber/fake',
    'wiki/dsa-4.1/../andere/artikel',
    f'wiki\\dsa-4.1\\zauber\\adlerauge',
    f'{ZAUBER}\\adlerauge',
    f'{ZAUBER}/..\\..\\..\\helden\\illaen-baernhold\\zauber',
    '/wiki/dsa-4.1/zauber/adlerauge',
    'C:/wiki/dsa-4.1/zauber/adlerauge',
    f'{ZAUBER}/adlerauge\x00',
])
def test_path_outside_whitelist_is_skipped(secret_vault, path):
    assert _load(secret_vault, [path]) == {}


def test_absolute_path_is_skipped(secret_vault):
    absolute = str(secret_vault / ZAUBER / 'adlerauge')
    assert _load(secret_vault, [absolute]) == {}
    assert _load(secret_vault, [absolute.replace('\\', '/')]) == {}


def test_other_wiki_folder_files_inside_dsa_are_allowed(secret_vault):
    assert list(_load(secret_vault, ['wiki/dsa-4.1/_regeln'])) == ['wiki/dsa-4.1/_regeln']


def test_dotdot_that_stays_inside_whitelist_is_allowed(secret_vault):
    key = f'{ZAUBER}/../zauber/adlerauge'
    assert list(_load(secret_vault, [key])) == [key]


def test_symlink_escape_is_skipped(vault):
    _write(vault, 'helden/illaen-baernhold/zauber', '---\nname: GEHEIM\n---\n# Geheim\n')
    (vault / ZAUBER).mkdir(parents=True)
    link = vault / ZAUBER / 'boese.md'
    try:
        link.symlink_to(vault / 'helden' / 'illaen-baernhold' / 'zauber.md')
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f'symlinks not creatable here: {exc}')
    assert _load(vault, [f'{ZAUBER}/boese']) == {}


def test_symlinked_directory_escape_is_skipped(vault):
    _write(vault, 'helden/illaen-baernhold/zauber', '---\nname: GEHEIM\n---\n# Geheim\n')
    (vault / 'wiki' / 'dsa-4.1').mkdir(parents=True)
    link = vault / 'wiki' / 'dsa-4.1' / 'raus'
    try:
        link.symlink_to(vault / 'helden' / 'illaen-baernhold', target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f'symlinks not creatable here: {exc}')
    assert _load(vault, ['wiki/dsa-4.1/raus/zauber']) == {}


# --- Unreadable / broken files -------------------------------------------

@pytest.mark.parametrize('text', [
    '---\nname: X\nkosten: 1 AsP (Ach: 2)\n# X\n\nText.\n',
    '---\nname: X\nprobe: KL/IN/FF\n# X\n\nText.\n',
    '---\nname: X\nkosten: 1 AsP (Ach: 2)\n---\n# X\n\nText.\n',  # closed, but unquoted ': ' is invalid YAML
    '---\n- a\n- b\n---\n# X\n\nText.\n',  # valid YAML, but not a mapping
])
def test_unreadable_frontmatter_warns_and_is_skipped(vault, caplog, text):
    _write(vault, f'{ZAUBER}/offen', text)
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    with caplog.at_level(logging.WARNING):
        res = _load(vault, [f'{ZAUBER}/offen', f'{ZAUBER}/adlerauge'])
    assert list(res) == [f'{ZAUBER}/adlerauge']
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert f'{ZAUBER}/offen' in warnings[0].getMessage()


def test_invalid_yaml_warning_carries_the_yaml_diagnosis(vault, caplog):
    _write(vault, f'{ZAUBER}/kaputt', '---\nname: X\nkosten: 1 AsP (Ach: 2)\n---\n# X\n')
    with caplog.at_level(logging.WARNING):
        assert _load(vault, [f'{ZAUBER}/kaputt']) == {}
    message = caplog.records[0].getMessage()
    assert 'Zeile' in message  # the wording of PyYAML's message itself is not ours to pin


def test_non_utf8_file_warns_and_is_skipped(vault, caplog):
    p = vault / ZAUBER / 'latin.md'
    p.parent.mkdir(parents=True)
    p.write_bytes('---\nname: Ärger\n---\n# Ärger\n'.encode('latin-1'))
    _write(vault, f'{ZAUBER}/adlerauge', ADLERAUGE)
    with caplog.at_level(logging.WARNING):
        res = _load(vault, [f'{ZAUBER}/latin', f'{ZAUBER}/adlerauge'])
    assert list(res) == [f'{ZAUBER}/adlerauge']
    assert len([r for r in caplog.records if r.levelno == logging.WARNING]) == 1


# --- Sonderfertigkeiten: pfad#anker laedt nur den ##-Abschnitt ------------------

SF = 'wiki/dsa-4.1/sonderfertigkeiten'
SF_DATEI = f'{SF}/magische-sonderfertigkeiten'
ANKER_A = 'Aufmerksamkeit'
ANKER_MK = 'Merkmalskenntnis [einzelnes Merkmal]'
ANKER_OK = 'Ortskenntnis (Stadtteil / Kleinstadt)'

SF_GRUPPE = """---
typ: sf-gruppe
kategorie: magisch
quelle: WdZ
---

# Magische Sonderfertigkeiten (Gildenmagier)

> **Quelle:** Wege der Zauberei (WdZ)

Einleitung vor der ersten Ueberschrift.

---

## Aufmerksamkeit

Text ALPHA mit **Fettdruck**.

### Regel

Unterabschnitt REGEL.

---

## Merkmalskenntnis [einzelnes Merkmal]

Text BETA.

- Punkt eins

---

## Ortskenntnis (Stadtteil / Kleinstadt)

Text GAMMA.

---
"""


def _sf(vault, *anker):
    _write(vault, SF_DATEI, SF_GRUPPE)
    return _load(vault, [f'{SF_DATEI}#{a}' for a in anker])


def test_anchor_loads_only_that_section(vault):
    res = _sf(vault, ANKER_A)
    assert list(res) == [f'{SF_DATEI}#{ANKER_A}']
    art = res[f'{SF_DATEI}#{ANKER_A}']
    assert art['titel'] == ANKER_A
    html = art['html']
    assert 'ALPHA' in html and '<strong>Fettdruck</strong>' in html
    assert '<h3>Regel</h3>' in html and 'REGEL' in html
    assert 'BETA' not in html and 'GAMMA' not in html
    assert 'Einleitung' not in html and 'Gildenmagier' not in html
    assert '<h1' not in html and '<h2' not in html
    assert '<hr' not in html


def test_anchor_section_without_trailing_rule_and_last_section(vault):
    _write(vault, SF_DATEI, SF_GRUPPE.rstrip('\n').removesuffix('---'))
    html = _load(vault, [f'{SF_DATEI}#{ANKER_OK}'])[f'{SF_DATEI}#{ANKER_OK}']['html']
    assert 'GAMMA' in html
    assert '<hr' not in html


def test_only_the_trailing_rule_of_a_section_is_removed(vault):
    _write(vault, SF_DATEI, SF_GRUPPE.replace('Text BETA.', 'Text BETA.\n\n---\n\nText DELTA.'))
    html = _load(vault, [f'{SF_DATEI}#{ANKER_MK}'])[f'{SF_DATEI}#{ANKER_MK}']['html']
    assert 'BETA' in html and 'DELTA' in html
    assert html.count('<hr') == 1


def test_missing_anchor_warns_once_and_is_skipped(vault, caplog):
    _write(vault, SF_DATEI, SF_GRUPPE)
    fehlt = f'{SF_DATEI}#Gibt es nicht'
    with caplog.at_level(logging.WARNING):
        res = _load(vault, [fehlt, f'{SF_DATEI}#{ANKER_A}'])
    assert list(res) == [f'{SF_DATEI}#{ANKER_A}']
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert fehlt in warnings[0].getMessage()


def test_missing_anchor_never_falls_back_to_the_whole_file(vault):
    _write(vault, SF_DATEI, SF_GRUPPE)
    assert _load(vault, [f'{SF_DATEI}#Gibt es nicht']) == {}
    assert _load(vault, [f'{SF_DATEI}#']) != {}  # empty anchor = no anchor = whole file, as before


@pytest.mark.parametrize('anker, marker', [(ANKER_MK, 'BETA'), (ANKER_OK, 'GAMMA')])
def test_anchor_with_brackets_spaces_and_slash_hits_the_right_section(vault, anker, marker):
    art = _sf(vault, anker)[f'{SF_DATEI}#{anker}']
    assert art['titel'] == anker
    assert marker in art['html']
    assert 'ALPHA' not in art['html']


def test_two_anchors_of_one_file_are_two_separate_entries(vault):
    res = _sf(vault, ANKER_A, ANKER_MK)
    assert list(res) == [f'{SF_DATEI}#{ANKER_A}', f'{SF_DATEI}#{ANKER_MK}']
    assert 'ALPHA' in res[f'{SF_DATEI}#{ANKER_A}']['html'] and 'BETA' not in res[f'{SF_DATEI}#{ANKER_A}']['html']
    assert 'BETA' in res[f'{SF_DATEI}#{ANKER_MK}']['html'] and 'ALPHA' not in res[f'{SF_DATEI}#{ANKER_MK}']['html']


def test_same_anchor_twice_is_loaded_once(vault):
    res = _sf(vault, ANKER_A, ANKER_A)
    assert list(res) == [f'{SF_DATEI}#{ANKER_A}']


def test_anchor_entry_takes_quelle_from_frontmatter_and_has_no_meta(vault):
    art = _sf(vault, ANKER_A)[f'{SF_DATEI}#{ANKER_A}']
    assert art['quelle'] == 'WdZ'
    assert art['meta'] == []
    assert set(art) == {'titel', 'quelle', 'meta', 'html'}


def test_anchor_is_never_used_as_a_file_path(vault):
    # Decoy INSIDE the whitelist: SF_DATEI + '/' + '../geheim' would land on it, and it even carries the matching
    # heading, so a path-building anchor would load it (verified by mutation: replace('#', '/') in _resolve_article).
    _write(vault, SF_DATEI, SF_GRUPPE)
    _write(vault, f'{SF}/geheim', '---\nname: G\n---\n# G\n\n## ../geheim\n\nGEHEIM\n')
    assert _load(vault, [f'{SF_DATEI}#../geheim']) == {}


def test_empty_section_warns_and_is_skipped(vault, caplog):
    _write(vault, SF_DATEI, '---\ntyp: sf-gruppe\n---\n\n# G\n\n## Leer\n\n---\n\n## Voll\n\nINHALT\n')
    with caplog.at_level(logging.WARNING):
        res = _load(vault, [f'{SF_DATEI}#Leer', f'{SF_DATEI}#Voll'])
    assert list(res) == [f'{SF_DATEI}#Voll']
    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert f'{SF_DATEI}#Leer' in warnings[0].getMessage()


def test_path_without_anchor_still_loads_the_whole_file(vault):
    _write(vault, SF_DATEI, SF_GRUPPE)
    art = _load(vault, [SF_DATEI])[SF_DATEI]
    assert art['titel'] == 'Magische Sonderfertigkeiten (Gildenmagier)'
    for marker in ('ALPHA', 'BETA', 'GAMMA'):
        assert marker in art['html']
    assert '<h2>Aufmerksamkeit</h2>' in art['html']


# --- Escaping / security --------------------------------------------------

def _body_html(vault, body):
    _write(vault, f'{ZAUBER}/x', f'---\nname: X\n---\n# X\n\n{body}\n')
    return _load(vault, [f'{ZAUBER}/x'], obsidian_uri)[f'{ZAUBER}/x']['html']


def test_script_tag_is_escaped(vault):
    html = _body_html(vault, '<script>alert(1)</script>')
    assert '<script' not in html
    assert '&lt;script&gt;' in html


def test_inline_script_tag_is_escaped(vault):
    html = _body_html(vault, 'Text <script>alert(1)</script> Ende')
    assert '<script' not in html
    assert '&lt;script&gt;' in html


def test_img_onerror_is_escaped(vault):
    html = _body_html(vault, '<img src=x onerror=alert(1)>\n\nInline <img src=x onerror=alert(2)> Text')
    assert '<img' not in html
    assert '&lt;img' in html


def test_html_block_and_comment_are_escaped(vault):
    html = _body_html(vault, '<div onclick="x()">Box</div>\n\n<!-- Kommentar -->')
    assert '<div' not in html
    assert '<!--' not in html


@pytest.mark.parametrize('link', [
    '[x](javascript:alert(1))',
    '[x](JavaScript:alert(1))',
    '[x](vbscript:msgbox(1))',
    '[x](data:text/html;base64,PHNjcmlwdD4=)',
    '[x][ref]\n\n[ref]: javascript:alert(1)',
    '<javascript:alert(1)>',
])
def test_dangerous_link_protocols_do_not_become_href(vault, link):
    html = _body_html(vault, link)
    assert 'href="javascript:' not in html.lower()
    assert 'href="vbscript:' not in html.lower()
    assert 'href="data:' not in html.lower()


def test_dangerous_image_protocol_does_not_become_src(vault):
    html = _body_html(vault, '![x](javascript:alert(1))')
    assert 'src="javascript:' not in html.lower()


def test_obsidian_link_survives_harmful_protocol_filter(vault):
    html = _body_html(vault, f'[[{ZAUBER}/y|Text]]')
    assert 'href="obsidian://' in html


# --- Echte Stabzauber-Seite: Vorbedingung der Ritual-Artikelvorschau ------------
# Bewusst gegen die echte Wiki-Datei (LLM-Domäne, kein Live-Bogen; vgl. den zustaende.md-Test in test_rendering.py):
# der Loader lädt nur '## <Anker>'-Abschnitte, also muss jeder Stabzauber eine H2-Überschrift haben.

STABZAUBER_DATEI = 'wiki/dsa-4.1/rituale/stabzauber'
STABZAUBER_NAMEN = [
    'Bindung des Stabes', 'Doppeltes Maß', 'Ewige Flamme', 'Flammenschwert', 'Hammer des Magus', 'Kraftfokus',
    'Merkmalsfokus', 'Modifikationsfokus', 'Schuppenhaut', 'Seil des Adepten', 'Zauberspeicher', 'Apport',
]


@pytest.fixture(scope='module')
def stabzauber_sections():
    text = (VAULT_ROOT / (STABZAUBER_DATEI + '.md')).read_text(encoding='utf-8')
    return split_sections(text, 2)


@pytest.mark.parametrize('name', STABZAUBER_NAMEN)
def test_stabzauber_article_has_a_nonempty_h2_section_per_stabzauber(stabzauber_sections, name):
    assert name in stabzauber_sections
    assert stabzauber_sections[name].strip()


@pytest.mark.parametrize('name', STABZAUBER_NAMEN)
def test_stabzauber_section_has_no_stray_rule_and_renders_no_hr(stabzauber_sections, name):
    lines = [ln.strip() for ln in stabzauber_sections[name].split('\n') if ln.strip()]
    assert '---' not in lines[:-1]  # only a single closing rule may remain; the loader cuts it off
    res = load_wiki_artikel(VAULT_ROOT, [f'{STABZAUBER_DATEI}#{name}'], _link)
    assert '<hr' not in res[f'{STABZAUBER_DATEI}#{name}']['html']


@pytest.mark.parametrize('name, eigen, fremd', [
    ('Kraftfokus', 'Erschaffungsprobe', 'zusätzliche Spontane Modifikation'),  # Fokus mit Detailtext
    ('Ewige Flamme', 'Stab brennt auf Kommando', 'Chamäleon'),                 # knapper Abschnitt aus den Tabellen
])
def test_stabzauber_anchor_loads_only_its_section_without_warning(caplog, name, eigen, fremd):
    pfad = f'{STABZAUBER_DATEI}#{name}'
    with caplog.at_level(logging.WARNING):
        res = load_wiki_artikel(VAULT_ROOT, [pfad], _link)
    assert list(res) == [pfad]
    art = res[pfad]
    assert art['titel'] == name and art['html'].strip()
    assert eigen in art['html'] and fremd not in art['html']
    assert not [r for r in caplog.records if r.levelno == logging.WARNING]


# --- Detailregeln der sieben zunächst knappen Abschnitte (Sprint 023 T2) ----------
# Bindung/Doppeltes Maß/Ewige Flamme/Flammenschwert/Hammer/Schuppenhaut/Seil tragen die Buchregeln und enden mit einer
# Quellenzeile; Foki, Zauberspeicher und Apport waren schon ausgeführt und haben bewusst keine solche Schlusszeile.

STABZAUBER_MIT_REGELN = [
    'Bindung des Stabes', 'Doppeltes Maß', 'Ewige Flamme', 'Flammenschwert', 'Hammer des Magus', 'Schuppenhaut',
    'Seil des Adepten',
]


def _stabzauber_html(name):
    pfad = f'{STABZAUBER_DATEI}#{name}'
    return load_wiki_artikel(VAULT_ROOT, [pfad], _link)[pfad]['html']


@pytest.mark.parametrize('name', STABZAUBER_NAMEN)
def test_stabzauber_section_has_no_detailregeln_placeholder_left(stabzauber_sections, name):
    assert 'ausgearbeitet' not in stabzauber_sections[name]


@pytest.mark.parametrize('name', STABZAUBER_MIT_REGELN)
def test_stabzauber_section_with_rules_ends_with_source_line(stabzauber_sections, name):
    lines = [ln.strip() for ln in stabzauber_sections[name].split('\n') if ln.strip() and ln.strip() != '---']
    assert re.fullmatch(r'\*Quelle: WdZ S\. [^*]+\*', lines[-1]), lines[-1]


def test_flammenschwert_misslingens_table_lists_every_w6_result():
    html = _stabzauber_html('Flammenschwert')
    tabellen = [t for t in re.findall(r'<table.*?</table>', html, re.S) if '1W6' in t]
    assert len(tabellen) == 1
    zeilen = [r for r in re.findall(r'<tr>(.*?)</tr>', tabellen[0], re.S) if '<td' in r]
    # Buch (WdZ S. 110): vier Ergebniszeilen, die zusammen alle sechs W6-Werte abdecken
    labels = [re.sub(r'<[^>]+>', '', re.search(r'<td[^>]*>(.*?)</td>', r, re.S).group(1)).strip() for r in zeilen]
    assert labels == ['1–3', '4', '5', '6']


@pytest.mark.parametrize('name', STABZAUBER_NAMEN)
def test_stabzauber_anchor_html_text_has_no_literal_double_asterisk(name):
    text = re.sub(r'<[^>]+>', '', _stabzauber_html(name))
    assert '**' not in text
