"""Tests for git_ops.commit_helden and the /api/commit Flask route."""
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
            resp = client.post('/api/commit')
            assert resp.status_code in (200, 500)
            data = resp.get_json()
            assert data is not None
            assert 'ok' in data
    finally:
        server_mod.VAULT_ROOT = original_vault_root
