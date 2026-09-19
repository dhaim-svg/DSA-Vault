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


def render(chronik, sessions=None, prefix=PREFIX, register=None):
    tpl = make_env().get_template('partials/chronik.j2')
    ctx = {'chronik': chronik, 'chronik_bild_prefix': prefix,
           'kampagne': {'sessions': sessions if sessions is not None else []}}
    if register is not None:
        ctx['register'] = register
    return tpl.render(**ctx)


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


def _eintrag(name, unsicher=False, qualifier='', sessions=None, erwaehnungen=None, such=None):
    erwaehnungen = erwaehnungen if erwaehnungen is not None else []
    return {
        'name': name, 'unsicher': unsicher, 'qualifier': qualifier,
        'sessions': sessions if sessions is not None else [],
        'erwaehnungen': erwaehnungen,
        'such': such if such is not None else ' '.join([name, qualifier] + [e['text'] for e in erwaehnungen]).lower(),
    }


REGISTER = {
    'nscs': [
        _eintrag('Richesa Bolongaro', qualifier='Händlerin', sessions=['1', '3'],
                 erwaehnungen=[{'nr': '1', 'text': 'Traf uns am Tor.'}, {'nr': '3', 'text': 'Wieder da.'}],
                 such='richesa bolongaro handlerin traf uns am tor. wieder da.'),
        _eintrag('Unklarer Kerl', unsicher=True, sessions=['2'],
                 erwaehnungen=[{'nr': '', 'text': 'Ohne Nummer.'}, {'nr': '2', 'text': ''}]),
    ],
    'orte': [_eintrag('Havena', sessions=['1'], erwaehnungen=[{'nr': '1', 'text': 'Hafenstadt.'}])],
}


def test_switch_has_three_buttons_in_order():
    html = render(_chronik(), register=REGISTER)
    assert re.findall(r'<button[^>]*data-view="(\w+)"', html) == ['roh', 'kompiliert', 'register']
    btn = re.search(r'<button[^>]*data-view="register"[^>]*>', html).group(0)
    assert 'role="tab"' in btn and 'aria-selected="false"' in btn
    assert 'aria-controls="chronik-view-register"' in btn
    assert 'chronik-switch-btn--active' not in btn


def test_register_button_count_is_nscs_plus_orte():
    html = render(_chronik(), register=REGISTER)
    btn = re.search(r'<button[^>]*data-view="register"[^>]*>(.*?)</button>', html, re.S).group(1)
    assert re.search(r'Register\s*<span class="chronik-switch-count">3</span>', btn)


def test_register_view_panel_follows_kompiliert_and_is_inactive():
    html = render(_chronik(), register=REGISTER)
    assert html.index('id="chronik-view-kompiliert"') < html.index('id="chronik-view-register"')
    tag = re.search(r'<div[^>]*id="chronik-view-register"[^>]*>', html).group(0)
    assert 'data-view="register"' in tag and 'role="tabpanel"' in tag
    assert 'chronik-view--active' not in tag
    assert html.count('id="chronik-view-register"') == 1


def test_register_view_renders_entries():
    reg = register_view(render(_chronik(), register=REGISTER))
    assert '<input type="search" class="register-suche"' in reg
    assert 'aria-label="Register durchsuchen"' in reg
    assert 'class="register-zaehler"' in reg and 'aria-live="polite"' in reg
    assert len(re.findall(r'<section class="card register-gruppe"', reg)) == 2
    assert 'data-gruppe="nsc"' in reg and 'data-gruppe="ort"' in reg
    assert len(re.findall(r'<article class="register-eintrag"', reg)) == 3
    assert '<h4 class="register-name">Richesa Bolongaro' in reg
    assert 'Händlerin' in reg
    assert 'data-such="richesa bolongaro handlerin traf uns am tor. wieder da."' in reg
    assert len(re.findall(r'class="register-chip"', reg)) == 4
    assert 'S1' in reg and 'S3' in reg
    assert 'Traf uns am Tor.' in reg and 'Hafenstadt.' in reg
    assert re.search(r'<p class="register-leer" hidden>Keine Treffer\.</p>', reg)


def test_register_group_counts_are_totals():
    reg = register_view(render(_chronik(), register=REGISTER))
    counts = re.findall(r'<span class="register-count">(\d+)</span>', reg)
    assert counts == ['2', '1']


def test_register_unsicher_badge_only_for_unsichere_eintraege():
    reg = register_view(render(_chronik(), register=REGISTER))
    assert reg.count('class="register-unsicher"') == 1
    assert re.search(r'<span class="register-unsicher" title="unsichere Lesart">\(\?\)</span>', reg)
    unsicher_pos = reg.index('register-unsicher')
    assert reg.index('Unklarer Kerl') < unsicher_pos < reg.index('Havena')


def test_register_erwaehnungen_skip_empty_text_and_omit_empty_nr():
    reg = register_view(render(_chronik(), register=REGISTER))
    kerl = reg[reg.index('Unklarer Kerl'):reg.index('Havena')]
    assert len(re.findall(r'<li\b', kerl)) == 1
    assert 'Ohne Nummer.' in kerl
    assert not re.search(r'<li[^>]*>\s*S\s*Ohne', kerl)
    richesa = reg[reg.index('Richesa'):reg.index('Unklarer Kerl')]
    assert len(re.findall(r'<li\b', richesa)) == 2
    assert re.search(r'<li[^>]*>\s*(?:<[^>]+>)?S3(?:</[^>]+>)?\s*Wieder da\.', richesa)


def test_register_user_content_is_escaped():
    evil = '<script>alert(1)</script>'
    reg_data = {
        'nscs': [_eintrag(evil, unsicher=True, qualifier=evil, sessions=[evil],
                          erwaehnungen=[{'nr': evil, 'text': evil}],
                          such='x" onmouseover="y')],
        'orte': [_eintrag('Ort', qualifier='<b>q</b>', such=evil)],
    }
    html = render(_chronik(), register=reg_data)
    assert '<script' not in html
    assert '&lt;script&gt;alert(1)&lt;/script&gt;' in html
    assert '<b>q' not in html
    assert '" onmouseover="' not in html
    assert 'data-such="x&#34; onmouseover=&#34;y"' in html
    assert 'data-such="&lt;script&gt;' in html


def test_render_without_register_shows_empty_state():
    html = render(_chronik())
    reg = register_view(html)
    assert 'register-suche' not in reg and 'register-eintrag' not in reg
    assert 'session-compile' in reg
    assert 'None' not in html
    assert re.search(r'Register\s*<span class="chronik-switch-count">0</span>', html)


def test_register_group_without_entries_is_not_rendered():
    reg = register_view(render(_chronik(), register={'nscs': REGISTER['nscs'], 'orte': []}))
    assert 'data-gruppe="nsc"' in reg
    assert 'data-gruppe="ort"' not in reg
    assert 'register-suche' in reg


def test_render_with_empty_register_shows_empty_state():
    reg = register_view(render(_chronik(), register={'nscs': [], 'orte': []}))
    assert 'register-suche' not in reg
    assert 'session-compile' in reg


def test_kompiliert_view_does_not_leak_register():
    html = render(_chronik(), sessions=[SESSION], register=REGISTER)
    komp = kompiliert_view(html)
    assert 'register-suche' not in komp
    assert 'register-eintrag' not in komp
    assert 'journal-session' in komp
    assert 'register-suche' not in roh_view(html)
