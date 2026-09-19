"""
check-frontmatter.py — Read-only Verifizierer für das YAML-Frontmatter der Wiki-Artikel.

Verwendung:
    python raw/pdf-extracted/_tools/check-frontmatter.py [wurzel]

    wurzel  Ordner, der rekursiv nach *.md durchsucht wird
            (Default: wiki/ im Vault-Root; relative Angaben gelten ab Vault-Root).

Frontmatter wird wie in helden/_tools/parsers/held.py (parse_frontmatter) geteilt:
nur wenn der Text mit '---' beginnt, dann text.split('---', 2); bei weniger als
3 Teilen gilt die Datei als frontmatter-los. Geprüft wird yaml.safe_load(parts[1]);
fehlerhaft ist ein YAML-Fehler oder ein Ergebnis, das weder None noch dict ist.
Nicht lesbare Dateien zählen ebenfalls als fehlerhaft.

Häufigste Ursache: unquotierter Wert mit ': ' (z.B. kosten: 4 AsP (Ach: 3 AsP)).
Abhilfe: Wert in doppelte Anführungszeichen setzen.

Output: je Fehler eine Zeile '<relativer Pfad>: <Fehlertext>' (Zeilennummer = Zeile in
der Datei, falls verfügbar), am Ende 'N Dateien geprüft, M mit Frontmatter, K fehlerhaft'.
Exit-Code 0 bei 0 Fehlern, sonst 1. Schreibt nie in Dateien.
"""

import os
import sys

import yaml

VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))


def check_file(path: str) -> tuple[bool, str | None]:
    """Gibt (hat_frontmatter, fehlertext_oder_None) zurück."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        return False, f"nicht lesbar: {' '.join(str(e).split())}"

    if not text.startswith("---"):
        return False, None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, None

    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        # parts[1] beginnt hinter dem ersten '---' → mark.line (0-basiert) == Dateizeile - 1
        mark = getattr(e, "problem_mark", None)
        problem = getattr(e, "problem", None) or str(e)
        where = f"Zeile {mark.line + 1}: " if mark is not None else ""
        return True, where + " ".join(problem.split())
    if data is not None and not isinstance(data, dict):
        return True, f"Frontmatter ist kein Mapping ({type(data).__name__})"
    return True, None


def main(argv: list[str]) -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows-Konsole/Pipe: cp1252 würde Umlaute verfälschen
    root =argv[1] if len(argv) > 1 else "wiki"
    if not os.path.isabs(root):
        root = os.path.join(VAULT_ROOT, root)
    if not os.path.isdir(root):
        print(f"Ordner nicht gefunden: {root}", file=sys.stderr)
        return 2

    checked = with_fm = bad = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            if not name.lower().endswith(".md"):
                continue
            path = os.path.join(dirpath, name)
            checked += 1
            has_fm, error = check_file(path)
            with_fm += has_fm
            if error:
                bad += 1
                rel = os.path.relpath(path, VAULT_ROOT).replace(os.sep, "/")
                print(f"{rel}: {error}")

    print(f"{checked} Dateien geprüft, {with_fm} mit Frontmatter, {bad} fehlerhaft")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
