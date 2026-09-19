"""Tests for GET /chronik-bild/<path> — hardened image delivery (synthetic vault only)."""
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import server

PNG_BYTES = b'\x89PNG\r\n\x1a\n-synthetic-'


@pytest.fixture
def client(tmp_path, monkeypatch):
    chronik = tmp_path / 'abenteuer' / 'drachenchronik'
    daten = chronik / 'drachenchronik-daten'
    daten.mkdir(parents=True)
    (daten / 'a.png').write_bytes(PNG_BYTES)
    (daten / 'GROSS.PNG').write_bytes(PNG_BYTES)
    (daten / 'vektor.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg"/>', encoding='utf-8')
    (daten / 'geheim.md').write_text('# privat', encoding='utf-8')
    (chronik / 'chronik.md').write_text('# privat', encoding='utf-8')
    (chronik / 'x.png').write_bytes(PNG_BYTES)
    monkeypatch.setattr(server, 'VAULT_ROOT', tmp_path)
    return server.create_app('illaen-baernhold').test_client()


def test_image_in_daten_folder_is_served(client):
    with client.get('/chronik-bild/drachenchronik-daten/a.png') as resp:
        assert resp.status_code == 200
        assert resp.data == PNG_BYTES


def test_uppercase_extension_is_served(client):
    with client.get('/chronik-bild/drachenchronik-daten/GROSS.PNG') as resp:
        assert resp.status_code == 200
        assert resp.data == PNG_BYTES


def test_markdown_at_folder_root_is_404(client):
    assert client.get('/chronik-bild/chronik.md').status_code == 404


@pytest.mark.parametrize('path', [
    '/chronik-bild/drachenchronik-daten/../chronik.md',
    '/chronik-bild/../chronik.md',
    '/chronik-bild/drachenchronik-daten/%2e%2e/chronik.md',
    '/chronik-bild/%2e%2e/chronik.md',
    '/chronik-bild/drachenchronik-daten/%2e%2e/x.png',
    '/chronik-bild/drachenchronik-daten/..%2fchronik.md',
    '/chronik-bild/drachenchronik-daten%2f..%2fx.png',
    '/chronik-bild/drachenchronik-daten/..%5cx.png',
    '/chronik-bild/drachenchronik-daten/..%5cchronik.md',
])
def test_traversal_is_404(client, path):
    assert client.get(path).status_code == 404


def test_svg_inside_daten_folder_is_404(client):
    assert client.get('/chronik-bild/drachenchronik-daten/vektor.svg').status_code == 404


def test_markdown_inside_daten_folder_is_404(client):
    assert client.get('/chronik-bild/drachenchronik-daten/geheim.md').status_code == 404


def test_image_outside_daten_folder_is_404(client):
    assert client.get('/chronik-bild/x.png').status_code == 404


def test_folder_prefix_lookalike_is_404(client):
    assert client.get('/chronik-bild/drachenchronik-daten-evil/a.png').status_code == 404


def test_missing_image_is_404(client):
    assert client.get('/chronik-bild/drachenchronik-daten/fehlt.png').status_code == 404
