"""Tests for CSS bundling in rendering.py."""
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from rendering import CSS_FILES, STATIC_DIR, css_bundle, make_env


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
TAB_PARTIALS = ['kampf', 'talente', 'zauber', 'steigern', 'inventar', 'profil', 'journal', 'sprachen']


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
    assert 'class="tab-content" id="tab-' not in _dashboard_source()
