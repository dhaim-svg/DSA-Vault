"""git_ops.py — Git operations for the DSA hero dashboard.

Provides commit_helden() to stage helden/ and commit with an auto-generated message.
Never pushes to remote.
"""
import datetime
import subprocess
from pathlib import Path


def commit_helden(vault_root: Path, slug: str) -> dict:
    """Stage helden/ and commit with an auto-generated message.

    Args:
        vault_root: Path to the git repository root (the vault directory).
        slug: Hero slug used in the commit message.

    Returns:
        On success (changes committed):
            {'ok': True, 'committed': True, 'message': <commit message>}
        On nothing-to-commit:
            {'ok': True, 'committed': False, 'message': 'nothing to commit'}
        On git error:
            {'ok': False, 'error': <stderr text>}
    """
    root = str(vault_root)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M')
    commit_msg = f'dashboard: {slug} {timestamp}'

    # Step 1: stage helden/
    add_result = subprocess.run(
        ['git', '-C', root, 'add', 'helden/'],
        capture_output=True,
        text=True,
    )
    if add_result.returncode != 0:
        return {'ok': False, 'error': add_result.stderr or add_result.stdout}

    # Step 2: commit
    commit_result = subprocess.run(
        ['git', '-C', root, 'commit', '-m', commit_msg],
        capture_output=True,
        text=True,
    )

    if commit_result.returncode == 0:
        return {'ok': True, 'committed': True, 'message': commit_msg}

    # git commit exits with code 1 when there is nothing to commit
    combined = (commit_result.stdout or '') + (commit_result.stderr or '')
    if 'nothing to commit' in combined:
        return {'ok': True, 'committed': False, 'message': 'nothing to commit'}

    return {'ok': False, 'error': commit_result.stderr or commit_result.stdout}
