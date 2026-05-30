"""Shared Jinja2 rendering helpers for the DSA hero dashboard."""
from pathlib import Path
from urllib.parse import quote
import jinja2

TOOLS_DIR = Path(__file__).parent
TEMPLATES_DIR = TOOLS_DIR / 'templates'


def obsidian_uri(wiki_path: str, vault_name: str = 'DSA-Vault') -> str:
    if not wiki_path:
        return ''
    path, _, anker = wiki_path.partition('#')
    file_part = quote(path + '.md', safe='/')
    anker_part = f'#{quote(anker)}' if anker else ''
    return f'obsidian://open?vault={quote(vault_name)}&file={file_part}{anker_part}'


def roman(n: int) -> str:
    vals = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),
            (50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]
    result = ''
    for v, s in vals:
        while n >= v:
            result += s
            n -= v
    return result


def format_ap(n: int) -> str:
    """Format AP integer as narrow-space-separated thousands: 3850 → '3 850'."""
    s = str(int(n))
    if len(s) > 3:
        return ' '.join([s[:-3], s[-3:]])
    return s


def make_env() -> jinja2.Environment:
    loader = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
    env = jinja2.Environment(loader=loader, autoescape=False,
                             trim_blocks=True, lstrip_blocks=True)
    env.filters['roman'] = roman
    env.filters['format_ap'] = format_ap
    env.filters['obsidian'] = obsidian_uri
    return env
