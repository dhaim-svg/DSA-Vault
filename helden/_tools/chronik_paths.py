"""Single source of truth for where the Drachenchronik lives inside the vault."""
from pathlib import Path

CHRONIK_DIR_PARTS = ('abenteuer', 'drachenchronik')
CHRONIK_MD_NAME = 'chronik.md'
CHRONIK_IMG_DIRNAME = 'drachenchronik-daten'


def chronik_dir(vault_root: Path) -> Path:
    return Path(vault_root).joinpath(*CHRONIK_DIR_PARTS)
