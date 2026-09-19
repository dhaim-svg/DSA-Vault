"""Tests for CSS/JS bundling and static vs. server rendering in rendering.py."""
import json
import re
import shutil
import subprocess
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


def test_build_context_has_wiki_artikel_from_live_vault():
    ctx = build_context('illaen-baernhold')
    artikel = ctx['wiki_artikel']
    assert isinstance(artikel, dict)
    assert artikel
    zauber_pfade = {z['wiki_path'] for z in ctx['held']['zauber']}
    sf_pfade = {sf['wiki_path'] for sf in ctx['held']['sf']['magisch'] + ctx['held']['sf']['allgemein'] if sf['wiki_path']}
    assert set(artikel) <= zauber_pfade | sf_pfade
    assert set(artikel) & zauber_pfade
    assert set(artikel) & sf_pfade
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


def test_render_zauber_sort_toolbar_and_list_wrapper(live_html):
    # D-043: Toolbar-Button -> Kopfzeile -> Listen-Wrapper -> Legende; Sortier-JS verschiebt nur Zeilen im Wrapper.
    assert live_html.count('data-spell-list') == 1
    assert live_html.count('data-spell-sort') == 1
    assert '<button type="button" class="spell-sort-btn" data-spell-sort' in live_html
    toolbar = live_html.index('data-spell-sort')
    head = live_html.index('class="spell spell-head"')
    wrapper = live_html.index('data-spell-list')
    legend = live_html.index('class="legend-row"')
    assert toolbar < head < wrapper < legend


def test_render_zauber_rows_all_inside_list_wrapper(live_html):
    n = len(build_context('illaen-baernhold')['held']['zauber'])
    start = live_html.index('data-spell-list')
    inside = live_html[start:live_html.index('class="legend-row"')]
    assert len(re.findall(r'<div class="spell"[ >]', inside)) == n
    assert len(re.findall(r'<div class="spell"[ >]', live_html)) == n
    assert 'spell-head' not in inside


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
    return html[html.index('<div class="spell-list" data-spell-list>'):html.index('class="legend-row"')]


def _first_wiki_path(ctx):
    return next(z['wiki_path'] for z in ctx['held']['zauber'] if z.get('wiki_path'))


def test_render_wiki_artikel_details_one_per_spell_with_article(live_html):
    ctx = build_context('illaen-baernhold')
    erwartet = sum(1 for z in ctx['held']['zauber'] if z.get('wiki_path') in ctx['wiki_artikel'])
    assert erwartet
    sf = ctx['held']['sf']['magisch'] + ctx['held']['sf']['allgemein']
    erwartet_sf = sum(1 for e in sf if e.get('wiki_path') in ctx['wiki_artikel'])
    assert erwartet_sf
    assert live_html.count('class="artikel-details"') == erwartet + erwartet_sf
    assert len(_artikel_details_parents(_sf_card(live_html))) == erwartet_sf  # D-050: SF-Zeilen, nicht die Zauberliste
    parents = _artikel_details_parents(_spell_list_fragment(live_html))
    assert len(parents) == erwartet
    # direktes Kind der Zeile (wandert beim Sortieren mit), Zeile direkt im Listen-Wrapper
    assert all(p == (('div', 'spell'), ('div', True)) for p in parents)


def test_render_wiki_artikel_empty_or_missing_has_no_details_but_keeps_name_links():
    ctx = build_context('illaen-baernhold')
    ctx['wiki_artikel'] = {}
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 0
    assert 'class="nlink"' in html
    del ctx['wiki_artikel']
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 0
    assert 'class="nlink"' in html


def test_render_wiki_artikel_escapes_text_fields_but_not_html():
    ctx = build_context('illaen-baernhold')
    pfad = _first_wiki_path(ctx)
    ctx['wiki_artikel'] = {pfad: {
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


def test_render_wiki_artikel_has_single_obsidian_link_without_nlink(live_html):
    block = re.search(r'<details class="artikel-details">.*?</details>', live_html, re.S).group(0)
    kopf = re.search(r'<div class="artikel-kopf">.*?</div>', block, re.S).group(0)
    assert kopf.count('href="obsidian://') == 1
    assert re.search(r'<a class="artikel-obsidian" href="obsidian://[^"]+">↗ Obsidian</a>', kopf)
    assert 'nlink' not in block
    # der ↗ am Zaubernamen bleibt Sache des Namenslinks in .name (CSS ::after)
    row = live_html[:live_html.index('class="artikel-details"')]
    assert row.rindex('class="nlink"') > row.rindex('<div class="spell"')


# -- D-050: Artikelvorschau fuer Sonderfertigkeiten ---------------------------

SF_A = 'wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Alpha'
SF_D = 'wiki/dsa-4.1/sonderfertigkeiten/allgemeine-sonderfertigkeiten#Delta'


def _sf_context(wiki_artikel):
    """Kontext mit synthetischen SF: Alpha (magisch) und Delta (allgemein) haben einen Anker-Link, Gamma/Eps
    einen ohne geladenen Artikel, Beta keinen Link."""
    ctx = build_context('illaen-baernhold')
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


def _sf_artikel(titel='Titel A', html='<p>Body A</p>'):
    return {'titel': titel, 'quelle': 'WdZ', 'meta': [], 'html': html}


def _sf_card(html):
    start = html.index('<h3 class="card-title">Sonderfertigkeiten</h3>')
    return html[start:html.index('</section>', start)]


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


def test_render_sf_artikel_details_inside_their_own_li_with_title_source_and_body():
    html = render_dashboard(_sf_context({SF_A: _sf_artikel(), SF_D: _sf_artikel('Titel D', '<p>Body D</p>')}))
    items = _sf_items(_sf_card(html))
    assert [i['details'] for i in items] == [['li'], [], [], ['li'], []]
    assert 'Alpha' in items[0]['text'] and 'Titel A' in items[0]['text'] and 'Body A' in items[0]['text']
    assert 'Titel D' in items[3]['text'] and 'Body D' in items[3]['text'] and 'Body A' not in items[3]['text']
    assert html.count('class="artikel-details"') == 2  # Zauber ohne geladenen Artikel bekommen keinen
    block = re.search(r'<details class="artikel-details">.*?</details>', _sf_card(html), re.S).group(0)
    assert '<span class="artikel-quelle">WdZ</span>' in block
    assert re.search(r'<a class="artikel-obsidian" href="obsidian://[^"]+">↗ Obsidian</a>', block)


def test_render_sf_artikel_details_follow_the_description():
    html = _sf_card(render_dashboard(_sf_context({SF_A: _sf_artikel()})))
    li = html[html.index('Alpha'):html.index('</li>', html.index('Alpha'))]
    assert li.index('Beschreibung-A') < li.index('class="artikel-details"')


def test_render_sf_without_article_has_no_details_and_keeps_its_row():
    ctx = _sf_context({SF_A: _sf_artikel()})
    unveraendert = _sf_card(render_dashboard(_sf_context({})))
    assert 'artikel-details' not in unveraendert
    ctx['wiki_artikel'] = {}
    assert _sf_card(render_dashboard(ctx)) == unveraendert
    del ctx['wiki_artikel']
    assert _sf_card(render_dashboard(ctx)) == unveraendert
    for name in ('Alpha', 'Beta', 'Gamma', 'Delta', 'Eps'):
        assert name in unveraendert


def test_render_sf_artikel_escapes_text_fields_but_not_html():
    art = {'titel': '<b>T</b>', 'quelle': 'Q<i>', 'meta': [], 'html': '<p>ok</p>'}
    html = render_dashboard(_sf_context({SF_A: art}))
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


def test_render_kampf_tab_has_wund_stat_hooks_for_wound_stats(live_html):
    kampf = _kampf_tab(live_html)
    stats = re.findall(r'data-wund-stat="(\w+)"', kampf)
    # Vitalwerte: INI, GS; Kampfwerte: AT, PA, FK; Waffenkarte: AT, PA
    assert sorted(stats) == sorted(['INI', 'GS', 'AT', 'PA', 'FK', 'AT', 'PA'])
    assert len(re.findall(r'data-wund-base="', kampf)) == len(stats)


def test_render_kampf_tab_wund_stat_hooks_skip_mr_so_and_weapon_ini(live_html):
    kampf = _kampf_tab(live_html)
    for abbr in ('MR', 'SO'):
        assert f'data-wund-stat="{abbr}"' not in kampf
    # jede Zelle mit dem Hook traegt einen der fuenf Basiswert-Schluessel; Waffen-INI/BF/DK/TP nicht
    for cell in re.findall(r'<div[^>]*>\s*<span class="k">(?:MR|SO|DK|TP|BF)</span>.*?</div>', kampf, re.S):
        assert 'data-wund-stat' not in cell
    weapon_ini = re.search(r'<span class="k">INI</span><span class="v"[^>]*>', kampf)
    assert weapon_ini and 'data-wund-stat' not in weapon_ini.group(0)


def test_render_kampf_tab_wund_hooks_keep_click_handlers_on_base_values(live_html):
    kampf = _kampf_tab(live_html)
    assert re.search(r'<div class="minor" data-at="\d+">', kampf)
    assert re.search(r'<div class="minor" data-pa="\d+">', kampf)


# -- Zustands-Chips als Hausregel gekennzeichnet (D-041c) --

def test_render_kampf_tab_has_one_zustand_legend_below_chips(live_html):
    kampf = _kampf_tab(live_html)
    assert kampf.count('class="zustand-legend"') == 1
    chips_at = kampf.index('id="zustand-chips"')
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


def _js_function(src, name):
    """Quelltext von 'function <name>(...) { ... }' (Klammer-Zaehlung; nur fuer klammerneutrale Funktionskoerper)."""
    start = src.index('function %s(' % name)
    depth, j = 0, src.index('{', start)
    while True:
        depth += {'{': 1, '}': -1}.get(src[j], 0)
        j += 1
        if depth == 0:
            return src[start:j]


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
    body = _js_function(js, 'syncPanelReserve')
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
    body = _js_function(js, 'syncScrollOverflow')
    assert 'scrollWidth' in body and 'clientWidth' in body
    for attr in ('tabindex', 'role', 'aria-label'):
        assert re.search(r"setAttribute\('%s'" % attr, body) and re.search(r"removeAttribute\('%s'\)" % attr, body), attr
    # Neubewertung bei Groessenaenderung (Tab-Wechsel display:none -> sichtbar, Resize)
    watch = _js_function(js, 'watchScrollOverflow')
    assert 'ResizeObserver' in watch and re.search(r"addEventListener\('resize'", watch)
    assert re.search(r'syncScrollOverflow\(wrap,\s*scrollHint,\s*title\)', section)


needs_node = pytest.mark.skipif(shutil.which('node') is None, reason='node nicht installiert')

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
    src = _js_function(_steigern_js(), 'syncScrollOverflow')
    res = subprocess.run(['node', '-e', src + _NODE_OVERFLOW_RUNNER], capture_output=True, text=True, timeout=30)
    assert res.returncode == 0, res.stderr
    out = json.loads(res.stdout)
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
