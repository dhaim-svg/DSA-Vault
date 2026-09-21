"""Tests for CSS/JS bundling and static vs. server rendering in rendering.py."""
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import pytest

import rendering
import server
from rendering import (
    CHRONIK_BILD_PREFIX_SERVER, CHRONIK_BILD_PREFIX_STATIC, CSS_FILES, JS_FILES, STATIC_DIR, VAULT_ROOT,
    build_context, css_bundle, js_files, make_env, render_dashboard,
)
from tests.heldfixtures import write_mini_held
from tests.jsfixtures import js_function, needs_node, run_node


def test_css_files_exist_and_nonempty():
    for name in CSS_FILES:
        path = STATIC_DIR / name
        assert path.is_file(), f'{name} fehlt in static/'
        assert path.read_text(encoding='utf-8').strip(), f'{name} ist leer'


def test_css_bundle_is_ordered_concatenation():
    expected = ''.join(
        (STATIC_DIR / name).read_text(encoding='utf-8') for name in CSS_FILES
    )
    assert css_bundle() == expected


def test_every_static_css_file_is_listed():
    on_disk = {p.name for p in STATIC_DIR.glob('*.css')}
    assert on_disk == set(CSS_FILES)


def test_css_files_have_no_duplicates():
    assert len(CSS_FILES) == len(set(CSS_FILES))


def test_css_bundle_is_env_global():
    assert make_env().globals['css_bundle'] is css_bundle


TEMPLATES_DIR = TOOLS_DIR / 'templates'
PARTIALS_DIR = TEMPLATES_DIR / 'partials'
TAB_PARTIALS = ['kampf', 'talente', 'zauber', 'steigern', 'inventar', 'profil', 'chronik', 'sprachen']


def _dashboard_source():
    return (TEMPLATES_DIR / 'dashboard.html.j2').read_text(encoding='utf-8')


def test_tab_partial_files_exist():
    on_disk = {p.name for p in PARTIALS_DIR.glob('*.j2')}
    assert {f'{name}.j2' for name in TAB_PARTIALS} <= on_disk


def test_dashboard_includes_each_partial_once_in_order():
    src = _dashboard_source()
    positions = []
    for name in TAB_PARTIALS:
        tag = "{% include 'partials/" + name + ".j2' %}"
        assert src.count(tag) == 1, f'{tag} muss genau einmal vorkommen'
        positions.append(src.index(tag))
    assert positions == sorted(positions)


def test_every_include_target_exists():
    targets = re.findall(r"\{%\s*include\s+'([^']+)'\s*%\}", _dashboard_source())
    assert targets
    for target in targets:
        assert (TEMPLATES_DIR / target).is_file(), f'{target} fehlt'


def test_no_tab_block_left_in_dashboard():
    assert not re.search(r'''id=["']tab-''', _dashboard_source())


def test_each_partial_starts_with_its_own_tab_container():
    for name in TAB_PARTIALS:
        text = (PARTIALS_DIR / f'{name}.j2').read_text(encoding='utf-8')
        first_line = next(line for line in text.splitlines() if line.strip())
        assert first_line.lstrip().startswith('<'), f'{name}.j2 beginnt nicht mit einem Tag'
        assert f'id="tab-{name}"' in first_line, f'{name}.j2 beginnt mit fremdem Tab-Container'


def test_journal_partial_is_sub_partial_of_chronik():
    journal = (PARTIALS_DIR / 'journal.j2').read_text(encoding='utf-8')
    assert not journal.lstrip().startswith('<div class="tab-content"')
    assert 'id="tab-journal"' not in journal
    chronik = (PARTIALS_DIR / 'chronik.j2').read_text(encoding='utf-8')
    assert chronik.count("{% include 'partials/journal.j2' %}") == 1
    assert "{% include 'partials/journal.j2' %}" not in _dashboard_source()


def test_register_partial_is_sub_partial_of_chronik():
    register = (PARTIALS_DIR / 'register.j2').read_text(encoding='utf-8')
    assert not register.lstrip().startswith('<div class="tab-content"')
    assert 'id="tab-register"' not in register
    chronik = (PARTIALS_DIR / 'chronik.j2').read_text(encoding='utf-8')
    assert chronik.count("{% include 'partials/register.j2' %}") == 1
    assert "{% include 'partials/register.j2' %}" not in _dashboard_source()


def test_missing_css_file_fails_loudly(monkeypatch):
    monkeypatch.setattr(rendering, 'CSS_FILES', ['gibt-es-nicht.css'])
    with pytest.raises(FileNotFoundError):
        css_bundle()


LIVE_HELD = VAULT_ROOT / 'helden' / 'illaen-baernhold'


@pytest.fixture(scope='module')
def live_html():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    return render_dashboard(build_context('illaen-baernhold'))


def test_render_has_single_style_tag_and_single_css_bundle(live_html):
    assert len(re.findall(r'<style\b', live_html)) == 1
    assert live_html.count(css_bundle()) == 1


def test_render_has_each_tab_container_exactly_once(live_html):
    for name in TAB_PARTIALS:
        assert live_html.count(f'id="tab-{name}"') == 1, f'tab-{name}'


def test_render_hoists_resource_values_into_js(live_html):
    assert re.search(r'LE: \{ current: \d+', live_html)


def test_build_context_exposes_kampagne_slug_and_chronik():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    ctx = build_context('illaen-baernhold')
    assert ctx['kampagne_slug'] == 'drachenchronik'
    assert 'chronik' in ctx
    assert ctx['chronik_bild_prefix'] == CHRONIK_BILD_PREFIX_STATIC


def test_server_render_passes_kampagne_slug_to_js():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    assert 'kampagne_slug: "drachenchronik"' in server._render_dashboard('illaen-baernhold')


def test_server_context_uses_server_bild_prefix(monkeypatch):
    captured = {}
    monkeypatch.setattr(server, 'build_context',
                        lambda slug, vault_root, **kw: captured.update(kw) or {})
    monkeypatch.setattr(server, 'render_dashboard', lambda ctx: '')
    server._render_dashboard('illaen-baernhold')
    assert captured == {'chronik_bild_prefix': CHRONIK_BILD_PREFIX_SERVER}


def test_build_context_without_chronik_file_has_empty_chronik(tmp_path, monkeypatch):
    monkeypatch.setattr(rendering, 'load_held', lambda root, slug: {})
    monkeypatch.setattr(rendering, 'load_kampagne', lambda root, slug: {})
    ctx = build_context('x', tmp_path, chronik_bild_prefix='/p/')
    assert ctx['chronik'] == {'spielabende': [], 'meta': {}}
    assert ctx['chronik_bild_prefix'] == '/p/'
    assert ctx['register'] == {'nscs': [], 'orte': []}
    assert ctx['wiki_artikel'] == {}


def test_build_context_has_register_from_live_vault():
    ctx = build_context('illaen-baernhold')
    assert set(ctx['register']) == {'nscs', 'orte'}
    assert ctx['register']['nscs']
    assert ctx['register']['orte']


def test_build_context_wiki_artikel_smoke_live_vault():
    """Bewusst live: Rauchtest, dass die Kette Bogen -> Artikel-Pfade -> geladene Artikel mit dem echten Vault noch
    zusammenpasst (ein zerschossener Bogen faellt hier auf). Keine Zusicherung ueber einzelne Zauber/SF/Rituale --
    welche einen Artikel-Link haben, aendert der User; das pruefen die synthetischen Tests."""
    ctx = build_context('illaen-baernhold')
    artikel = ctx['wiki_artikel']
    assert isinstance(artikel, dict)
    assert artikel
    zauber_pfade = {z['wiki_path'] for z in ctx['held']['zauber']}
    sf_pfade = {sf['wiki_path'] for sf in ctx['held']['sf']['magisch'] + ctx['held']['sf']['allgemein'] if sf['wiki_path']}
    rituale = ctx['held']['rituale']
    ritual_pfade = {r['wiki_path'] for r in rituale['stabzauber'] + rituale['andere'] if r['wiki_path']}
    assert set(artikel) <= zauber_pfade | sf_pfade | ritual_pfade
    # completeness (incl. unquoted ': ' frontmatter) is pinned by the synthetic loader tests, not by the live vault
    for pfad, art in artikel.items():
        assert set(art) == {'titel', 'quelle', 'meta', 'html'}, pfad
        assert art['html'].strip(), pfad


def test_build_context_wiki_artikel_skips_spells_without_article(tmp_path, monkeypatch):
    artikel_dir = tmp_path / 'wiki' / 'dsa-4.1' / 'zauber'
    artikel_dir.mkdir(parents=True)
    (artikel_dir / 'da.md').write_text('---\nname: DA\n---\n# DA\n\n## Wirkung\n\nText.\n', encoding='utf-8')
    monkeypatch.setattr(rendering, 'load_held', lambda root, slug: {'zauber': [
        {'name': 'Da', 'wiki_path': 'wiki/dsa-4.1/zauber/da'},
        {'name': 'Weg', 'wiki_path': 'wiki/dsa-4.1/zauber/weg'},
        {'name': 'Leer', 'wiki_path': None},
        {'name': 'Ohne'},
    ]})
    monkeypatch.setattr(rendering, 'load_kampagne', lambda root, slug: {})
    ctx = build_context('x', tmp_path)
    assert list(ctx['wiki_artikel']) == ['wiki/dsa-4.1/zauber/da']
    assert ctx['wiki_artikel']['wiki/dsa-4.1/zauber/da']['titel'] == 'DA'


def test_build_context_wiki_artikel_includes_sf_anchor_sections(tmp_path, monkeypatch):
    sf_dir = tmp_path / 'wiki' / 'dsa-4.1' / 'sonderfertigkeiten'
    sf_dir.mkdir(parents=True)
    (sf_dir / 'magische.md').write_text(
        '---\nquelle: WdZ\n---\n# M\n\n## Eins\n\nText EINS.\n\n---\n\n## Zwei\n\nText ZWEI.\n', encoding='utf-8')
    (sf_dir / 'allgemeine.md').write_text('---\nquelle: WdH\n---\n# A\n\n## Drei\n\nText DREI.\n', encoding='utf-8')
    pfad = 'wiki/dsa-4.1/sonderfertigkeiten/'
    monkeypatch.setattr(rendering, 'load_held', lambda root, slug: {
        'zauber': [],
        'sf': {
            'magisch': [
                {'name': 'Eins', 'wiki_path': pfad + 'magische#Eins'},
                {'name': 'Eins b', 'wiki_path': pfad + 'magische#Eins'},
                {'name': 'Ohne', 'wiki_path': None},
                {'name': 'Fehlt', 'wiki_path': pfad + 'magische#Fehlt'},
            ],
            'allgemein': [{'name': 'Drei', 'wiki_path': pfad + 'allgemeine#Drei'}, {'name': 'Leer'}],
        },
    })
    monkeypatch.setattr(rendering, 'load_kampagne', lambda root, slug: {})
    ctx = build_context('x', tmp_path)
    assert list(ctx['wiki_artikel']) == [pfad + 'magische#Eins', pfad + 'allgemeine#Drei']
    assert ctx['wiki_artikel'][pfad + 'magische#Eins']['titel'] == 'Eins'
    assert 'ZWEI' not in ctx['wiki_artikel'][pfad + 'magische#Eins']['html']
    assert ctx['wiki_artikel'][pfad + 'allgemeine#Drei']['quelle'] == 'WdH'


def test_build_context_wiki_artikel_includes_ritual_rows(tmp_path, monkeypatch):
    rit_dir = tmp_path / 'wiki' / 'dsa-4.1' / 'rituale'
    rit_dir.mkdir(parents=True)
    # frontmatterlos: die Quelle kommt aus dem Kopfblock (B-022-Fallback), nicht aus dem YAML
    (rit_dir / 'stabzauber.md').write_text(
        '# Stabzauber\n\n> **Quelle:** WdZ S. 99\n\n## Eins\n\nText EINS.\n\n---\n\n## Zwei\n\nText ZWEI.\n',
        encoding='utf-8')
    (rit_dir / 'andere.md').write_text('# Andere\n\n> **Quelle:** WdH S. 7\n\n## Apport\n\nText APPORT.\n',
                                       encoding='utf-8')
    pfad = 'wiki/dsa-4.1/rituale/'
    monkeypatch.setattr(rendering, 'load_held', lambda root, slug: {
        'zauber': [],
        'sf': {'magisch': [], 'allgemein': []},
        'rituale': {
            'stabzauber': [
                {'name': 'Eins', 'wiki_path': pfad + 'stabzauber#Eins'},
                {'name': 'Eins b', 'wiki_path': pfad + 'stabzauber#Eins'},
                {'name': 'Ohne', 'wiki_path': None},
                {'name': 'Fehlt', 'wiki_path': pfad + 'stabzauber#Fehlt'},
            ],
            'andere': [{'name': 'Apport', 'wiki_path': pfad + 'andere#Apport'}, {'name': 'Leer', 'wiki_path': None}],
        },
    })
    monkeypatch.setattr(rendering, 'load_kampagne', lambda root, slug: {})
    ctx = build_context('x', tmp_path)
    assert list(ctx['wiki_artikel']) == [pfad + 'stabzauber#Eins', pfad + 'andere#Apport']
    eins = ctx['wiki_artikel'][pfad + 'stabzauber#Eins']
    assert eins['titel'] == 'Eins'
    assert eins['quelle'] == 'WdZ S. 99'
    assert 'EINS' in eins['html']
    assert 'ZWEI' not in eins['html']
    apport = ctx['wiki_artikel'][pfad + 'andere#Apport']
    assert apport['titel'] == 'Apport'
    assert apport['quelle'] == 'WdH S. 7'
    assert 'APPORT' in apport['html']


@pytest.mark.parametrize('rituale', [None, {}, {'stabzauber': None, 'andere': None}, {'stabzauber': [], 'andere': []}])
def test_build_context_wiki_artikel_tolerates_missing_ritual_lists(tmp_path, monkeypatch, rituale):
    artikel_dir = tmp_path / 'wiki' / 'dsa-4.1' / 'zauber'
    artikel_dir.mkdir(parents=True)
    (artikel_dir / 'da.md').write_text('---\nname: DA\n---\n# DA\n\n## Wirkung\n\nText.\n', encoding='utf-8')
    monkeypatch.setattr(rendering, 'load_held', lambda root, slug: {
        'zauber': [{'name': 'Da', 'wiki_path': 'wiki/dsa-4.1/zauber/da'}], 'rituale': rituale})
    monkeypatch.setattr(rendering, 'load_kampagne', lambda root, slug: {})
    ctx = build_context('x', tmp_path)
    assert list(ctx['wiki_artikel']) == ['wiki/dsa-4.1/zauber/da']


BILD = 'drachenchronik-daten/pergament-abschrift.png'


def test_render_chronik_tab_static(live_html):
    ctx = build_context('illaen-baernhold')
    assert live_html.count('id="tab-chronik"') == 1
    assert 'id="tab-journal"' not in live_html
    assert live_html.count('data-tab="chronik"') == 1
    assert 'data-tab="journal"' not in live_html
    assert len(re.findall(r'class="card chronik-abend"', live_html)) == len(ctx['chronik']['spielabende'])
    assert '../abenteuer/drachenchronik/' + BILD in live_html
    assert '/chronik-bild/' not in live_html


def test_render_has_register_view_exactly_once(live_html):
    assert live_html.count('id="chronik-view-register"') == 1


def test_render_zauber_header_row_has_spell_head_class(live_html):
    # Kopfzeile teilt .spell mit den Datenzeilen (Sortier-JS: .spell:first-child); die
    # Zusatzklasse ist der Haken, mit dem die Schmalansicht sie ausblendet (D-040).
    assert live_html.count('class="spell spell-head"') == 1
    assert re.search(r'\.spell\.spell-head\s*\{[^}]*display:\s*none', css_bundle())


def _strip_print_blocks(css):
    """CSS ohne @media-print-Bloecke (Klammer-Zaehlung, damit verschachtelte Regeln nicht brechen)."""
    out, i = [], 0
    for m in re.finditer(r'@media\s+print\s*\{', css):
        if m.start() < i:
            continue
        out.append(css[i:m.start()])
        depth, j = 1, m.end()
        while depth and j < len(css):
            depth += {'{': 1, '}': -1}.get(css[j], 0)
            j += 1
        i = j
    out.append(css[i:])
    return ''.join(out)


def _pos(html, marker, was=''):
    """Position des Markers im HTML; fehlt er, scheitert der Test mit lesbarer Meldung statt mit ValueError (B-024)."""
    pos = html.find(marker)
    assert pos != -1, f'{was or marker} fehlt im Render'
    return pos


def test_pos_returns_position_or_fails_with_readable_message():
    assert _pos('ab<x>cd', '<x>') == 2
    with pytest.raises(AssertionError, match='Sortier-Button fehlt im Render'):
        _pos('ab', 'data-spell-sort', 'Sortier-Button')
    with pytest.raises(AssertionError, match='data-spell-sort fehlt im Render'):
        _pos('ab', 'data-spell-sort')


def test_render_zauber_sort_toolbar_and_list_wrapper(live_html):
    # D-043: Toolbar-Button -> Kopfzeile -> Listen-Wrapper -> Legende; Sortier-JS verschiebt nur Zeilen im Wrapper.
    assert live_html.count('data-spell-list') == 1
    assert live_html.count('data-spell-sort') == 1
    assert '<button type="button" class="spell-sort-btn" data-spell-sort' in live_html
    toolbar = _pos(live_html, 'data-spell-sort', 'Sortier-Button')
    head = _pos(live_html, 'class="spell spell-head"', 'Zauber-Kopfzeile')
    wrapper = _pos(live_html, 'data-spell-list', 'Listen-Wrapper')
    legend = _pos(live_html, 'class="legend-row"', 'Legende')
    assert toolbar < head < wrapper < legend


def test_render_zauber_rows_all_inside_list_wrapper(live_html):
    n = len(build_context('illaen-baernhold')['held']['zauber'])
    start = live_html.index('data-spell-list')
    inside = live_html[start:live_html.index('class="legend-row"')]
    assert len(re.findall(r'<div class="spell"[ >]', inside)) == n
    assert len(re.findall(r'<div class="spell"[ >]', live_html)) == n
    assert 'spell-head' not in inside


# -- Synthetischer Vault: Artikel-/SF-Render-Tests haengen nicht am echten Heldenbogen ---------------------------
# Live-Zusicherungen ("Zauber X hat einen Artikel-Link") brechen, sobald der User seinen Bogen aendert, ohne dass ein
# Codefehler vorliegt. Der Vault unten hat genau die Faelle, die die Tests brauchen; die einzige bewusst live
# gebliebene Pruefung dieser Kette ist test_build_context_wiki_artikel_smoke_live_vault.

SYNTH_SLUG = 'synth'
ZAUBER_ALPHA = 'wiki/dsa-4.1/zauber/alpha'
ZAUBER_BETA = 'wiki/dsa-4.1/zauber/beta'
ZAUBER_OHNE_DATEI = 'wiki/dsa-4.1/zauber/gamma'  # Link im Bogen, aber kein Artikel im Wiki

_SYNTH_ILLAEN = """---
typ: held
name: Synth Held
stufe: 1
---

## Eigenschaften & Basiswerte

### Eigenschaften

| Eigenschaft | Mod. | Start | Aktuell |
|-------------|------|-------|---------|
| Mut (MU) | 0 | 12 | 12 |
| Klugheit (KL) | 0 | 12 | 12 |
| Intuition (IN) | 0 | 12 | 12 |
| Charisma (CH) | 0 | 12 | 12 |
| Fingerfertigkeit (FF) | 0 | 12 | 12 |
| Gewandtheit (GE) | 0 | 12 | 12 |
| Konstitution (KO) | 0 | 12 | 12 |
| Körperkraft (KK) | 0 | 12 | 12 |

### Basiswerte

| Basiswert | Formel | Mod. | Start | Max | Akt. |
|-----------|--------|------|-------|-----|------|
| Lebensenergie (LE) | (KO+KO+KK)/2 | 0 | 18 | 18 | 18 |
| Ausdauer (AU) | (MU+KO+GE)/2 | 0 | 18 | 18 | 18 |
| Astralenergie (AE) | (MU+IN+CH)/2 | 0 | 18 | 18 | 18 |
"""

_SYNTH_ZAUBER = r"""## Zauberliste

| Zauber | Probe | ZfW | Merkmale | Haus | Komp | Lern | ZD | Kosten | Wirkung | Modifikationen | Notizen |
|--------|-------|-----|----------|------|------|------|----|--------|---------|----------------|---------|
| [[wiki/dsa-4.1/zauber/alpha\|Alpha Zauber]] | KL/KL/FF | 7 | Objk | | C | C | 15 A | 4 AsP | Wirkung A | — | |
| [[wiki/dsa-4.1/zauber/beta\|Beta Zauber]] | KL/IN/CH | 5 | Hell | | C | C | 30 A | 6 AsP | Wirkung B | — | |
| [[wiki/dsa-4.1/zauber/gamma\|Gamma Zauber]] | IN/GE/KO | 3 | Eign | | C | C | 1 A | 2 AsP | Wirkung G | — | |
"""

_SYNTH_SF = r"""## Magische Sonderfertigkeiten

| Sonderfertigkeit | Beschreibung / Nutzen |
|------------------|-----------------------|
| [[wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Alpha\|Alpha]] | Beschreibung-A |
| Beta | Beschreibung-B |

## Allgemeine Sonderfertigkeiten

| Sonderfertigkeit | Beschreibung / Nutzen |
|------------------|-----------------------|
| [[wiki/dsa-4.1/sonderfertigkeiten/allgemeine-sonderfertigkeiten#Delta\|Delta]] | Beschreibung-D |
"""


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


@pytest.fixture(scope='module')
def synth_vault(tmp_path_factory):
    """Minimaler Vault mit einem Helden (3 Zauber, 3 SF) und den zugehoerigen Wiki-Artikeln.

    Mit Artikel: Zauber Alpha/Beta, SF Alpha (magisch, Anker) und Delta (allgemein, Anker).
    Ohne Artikel: Zauber Gamma (Link ohne Datei), SF Beta (ohne Link)."""
    root = tmp_path_factory.mktemp('synth_vault')
    held = root / 'helden' / SYNTH_SLUG
    for name in ('talente', 'rituale', 'vor-nachteile', 'ausruestung', 'steigerungs-log', 'vorgeschichte'):
        _write(held / f'{name}.md', '')
    _write(held / '_illaen.md', _SYNTH_ILLAEN)
    _write(held / 'zauber.md', _SYNTH_ZAUBER)
    _write(held / 'sonderfertigkeiten.md', _SYNTH_SF)
    wiki = root / 'wiki' / 'dsa-4.1'
    for name, quelle in (('alpha', 'LC'), ('beta', 'WdZ')):
        _write(wiki / 'zauber' / f'{name}.md',
               f'---\nname: {name.title()}\nquelle: {quelle}\nseite: 1\n---\n# {name.title()}\n\n## Wirkung\n\nText {name.upper()}.\n')
    _write(wiki / 'sonderfertigkeiten' / 'magische-sonderfertigkeiten.md',
           '---\nquelle: WdZ\n---\n# M\n\n## Alpha\n\nText SF-ALPHA.\n')
    _write(wiki / 'sonderfertigkeiten' / 'allgemeine-sonderfertigkeiten.md',
           '---\nquelle: WdH\n---\n# A\n\n## Delta\n\nText SF-DELTA.\n')
    return root


@pytest.fixture(scope='module')
def synth_ctx(synth_vault):
    return build_context(SYNTH_SLUG, synth_vault)


@pytest.fixture(scope='module')
def synth_html(synth_ctx):
    return render_dashboard(synth_ctx)


VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


def _artikel_details_parents(html_fragment):
    """(Klassen des Elternelements, Klassen des Grosselternelements, data-spell-list am Grosselternelement) je
    <details class="artikel-details"> im Fragment; das Fragment beginnt am Listen-Wrapper."""
    from html.parser import HTMLParser

    found, stack = [], []

    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == 'details' and 'artikel-details' in (a.get('class') or '').split():
                parent = stack[-1] if stack else ('', {})
                grand = stack[-2] if len(stack) > 1 else ('', {})
                found.append(((parent[0], parent[1].get('class')), (grand[0], 'data-spell-list' in grand[1])))
            if tag not in VOID_TAGS:
                stack.append((tag, a))

        def handle_endtag(self, tag):
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    del stack[i:]
                    return

    P().feed(html_fragment)
    return found


def _spell_list_fragment(html):
    start = html.find('<div class="spell-list" data-spell-list>')
    assert start != -1, 'Zauberliste (data-spell-list) fehlt im Render'
    end = html.find('class="legend-row"', start)
    assert end != -1, 'Legende (legend-row) folgt nicht auf die Zauberliste'
    return html[start:end]


def test_render_wiki_artikel_details_one_per_spell_with_article(synth_ctx, synth_html):
    assert set(synth_ctx['wiki_artikel']) == {ZAUBER_ALPHA, ZAUBER_BETA, SF_A, SF_D}  # Zauber Gamma / SF Beta: kein Artikel
    assert synth_html.count('class="artikel-details"') == 2 + 2
    assert len(_artikel_details_parents(_sf_card(synth_html))) == 2  # D-050: SF-Zeilen, nicht die Zauberliste
    fragment = _spell_list_fragment(synth_html)
    assert len(re.findall(r'<div class="spell"[ >]', fragment)) == 3  # Gamma behaelt seine Zeile, nur ohne Details
    parents = _artikel_details_parents(fragment)
    assert len(parents) == 2
    # direktes Kind der Zeile (wandert beim Sortieren mit), Zeile direkt im Listen-Wrapper
    assert all(p == (('div', 'spell'), ('div', True)) for p in parents)


def test_render_wiki_artikel_empty_or_missing_has_no_details_but_keeps_name_links(synth_vault):
    ctx = build_context(SYNTH_SLUG, synth_vault)
    ctx['wiki_artikel'] = {}
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 0
    assert 'class="nlink"' in html
    del ctx['wiki_artikel']
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 0
    assert 'class="nlink"' in html


def test_render_wiki_artikel_escapes_text_fields_but_not_html(synth_vault):
    ctx = build_context(SYNTH_SLUG, synth_vault)
    ctx['wiki_artikel'] = {ZAUBER_ALPHA: {
        'titel': '<b>T</b>', 'quelle': 'Q<i>', 'meta': [{'label': 'L<u>', 'wert': 'W<s>'}], 'html': '<p>ok</p>',
    }}
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 1
    block = re.search(r'<details class="artikel-details">.*?</details>', html, re.S).group(0)
    for roh in ('<b>T</b>', 'Q<i>', 'L<u>', 'W<s>'):
        assert roh not in block
    for escaped in ('&lt;b&gt;T&lt;/b&gt;', 'Q&lt;i&gt;', 'L&lt;u&gt;', 'W&lt;s&gt;'):
        assert escaped in block
    assert '<div class="artikel-body"><p>ok</p></div>' in block


def test_render_wiki_artikel_has_single_obsidian_link_without_nlink(synth_html):
    fragment = _spell_list_fragment(synth_html)  # Zauberliste isolieren: die SF-Karte hat eigene Details
    found = re.search(r'<details class="artikel-details">.*?</details>', fragment, re.S)
    assert found, 'kein artikel-details in der Zauberliste'
    block = found.group(0)
    kopf = re.search(r'<div class="artikel-kopf">.*?</div>', block, re.S).group(0)
    assert kopf.count('href="obsidian://') == 1
    assert re.search(r'<a class="artikel-obsidian" href="obsidian://[^"]+">↗ Obsidian</a>', kopf)
    assert 'nlink' not in block
    # der ↗ am Zaubernamen bleibt Sache des Namenslinks in .name (CSS ::after)
    row = fragment[:fragment.find('class="artikel-details"')]
    assert '<div class="spell"' in row, 'die Details stehen in keiner Zauberzeile'
    assert row.rfind('class="nlink"') > row.rfind('<div class="spell"'), 'Zauberzeile ohne Namenslink vor den Details'


# -- D-050: Artikelvorschau fuer Sonderfertigkeiten ---------------------------

SF_A = 'wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Alpha'
SF_D = 'wiki/dsa-4.1/sonderfertigkeiten/allgemeine-sonderfertigkeiten#Delta'


@pytest.fixture
def sf_context(synth_vault):
    """Fabrik (wiki_artikel) -> frischer Kontext des synthetischen Vaults mit fuenf SF: Alpha (magisch) und Delta
    (allgemein) haben einen Anker-Link, Gamma/Eps einen ohne geladenen Artikel, Beta keinen Link. Jeder Aufruf
    baut den Kontext neu, damit Tests, die mehrere Varianten vergleichen, sich nicht ueber ein Dict beeinflussen."""
    def make(wiki_artikel):
        ctx = build_context(SYNTH_SLUG, synth_vault)
        ctx['held']['sf'] = {
            'magisch': [
                {'name': 'Alpha', 'wiki_path': SF_A, 'desc': 'Beschreibung-A'},
                {'name': 'Beta', 'wiki_path': None, 'desc': 'Beschreibung-B'},
                {'name': 'Gamma', 'wiki_path': 'wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Gamma',
                 'desc': 'Beschreibung-G'},
            ],
            'allgemein': [
                {'name': 'Delta', 'wiki_path': SF_D, 'desc': 'Beschreibung-D'},
                {'name': 'Eps', 'wiki_path': 'wiki/dsa-4.1/sonderfertigkeiten/allgemeine-sonderfertigkeiten#Eps', 'desc': ''},
            ],
        }
        ctx['wiki_artikel'] = wiki_artikel
        return ctx
    return make


def _sf_artikel(titel='Titel A', html='<p>Body A</p>'):
    return {'titel': titel, 'quelle': 'WdZ', 'meta': [], 'html': html}


def _sf_card(html):
    start = html.find('<h3 class="card-title">Sonderfertigkeiten</h3>')
    assert start != -1, 'SF-Karte fehlt im Render'
    end = html.find('</section>', start)
    assert end != -1, 'SF-Karte ist nicht geschlossen'
    return html[start:end]


def _sf_items(html_fragment):
    """[{'text': Text der Zeile, 'details': [Tag-Name des Elternelements je artikel-details]}] je <li> direkt unter
    einer ul.sf-list."""
    from html.parser import HTMLParser

    items, stack = [], []

    class P(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            item = stack[-1][2] if stack else None
            if tag == 'li' and stack and stack[-1][0] == 'ul' and 'sf-list' in (stack[-1][1].get('class') or '').split():
                item = {'text': '', 'details': []}
                items.append(item)
            if tag == 'details' and 'artikel-details' in (a.get('class') or '').split() and item is not None:
                item['details'].append(stack[-1][0])
            if tag not in VOID_TAGS:
                stack.append((tag, a, item))

        def handle_endtag(self, tag):
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    del stack[i:]
                    return

        def handle_data(self, data):
            if stack and stack[-1][2] is not None:
                stack[-1][2]['text'] += data

    P().feed(html_fragment)
    return items


def test_render_sf_artikel_details_inside_their_own_li_with_title_source_and_body(sf_context):
    html = render_dashboard(sf_context({SF_A: _sf_artikel(), SF_D: _sf_artikel('Titel D', '<p>Body D</p>')}))
    items = _sf_items(_sf_card(html))
    assert [i['details'] for i in items] == [['li'], [], [], ['li'], []]
    assert 'Alpha' in items[0]['text'] and 'Titel A' in items[0]['text'] and 'Body A' in items[0]['text']
    assert 'Titel D' in items[3]['text'] and 'Body D' in items[3]['text'] and 'Body A' not in items[3]['text']
    assert html.count('class="artikel-details"') == 2  # Zauber ohne geladenen Artikel bekommen keinen
    block = re.search(r'<details class="artikel-details">.*?</details>', _sf_card(html), re.S).group(0)
    assert '<span class="artikel-quelle">WdZ</span>' in block
    assert re.search(r'<a class="artikel-obsidian" href="obsidian://[^"]+">↗ Obsidian</a>', block)


def test_render_sf_artikel_details_follow_the_description(sf_context):
    card = _sf_card(render_dashboard(sf_context({SF_A: _sf_artikel()})))
    start = card.find('Alpha')
    assert start != -1, 'SF Alpha fehlt in der SF-Karte'
    end = card.find('</li>', start)
    assert end != -1, 'Zeile von Alpha ist nicht geschlossen'
    li = card[start:end]
    assert 'Beschreibung-A' in li, 'Beschreibung fehlt in der Alpha-Zeile'
    assert 'class="artikel-details"' in li, 'Details fehlen in der Alpha-Zeile'
    assert re.search(r'Beschreibung-A.*class="artikel-details"', li, re.S), 'Details stehen vor der Beschreibung'


def test_render_sf_without_article_has_no_details_and_keeps_its_row(sf_context):
    ctx = sf_context({SF_A: _sf_artikel()})
    unveraendert = _sf_card(render_dashboard(sf_context({})))
    assert 'artikel-details' not in unveraendert
    ctx['wiki_artikel'] = {}
    assert _sf_card(render_dashboard(ctx)) == unveraendert
    del ctx['wiki_artikel']
    assert _sf_card(render_dashboard(ctx)) == unveraendert
    for name in ('Alpha', 'Beta', 'Gamma', 'Delta', 'Eps'):
        assert name in unveraendert


def test_render_sf_artikel_escapes_text_fields_but_not_html(sf_context):
    art = {'titel': '<b>T</b>', 'quelle': 'Q<i>', 'meta': [], 'html': '<p>ok</p>'}
    html = render_dashboard(sf_context({SF_A: art}))
    block = re.search(r'<details class="artikel-details">.*?</details>', _sf_card(html), re.S).group(0)
    for roh in ('<b>T</b>', 'Q<i>'):
        assert roh not in block
    for escaped in ('&lt;b&gt;T&lt;/b&gt;', 'Q&lt;i&gt;'):
        assert escaped in block
    assert '<div class="artikel-body"><p>ok</p></div>' in block


def test_css_sf_artikel_details_sit_in_the_text_column_of_the_row():
    base = ' '.join(_decls(_css_rules(_strip_print_blocks(css_bundle())), '.sf-list > li > .artikel-details'))
    assert re.search(r'grid-column\s*:\s*2\b', base)
    assert re.search(r'min-width\s*:\s*0', base)
    # Abstand zur Beschreibung: nur Zeilen MIT Vorschau rücken auf 4px (kein Negativrand, der an gap:10px koppelt)
    rows = _css_rules(_strip_print_blocks(css_bundle()))
    assert any(re.search(r'row-gap\s*:\s*4px', d) for d in _decls(rows, '.sf-list > li:has(> .artikel-details)'))
    assert 'margin-top:-6px' not in base.replace(' ', '')


def test_css_print_sf_row_with_open_article_may_break_across_columns():
    # .sf-list > li{break-inside:avoid} zwaenge einen langen offenen Artikel sonst in eine Spalte
    prints = ''.join(_media_blocks(css_bundle(), r'@media\s+print'))
    assert re.search(r'\.sf-list\s*>\s*li\s*:has\(\s*\.artikel-details\[open\]\s*\)\s*\{[^}]*break-inside\s*:\s*auto', prints)


# Nachfahren-li direkt unter .sf-list: '.sf-list li', '.sf-list.general li', '.sf-list li:last-child', '.sf-list li:has(...)'
SF_DESCENDANT_LI_RE = re.compile(r'\.sf-list(?:\.[\w-]+)*\s+li(?::{1,2}[\w-]+(?:\([^()]*\))?)*$')


def test_css_sf_row_rules_only_hit_direct_li_children():
    # D-050: `.sf-list li{display:grid;grid-template-columns:14px 1fr;…}` traf auch die <li> der Aufzaehlungen IM Artikel
    # (.artikel-body li) und setzte deren Text in die 14-px-Spalte (~2 Zeichen je Zeile; Druck: break-inside/padding
    # ebenso). Zeilenregeln gehoeren auf `.sf-list > li` — auch im Druck-Block (css_bundle() enthaelt beide).
    rules = _css_rules(css_bundle())
    bad = sorted({sel for sel, _ in rules if SF_DESCENDANT_LI_RE.search(sel)})
    assert not bad, f'Nachfahren-li unter .sf-list (trifft auch Artikel-Listen): {bad}'
    direct = [sel for sel, _ in rules if re.match(r'\.sf-list\s*>\s*li\b', sel)]
    assert len(direct) >= 6, direct  # nicht vakuoes: Basis- und Druckregeln muessen als Kind-Selektoren vorhanden sein
    assert any('has(' in sel and 'open' in sel for sel in direct)  # Druckregel offener Artikel
    assert any(sel.endswith(':last-child') for sel in direct)


# -- D-051: Artikelvorschau fuer Ritual-Zeilen (Stabzauber & Rituale) ----------

RIT_A = 'wiki/dsa-4.1/rituale/stabzauber#Alfa'
RIT_C = 'wiki/dsa-4.1/rituale/stabzauber#Charlie'
RIT_D = 'wiki/dsa-4.1/rituale/stabzauber#Delta'

# heutiges Markup der Zeilen OHNE Link/Artikel (Stabzauber mit Badge+Meta, andere schlicht): darf sich nicht aendern
RIT_ROW_B = ('<li><span class="ico">❖</span><span><span class="sf-name">Bravo<span class="vol-badge">II</span>'
             '<span class="meta">MU/IN/CH · 3 AsP</span></span><span class="sf-desc">Effekt-B</span></span></li>')
RIT_ROW_E = ('<li><span class="ico">❖</span><span><span class="sf-name">Echo</span>'
             '<span class="sf-desc">Effekt-E</span></span></li>')


@pytest.fixture
def ritual_context(synth_vault):
    """Fabrik (wiki_artikel) -> frischer Kontext des synthetischen Vaults mit fuenf Ritual-Zeilen: Stabzauber Alfa
    (Anker-Link, Vol + Erschaffungsprobe), Bravo (kein Link), Charlie (Link ohne geladenen Artikel); andere Delta
    (Link), Echo (kein Link). Dazu ein belegter Zauberspeicher-Slot fuer die Abgrenzung der Speicher-Box."""
    def make(wiki_artikel):
        ctx = build_context(SYNTH_SLUG, synth_vault)
        ctx['held']['rituale'] = {
            'stabzauber': [
                {'name': 'Alfa', 'wiki_path': RIT_A, 'vol': 'I', 'erschaffungsprobe': 'KL/FF/KK', 'asp': '7',
                 'effekt': 'Effekt-A'},
                {'name': 'Bravo', 'wiki_path': None, 'vol': 'II', 'erschaffungsprobe': 'MU/IN/CH', 'asp': '3',
                 'effekt': 'Effekt-B'},
                {'name': 'Charlie', 'wiki_path': RIT_C, 'vol': '', 'erschaffungsprobe': '', 'asp': '',
                 'effekt': 'Effekt-C'},
            ],
            'andere': [
                {'name': 'Delta', 'wiki_path': RIT_D, 'effekt': 'Effekt-D'},
                {'name': 'Echo', 'wiki_path': None, 'effekt': 'Effekt-E'},
            ],
            'zauberspeicher_slots': [
                {'slot': 1, 'asp': '5', 'zauber': 'Ignifaxius', 'mods': '—', 'erneuerung': '—'},
            ],
            'stabzauber_regel': '',
        }
        ctx['wiki_artikel'] = wiki_artikel
        return ctx
    return make


def _ritual_card(html):
    start = html.find('<h3 class="card-title">Stabzauber &amp; Rituale')
    assert start != -1, 'Ritual-Karte fehlt im Render'
    end = html.find('</section>', start)
    assert end != -1, 'Ritual-Karte ist nicht geschlossen'
    return html[start:end]


def _ritual_li(card, name):
    """<li>…</li> der Zeile mit diesem Namen (der Artikelinhalt enthaelt kein </li>, solange die Fixture-HTML keine Liste hat)."""
    start = card.find(f'>{name}<')
    assert start != -1, f'Zeile {name} fehlt in der Ritual-Karte'
    start = card.rfind('<li>', 0, start)
    end = card.find('</li>', start)
    assert end != -1, f'Zeile {name} ist nicht geschlossen'
    return card[start:end + len('</li>')]


def test_render_ritual_artikel_details_inside_their_own_li_with_title_source_and_body(ritual_context):
    html = render_dashboard(ritual_context({RIT_A: _sf_artikel('Titel A', '<p>Body A</p>'),
                                            RIT_D: _sf_artikel('Titel D', '<p>Body D</p>')}))
    items = _sf_items(_ritual_card(html))
    assert [i['details'] for i in items] == [['li'], [], [], ['li'], []]  # Alfa, Bravo, Charlie, Delta, Echo
    assert 'Alfa' in items[0]['text'] and 'Titel A' in items[0]['text'] and 'Body A' in items[0]['text']
    assert 'Titel D' in items[3]['text'] and 'Body D' in items[3]['text'] and 'Body A' not in items[3]['text']
    for i in (1, 2, 4):  # Bravo (kein Link), Charlie (Link ohne Artikel), Echo (kein Link)
        assert 'Body' not in items[i]['text'] and 'Titel' not in items[i]['text']
    assert html.count('class="artikel-details"') == 2  # keine Zauber/SF im Kontext geladen
    block = re.search(r'<details class="artikel-details">.*?</details>', _ritual_card(html), re.S).group(0)
    assert '<span class="artikel-quelle">WdZ</span>' in block
    assert re.search(r'<a class="artikel-obsidian" href="obsidian://[^"]+">↗ Obsidian</a>', block)


def test_render_ritual_artikel_details_follow_the_description(ritual_context):
    card = _ritual_card(render_dashboard(ritual_context({RIT_A: _sf_artikel(), RIT_D: _sf_artikel()})))
    for name, effekt in (('Alfa', 'Effekt-A'), ('Delta', 'Effekt-D')):
        li = _ritual_li(card, name)
        assert effekt in li, f'Effekt fehlt in der {name}-Zeile'
        assert 'class="artikel-details"' in li, f'Details fehlen in der {name}-Zeile'
        assert re.search(effekt + r'.*class="artikel-details"', li, re.S), f'Details stehen vor dem Effekt ({name})'


def test_render_ritual_name_links_wrap_only_the_name_text(ritual_context):
    card = _ritual_card(render_dashboard(ritual_context({RIT_A: _sf_artikel(), RIT_D: _sf_artikel()})))
    alfa = _ritual_li(card, 'Alfa')
    assert re.search(r'<span class="sf-name"><a href="obsidian://[^"]+">Alfa</a><span class="vol-badge">I</span>'
                     r'<span class="meta">KL/FF/KK · 7 AsP</span></span>', alfa)
    for link in re.findall(r'<a href="obsidian://[^"]*">.*?</a>', card, re.S):
        assert 'vol-badge' not in link and 'meta' not in link  # sonst wird die Badge zum Link (↗ aus .sf-name a::after)
    # Link haengt an wiki_path, nicht am Artikel: Charlie hat keinen Artikel und behaelt den Link
    assert re.search(r'<span class="sf-name"><a href="obsidian://[^"]+">Charlie</a></span>', _ritual_li(card, 'Charlie'))
    assert re.search(r'<span class="sf-name"><a href="obsidian://[^"]+">Delta</a></span>', _ritual_li(card, 'Delta'))
    for name in ('Bravo', 'Echo'):  # ohne wiki_path: kein <a> im Namen
        li = _ritual_li(card, name)
        assert '<a ' not in li[:li.find('class="sf-desc"')], f'{name} hat einen Link im Namen'


def test_render_ritual_rows_without_wiki_path_keep_their_exact_markup(ritual_context):
    for artikel in ({}, {RIT_A: _sf_artikel(), RIT_D: _sf_artikel()}):
        card = _ritual_card(render_dashboard(ritual_context(artikel)))
        assert RIT_ROW_B in card
        assert RIT_ROW_E in card


def test_render_ritual_without_article_has_no_details_and_keeps_its_rows(ritual_context):
    ctx = ritual_context({RIT_A: _sf_artikel()})  # bewusst MIT Artikel gebaut und unten geleert bzw. entfernt
    unveraendert = _ritual_card(render_dashboard(ritual_context({})))
    assert 'artikel-details' not in unveraendert
    ctx['wiki_artikel'] = {}
    assert _ritual_card(render_dashboard(ctx)) == unveraendert
    del ctx['wiki_artikel']
    assert _ritual_card(render_dashboard(ctx)) == unveraendert
    for name in ('Alfa', 'Bravo', 'Charlie', 'Delta', 'Echo'):
        assert name in unveraendert
    assert unveraendert.count('<a href="obsidian://') == 3  # Alfa, Charlie, Delta: Namenslinks bleiben ohne Artikel


def test_render_ritual_artikel_escapes_text_fields_but_not_html(ritual_context):
    art = {'titel': '<b>T</b>', 'quelle': 'Q<i>', 'meta': [], 'html': '<p>ok</p>'}
    html = render_dashboard(ritual_context({RIT_A: art}))
    block = re.search(r'<details class="artikel-details">.*?</details>', _ritual_card(html), re.S).group(0)
    for roh in ('<b>T</b>', 'Q<i>'):
        assert roh not in block
    for escaped in ('&lt;b&gt;T&lt;/b&gt;', 'Q&lt;i&gt;'):
        assert escaped in block
    assert '<div class="artikel-body"><p>ok</p></div>' in block


def test_render_ritual_zauberspeicher_box_has_no_article_details(ritual_context):
    card = _ritual_card(render_dashboard(ritual_context({RIT_A: _sf_artikel(), RIT_D: _sf_artikel()})))
    box = card[card.find('<div class="speicher-box">'):]
    assert 'Zauberspeicher-Inhalt' in box and 'Ignifaxius' in box, 'Speicher-Box fehlt im Render'
    assert 'artikel-details' not in box
    assert card.count('class="artikel-details"') == 2  # beide Vorschauen stehen vor der Box (in den Ritual-Zeilen)


def test_dice_js_click_guard_ignores_clicks_inside_details():
    js = (STATIC_DIR / 'dice.js').read_text(encoding='utf-8')
    start = js.index("querySelectorAll('.spell[data-probe]')")
    guard = js[start:start + 400]
    assert re.search(r"if\s*\(\s*e\.target\.closest\('details'\)", guard)
    assert guard.index("closest('details')") < guard.index('openPanel')


def _media_blocks(css, header_regex):
    """Rumpf aller @media-Bloecke, deren Kopf zu header_regex passt (Klammer-Zaehlung)."""
    blocks = []
    for m in re.finditer(header_regex + r'\s*\{', css):
        depth, j = 1, m.end()
        while depth and j < len(css):
            depth += {'{': 1, '}': -1}.get(css[j], 0)
            j += 1
        blocks.append(css[m.end():j - 1])
    return blocks


def test_css_artikel_details_rules_desktop_compact_and_print():
    css = css_bundle()
    screen = _strip_print_blocks(css)
    assert re.search(r'\.spell\s+\.artikel-details\s*\{[^}]*grid-column\s*:\s*1\s*/\s*-1', screen)
    compact = ''.join(_media_blocks(css, r'@media\s+screen\s+and\s+\(max-width:\s*1070px\)'))
    assert re.search(r'\.artikel-details[^{}]*\{[^}]*flex\s*:\s*1\s+1\s+100%', compact)
    # table cells must not inherit the panel's overflow-wrap:anywhere (columns collapsed to 1 char at 400 px)
    assert re.search(r'\.artikel-body\s+td\s*\{[^}]*overflow-wrap\s*:\s*normal', screen)
    prints = ''.join(_media_blocks(css, r'@media\s+print'))
    assert re.search(r'\.artikel-panel\s*\{[^}]*background\s*:\s*transparent', prints)
    assert re.search(r'\.artikel-details\[open\]\s*\)\s*\{[^}]*break-inside\s*:\s*auto', prints)
    assert re.search(r'\.artikel-details:not\(\[open\]\)\s*\{[^}]*display\s*:\s*none', prints)


def _css_rules(css):
    """[(Selektor, Deklarationen)] aller flachen Regeln im CSS-Text (ohne Kommentare, Selektorlisten aufgespalten, Whitespace normalisiert)."""
    rules = []
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', re.sub(r'/\*.*?\*/', '', css, flags=re.S)):
        for sel in m.group(1).split(','):
            rules.append((' '.join(sel.split()), m.group(2)))
    return rules


PRINT_SPELL_SELECTORS = (
    '.spell .name .nlink', '.spell .name .nlink::after', '.spell .name .haus', '.spell .zfw-num',
    '.spell .zd', '.spell .kosten', '.spell .wirkung', '.spell .submeta',
    # Browser-Messung Sprint 019: Kopfzeile (Inline-color) 1,95:1, Modifikations-Details 4,28:1 im Druck
    '.spell.spell-head', '.spell.spell-head *', '.mods-details summary.mods-toggle', '.mods-details .mods-list',
)


def test_css_print_spell_list_colors_are_paper_ink():
    # D-046: ohne Druckregel fielen die hellen Bildschirmfarben (Kontrast ~1,1:1 auf Papier) durch; .spell .name .nlink
    # hat eine eigene color-Regel, das !important auf .spell .name vererbt sich nicht.
    prints = ''.join(_media_blocks(css_bundle(), r'@media\s+print'))
    rules = _css_rules(prints)
    missing = [
        sel for sel in PRINT_SPELL_SELECTORS
        if not any(
            s == sel and re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', decl)
            for s, decl in rules
        )
    ]
    assert not missing, f'ohne color:var(--paper-ink) !important im Druck-Block: {missing}'


def test_css_print_spell_name_link_arrow_is_fully_opaque():
    prints = ''.join(_media_blocks(css_bundle(), r'@media\s+print'))
    decls = [d for s, d in _css_rules(prints) if s == '.spell .name .nlink::after']
    assert any(re.search(r'opacity\s*:\s*1\b', d) for d in decls)


def test_css_print_sf_and_ritual_name_link_is_paper_ink_and_arrow_fully_opaque():
    # D-050/D-051: `.sf-list li .sf-name a` hat eine eigene Bildschirm-color (var(--ink), 1,07:1 auf Papier); das
    # !important auf .sf-name vererbt sich nicht auf den Link. Der Pfeil (::after, --accent-cold, opacity .6) ebenso.
    prints = ''.join(_media_blocks(css_bundle(), r'@media\s+print'))
    rules = _css_rules(prints)
    link = _decls(rules, '.sf-list li .sf-name a')
    assert any(re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', d) for d in link), link
    arrow = _decls(rules, '.sf-list li .sf-name a::after')
    assert any(re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', d) for d in arrow), arrow
    assert any(re.search(r'opacity\s*:\s*1\s*!important', d) for d in arrow), arrow


def test_css_print_name_link_arrow_is_bound_with_nbsp():
    # D-053 Ruling R2 (Sprint 026 T2-Nachtrag): der Pfeil (::after, " ↗") stand bei 703 px bei 5 von 25
    # Zaubernamen allein in der Folgezeile. Geschuetztes Leerzeichen bindet ihn an den Namen, nur im Druckblock
    # (base.css:400/637 setzen " ↗" ausserhalb jeder Media Query, gelten also weiter fuer den Bildschirm).
    rules = _print_rules()
    for sel in ('.spell .name .nlink::after', '.sf-list li .sf-name a::after'):
        decls = _decls(rules, sel)
        # CSS-Escape fuer das geschuetzte Leerzeichen steht als literale Zeichenfolge \00a0 im Quelltext
        # (der Browser interpretiert sie erst beim Rendern zu U+00A0); direkt vor dem Pfeilzeichen.
        assert any(re.search(r'content\s*:\s*"\\00a0\u2197"', d) for d in decls), (sel, decls)


def test_css_screen_name_link_arrow_keeps_plain_space():
    # Regressionswaechter: der Bildschirm darf sich durch die Pfeil-Bindung nicht aendern.
    screen = _css_rules(_strip_print_blocks(css_bundle()))
    for sel in ('.spell .name .nlink::after', '.sf-list li .sf-name a::after'):
        decls = _decls(screen, sel)
        assert any(re.search(r'content\s*:\s*" ↗"', d) for d in decls), (sel, decls)
        assert not any(' ' in d for d in decls), (sel, decls)


# Zauber-Tab im Druck (D-052, Sprint 025 T2-Messung im Browser, Papier #ece4d0): 20 Selektor-Gruppen lagen mit 1,04 bis 4,28 : 1
# unter 4,5 : 1. Ursache: ein Kind mit eigener Bildschirm-color erbt das !important am Eltern (.card, .card-title, .sf-name,
# .sec-head h2) nicht, und Inline-Styles (zauber.j2:7/95/124/189/210) schlaegt nur !important mit passendem Selektor.
# Die Ueberschriften/Meta-Zeilen mit Inline-color sind auf #tab-zauber begrenzt (gleiche Klassen stehen in anderen, nicht
# vermessenen Tabs).
PRINT_ZAUBERTAB_SELECTORS = (
    # Zauberspeicher (T2: .slot-zauber 1,04 / .slot-num 1,54 / .speicher-title, -summary 1,90 / .slot-asp, p.meta 4,16)
    '.slot-zauber', '.slot-num', '.slot-asp', '.speicher-title', '.speicher-summary', '#tab-zauber .card p.meta',
    # vorsorglich: im Ist-Render sind alle 3 Slots leer (base.css:503-505,523)
    '.slot-mods-row', '.slot-mods-label', '.slot-erneuerung-label', '.speicher-slot.leer .slot-header',
    # Spontane Modifikationen (T2: .mod-name 1,07 / .mod-zfp 1,74 / Kopf, .mod-probe, Link 1,95 / .mod-zd 4,28)
    '.mod-row .mod-name', '.mod-row .mod-zfp', '.mod-row .mod-probe', '.mod-row .mod-zd', '.mod-row.header > span',
    '.mod-footer-link',
    # Legende (1,74 / 1,95)
    '.legend-row', '.legend-row span', '.legend-row span b',
    # Kartenkopf, Badges, Ueberschriften mit Inline-color (1,95 / 4,28 / 4,12 / 4,19 / 1,74)
    # Sprint 026 T2 (Ruling R4): Praefix entfernt, dieselbe Klasse wird jetzt auch in profil/inventar/kampf gebraucht
    '.card-title .meta', '.sf-list li .sf-name .meta', '.vol-badge', '#tab-zauber .sec-head h2 span',
    '#tab-zauber .card > h4',
)
PRINT_SLOT_BUTTON_SELECTORS = (
    '.slot-befuellen-toggle', '.slot-befuellen-area', '.slot-befuellen-form', '.slot-entleeren-btn', '.slot-ausloesen-btn',
)


def _print_rules():
    return _css_rules(''.join(_media_blocks(css_bundle(), r'@media\s+print')))


def test_css_print_zauber_tab_colors_are_paper_ink():
    rules = _print_rules()
    missing = [
        sel for sel in PRINT_ZAUBERTAB_SELECTORS
        if not any(
            s == sel and re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', decl)
            for s, decl in rules
        )
    ]
    assert not missing, f'ohne color:var(--paper-ink) !important im Druck-Block: {missing}'


def test_css_print_zauber_tab_non_text_rules():
    # T2: .vol-badge (Rahmen 1,08:1, Grund 1,04:1), .speicher-box (Rahmen 1,08:1, Grund 1,03:1) und der gepunktete Unterstrich
    # der Namenslinks (rgba(95,195,228,.25) = 1,13:1) sind auf Papier praktisch unsichtbar.
    rules = _print_rules()
    for sel in ('.vol-badge', '.speicher-box'):
        decls = ' '.join(_decls(rules, sel))
        assert re.search(r'(?<![-\w])background\s*:\s*transparent\s*!important', decls), (sel, decls)
        assert re.search(r'border(?:-color)?\s*:[^;]*var\(--paper-rule\)\s*!important', decls), (sel, decls)
    for sel in ('.spell .name .nlink', '.sf-list li .sf-name a'):
        decls = ' '.join(_decls(rules, sel))
        assert re.search(r'border-bottom-color\s*:\s*var\(--paper-ink\)\s*!important', decls), (sel, decls)


def test_css_print_hides_zauberspeicher_slot_buttons():
    # T2 (Ruling R9): "+ Befuellen" stand im Druck sichtbar (1,47:1); Entleeren/Ausloesen/Formular sind reine Bedienelemente.
    rules = _print_rules()
    missing = [
        sel for sel in PRINT_SLOT_BUTTON_SELECTORS
        if not any(s == sel and re.search(r'display\s*:\s*none\s*!important', decl) for s, decl in rules)
    ]
    assert not missing, f'im Druck nicht ausgeblendet: {missing}'


# Uebrige 7 Tabs im Druck (D-053, Sprint 026 T2-Messung im Browser, Papier #ece4d0): 37 Selektor-Gruppen / 495 Elemente
# lagen mit 1,07 bis 4,28 : 1 unter 4,5 : 1 — dieselbe Falle wie D-052 (Kind mit eigener Bildschirm-color erbt das
# !important am Vorfahren nicht; Inline-Styles in inventar.j2:43/90 und profil.j2:84-93 schlaegt nur !important mit
# passendem Selektor). .talent-row.zero (eigener Farbwert statt paper-ink) und sprachen.css (eigene Datei/eigener
# Druckblock) haben eigene Tests unten.
PRINT_SEVEN_TABS_PAPER_INK_SELECTORS = (
    # Inventar (T1: 10 Gruppen)
    '.equip-stat .k', '.equip-stat .v', '.inv-coin-label', '.inv-coin-val', '.inv-coin-total',
    '.inv-weight-note', '.inv-reise-note', '.equip-stat + p', '.inv-list li > span',
    # Profil (T1: 9 Gruppen)
    '.aussehen-row dt', '.aussehen-row dd', '#tab-profil .sessions-table', '#tab-profil .sessions-table *', '.feed li small',
    # Kampf: R6 (vorsorglich, ungemessen)
    '.weapon-card + div', '.weapon-card + div *',
    # Talente (T1: 3 Gruppen; .talent-row.zero siehe test_css_print_talente_zero_meets_contrast_threshold)
    '.talent-grp h4 .skt',
    # Steigern (T1: 10 Gruppen; .sg-name > span faengt seit der Gesamt-Review-Fixwelle auch .sg-cap-warn mit,
    # siehe test_css_print_cap_warn_family_meets_contrast_threshold)
    '.sg-section-head', '.sg-ap-label', '.sg-ap-val', '.sg-val', '.sg-cost', '.sg-select-hint',
    '.sg-name > span', '.steiger-table th',
)


def test_css_print_seven_tabs_colors_are_paper_ink():
    rules = _print_rules()
    missing = [
        sel for sel in PRINT_SEVEN_TABS_PAPER_INK_SELECTORS
        if not any(
            s == sel and re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', decl)
            for s, decl in rules
        )
    ]
    assert not missing, f'ohne color:var(--paper-ink) !important im Druck-Block: {missing}'


def test_sessions_table_has_class_in_markup(live_html):
    """Verifies D-057: Sessions-Tabelle hat .sessions-table Klasse fuer Selector-Scoping."""
    assert 'class="sessions-table"' in live_html, 'Sessions-Tabelle in profil.j2 muss .sessions-table Klasse haben'
    # Stelle sicher, dass die alte Tag-basierte Selector-Regel nicht mehr im CSS vorkommt
    rules = _print_rules()
    old_selectors = ['#tab-profil table', '#tab-profil table *']
    # Finde den alten Selector im CSS
    old_found = [s for s in old_selectors if any(sel == s for sel, _ in rules)]
    assert not old_found, f'alte Tag-Selektoren sollten nicht mehr im CSS sein: {old_found}'


def _relative_luminance(rgb):
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def _contrast_ratio(rgb1, rgb2):
    l1, l2 = _relative_luminance(rgb1), _relative_luminance(rgb2)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _hex_to_rgb(hexstr):
    hexstr = hexstr.lstrip('#')
    return tuple(int(hexstr[i:i + 2], 16) for i in (0, 2, 4))


PAPER_RGB = (0xec, 0xe4, 0xd0)


def test_css_print_talente_zero_meets_contrast_threshold():
    # T1 mass den alten Fix (#7a6a4a) bei 4,156:1 — noch unter 4,5:1. Prueft die Wirkung (Kontrast), nicht die
    # Schreibweise: welcher Hex-Wert es ist, ist egal, solange er den Zielwert erreicht.
    rules = _print_rules()
    decls = _decls(rules, '.talent-row.zero .t-name') + _decls(rules, '.talent-row.zero .t-zfw')
    assert decls, 'keine Druck-Regel fuer .talent-row.zero .t-name/.t-zfw gefunden'
    for decl in decls:
        m = re.search(r'(?<![-\w])color\s*:\s*#([0-9a-fA-F]{6})\s*!important', decl)
        assert m, decl
        ratio = _contrast_ratio(_hex_to_rgb(m.group(1)), PAPER_RGB)
        assert ratio >= 4.5, (m.group(1), ratio)


def test_css_print_strips_steigern_erfahrungs_select_chrome():
    # Ruling R7 (revidiert, Sprint 026 T2-Nachtrag 2): <select class="sg-erf"> druckte als voller schwarzer Kasten
    # (Screenshot-Fund) — Ursache war die Bildschirm-Optik (Hintergrund/Rahmen/native Pfeilgrafik), nicht der
    # <select> selbst; ausgeblendet verlor er die sonst nirgends im Druck stehende Erfahrungsstufe ersatzlos.
    # Jetzt bleibt der gewaehlte <option>-Text sichtbar, der Select verliert nur seinen Bedienelement-Look.
    rules = _print_rules()
    decls = _decls(rules, '.sg-erf')
    assert decls, '.sg-erf hat keine Druck-Regel'
    combined = ' '.join(decls)
    assert re.search(r'(?<![-\w])appearance\s*:\s*none\b', combined), combined
    assert re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', combined), combined
    assert re.search(r'background\s*:\s*transparent\s*!important', combined), combined
    assert re.search(r'border\s*:\s*none\s*!important', combined), combined
    assert not re.search(r'display\s*:\s*none', combined), combined


# Bekannte CSS-Variablen -> Hex (aus base.css :root), um die Druck-Farbe eines Selektors aufzuloesen, ohne einen
# Browser zu brauchen. Nur die Werte, die in Druckregeln tatsaechlich als color vorkommen.
CSS_VAR_HEX = {
    'ink': 'e8dcc3', 'ink-mute': '9aa6b4', 'ink-dim': '5f6b7a', 'ink-probe': 'b8c4d0',
    'accent-cold': '5fc3e4', 'accent-gold': 'd4a84b',
    'paper': 'ece4d0', 'paper-ink': '1a1208', 'paper-rule': '8a7758',
}


def _resolve_color_rgb(decl):
    """Farbwert eines color:-Deklarationsteils als RGB-Tupel — hex-Literal oder bekannte var(--...)."""
    m = re.search(r'(?<![-\w])color\s*:\s*(#[0-9a-fA-F]{6}|var\(--([\w-]+)\))', decl)
    assert m, decl
    if m.group(1).startswith('#'):
        return _hex_to_rgb(m.group(1))
    return _hex_to_rgb(CSS_VAR_HEX[m.group(2)])


def test_css_print_steigern_erfahrungs_select_meets_contrast_threshold():
    # Wirkungstest statt Farbwert-Vergleich: egal welche Farbe/Variable im Druck-Block steht, sie muss auf Papier
    # >= 4,5:1 erreichen (etablierter Wert waere var(--paper-ink) = 14,62:1, siehe PAPER_RGB).
    rules = _print_rules()
    decls = _decls(rules, '.sg-erf')
    assert decls, '.sg-erf hat keine Druck-Regel'
    ratio = _contrast_ratio(_resolve_color_rgb(' '.join(decls)), PAPER_RGB)
    assert ratio >= 4.5, ratio


def test_css_print_steigern_erfahrungs_select_chrome_wins_the_cascade():
    # Fix-Runde 1 (Review-Fund): padding/border-radius/max-width standen ohne !important im Druckblock. Die
    # Bildschirm-Regel tabs.css:523 (gleiche Spezifitaet .sg-erf, aber SPAETER im Quelltext) gewann darum auch im
    # Druck (Reviewer-Beleg per getComputedStyle: alle drei Werte kamen aus Zeile 523). Bei gleicher Spezifitaet
    # entscheidet nicht die Media-Query-Zugehoerigkeit, sondern Reihenfolge + Wichtigkeit — !important ist die
    # einzige verlaessliche Lösung, solange die Bildschirmregel spaeter im Bundle steht.
    rules = _print_rules()
    decls = ' '.join(_decls(rules, '.sg-erf'))
    for prop in ('padding', 'border-radius', 'max-width'):
        assert re.search(rf'(?<![-\w]){prop}\s*:[^;]*!important', decls), (prop, decls)


PRINT_SPRACHEN_SELECTORS = ('.lang-table th', '.l-name', '.l-taw', '.l-kompl', '.lang-section-head')


def test_css_print_sprachen_colors_are_paper_ink():
    # sprachen.css hatte noch keinen eigenen @media print-Block; T1 mass 6 Gruppen zwischen 1,07 und 1,95:1.
    rules = _print_rules()
    missing = [
        sel for sel in PRINT_SPRACHEN_SELECTORS
        if not any(
            s == sel and re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', decl)
            for s, decl in rules
        )
    ]
    assert not missing, f'ohne color:var(--paper-ink) !important im Druck-Block: {missing}'
    # der neue Block muss tatsaechlich in sprachen.css liegen, nicht in tabs.css
    sprachen_css = (STATIC_DIR / 'sprachen.css').read_text(encoding='utf-8')
    assert re.search(r'@media\s+print\s*\{[^@]*\.lang-table\s+th', sprachen_css)


# "Nicht ausgeloest"-Familie (Gesamt-Review-Fixwelle, war I1): drei Badges/Platzhalter, die sich nur in
# Datenzustaenden zeigen, die illaen-baernhold heute nicht hat (Komplexitaetsgrenze erreicht bzw. leeres Register).
# R6 (kampf.j2, vorsorglich) galt bisher nur fuer EINEN solchen Fall — jetzt konsequent fuer alle drei. Gemessen per
# DOM-Simulation (siehe Bericht): .lang-cap-warn/.sg-cap-warn 1,744:1 (eigene accent-gold-Bildschirm-color),
# .register-leer/.register-empty 4,282:1 (ink-dim). Rahmen/Hintergrund bleiben bewusst unangetastet (Badge-Optik).
PRINT_CAP_WARN_FAMILY = ('.lang-cap-warn', '.register-leer', '.register-empty')


def test_css_print_cap_warn_family_meets_contrast_threshold():
    # Wirkungstest wie bei .sg-erf: die im Druck deklarierte Farbe muss auf Papier >= 4,5:1 erreichen, egal welche
    # Variable dort steht. (Browser-Messung der Fixwelle: .sg-cap-warn/.register-* 14,617:1; .lang-cap-warn 13,496:1,
    # weil das Badge seinen halbtransparenten Gold-Grund behaelt — dieser Grund wird hier nicht mitgerechnet, der
    # Test prueft die Deklaration gegen Papier. Ohne gedruckten Hintergrund liegt der echte Wert hoeher, s. D-056.)
    rules = _print_rules()
    for sel in PRINT_CAP_WARN_FAMILY + ('.sg-name > span',):
        decls = _decls(rules, sel)
        assert decls, f'{sel} hat keine Druck-Regel'
        joined = ' '.join(decls)
        assert re.search(r'(?<![-\w])color\s*:[^;]*!important', joined), (sel, joined)
        ratio = _contrast_ratio(_resolve_color_rgb(joined), PAPER_RGB)
        assert ratio >= 4.5, (sel, ratio)
    # .sg-cap-warn haengt nicht an einem eigenen Selektor, sondern wird von .sg-name > span mitgefangen, seit die
    # :not(.sg-cap-warn)-Ausnahme entfernt wurde (Wirkungstest statt Literalvergleich; Kommentare koennen die
    # Zeichenfolge weiterhin erwaehnen, daher Pruefung ueber die geparsten Selektoren, nicht den Rohtext).
    assert not any(s == '.sg-name > span:not(.sg-cap-warn)' for s, _ in rules)
    assert any(s == '.sg-name > span' for s, _ in rules)


def test_css_print_cap_warn_family_lives_at_its_origin_file():
    # Fix an der Datei der Ursprungsregel: .lang-cap-warn in sprachen.css, .register-leer/.register-empty in
    # chronik.css (nicht in tabs.css gesammelt). Kommentare werden vorher entfernt — sie duerfen die Klasse
    # erwaehnen (z. B. tabs.css' Verweis "dieselbe Klasse wie .lang-cap-warn/sprachen.css"), ohne die Pruefung zu
    # verfaelschen.
    def print_selectors_of(filename):
        css = (STATIC_DIR / filename).read_text(encoding='utf-8')
        return {s for s, _ in _css_rules(''.join(_media_blocks(css, r'@media\s+print')))}

    assert '.lang-cap-warn' in print_selectors_of('sprachen.css')
    assert '.lang-cap-warn' not in print_selectors_of('tabs.css')
    chronik_selectors = print_selectors_of('chronik.css')
    assert '.register-leer' in chronik_selectors and '.register-empty' in chronik_selectors


# Chronik "Kompiliert"-Ansicht (D-053, Sprint 026 T2, Fix-Runde 1 — Review-Fund): T1 mass fuer #tab-chronik 0
# Verstoesse, aber nur die Default-Ansicht "Roh" (chronik.css: .chronik-view{display:none}, nur die aktive Ansicht
# ist sichtbar; das Journal-Partial liegt in "Kompiliert"). Eigene Messung (Playwright, Print-Emulation, 718px,
# Ansicht per .chronik-switch-btn[data-view="kompiliert"].click() umgeschaltet — Bildschirm-Interaktion, kein
# Schreibzugriff im Vault): 3 Gruppen zwischen 1,95 und 4,28:1, alle ZUSTANDSABHAENGIG (nur in "Kompiliert" sichtbar).
PRINT_JOURNAL_SELECTORS = ('.journal-section h4', '.journal-section summary', '.journal-readonly')


def test_css_print_journal_kompiliert_view_colors_are_paper_ink():
    rules = _print_rules()
    missing = [
        sel for sel in PRINT_JOURNAL_SELECTORS
        if not any(
            s == sel and re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)\s*!important', decl)
            for s, decl in rules
        )
    ]
    assert not missing, f'ohne color:var(--paper-ink) !important im Druck-Block: {missing}'
    # der neue Block muss tatsaechlich in journal.css liegen (Ursprungsregel-Datei), nicht in tabs.css/chronik.css
    journal_css = (STATIC_DIR / 'journal.css').read_text(encoding='utf-8')
    assert re.search(r'@media\s+print\s*\{[^@]*\.journal-readonly', journal_css)


def test_css_print_journal_verlauf_textarea_is_hidden_and_replaced_by_a_readable_mirror():
    # D-055 v2 (Final-Review Important): v1 kept the <textarea> itself visible in print (Fix-Runde 2 below fixed
    # its screen-look colors), but even a correctly-colored <textarea> only prints its scrolled viewport — v1's
    # scrollHeight-resize approach still lost ~17% of the text at normal desktop window widths (scrollHeight was
    # measured at the wider SCREEN layout, not the narrower real print width). chronik.js now hides the textarea
    # entirely in print and shows a plain flowed <pre class="journal-verlauf-print"> snapshot of the live value
    # instead, so the browser's own print layout wraps it correctly. The mirror must stay readable without
    # relying on a printed background (Fix-Runde 2 lesson still applies: Chromium doesn't print backgrounds
    # without print-color-adjust:exact) — it sits inside .card, which tabs.css already resets to a transparent
    # background + paper-ink text color in print, so the mirror only needs its own text/border colors.
    rules = _print_rules()
    hidden = ' '.join(_decls(rules, '.journal-verlauf'))
    assert re.search(r'display\s*:\s*none\s*!important', hidden), hidden
    mirror = ' '.join(_decls(rules, '.journal-verlauf-print'))
    assert mirror, '.journal-verlauf-print hat keine Druck-Regel'
    assert re.search(r'display\s*:\s*block\s*!important', mirror), mirror
    assert re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)', mirror), mirror
    assert re.search(r'border(?:-color)?\s*:[^;]*var\(--paper-rule\)', mirror), mirror
    assert re.search(r'white-space\s*:\s*pre-wrap', mirror), mirror


def test_css_print_hides_steigern_cart_bar():
    # Fix-Runde 3 (Re-Review, PDF-Pfad): .sg-cart (position:sticky, tabs.css:529) klebte bei der PDF-Paginierung auf
    # Seite 8 ueber einer Zeile der Steigerungstabelle (bestaetigt per page.pdf() + pdftoppm-Rasterung: "CH ·
    # Charisma" war ueberdeckt). Reines Bedienelement (Session-Zustand des Warenkorbs, keine Heldenbogen-Info) —
    # wie .inv-stepper/.inv-add-form/.journal-actions/.spell-toolbar ausgeblendet statt kontrastgefixt.
    rules = _print_rules()
    assert any(s == '.sg-cart' and re.search(r'display\s*:\s*none\s*!important', d) for s, d in rules)


def test_css_print_vital_input_is_not_hidden():
    # D-054: .vital-input stand mit .vital-btn/#save-indicator/.vitals-sticky/.wunden-counter/#zustand-chips/
    # .zustand-legend in einer gemeinsamen Ausblend-Regel. Anders als diese reinen Bedienelemente traegt das
    # Eingabefeld den aktuellen LeP/AsP/AuP-Wert selbst (kein anderer Knoten zeigt ihn im Druck) — es bleibt sichtbar.
    rules = _print_rules()
    assert not any(
        s == '.vital-input' and re.search(r'display\s*:\s*none\s*!important', d) for s, d in rules
    ), 'vital-input darf im Druck nicht ausgeblendet sein'


def test_css_print_vital_stepper_has_no_display_none():
    # Die Stepper-Ausblendung verdeckte auch ihre nicht ausblendungspflichtigen Kinder (Input, .vital-sep,
    # .vital-max) komplett. .vital-btn (+/-) bleibt ueber seine eigene Regel (siehe oben) ausgeblendet.
    rules = _print_rules()
    assert not any(
        s == '.vital-stepper' and re.search(r'display\s*:\s*none\s*!important', d) for s, d in rules
    ), '.vital-stepper darf im Druck keine display:none-Regel mehr haben'


def test_css_print_vital_after_pseudo_element_is_gone():
    # .vital::after konnte nie funktionieren: attr() liest kein data-current eines Nachfahren, und das
    # Attribut wird im ganzen Code nirgends gesetzt (nur data-max existiert, auf .vital-stepper). Toter Code,
    # ersetzt durch das jetzt sichtbare .vital-input + .vital-max.
    rules = _print_rules()
    assert not any(s == '.vital::after' for s, _ in rules), 'vital::after haette entfernt werden sollen'
    assert '.vital::after' not in css_bundle(), 'vital::after darf auch ausserhalb des Druckblocks nicht mehr vorkommen'


def test_css_print_vital_value_selectors_use_paper_ink():
    # .vital-max/.vital-sep hatten am Bildschirm nur opacity:0.7 (keine eigene color) und waren im Druck bisher
    # immer im ausgeblendeten Stepper versteckt — nie gegen Papier geprueft. .vital-input braucht dieselbe Farbe,
    # jetzt wo es im Druck sichtbar bleibt.
    rules = _print_rules()
    for sel in ('.vital-max', '.vital-sep', '.vital-input'):
        decls = ' '.join(_decls(rules, sel))
        assert re.search(r'(?<![-\w])color\s*:\s*var\(--paper-ink\)', decls), (sel, decls)


def test_css_print_vital_max_and_sep_reset_screen_opacity():
    # Fix-Runde 1 (Review): tabs.css:243 setzt ".vital-sep, .vital-max { opacity: 0.7; }" unscoped (gilt auch im
    # Druck). Die reine color:var(--paper-ink)-Regel von oben ueberschreibt das nicht — erst seit diesem Fix ist
    # der Stepper im Druck ueberhaupt sichtbar, die verduennte Opazitaet greift also zum ersten Mal wirklich.
    # Gleiches Muster wie .spell .name .nlink::after / .sf-list li .sf-name a::after (tabs.css:91/95).
    rules = _print_rules()
    for sel in ('.vital-max', '.vital-sep'):
        decls = ' '.join(_decls(rules, sel))
        assert re.search(r'opacity\s*:\s*1\s*!important', decls), (sel, decls)


def test_css_no_other_sticky_or_fixed_element_leaks_into_print():
    # Vollstaendigkeits-Check (Re-Review-Auftrag Punkt 2): jedes position:sticky/fixed im Bildschirm-CSS muss im
    # Druck entweder auf position:static/relative zurueckgesetzt, per display:none ausgeblendet, oder Nachfahre
    # eines so behandelten Vorfahren sein — sonst wiederholt sich der .sg-cart-Fund (Screen-Positionierung bleibt
    # im Druck aktiv). Bekannte, bereits abgedeckte Faelle: body::before/.sparkles (tabs.css frueher Block),
    # .eig-leiste (base.css:375), #footer-bar + .print-btn darin (per screen-only-Klasse im Template — der ganze
    # Teilbaum wird im Druck nicht gerendert, siehe PRINT_BTN_ANCESTOR_HIDDEN unten), #save-indicator/.vitals-sticky
    # (tabs.css), .dice-panel (tabs.css), .tab-bar (tabs.css), .sg-cart (siehe oben).
    #
    # Gesamt-Review-Fixwelle (M1): zwei Luecken gehaertet — (a) has_descendant_static_override durchsuchte zuvor
    # ALLE Regeln (auch Bildschirm-CSS ohne Druckkontext), (b) eine Druckregel position:static OHNE !important galt
    # als Neutralisierung, obwohl Fix-Runde 1 an .sg-erf bewiesen hat, dass eine spaetere Bildschirm-Regel mit
    # gleicher Spezifitaet dann gewinnt. Beide Zweige jetzt auf Druckregeln MIT !important beschraenkt.
    #
    # Bewusst verbliebene Heuristik (Re-Review-Empfehlung: dokumentieren statt Spezifitaets-Parser bauen): die
    # Nachfahren-Pruefung vergleicht Selektor-Suffixe, nicht echte Spezifitaet. Eine Druck-!important-static-Regel
    # in einem Ahnenkontext, den es gar nicht gibt (z. B. ".gibtsnicht .zz"), zaehlt darum weiter als Nachweis.
    # Ausloeser waere eine wirkungslose !important-Druckregel — in diesem Projekt kein realer Fall.
    full_css = css_bundle()
    screen = _strip_print_blocks(full_css)
    sticky_fixed_selectors = set()
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', re.sub(r'/\*.*?\*/', '', screen, flags=re.S)):
        if re.search(r'(?<![-\w])position\s*:\s*(?:sticky|fixed)\b', m.group(2)):
            for sel in m.group(1).split(','):
                sticky_fixed_selectors.add(' '.join(sel.split()))
    prints = _print_rules()
    dashboard = (TEMPLATES_DIR / 'dashboard.html.j2').read_text(encoding='utf-8')
    # .print-btn: base.css:744 setzt "#footer-bar .print-btn{ position:static; }" unbedingt (nicht nur im Druck,
    # kein !important) — reicht am Bildschirm, weil es dort die einzige Regel mit dieser Spezifitaet ist. Im Druck
    # zaehlt das nach der obigen Haertung nicht mehr als Nachweis, ist aber ohnehin wirkungslos: jede .print-btn-
    # Instanz liegt ausschliesslich in #footer-bar (grep templates/**/*.j2 bestaetigt), das per screen-only komplett
    # display:none ist — ein nicht gerenderter Teilbaum kann nicht ueberlappen, unabhaengig von seiner eigenen
    # position. Explizite, begruendete Ausnahme statt eines Kaskaden-Nachweises, den es hier nicht gibt.
    PRINT_BTN_ANCESTOR_HIDDEN = {'.print-btn'}

    def has_descendant_static_override(sel):
        # nur DRUCK-Regeln (nicht das ganze Bundle) UND nur mit !important zaehlen als Nachweis — sonst gewinnt
        # ggf. eine spaetere Bildschirm-Regel gleicher Spezifitaet (exakt der .sg-erf-Fund aus Fix-Runde 1).
        for s, d in prints:
            if s != sel and re.search(rf'(?:^|[\s>]){re.escape(sel)}$', s) and re.search(r'(?<![-\w])position\s*:\s*(?:static|relative)\b[^;]*!important', d):
                return True
        return False

    def neutralised(sel):
        if any(s == sel and re.search(r'display\s*:\s*none\s*!important', d) for s, d in prints):
            return True
        if any(s == sel and re.search(r'(?<![-\w])position\s*:\s*(?:static|relative)\b[^;]*!important', d) for s, d in prints):
            return True
        # das Template-Element traegt "screen-only" (per .screen-only{display:none!important} in base.css abgedeckt)
        id_match = re.fullmatch(r'#([\w-]+)', sel)
        if id_match and re.search(rf'id=["\']{id_match.group(1)}["\'][^>]*class=["\'][^"\']*screen-only', dashboard):
            return True
        if has_descendant_static_override(sel):
            return True
        if sel in PRINT_BTN_ANCESTOR_HIDDEN:
            return True
        return False

    unneutralised = sorted(sel for sel in sticky_fixed_selectors if not neutralised(sel))
    assert not unneutralised, unneutralised


def test_css_seven_tabs_print_fix_leaves_screen_css_untouched():
    # Regressionswaechter: die Bildschirmdarstellung darf sich durch D-053 nicht aendern; alle neuen Regeln stehen
    # im Druckblock (Sprint-025-Vorbild: test_css_zauber_tab_print_fix_leaves_screen_css_untouched).
    screen_rules = _css_rules(_strip_print_blocks(css_bundle()))
    new_selectors = set(PRINT_SEVEN_TABS_PAPER_INK_SELECTORS) | set(PRINT_SPRACHEN_SELECTORS) | set(PRINT_JOURNAL_SELECTORS) | set(PRINT_CAP_WARN_FAMILY) | {
        '.talent-row.zero .t-name', '.talent-row.zero .t-zfw', '.sg-erf', '.card-title .meta', '.journal-verlauf',
        '.sg-cart',
    }
    leaked = [(s, d) for s, d in screen_rules if s in new_selectors and re.search(r'paper-(?:ink|rule)|!important|display:\s*none', d)]
    assert not leaked, leaked


def _print_spell_grid_decl():
    decls = [d for d in _decls(_print_rules(), '.spell') if 'grid-template-columns' in d]
    assert len(decls) == 1, decls
    return decls[0]


def test_css_print_spell_grid_has_six_columns_and_cannot_overflow():
    # T2: das Bildschirm-Grid loest im Druck zu 858 px auf (Minima 160+240+38+80+90+200 + 5 Gaps) gegen 733 px Innenbreite
    # (Emulation) bzw. ca. 657 px auf echtem A4 (186 mm): der Ueberlauf kam aus der letzten Spalte (Wirkung, right 881 > 779).
    decl = _print_spell_grid_decl()
    cols = _top_level_tokens(re.search(r'grid-template-columns\s*:\s*([^;]+?)\s*(?:!important\s*)?(?:;|$)', decl).group(1))
    assert len(cols) == 6, cols
    fixed = 0.0
    for col in cols:
        m = re.fullmatch(r'minmax\(\s*([^,\s]+)\s*,\s*([^)]+?)\s*\)', col)
        if m:
            # kein px-Minimum: nur 0 als Minimum ist "durch Konstruktion" nie breiter als der Container
            assert m.group(1) == '0', f'minmax mit Minimum {m.group(1)}: {col}'
        elif col.endswith('px'):
            fixed += _px_list(col)[0]
        else:
            raise AssertionError(f'unerwartete Spalte {col}: nur minmax(0,Xfr) oder feste px-Spalte erlaubt')
    gap = re.search(r'(?<![-\w])gap\s*:\s*([^;]+)', decl).group(1).split()
    column_gap = _px_list(gap[-1])[0]
    assert fixed <= 120, fixed
    assert fixed + 5 * column_gap <= 120, (fixed, column_gap)


def test_css_print_spell_cells_may_shrink_and_probe_wraps():
    # base.css:406 setzt .spell .probe auf white-space:nowrap (sprengt die Probe-Spalte); Grid-Items brauchen min-width:0
    rules = _print_rules()
    assert any(re.search(r'(?<![-\w])min-width\s*:\s*0\b', d) for d in _decls(rules, '.spell > *')), _decls(rules, '.spell > *')
    assert any(re.search(r'overflow-wrap\s*:\s*anywhere', d) for d in _decls(rules, '.spell > *'))
    assert any(re.search(r'white-space\s*:\s*normal', d) for d in _decls(rules, '.spell .probe'))


def test_css_print_spell_probe_column_fr_grows_without_changing_row_width():
    # D-058 Sub-Fix A: Probe brach mit 1,4 fr in allen 25 Zeilen der Live-Vault zweizeilig um (Browser-Messung
    # @703 px: Spalte 116,8 px gegen laengsten realen Probe-Text "MU 12 / KL 14 / KO 13" = 137,6 px ungewrappt).
    # Probe-Anteil angehoben, Kosten/Wirkung geben ab; die fr-Summe der 4 variablen Spalten bleibt bei 6,4 —
    # die Gesamtbreite haengt nur von der verfuegbaren Restbreite ab, nicht vom fr-Verhaeltnis (minmax(0,Xfr)
    # fuellt per CSS-Grid-Konstruktion immer exakt die Restbreite), daher keine Ueberlaufregression moeglich.
    # Browser-Nachmessung (Sprint-028 T2-Report): scrollWidth @703/718/615 px vor/nach identisch (662/677/574).
    decl = _print_spell_grid_decl()
    cols = _top_level_tokens(re.search(r'grid-template-columns\s*:\s*([^;]+?)\s*(?:!important\s*)?(?:;|$)', decl).group(1))
    fr_values = []
    for col in cols:
        m = re.fullmatch(r'minmax\(\s*0\s*,\s*([\d.]+)fr\s*\)', col)
        if m:
            fr_values.append(float(m.group(1)))
    assert len(fr_values) == 4, cols
    zauber_fr, probe_fr, kosten_fr, wirkung_fr = fr_values
    assert probe_fr >= 1.9, f'Probe-fr {probe_fr} unter der D-058-Zielbreite (Browser-Messung: 1,9 fr = 158,5 px @703 px)'
    assert probe_fr > 1.4, 'Probe-Anteil muss gegenueber dem Vorzustand (1.4fr) wachsen'
    assert kosten_fr < 1.0, 'Kosten muss Anteil abgeben (Vorzustand 1fr)'
    assert abs((zauber_fr + probe_fr + kosten_fr + wirkung_fr) - 6.4) < 1e-9, fr_values


def test_css_zauber_tab_print_fix_leaves_screen_css_untouched():
    # Regressionswaechter: die Bildschirmdarstellung darf sich durch D-052 nicht aendern; alle neuen Regeln stehen im Druckblock.
    screen_rules = _css_rules(_strip_print_blocks(css_bundle()))
    new_selectors = set(PRINT_ZAUBERTAB_SELECTORS) | set(PRINT_SLOT_BUTTON_SELECTORS) | {
        '.vol-badge', '.speicher-box', '.spell .name .nlink', '.sf-list li .sf-name a', '.spell > *',
    }
    leaked = [(s, d) for s, d in screen_rules if s in new_selectors and re.search(r'paper-(?:ink|rule)|!important', d)]
    assert not leaked, leaked
    spell_grid = [d for s, d in screen_rules if s == '.spell' and 'grid-template-columns' in d]
    assert spell_grid and all('minmax(0' not in d for d in spell_grid), spell_grid
    assert not [d for s, d in screen_rules if s == '.spell .probe' and 'white-space:normal' in d.replace(' ', '')]


# -- D-058 Sub-Fix B: Ritual-/SF-Karten-Grid-Stretch (nur Zauber-Tab-Instanz) ------------

def test_css_grid_align_top_modifier_sets_align_items_start():
    # CSS-Grid-Default align-items:stretch zog die (kuerzere) SF-Karte auf die Hoehe der Rituale-Karte, sobald
    # dort mehrere Artikelvorschauen offen waren (Browser-Messung: 1626,9 px -> 7122,6 px ohne Fix). User-
    # Entscheidung: Modifier-Klasse statt globaler .cols-2-Aenderung (base.css:78-81 bleibt unangetastet).
    rules = _css_rules(_strip_print_blocks(css_bundle()))
    modifier = _decls(rules, '.grid.align-top')
    assert modifier, 'Modifier-Selektor .grid.align-top fehlt'
    assert any(re.search(r'align-items\s*:\s*(?:start|flex-start)\b', d) for d in modifier), modifier
    # .cols-2 selbst bekommt kein align-items -> die 3 anderen Verwendungsstellen (profil/inventar/kampf)
    # behalten den Grid-Default stretch.
    cols2 = _decls(rules, '.cols-2')
    assert cols2 and not any('align-items' in d for d in cols2), cols2


def test_render_align_top_modifier_only_on_zauber_tab_grid(live_html):
    # Nur zauber.j2:91 bekommt den Modifier; profil.j2/inventar.j2/kampf.j2 bleiben bei "grid cols-2" (unveraendert).
    assert live_html.count('class="grid cols-2 align-top"') == 1
    zauber_src = (PARTIALS_DIR / 'zauber.j2').read_text(encoding='utf-8')
    assert '<div class="grid cols-2 align-top"' in zauber_src
    for name in ('profil', 'inventar', 'kampf'):
        src = (PARTIALS_DIR / f'{name}.j2').read_text(encoding='utf-8')
        assert '<div class="grid cols-2">' in src, name
        assert 'align-top' not in src, name


def test_css_has_no_dead_merk_selector():
    # .merk kommt in keinem Template/JS mehr vor (heute .spell .submeta); der Druck-Selektor war tot.
    assert '.merk' not in css_bundle()


def _px_list(value):
    return [float(v) for v in re.findall(r'(-?[\d.]+)px', value)]


def _top_level_tokens(value):
    """Whitespace-Split der grid-template-columns-Werte, ohne minmax(...) aufzubrechen."""
    tokens, depth, cur = [], 0, ''
    for ch in value.strip():
        depth += {'(': 1, ')': -1}.get(ch, 0)
        if ch.isspace() and not depth:
            if cur:
                tokens.append(cur)
            cur = ''
        else:
            cur += ch
    if cur:
        tokens.append(cur)
    return tokens


def _spell_grid_min_width(css):
    """Mindestbreite der Desktop-Zeile (.spell, Bildschirm; nur Print-Bloecke entfernt, die kompakte .spell-Regel setzt kein grid-template-columns):
    Summe der Spaltenminima (feste Spalte = ihr Wert, minmax(a,b) = a) + (Spalten-1) * column-gap + horizontales Padding."""
    screen = _strip_print_blocks(css)
    decl = next(d for s, d in _css_rules(screen) if s == '.spell' and 'grid-template-columns' in d)
    cols = _top_level_tokens(re.search(r'grid-template-columns\s*:\s*([^;]+);', decl).group(1))
    minima = []
    for col in cols:
        m = re.fullmatch(r'minmax\(\s*([\d.]+)px\s*,[^)]*\)', col)
        minima.append(float(m.group(1)) if m else _px_list(col)[0])
    gap = _px_list(re.search(r'(?<![-\w])gap\s*:\s*([^;]+);', decl).group(1))[0]
    pad = _px_list(re.search(r'(?<![-\w])padding\s*:\s*([^;]+);', decl).group(1))
    horizontal_padding = 2 * (pad[1] if len(pad) > 1 else pad[0])
    return sum(minima) + (len(cols) - 1) * gap + horizontal_padding


def test_css_spell_grid_min_width_fits_row_at_1071px():
    # D-046: bei Viewport 1071 px ist die Zeile ~934 px breit (Sprint-018-Messung); das Grid darf mit Padding hoechstens
    # 934 - 40 px Reserve brauchen, sonst ragen letzte Zelle und Artikel-Panel aus der .spell-Box (Vorzustand: 978 px).
    assert _spell_grid_min_width(css_bundle()) <= 934 - 40


def test_css_spell_grid_min_width_helper_computes_old_and_new_layouts():
    old = '.spell{ display:grid; grid-template-columns: minmax(200px,1.7fr) 240px 38px 80px minmax(110px,1fr) minmax(240px,2fr); gap:10px; padding:9px 10px; }'
    assert _spell_grid_min_width(old) == 908 + 5 * 10 + 20


def test_zauber_sort_button_accessible_name_contains_visible_label(live_html):
    m = re.search(r'<button[^>]*data-spell-sort[^>]*aria-label="([^"]*)"[^>]*>([^<]*)</button>', live_html)
    assert m
    assert m.group(1).startswith(m.group(2))
    js = (Path(rendering.STATIC_DIR) / 'zauber-sort.js').read_text(encoding='utf-8')
    assert "setAttribute('aria-label', btn.textContent" in js


def test_render_has_no_inline_spell_sort_block(live_html, static_js_html):
    for html in (live_html, static_js_html, server._render_dashboard('illaen-baernhold')):
        assert 'Sortierung Zauber-Tabelle' not in html
        assert '.spell:first-child' not in html


def test_static_render_inlines_zauber_sort_js_once(static_js_html):
    assert static_js_html.count('<script>/* zauber-sort.js */') == 1
    assert static_js_html.count("querySelector('[data-spell-list]')") == 1


def test_zauber_sort_js_follows_zauberspeicher_js():
    assert JS_FILES.index('zauber-sort.js') == JS_FILES.index('zauberspeicher.js') + 1


def test_spell_toolbar_css_stays_visible_in_compact_layout():
    css = css_bundle()
    assert '.spell-toolbar' in css and '.spell-sort-btn' in css
    # ausserhalb der Druckregel darf nichts die Toolbar ausblenden (auch nicht der 1070-px-Block)
    screen = _strip_print_blocks(css)
    assert not re.search(r'\.spell-(?:toolbar|sort-btn)[^{}]*\{[^}]*display:\s*none', screen)
    assert re.search(r'@media print\s*\{[^@]*\.spell-toolbar\s*\{[^}]*display:\s*none', css)
    # Touch-Ziel im Kompaktlayout
    m = re.search(r'@media screen and \(max-width:1070px\)\{(.*?)\n\}', css, re.S)
    assert m and re.search(r'\.spell-sort-btn\{[^}]*min-height:\s*44px', m.group(1))


def test_render_chronik_tab_server():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    html = server._render_dashboard('illaen-baernhold')
    ctx = build_context('illaen-baernhold')
    assert html.count('id="tab-chronik"') == 1
    assert 'id="tab-journal"' not in html
    assert len(re.findall(r'class="card chronik-abend"', html)) == len(ctx['chronik']['spielabende'])
    assert '/chronik-bild/' + BILD in html
    assert '<script src="/static/chronik.js"></script>' in html


def test_every_static_js_file_is_listed():
    on_disk = {p.name for p in STATIC_DIR.glob('*.js')}
    assert on_disk == set(JS_FILES)


def test_register_js_follows_chronik_js():
    assert JS_FILES.index('register.js') == JS_FILES.index('chronik.js') + 1


def test_js_files_have_no_duplicates():
    assert len(JS_FILES) == len(set(JS_FILES))


def test_no_static_js_contains_script_end_tag():
    for name in JS_FILES:
        text = (STATIC_DIR / name).read_text(encoding='utf-8')
        assert '</script' not in text.lower(), f'{name} enthaelt </script — Einbettung inline waere kaputt'


def test_js_files_is_env_global_in_order():
    assert make_env().globals['js_files'] is js_files
    assert js_files() == [(n, (STATIC_DIR / n).read_text(encoding='utf-8')) for n in JS_FILES]


def test_build_context_inline_js_flag():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    assert build_context('illaen-baernhold')['inline_js'] is False
    assert build_context('illaen-baernhold', inline_js=True)['inline_js'] is True


@pytest.fixture(scope='module')
def static_js_html():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    return render_dashboard(build_context('illaen-baernhold', inline_js=True))


def test_static_render_inlines_each_js_file_once_in_order(static_js_html):
    assert not re.search(r'<script src="/static/', static_js_html)
    positions = []
    for name in JS_FILES:
        marker = f'<script>/* {name} */'
        assert static_js_html.count(marker) == 1, f'{name}: Inline-Block fehlt oder doppelt'
        positions.append(static_js_html.index(marker))
    assert positions == sorted(positions)
    for name, text in js_files():
        assert text in static_js_html, f'{name}: Quelltext nicht eingebettet'


def test_server_render_links_each_js_file_in_order():
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    html = server._render_dashboard('illaen-baernhold')
    tags = re.findall(r'<script src="/static/([^"]+)"></script>', html)
    assert tags == list(JS_FILES) and len(tags) == len(JS_FILES)
    assert not re.search(r'/\* \w+\.js \*/', html)


def test_static_hinweis_banner_only_in_static_render(static_js_html):
    assert static_js_html.count('id="static-hinweis"') == 1
    assert 'nicht gespeichert' in static_js_html
    assert 'id="static-hinweis"' not in server._render_dashboard('illaen-baernhold')
    assert 'id="static-hinweis"' not in render_dashboard(build_context('illaen-baernhold'))


def _kampf_tab(html):
    start = html.index('id="tab-kampf"')
    end = html.index('class="tab-content"', start + 1)
    return html[start:end]


def _weapon_cards(kampf):
    return kampf.count('class="weapon-card"')


def _assert_wund_stat_hooks(kampf):
    stats = re.findall(r'data-wund-stat="(\w+)"', kampf)
    # Vitalwerte: INI, GS; Kampfwerte: AT, PA, FK; je Waffenkarte: AT, PA (Kartenzahl aus demselben HTML, nicht aus dem Bogen)
    assert sorted(stats) == sorted(['INI', 'GS', 'AT', 'PA', 'FK'] + ['AT', 'PA'] * _weapon_cards(kampf))
    assert len(re.findall(r'data-wund-base="', kampf)) == len(stats)


def test_render_kampf_tab_has_wund_stat_hooks_for_wound_stats(live_html):
    _assert_wund_stat_hooks(_kampf_tab(live_html))


def test_render_kampf_tab_without_weapon_has_only_the_five_base_wund_stat_hooks(synth_html):
    kampf = _kampf_tab(synth_html)  # synthetischer Held ohne Nahkampfwaffe
    assert _weapon_cards(kampf) == 0
    _assert_wund_stat_hooks(kampf)


def test_render_kampf_tab_wund_stat_hooks_skip_mr_so_and_weapon_ini(live_html):
    kampf = _kampf_tab(live_html)
    for abbr in ('MR', 'SO'):
        assert f'data-wund-stat="{abbr}"' not in kampf
    # jede Zelle mit dem Hook traegt einen der fuenf Basiswert-Schluessel; Waffen-INI/BF/DK/TP nicht
    for cell in re.findall(r'<div[^>]*>\s*<span class="k">(?:MR|SO|DK|TP|BF)</span>.*?</div>', kampf, re.S):
        assert 'data-wund-stat' not in cell
    # Waffen-INI: Label vor dem Wert (beim Vitalwert INI steht der Wert vor dem Label) -- je Waffenkarte genau eine
    weapon_ini = re.findall(r'<span class="k">INI</span><span class="v"[^>]*>', kampf)
    assert len(weapon_ini) == _weapon_cards(kampf)
    assert all('data-wund-stat' not in tag for tag in weapon_ini)


def test_render_kampf_tab_wund_hooks_keep_click_handlers_on_base_values(live_html):
    kampf = _kampf_tab(live_html)
    assert re.search(r'<div class="minor" data-at="\d+">', kampf)
    assert re.search(r'<div class="minor" data-pa="\d+">', kampf)


# Fall "mit Waffe" synthetisch (B-024): Die drei Live-Tests oben werden vakuoes (0 == 0), sobald der Live-Bogen keine
# Nahkampfwaffe fuehrt. Der Mini-Held hat genau eine; kampf.j2 rendert nur waffen[0] (eine Waffenkarte).
WAFFE_SLUG = 'synth-waffe'
# _SYNTH_ILLAEN hat nur LE/AU/AE; die Kampfwerte-Karte braucht AT/PA/FK/INI mit Zahlen, sonst waere data-at leer.
_WAFFE_ILLAEN = _SYNTH_ILLAEN + """| Magieresistenz (MR) | (MU+KL+KO)/5 | 0 | 7 | 7 | — |
| Initiative (INI) | (MU+MU+IN+GE)/5 | 0 | 10 | 10 | — |
| Attacke (AT) | (MU+GE+KK)/5 | 0 | 7 | 7 | — |
| Parade (PA) | (IN+GE+KK)/5 | 0 | 8 | 8 | — |
| Fernkampf-Basis (FK) | (IN+FF+KK)/5 | 0 | 8 | 8 | — |
"""
_WAFFE_AUSRUESTUNG = """## Nahkampfwaffen

| Waffe | Typ/BE | DK | TP | TP/KK | Ini | WM | AT | PA | eff. TP | min BF | akt. BF |
|-------|--------|----|----|-------|-----|----|----|----|---------|--------|---------|
| Testdolch | Dolch / BE−1 | H | 1W+2 | 12/4 | 1 | 0/0 | 11 | 9 | 1W+2 | −8 | −8 |
"""


@pytest.fixture(scope='module')
def waffe_kampf(tmp_path_factory):
    """Kampf-Tab-HTML eines synthetischen Helden mit genau einer Nahkampfwaffe (ohne Wiki-Artikel)."""
    root = write_mini_held(tmp_path_factory.mktemp('waffe_vault'), slug=WAFFE_SLUG,
                           illaen=_WAFFE_ILLAEN, ausruestung=_WAFFE_AUSRUESTUNG)
    ctx = build_context(WAFFE_SLUG, root)
    assert [w['name'] for w in ctx['held']['ausruestung']['waffen']] == ['Testdolch']
    kampf = _kampf_tab(render_dashboard(ctx))
    assert _weapon_cards(kampf) == 1  # nicht vakuoes: die Waffe kommt wirklich als Karte im HTML an
    return kampf


def test_render_kampf_tab_with_weapon_has_wund_stat_hooks_on_base_values_and_weapon_card(waffe_kampf):
    _assert_wund_stat_hooks(waffe_kampf)
    assert len(re.findall(r'data-wund-stat="(?:AT|PA)"', waffe_kampf)) == 4  # AT/PA-Basis + AT/PA der Waffenkarte


def test_render_kampf_tab_with_weapon_wund_stat_hooks_skip_mr_so_and_weapon_ini(waffe_kampf):
    for abbr in ('MR', 'SO'):
        assert f'data-wund-stat="{abbr}"' not in waffe_kampf
    cells = re.findall(r'<div[^>]*>\s*<span class="k">(?:MR|SO|DK|TP|BF)</span>.*?</div>', waffe_kampf, re.S)
    assert len(cells) >= 3  # mindestens DK/TP/BF der Waffenkarte (plus MR/SO), sonst prueft die Schleife nichts
    for cell in cells:
        assert 'data-wund-stat' not in cell
    weapon_ini = re.findall(r'<span class="k">INI</span><span class="v"[^>]*>', waffe_kampf)
    assert len(weapon_ini) == 1
    assert 'data-wund-stat' not in weapon_ini[0]


def test_render_kampf_tab_with_weapon_wund_hooks_keep_click_handlers_on_base_values(waffe_kampf):
    assert re.search(r'<div class="minor" data-at="\d+">', waffe_kampf)
    assert re.search(r'<div class="minor" data-pa="\d+">', waffe_kampf)


# -- Zustands-Chips als Hausregel gekennzeichnet (D-041c) --

def test_render_kampf_tab_has_one_zustand_legend_below_chips(live_html):
    kampf = _kampf_tab(live_html)
    assert kampf.count('class="zustand-legend"') == 1
    chips_at = _pos(kampf, 'id="zustand-chips"', 'Zustands-Chips')
    legend = re.search(r'<div class="zustand-legend">(.*?)</div>', kampf, re.S)
    assert legend and legend.start() > chips_at
    text = legend.group(1)
    assert 'Hausregel' in text
    assert 'WdS S. 57' in text
    assert 'kein fester Probenmalus' in text


def test_render_zustand_legend_wound_sentence_stays_outside_the_hideable_chips_span(live_html):
    # Ohne Chips (Static-Render) verschwindet nur der Chip-Satz; der Wund-Satz ist der einzige Seitenhinweis auf die Regel.
    legend = re.search(r'<div class="zustand-legend">(.*?)</div>', _kampf_tab(live_html), re.S).group(1)
    spans = re.findall(r'<span class="zustand-legend-chips">(.*?)</span>', legend, re.S)
    assert len(spans) == 1
    assert 'Hausregel' in spans[0] and 'kein fester Probenmalus' in spans[0]
    outside = legend.replace(spans[0], '')
    assert 'WdS S. 57' in outside and 'Wunden wirken' in outside
    assert 'WdS S. 57' not in spans[0]
    assert '<a href=' in outside and 'Details' in outside


def test_zustand_legend_chip_sentence_hidden_without_chips_wound_sentence_kept_and_print_hides_all():
    # Static-Render (file://): session.js rendert die Chips nicht -> nur der Chip-Satz ist ohne Bezug; die Legende
    # selbst bleibt (Wund-Regel). Druck blendet Chips UND Legende komplett aus.
    css = css_bundle()
    rules = _css_rules(css)
    chips_span = '#zustand-chips:empty + .zustand-legend .zustand-legend-chips'
    assert any(re.search(r'display\s*:\s*none', d) for d in _decls(rules, chips_span))
    assert not any(re.search(r'display\s*:\s*none', d) for d in _decls(rules, '#zustand-chips:empty + .zustand-legend'))
    print_rules = _css_rules(''.join(_media_blocks(css, r'@media\s+print')))
    for sel in ('#zustand-chips', '.zustand-legend'):
        assert any(re.search(r'display\s*:\s*none', d) for d in _decls(print_rules, sel)), f'{sel} fehlt in der Druck-Ausblendung'


# -- D-048: Legende sagt, dass Zustands-Chips nur die Probe veraendern, nicht die angezeigten Werte --

def test_render_zustand_legend_says_chips_change_only_the_roll_not_displayed_values(live_html):
    legend = re.search(r'<div class="zustand-legend">(.*?)</div>', _kampf_tab(live_html), re.S).group(1)
    chips_span = re.search(r'<span class="zustand-legend-chips">(.*?)</span>', legend, re.S).group(1)
    assert 'nur die Probe' in chips_span and 'Würfelpanel' in chips_span
    assert re.search(r'nicht die angezeigten\s+Attribut- und Basiswerte', chips_span)
    assert chips_span.endswith(' '), 'Leerzeichen trennt Chip- und Wund-Satz, wenn die Chips sichtbar sind'
    # Der Wund-Satz (regelkonformes Overlay) bleibt ausserhalb des ausblendbaren Chip-Satzes und ohne fuehrendes Leerzeichen.
    outside = legend.replace(chips_span, '')
    assert 'nicht die angezeigten' not in outside
    assert re.search(r'</span>Wunden wirken regelkonform', legend)


def test_render_zustand_legend_links_to_wiki_article_without_double_md(live_html):
    legend = re.search(r'<div class="zustand-legend">(.*?)</div>', _kampf_tab(live_html), re.S).group(1)
    hrefs = re.findall(r'href="([^"]+)"', legend)
    assert hrefs == ['obsidian://open?vault=DSA-Vault&file=wiki/dsa-4.1/grundregeln/zustaende.md']
    assert (VAULT_ROOT / 'wiki' / 'dsa-4.1' / 'grundregeln' / 'zustaende.md').exists()


def test_css_bundle_styles_hausregel_chip_and_legend():
    css = _strip_print_blocks(css_bundle())
    assert re.search(r'\.zustand-chip\.hausregel\s*\{[^}]*dashed', css)
    assert re.search(r'\.zustand-chip\.hausregel\.active\s*\{', css)
    legend = re.search(r'\.zustand-legend\s*\{([^}]*)\}', css)
    assert legend and 'overflow-wrap' in legend.group(1)
    for _sel, body in re.findall(r'(\.zustand-(?:chip\.hausregel|legend)[^{]*)\{([^}]*)\}', css):
        assert not re.search(r'#[0-9a-fA-F]{3,8}\b', re.sub(r'var\([^)]*\)', '', body)), 'keine neuen Hex-Werte'


# ---- D-044: Mobile/Touch-Feinschliff (Sprint 019, Task 5) ----

def _screen_rules(css, max_width):
    """Flache Regeln aller '@media screen and (max-width:<max_width>px)'-Bloecke."""
    return _css_rules(''.join(_media_blocks(css, r'@media\s+screen\s+and\s+\(max-width:\s*%dpx\)' % max_width)))


def _decls(rules, selector):
    return [d for s, d in rules if s == selector]


def test_css_banner_narrow_layout_at_600px():
    # D-044: bei 400 px war "BAERNHOLD" (44 px Cinzel) rechts abgeschnitten (.banner overflow:hidden).
    rules = _screen_rules(css_bundle(), 600)
    assert any(re.search(r'padding\s*:\s*24px\s+16px\s+20px', d) for d in _decls(rules, '.banner'))
    assert any(
        re.search(r'grid-template-columns\s*:\s*(?:minmax\(\s*0\s*,\s*1fr\s*\)|1fr)\s*(?:;|$)', d)
        for d in _decls(rules, '.banner-inner')
    )
    assert any(re.search(r'font-size\s*:\s*clamp\(', d) for d in _decls(rules, '.title-block h1'))
    assert any(re.search(r'flex-wrap\s*:\s*wrap', d) for d in _decls(rules, '.identity-stats'))
    # Desktop-Grid bleibt dreispaltig (Regel ausserhalb der Media-Bloecke)
    assert re.search(r'\.banner-inner\s*\{[^}]*grid-template-columns\s*:\s*auto\s+1fr\s+auto', css_bundle())


def test_css_banner_longest_word_fits_at_400px():
    # Rechnung: Cinzel Bold ~0,75 em/Zeichen + 0,04 em Laufweite -> konservativ 0,83 em (Brief: 44 px ~ 330 px fuer 9 Zeichen).
    # Innenbreite bei Viewport 400 px = 400 - 2*28 (.codex-Padding) - 2 (Banner-Rahmen) - 2*horizontales Banner-Padding.
    rules = _screen_rules(css_bundle(), 600)
    pad = next(re.search(r'padding\s*:\s*[\d.]+px\s+([\d.]+)px', d) for d in _decls(rules, '.banner') if 'padding' in d)
    inner = 400 - 2 * 28 - 2 - 2 * float(pad.group(1))
    h1 = next(d for d in _decls(rules, '.title-block h1') if 'clamp(' in d)
    vw = float(re.search(r'clamp\(\s*[\d.]+px\s*,\s*([\d.]+)vw', h1).group(1))
    word = 9 * 0.83 * (400 * vw / 100)
    assert word <= inner - 40, f'BAERNHOLD braucht ~{word:.0f} px von {inner:.0f} px (mind. 40 px Reserve)'
    assert re.search(r'overflow-wrap\s*:\s*anywhere', h1)


def test_css_footer_bar_static_and_touch_sized_at_480px():
    # D-044: Leiste verdeckte ~82 px Viewport, Buttons schrumpften auf ~33 px -> statisch am Seitenende, >= 44 px hoch.
    css = css_bundle()
    block = ''.join(_media_blocks(css, r'@media\s+screen\s+and\s+\(max-width:\s*480px\)'))
    assert 'position:fixed' not in block.replace(' ', '')
    rules = _css_rules(block)
    bar = ' '.join(_decls(rules, '#footer-bar'))
    assert re.search(r'position\s*:\s*static', bar)
    assert not re.search(r'(?<![-\w])(?:left|right|bottom)\s*:', bar)
    # statische Leiste braucht die 120 px Reserve der schwebenden nicht mehr (sonst ~136 px Leerraum davor)
    assert re.search(r'padding-bottom\s*:\s*36px', ' '.join(_decls(rules, '.codex')))
    for sel in ('#footer-bar .print-btn', '#footer-bar .commit-input'):
        assert any(re.search(r'min-height\s*:\s*44px', d) for d in _decls(rules, sel)), sel
    # Desktop: schwebend unten rechts, hebt sich um die Panelhoehe (D-049)
    assert re.search(
        r'#footer-bar\s*\{\s*position\s*:\s*fixed;\s*bottom\s*:\s*calc\(\s*28px\s*\+\s*var\(\s*--dice-panel-h\s*,\s*0px\s*\)\s*\)\s*;\s*right\s*:\s*28px;',
        css,
    )


def _steigern_js():
    return (STATIC_DIR / 'steigern.js').read_text(encoding='utf-8')


def test_steigern_js_wraps_tables_in_focusable_scroll_region():
    # D-044: Wrapper-div statt role auf <table> (role=region wuerde die Tabellensemantik zerstoeren).
    js = _steigern_js()
    section = js[js.index('function addSection'):]
    section = section[:section.index('/* Eigenschaften */')]
    assert "className = 'steiger-scroll'" in section
    # tabindex/role/aria-label setzt seit D-047 nur syncScrollOverflow (bei echtem Ueberlauf, s. Abschnitt D-047)
    assert not re.search(r"table\.setAttribute\('role'", section)
    assert re.search(r'\.appendChild\(table\)', section)
    assert section.index('.appendChild(table)') < section.index('list.appendChild(wrap')
    # sichtbarer Hinweis vor der Tabelle, fuer Screenreader ausgeblendet (der Wrapper hat schon einen Namen)
    assert "className = 'sg-scroll-hint'" in section
    assert re.search(r"setAttribute\('aria-hidden',\s*'true'\)", section)
    assert section.index('sg-scroll-hint') < section.index('list.appendChild(wrap')


def test_css_steigern_scroll_wrapper_and_hint_base():
    css = css_bundle()
    screen = _strip_print_blocks(css)
    top = _css_rules(re.sub(r'@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', screen))
    # Scrollen wandert von der Tabelle auf den Wrapper; die Tabelle bleibt display:table
    assert any(re.search(r'overflow-x\s*:\s*auto', d) for d in _decls(top, '.steiger-scroll'))
    assert any(re.search(r'outline\s*:\s*2px\s+solid\s+var\(--accent-cold\)', d) for d in _decls(top, '.steiger-scroll:focus-visible'))
    assert not any(re.search(r'display\s*:', d) for d in _decls(_css_rules(screen), '.steiger-table'))
    assert not any(re.search(r'overflow', d) for d in _decls(_css_rules(screen), '.steiger-table'))
    # Hinweis: sonst aus, gedaempft (Einblenden bei Ueberlauf: D-047, Abschnitt am Dateiende)
    base = ' '.join(_decls(top, '.sg-scroll-hint'))
    assert re.search(r'display\s*:\s*none', base) and 'var(--ink-mute)' in base


def _inv_add_input(html, input_id):
    return re.search(r'<input[^>]*id="%s"[^>]*>' % input_id, html).group(0)


def test_render_inventar_add_inputs_use_modifier_classes(live_html):
    name, anzahl = _inv_add_input(live_html, 'inv-add-name'), _inv_add_input(live_html, 'inv-add-anzahl')
    assert re.search(r'class="inv-add-input inv-add-input--name"', name)
    assert re.search(r'class="inv-add-input inv-add-input--anzahl"', anzahl)
    assert 'style=' not in name and 'style=' not in anzahl
    assert 'placeholder="Gegenstand"' in name and 'placeholder="Anzahl"' in anzahl
    assert live_html.count('id="inv-add-name"') == 1 and live_html.count('id="inv-add-anzahl"') == 1


def test_css_inventar_add_inputs_do_not_depend_on_dom_order():
    css = css_bundle()
    assert '.inv-add-input:first-child' not in css
    assert any(re.search(r'flex-basis\s*:\s*100%', d) for d in _decls(_screen_rules(css, 480), '.inv-add-input--name'))
    assert any(re.search(r'max-width\s*:\s*80px', d) for d in _decls(_css_rules(_strip_print_blocks(css)), '.inv-add-input--anzahl'))


def test_css_artikel_toggle_is_touch_sized_only_in_compact_layout():
    # D-044: Summary "Artikel" war ~18 px hoch; Ziel 44 px, aber nur im Kompaktlayout (Desktop-Grid unveraendert).
    css = css_bundle()
    compact = _decls(_screen_rules(css, 1070), 'summary.artikel-toggle')
    assert any(
        re.search(r'display\s*:\s*flex', d) and re.search(r'align-items\s*:\s*center', d) and re.search(r'min-height\s*:\s*44px', d)
        for d in compact
    )
    base = ' '.join(_decls(_css_rules(_strip_print_blocks(css)), '.artikel-details summary.artikel-toggle'))
    assert 'min-height' not in base


# -- D-045: Chronik-Druck — nur aktive Ansicht + Filter-Kopfzeile ------------

def _print_rules():
    return _css_rules(''.join(_media_blocks(css_bundle(), r'@media\s+print')))


def test_css_print_chronik_prints_only_active_view():
    # D-045: die Druckregel .chronik-view{display:block!important} erzwang Roh + Kompiliert immer gemeinsam.
    prints = _print_rules()
    active = [d for s, d in prints if s == '.chronik-view--active']
    assert any(re.search(r'display\s*:\s*block\s*!important', d) for d in active)
    assert not [s for s, _ in prints if s == '.chronik-view'], 'nacktes .chronik-view im Druck-Block'
    assert not [s for s, _ in prints if ':not(.chronik-view--active)' in s], 'Register-Sonderregel muss entfallen'
    # nicht aktive Ansichten bleiben ueber die Bildschirm-Basisregel ausgeblendet (kein Druck-Override darauf)
    screen = _css_rules(_strip_print_blocks(css_bundle()))
    assert any(re.search(r'display\s*:\s*none', d) for s, d in screen if s == '.chronik-view')


def test_css_register_druckfilter_only_visible_in_print_when_not_hidden():
    screen = _css_rules(_strip_print_blocks(css_bundle()))
    base = [d for s, d in screen if s == '.register-druckfilter']
    assert any(re.search(r'display\s*:\s*none', d) for d in base), 'am Bildschirm immer unsichtbar'
    print_rules = [(s, d) for s, d in _print_rules() if s.startswith('.register-druckfilter')]
    shown = [s for s, d in print_rules if re.search(r'display\s*:\s*block\s*!important', d)]
    assert shown == ['.register-druckfilter:not([hidden])']
    # keine andere Druckregel darf display setzen (wuerde [hidden] uebersteuern)
    assert all(s in shown or 'display' not in d for s, d in print_rules)


def test_render_register_druckfilter_is_hidden_and_outside_register_tools(live_html):
    assert live_html.count('class="register-druckfilter"') == 1
    tag = re.search(r'<p class="register-druckfilter"[^>]*></p>', live_html)
    assert tag and re.search(r'(?<![-\w])hidden(?![-\w])', tag.group(0)), 'Kopfzeile muss initial hidden sein'
    tools = re.search(r'<div class="register-tools">.*?</div>', live_html, re.S).group(0)
    assert 'register-druckfilter' not in tools, 'register-tools wird im Druck ausgeblendet'
    view = live_html.index('id="chronik-view-register"')
    assert view < tag.start() < live_html.index('<section class="card register-gruppe"', view)


# -- D-047: Touch-Ziele & Mobile-Restposten bei 400 px ------------------------

def _toplevel_rules(css):
    """Flache Regeln ausserhalb jedes @media-Blocks (Desktop-/Basis-Layout)."""
    stripped = re.sub(r'@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}', '', re.sub(r'/\*.*?\*/', '', css, flags=re.S))
    return _css_rules(stripped)


def test_css_inventar_add_controls_touch_sized_only_at_480px():
    # D-047: Eingaben + "+ Hinzufuegen" waren bei 400 px je 30 px hoch. Nur im <= 480-px-Block, Desktop unveraendert.
    css = css_bundle()
    narrow = _screen_rules(css, 480)
    for sel in ('.inv-add-input', '.inv-add-btn'):
        assert any(re.search(r'min-height\s*:\s*44px', d) for d in _decls(narrow, sel)), sel
        assert not any('min-height' in d for d in _decls(_toplevel_rules(css), sel)), f'{sel}: min-height auch ausserhalb des Blocks'


def test_css_zustand_chip_touch_sized_only_at_480px():
    # D-047: Chips waren 25 px hoch; inline-flex + align-items:center zentriert das Label in der 44-px-Flaeche.
    css = css_bundle()
    decl = ' '.join(_decls(_screen_rules(css, 480), '.zustand-chip'))
    assert re.search(r'min-height\s*:\s*44px', decl)
    assert re.search(r'display\s*:\s*inline-flex', decl) and re.search(r'align-items\s*:\s*center', decl)
    assert not any('min-height' in d for d in _decls(_toplevel_rules(css), '.zustand-chip'))


def test_css_body_reserves_dice_panel_height_at_480px():
    # D-047: das fixe Wuerfelpanel (~190 px bei 400 px) verdeckte Footer-Leiste und letzte Zeilen. Reserve = gemessene Panelhoehe
    # (--dice-panel-h, von dice.js gepflegt), auf <body> (die Footer-Leiste liegt ausserhalb von .codex). Nur <= 480 px.
    css = css_bundle()
    assert any(
        re.search(r'padding-bottom\s*:\s*var\(\s*--dice-panel-h\s*(?:,\s*0(?:px)?\s*)?\)', d)
        for d in _decls(_screen_rules(css, 480), 'body')
    )
    # Top-Level nutzt nur die Footer-Leiste die Variable (D-049); die body-Reserve bleibt exklusiv im schmalen Block
    assert {s for s, d in _toplevel_rules(css) if '--dice-panel-h' in d} == {'#footer-bar'}


def test_css_footer_bar_rises_above_open_dice_panel_on_desktop():
    # D-049: das offene Panel (fixed, z-index 200) verdeckte die Leiste (fixed, z-index 100; ~277 px bei 1280 px).
    # Ursache festhalten: solange das Panel darueber liegt, muss die Leiste um --dice-panel-h steigen.
    top = _toplevel_rules(css_bundle())
    bar = ' '.join(_decls(top, '#footer-bar'))
    panel = ' '.join(_decls(top, '.dice-panel'))
    assert re.search(r'(?<![-\w])bottom\s*:\s*calc\(\s*28px\s*\+\s*var\(\s*--dice-panel-h\s*,\s*0px\s*\)\s*\)', bar)
    assert re.search(r'position\s*:\s*fixed', panel)
    assert re.search(r'(?<![-\w])bottom\s*:\s*0(?![.\w])', panel), 'die Anhebung stimmt nur bei Panel am Viewport-Boden'
    m_panel, m_bar = (re.search(r'z-index\s*:\s*(\d+)', d) for d in (panel, bar))
    assert m_panel and m_bar, 'Panel und Leiste brauchen beide ein z-index'
    z_panel, z_bar = int(m_panel.group(1)), int(m_bar.group(1))
    assert z_panel > z_bar, 'Panel liegt ueber der Leiste -> Leiste muss um die Panelhoehe steigen'


def test_dice_js_publishes_open_panel_height_as_css_variable():
    js = (STATIC_DIR / 'dice.js').read_text(encoding='utf-8')
    body = js_function(js, 'syncPanelReserve')
    assert re.search(r"setProperty\(\s*'--dice-panel-h'", body)
    # geschlossen (.hidden bleibt nur per transform aus dem Bild) => 0px, sonst gemessene Hoehe
    assert "classList.contains('hidden')" in body and "'0px'" in body and 'offsetHeight' in body
    # bei jedem Oeffnen/Schliessen und bei Hoehenaenderung (Modus-/Ergebnis-Umschaltung) neu setzen
    assert re.search(r'new ResizeObserver\(syncPanelReserve\)\.observe\(panel\)', js)
    assert re.search(r"panel\.classList\.remove\('hidden'\);\s*syncPanelReserve\(\)", js)
    assert re.search(r"panel\.classList\.add\('hidden'\);\s*syncPanelReserve\(\)", js)


def test_css_print_zfw_num_is_scoped_to_spell():
    # D-047: der Druck-Selektor war nackt (.zfw-num), die Geschwister (.spell .zd, .spell .kosten) sind gescoped.
    selectors = [s for s, _ in _print_rules()]
    assert '.spell .zfw-num' in selectors
    assert '.zfw-num' not in selectors


def test_steigern_js_scroll_region_only_on_real_overflow():
    # D-047: tabindex/role/aria-label und der Hinweis nur bei scrollWidth > clientWidth (sonst Extra-Tab-Stop ohne Nutzen).
    js = _steigern_js()
    section = js[js.index('function addSection'):]
    section = section[:section.index('/* Eigenschaften */')]
    assert not re.search(r"wrap\.setAttribute\('(?:tabindex|role|aria-label)'", section), 'Attribute nicht mehr bedingungslos'
    body = js_function(js, 'syncScrollOverflow')
    assert 'scrollWidth' in body and 'clientWidth' in body
    for attr in ('tabindex', 'role', 'aria-label'):
        assert re.search(r"setAttribute\('%s'" % attr, body) and re.search(r"removeAttribute\('%s'\)" % attr, body), attr
    # Neubewertung bei Groessenaenderung (Tab-Wechsel display:none -> sichtbar, Resize)
    watch = js_function(js, 'watchScrollOverflow')
    assert 'ResizeObserver' in watch and re.search(r"addEventListener\('resize'", watch)
    assert re.search(r'syncScrollOverflow\(wrap,\s*scrollHint,\s*title\)', section)


_NODE_OVERFLOW_RUNNER = """
function el(cw, sw) {
  var a = {}, c = {};
  return {clientWidth: cw, scrollWidth: sw, a: a, c: c,
    setAttribute: function (k, v) { a[k] = v; }, removeAttribute: function (k) { delete a[k]; },
    classList: {toggle: function (n, f) { if (f) c[n] = 1; else delete c[n]; return !!f; }}};
}
var out = {};
function run(name, cw, sw) {
  var wrap = el(cw, sw), hint = el(0, 0);
  syncScrollOverflow(wrap, hint, 'Zauber');
  out[name] = {attrs: wrap.a, hint: Object.keys(hint.c)};
}
run('overflow', 283, 340);
run('fits', 283, 283);
run('hidden_tab', 0, 340);
var w = el(283, 340), h = el(0, 0);
syncScrollOverflow(w, h, 'Zauber');
w.scrollWidth = 283;              // Fenster wird breiter -> Tabelle passt
syncScrollOverflow(w, h, 'Zauber');
out.widened = {attrs: w.a, hint: Object.keys(h.c)};
console.log(JSON.stringify(out));
"""


@needs_node
def test_steigern_sync_scroll_overflow_behaviour():
    out = run_node(js_function(_steigern_js(), 'syncScrollOverflow') + _NODE_OVERFLOW_RUNNER)
    assert out['overflow'] == {'attrs': {'tabindex': '0', 'role': 'region', 'aria-label': 'Zauber'}, 'hint': ['sg-scroll-hint--on']}
    assert out['fits'] == {'attrs': {}, 'hint': []}
    assert out['hidden_tab'] == {'attrs': {}, 'hint': []}, 'clientWidth 0 (display:none) ist kein Ueberlauf'
    assert out['widened'] == {'attrs': {}, 'hint': []}, 'Attribute muessen wirklich entfernt werden'


def test_css_steigern_scroll_hint_follows_overflow_state_not_media_query():
    css = css_bundle()
    screen = _strip_print_blocks(css)
    assert any(re.search(r'display\s*:\s*none', d) for d in _decls(_toplevel_rules(screen), '.sg-scroll-hint'))
    assert any(re.search(r'display\s*:\s*block', d) for d in _decls(_css_rules(screen), '.sg-scroll-hint.sg-scroll-hint--on'))
    assert not _decls(_screen_rules(css, 600), '.sg-scroll-hint'), 'Sichtbarkeit haengt nicht mehr an der Media-Query'
