# Sprint 033 — Verifikation

## Test Suite

- `pytest tests/ -q` nach `__pycache__`-Löschen: **698 passed** (19,70s)
- `pytest tests/ -q -W error` nach erneutem `__pycache__`-Löschen: **698 passed**, keine Warnungen (19,82s)
- Verlauf: 688 (Sprint-032-Stand) → 693 (T1/D-065, +5) → 698 (T2/D-066, +5)

## Static Render

- `python render-held.py illaen-baernhold` — exit 0, `output/illaen-baernhold-dashboard.html` erfolgreich geschrieben
- `git status --short` zeigt keine Diff auf `output/` — erwartet, da beide Tasks ausschließlich `server.py`/Tests ändern, kein Template-/Render-Code

## Task-Reviews

- **T1 (D-065):** Sonnet, Spec ✅, 0 Critical/Important, 2 Minor (no-action-needed), Approved — kein Fix-Loop.
- **T2 (D-066):** Sonnet, Spec ✅, 0 Critical/Important, 2 Minor (no-action-needed), Approved — kein Fix-Loop.

## Gesamt-Review (Opus)

**Ready to merge: Yes.** 0 Critical, 0 Important.

Empirische Verifikation in einer isolierten Scratch-Kopie (`git archive` bei
`0bdbb48`/pre-fix und `b46ac14`/post-fix, jeweils eigener temporärer
Ordner außerhalb des Projekt-Trees) — echte Flask-Server gegen
Throwaway-Fixture-Repos, rohe `http.client`-Requests, Commit-Anzahl +
Datei-Bytes vor/nach jedem Request gemessen:

| Szenario | Pre-Fix | Post-Fix |
|---|---|---|
| text/plain-POST, fremder Origin | 200, Commit | 403, kein Commit |
| text/plain-POST, kein Origin | 200, Commit | **415**, kein Commit |
| urlencoded, fremder Origin | 200, Commit | 403 |
| JSON, Origin fremd/`null`/leer | 200, Commit | 403 jeweils |
| Same-Origin via `127.0.0.1` und `localhost` | 200 | 200, Commit (beide funktionieren) |
| Cross localhost↔127, https, falscher Port, Trailing `/`, Großschreibung Schema | 200 | 403 jeweils |
| Kleingeschriebene Methode `post` | 200 | 403 (Werkzeug normalisiert) |
| PATCH `/value`, fremder Origin (JSON + text/plain) | 200, Datei überschrieben | 403, Datei unverändert |
| OPTIONS-Preflight | 200, nur `Allow`, keine `Access-Control-*` | unverändert |
| **DNS-Rebinding (Host = Origin = Angreifer-Hostname)** | 200, Commit | **200, Commit — Lücke bleibt** |

- 9 von 10 neuen Tests schlagen gegen den ungefixten Stand fehl (diskriminieren
  korrekt); der 10. (Same-Origin) ist die bereits von T1 offengelegte,
  nicht-diskriminierende Ausnahme (kann pre-/post-fix nicht unterscheiden,
  weil beide 200 liefern).
- Gezielt einzelne Fix-Bestandteile deaktiviert: ohne die 5 Logging-Calls
  schlagen genau die 5 D-066-Tests fehl; ohne Origin-Check schlagen 4 Tests
  fehl; ohne `is_json`-Check schlagen 2 Tests fehl — jeder Fix-Bestandteil ist
  durch mindestens einen Test abgedeckt.
- `-W error` auf den betroffenen Testdateien in der Scratch-Kopie: 57 passed
  (mit `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` wegen einer projektfremden
  ipykernel-Warnung).

3 neue Minor (keine Blocker): fehlender Test für `%r`-Escaping von
CR/LF in einem feindlichen Origin-Header in den Log-Zeilen; `api_commit`
loggt Git-Stderr via `%s` statt `%r` (kein Client-Reflect, geringes Risiko);
Großschreibungs-Schema (`HTTP://...`) wird abgelehnt (Browser senden das nie,
nur ein False-403 für handgebaute Clients).

Ledger-Minor-Triage: alle 4 aus T1/T2 deferred als "no action needed"
bestätigt.

**Neu gefunden, bewusst nicht mitgefixt (User-Ruling in der Sprint-Planung):**
DNS-Rebinding umgeht den Origin-Check vollständig, empirisch bestätigt
(echter Commit + echtes Datei-Überschreiben, zusätzlich Lese-Leak nach
Rebind über GET-Routen) → **D-067** neu gefiled.

## Scope-Bestätigung

- `api_patch_kampagne` (PATCH `/api/kampagne/<camp>/value`) profitiert vom
  selben app-weiten Origin-Hook wie `api_patch_value` — kein separater Fix
  nötig, per Konstruktion (Hook ist nicht routen-gescoped).
- Keine CORS-Header hinzugefügt — Preflights scheitern weiterhin wie vor
  diesem Sprint (Gesamtreview-Szenario „OPTIONS-Preflight" bestätigt).
