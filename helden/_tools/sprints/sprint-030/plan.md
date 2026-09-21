# Sprint 030 — `slug_param`-Traversal schließen (D-062)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-062 → in-progress, plan.md) | ⬜ todo | BACKLOG.md, sprints/sprint-030/plan.md |
| T1 | `slug_param`-Guard auf allen 5 Routen (`_valid_slug`-Helper + Route-Checks in server.py) + diskriminierende Traversal-/Regressionstests | ⬜ todo | server.py, tests/test_server.py |
| T2 | Verifikation + `/sprint-wrap` | ⬜ todo | — |

## Befund (Grundlage für T1)

`_safe_join`s Containment-Check (D-061) prüft relativ zu `base` — greift hier nicht,
weil `slug_param` selbst `base` verschiebt: `_resolve_base()` (und
`parsers/held.py::load_held()`) bauen `vault_root / 'helden' / slug` ungeprüft.
`slug_param='..'` → `base == vault_root`. Empirisch bestätigt (Sprint-029-
Gesamtreview): `PATCH /api/held/../value` → HTTP 200, echtes Überschreiben einer
`.md`-Datei im Vault-Root.

Recherche während der Planung erweitert den Ticket-Titel-Scope: dieselbe ungeprüfte
`slug`/`s`-Variable erreicht denselben Join über **zwei Funktionsfamilien**:
1. `writers/held_writer.py::_resolve_base()` → `patch()`, `etag_for()`, `mtime_map()`
   → Routen `/api/held/<slug_param>/value` (PATCH), `/mtime`, `/etag`.
2. `parsers/held.py::load_held()` → direkt in der `api_held`-Route **und** über
   `build_context()`/`_render_dashboard()` in **`/held/<path:s>`** (Seiten-Route, nicht
   im Ticket-Titel genannt, aber exakt dieselbe Fehlerklasse — kein Client-JS ruft sie
   auf, aber HTTP-erreichbar).

→ Fix deckt alle 5 Routen ab: `api_held`, `api_mtime`, `api_etag`,
`api_patch_value`, `held_page`.

**Geplanter Fix (in `server.py`):**
1. Neuer Helper `_valid_slug(s)`: `bool(re.fullmatch(r'[a-z0-9_-]+', s or ''))` —
   identisches Pattern zum bestehenden Campaign-Guard (`server.py:111`,
   `held_writer.py:203`).
2. Jede der 5 Routen prüft `slug_param`/`s` als erste Zeile:
   - `api_held`, `api_mtime`, `api_etag`, `api_patch_value` → bei Fehlschlag
     `jsonify({'error': 'invalid slug'}), 400` (Muster: `api_patch_kampagne`).
   - `held_page` → bei Fehlschlag `abort(404)` (Muster: `chronik_bild`).

**Tests** (Muster aus `tests/test_server.py`, `_client()`/`_write_held_file()`
wiederverwenden):
- Traversal-PoC nachbauen: `slug_param='..'` gegen `/value` (PATCH) mit einer echten
  Opfer-`.md`-Datei im Fixture-Vault-Root → 400, Opferdatei-Inhalt unverändert
  (Datei-Diff, nicht nur Status-Code — Sprint-029-Lehre gegen vakuose Tests).
- Parametrisierte ungültige Slugs (Großbuchstabe, Leerzeichen, Punkt, `..`, `../x`)
  gegen mindestens `/value` und `held_page`.
- Je eine Regression mit validem Slug (`illaen-baernhold` oder `test-held`) pro
  Routentyp, die weiterhin normal funktioniert.

## Key Design Decisions

- **Guard-Ort: nur Route-Ebene in `server.py`** — kein zusätzlicher Funktions-Level-
  Guard in `_resolve_base`/`load_held`. Anders als bei D-061s Campaign-Feld (das über
  einen JSON-Body-Bypass einen zweiten HTTP-Eintrittspunkt hatte) kommt `slug`/`s`
  ausschließlich aus dem URL-Segment — ein Routen-Guard deckt die komplette aktuell
  erreichbare Angriffsfläche ab.
- Ein gemeinsamer `_valid_slug()`-Helper statt 5× denselben Regex-Literal (der
  Campaign-Guard ist bewusst 2× dupliziert — Route + `_resolve_base` — aus dem oben
  genannten Grund; hier gäbe es dafür keinen Grund).
- `held_page`/`/held/<path:s>` wird bewusst mitgefixt, obwohl nicht im Ticket-Titel
  genannt (gleiche Fehlerklasse, gleiche Variable) — Konvention „ganze Fehlerklasse,
  nicht nur der benannte Fall" (Sprint 026/029).

## Out of Scope

- **Funktions-Level-Guard in `_resolve_base`/`load_held`** — s. Key Design Decisions,
  kein bekannter HTTP-Bypass, der ihn nötig macht.
- **„Bekannte Einschränkungen" aus dem Sprint-029-Handoff** (echter Druckdialog,
  D-058-Seitenumbruch, SF-Vorschau-Randfälle, Desktop-Footer ≤480px,
  `/session-compile`-Mängel, u. a.) — unscoped Prosa-Notizen, kein konkretes Ticket.
- **Vault-`backlog.md`** — weiterhin leer, kein B-Task diesen Sprint.
