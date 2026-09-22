# Sprint 033 — CSRF-Schutz für schreibende Routen + Logging verschluckter Fehler (D-065, D-066)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-065/D-066 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-033/plan.md |
| T1 | D-065: `POST /api/commit` verlangt `application/json` (415 sonst); app-weiter `before_request`-Origin-Check für alle schreibenden Methoden (403 bei fremdem/`null`-Origin, GET/HEAD/OPTIONS unbetroffen). Bestehende `test_commit.py`-Tests (Body-loser POST) auf `json={}` umgestellt, da sie den alten Vertrag pinnten. Neue Tests: text/plain → 415 + kein Commit; fremder Origin → 403 + kein Commit; `Origin: null` → 403; gleicher Origin → 200; PATCH mit fremdem Origin → 403 + Datei unverändert. | ✅ done | server.py, tests/test_commit.py, tests/test_server.py |
| T2 | D-066: `app.logger.warning(...)` an 4 Stellen (api_held FileNotFoundError, api_etag FileNotFoundError, api_commit Git-Stderr, CSRF-Hook-Abweisungen inkl. 415) — Response-Body bleibt generisch. Tests mit `caplog`: (a) Record enthält den vollen Grund, (b) Body weiterhin ohne (Dual-Assertion `str(tmp_path) not in body` + Windows-Laufwerksbuchstaben-Regex). Git-Fehler via stale `.git/index.lock` (Muster D-064). | ✅ done | server.py, tests/test_server.py, tests/test_commit.py |
| T3 | Verifikation (volle Suite + `-W error` nach `__pycache__`-Löschen) + Gesamt-Review (Scratch-Kopie-Repro CSRF-Angriff vor/nach Fix, neue Tests gegen ungefixten Stand); D-067 (Host-Allowlist/DNS-Rebinding) filen | ✅ done | verification.md, BACKLOG.md |

## Rulings (User, AskUserQuestion in der Sprint-Planung)

- **CSRF-Umfang:** JSON-Pflicht auf `/api/commit` + app-weiter Origin-Check für alle schreibenden Methoden. Host-Allowlist/DNS-Rebinding bewusst nicht in diesem Sprint → neues EPIC **D-067**.
- **Logging-Umfang:** alle 3 verschluckten Fehler (`api_held`, `api_etag` — letzterer stand nicht im Ticket-Wortlaut, aber dieselbe Fehlerklasse — und `api_commit`) plus die CSRF-Abweisungen aus D-065.

## Befund (Grundlage für T1/T2)

- **D-065:** `api_commit()` (`server.py:143-154`) liest den Body per `request.get_json(silent=True)`, toleriert also auch Nicht-JSON-Bodies. Ein Cross-Origin-Formular-POST (`enctype=text/plain`, kein Preflight nötig) erreicht die Route trotzdem und committet real. Die beiden PATCH-Routen (`api_patch_value`, `api_patch_kampagne`) sind bereits durch ihre HTTP-Methode geschützt — ein Cross-Origin-PATCH löst immer einen Preflight aus, den der Server (keine CORS-Header) ablehnt.
- **D-066:** `api_held` (Z. 78, `except FileNotFoundError`) und `api_etag` (Z. 94, identisches Muster) verwerfen den Grund der 404-Antwort kommentarlos; `api_commit` (Z. 149) verwirft `result['error']` (rohen Git-Stderr, seit D-064 nicht mehr in der Antwort). Kein Logging-Setup im Projekt außer `parsers/wikiartikel.py` (`logging.getLogger(__name__)`, Muster für `app.logger`).

## Key Design Decisions

- Origin-Check als app-weiter `before_request`-Hook (nicht pro Route) — deckt künftige schreibende Routen automatisch ab, statt die Fehlerklasse endpunktweise nachzuziehen (Lehre aus D-062→D-063→D-064).
- Fehlender Origin-Header wird zugelassen (Tests, `curl`, CLI-Clients senden i. d. R. keinen); die JSON-Pflicht auf `/api/commit` bleibt die eigentliche Sperre gegen den Formular-POST-Vektor, der ohne Origin-Header funktionieren würde.
- Keine CORS-Header gesetzt — Preflights scheitern weiterhin wie bisher.
- `git_ops.commit_helden()`s Rückgabe-Kontrakt bleibt unverändert (D-064-Präzedenz); Logging liest `result['error']` nur in `server.py`, loggt es, gibt es aber weiterhin nicht in der JSON-Antwort aus.
- Logging über `app.logger` (Flask-Default-Handler, stderr) — keine Log-Datei, keine neue Konfiguration.
- Status-Codes: 415 für fehlendes/falsches Content-Type auf `/api/commit`, 403 für Origin-Verstoß, unverändert 500 für echte Git-Fehler.

## Out of Scope

- Host-Allowlist/DNS-Rebinding-Schutz → **D-067** (neu gefiled in T3).
- CSRF-Tokens — für ein lokales Single-User-Tool reichen JSON-Pflicht + Origin-Check.
- Log-Datei/Log-Rotation — nur stderr über `app.logger`.
- Alle unter „Bekannte Einschränkungen" in `sprints/sprint-032/handoff.md` gelisteten Altlasten.
