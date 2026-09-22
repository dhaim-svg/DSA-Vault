# Sprint 032 — Pfad-Leak im `api_commit`-Fehlerpfad schließen (D-064)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-064 → in-progress, plan.md) | ✅ done | BACKLOG.md, sprints/sprint-032/plan.md |
| T1 | `api_commit`: rohen Git-Stderr-Text nicht mehr in die JSON-Antwort durchreichen — Fix an der HTTP-Grenze (Muster D-063), `git_ops.commit_helden`s Rückgabe-Kontrakt bleibt unverändert. Neuer Test erzwingt einen echten Git-Fehler mit pfad-tragendem Stderr (stale `.git/index.lock`, identisches Szenario wie im Backlog-Titel) und prüft die Abwesenheit sowohl von `str(tmp_path)` als auch eines Windows-Laufwerkspfad-Musters im Body (Dual-Assertion, Lehre aus Sprint 031: eine reine `str(tmp_path) not in body`-Prüfung kann auf Windows vakuos gegen den ungefixten Code bestehen). Erfolgs-Regressionstest (bestehender `test_api_commit_route_returns_json` + `commit_helden`-Unit-Tests) bleibt grün. | ✅ done | server.py, tests/test_commit.py |
| T2 | Verifikation (volle Suite + `-W error` nach `__pycache__`-Löschen) + Gesamt-Review | ⬜ todo | verification.md |

## Befund (Grundlage für T1)

Sprint 031 schloss D-063 (`api_held`s Pfad-Leak im Fehlerhandler). Bei der
Gesamtreview-Verifikation dieses Fixes (Scratch-Kopie, empirischer
Fehler-Body-Vergleich) fand sich ein zweiter, unabhängiger, vorbestehender
Leak: `api_commit`s Fehlerpfad (`server.py:149`,
`jsonify({'ok': False, 'error': result.get('error', 'unknown error')}), 500`)
reicht `result['error']` direkt durch. `git_ops.py` füllt dieses Feld an
zwei Stellen mit unbereinigtem `subprocess`-Stderr:

- Zeile 45 (`git add` schlägt fehl): `{'ok': False, 'error': add_result.stderr or add_result.stdout}`
- Zeile 62 (`git commit` schlägt fehl, kein „nothing to commit"): `{'ok': False, 'error': commit_result.stderr or commit_result.stdout}`

Ein stale `.git/index.lock` (z. B. durch einen abgebrochenen vorherigen
Commit) liefert `fatal: Unable to create '<absoluter Vault-Pfad>/.git/index.lock':
File exists.` — der volle Windows-Dateisystempfad landet ungefiltert im
HTTP-Response-Body. HTTP-erreichbar über `POST /api/commit`
(`static/commit.js:20`). Gleiche Fehlerklasse wie D-063, anderer
Endpunkt/anderes Feld, bewusst nicht in D-063 mitgefixt (Ticket-Scope).

Code-Verifikation vor Task-Dispatch:
- `server.py:144-154` (`api_commit`): einziger Ort, der `result['error']`
  aus `commit_helden()` in eine JSON-Antwort setzt.
- `git_ops.py`: Docstring dokumentiert den Kontrakt bereits akkurat
  („On git error: `{'ok': False, 'error': <stderr text>}`") — das ist ein
  bewusster interner Rückgabewert, keine versehentliche Exception-Message
  wie bei D-063. Einziger Importeur von `commit_helden` ist `server.py`.
- `tests/test_commit.py`: bestehende Tests (`test_commit_helden_success`,
  `test_commit_helden_nothing_to_commit`, `test_commit_helden_adds_helden_subpath`,
  `test_api_commit_route_returns_json`) decken nur Erfolgs-/
  Nothing-to-commit-Fälle ab, keinen Fehlerfall mit Pfad-Leak.
- `tests/test_server.py:415-494`: D-063s Fix- und Test-Muster
  (`except FileNotFoundError` an der Route, Dual-Assertion
  `str(tmp_path) not in body` + Windows-Laufwerksbuchstaben-Regex) — hier
  gespiegelt, angepasst an den Dict-Rückgabewert statt eine Exception.

D-064 ist der einzige sofort startbare Eintrag in `helden/_tools/BACKLOG.md`
(Effort S, Blocked by `—`); das Vault-weite `backlog.md` ist leer. Sprint 032
bleibt daher bewusst auf dieses eine EPIC beschränkt (gleiches Muster wie
Sprint 029–031).

## Key Design Decisions

- **Fix-Ort: HTTP-Grenze in `server.py`, nicht `git_ops.py`.** Exakt das
  D-063-Präzedenzmuster: `load_held()`s `FileNotFoundError` behält intern
  den vollen Pfad, nur `server.py`s Route filtert ihn vor dem `jsonify()`.
  Hier analog: `commit_helden()`s Rückgabe-Kontrakt bleibt exakt wie er ist
  — `api_commit()` liest `result['error']` einfach nicht mehr in die
  Response, sondern setzt eine feste, generische Fehlermeldung.
- **Eine generische Fehlermeldung, keine Stage-Unterscheidung
  (add vs. commit).** `git_ops.py` gibt für beide Fehlerfälle dieselbe
  Dict-Form zurück, ohne zu markieren, welcher Schritt fehlschlug. Eine
  Unterscheidung ließe sich nachrüsten (neues `stage`-Feld), ist aber für
  ein lokales Single-User-Tool ohne bestehenden zweiten Konsumenten von
  `commit_helden()` unnötiger Umfang für einen S-Fix — Parallele zu D-063s
  einzelnem `'not found'` statt mehrerer Fehlermeldungs-Varianten.
- **Status-Code bleibt 500.** Anders als D-063 (wo `FileNotFoundError` zu
  einem legitimen Client-Fall wurde, daher 404) ist ein Git-Fehler weiterhin
  ein echter Server-Fehler — nur der Body-Inhalt ändert sich, nicht der Code.
- **Kein Logging-Ausbau.** Konsistent mit der wiederholten Projekt-Ruling aus
  D-054/D-063: kein bestehendes Logging-Setup, der verworfene Stderr-Text
  wird nicht protokolliert, nur fallengelassen.
- **Repro-Mechanismus für den Test: stale `.git/index.lock`.** Deterministisch,
  plattformunabhängig, erzeugt zuverlässig eine Stderr-Meldung mit dem vollen
  Repo-Pfad — exakt das im Backlog-Titel zitierte Szenario, kein Mocking von
  `subprocess` nötig.

## Out of Scope

- Andere Endpunkte auf dieselbe Fehlerklasse absuchen (`api_patch_value`/
  `api_patch_kampagne` geben ebenfalls `result.error` aus `held_writer.patch()`
  zurück). Projekt-Lehre aus dem Sprint-031-Handoff: „ein einzelner Sprint
  sollte nicht versuchen, die ganze Fehlerklasse projektweit auf einmal zu
  jagen, ohne dass eine Review sie konkret benennt" — nur D-064 ist
  reviewer-identifiziert und gescopt.
- `git_ops.py`s Rückgabe-Kontrakt/Docstring ändern oder ein `stage`-Feld
  einführen (s. Key Design Decisions).
- Alle unter „Bekannte Einschränkungen" in `sprints/sprint-031/handoff.md`
  gelisteten Altlasten (Druckdialog, Session-Format-Kopplung, Touch-Tooltips,
  verschluckte `FileNotFoundError` ohne Server-Log, …) — keine davon ist ein
  gescopter Backlog-Eintrag, D-064 füllt den Sprint bereits vollständig aus.
