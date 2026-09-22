# Sprint 031 — Pfad-Leak im `api_held`-Fehlerhandler schließen (D-063)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-063 → in-progress, plan.md) | ✅ done | BACKLOG.md, sprints/sprint-031/plan.md |
| T1 | `api_held`-Fehlerhandler: `FileNotFoundError` → 404 `{'error': 'not found'}` (Muster `api_etag`), bare `except Exception`/`str(exc)` entfernt; Tests für Leak-Fall (kein Pfad im Body), Erfolgsfall (Regression) und Diskriminierung (ein anderer Exception-Typ wird NICHT abgefangen, propagiert zu Flasks generischem 500) | ✅ done | server.py, tests/test_server.py |
| T2 | Verifikation (volle Suite + `-W error`) + Gesamt-Review + `/sprint-wrap` | ⬜ todo | — |

## Befund (Grundlage für T1)

Sprint 030 schloss den `slug_param`-Path-Traversal-Vektor (D-062). Beim
unabhängigen Exploit-Repro in einem Scratch-Worktree gegen den *ungefixten*
Stand (`eeb8736`) fand die Gesamtreview einen zweiten, unabhängigen Fund:
`api_held`s bare `except Exception as exc: return jsonify({'error':
str(exc)}), 500` (`server.py:78-79`) reicht die volle Exception-Message —
inklusive absolutem Dateisystempfad — direkt an den HTTP-Client durch. Das
gilt für **jede** Exception aus `load_held()`/`load_kampagne()`, nicht nur
für Traversal-Fälle: bereits ein syntaktisch gültiger, aber nicht
existierender Slug (z. B. `/api/held/does-not-exist`, besteht
`_valid_slug()` anstandslos) lässt `load_held()` beim `read_text()` von
`_illaen.md` ein `FileNotFoundError` mit vollem Pfad werfen, das ungefiltert
in der JSON-Antwort landet. Der Fund ist vorbestehend, nicht durch D-062
eingeführt, und wurde als eigenes Ticket D-063 gefiled (gleiches Muster wie
D-062 selbst aus D-061 heraus).

Code-Verifikation vor Task-Dispatch:
- `server.py:70-79` (`api_held`): einziger bare `except Exception`-Handler
  im ganzen File, der `str(exc)` in die JSON-Antwort setzt.
- `server.py:87-95` (`api_etag`) hat bereits das Zielmuster: `except
  FileNotFoundError: return jsonify({'error': 'not found'}), 404` — keine
  Exception-Message im Body.
- `app.run(..., debug=False, ...)` (`server.py:168`): jede Exception, die
  *nicht* abgefangen wird, fällt auf Flasks Standard-500-Handler durch, der
  im Nicht-Debug-Modus generisch antwortet — kein Leak, kein zusätzlicher
  Blanket-Catch nötig.
- `load_kampagne()` wird in `api_held` nur mit dem festen Literal
  `'drachenchronik'` aufgerufen (nicht attacker-controlled), kann aber bei
  einem race-artigen Verzeichnis-Zustand ebenfalls `FileNotFoundError`
  werfen — vom selben Fix mitabgedeckt.

D-063 ist der einzige sofort startbare Eintrag in `helden/_tools/BACKLOG.md`
(Effort S, Blocked by `—`); das Vault-weite `backlog.md` ist leer. Sprint 031
bleibt daher bewusst auf dieses eine EPIC beschränkt (gleiches Muster wie
Sprint 030).

## Key Design Decisions

- **Fix-Ansatz: gezielt `FileNotFoundError` abfangen (Ticket-Option 2), kein
  generischer „Fehlermeldung ohne `str(exc)`"-Blanket-Catch (Option 1).**
  Grund: `api_etag` etabliert dieses Muster bereits im selben File — Fix
  folgt bestehender Konvention statt eine zweite Fehlerbehandlungs-Strategie
  einzuführen. Jede nicht-`FileNotFoundError`-Exception fällt auf Flasks
  eigenen, bereits sicheren 500-Handler durch (`debug=False`) — kein neuer
  Blanket-Catch, der versehentlich wieder Details leaken könnte.
- **Kein Logging-Ausbau.** Der Server hat aktuell keine Logging-Infrastruktur;
  „verschluckte" Exceptions server-seitig protokollieren wäre ein separates,
  größeres EPIC (siehe Out of Scope), nicht Teil des S-Fixes.
- **Diskriminierender Test statt reinem Positiv-Test.** Gelernte Lehre aus
  Sprint 029/030 (vakuose Tests): ein Test muss zeigen, dass der Fix nicht
  einfach zu einem anderen Blanket-Catch geworden ist — ein gemockter/
  erzwungener Exception-Typ ≠ `FileNotFoundError` muss weiterhin
  durchschlagen (kein stiller Catch-all mehr vorhanden).

## Out of Scope

- Server-seitiges Logging verschluckter Exceptions (kein bestehendes
  Logging-Setup; eigenes EPIC bei Bedarf).
- `api_patch_kampagne`s Inline-Campaign-Regex-DRY-Nit (Sprint-030-Gesamtreview,
  bewusst als „defensible as-is" geparkt).
- Alle unter „Bekannte Einschränkungen" in `sprints/sprint-030/handoff.md`
  gelisteten Altlasten (Druckdialog, Session-Format-Kopplung, Touch-Tooltips,
  …) — keine davon ist ein gescopter Backlog-Eintrag, D-063 füllt den Sprint
  bereits vollständig aus.
