"""Tests fuer tests/jsfixtures.py: die gemeinsamen Helfer tragen drei Testdateien und brauchen einen eigenen Boden."""
import pytest

from tests.jsfixtures import js_function, js_function_body, needs_node, run_node

SRC = 'var x = 1;\nfunction f(a, b){ if (a) { b; } }\nfunction fooBar(){ return 1; }\n'


def test_js_function_returns_whole_function_text():
    assert js_function(SRC, 'f') == 'function f(a, b){ if (a) { b; } }'


def test_js_function_body_returns_params_and_exact_body():
    # exakte Gleichheit: ein Off-by-one an der schliessenden Klammer faellt hier auf
    assert js_function_body(SRC, 'f') == ('a, b', ' if (a) { b; } ')


def test_js_function_matches_whole_name_only():
    assert js_function(SRC, 'fooBar') == 'function fooBar(){ return 1; }'
    with pytest.raises(AssertionError, match='foo fehlt'):
        js_function(SRC, 'foo')


def test_missing_function_asserts_with_its_name():
    with pytest.raises(AssertionError, match='g fehlt'):
        js_function_body(SRC, 'g')


def test_unbalanced_braces_assert_instead_of_looping():
    with pytest.raises(AssertionError, match='nicht ausgeglichen'):
        js_function('function f(){ { }', 'f')


@needs_node
def test_run_node_returns_parsed_json_and_passes_args_as_strings():
    assert run_node('console.log(JSON.stringify(process.argv.slice(1)))', 'a', 3) == ['a', '3']


@needs_node
def test_run_node_failing_script_reports_stderr():
    with pytest.raises(AssertionError, match='boom'):
        run_node("throw new Error('boom')")
