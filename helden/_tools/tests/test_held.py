"""Tests for parsers.held wikilink helpers (WIKILINK_RE, extract_wiki_path, strip_wikilink)."""
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from parsers.held import WIKILINK_RE, extract_wiki_path, parse_md_table, strip_wikilink

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
