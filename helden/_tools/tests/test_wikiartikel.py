"""Tests for parsers.wikiartikel — wiki article/section loader (synthetic vault only)."""
import html as html_lib
import logging
import re
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import WIKILINK_RE, split_sections
from parsers.wikiartikel import _MARKDOWN, load_wiki_artikel, render_markdown
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


def test_empty_frontmatter_quelle_falls_back_to_the_quote_block(vault):
    _write(vault, f'{ZAUBER}/x', '---\nname: X\nquelle:\nseite: 12\n---\n# X\n\n> **Quelle:** WdZ S. 3\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == 'WdZ S. 3'


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


# --- Quelle-Fallback aus dem Zitatblock (Sprint 023 T4, B-022) --------------------
# Kapitelartikel ohne Frontmatter (u. a. alle Rituale) tragen die Quelle nur als '> **Quelle:** …' unter der H1.
# Gelesen wird sie vor dem Abschnittsschnitt, aber nur aus dem Kopfblock (vor der ersten '## '-Überschrift).

KAPITEL = ('# Kapitel\n\n> **Quelle:** WdZ S. 108–114\n\nEinleitung.\n\n'
           '## Erster\n\nText ALPHA.\n\n---\n\n## Zweiter\n\nText BETA.\n')
QUELLE_SPAETER = '# Kapitel\n\n> Hinweis\n\nText.\n\n## Abschnitt\n\n> **Quelle:** WdZ S. 9\n\nText.\n'


def test_quelle_falls_back_to_quote_block_without_frontmatter(vault):
    _write(vault, f'{ZAUBER}/k', KAPITEL)
    assert _load(vault, [f'{ZAUBER}/k'])[f'{ZAUBER}/k']['quelle'] == 'WdZ S. 108–114'


def test_quelle_fallback_reads_the_head_block_on_anchor_load(vault):
    _write(vault, f'{ZAUBER}/k', KAPITEL)
    art = _load(vault, [f'{ZAUBER}/k#Zweiter'])[f'{ZAUBER}/k#Zweiter']
    assert art['quelle'] == 'WdZ S. 108–114'
    assert 'BETA' in art['html'] and 'ALPHA' not in art['html'] and 'Quelle' not in art['html']


def test_frontmatter_quelle_wins_over_quote_block_line(vault):
    _write(vault, f'{ZAUBER}/x', '---\nquelle: LC\nseite: 15\n---\n# X\n\n> **Quelle:** WdZ S. 1\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == 'LC S. 15'


def test_fallback_does_not_append_frontmatter_seite(vault):
    _write(vault, f'{ZAUBER}/x', '---\nseite: 12\n---\n# X\n\n> **Quelle:** WdZ S. 108–114\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == 'WdZ S. 108–114'


@pytest.mark.parametrize('anker', ['', '#Abschnitt'])
def test_quelle_line_in_a_later_section_is_not_used(vault, anker):
    _write(vault, f'{ZAUBER}/k', QUELLE_SPAETER)
    assert _load(vault, [f'{ZAUBER}/k{anker}'])[f'{ZAUBER}/k{anker}']['quelle'] == ''


def test_fallback_takes_only_the_first_line_of_the_quote_block(vault):
    _write(vault, f'{ZAUBER}/x', '# X\n\n> **Quelle:** WdZ S. 1  \n> zweite Zeile\n\nText.\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == 'WdZ S. 1'


@pytest.mark.parametrize('zeile, erwartet', [
    ('> **Quelle:** **WdZ** `S. 9` – [[wiki/dsa-4.1/buecher/wege-der-zauberei|Wege der Zauberei]]',
     'WdZ S. 9 – Wege der Zauberei'),
    ('> **Quelle:** siehe [[wiki/dsa-4.1/buecher/liber-cantiones]]', 'siehe liber cantiones'),
    ('> **Quelle**: WdZ S. 9', 'WdZ S. 9'),
    ('> **Quelle:**', ''),
])
def test_fallback_strips_markup_for_display(vault, zeile, erwartet):
    _write(vault, f'{ZAUBER}/x', f'# X\n\n{zeile}\n\nText.\n')
    assert _load(vault, [f'{ZAUBER}/x'])[f'{ZAUBER}/x']['quelle'] == erwartet


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
    # die Effektzellen tragen die Buchwerte (Ausschnitte statt Volltext: robust gegen Umformulierungen)
    effekte = [re.sub(r'<[^>]+>', '', re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)[1]) for r in zeilen]
    for erwartet, effekt in zip(['1W20', '7 Punkte Volumen', 'nicht wiederholt', 'Bruchfaktor'], effekte):
        assert erwartet in effekt, (erwartet, effekt)
    assert 'sieben Wochen' in effekte[0]


@pytest.mark.parametrize('name', STABZAUBER_NAMEN)
def test_stabzauber_anchor_html_text_has_no_literal_double_asterisk(name):
    text = re.sub(r'<[^>]+>', '', _stabzauber_html(name))
    assert '**' not in text


# --- Rohsternchen am Fettrand (Sprint 023 T3, B-020) -----------------------------
# Bewusst gegen die echten Wiki-Dateien (LLM-Domäne): Buchnotation `ZfP*`/`TaP*`/`RkP*` am Ende eines Fettbereichs muss
# als `**… ZfP\***` geschrieben sein, sonst zeigt die Artikelvorschau (mistune) rohes `**…***`. Der Test rendert die echte
# Zeile bzw. die ganze Datei mit derselben Renderer-Konfiguration wie der Loader.

ROHSTERN_DATEIEN = [
    'wiki/dsa-4.1/zauber/odem-arcanum',
    'wiki/dsa-4.1/alchimie/alchimie-grundregeln',
    'wiki/dsa-4.1/alchimie/artefakt-herstellung',
    'wiki/dsa-4.1/alchimie/zauberzeichen-grundregeln',
    'wiki/dsa-4.1/goetter/liturgien-grundregeln',
    'wiki/dsa-4.1/grundregeln/erfahrung',
    'wiki/dsa-4.1/magie/magische-bibliothek',
    'wiki/dsa-4.1/rituale/rituale-grundregeln',
    'wiki/dsa-4.1/magie/metamagie',
    'wiki/dsa-4.1/vor-nachteile/sonderfertigkeiten-allgemein',
]

# (Datei, eindeutiger Zeilenausschnitt, erwarteter <strong>-Inhalt)
ROHSTERN_ZEILEN = [
    ('wiki/dsa-4.1/zauber/odem-arcanum', '- **0–2 ZfP', '0–2 ZfP*'),
    ('wiki/dsa-4.1/zauber/odem-arcanum', '- **3 ZfP', '3 ZfP*'),
    ('wiki/dsa-4.1/zauber/odem-arcanum', '- **7 ZfP', '7 ZfP*'),
    ('wiki/dsa-4.1/zauber/odem-arcanum', '- **12+ ZfP', '12+ ZfP*'),
    ('wiki/dsa-4.1/alchimie/alchimie-grundregeln', 'Je **4 ZfP', '4 ZfP*'),
    ('wiki/dsa-4.1/alchimie/artefakt-herstellung', '**Maximale akkumulierbare ZfP', 'Maximale akkumulierbare ZfP*'),
    ('wiki/dsa-4.1/alchimie/zauberzeichen-grundregeln', 'richtet sich nach **RkP', 'RkP*'),
    ('wiki/dsa-4.1/goetter/liturgien-grundregeln', 'im Sinne der ZfP', 'LkP*'),
    ('wiki/dsa-4.1/grundregeln/erfahrung', 'Nur durch besondere Erleichterungen', 'A*'),
    ('wiki/dsa-4.1/magie/magische-bibliothek', 'mindestens **30 TaP', '30 TaP*'),
    ('wiki/dsa-4.1/rituale/rituale-grundregeln', 'Die **RkP', 'RkP*'),
    ('wiki/dsa-4.1/magie/metamagie', 'Modifikationen werden durch **Ansammeln', 'Ansammeln von TaP* + ZfP*'),
    ('wiki/dsa-4.1/vor-nachteile/sonderfertigkeiten-allgemein', '| **Apport (OR)', 'Apport (OR)*'),
    ('wiki/dsa-4.1/vor-nachteile/sonderfertigkeiten-allgemein', '| **Zibilja-Rituale', 'Zibilja-Rituale*'),
    ('wiki/dsa-4.1/vor-nachteile/sonderfertigkeiten-allgemein', '| **Kontakt zum Großen Geist', 'Kontakt zum Großen Geist*'),
    ('wiki/dsa-4.1/vor-nachteile/sonderfertigkeiten-allgemein', '| **Ritualkenntnis [Schamanentradition]',
     'Ritualkenntnis [Schamanentradition] (H)*'),
]


def _rohstern_html(zeile):
    if zeile.lstrip().startswith('|'):  # Tabellenzeile: ohne Kopf/Trennzeile würde sie als Absatz gerendert
        n = zeile.count('|') - 1
        zeile = '|' + ' a |' * n + '\n' + '|' + '---|' * n + '\n' + zeile
    return render_markdown(zeile)


def _sichtbarer_text(rendered):
    return html_lib.unescape(re.sub(r'<[^>]+>', '', rendered))


@pytest.mark.parametrize('datei, ausschnitt, erwartet', ROHSTERN_ZEILEN)
def test_rohsternchen_am_fettrand_rendert_als_strong_mit_literalem_stern(datei, ausschnitt, erwartet):
    zeilen = [z for z in (VAULT_ROOT / (datei + '.md')).read_text(encoding='utf-8').split('\n') if ausschnitt in z]
    assert len(zeilen) == 1, zeilen
    rendered = _rohstern_html(zeilen[0])
    assert f'<strong>{erwartet}</strong>' in rendered
    assert '**' not in _sichtbarer_text(rendered)


@pytest.mark.parametrize('datei', ROHSTERN_DATEIEN)
def test_rohsternchen_datei_zeigt_kein_woertliches_doppelsternchen(datei):
    rendered = render_markdown((VAULT_ROOT / (datei + '.md')).read_text(encoding='utf-8'))
    betroffen = [z for z in _sichtbarer_text(rendered).split('\n') if '**' in z]
    assert not betroffen, betroffen[:3]


# --- Buch-Sternchen (Sprint 025 T1, B-023) ---------------------------------------------------------------------
# `ZfP*`/`LkP*`/`RkP*`/`TaP*` ist im Wiki absichtliche Buchnotation (Stern = „nach Abzug"). mistune paart solche Sterne
# sonst zu <em>; render_markdown schützt sie per Platzhalter. Synthetische Texte belegen den Fehler, die Korpus-Tests
# laufen BEWUSST gegen die echten Wiki-Dateien (LLM-Domäne) und sichern die Stern-Bilanz Quelle == HTML.

BUCHKUERZEL = ['ZfP', 'LkP', 'RkP', 'TaP']
PLATZHALTER = chr(0xE000)  # kein Backslash-Escape im Quelltext (Werkzeug-Übergaben machen daraus Steuerzeichen)
BACKSLASH = chr(92)
_KUERZEL_RE = '(?:ZfP|LkP|RkP|TaP)'
# Quelle: `ZfP*` oder `ZfP<Backslash>*`; ein unmaskierter Stern vor weiterem Stern (`**LkP**`) ist Fettrand.
_STERN_RE = re.escape('*')
_QUELL_STERN_RE = re.compile(
    _KUERZEL_RE + '(?:' + re.escape(BACKSLASH) + _STERN_RE + '|' + _STERN_RE + '(?!' + _STERN_RE + '))')
_HTML_STERN_RE = re.compile(_KUERZEL_RE + _STERN_RE)
WIKI_DIR = VAULT_ROOT / 'wiki'


@pytest.mark.parametrize('kuerzel', BUCHKUERZEL)
def test_buchstern_einzeln_bleibt_literal(kuerzel):
    rendered = render_markdown(f'{kuerzel}* nach Abzug')
    assert rendered == f'<p>{kuerzel}* nach Abzug</p>\n'


@pytest.mark.parametrize('kuerzel', BUCHKUERZEL)
def test_buchstern_zwei_vorkommen_in_einer_zeile_werden_nicht_zu_em(kuerzel):
    rendered = render_markdown(f'{kuerzel}*/2 > {kuerzel}*')
    assert rendered == f'<p>{kuerzel}*/2 &gt; {kuerzel}*</p>\n'


def test_buchstern_in_umschliessender_kursivspanne_bleibt_sichtbar():
    rendered = render_markdown('*TaP*-Schwellen sind SL-anpassbar. Verdecktes Würfeln möglich.*')
    assert rendered == '<p><em>TaP*-Schwellen sind SL-anpassbar. Verdecktes Würfeln möglich.</em></p>\n'


def test_echte_kursivschrift_neben_buchstern_bleibt_kursiv():
    rendered = render_markdown('*kursiv* und ZfP* dazwischen *noch kursiv*')
    assert rendered == '<p><em>kursiv</em> und ZfP* dazwischen <em>noch kursiv</em></p>\n'


def test_bereits_escapter_buchstern_bleibt_ein_stern():
    rendered = render_markdown(f'*kursiv* ZfP{BACKSLASH}*/2 > TaP{BACKSLASH}* *noch kursiv*')
    assert rendered == '<p><em>kursiv</em> ZfP*/2 &gt; TaP* <em>noch kursiv</em></p>\n'


def test_fettrand_vor_buchstern_wird_nicht_mit_notation_verwechselt():
    # `**LkP**` schließt einen Fettbereich (Stern folgt auf Stern): darf nicht als `LkP*` geschützt werden.
    rendered = render_markdown(f'**LkW** = Wert · **LkP** = Rest · **LkP{BACKSLASH}*** = im Sinne der ZfP*')
    assert rendered == ('<p><strong>LkW</strong> = Wert · <strong>LkP</strong> = Rest · '
                        '<strong>LkP*</strong> = im Sinne der ZfP*</p>\n')


def test_buchstern_in_code_bleibt_literal_und_platzhalter_leckt_nicht():
    fence = '```'
    text = f'Bei `ZfP*/2 > ZfP*` gilt ZfP* nicht.\n\n{fence}\nZfP*/2 > ZfP*\n{fence}\n'
    rendered = render_markdown(text)
    assert '<code>ZfP*/2 &gt; ZfP*</code>' in rendered
    assert '<pre><code>ZfP*/2 &gt; ZfP*\n</code></pre>' in rendered
    assert PLATZHALTER not in rendered


def test_buchstern_in_tabellenzelle_bleibt_literal():
    rendered = render_markdown('| TaP* | Wert |\n|---|---|\n| ZfP*/2 > ZfP* | TaP* |\n')
    assert '<th>TaP*</th>' in rendered
    assert '<td>ZfP*/2 &gt; ZfP*</td>' in rendered
    assert '<td>TaP*</td>' in rendered
    assert '<em>' not in rendered


def test_vorhandener_platzhalter_im_text_laesst_die_vorbehandlung_aus():
    # Ein fremdes U+E000 dürfte nach der Rückersetzung nicht fälschlich zu '*' werden: dann läuft der Text unverändert.
    text = f'Fremd {PLATZHALTER} und ZfP*/2 > ZfP*'
    rendered = render_markdown(text)
    assert rendered == _MARKDOWN(text)
    assert PLATZHALTER in rendered


def test_loader_rendert_buchstern_literal_ohne_em(vault):
    text = ADLERAUGE.replace('Schärft den **Blick** des Zaubernden.', 'Bei ZfP*/2 > ZfP* gilt X.')
    _write(vault, f'{ZAUBER}/sternchen', text)
    html = _load(vault, [f'{ZAUBER}/sternchen'])[f'{ZAUBER}/sternchen']['html']
    assert 'ZfP*/2 &gt; ZfP*' in html
    assert '<em>' not in html
    assert PLATZHALTER not in html


def _wiki_dateien():
    dateien = sorted(WIKI_DIR.rglob('*.md'))
    assert dateien, f'keine Wiki-Dateien unter {WIKI_DIR}'
    return dateien


def test_korpus_stern_bilanz_quelle_gleich_html():
    abweichend = []
    for datei in _wiki_dateien():
        text = datei.read_text(encoding='utf-8')
        quelle = len(_QUELL_STERN_RE.findall(text))
        if quelle and quelle != len(_HTML_STERN_RE.findall(render_markdown(text))):
            abweichend.append(datei.relative_to(VAULT_ROOT).as_posix())
    assert not abweichend, (len(abweichend), abweichend[:3])


def test_korpus_enthaelt_keinen_platzhalter():
    # Sichert die Annahme der Rückersetzung: kein Wiki-Text bringt U+E000 selbst mit.
    mit_platzhalter = [d.relative_to(VAULT_ROOT).as_posix() for d in _wiki_dateien()
                       if PLATZHALTER in d.read_text(encoding='utf-8')]
    assert not mit_platzhalter, mit_platzhalter[:3]


# --- Quelle der Stabzauber-Vorschau (Sprint 023 T4, B-022) -------------------------
# Bewusst gegen die echte Wiki-Datei (LLM-Domäne, Vorbild der Stabzauber-Tests oben): stabzauber.md hat kein Frontmatter
# (Ordner-Konvention rituale/), die Quelle steht nur im Zitatblock unter der H1 – die Anker-Vorschau braucht sie von dort.

@pytest.mark.parametrize('name', STABZAUBER_NAMEN)
def test_stabzauber_anchor_quelle_comes_from_the_quote_block(name):
    pfad = f'{STABZAUBER_DATEI}#{name}'
    assert load_wiki_artikel(VAULT_ROOT, [pfad], _link)[pfad]['quelle'].startswith('WdZ')


# --- Anker-Links des Heldenbogens <-> Stabzauber-Überschriften (Sprint 023 T6, L25(b)) ----------------------------
# Läuft BEWUSST gegen den echten Bogen (helden/illaen-baernhold/rituale.md): der Test soll die Drift zwischen den
# Wiki-Überschriften und den Anker-Links im Bogen erkennen (zweiter bewusst live gekoppelter Test nach
# test_build_context_wiki_artikel_smoke_live_vault in test_rendering.py). Er pinnt weder Spielwerte noch eine Anzahl.

HELD_RITUALE = VAULT_ROOT / 'helden' / 'illaen-baernhold' / 'rituale.md'


def test_held_stabzauber_anchor_links_hit_a_section_of_the_wiki_article(stabzauber_sections):
    if not HELD_RITUALE.is_file():
        pytest.skip(f'{HELD_RITUALE} fehlt')
    text = HELD_RITUALE.read_text(encoding='utf-8')
    anker = [m.group(1).split('#', 1)[1] for m in WIKILINK_RE.finditer(text)
             if m.group(1).startswith(STABZAUBER_DATEI + '#')]
    if not anker:
        # kein Anker-Link mehr im Bogen = Entscheidung des Users, nicht rot; nur ein kaputter Extraktor wäre ein Fehler
        assert STABZAUBER_DATEI + '#' not in text, 'Anker-Links vorhanden, aber nicht extrahiert'
        pytest.skip('Heldenbogen enthält keinen Stabzauber-Anker-Link mehr')
    for name in anker:
        assert name in stabzauber_sections, f'kein "## {name}" in stabzauber.md'
        pfad = f'{STABZAUBER_DATEI}#{name}'
        res = load_wiki_artikel(VAULT_ROOT, [pfad], _link)
        assert pfad in res, f'load_wiki_artikel lädt {pfad} nicht'
        assert res[pfad]['html'].strip(), pfad
