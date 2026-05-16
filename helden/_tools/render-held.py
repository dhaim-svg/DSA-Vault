#!/usr/bin/env python3
"""Render a DSA 4.1 hero dashboard to output/illaen-dashboard.html."""
import argparse
import sys
import webbrowser
from pathlib import Path

import jinja2

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
TEMPLATES_DIR = TOOLS_DIR / 'templates'
OUTPUT_DIR = VAULT_ROOT / 'output'

sys.path.insert(0, str(TOOLS_DIR))
from parsers.held import load_held
from parsers.kampagne import load_kampagne


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
        return ' '.join([s[:-3], s[-3:]])
    return s


def render(slug: str) -> Path:
    held = load_held(VAULT_ROOT, slug)
    kampagne = load_kampagne(VAULT_ROOT, 'drachenchronik')

    loader = jinja2.FileSystemLoader(str(TEMPLATES_DIR))
    env = jinja2.Environment(loader=loader, autoescape=False,
                             trim_blocks=True, lstrip_blocks=True)
    env.filters['roman'] = roman
    env.filters['format_ap'] = format_ap

    template = env.get_template('dashboard.html.j2')
    html = template.render(held=held, kampagne=kampagne)

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f'{slug}-dashboard.html'
    out_path.write_text(html, encoding='utf-8')
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description='Render DSA hero dashboard.')
    parser.add_argument('slug', help='Hero slug, e.g. illaen-baernhold')
    parser.add_argument('--open', action='store_true', dest='do_open',
                        help='Open in browser after render')
    parser.add_argument('--watch', action='store_true',
                        help='Watch for changes and auto-reload')
    args = parser.parse_args()

    out_path = render(args.slug)
    print(f'Rendered -> {out_path}')

    if args.watch:
        from watcher import start_watch
        start_watch(args.slug, render_fn=lambda: render(args.slug),
                    open_browser=args.do_open)
    elif args.do_open:
        webbrowser.open(out_path.as_uri())


if __name__ == '__main__':
    main()
