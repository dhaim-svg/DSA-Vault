# Sprint 028 — Deferred Cleanup: Selector-Scoping, Druck-Feinschliff, PATCH-Testabdeckung, Footer-Transition

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-057..D-060 anlegen + in-progress, plan.md) | ✅ done | BACKLOG.md, sprints/sprint-028/plan.md |
| T1 | D-057: `#tab-profil table *`-Flächenschlag entschärfen (Selector-Scoping, kein Verhaltenswechsel) | ✅ done | static/tabs.css, templates/partials/profil.j2, tests/test_rendering.py |
| T2 | D-058: Probe-Spalte im Druck einzeilig (Zauber-Tab) + Ritual-/SF-Karten-Grid-Stretch (Zauber-Tab-scoped) | ✅ done | static/tabs.css, static/base.css, templates/partials/zauber.j2, tests/test_rendering.py |
| T3 | D-059: PATCH-Pfad „Verlauf speichern" — Flask-Route-Test (sicher, Fixture-VAULT_ROOT, kein Live-Write) | ✅ done | tests/test_server.py (neu) |
| T4 | D-060: Footer-Transition beim Einblenden des Würfelpanels glätten | ✅ done | static/base.css, tests/test_rendering.py |
| T5 | Verifikation + `/sprint-wrap` | ✅ done | verification.md, handoff.md, output/illaen-baernhold-dashboard.html |

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

## Verification Addendum (Final Review Fix Wave)

**D-058 — Zeilenhoehen-Nebenwirkung der fr-Verschiebung (Gesamt-Review Important #1):** T2 verifizierte
vor dem Fix nur `scrollWidth` (Horizontal-Ueberlauf), nicht die Zeilenhoehe. Nachgemessen (Playwright
gegen `python -m http.server`, Druck-Emulation, echte Vault-Daten `illaen-baernhold`, 703 px Viewport,
BEFORE = `tabs.css` Stand `5eca7d5` vor D-058, AFTER = aktueller HEAD, je 25 `.spell`-Zeilen im
Zauber-Tab):

| | vorher | nachher | Delta |
|---|---|---|---|
| Summe Zeilenhoehen (25 Zeilen) | 1733,70 px | 1810,95 px | **+77,25 px (+4,5 %)** |
| Zeilen mit gewachsener Hoehe | — | 6 von 25 | — |
| groesster Einzelzuwachs | — | +24,49 px (Zeile „1 AsP/LeP (mind. 5)“, Kosten 2→4 Zeilen) | — |

Ursache real: die schmalere Kosten-Spalte (1 → 0,7 fr) laesst 13 von 25 Kosten-Werten mehr umbrechen
als vorher (einige neu 3–4-zeilig statt 1–2-zeilig) — das war im T2-Report bereits als moeglicher
Trade-off benannt, aber nie gemessen. Zusaetzlich, **von T2 nicht vorhergesehen**: die knapp schmalere
Wirkung-Spalte (2,2 → 2 fr, −17 px) laesst bei 3 der 25 Zeilen (13, 17, 18) den Wirkungstext von
1 auf 2 Zeilen umbrechen; bei 2 davon (17, 18) schlaegt das direkt auf die Zeilenhoehe durch (+13,03 px
je Zeile), bei Zeile 13 absorbiert eine ohnehin schon hoehere Nachbarspalte den Zuwachs.

**Einordnung:** Der Effekt ist real, aber klein — 77 px auf eine ohnehin ca. 1,7–1,8 kB hohe Liste
(~4,5 %), verteilt auf 6 von 25 Zeilen. `.spell{ break-inside:avoid; }` (tabs.css:75) verhindert
Zeilen-Zerreissung am Seitenumbruch; ob die zusaetzlichen 77 px einen zusaetzlichen Seitenumbruch nach
sich ziehen, haengt von der Position der Liste auf der Seite ab und wurde nicht per echtem `page.pdf()`
nachgeprueft (Methodenbefund Sprint 026: Druck-Emulation ≠ echter Druck galt dort speziell fuer nicht
gerenderte Hintergruende, nicht fuer Textumbruch/Layout — fuer die hier gemessene Zeilenhoehe gilt die
Druck-Emulation als verlaesslich, siehe T2s bereits etablierte scrollWidth-Messung mit derselben
Methode). Kein Rollback noetig (Kernziel „Probe einzeilig bei 703 px" bleibt erreicht, keine
Ueberlauf-Regression), aber die D-058-Done-Tabellenzeile sollte diesen Zeilenhoehen-Zuwachs nennen statt
ihn zu verschweigen.

**D-059 — Coverage-Umfang praezisiert (Gesamt-Review Important #2):** Commit `88ea374`s Nachrichtentext
„abgesichert" ist im Ergebnis breiter formuliert als der tatsaechliche Testumfang. Tatsaechlich
abgedeckt: Routen-Wiring (`/api/kampagne/<camp>/value` existiert, nimmt PATCH), der `camp`-Guard
(`re.fullmatch(r'[a-z0-9_-]+', camp)`), und JSON-Body-Handling (fehlendes/kaputtes JSON → 400). **Nicht**
abgedeckt: Validierung des `file`/Locator-Felds selbst (`held_writer.py:76-77`, `target = base /
rel_file` ohne Pruefung auf `../` oder absolute Pfade) — das war laut plan.md-Ruling nie Teil des
Scopes, aber sollte in der Sprint-Wrap-Formulierung von D-059 nicht implizit mitgelesen werden. Als
D-061 im Tracker nachgetragen (`BACKLOG.md`), Referenz auf D-059 als Fundort.
