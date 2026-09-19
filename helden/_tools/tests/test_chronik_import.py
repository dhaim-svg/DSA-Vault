"""Tests for chronik_import.py — one-way Drive -> Vault chronicle mirror.

All tests use tmp_path fixtures exclusively; never touch the real
Drive or vault paths.
"""
import os
import sys
import time
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import chronik_import
from chronik_import import import_chronik
from chronik_paths import CHRONIK_IMG_DIRNAME, CHRONIK_MD_NAME, chronik_dir


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _paths(tmp_path):
    """Return (source_md, source_img_dir, target_md, target_img_dir) under tmp_path."""
    source_md = tmp_path / 'drive' / 'Drachenchronik.md'
    source_img_dir = tmp_path / 'drive' / 'drachenchronik-daten'
    target_md = tmp_path / 'vault' / 'abenteuer' / 'drachenchronik' / 'chronik.md'
    target_img_dir = tmp_path / 'vault' / 'abenteuer' / 'drachenchronik' / 'drachenchronik-daten'
    return source_md, source_img_dir, target_md, target_img_dir


# ---------------------------------------------------------------------------
# Markdown copy
# ---------------------------------------------------------------------------

def test_first_import_creates_target_with_source_content(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\nZeile 2\nZeile 3\n', encoding='utf-8')

    result = import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert target_md.exists()
    assert target_md.read_text(encoding='utf-8') == source_md.read_text(encoding='utf-8')
    assert result['lines_before'] == 0
    assert result['lines_after'] == 3


def test_second_import_overwrites_and_reports_line_delta(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\nZeile 2\nZeile 3\n', encoding='utf-8')
    import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    # Source shrinks — delta should be allowed to be negative.
    source_md.write_text('Nur eine Zeile\n', encoding='utf-8')
    result = import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert target_md.read_text(encoding='utf-8') == 'Nur eine Zeile\n'
    assert result['lines_before'] == 3
    assert result['lines_after'] == 1
    assert result['lines_after'] - result['lines_before'] == -2


def test_missing_source_raises_file_not_found(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)

    with pytest.raises(FileNotFoundError):
        import_chronik(source_md, source_img_dir, target_md, target_img_dir)


def test_never_writes_to_source(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    original = 'Zeile 1\nZeile 2\n'
    source_md.write_text(original, encoding='utf-8')

    import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert source_md.read_text(encoding='utf-8') == original


# ---------------------------------------------------------------------------
# Image copy
# ---------------------------------------------------------------------------

def test_new_image_is_copied_and_reported(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\n', encoding='utf-8')
    source_img_dir.mkdir(parents=True)
    (source_img_dir / 'screenshot.png').write_bytes(b'fake-png-bytes')

    result = import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert (target_img_dir / 'screenshot.png').exists()
    assert (target_img_dir / 'screenshot.png').read_bytes() == b'fake-png-bytes'
    assert result['copied_images'] == ['screenshot.png']


def test_unchanged_image_is_not_recopied_on_rerun(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\n', encoding='utf-8')
    source_img_dir.mkdir(parents=True)
    img = source_img_dir / 'screenshot.png'
    img.write_bytes(b'fake-png-bytes')

    first = import_chronik(source_md, source_img_dir, target_md, target_img_dir)
    assert first['copied_images'] == ['screenshot.png']

    # Rerun with no changes to the source image (shutil.copy2 preserved its
    # mtime on the target, so dest mtime >= src mtime holds without relying
    # on real-time timing gaps).
    second = import_chronik(source_md, source_img_dir, target_md, target_img_dir)
    assert second['copied_images'] == []


def test_newer_image_replaces_older_target(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\n', encoding='utf-8')
    source_img_dir.mkdir(parents=True)
    img = source_img_dir / 'screenshot.png'
    img.write_bytes(b'v1')

    import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    # Explicitly age the target file back, then bump the source mtime
    # forward, to avoid depending on real-time sleeps for a "newer" check.
    old_time = time.time() - 3600
    os.utime(target_img_dir / 'screenshot.png', (old_time, old_time))
    img.write_bytes(b'v2')
    new_time = time.time()
    os.utime(img, (new_time, new_time))

    result = import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert result['copied_images'] == ['screenshot.png']
    assert (target_img_dir / 'screenshot.png').read_bytes() == b'v2'


def test_os_metadata_files_are_never_copied(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\n', encoding='utf-8')
    source_img_dir.mkdir(parents=True)
    (source_img_dir / 'screenshot.png').write_bytes(b'fake-png-bytes')
    (source_img_dir / 'desktop.ini').write_text('[.ShellClassInfo]\n', encoding='utf-8')
    (source_img_dir / 'Thumbs.db').write_bytes(b'junk')
    (source_img_dir / '.DS_Store').write_bytes(b'junk')

    result = import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert result['copied_images'] == ['screenshot.png']
    assert not (target_img_dir / 'desktop.ini').exists()
    assert not (target_img_dir / 'Thumbs.db').exists()
    assert not (target_img_dir / '.DS_Store').exists()


def test_no_image_dir_is_not_an_error(tmp_path):
    source_md, source_img_dir, target_md, target_img_dir = _paths(tmp_path)
    source_md.parent.mkdir(parents=True)
    source_md.write_text('Zeile 1\n', encoding='utf-8')
    # source_img_dir deliberately not created

    result = import_chronik(source_md, source_img_dir, target_md, target_img_dir)

    assert result['copied_images'] == []
    assert not target_img_dir.exists()


# ---------------------------------------------------------------------------
# Shared path constants (importer and parser must agree on the location)
# ---------------------------------------------------------------------------

def test_import_targets_are_derived_from_shared_chronik_paths():
    assert chronik_import.TARGET_MD == chronik_dir(chronik_import.VAULT_ROOT) / CHRONIK_MD_NAME
    assert chronik_import.TARGET_IMG_DIR == chronik_dir(chronik_import.VAULT_ROOT) / CHRONIK_IMG_DIRNAME


def test_chronik_dir_layout(tmp_path):
    assert chronik_dir(tmp_path) == tmp_path / 'abenteuer' / 'drachenchronik'
    assert (CHRONIK_MD_NAME, CHRONIK_IMG_DIRNAME) == ('chronik.md', 'drachenchronik-daten')
