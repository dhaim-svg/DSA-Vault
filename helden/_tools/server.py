"""Flask server for the interactive DSA hero dashboard.

Serves the dashboard live-rendered from markdown and exposes a
PATCH /api/held/<slug>/value endpoint as the single write path.
"""
import sys
import threading
import webbrowser
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
STATIC_DIR = TOOLS_DIR / 'static'
sys.path.insert(0, str(TOOLS_DIR))

from flask import Flask, jsonify, request
from parsers.held import load_held
from parsers.kampagne import load_kampagne
from rendering import make_env           # shared Jinja helpers — no duplication
from writers.held_writer import patch, etag_for, mtime_map


def _render_dashboard(slug: str) -> str:
    held = load_held(VAULT_ROOT, slug)
    kampagne = load_kampagne(VAULT_ROOT, 'drachenchronik')
    env = make_env()
    return env.get_template('dashboard.html.j2').render(
        held=held, kampagne=kampagne, slug=slug
    )


def create_app(slug: str) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path='/static')

    # ------------------------------------------------------------------ #
    # Page routes
    # ------------------------------------------------------------------ #

    @app.route('/')
    def index():
        return _render_dashboard(slug)

    @app.route('/held/<path:s>')
    def held_page(s):
        return _render_dashboard(s)

    # ------------------------------------------------------------------ #
    # API: read
    # ------------------------------------------------------------------ #

    @app.route('/api/held/<slug_param>')
    def api_held(slug_param):
        try:
            held = load_held(VAULT_ROOT, slug_param)
            kampagne = load_kampagne(VAULT_ROOT, 'drachenchronik')
            return jsonify({'held': held, 'kampagne': kampagne})
        except Exception as exc:
            return jsonify({'error': str(exc)}), 500

    @app.route('/api/held/<slug_param>/mtime')
    def api_mtime(slug_param):
        return jsonify(mtime_map(VAULT_ROOT, slug_param))

    @app.route('/api/held/<slug_param>/etag')
    def api_etag(slug_param):
        rel_file = request.args.get('file', '_illaen.md')
        try:
            return jsonify({'etag': etag_for(VAULT_ROOT, slug_param, rel_file)})
        except FileNotFoundError:
            return jsonify({'error': 'not found'}), 404

    # ------------------------------------------------------------------ #
    # API: write (THE single mutation path)
    # ------------------------------------------------------------------ #

    @app.route('/api/held/<slug_param>/value', methods=['PATCH'])
    def api_patch_value(slug_param):
        locator = request.get_json(force=True)
        if not locator:
            return jsonify({'error': 'missing JSON body'}), 400
        result = patch(VAULT_ROOT, slug_param, locator)
        if not result.ok:
            status = 409 if result.error == 'conflict' else 400
            return jsonify({
                'ok': False,
                'error': result.error,
                'current_value': result.old_value,
            }), status
        return jsonify({
            'ok': True,
            'old': result.old_value,
            'new': result.new_value,
            'mtime': result.mtime_after,
        })

    return app


def run_server(slug: str, port: int = 5500, open_browser: bool = False) -> None:
    app = create_app(slug)
    if open_browser:
        def _open():
            import time
            time.sleep(0.8)
            webbrowser.open(f'http://localhost:{port}/')
        threading.Thread(target=_open, daemon=True).start()
    print(f'[server] DSA Dashboard at http://localhost:{port}/ — Ctrl-C to stop')
    app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
