"""Parser for the Drachenchronik campaign log (abenteuer/drachenchronik/chronik.md)."""
import re
from pathlib import Path

from .held import parse_frontmatter, split_sections, strip_wikilink

DATUM_RE = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{4}$')

DSA_MONATE = [
    'Praios', 'Rondra', 'Efferd', 'Travia', 'Boron', 'Hesinde',
    'Firun', 'Tsa', 'Phex', 'Peraine', 'Ingerimm', 'Rahja',
]
IG_DATUM_RE = re.compile(
    r'^\d{1,2}\.\s+(?:' + '|'.join(DSA_MONATE) + r')$'
    r'|^\d\.\s+Namenloser Tag$'
)

BOLD_LINE_RE = re.compile(r'^\*\*([^*]+)\*\*$')
ITALIC_LINE_RE = re.compile(r'^\*([^*]+)\*$')
BULLET_RE = re.compile(r'^(\s*)-\s+(.*)$')
IMG_RE = re.compile(r'<img\s+src="([^"]+)"')


def _parse_spielabend_body(body: str) -> list[dict]:
    ig_tage: list[dict] = []
    current = {'ig_datum': None, 'bloecke': []}

    def flush():
        if current['bloecke']:
            ig_tage.append(current)

    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue

        bold_m = BOLD_LINE_RE.match(stripped)
        if bold_m:
            inner = bold_m.group(1).strip()
            if IG_DATUM_RE.match(inner):
                flush()
                current = {'ig_datum': inner, 'bloecke': []}
                continue
            current['bloecke'].append({'typ': 'szene', 'text': strip_wikilink(inner)})
            continue

        italic_m = ITALIC_LINE_RE.match(stripped)
        if italic_m:
            current['bloecke'].append({'typ': 'szene', 'text': strip_wikilink(italic_m.group(1).strip())})
            continue

        img_m = IMG_RE.search(stripped)
        if img_m:
            # Source chronicle uses Windows-style paths ("dir\bild.png"); a
            # backslash is not a valid URL path separator, so <img src>
            # emitted by a future renderer would 404. Normalize now, at the
            # parsing boundary, rather than pushing this onto every consumer.
            src = img_m.group(1).replace('\\', '/')
            current['bloecke'].append({'typ': 'bild', 'src': src})
            continue

        bullet_m = BULLET_RE.match(raw_line)
        if bullet_m:
            tiefe = len(bullet_m.group(1)) // 2
            current['bloecke'].append({
                'typ': 'bullet',
                'tiefe': tiefe,
                'text': strip_wikilink(bullet_m.group(2).strip()),
            })
            continue

        current['bloecke'].append({'typ': 'text', 'text': strip_wikilink(stripped)})

    flush()
    return ig_tage


def load_chronik(vault_root: Path, filename: str = 'chronik.md') -> dict:
    """Load and parse the Drachenchronik from abenteuer/drachenchronik/<filename>."""
    chronik_file = vault_root / 'abenteuer' / 'drachenchronik' / filename
    if not chronik_file.exists():
        return {'spielabende': [], 'meta': {}}

    text = chronik_file.read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    h2 = split_sections(rest, 2)

    spielabende: list[dict] = []
    meta: dict[str, str] = {}
    for heading, body in h2.items():
        if heading == '__pre__':
            continue
        if DATUM_RE.match(heading):
            spielabende.append({'datum': heading, 'ig_tage': _parse_spielabend_body(body)})
        else:
            meta[heading] = strip_wikilink(body)

    return {'spielabende': spielabende, 'meta': meta}
