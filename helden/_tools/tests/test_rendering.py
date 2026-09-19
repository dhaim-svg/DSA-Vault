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
    assert '<script src=' not in static_js_html
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
    assert tags == list(JS_FILES) and len(tags) == 11
    assert not re.search(r'/\* \w+\.js \*/', html)


def test_static_hinweis_banner_only_in_static_render(static_js_html):
    assert static_js_html.count('id="static-hinweis"') == 1
    assert 'nicht gespeichert' in static_js_html
    if not LIVE_HELD.exists():
        pytest.skip('Live-Vault ohne helden/illaen-baernhold')
    assert 'id="static-hinweis"' not in server._render_dashboard('illaen-baernhold')
    assert 'id="static-hinweis"' not in render_dashboard(build_context('illaen-baernhold'))
