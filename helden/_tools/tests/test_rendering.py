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
    assert ctx['zauber_artikel'] == {}


def test_build_context_has_register_from_live_vault():
    ctx = build_context('illaen-baernhold')
    assert set(ctx['register']) == {'nscs', 'orte'}
    assert ctx['register']['nscs']
    assert ctx['register']['orte']


def test_build_context_has_zauber_artikel_from_live_vault():
    ctx = build_context('illaen-baernhold')
    artikel = ctx['zauber_artikel']
    assert isinstance(artikel, dict)
    assert artikel
    zauber_pfade = {z['wiki_path'] for z in ctx['held']['zauber']}
    assert set(artikel) <= zauber_pfade
    # every spell whose wiki file exists gets an entry, even with unquoted ': ' in its frontmatter
    mit_datei = {p for p in zauber_pfade if p and (VAULT_ROOT / (p.partition('#')[0] + '.md')).is_file()}
    assert set(artikel) == mit_datei
    for pfad, art in artikel.items():
        assert set(art) == {'titel', 'quelle', 'meta', 'html'}, pfad
        assert art['html'].strip(), pfad


def test_build_context_zauber_artikel_skips_spells_without_article(tmp_path, monkeypatch):
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
    assert list(ctx['zauber_artikel']) == ['wiki/dsa-4.1/zauber/da']
    assert ctx['zauber_artikel']['wiki/dsa-4.1/zauber/da']['titel'] == 'DA'


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


def test_render_zauber_artikel_details_one_per_spell_with_article(live_html):
    ctx = build_context('illaen-baernhold')
    erwartet = sum(1 for z in ctx['held']['zauber'] if z.get('wiki_path') in ctx['zauber_artikel'])
    assert erwartet
    assert live_html.count('class="artikel-details"') == erwartet
    parents = _artikel_details_parents(_spell_list_fragment(live_html))
    assert len(parents) == erwartet
    # direktes Kind der Zeile (wandert beim Sortieren mit), Zeile direkt im Listen-Wrapper
    assert all(p == (('div', 'spell'), ('div', True)) for p in parents)


def test_render_zauber_artikel_empty_or_missing_has_no_details_but_keeps_name_links():
    ctx = build_context('illaen-baernhold')
    ctx['zauber_artikel'] = {}
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 0
    assert 'class="nlink"' in html
    del ctx['zauber_artikel']
    html = render_dashboard(ctx)
    assert html.count('class="artikel-details"') == 0
    assert 'class="nlink"' in html


def test_render_zauber_artikel_escapes_text_fields_but_not_html():
    ctx = build_context('illaen-baernhold')
    pfad = _first_wiki_path(ctx)
    ctx['zauber_artikel'] = {pfad: {
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


def test_render_zauber_artikel_has_single_obsidian_link_without_nlink(live_html):
    block = re.search(r'<details class="artikel-details">.*?</details>', live_html, re.S).group(0)
    kopf = re.search(r'<div class="artikel-kopf">.*?</div>', block, re.S).group(0)
    assert kopf.count('href="obsidian://') == 1
    assert re.search(r'<a class="artikel-obsidian" href="obsidian://[^"]+">↗ Obsidian</a>', kopf)
    assert 'nlink' not in block
    # der ↗ am Zaubernamen bleibt Sache des Namenslinks in .name (CSS ::after)
    row = live_html[:live_html.index('class="artikel-details"')]
    assert row.rindex('class="nlink"') > row.rindex('<div class="spell"')


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
    prints = ''.join(_media_blocks(css, r'@media\s+print'))
    assert re.search(r'\.artikel-panel\s*\{[^}]*background\s*:\s*transparent', prints)
    assert re.search(r'\.artikel-details\[open\]\s*\)\s*\{[^}]*break-inside\s*:\s*auto', prints)


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
