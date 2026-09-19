"""Parser for the Drachenchronik campaign log (abenteuer/drachenchronik/chronik.md)."""
import re
from pathlib import Path

from chronik_paths import CHRONIK_MD_NAME, chronik_dir

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
IMG_TAG_RE = re.compile(r'<img\b[^>]*>', re.I)
IMG_SRC_RE = re.compile(r'\bsrc\s*=\s*["\']([^"\']+)["\']', re.I)


def _text_block(line: str) -> dict:
    bullet_m = BULLET_RE.match(line)
    if bullet_m:
        return {
            'typ': 'bullet',
            'tiefe': len(bullet_m.group(1)) // 2,
            'text': strip_wikilink(bullet_m.group(2).strip()),
        }
    return {'typ': 'text', 'text': strip_wikilink(line.strip())}


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

        if IMG_TAG_RE.search(stripped):
            srcs: list[str] = []

            def _extract(tag_m: re.Match) -> str:
                src_m = IMG_SRC_RE.search(tag_m.group(0))
                if not src_m:
                    # No src at all: keep the raw tag visible instead of dropping it silently.
                    return tag_m.group(0)
                # Source chronicle uses Windows-style paths ("dir\bild.png"); a
                # backslash is not a valid URL path separator, so <img src>
                # emitted by a future renderer would 404. Normalize now, at the
                # parsing boundary, rather than pushing this onto every consumer.
                srcs.append(src_m.group(1).replace('\\', '/'))
                return ' '

            block = _text_block(IMG_TAG_RE.sub(_extract, raw_line))
            block['text'] = ' '.join(block['text'].split())
            if block['text']:
                current['bloecke'].append(block)
            for src in srcs:
                current['bloecke'].append({'typ': 'bild', 'src': src})
            continue

        current['bloecke'].append(_text_block(raw_line))

    flush()
    return ig_tage


def load_chronik(vault_root: Path, filename: str = CHRONIK_MD_NAME) -> dict:
    """Load and parse the Drachenchronik from abenteuer/drachenchronik/<filename>."""
    chronik_file = chronik_dir(vault_root) / filename
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
