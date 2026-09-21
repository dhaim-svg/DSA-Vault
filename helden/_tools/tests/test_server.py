"""Tests for the /api/kampagne/<camp>/value Flask route (PATCH — 'Verlauf speichern').

Route-level tests for server.py don't yet have a dedicated home (test_commit.py and
test_chronik_bild.py each own a single route); this file starts one for /api/kampagne.
Pattern follows test_commit.py:107-131 — tmp_path fixture + VAULT_ROOT monkeypatch,
restored in finally, so the real vault is never touched.
"""
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import server as server_mod

FIXTURE_TEXT = """\
## Hintergrund

Kampagnenhintergrund hier.

## Verlauf

Alter Verlauf-Text.
Mehrere Zeilen.

## Notizen

Weitere Notizen.
"""


def _write_kampagne_file(tmp_path: Path, campaign: str, filename: str, content: str = FIXTURE_TEXT) -> Path:
    """Create a file inside abenteuer/<campaign>/ (unter tmp_path) und gibt den Pfad zurück."""
    target = tmp_path / 'abenteuer' / campaign / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    return target


def _client(tmp_path: Path, slug: str = 'illaen-baernhold'):
    """App mit VAULT_ROOT auf tmp_path gepatcht; ruft der Aufrufer in try/finally auf."""
    app = server_mod.create_app(slug)
    app.config['TESTING'] = True
    return app.test_client()


# ---------------------------------------------------------------------------
# PATCH /api/kampagne/<camp>/value — Erfolgsfall
# ---------------------------------------------------------------------------

def test_patch_kampagne_route_replaces_section_body(tmp_path):
    """PATCH mit kind=section_body ersetzt den Verlauf-Abschnitt und schreibt die Datei."""
    campaign = 'drachenchronik'
    md_file = _write_kampagne_file(tmp_path, campaign, 'session.md')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(tmp_path) as client:
            resp = client.patch(f'/api/kampagne/{campaign}/value', json={
                'kind': 'section_body',
                'file': 'session.md',
                'section': 'Verlauf',
                'value': 'Neuer Verlauf-Text nach dem Patch.',
            })
            assert resp.status_code == 200
            data = resp.get_json()
            assert data is not None
            assert data['ok'] is True
            assert 'Alter Verlauf-Text.' in data['old']
            assert data['new'] == 'Neuer Verlauf-Text nach dem Patch.'
            assert 'mtime' in data
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    # Wirklich geschrieben? Nur innerhalb von tmp_path lesen, nie im echten Vault.
    updated = md_file.read_text(encoding='utf-8')
    assert 'Neuer Verlauf-Text nach dem Patch.' in updated
    assert 'Alter Verlauf-Text.' not in updated
    # Nachbar-Abschnitte und die Überschrift selbst bleiben unangetastet
    assert '## Verlauf' in updated
    assert '## Hintergrund' in updated
    assert 'Kampagnenhintergrund hier.' in updated
    assert '## Notizen' in updated
    assert 'Weitere Notizen.' in updated


# ---------------------------------------------------------------------------
# PATCH /api/kampagne/<camp>/value — re.fullmatch-Guard auf den Kampagnennamen
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('bad_camp', [
    'Drachenchronik',      # Großbuchstabe
    'drachen chronik',     # Leerzeichen
    'drachen.chronik',     # Punkt
])
def test_patch_kampagne_route_rejects_invalid_campaign_name(tmp_path, bad_camp):
    """Kampagnennamen außerhalb von [a-z0-9_-]+ werden mit 400 abgelehnt, ohne patch() aufzurufen."""
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(tmp_path) as client:
            resp = client.patch(f'/api/kampagne/{bad_camp}/value', json={
                'kind': 'section_body',
                'file': 'session.md',
                'section': 'Verlauf',
                'value': 'x',
            })
            assert resp.status_code == 400
            data = resp.get_json()
            assert data == {'error': 'invalid campaign name'}
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    # Nichts darf angelegt worden sein — der Guard greift vor jedem Datei-Zugriff.
    assert not (tmp_path / 'abenteuer').exists()


# ---------------------------------------------------------------------------
# PATCH /api/kampagne/<camp>/value — fehlerhafter JSON-Body
# ---------------------------------------------------------------------------

def test_patch_kampagne_route_malformed_json_returns_400(tmp_path):
    """Kaputtes JSON im Body → Flask antwortet 400, patch() wird nie erreicht."""
    campaign = 'drachenchronik'
    _write_kampagne_file(tmp_path, campaign, 'session.md')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(tmp_path) as client:
            resp = client.patch(
                f'/api/kampagne/{campaign}/value',
                data='das ist kein JSON',
                content_type='application/json',
            )
            assert resp.status_code == 400
    finally:
        server_mod.VAULT_ROOT = original_vault_root
