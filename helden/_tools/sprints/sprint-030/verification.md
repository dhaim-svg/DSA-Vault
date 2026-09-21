# Sprint 030 — Verifikation

## Testsuite

- `pytest tests/ -q` (aus `helden/_tools/`, Controller-Gegenprobe, unabhängig
  vom Implementierer-Report): **684 passed**, 16.68s.
- `pytest tests/ -q -W error` (nach `__pycache__`-Löschen): **684 passed**,
  17.54s, keine Warnings.
- Baseline vor Sprint 030 (aus Sprint-029-Verifikation): 671.
  671 → 683 (T1, +12 neue Tests) → 684 (Fix-Runde 1: `'../outside'` als
  eigener Parametrize-Fall auf `held_page` statt auf `/value`, +1).

## Static Render

Nicht betroffen — D-062 ändert nur Routen-Guards in `server.py` (kein
Rendering-Code, kein Template/CSS). `output/illaen-baernhold-dashboard.html`
unverändert, keine Regenerierung nötig.

## Git

- `git status --short`: sauber, alle Änderungen committet.
- 5 Commits auf `master` (kein Worktree, kein Push, per Projekt-Konvention):
  - `36bb140` — T0 Scaffold (D-062 in-progress, plan.md)
  - `5ca5dde` — T1 Fix (`_valid_slug`-Guard auf allen 5 Routen + 12 Tests)
  - `bcce11e` — T1 Fix-Runde 1 (`'../outside'` auf `held_page` statt `/value`
    — Controller-Ruling während der Implementierung, s. u.)
  - `db2ecf8` — Controller-Tracker-Update (plan.md T0/T1 ✅)
  - `7b897eb` — Controller-Doku-Fix (D-062-Severity-Text korrigiert, Fund der
    Gesamtreview, kein Code-Fix)

## Review-Kette

- **Live-Ruling während T1** (kein Review-Fund, eigene Verifikation vor
  Ruling): Implementierer meldete, dass `'../outside'` im Brief-Parametrize
  für `/value` unerreichbar ist (Werkzeugs `string`-Converter auf
  `<slug_param>` nimmt kein `/`). Controller reproduzierte das unabhängig
  (Live-Request gegen den Arbeitsbaum) und ruling-te: aus `/value` streichen,
  stattdessen auf `held_page` (nutzt `<path:s>`, nimmt echte Slashes) — dort
  reproduzierte der Controller ebenfalls live, dass es die Route erreicht.
- **Task-Review** (Sonnet, Range `36bb140..5ca5dde`): Spec 8/9 ✅, 1
  Important — genau der vorhergesagte, zeitlich bereits überholte Fund
  (Diff-Snapshot vor der `held_page`-Ergänzung aus dem Ruling oben). Keine
  weiteren Funde; Strengths bestätigten `heldfixtures`-Nutzung und
  diskriminierende Read-Route-Tests per eigener Nachverfolgung der
  Fehlerpfade.
- **Scoped Re-Review** (Haiku, Range `5ca5dde..bcce11e`): Finding ADDRESSED,
  keine neue Breakage, reiner Test-Diff.
- **Gesamt-Review** (Opus, volle Sprint-Range `eeb8736..db2ecf8`): **„Ready to
  merge: Yes"**. Reproduzierte den Fix unabhängig in einem Scratch-Worktree
  bei `eeb8736` (getrennt vom eigenen Arbeitsbaum) und maß dort real:
  `PATCH /api/held/../value` → 200/Überschreiben; `GET /held/../outside` →
  `FileNotFoundError`; Null-Byte erreicht `patch()` ungefiltert. Kopierte
  zusätzlich den kompletten neuen Testfile auf den ungefixten Stand und lief
  ihn dort: **11 von 13 neuen Tests schlagen dort fehl** (= diskriminieren
  korrekt), die übrigen 2 sind bewusst beidseitig grüne Regressionstests mit
  echten Inhalts-Assertions — **0 vakuose Tests** (Gegensatz zu 5 von 8 in
  Sprint 029). Mutationsprobe (Guard `fullmatch`→`search` geschwächt) von 5
  Tests gefangen.
  - **1 Important, dokumentationsbezogen, kein Code-Fix**: Werkzeugs
    `string`-Converter schliesst `/` aus, aber NICHT `\` — unter Windows
    escaped `..%5C...` sowohl innerhalb als auch **ausserhalb** des
    Vault-Root (gemessen, real überschrieben), nicht nur `.md`-Dateien im
    Vault-Root wie der ursprüngliche Backlog-Text annahm. Fix deckt auch
    diesen Vektor ab (Allowlist-Regex, kein `/`-spezifisches Denylist) —
    gegen `db2ecf8` verifiziert. Behoben per Doku-Commit `7b897eb`
    (BACKLOG.md-Text korrigiert), kein Code-Fix nötig.
  - 3 Minor, alle geparkt (s. Ledger `progress.md` für vollständige
    Begründung je Punkt): (a) `%5C`-Testlückenabdeckung + Docstring-Korrektur
    in `test_server.py` — Mutationsprobe zeigt keine echte
    Diskriminierungslücke; (b) DRY-Nit `api_patch_kampagne`s Inline-Regex
    könnte `_valid_slug` nutzen; (c) vorbestehender Pfad-Leak in `api_held`s
    500-Handler (`server.py:78-79`) — nicht von diesem Sprint eingeführt,
    Backlog-Kandidat.

## Ergebnis

Kein Critical-, kein offenes Important-Code-Finding. Ein Important-Finding
war dokumentationsbezogen und wurde direkt behoben (kein Fix-Loop nötig,
kein Implementierer-Dispatch — Controller-Edit gemäß Projekt-Konvention für
triviale Review-Funde). 3 Minor geparkt mit Begründung.
`helden/_tools/sprints/sprint-030/plan.md`: T0/T1 ✅, T2 (dieses Dokument) ✅.
Bereit für `/sprint-wrap`.

## Für den Handoff vorzumerken (Lehre, projektübergreifend)

Die Gesamtreview flaggte explizit als Empfehlung: „Werkzeugs Routing schliesst
Pfad-Separatoren aus" ist auf Windows falsch — nur `/` (`%2F`) wird vom
Default-`string`-Converter/Routing abgefangen, `\` (`%5C`) nicht. Diese exakte
(falsche) Annahme stand wörtlich sowohl im ursprünglichen D-062-Ticket-Text
als auch in einem neuen Test-Docstring. Jede künftige Route, die sich auf
Werkzeugs Routing als alleinigen Trennzeichen-Schutz verlässt, erbt dieselbe
Lücke — für `wiki-luecken.md`/Sprint-Lehren-Abschnitt im Handoff vormerken.
