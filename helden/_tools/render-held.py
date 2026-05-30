#!/usr/bin/env python3
"""Render a DSA 4.1 hero dashboard to output/<slug>-dashboard.html."""
import argparse
import sys
import webbrowser
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
OUTPUT_DIR = VAULT_ROOT / 'output'

sys.path.insert(0, str(TOOLS_DIR))
from parsers.held import load_held
from parsers.kampagne import load_kampagne
from rendering import make_env


def build_context(slug: str) -> dict:
    """Load hero + campaign data, return the Jinja template context dict."""
    return {
        'held': load_held(VAULT_ROOT, slug),
        'kampagne': load_kampagne(VAULT_ROOT, 'drachenchronik'),
        'slug': slug,
    }


def render_html(context: dict) -> str:
    """Render dashboard HTML from a pre-built context dict."""
    env = make_env()
    return env.get_template('dashboard.html.j2').render(**context)


def render(slug: str) -> Path:
    """Full pipeline: load → render → write file. Returns the output path."""
    html = render_html(build_context(slug))
    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f'{slug}-dashboard.html'
    out_path.write_text(html, encoding='utf-8')
    return out_path


def main() -> None:
    # Manual dispatch: detect 'serve' as first arg to avoid subparser backward-compat issues
    if len(sys.argv) > 1 and sys.argv[1] == 'serve':
        parser = argparse.ArgumentParser(description='Run interactive Flask server.')
        parser.add_argument('cmd')           # 'serve' — consumed to shift positionals
        parser.add_argument('slug', help='Hero slug, e.g. illaen-baernhold')
        parser.add_argument('--port', type=int, default=5500)
        parser.add_argument('--open', action='store_true', dest='do_open')
        args = parser.parse_args()
        from server import run_server
        run_server(args.slug, port=args.port, open_browser=args.do_open)
    else:
        # Legacy render mode — backward-compatible with existing usage
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
