# Sprint 031 — Verifikation

## Testsuite

- `pytest tests/ -v` (aus `helden/_tools/`, nach `__pycache__`-Löschen,
  Controller-Gegenprobe unabhängig vom Implementierer-Report): **687
  passed**, 18.10s.
- `pytest tests/ -q -W error`: **687 passed**, 16.90s, keine Warnings.
- Baseline vor Sprint 031 (aus Sprint-030-Verifikation): 684.
  684 → 687 (T1, +3 neue Tests aus dem Brief) — kein Fix-Loop nötig, kein
  Test-Delta durch die anschließenden Polish-Fixes (nur Kommentar +
  Entfernung von totem Setup-Code, keine neuen/gelöschten Tests).

## Static Render

- `python render-held.py illaen-baernhold`: exit 0,
  `output/illaen-baernhold-dashboard.html` erzeugt.
- Nicht inhaltlich betroffen — D-063 ändert nur den Fehlerpfad einer
  API-Route in `server.py` (kein Rendering-/Template-Code). `git status
  --short` zeigt keine Diff auf `output/`.

## Git

- `git status --short`: sauber, alle Änderungen committet.
- 5 Commits auf `master` (kein Worktree, kein Push, per Projekt-Konvention):
  - `704d3cc` — T0 Scaffold (D-063 in-progress, plan.md)
  - `995c0d1` — T1 Fix (`except FileNotFoundError` statt `except Exception`
    in `api_held`, Muster `api_etag`) + 3 Tests
  - `8e8aa05` — Controller-Tracker-Update (plan.md T1 ✅)
  - `fee5167` — Controller-Polish (2 Minor-Funde der Gesamtreview: Kommentar
    + toter Setup-Code in `test_server.py`)
  - (dieser Commit) — T2 Verifikation, D-064-Filing

## Review-Kette

- **Task-Review** (Sonnet, Range `704d3cc..995c0d1`): Spec ✅ compliant,
  Task quality Approved. 0 Critical, 0 Important. 1 Minor (dead `mkdir()`
  in Testfall (c)) — geparkt im Ledger, dann per Polish-Commit behoben.
  Reviewer verifizierte unabhängig (nicht nur Report vertraut): `_client()`
  setzt `TESTING=True` (Testclient propagiert unbehandelte Exceptions
  wirklich), `load_held` ist ein Modul-globaler Name (Monkeypatch trifft
  den echten Call-Site), `load_held` wirft tatsächlich `FileNotFoundError`
  bei fehlendem Slug.
- **Gesamt-Review** (Opus, volle Sprint-Range `c42d46e..8e8aa05`): **„Ready
  to merge: Yes"**. Reproduzierte Leak + Fix unabhängig in einer
  Scratch-Kopie (`git archive` beider Commits, kein Worktree/HEAD-Wechsel
  auf dem eigenen Checkout) mit Produktions-Semantik (`debug=False`):
  - `c42d46e` (vor Fix): `GET /api/held/does-not-exist` → 500, Body
    enthält den vollen Windows-Pfad (`[Errno 2] ... 'C:\\...\\_illaen.md'`)
    — Leak real bestätigt.
  - `8e8aa05` (nach Fix): → 404, `{'error': 'not found'}`, kein Pfad.
  - Erzwungene `ValueError` nach Fix: fällt durch auf Flasks generische
    HTML-500-Antwort, Message fehlt im Body — die „debug=False macht das
    sicher"-Annahme empirisch bestätigt, nicht nur auf dem Papier.
  - Lief den neuen Testfile selbst gegen den ungefixten Stand: Tests (a)
    und (c) schlagen dort fehl (= diskriminieren korrekt), (b) besteht
    beidseitig (echte Regression). Volle Suite selbst nachgelaufen: 687
    bestanden.
  - **1 Important, außerhalb dieses Sprints geliedert**: `api_commit`
    (`server.py:149`) leakt rohen Git-Stderr (`git_ops.py:45,62`) nach
    demselben Muster wie D-063, anderer Endpunkt/anderes Feld — empirisch
    in einem isolierten Wegwerf-Repo gemessen (`fatal: Unable to create
    '.../.git/index.lock'` im Body). Nicht Teil des D-063-Tickets (anderer
    Scope) → als **D-064** neu gefiled (BACKLOG.md), kein Fix diesen
    Sprint.
  - 3 Minor: (1) `str(tmp_path) not in body`-Assert in Testfall (a) ist auf
    Windows vakuos (Pfad landet doppelt escaped, der Assert besteht auch
    gegen den Leak) — der folgende Regex-Assert diskriminiert tatsächlich;
    behoben per Kommentar (Polish-Commit `fee5167`). (2) `FileNotFoundError`
    wird jetzt ohne Server-Log verschluckt — konsistent mit der bewussten
    „Kein Logging-Ausbau"-Entscheidung im Plan, hier nur dokumentiert. (3)
    toter `mkdir()`-Setup in Testfall (c), identisch mit dem Task-Review-Fund
    — behoben per Polish-Commit `fee5167`.

## Ergebnis

Kein Critical-, kein offenes Important-Code-Finding gegen diesen Diff. Das
einzige Important-Finding betraf einen anderen, vorbestehenden Endpunkt
außerhalb des D-063-Scopes und wurde als D-064 gefiled statt gefixt
(Ruling: eigener Ticket-Scope, gleiches Muster wie D-062/D-063 selbst
entstanden sind). 2 der 3 Minor-Funde per trivialem Controller-Polish
behoben (Kommentar + toter Code, kein Subagent nötig — Projekt-Konvention
für triviale Review-Funde), 1 Minor dokumentiert (Logging bewusst out of
scope, keine Aktion nötig).

`helden/_tools/sprints/sprint-031/plan.md`: T0/T1 ✅, T2 (dieses Dokument) ✅.
Bereit für `/sprint-wrap`.
