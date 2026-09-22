"""Tests fuer die Flask-Route /api/kampagne/<camp>/value (PATCH — 'Verlauf speichern').

Routen-Tests fuer server.py hatten noch keine feste Heimat (test_commit.py und
test_chronik_bild.py besitzen je eine einzelne Route); diese Datei startet eine fuer
/api/kampagne. Muster folgt test_commit.py:107-131 — tmp_path-Fixture + VAULT_ROOT-
Monkeypatch, im finally zurueckgesetzt, sodass der echte Vault nie beruehrt wird.
"""
import re
import sys
from pathlib import Path

import pytest

TOOLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLS_DIR))

import server as server_mod
from tests.heldfixtures import write_mini_held

FIXTURE_TEXT = """\
## Hintergrund

Kampagnenhintergrund hier.

## Verlauf

Alter Verlauf-Text.
Mehrere Zeilen.

## Notizen

Weitere Notizen.
"""

# Minimal but valid _illaen.md: dashboard.html.j2 hard-requires all 8 Eigenschaften
# keys (held.eigenschaften.MU.aktuell etc., no .get() fallback) to render at all.
MINI_ILLAEN_TEXT = """\
---
name: Test Held
stufe: 1
---

## Eigenschaften & Basiswerte

### Eigenschaften

| Eigenschaft | Mod. | Start | Aktuell |
|-------------|------|-------|---------|
| Mut (MU) | 0 | 12 | 12 |
| Klugheit (KL) | 0 | 12 | 12 |
| Intuition (IN) | 0 | 12 | 12 |
| Charisma (CH) | 0 | 12 | 12 |
| Fingerfertigkeit (FF) | 0 | 12 | 12 |
| Gewandtheit (GE) | 0 | 12 | 12 |
| Konstitution (KO) | 0 | 12 | 12 |
| Körperkraft (KK) | 0 | 12 | 12 |
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


# ---------------------------------------------------------------------------
# slug_param Path-Traversal-Guard (D-062) — _valid_slug() auf allen 5 Routen
# ---------------------------------------------------------------------------
#
# Anders als bei D-061 (file-/campaign-Feld im JSON-Body) liegt die Luecke hier
# in slug_param selbst: slug_param='..' verschiebt schon die Basis-Verzeichnis-
# Aufloesung (vault_root/helden/.. == vault_root), sodass D-061s _safe_join
# (der nur relativ zur -- hier bereits falschen -- base prueft) sie nicht faengt.

def test_patch_held_route_rejects_slug_param_traversal_to_vault_root(tmp_path):
    """Der Sprint-029-Review-PoC: PATCH /api/held/../value verschiebt die Basis auf
    den Vault-Root selbst. Eine echte .md-Datei direkt unter tmp_path (Vault-Root,
    NICHT unter helden/) bekommt FIXTURE_TEXT (echter '## Verlauf'-Abschnitt): ohne
    den slug_param-Guard wuerde die Route sie klaglos ueberschreiben (200/ok=True) --
    empirisch mit einem temporaer deaktivierten Guard bestaetigt (200, ok=True, Datei
    ueberschrieben)."""
    victim = tmp_path / 'root-victim.md'
    victim.write_text(FIXTURE_TEXT, encoding='utf-8')
    (tmp_path / 'helden' / 'test-held').mkdir(parents=True)

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(slug='test-held') as client:
            resp = client.patch('/api/held/../value', json={
                'kind': 'section_body',
                'file': 'root-victim.md',
                'section': 'Verlauf',
                'value': 'boese',
            })
            assert resp.status_code == 400
            data = resp.get_json()
            assert data == {'error': 'invalid slug'}
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    assert victim.read_text(encoding='utf-8') == FIXTURE_TEXT


@pytest.mark.parametrize('bad_slug', [
    'Illaen-Baernhold',   # Grossbuchstabe
    'illaen baernhold',   # Leerzeichen
    'illaen.baernhold',   # Punkt
    '..',                 # Traversal (siehe PoC-Test oben)
])
def test_patch_held_route_rejects_invalid_slug_param(tmp_path, bad_slug):
    """slug_param ausserhalb von [a-z0-9_-]+ wird mit 400 abgelehnt, patch() wird
    nie erreicht -- nichts Neues landet unter tmp_path."""
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
            resp = client.patch(f'/api/held/{bad_slug}/value', json={
                'kind': 'section_body',
                'file': 'x.md',
                'section': 'Verlauf',
                'value': 'x',
            })
            assert resp.status_code == 400
            data = resp.get_json()
            assert data == {'error': 'invalid slug'}
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    assert not (tmp_path / 'helden').exists()


def test_valid_slug_rejects_embedded_slash_traversal():
    """'../outside' (mit '/') laesst sich ueber diese Route nicht als HTTP-Test
    fuehren: <slug_param> nutzt Flasks Standard-'string'-Converter, der nie einen
    '/' erfasst -- Werkzeug dekodiert ein %2F vor dem Routing zurueck in einen
    echten Trenner, wodurch /api/held/..%2Foutside/value nicht mehr auf das
    3-Segment-Muster /api/held/<slug_param>/value passt und -- mit oder ohne
    diesen Guard identisch -- 404 auf Routing-Ebene liefert (empirisch mit
    app.url_map.bind(...).match(...) bestaetigt; ein HTTP-Test dieses Werts waere
    also vakuos). Die Regex-Funktion selbst deckt den Fall trotzdem ab."""
    assert server_mod._valid_slug('../outside') is False


@pytest.mark.parametrize('bad_slug', [
    '..',            # Traversal auf den Vault-Root
    '../outside',    # Anders als bei den API-Routen (Standard-'string'-Converter,
                      # kein '/' moeglich) nutzt /held/<path:s> den 'path'-Converter,
                      # der '/' explizit erfasst -- ohne Guard laeuft dieser Wert
                      # tatsaechlich bis in _render_dashboard('../outside') ->
                      # load_held() -> FileNotFoundError beim Lesen ausserhalb von
                      # helden/ (empirisch mit einem temporaer deaktivierten Guard
                      # bestaetigt); mit dem Guard: sauberes 404 vor jedem Datei-Zugriff.
])
def test_held_page_route_rejects_invalid_slug_param(tmp_path, bad_slug):
    """GET /held/<path:s> mit ungueltigem slug -> 404 (analog zum chronik_bild()-
    Muster in derselben Datei: abort(404) auf einer Nicht-JSON-Route)."""
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
            resp = client.get(f'/held/{bad_slug}')
            assert resp.status_code == 404
    finally:
        server_mod.VAULT_ROOT = original_vault_root


@pytest.mark.parametrize('suffix', ['', '/mtime', '/etag'])
def test_api_held_read_routes_reject_invalid_slug_param(tmp_path, suffix):
    """api_held/api_mtime/api_etag: derselbe 400-JSON-Guard wie bei PATCH /value,
    hier stichprobenartig fuer alle drei GET-Lese-Routen mit demselben Traversal-Wert."""
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
            resp = client.get(f'/api/held/..{suffix}')
            assert resp.status_code == 400
            assert resp.get_json() == {'error': 'invalid slug'}
    finally:
        server_mod.VAULT_ROOT = original_vault_root


# ---------------------------------------------------------------------------
# D-062 Regression — gueltige Slugs funktionieren weiterhin
# ---------------------------------------------------------------------------

def test_api_mtime_route_accepts_valid_slug(tmp_path):
    """Regression: der neue Guard darf legitime Requests nicht blockieren.
    api_mtime hatte bisher noch keinen Routen-Test in dieser Datei."""
    slug = 'test-held'
    md_file = _write_held_file(tmp_path, slug, 'x.md')

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(slug=slug) as client:
            resp = client.get(f'/api/held/{slug}/mtime')
            assert resp.status_code == 200
            data = resp.get_json()
            assert data == {'x.md': md_file.stat().st_mtime}
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_held_page_route_accepts_valid_slug(tmp_path):
    """Regression (Seiten-Route): ein vollstaendiger, gueltiger Bogen wird weiterhin
    gerendert (200, kein 404 durch den neuen Guard). write_mini_held() statt
    _write_held_file(), weil held_page() ueber render_dashboard()/load_held() alle
    9 Held-Dateien braucht und das Template alle 8 Eigenschaften-Keys hart voraussetzt."""
    slug = 'test-held'
    write_mini_held(tmp_path, slug=slug, illaen=MINI_ILLAEN_TEXT)

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(slug=slug) as client:
            resp = client.get(f'/held/{slug}')
            assert resp.status_code == 200
            assert 'Test Held' in resp.get_data(as_text=True)
    finally:
        server_mod.VAULT_ROOT = original_vault_root


# ---------------------------------------------------------------------------
# GET /api/held/<slug_param> — Pfad-Leak im Fehlerhandler (D-063)
# ---------------------------------------------------------------------------
#
# api_held() hatte als einzige Route einen bare `except Exception as exc: ...
# str(exc)`-Handler. Ein nicht existierender (aber syntaktisch gueltiger) Slug
# liess load_held() ein FileNotFoundError mit dem vollen Dateisystempfad werfen,
# das ungefiltert in der JSON-Antwort landete. Fix: exakt das api_etag()-Muster
# (except FileNotFoundError -> 404/'not found').

def test_api_held_route_missing_slug_returns_404_without_path_leak(tmp_path):
    """Testfall (a): ein syntaktisch gueltiger, aber nicht existierender Slug besteht
    _valid_slug(), hat aber keinen helden/<slug>/-Ordner -> load_held() wirft
    FileNotFoundError. Muss als generisches 404 ankommen, nicht als 500 mit dem
    vollen tmp_path-Dateisystempfad im Body (der alten str(exc)-Form)."""
    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client() as client:
            resp = client.get('/api/held/does-not-exist')
            assert resp.status_code == 404
            assert resp.get_json() == {'error': 'not found'}

            body = resp.get_data(as_text=True)
            # Nicht nur den erwarteten Body pruefen -- explizit die AFWESENHEIT
            # jedes Dateisystempfads, auch in einem dritten, unerwarteten Feld.
            # Hinweis (Gesamtreview Sprint 031): auf Windows landet der Pfad im
            # alten str(exc)-Leak doppelt escaped (repr() in der errno-Message,
            # dann JSON) -- die folgende str(tmp_path)-Prüfung besteht deshalb
            # sogar gegen den ungefixten Code. Der Regex-Assert darunter ist der
            # tatsaechlich diskriminierende Beleg.
            assert str(tmp_path) not in body
            assert not re.search(r'[A-Za-z]:[\\/]', body)  # kein Windows-Laufwerkspfad
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_held_route_valid_slug_returns_held_and_kampagne(tmp_path):
    """Testfall (b): Erfolgs-Regression -- der Fix (except Exception -> except
    FileNotFoundError) darf den Erfolgspfad von api_held() nicht anfassen."""
    slug = 'test-held'
    write_mini_held(tmp_path, slug=slug, illaen=MINI_ILLAEN_TEXT)

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(slug=slug) as client:
            resp = client.get(f'/api/held/{slug}')
            assert resp.status_code == 200
            data = resp.get_json()
            assert 'held' in data
            assert 'kampagne' in data
    finally:
        server_mod.VAULT_ROOT = original_vault_root


def test_api_held_route_non_filenotfound_exception_is_not_swallowed(tmp_path, monkeypatch):
    """Testfall (c), Anti-Blanket-Catch-Beleg: die alte Handler-Form haette JEDE
    Exception mit {'error': str(exc)}/500 abgefangen. Der neue Handler faengt nur
    FileNotFoundError -- eine ValueError aus load_held() muss unbehandelt
    durchschlagen. _client() setzt app.config['TESTING'] = True, wodurch Flasks
    Testclient nicht abgefangene Exceptions propagiert statt sie in eine generische
    500-Antwort umzuwandeln -- pytest.raises() ist hier also der direkte Nachweis,
    dass die ValueError-Nachricht in KEINER Response landet (weder alte str(exc)-
    Form noch irgendein anderer Body)."""
    slug = 'test-held'

    def _boom(*args, **kwargs):
        raise ValueError('boom: geheime interna')

    monkeypatch.setattr(server_mod, 'load_held', _boom)

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(slug=slug) as client:
            with pytest.raises(ValueError, match='boom: geheime interna'):
                client.get(f'/api/held/{slug}')
    finally:
        server_mod.VAULT_ROOT = original_vault_root


# ---------------------------------------------------------------------------
# PATCH /api/held/<slug_param>/value — CSRF-Schutz (D-065)
# ---------------------------------------------------------------------------

def test_patch_held_route_rejects_foreign_origin(tmp_path):
    """Der app-weite before_request-Hook muss auch die PATCH-Route schuetzen,
    nicht nur /api/commit. Ein Cross-Origin-Header -> 403, die Zieldatei bleibt
    byte-identisch (kein patch()-Aufruf hat stattgefunden)."""
    slug = 'test-held'
    target = _write_held_file(tmp_path, slug, 'x.md')
    before = target.read_bytes()

    original_vault_root = server_mod.VAULT_ROOT
    server_mod.VAULT_ROOT = tmp_path
    try:
        with _client(slug=slug) as client:
            resp = client.patch(
                f'/api/held/{slug}/value',
                json={
                    'kind': 'section_body',
                    'file': 'x.md',
                    'section': 'Verlauf',
                    'value': 'boese',
                },
                headers={'Origin': 'http://evil.example'},
            )
            assert resp.status_code == 403
    finally:
        server_mod.VAULT_ROOT = original_vault_root

    assert target.read_bytes() == before
