"""Synthetischer Mini-Held fuer Tests, die load_held ohne den Live-Bogen (helden/illaen-baernhold) brauchen.

Verwendung:
    root = write_mini_held(tmp_path, talente=..., zauber=...)   # legt <root>/helden/mini-held/ an
    held = load_held(root, MINI_SLUG)
Jede der neun Dateien, die load_held liest, wird angelegt und ist leer, solange sie nicht per Schluesselwort
befuellt wird (Schluessel siehe HELD_DATEIEN; `_illaen.md` heisst `illaen`, Bindestriche werden zu Unterstrichen)."""
from pathlib import Path

MINI_SLUG = 'mini-held'

HELD_DATEIEN = {
    'illaen': '_illaen.md',
    'talente': 'talente.md',
    'zauber': 'zauber.md',
    'rituale': 'rituale.md',
    'sonderfertigkeiten': 'sonderfertigkeiten.md',
    'vor_nachteile': 'vor-nachteile.md',
    'ausruestung': 'ausruestung.md',
    'steigerungs_log': 'steigerungs-log.md',
    'vorgeschichte': 'vorgeschichte.md',
}


def write_mini_held(root, slug=MINI_SLUG, **inhalte):
    """Schreibt helden/<slug>/*.md unter root (leere Dateien ausser den per Schluesselwort uebergebenen) und liefert root."""
    unbekannt = set(inhalte) - set(HELD_DATEIEN)
    assert not unbekannt, f'unbekannte Held-Dateien: {sorted(unbekannt)}'
    held_dir = Path(root) / 'helden' / slug
    held_dir.mkdir(parents=True, exist_ok=True)
    for key, name in HELD_DATEIEN.items():
        (held_dir / name).write_text(inhalte.get(key, ''), encoding='utf-8')
    return root
