"""Render tests for the Chronik tab partial (synthetic context, independent of the live vault)."""
import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from rendering import make_env

PREFIX = '/chronik-bild/'


def _abend(datum, ig_tage):
    return {'datum': datum, 'ig_tage': ig_tage}


def _tag(bloecke, ig_datum=None):
    return {'ig_datum': ig_datum, 'bloecke': bloecke}


def _chronik(spielabende=None, meta=None):
    return {'spielabende': spielabende or [], 'meta': meta or {}}


SESSION = {
    'nr': 3, 'datum': '2026-05-01', 'datei': '2026-05-01-session-03.md',
    'sektionen': {'Verlauf': 'Wir zogen los.', 'Zusammenfassung': 'Kurz.'},
}


def render(chronik, sessions=None, prefix=PREFIX):
    tpl = make_env().get_template('partials/chronik.j2')
    return tpl.render(chronik=chronik, chronik_bild_prefix=prefix,
                      kampagne={'sessions': sessions if sessions is not None else []})


def roh_view(html):
    start = html.index('id="chronik-view-roh"')
    end = html.index('id="chronik-view-kompiliert"')
    return html[start:end]


def kompiliert_view(html):
    start = html.index('id="chronik-view-kompiliert"')
    end = html.find('id="chronik-view-register"', start)
    return html[start:] if end == -1 else html[start:end]


def register_view(html):
    return html[html.index('id="chronik-view-register"'):html.index('<!-- end tab-chronik -->')]


def test_empty_chronik_shows_empty_state_without_details():
    roh = roh_view(render(_chronik()))
    assert 'Noch keine Chronik importiert' in roh
    assert 'chronik_import.py' in roh
    assert '<details' not in roh


def test_newest_abend_first_and_only_newest_open():
    chronik = _chronik(spielabende=[
        _abend('01.01.2026', [_tag([{'typ': 'text', 'text': 'alt'}])]),
        _abend('08.01.2026', [_tag([{'typ': 'text', 'text': 'neu'}])]),
    ])
    roh = roh_view(render(chronik))
    assert roh.index('08.01.2026') < roh.index('01.01.2026')
    assert len(re.findall(r'<details\b[^>]*\bopen\b', roh)) == 1
    assert roh.count('chronik-abend') == 2
    assert re.search(r'<details[^>]*\bopen\b[^>]*>\s*<summary[^>]*>.*?08\.01\.2026', roh, re.S)


def test_all_block_types_render_with_classes():
    blocks = [
        {'typ': 'szene', 'text': 'Am Tor'},
        {'typ': 'text', 'text': 'Es regnete.'},
        {'typ': 'bullet', 'tiefe': 2, 'text': 'tiefer Punkt'},
        {'typ': 'bild', 'src': 'drachenchronik-daten/x.png'},
    ]
    roh = roh_view(render(_chronik(spielabende=[_abend('01.01.2026', [_tag(blocks)])])))
    assert '<h5 class="chronik-szene">Am Tor</h5>' in roh
    assert '<p class="chronik-text">Es regnete.</p>' in roh
    assert re.search(r'<div class="chronik-bullet" style="--tiefe: 2">\s*tiefer Punkt', roh)
    assert '<figure class="chronik-bild">' in roh
    assert '<img src="/chronik-bild/drachenchronik-daten/x.png"' in roh


def test_ig_datum_none_renders_no_heading_and_no_none_text():
    chronik = _chronik(spielabende=[_abend('01.01.2026', [
        _tag([{'typ': 'text', 'text': 'a'}], ig_datum=None),
    ])])
    roh = roh_view(render(chronik))
    assert 'chronik-igtag-datum' not in roh
    assert 'None' not in roh
    assert 'class="chronik-igtag"' in roh


def test_ig_datum_set_renders_heading():
    chronik = _chronik(spielabende=[_abend('01.01.2026', [
        _tag([{'typ': 'text', 'text': 'a'}], ig_datum='1. Praios 1040 BF'),
    ])])
    roh = roh_view(render(chronik))
    assert '<h4 class="chronik-igtag-datum">1. Praios 1040 BF</h4>' in roh
    assert 'None' not in roh


def test_bild_src_is_url_encoded():
    blocks = [{'typ': 'bild', 'src': 'drachenchronik-daten/mein bild #1.png'}]
    roh = roh_view(render(_chronik(spielabende=[_abend('01.01.2026', [_tag(blocks)])])))
    assert 'mein%20bild%20%231.png' in roh
    assert 'mein bild' not in roh
    assert '#1.png' not in roh


def test_user_content_is_escaped():
    blocks = [
        {'typ': 'text', 'text': '<script>alert(1)</script>'},
        {'typ': 'szene', 'text': '<b>szene</b>'},
        {'typ': 'bullet', 'tiefe': 0, 'text': '<i>bullet</i>'},
        {'typ': 'bild', 'src': 'x.png" onerror="alert(1)'},
    ]
    chronik = _chronik(
        spielabende=[_abend('<u>01.01.2026</u>', [_tag(blocks, ig_datum='<s>IG</s>')])],
        meta={'<h1>Kopf</h1>': '<script>meta()</script>'},
    )
    html = render(chronik)
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '<script' not in html
    for raw in ('<b>szene', '<i>bullet', '<u>01', '<s>IG', '<h1>Kopf', '<script>meta'):
        assert raw not in html, raw
    assert 'onerror="' not in html
    assert '&lt;h1&gt;Kopf&lt;/h1&gt;' in html
    assert '&lt;script&gt;meta()&lt;/script&gt;' in html


def test_bullet_tiefe_is_coerced_to_int():
    blocks = [{'typ': 'bullet', 'tiefe': '2"><script>x</script>', 'text': 't'}]
    html = render(_chronik(spielabende=[_abend('01.01.2026', [_tag(blocks)])]))
    assert '<script' not in html
    assert 'style="--tiefe: 0"' in html


def test_meta_sections_after_abende_and_empty_text_skipped():
    chronik = _chronik(
        spielabende=[_abend('01.01.2026', [_tag([{'typ': 'text', 'text': 'x'}])])],
        meta={'Nützliche SF': 'Wuchtschlag\nFinte', 'Leer': '', 'Nur Blanks': '  \n '},
    )
    roh = roh_view(render(chronik))
    assert roh.index('01.01.2026') < roh.index('Nützliche SF')
    assert '<h3 class="card-title">Nützliche SF</h3>' in roh
    assert 'Wuchtschlag\nFinte' in roh
    assert roh.count('chronik-meta"') == 1
    assert 'Leer' not in roh
    assert 'Nur Blanks' not in roh


def test_kompiliert_view_includes_journal_markup_when_sessions_present():
    html = render(_chronik(), sessions=[SESSION])
    komp = kompiliert_view(html)
    assert 'journal-session' in komp
    assert 'Wir zogen los.' in komp
    assert 'Noch keine Sessions gespielt' not in komp


def test_kompiliert_view_empty_state_without_sessions():
    komp = kompiliert_view(render(_chronik(), sessions=[]))
    assert 'Noch keine Sessions gespielt' in komp
    assert 'journal-session' not in komp


def test_roh_view_is_read_only():
    chronik = _chronik(
        spielabende=[_abend('01.01.2026', [_tag([{'typ': 'text', 'text': 'x'}])])],
        meta={'A': 'b'},
    )
    html = render(chronik, sessions=[SESSION])
    roh = roh_view(html)
    for forbidden in ('<textarea', 'journal-save-btn', '<button', '<input', '<form', 'contenteditable'):
        assert forbidden not in roh, forbidden
    assert '<textarea' in kompiliert_view(html)


def test_default_view_is_roh():
    html = render(_chronik(), sessions=[SESSION])
    roh_tag = re.search(r'<div[^>]*id="chronik-view-roh"[^>]*>', html).group(0)
    komp_tag = re.search(r'<div[^>]*id="chronik-view-kompiliert"[^>]*>', html).group(0)
    assert 'chronik-view--active' in roh_tag
    assert 'chronik-view--active' not in komp_tag
    roh_btn = re.search(r'<button[^>]*data-view="roh"[^>]*>', html).group(0)
    komp_btn = re.search(r'<button[^>]*data-view="kompiliert"[^>]*>', html).group(0)
    assert 'chronik-switch-btn--active' in roh_btn and 'aria-selected="true"' in roh_btn
    assert 'chronik-switch-btn--active' not in komp_btn and 'aria-selected="false"' in komp_btn


def test_partial_wrapper_and_header():
    html = render(_chronik())
    assert html.lstrip().startswith('<div class="tab-content" id="tab-chronik">')
    assert '<h2>📜 Chronik</h2>' in html
    assert html.rstrip().endswith('</div><!-- end tab-chronik -->')
