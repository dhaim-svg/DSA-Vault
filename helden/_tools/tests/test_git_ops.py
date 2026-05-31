"""Tests for the optional custom-message parameter of commit_helden."""
import re
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

from git_ops import commit_helden


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_run(returncode=0, stdout='', stderr=''):
    """Return a mock subprocess.CompletedProcess-like object."""
    result = MagicMock()
    result.returncode = returncode
    result.stdout = stdout
    result.stderr = stderr
    return result


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_commit_helden_custom_message(tmp_path):
    """When a non-empty message is supplied, commit should use the em-dash format."""
    add_ok = _make_run(returncode=0)
    commit_ok = _make_run(returncode=0, stdout='[master abc1234] dashboard: illaen — My note')

    with patch('subprocess.run', side_effect=[add_ok, commit_ok]) as mock_run:
        result = commit_helden(tmp_path, 'illaen', message='My note')

    assert result == {'ok': True, 'committed': True, 'message': 'dashboard: illaen — My note'}

    # Verify the commit call used the expected message
    _commit_call = mock_run.call_args_list[1]
    cmd = _commit_call[0][0]  # positional first arg is the command list
    assert '-m' in cmd
    msg_index = cmd.index('-m') + 1
    assert cmd[msg_index] == 'dashboard: illaen — My note'


def test_commit_helden_auto_message_when_empty(tmp_path):
    """When message is '' or None, commit should fall back to the timestamp format."""
    timestamp_pattern = re.compile(r'^dashboard: illaen \d{4}-\d{2}-\d{2}T\d{2}:\d{2}$')

    for msg in ('', None):
        add_ok = _make_run(returncode=0)
        commit_ok = _make_run(returncode=0, stdout='[master abc1234] auto msg')

        with patch('subprocess.run', side_effect=[add_ok, commit_ok]) as mock_run:
            result = commit_helden(tmp_path, 'illaen', message=msg)

        assert result['ok'] is True
        assert result['committed'] is True
        assert timestamp_pattern.match(result['message']), (
            f"Expected timestamp pattern, got: {result['message']!r}"
        )

        # Verify the actual git call used the same timestamped message
        _commit_call = mock_run.call_args_list[1]
        cmd = _commit_call[0][0]
        msg_index = cmd.index('-m') + 1
        assert timestamp_pattern.match(cmd[msg_index]), (
            f"Git commit called with unexpected message: {cmd[msg_index]!r}"
        )
