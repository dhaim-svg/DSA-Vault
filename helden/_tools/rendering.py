"""Shared Jinja2 rendering helpers for the DSA hero dashboard."""
from pathlib import Path
from urllib.parse import quote
import jinja2

from parsers.held import load_held
from parsers.chronik import load_chronik
from parsers.kampagne import load_kampagne
from parsers.register import build_register

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
TEMPLATES_DIR = TOOLS_DIR / 'templates'
STATIC_DIR = TOOLS_DIR / 'static'
KAMPAGNE_SLUG = 'drachenchronik'

# Prefix + chronik bild.src (which starts with 'drachenchronik-daten/') gives the <img> URL.
CHRONIK_BILD_PREFIX_SERVER = '/chronik-bild/'
CHRONIK_BILD_PREFIX_STATIC = '../abenteuer/drachenchronik/'

# Bundle order is load-bearing: CSS cascade depends on it.
CSS_FILES = ['base.css', 'tabs.css', 'journal.css', 'sprachen.css', 'chronik.css']

# Order = load dependency: util.js first (app.js/commit.js use dsaShowIndicator), session.js before dice.js.
# Every new static/*.js must be listed here (a test enforces it).
JS_FILES = ['util.js', 'app.js', 'session.js', 'dice.js', 'tabs.js', 'steigern.js',
            'inventar.js', 'zauberspeicher.js', 'journal.js', 'chronik.js', 'register.js', 'commit.js']


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


def css_bundle() -> str:
    return ''.join((STATIC_DIR / name).read_text(encoding='utf-8') for name in CSS_FILES)


def js_files() -> list[tuple[str, str]]:
    return [(name, (STATIC_DIR / name).read_text(encoding='utf-8')) for name in JS_FILES]


def make_env() -> jinja2.Environment:
    loader = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
    env = jinja2.Environment(loader=loader, autoescape=False,
                             trim_blocks=True, lstrip_blocks=True)
    env.filters['roman'] = roman
    env.filters['format_ap'] = format_ap
    env.filters['obsidian'] = obsidian_uri
    env.globals['css_bundle'] = css_bundle
    env.globals['js_files'] = js_files
    return env


def build_context(slug: str, vault_root: Path = VAULT_ROOT, *,
                  chronik_bild_prefix: str = CHRONIK_BILD_PREFIX_STATIC,
                  inline_js: bool = False) -> dict:
    """Template context shared by the live server and the static render.

    inline_js=True (static file:// render) embeds the JS and shows the "not saved" hint.
    """
    kampagne = load_kampagne(vault_root, KAMPAGNE_SLUG)
    return {
        'held': load_held(vault_root, slug),
        'kampagne': kampagne,
        'register': build_register(kampagne.get('sessions', [])),
        'chronik': load_chronik(vault_root),
        'chronik_bild_prefix': chronik_bild_prefix,
        'inline_js': inline_js,
        'slug': slug,
        'kampagne_slug': KAMPAGNE_SLUG,
    }


def render_dashboard(context: dict) -> str:
    return make_env().get_template('dashboard.html.j2').render(**context)
