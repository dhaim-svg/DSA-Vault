"""
split-chapters.py — Zerlegt pdftotext-Output in Kapitel-Dateien.

Verwendung:
    python split-chapters.py <buch-slug>

Verfügbare Bücher (--list):
    wege-der-helden

Output: raw/pdf-extracted/<buch-slug>/kapitel-<nn>-<slug>.txt
"""

import re
import sys
import os

# ---------------------------------------------------------------------------
# Buch-Profile
# Jedes Kapitel: (datei_slug, regex_pattern, min_zeile)
# min_zeile verhindert, dass TOC-Matches als Kapitel erkannt werden.
# ---------------------------------------------------------------------------

PROFILE_WDH = {
    "name": "wege-der-helden",
    "input": "wege-der-helden/full.txt",
    "chapters": [
        # (slug, regex, erste mögliche Zeile)
        ("inhalt",          r"^Inhalt\s*$",                                    74),
        ("vorwort",         r"^Vorwort\s*$",                                  138),
        ("erschaffung",     r"^Die Erschaffung\s*$",                          162),
        ("rassen",          r"^Die Rassen(?!\.*\.)",                         1620),
        ("kulturen",        r"^Die Kulturen(?!\.*\.)",                       2580),
        ("professionen",    r"^Die Professionen(?!\.*\.)",                   5990),
        ("vor-nachteile",   r"^Vorteile, Nachteile,\s*$",                  16280),
        ("zwanzig-fragen",  r"^Zwanzig Fragen",                            18400),
        ("anhang-1",        r"^Anhang 1:",                                 19970),
        ("anhang-2",        r"^Anhang 2:",                                 20380),
        ("anhang-3",        r"^Anhang 3:",                                 20660),
        ("anhang-4",        r"^Anhang 4:",                                 21160),
        ("anhang-5",        r"^Anhang 5:",                                 21500),
        ("anhang-6",        r"^Anhang 6:",                                 21600),
        ("index",           r"^Index\s*$",                                 22000),
    ]
}

PROFILE_WDS = {
    "name": "wege-des-schwertes",
    "input": "wege-des-schwertes/full.txt",
    "chapters": [
        # min_line ist 0-basiert (grep-Zeile – 2)
        ("vorwort",         r"^Vorwort\s*$",                                    90),
        ("spielregeln",     r"^Die Spielregeln in Kürze\s*$",                  100),
        ("talente",         r"^Talente,\s*$",                                  200),
        ("kampf",           r"^Die Kampfregeln\s*$",                          2500),
        ("umfassend",       r"^Umfassende Regeln\s*$",                        9000),
        ("erfahrung",       r"Abenteuerpunkte\s*$",                          11000),  # führende Leerzeichen
        ("anhang-1-so",     r"^Anhang 1: Sozialstatus",                      12000),
        ("anhang-2-waffen", r"^Anhang 2: Feuer und Eisen",                   12500),
        ("anhang-3-meta",   r"^Anhang 3: Meta-Talente",                      13000),
        ("anhang-4-sf",     r"^Anhang 4: Die Sonderfertigkeit",              13300),
        ("anhang-5-sp",     r"^Anhang 5: Strukturpunkte",                    13400),
        ("anhang-6-alter",  r"^Anhang 6: Zur Alterung",                      13460),
        ("anhang-7-tab",    r"^Anhang 7: Tabellen",                          13500),
        ("index",           r"^Index\s*$",                                   14000),
    ]
}

PROFILE_WDZ = {
    "name": "wege-der-zauberei",
    "input": "wege-der-zauberei/full.txt",
    "chapters": [
        # (slug, regex, min_line_0based)
        ("vorwort",          r"^Vorwort\s*$",                                      140),
        ("grundlagen",       r"^Die Quelle der Magie\s*$",                         170),
        ("zauberprobe",      r"^Zauberfertigkeiten und\s*$",                        540),
        ("sonderregeln",     r"^Bann des Eisens\s*$",                             2060),
        ("zauberwerkstatt",  r"Metamagische Methoden\s*$",                        2540),
        ("artefakte",        r"Magische Artefakte\s*$",                           3080),
        ("alchimie-traeume", r"^Die Kunst der Alchimie\s*$",                      4115),
        ("erfahrung",        r"^Erfahrung und Steigerung\s*$",                    5005),
        ("rituale",          r"^Ritualzauberei\s*$",                              7280),
        ("invokation",       r"^Die Kunst der Invokation\s*$",                   12260),
        ("besessenheit",     r"^Besessenheit\s*$",                               17685),
        ("traditionen",      r"^Die magischen\s*$",                              17806),
        ("welt-sphaeren",    r"^Welt, Sph.ren und Kosmos\s*$",                   25030),
        ("satinav-elemente", r"^Satinav und das Wesen der Zeit\s*$",             26088),
        ("kreaturen-legenden", r"^Magische Kreaturen\s*$",                       28808),
        ("index",            r"^Index\s*$",                                      30190),
    ]
}

PROFILES = {
    "wege-der-helden": PROFILE_WDH,
    "wege-des-schwertes": PROFILE_WDS,
    "wege-der-zauberei": PROFILE_WDZ,
}


def find_chapter_starts(lines: list[str], chapters: list) -> list[tuple[int, str]]:
    """Gibt (zeilennummer_0based, slug) für jeden gefundenen Kapitelstart zurück."""
    remaining = list(chapters)  # Kapitel, auf die noch gewartet wird
    found = []

    for lineno, line in enumerate(lines):
        if not remaining:
            break
        slug, pattern, min_line = remaining[0]
        # pdftotext setzt \x0c (Form-Feed) am Anfang jeder Seite → abstreifen
        stripped = line.lstrip('\x0c')
        if lineno >= min_line and re.search(pattern, stripped):
            found.append((lineno, slug))
            remaining.pop(0)

    if remaining:
        missing = [c[0] for c in remaining]
        print(f"  WARNUNG: Folgende Kapitel nicht gefunden: {missing}", file=sys.stderr)

    return found


def split_and_write(text_path: str, chapters: list, out_dir: str):
    with open(text_path, encoding="utf-8") as f:
        lines = f.readlines()

    starts = find_chapter_starts(lines, chapters)
    if not starts:
        print("FEHLER: Keine Kapitel gefunden.", file=sys.stderr)
        return

    # Kapitelgrenzen aufbauen: (start_zeile, end_zeile_exkl, slug, nummer)
    boundaries = []
    for i, (lineno, slug) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(lines)
        boundaries.append((lineno, end, slug, i + 1))

    os.makedirs(out_dir, exist_ok=True)
    for start, end, slug, num in boundaries:
        fname = f"kapitel-{num:02d}-{slug}.txt"
        out_path = os.path.join(out_dir, fname)
        with open(out_path, "w", encoding="utf-8") as f:
            f.writelines(lines[start:end])
        lines_count = end - start
        print(f"  {fname}  ({lines_count} Zeilen, ab Zeile {start + 1})")


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print(__doc__)
        sys.exit(0)

    if sys.argv[1] == "--list":
        print("Verfügbare Profile:", ", ".join(PROFILES.keys()))
        sys.exit(0)

    book = sys.argv[1]
    if book not in PROFILES:
        print(f"Unbekanntes Buch: {book}. Verfügbar: {', '.join(PROFILES)}", file=sys.stderr)
        sys.exit(1)

    profile = PROFILES[book]
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    text_path = os.path.join(base, profile["input"])
    out_dir = os.path.join(base, book)

    if not os.path.exists(text_path):
        print(f"Datei nicht gefunden: {text_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Trenne Kapitel für: {profile['name']}")
    print(f"Input:  {text_path}")
    print(f"Output: {out_dir}/")
    print()

    split_and_write(text_path, profile["chapters"], out_dir)
    print("\nFertig.")


if __name__ == "__main__":
    main()
