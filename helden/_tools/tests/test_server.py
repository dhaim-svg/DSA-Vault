"""Tests fuer die Flask-Route /api/kampagne/<camp>/value (PATCH — 'Verlauf speichern').

Routen-Tests fuer server.py hatten noch keine feste Heimat (test_commit.py und
test_chronik_bild.py besitzen je eine einzelne Route); diese Datei startet eine fuer
/api/kampagne. Muster folgt test_commit.py:107-131 — tmp_path-Fixture + VAULT_ROOT-
Monkeypatch, im finally zurueckgesetzt, sodass der echte Vault nie beruehrt wird.
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
    """Legt eine Datei unter abenteuer/<campaign>/ (innerhalb von tmp_path) an und gibt den Pfad zurueck."""
    target = tmp_path / 'abenteuer' / campaign / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    return target


def _client(slug: str = 'illaen-baernhold'):
    """Erstellt einen Flask-Test-Client. Patcht KEIN VAULT_ROOT — das erledigt der Aufrufer
    selbst davor (in try/finally, s. Call-Sites), damit es sich zuverlaessig zuruecksetzen laesst."""
    app = server_mod.create_app(slug)
    app.config['TESTING'] = True
    return app.test_client()


def _write_held_file(tmp_path: Path, slug: str, filename: str, content: str = FIXTURE_TEXT) -> Path:
    """Legt eine Datei unter helden/<slug>/ (innerhalb von tmp_path) an und gibt den Pfad zurueck."""
    target = tmp_path / 'helden' / slug / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding='utf-8')
    return target


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
        with _client() as client:
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
    # Nachbar-Abschnitte und die Ueberschrift selbst bleiben unangetastet
    assert '## Verlauf' in updated
    assert '## Hintergrund' in updated
    assert 'Kampagnenhintergrund hier.' in updated
    assert '## Notizen' in updated
    assert 'Weitere Notizen.' in updated


# ---------------------------------------------------------------------------
# PATCH /api/kampagne/<camp>/value — re.fullmatch-Guard auf den Kampagnennamen
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('bad_camp', [
    'Drachenchronik',      # Grossbuchstabe
    'drachen chronik',     # Leerzeichen
    'drachen.chronik',     # Punkt
])
def test_patch_kampagne_route_rejects_invalid_campaign_name(tmp_path, bad_camp):
    """Kampagnennamen ausserhalb von [a-z0-9_-]+ werden mit 400 abgelehnt, ohne patch() aufzurufen."""
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
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
        with _client() as client:
            resp = client.patch(
                f'/api/kampagne/{campaign}/value',
                data='das ist kein JSON',
                content_type='application/json',
            )
            assert resp.status_code == 400
    finally:
        server_mod.VAULT_ROOT = original_vault_root


# ---------------------------------------------------------------------------
# PATCH /api/held/<slug_param>/value — Path-Traversal-Guard (D-061)
# ---------------------------------------------------------------------------

def test_patch_held_route_rejects_path_traversal(tmp_path):
    """Anders als /api/kampagne hat diese Route keinen Regex-Guard vor patch() —
    der Schutz muss also aus held_writer.py selbst kommen. Traversal im file-Feld
    -> 400, eine ausserhalb der Fixture liegende Datei bleibt unangetastet.

    Die Fremddatei bekommt FIXTURE_TEXT (echter '## Verlauf'-Abschnitt): ohne den
    Guard wuerde die Route ihn klaglos ueberschreiben (200/ok=True) statt zufaellig
    an einer anderen Fehlerursache zu scheitern -- Fehlerfeld wird mitgeprueft."""
    slug = 'test-held'
    _write_held_file(tmp_path, slug, 'x.md')
    outside = tmp_path / 'helden' / 'outside.md'
    outside.write_text(FIXTURE_TEXT, encoding='utf-8')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
            resp = client.patch(f'/api/held/{slug}/value', json={
                'kind': 'section_body',
                'file': '../outside.md',
                'section': 'Verlauf',
                'value': 'boese',
            })
            assert resp.status_code == 400
            data = resp.get_json()
            assert data['ok'] is False
            assert data['error'] == 'file not found: ../outside.md'
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    assert outside.read_text(encoding='utf-8') == FIXTURE_TEXT


def test_patch_held_route_rejects_kampagne_campaign_traversal_in_body(tmp_path):
    """/api/held/<slug>/value reicht den kompletten JSON-Body ungefiltert an patch()
    durch. Ein Body mit scope='kampagne' + traversal-campaign muss trotzdem an
    _resolve_base()s Regex-Guard scheitern (400) -- nicht nur ueber die dedizierte
    /api/kampagne/<camp>/value-Route mit ihrem Route-Level-Regex.

    Die Kampagne zeigt (nach Aufloesung) auf einen echten, existierenden Ordner mit
    echtem '## Verlauf'-Inhalt: ohne den Regex-Guard waere die Datei darin real
    erreichbar und ueberschreibbar -- _safe_join allein greift hier nicht (base und
    target werden konsistent aufgeloest, das '..' bleibt innerhalb des aufgeloesten
    base-Ordners), nur der Regex-Guard auf den Kampagnennamen verhindert den Zugriff."""
    slug = 'test-held'
    victim_dir = tmp_path / 'helden' / 'campaign-traversal-victim'
    victim_dir.mkdir(parents=True)
    victim = victim_dir / 'secret.md'
    victim.write_text(FIXTURE_TEXT, encoding='utf-8')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
            resp = client.patch(f'/api/held/{slug}/value', json={
                'scope': 'kampagne',
                'campaign': '../helden/campaign-traversal-victim',
                'kind': 'section_body',
                'file': 'secret.md',
                'section': 'Verlauf',
                'value': 'boese',
            })
            assert resp.status_code == 400
            data = resp.get_json()
            assert data['ok'] is False
            assert 'invalid campaign name' in data['error']
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    assert victim.read_text(encoding='utf-8') == FIXTURE_TEXT
    # Nichts darf ausserhalb der Fixture angelegt worden sein.
    assert not (tmp_path / 'abenteuer').exists()
