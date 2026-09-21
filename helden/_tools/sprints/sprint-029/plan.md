# Sprint 029 — Path-Traversal-Fix (D-061)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-061 → in-progress, D-062 neu anlegen, plan.md) | ✅ done | BACKLOG.md, sprints/sprint-029/plan.md |
| T1 | D-061: Path-Traversal-Fix (`_safe_join` + campaign-Validierung in `_resolve_base`) + Tests | ✅ done | writers/held_writer.py, tests/test_held_writer.py, tests/test_server.py |
| T2 | Verifikation + `/sprint-wrap` | ✅ done (Verifikation; `/sprint-wrap` selbst folgt separat) | verification.md, handoff.md |

## Befund (Grundlage für T1)

**`helden/_tools/writers/held_writer.py`**
- `patch()` (Zeile 76): `target = base / rel_file` — `rel_file = locator.get('file', '')`
  kommt ungeprüft aus dem JSON-Body. Ein Wert wie `../../../irgendwo` (relative
  Traversal) oder `C:\Windows\win.ini` (absoluter Pfad — pathlib ersetzt bei Join mit
  einem absoluten Pfad den gesamten linken Teil) kann `target` außerhalb von `base`
  auflösen.
- `etag_for()` (Zeile 171): identisches Muster `base / rel_file`.
- `_resolve_base()` (Zeile 194-202): bei `scope='kampagne'` wird `campaign` ungeprüft in
  `vault_root / 'abenteuer' / campaign` eingesetzt. Für die Route
  `/api/kampagne/<camp>/value` validiert `server.py:111` den Wert vorher per
  `re.fullmatch(r'[a-z0-9_-]+', camp)` — **aber** für `/api/held/<slug>/value`
  (server.py:89-94) wird der komplette JSON-Body ungefiltert an `patch()` durchgereicht.
  Ein Aufruf gegen `/api/held/<slug>/value` mit
  `{"scope": "kampagne", "campaign": "../../x", ...}` im Body umgeht den Regex-Guard der
  anderen Route vollständig — dieselbe Fehlerklasse, nur über einen anderen
  Einstiegspunkt.
- Praxisrisiko bleibt gering (Flask bindet nur an `127.0.0.1`, `server.py:154`), aber der
  Fix ist trotzdem klein und sauber machbar.

**Geplanter Fix (in `writers/held_writer.py`):**
1. Neuer privater Helper `_safe_join(base, rel_file)`: löst `(base / rel_file).resolve()`
   auf und prüft per `relative_to(base.resolve())`, dass das Ergebnis unterhalb von `base`
   bleibt; gibt `None` zurück bei leerem `rel_file`, absolutem Pfad oder Traversal-Ausbruch.
2. `patch()`: `target = base / rel_file` → `target = _safe_join(base, rel_file)`, dann
   `if target is None or not target.exists(): return PatchResult(..., error=f'file not found: {rel_file}')`
   — gleiche Fehlermeldung/Status wie bisher für „nicht gefunden", keine neue
   Fehlerkategorie nötig.
3. `etag_for()`: gleiche Umstellung, `target is None` → `raise FileNotFoundError(rel_file)`
   (bestehender Caller in `server.py:82-83` fängt das bereits ab).
4. `_resolve_base()`: bei `scope == 'kampagne'` zusätzlich
   `re.fullmatch(r'[a-z0-9_-]+', campaign or '')` prüfen, sonst `raise ValueError(...)`.
   In `patch()`s bestehendem `except (KeyError, TypeError)` um `ValueError` erweitern,
   damit es als normaler `PatchResult`-Fehler (400) zurückkommt statt als 500.

**Tests** (Muster aus `tests/test_held_writer.py` und `tests/test_server.py` — beide
nutzen bereits `tmp_path`, kein Live-Write):
- `test_held_writer.py`: `patch()` und `etag_for()` mit `file='../outside.md'` und mit
  einem absoluten Pfad → beide lehnen ab, Datei außerhalb `tmp_path` bleibt unberührt.
- `test_held_writer.py`: `patch()` mit `scope='kampagne', campaign='../../x'` → `ValueError`
  wird zu einem `PatchResult(ok=False, ...)`, kein Crash.
- `test_server.py`: PATCH gegen `/api/held/<slug>/value` mit traversal-`file`-Wert → 400,
  Datei außerhalb des Fixture-Vaults bleibt unangetastet (Muster wie
  `test_patch_kampagne_route_rejects_invalid_campaign_name`).
- `test_server.py`: PATCH gegen `/api/held/<slug>/value` mit
  `{"scope":"kampagne","campaign":"../evil"}` im Body → 400 (beweist, dass der Guard
  jetzt auch über diesen Einstiegspunkt greift).

## Key Design Decisions

- Fix deckt beide betroffenen Felder ab, die über denselben `held_writer.py`-Pfad laufen
  (`file` UND `campaign`), nicht nur das im Backlog-Titel genannte `file`-Feld — passend
  zur Projektkonvention „ganze Fehlerklasse, nicht nur der benannte Fall".
- Traversal-Ablehnung liefert dieselbe Fehlermeldung/denselben Status wie „Datei nicht
  gefunden" (kein neuer Fehlertyp, kein Leck der genauen Ursache).
- `slug_param`-Traversal (verwandter, aber separater Fund: `/api/held/<slug_param>/...`
  ist nirgends gegen `..`-Werte geprüft) wird NICHT mitgefixt, sondern als neuer Eintrag
  D-062 im Backlog dokumentiert (gleiches Muster wie D-061 selbst, das aus D-059 heraus
  entdeckt und separat eingetragen wurde).

## Out of Scope

- **D-062 (slug_param-Traversal)** — neu entdeckt, eigener Fix + eigene Tests nötig,
  bewusst als separater Sprint-Kandidat statt Scope-Erweiterung von D-061.
- **Echter Druckdialog-Test, D-058-Seitenumbruch-Nachprüfung, Session-Inhalts-Sichtung,
  `/session-compile`-Mängel, Touch-Tooltips, Desktop-Footer ≤480px, SF-Vorschau-
  Randfälle** — alle aus Sprint 028s „Bekannte Einschränkungen", User hat sich für einen
  schlanken Ein-Item-Sprint entschieden (bestätigt in der Sprint-Planung).
