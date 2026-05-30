"""File-watcher for the DSA hero dashboard.

In serve mode: watching is implicit (GET / re-reads markdown on every request).
The /api/held/<slug>/mtime endpoint is the change signal; app.js polls it.

In render --watch mode: re-renders to the output file on .md changes.
"""
import sys
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
    def __init__(self, render_fn: Callable) -> None:
        self._render_fn = render_fn
        self._debounce_timer: threading.Timer | None = None

    def on_any_event(self, event):
        if event.is_directory:
            return
        path = getattr(event, 'src_path', '')
        if not path.endswith('.md'):
            return
        if self._debounce_timer:
            self._debounce_timer.cancel()
        self._debounce_timer = threading.Timer(0.3, self._do_render)
        self._debounce_timer.start()

    def _do_render(self):
        try:
            out = self._render_fn()
            print(f'[watcher] re-rendered → {out}')
        except Exception as exc:
            print(f'[watcher] render error: {exc}', file=sys.stderr)


def start_watch(slug: str, render_fn: Callable, open_browser: bool = False) -> None:
    """Start file watcher for render --watch mode (re-renders static HTML on .md change)."""
    import time
    import webbrowser

    if open_browser:
        out = VAULT_ROOT / 'output' / f'{slug}-dashboard.html'
        webbrowser.open(out.as_uri())
        print(f'[watcher] opened {out.as_uri()}')

    handler = _RenderHandler(render_fn)
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
