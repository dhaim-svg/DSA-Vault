"""Flask server for the interactive DSA hero dashboard.

Serves the dashboard live-rendered from markdown and exposes a
PATCH /api/held/<slug>/value endpoint as the single write path.
"""
import re
import sys
import threading
import webbrowser
from pathlib import Path

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent
STATIC_DIR = TOOLS_DIR / 'static'
sys.path.insert(0, str(TOOLS_DIR))

from flask import Flask, abort, jsonify, request, send_from_directory
from parsers.held import load_held
from parsers.kampagne import load_kampagne
from chronik_paths import CHRONIK_IMG_DIRNAME, chronik_dir
from rendering import CHRONIK_BILD_PREFIX_SERVER, build_context, render_dashboard   # shared with render-held.py
from writers.held_writer import patch, etag_for, mtime_map
from git_ops import commit_helden

# No .svg: SVG can carry script. abenteuer/drachenchronik/ also holds private markdown.
CHRONIK_BILD_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp'}


def _valid_slug(s: str) -> bool:
    return bool(re.fullmatch(r'[a-z0-9_-]+', s or ''))


def _render_dashboard(slug: str) -> str:
    return render_dashboard(build_context(
        slug, VAULT_ROOT, chronik_bild_prefix=CHRONIK_BILD_PREFIX_SERVER))


def create_app(slug: str) -> Flask:
    app = Flask(__name__, static_folder=str(STATIC_DIR), static_url_path='/static')

    # ------------------------------------------------------------------ #
    # CSRF: reject cross-origin writes (D-065)
    # ------------------------------------------------------------------ #

    @app.before_request
    def _reject_cross_origin_writes():
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return None
        origin = request.headers.get('Origin')
        if origin is None:
            return None
        expected = request.host_url.rstrip('/')
        if origin != expected:
            return jsonify({'error': 'cross-origin request rejected'}), 403
        return None

    # ------------------------------------------------------------------ #
    # Page routes
    # ------------------------------------------------------------------ #

    @app.route('/')
    def index():
        return _render_dashboard(slug)

    @app.route('/held/<path:s>')
    def held_page(s):
        if not _valid_slug(s):
            abort(404)
        return _render_dashboard(s)

    @app.route('/chronik-bild/<path:name>')
    def chronik_bild(name):
        prefix = CHRONIK_IMG_DIRNAME + '/'
        if not name.startswith(prefix):
            abort(404)
        if Path(name).suffix.lower() not in CHRONIK_BILD_EXTENSIONS:
            abort(404)
        # Root at the image folder itself: safe_join then rejects any '..' escape,
        # even one that would normalize out of it (drachenchronik-daten/../x.png).
        return send_from_directory(chronik_dir(VAULT_ROOT) / CHRONIK_IMG_DIRNAME, name[len(prefix):])

    # ------------------------------------------------------------------ #
    # API: read
    # ------------------------------------------------------------------ #

    @app.route('/api/held/<slug_param>')
    def api_held(slug_param):
        if not _valid_slug(slug_param):
            return jsonify({'error': 'invalid slug'}), 400
        try:
            held = load_held(VAULT_ROOT, slug_param)
            kampagne = load_kampagne(VAULT_ROOT, 'drachenchronik')
            return jsonify({'held': held, 'kampagne': kampagne})
        except FileNotFoundError:
            return jsonify({'error': 'not found'}), 404

    @app.route('/api/held/<slug_param>/mtime')
    def api_mtime(slug_param):
        if not _valid_slug(slug_param):
            return jsonify({'error': 'invalid slug'}), 400
        return jsonify(mtime_map(VAULT_ROOT, slug_param))

    @app.route('/api/held/<slug_param>/etag')
    def api_etag(slug_param):
        if not _valid_slug(slug_param):
            return jsonify({'error': 'invalid slug'}), 400
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
        if not _valid_slug(slug_param):
            return jsonify({'error': 'invalid slug'}), 400
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

    @app.route('/api/kampagne/<camp>/value', methods=['PATCH'])
    def api_patch_kampagne(camp):
        if not re.fullmatch(r'[a-z0-9_-]+', camp):
            return jsonify({'error': 'invalid campaign name'}), 400
        locator = request.get_json(force=True)
        if not locator:
            return jsonify({'error': 'missing JSON body'}), 400
        # Force scope=kampagne and campaign=camp into the locator
        locator['scope'] = 'kampagne'
        locator['campaign'] = camp
        result = patch(VAULT_ROOT, camp, locator)
        if not result.ok:
            status = 409 if result.error == 'conflict' else 400
            return jsonify({'ok': False, 'error': result.error}), status
        return jsonify({'ok': True, 'old': result.old_value, 'new': result.new_value, 'mtime': result.mtime_after})

    # ------------------------------------------------------------------ #
    # API: git commit
    # ------------------------------------------------------------------ #

    @app.route('/api/commit', methods=['POST'])
    def api_commit():
        if not request.is_json:
            return jsonify({'ok': False, 'error': 'expected application/json'}), 415
        body = request.get_json(silent=True)
        message = (body or {}).get('message', None)
        result = commit_helden(VAULT_ROOT, slug, message=message)
        if not result.get('ok'):
            return jsonify({'ok': False, 'error': 'git operation failed'}), 500
        return jsonify({
            'ok': True,
            'committed': result['committed'],
            'message': result['message'],
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
