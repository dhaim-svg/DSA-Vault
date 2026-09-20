"""Tests for parsers.held wikilink helpers (WIKILINK_RE, extract_wiki_path, strip_wikilink)."""
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import WIKILINK_RE, extract_wiki_path, load_held, parse_md_table, strip_wikilink
from tests.heldfixtures import MINI_SLUG, write_mini_held

MK_PFAD = 'wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Merkmalskenntnis [einzelnes Merkmal]'
# One backslash before the pipe, exactly as in the markdown table (Obsidian escapes | inside tables).
MK_LINK = '[[' + MK_PFAD + r'\|Merkmalskenntnis: Eigenschaften]]'


def test_extract_wiki_path_keeps_bracket_in_anchor():
    assert extract_wiki_path(MK_LINK) == MK_PFAD


def test_strip_wikilink_uses_display_text_for_bracket_anchor():
    assert strip_wikilink(MK_LINK) == 'Merkmalskenntnis: Eigenschaften'


@pytest.mark.parametrize('link, path, display', [
    ('[[a/b]]', 'a/b', None),
    ('[[a/b|Text]]', 'a/b', 'Text'),
    (r'[[a/b\|Text]]', 'a/b', 'Text'),
    ('[[a/b#Anker|Text]]', 'a/b#Anker', 'Text'),
    (r'[[a/b#Anker (mit / Klammern)\|Text]]', 'a/b#Anker (mit / Klammern)', 'Text'),
])
def test_unchanged_link_forms(link, path, display):
    m = WIKILINK_RE.fullmatch(link)
    assert m is not None
    assert m.group(1) == path
    assert m.group(2) == display
    assert extract_wiki_path(link) == path


def test_multiple_links_are_matched_separately():
    text = '[[a|A]] und [[b#X [y]|B]]'
    assert WIKILINK_RE.findall(text) == [('a', 'A'), ('b#X [y]', 'B')]
    assert [m.group(0) for m in WIKILINK_RE.finditer(text)] == ['[[a|A]]', '[[b#X [y]|B]]']


def test_link_without_display_stops_at_its_own_closing_brackets():
    text = '[[a/b]] und [[c/d]]'
    assert [m.group(1) for m in WIKILINK_RE.finditer(text)] == ['a/b', 'c/d']


def test_unclosed_double_bracket_does_not_swallow_following_link():
    matches = list(WIKILINK_RE.finditer('Text [[unfertig und [[a/b|A]]'))
    assert len(matches) == 1
    assert matches[0].group(1) == 'a/b'
    assert matches[0].group(2) == 'A'


def test_unclosed_double_bracket_without_display_does_not_swallow_following_link():
    matches = list(WIKILINK_RE.finditer('[[kaputt und [[c/d]] Rest'))
    assert len(matches) == 1
    assert matches[0].group(1) == 'c/d'


@pytest.mark.parametrize('text', [
    '[[a|x [[b]]',       # display text of the first link never closes; '[[' starts the real link
    r'[[a\|x [[b]]',     # same with the table-escaped pipe
    '[[a|x [[b]] Rest',
])
def test_unclosed_double_bracket_in_display_text_does_not_swallow_following_link(text):
    matches = list(WIKILINK_RE.finditer(text))
    assert [m.group(0) for m in matches] == ['[[b]]']
    assert matches[0].group(1) == 'b'
    assert matches[0].group(2) is None


def test_unclosed_double_bracket_in_display_text_before_link_with_display():
    matches = list(WIKILINK_RE.finditer('[[a|x [[b|B]] Rest'))
    assert [(m.group(1), m.group(2)) for m in matches] == [('b', 'B')]


def test_helpers_ignore_unclosed_display_text_before_real_link():
    text = '[[a|x [[b]]'
    assert extract_wiki_path(text) == 'b'
    assert strip_wikilink(text) == '[[a|x b'


@pytest.mark.parametrize('link, display', [
    ('[[a|x [y]]', 'x [y'),      # single '[' stays part of the display text
    ('[[a|[x]]', '[x'),
    ('[[a|x[]]', 'x['),
    (r'[[a\|x [y]]', 'x [y'),
])
def test_single_bracket_in_display_text_is_kept(link, display):
    m = WIKILINK_RE.fullmatch(link)
    assert m is not None
    assert m.group(1) == 'a'
    assert m.group(2) == display


def test_unclosed_double_bracket_without_later_link_does_not_match():
    assert WIKILINK_RE.search('Text [[unfertig und nichts mehr') is None
    # no real link behind the stray '[[': the old regex swallowed 'a [[' up to the ']]' here
    assert WIKILINK_RE.search('x [[a [[]] y') is None


def test_helpers_ignore_unclosed_double_bracket_before_real_link():
    text = '[[unfertig [[a/b|A]]'
    assert extract_wiki_path(text) == 'a/b'
    # The unclosed '[[' stays as plain text; only the real link is replaced by its display text.
    assert strip_wikilink(text) == '[[unfertig A'


def test_sf_table_rows_with_bracket_anchor_get_wiki_path():
    table = '\n'.join([
        '| Sonderfertigkeit | Beschreibung / Nutzen |',
        '|---|---|',
        '| [[' + MK_PFAD + r'\|Merkmalskenntnis: Eigenschaften]] | Sprüche des Merkmals |',
        '| [[' + MK_PFAD + r'\|Merkmalskenntnis: Schaden]] | Sprüche des Merkmals |',
        '| [[wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Aufmerksamkeit\\|Aufmerksamkeit]] | x |',
    ])
    rows = parse_md_table(table)
    assert [extract_wiki_path(r['Sonderfertigkeit']) for r in rows] == [
        MK_PFAD, MK_PFAD,
        'wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Aufmerksamkeit',
    ]
    assert [strip_wikilink(r['Sonderfertigkeit']) for r in rows] == [
        'Merkmalskenntnis: Eigenschaften', 'Merkmalskenntnis: Schaden', 'Aufmerksamkeit',
    ]


# --- Ritual-Zeilen mit Anker-Link (Sprint 023 T6, L25(b); Sprint 024 T2, D-051) -----------------------------------
# Der Heldenbogen verlinkt die Ritual-Namen mit Anker auf stabzauber.md. Anzeigetext und alle übrigen Felder bleiben
# davon unberührt (load_held führt den Link über strip_wikilink auf den Anzeigetext zurück); NEU seit D-051: der Link
# speist zusätzlich `wiki_path` (Pfad inkl. #Anker, sonst None) für die Ritual-Artikelvorschau. `wiki_path` kommt
# ausschließlich aus der Namensspalte, nie aus der Effekt-Spalte. Synthetisch, kein Live-Bogen.

STABZAUBER_KOPF = """## Stabzauber (2 Rituale)

Alle Stabzauber sind an den gebundenen Magierstab geknüpft.

| Stabzauber | Erschaffungsprobe | AsP | Vol | Effekt (Kurzform) |
|---|---|---|---|---|
"""
STABZAUBER_ZEILE = '| {name} | KL / KL / FF (+4) | 23 | 2 | Stab leuchtet auf Kommando |\n'
STABZAUBER_LEERE_ZEILE = '| {name} |  |  | ? | Stab verlängert sich auf Befehl |\n'
FACKEL_LINK = r'[[wiki/dsa-4.1/rituale/stabzauber#Ewige Flamme\|Stabzauber: Fackel]]'
VERLAENGERUNG_LINK = r'[[wiki/dsa-4.1/rituale/stabzauber#Doppeltes Maß\|Stabzauber: Stabverlängerung]]'
FACKEL_PFAD = 'wiki/dsa-4.1/rituale/stabzauber#Ewige Flamme'
VERLAENGERUNG_PFAD = 'wiki/dsa-4.1/rituale/stabzauber#Doppeltes Maß'

ANDERE_KOPF = """## Andere Rituale

| Ritual | Effekt (Kurzform) |
|---|---|
"""
ANDERE_ZEILE = '| {name} | {effekt} |\n'
APPORT_LINK = r'[[wiki/dsa-4.1/rituale/stabzauber#Apport\|Apport]]'
APPORT_PFAD = 'wiki/dsa-4.1/rituale/stabzauber#Apport'
GRUNDREGELN_LINK = r'[[wiki/dsa-4.1/rituale/rituale-grundregeln\|Rituale Grundregeln]]'


def _mini_rituale(tmp_path, fackel, verlaengerung):
    text = (STABZAUBER_KOPF + STABZAUBER_ZEILE.format(name=fackel)
            + STABZAUBER_LEERE_ZEILE.format(name=verlaengerung))
    return load_held(write_mini_held(tmp_path, rituale=text), MINI_SLUG)['rituale']


def _mini_andere(tmp_path, *zeilen):
    """zeilen: (name, effekt)-Paare der Tabelle „Andere Rituale“; liefert rituale['andere']."""
    text = ANDERE_KOPF + ''.join(ANDERE_ZEILE.format(name=n, effekt=e) for n, e in zeilen)
    return load_held(write_mini_held(tmp_path, rituale=text), MINI_SLUG)['rituale']['andere']


def test_stabzauber_anchor_link_keeps_display_name_and_all_other_fields(tmp_path):
    # Seit D-051 kommt `wiki_path` hinzu; name/erschaffungsprobe/asp/vol/effekt sind weiterhin die Anzeigewerte.
    rituale = _mini_rituale(tmp_path, FACKEL_LINK, VERLAENGERUNG_LINK)
    assert rituale['stabzauber'] == [
        {'name': 'Stabzauber: Fackel', 'wiki_path': FACKEL_PFAD, 'erschaffungsprobe': 'KL / KL / FF (+4)',
         'asp': '23', 'vol': '2', 'effekt': 'Stab leuchtet auf Kommando'},
        {'name': 'Stabzauber: Stabverlängerung', 'wiki_path': VERLAENGERUNG_PFAD, 'erschaffungsprobe': '',
         'asp': '', 'vol': '?', 'effekt': 'Stab verlängert sich auf Befehl'},
    ]


def test_stabzauber_anchor_link_gives_the_same_rituale_dict_as_plain_name_except_wiki_path(tmp_path):
    verlinkt = _mini_rituale(tmp_path / 'verlinkt', FACKEL_LINK, VERLAENGERUNG_LINK)
    schlicht = _mini_rituale(tmp_path / 'schlicht', 'Stabzauber: Fackel', 'Stabzauber: Stabverlängerung')
    assert [z['wiki_path'] for z in verlinkt['stabzauber']] == [FACKEL_PFAD, VERLAENGERUNG_PFAD]
    assert [z['wiki_path'] for z in schlicht['stabzauber']] == [None, None]
    for tabelle in (verlinkt, schlicht):
        for z in tabelle['stabzauber']:
            del z['wiki_path']
    assert verlinkt == schlicht


def test_stabzauber_plain_name_has_wiki_path_none(tmp_path):
    rituale = _mini_rituale(tmp_path, 'Stabzauber: Fackel', 'Stabzauber: Stabverlängerung')
    assert rituale['stabzauber'] == [
        {'name': 'Stabzauber: Fackel', 'wiki_path': None, 'erschaffungsprobe': 'KL / KL / FF (+4)',
         'asp': '23', 'vol': '2', 'effekt': 'Stab leuchtet auf Kommando'},
        {'name': 'Stabzauber: Stabverlängerung', 'wiki_path': None, 'erschaffungsprobe': '',
         'asp': '', 'vol': '?', 'effekt': 'Stab verlängert sich auf Befehl'},
    ]


def test_stabzauber_mixed_linked_and_plain_rows_keep_order_and_count(tmp_path):
    rituale = _mini_rituale(tmp_path, FACKEL_LINK, 'Stabzauber: Stabverlängerung')
    assert [(z['name'], z['wiki_path']) for z in rituale['stabzauber']] == [
        ('Stabzauber: Fackel', FACKEL_PFAD),
        ('Stabzauber: Stabverlängerung', None),
    ]
    rituale = _mini_rituale(tmp_path / 'umgekehrt', 'Stabzauber: Fackel', VERLAENGERUNG_LINK)
    assert [(z['name'], z['wiki_path']) for z in rituale['stabzauber']] == [
        ('Stabzauber: Fackel', None),
        ('Stabzauber: Stabverlängerung', VERLAENGERUNG_PFAD),
    ]


def test_andere_ritual_name_link_gives_wiki_path_with_anchor(tmp_path):
    andere = _mini_andere(tmp_path, (APPORT_LINK, 'Telekinesezauber'))
    assert andere == [{'name': 'Apport', 'wiki_path': APPORT_PFAD, 'effekt': 'Telekinesezauber'}]


def test_andere_ritual_without_name_link_ignores_link_in_effect_column(tmp_path):
    # Falle: der Effekt trägt einen eigenen Link (Grundregeln). Er darf nie zu wiki_path werden – sonst würde eine
    # unverlinkte Namenszelle den falschen Ganzartikel einbetten.
    andere = _mini_andere(tmp_path, ('Apport', 'Telekinesezauber; Details → ' + GRUNDREGELN_LINK))
    assert andere == [{'name': 'Apport', 'wiki_path': None,
                       'effekt': 'Telekinesezauber; Details → Rituale Grundregeln'}]


def test_andere_ritual_name_link_wins_over_link_in_effect_column(tmp_path):
    andere = _mini_andere(tmp_path, (APPORT_LINK, 'Telekinesezauber; Details → ' + GRUNDREGELN_LINK))
    assert andere == [{'name': 'Apport', 'wiki_path': APPORT_PFAD,
                       'effekt': 'Telekinesezauber; Details → Rituale Grundregeln'}]


def test_andere_ritual_mixed_linked_and_plain_rows_keep_order_and_count(tmp_path):
    andere = _mini_andere(tmp_path, ('Erstes', 'a'), (APPORT_LINK, 'b'), ('Drittes', 'c'))
    assert [(r['name'], r['wiki_path']) for r in andere] == [
        ('Erstes', None), ('Apport', APPORT_PFAD), ('Drittes', None),
    ]
