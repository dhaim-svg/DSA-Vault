"""Tests for git_ops.commit_helden and the /api/commit Flask route."""
import logging
import re
import subprocess
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from git_ops import commit_helden


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_repo(path: Path) -> None:
    """Initialise a minimal git repo with user config."""
    subprocess.run(['git', 'init', str(path)], capture_output=True, check=True)
    subprocess.run(
        ['git', '-C', str(path), 'config', 'user.email', 'test@test.com'],
        capture_output=True, check=True,
    )
    subprocess.run(
        ['git', '-C', str(path), 'config', 'user.name', 'Test'],
        capture_output=True, check=True,
    )


def _write_helden_file(repo: Path, slug: str, content: str = 'test') -> Path:
    """Create a file inside helden/<slug>/ and return its path."""
    target = repo / 'helden' / slug / 'test.md'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    return target


def _rev_count(repo: Path) -> int:
    """Number of commits reachable from HEAD (0 if there is no HEAD yet)."""
    result = subprocess.run(
        ['git', '-C', str(repo), 'rev-list', '--count', 'HEAD'],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return 0
    return int(result.stdout.strip())


# ---------------------------------------------------------------------------
# Unit tests: commit_helden
# ---------------------------------------------------------------------------

def test_commit_helden_success(tmp_path):
    """A staged file inside helden/ should result in a successful commit."""
    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'test-held')

    result = commit_helden(tmp_path, 'test-held')

    assert result['ok'] is True
    assert result['committed'] is True
    assert result['message'].startswith('dashboard: test-held')


def test_commit_helden_nothing_to_commit(tmp_path):
    """After an initial commit with no new changes, committed should be False."""
    _init_repo(tmp_path)
    f = _write_helden_file(tmp_path, 'test-held')

    # Make an initial commit so the repo is not empty and helden/ is tracked
    subprocess.run(
        ['git', '-C', str(tmp_path), 'add', 'helden/'],
        capture_output=True, check=True,
    )
    subprocess.run(
        ['git', '-C', str(tmp_path), 'commit', '-m', 'initial'],
        capture_output=True, check=True,
    )

    # No new changes — commit_helden should detect nothing to commit
    result = commit_helden(tmp_path, 'test-held')

    assert result['ok'] is True
    assert result['committed'] is False
    assert result['message'] == 'nothing to commit'


def test_commit_helden_adds_helden_subpath(tmp_path):
    """The commit should only include files from the helden/ subtree."""
    _init_repo(tmp_path)

    # Create a file in helden/ AND one outside it
    _write_helden_file(tmp_path, 'test-held')
    other = tmp_path / 'wiki' / 'notes.md'
    other.parent.mkdir(parents=True, exist_ok=True)
    other.write_text('outside helden', encoding='utf-8')

    result = commit_helden(tmp_path, 'test-held')
    assert result['ok'] is True
    assert result['committed'] is True

    # Inspect the committed files
    log = subprocess.run(
        ['git', '-C', str(tmp_path), 'show', '--name-only', '--format=', 'HEAD'],
        capture_output=True, text=True, check=True,
    )
    committed_files = [line.strip() for line in log.stdout.splitlines() if line.strip()]

    # Only the helden/ file should be in the commit
    assert all(f.startswith('helden/') for f in committed_files), (
        f"Expected only helden/ paths, got: {committed_files}"
    )
    # The wiki file should NOT be committed
    assert not any('wiki' in f for f in committed_files)


def test_api_commit_route_returns_json(tmp_path):
    """The /api/commit route should return JSON with an 'ok' key."""
    import importlib
    import types

    # Patch VAULT_ROOT in server to point to our tmp git repo
    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    # Import server fresh so we can patch VAULT_ROOT
    import server as server_mod
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            resp = client.post('/api/commit', json={})
            assert resp.status_code in (200, 500)
            data = resp.get_json()
            assert data is not None
            assert 'ok' in data
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_commit_route_does_not_leak_path_on_git_failure(tmp_path):
    """A git failure (stale index.lock) must not leak the vault's absolute
    path into the HTTP error response (D-064)."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    # Force a real git failure whose raw stderr contains the absolute path:
    # a stale index.lock makes `git add` (and if not, `git commit`) fail
    # with "fatal: Unable to create '<path>/.git/index.lock': File exists."
    lock_file = tmp_path / '.git' / 'index.lock'
    lock_file.write_text('', encoding='utf-8')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            resp = client.post('/api/commit', json={})
            body = resp.get_data(as_text=True)

            assert resp.status_code == 500
            data = resp.get_json()
            assert data['ok'] is False
            assert data['error'] == 'git operation failed'

            # Neither the raw path text nor a Windows drive-letter path
            # pattern may appear in the response body. Both checks are
            # required: the plain substring check alone passes vacuously
            # on Windows (git's stderr uses forward slashes, so it never
            # matches str(tmp_path)'s backslashes) -- only the drive-letter
            # regex actually discriminates (Sprint 031/D-063 lesson).
            assert str(tmp_path) not in body
            assert not re.search(r'[A-Za-z]:[\\/]', body)
    finally:
        server_mod.VAULT_ROOT = original_vault_root
        lock_file.unlink(missing_ok=True)


def test_api_commit_route_logs_git_failure_without_leaking_path(tmp_path, caplog):
    """D-066: the swallowed git failure (stale index.lock, same trigger as
    D-064 above) must reach the server log with the full detail incl. the
    tmp_path-derived absolute path, while the JSON response body stays the
    generic {'ok': False, 'error': 'git operation failed'} it already was."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    lock_file = tmp_path / '.git' / 'index.lock'
    lock_file.write_text('', encoding='utf-8')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            with caplog.at_level(logging.WARNING):
                resp = client.post('/api/commit', json={})
            body = resp.get_data(as_text=True)

            assert resp.status_code == 500
            assert resp.get_json() == {'ok': False, 'error': 'git operation failed'}

            assert str(tmp_path) not in body
            assert not re.search(r'[A-Za-z]:[\\/]', body)

            assert len(caplog.records) == 1
            assert caplog.records[0].levelno == logging.WARNING
            msg = caplog.records[0].getMessage()
            assert 'illaen-baernhold' in msg
            # str(tmp_path) itself is not a substring match on Windows: git's
            # stderr uses forward slashes, so tmp_path's backslash form never
            # occurs verbatim -- the folder name is the unambiguous,
            # slash-convention-proof detail marker (same lesson as D-064).
            assert tmp_path.name in msg
            assert 'index.lock' in msg
    finally:
        server_mod.VAULT_ROOT = original_vault_root
        lock_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# /api/commit — CSRF-Schutz (D-065)
# ---------------------------------------------------------------------------

def test_api_commit_route_rejects_non_json_body(tmp_path):
    """A non-JSON POST to /api/commit must be rejected with 415 and must not
    trigger a commit as a side effect."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            before = _rev_count(tmp_path)
            resp = client.post('/api/commit', content_type='text/plain', data='not json')
            assert resp.status_code == 415
            after = _rev_count(tmp_path)
            assert after == before
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_commit_route_logs_non_json_rejection(tmp_path, caplog):
    """D-066: the 415 non-JSON rejection must be logged with the offending
    content-type, while the JSON response body stays the generic
    {'ok': False, 'error': 'expected application/json'} it already was
    (D-065)."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            with caplog.at_level(logging.WARNING):
                resp = client.post('/api/commit', content_type='text/plain', data='not json')
            assert resp.status_code == 415
            assert resp.get_json() == {'ok': False, 'error': 'expected application/json'}

            assert len(caplog.records) == 1
            assert caplog.records[0].levelno == logging.WARNING
            msg = caplog.records[0].getMessage()
            assert 'text/plain' in msg
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_commit_route_rejects_foreign_origin(tmp_path):
    """A POST to /api/commit with a cross-origin Origin header must be
    rejected with 403 and must not trigger a commit."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            before = _rev_count(tmp_path)
            resp = client.post(
                '/api/commit',
                json={'message': 'x'},
                headers={'Origin': 'http://evil.example'},
            )
            assert resp.status_code == 403
            data = resp.get_json()
            assert 'error' in data
            after = _rev_count(tmp_path)
            assert after == before
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_commit_route_rejects_null_origin(tmp_path):
    """Browsers send the literal 'Origin: null' for some cross-origin/opaque
    contexts (e.g. sandboxed iframes, file:// pages) -- it must never match
    the expected same-origin value and so must be rejected with 403."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        with app.test_client() as client:
            before = _rev_count(tmp_path)
            resp = client.post(
                '/api/commit',
                json={'message': 'x'},
                headers={'Origin': 'null'},
            )
            assert resp.status_code == 403
            data = resp.get_json()
            assert 'error' in data
            after = _rev_count(tmp_path)
            assert after == before
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_commit_route_allows_same_origin(tmp_path):
    """A POST to /api/commit whose Origin header matches request.host_url
    must not be rejected by the CSRF hook (final status depends on whether
    the commit itself succeeds, which is not what this test checks)."""
    import server as server_mod

    _init_repo(tmp_path)
    _write_helden_file(tmp_path, 'illaen-baernhold')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        app = server_mod.create_app('illaen-baernhold')
        app.config['TESTING'] = True
        # Determine the test client's actual host_url empirically instead of
        # assuming Flask's documented default ('http://localhost/').
        with app.test_request_context('/'):
            from flask import request as flask_request
            expected_origin = flask_request.host_url.rstrip('/')
        with app.test_client() as client:
            resp = client.post(
                '/api/commit',
                json={'message': 'x'},
                headers={'Origin': expected_origin},
            )
            assert resp.status_code != 403
    finally:
        server_mod.VAULT_ROOT = original_vault_root
