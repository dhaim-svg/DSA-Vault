"""File-watcher for the hero dashboard. Used by render-held.py --watch."""
import sys
import time
import threading
from pathlib import Path
from typing import Callable

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

TOOLS_DIR = Path(__file__).parent
VAULT_ROOT = TOOLS_DIR.parent.parent

_WATCH_DIRS = [
    VAULT_ROOT / 'helden',
    VAULT_ROOT / 'abenteuer',
]


class _RenderHandler(FileSystemEventHandler):
    def __init__(self, render_fn: Callable, server) -> None:
        self._render_fn = render_fn
        self._server = server
        self._debounce_timer: threading.Timer | None = None

    def on_any_event(self, event):
        if event.is_directory:
            return
        path = getattr(event, 'src_path', '')
        if not path.endswith('.md'):
            return
        # Debounce: only render after 300ms of quiet
        if self._debounce_timer:
            self._debounce_timer.cancel()
        self._debounce_timer = threading.Timer(0.3, self._do_render)
        self._debounce_timer.start()

    def _do_render(self):
        try:
            out = self._render_fn()
            print(f'[watcher] re-rendered → {out}')
            if self._server:
                self._server.reload(str(out.name))
        except Exception as exc:
            print(f'[watcher] render error: {exc}', file=sys.stderr)


def start_watch(slug: str, render_fn: Callable, open_browser: bool = False) -> None:
    try:
        from livereload import Server
    except ImportError:
        Server = None

    server = None
    http_thread = None

    if Server:
        server = Server()
        output_dir = VAULT_ROOT / 'output'
        server.watch(str(output_dir / f'{slug}-dashboard.html'))
        port = 5500

        def _serve():
            server.serve(root=str(output_dir), port=port, open_url_delay=None)

        http_thread = threading.Thread(target=_serve, daemon=True)
        http_thread.start()
        print(f'[watcher] livereload server at http://localhost:{port}')
        if open_browser:
            import webbrowser, time
            time.sleep(0.5)
            webbrowser.open(f'http://localhost:{port}/{slug}-dashboard.html')
    else:
        print('[watcher] livereload not installed — file watching active, manual refresh needed.')
        if open_browser:
            import webbrowser
            out = VAULT_ROOT / 'output' / f'{slug}-dashboard.html'
            webbrowser.open(out.as_uri())

    handler = _RenderHandler(render_fn, server)
    observer = Observer()
    for watch_dir in _WATCH_DIRS:
        if watch_dir.exists():
            observer.schedule(handler, str(watch_dir), recursive=True)
            print(f'[watcher] watching {watch_dir}')

    observer.start()
    print('[watcher] press Ctrl-C to stop')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
        print('[watcher] stopped')
