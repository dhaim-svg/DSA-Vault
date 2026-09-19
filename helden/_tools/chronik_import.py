#!/usr/bin/env python3
"""chronik_import.py — one-way import of the live campaign log from Drive into the vault.

The user writes the campaign log live in Google Drive
(Drachenchronik.md + drachenchronik-daten/ images), outside the vault.
This script pulls the current state into abenteuer/drachenchronik/ whenever
run. It never writes back to Drive and is never triggered automatically.
"""
import shutil
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent

DRIVE_ROOT = Path(r'C:\Users\David\Google Drive\DSA\Helden')
SOURCE_MD = DRIVE_ROOT / 'Drachenchronik.md'
SOURCE_IMG_DIR = DRIVE_ROOT / 'drachenchronik-daten'

TARGET_DIR = VAULT_ROOT / 'abenteuer' / 'drachenchronik'
TARGET_MD = TARGET_DIR / 'chronik.md'
TARGET_IMG_DIR = TARGET_DIR / 'drachenchronik-daten'

# OS-generated metadata files that sometimes sit next to synced images
# (Windows/Google Drive folder customization, macOS Finder state) — never
# campaign content, never worth importing.
IGNORED_IMAGE_NAMES = {'desktop.ini', 'thumbs.db', '.ds_store'}


def import_chronik(source_md=SOURCE_MD, source_img_dir=SOURCE_IMG_DIR,
                    target_md=TARGET_MD, target_img_dir=TARGET_IMG_DIR) -> dict:
    """Copy the live chronicle from Drive into the vault, one-way.

    Overwrites target_md with source_md's exact content (not a merge).
    Copies new/changed images from source_img_dir to target_img_dir,
    skipping images already present with an equal-or-newer mtime.
    Never writes to source_md or source_img_dir.

    Returns:
        {'lines_before': int, 'lines_after': int, 'copied_images': [str, ...]}

    Raises:
        FileNotFoundError: if source_md doesn't exist.
    """
    source_md = Path(source_md)
    source_img_dir = Path(source_img_dir)
    target_md = Path(target_md)
    target_img_dir = Path(target_img_dir)

    if not source_md.exists():
        raise FileNotFoundError(
            f'Quelldatei nicht gefunden: {source_md}'
        )

    content = source_md.read_text(encoding='utf-8')

    lines_before = 0
    if target_md.exists():
        lines_before = len(target_md.read_text(encoding='utf-8').splitlines())

    target_md.parent.mkdir(parents=True, exist_ok=True)
    target_md.write_text(content, encoding='utf-8')
    lines_after = len(content.splitlines())

    copied_images = []
    if source_img_dir.exists():
        target_img_dir.mkdir(parents=True, exist_ok=True)
        for src_file in source_img_dir.iterdir():
            if not src_file.is_file():
                continue
            if src_file.name.lower() in IGNORED_IMAGE_NAMES:
                continue
            dest_file = target_img_dir / src_file.name
            if dest_file.exists() and dest_file.stat().st_mtime >= src_file.stat().st_mtime:
                continue
            shutil.copy2(src_file, dest_file)
            copied_images.append(src_file.name)

    return {
        'lines_before': lines_before,
        'lines_after': lines_after,
        'copied_images': copied_images,
    }


def main() -> None:
    try:
        result = import_chronik()
    except FileNotFoundError as exc:
        print(f'Fehler: Chronik-Import fehlgeschlagen — {exc}', file=sys.stderr)
        sys.exit(1)

    delta = result['lines_after'] - result['lines_before']
    sign = '+' if delta >= 0 else ''
    print(f'chronik.md aktualisiert: {result["lines_before"]} -> {result["lines_after"]} Zeilen ({sign}{delta})')

    if result['copied_images']:
        print('Kopierte Bilder:')
        for name in result['copied_images']:
            print(f'  - {name}')
    else:
        print('keine neuen/geänderten Bilder')


if __name__ == '__main__':
    main()
