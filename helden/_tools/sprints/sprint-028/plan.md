# Sprint 028 — Deferred Cleanup: Selector-Scoping, Druck-Feinschliff, PATCH-Testabdeckung, Footer-Transition

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-057..D-060 anlegen + in-progress, plan.md) | ✅ done | BACKLOG.md, sprints/sprint-028/plan.md |
| T1 | D-057: `#tab-profil table *`-Flächenschlag entschärfen (Selector-Scoping, kein Verhaltenswechsel) | ⬜ todo | static/tabs.css, templates/partials/profil.j2, tests/test_rendering.py |
| T2 | D-058: Probe-Spalte im Druck einzeilig (Zauber-Tab) + Ritual-/SF-Karten-Grid-Stretch (Zauber-Tab-scoped) | ⬜ todo | static/tabs.css, static/base.css, templates/partials/zauber.j2, tests/test_rendering.py |
| T3 | D-059: PATCH-Pfad „Verlauf speichern" — Flask-Route-Test (sicher, Fixture-VAULT_ROOT, kein Live-Write) | ⬜ todo | tests/test_server.py (neu, Muster test_commit.py:107-131) oder Erweiterung test_held_writer.py |
| T4 | D-060: Footer-Transition beim Einblenden des Würfelpanels glätten | ⬜ todo | static/base.css, tests/test_rendering.py |
| T5 | Verifikation + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **D-057**: Sessions-Tabelle (profil.j2:82-97) bekommt eigene Klasse (z.B. `.sessions-table`); `tabs.css:168` zielt darauf statt auf `table,table *`. Kein aktiver Bug (nur 1 Tabelle im Tab existiert), reines Refactoring gegen künftiges Regressionsrisiko → Golden-Render-Diff (Druck-Modus, vor/nach `cmp`) statt neuer Kontrastmessung.
- **D-058 Probe-Spalte**: nur `@media print`-Block (tabs.css:120-128) betroffen. Fix verschiebt `fr`-Anteile zwischen den 6 `.spell`-Spalten → reshuffelt die in D-052/D-053 vermessene Überlauf-Grenze. **Pflicht:** `scrollWidth` an allen 3 Viewports (703/718/615px) vor und nach dem Fix messen, keine Overflow-Regression.
- **D-058 Grid-Stretch**: User-Entscheidung — Fix nur auf die Zauber-Tab-Grid-Instanz (neue Modifier-Klasse auf `.grid.cols-2` in zauber.j2:91), NICHT global auf `.cols-2` (base.css:78-81). Die 3 anderen Verwendungsstellen (profil/inventar/kampf) bleiben unangetastet und ungeprüft.
- **D-059**: User-Entscheidung — nur sicherer Pytest-Test gegen Flask `test_client()` + `tmp_path`-Fixture-VAULT_ROOT (Route-Wiring, JSON-Body, `re.fullmatch`-Guard), Muster exakt wie `test_commit.py:107-131`. **Kein** Live-Browser-Klick gegen echte `abenteuer/`-Dateien diesen Sprint — keine User-Domäne-Schreibfreigabe nötig. Entdeckte Nebenbeobachtung (nicht Teil des Scopes): Client sendet nie ein `etag`, serverseitiger 409-Konfliktpfad ist vom Client aus tot — als Notiz vormerken, nicht fixen.
- Alle 4 EPICs bekommen neue IDs **D-057…D-060** (nächste freie nach D-056, gegen BACKLOG.md-Done-Tabelle verifiziert).

## Out of Scope

- **D-059 Live-Browser-Verifikation** des echten Schreibpfads gegen `abenteuer/` — User-Entscheidung, auf sicheren Pytest-Test beschränkt. Bleibt als wiederkehrende Notiz seit Sprint 015 offen, kein neuer EPIC.
- **D-059 etag/Konflikterkennung** clientseitig nachrüsten — entdeckt, nicht angefordert.
- **Globale `.cols-2`-Änderung** — User-Entscheidung, auf Zauber-Tab-Instanz beschränkt.
- **Echter Druckdialog (Papier-Ausdruck)** weiterhin ungeprüft — unverändert seit Sprint 020.
- **Register-Format-Fragilität** (separate von D-059, Sprint-017-Notiz) und **Messung nur an einem Charakter** (illaen-baernhold) — beide unverändert offen.
