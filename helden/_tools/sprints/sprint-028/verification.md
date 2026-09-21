# Sprint 028 — Verifikation

Stand: HEAD nach Gesamt-Review-Fixwelle (`d249fed`). Alle Zahlen sind gemessen oder
nachgerechnet, keine übernommen.

## Test-Suite

- `python -m pytest -W error -q` aus `helden/_tools/`, nach Löschen aller `__pycache__`:
  **662 passed** (Ausgangsstand Sprint 027: 652).
- Zuwachs pro Task (nachgerechnet gegen die tatsächlich berichteten Zwischenstände, nicht
  nur die Differenzenzeile der Reports übernommen — T2s eigener Report hatte hier selbst
  einen Rechenfehler, s. Reviews unten): 652 → **653** T1 (D-057, +1: Klassen-Präsenz-Test),
  → **656** T2 (D-058, +3: fr-Summe + align-top-Präsenz/-Absenz + Render-Level),
  → **661** T3 (D-059, +5: neue `tests/test_server.py`), → **662** T4 (D-060, +1:
  Transitions-Präsenz) = **+10** über die vier Feature-Tasks; unverändert durch die
  Gesamt-Review-Fixwelle (nur Doku/Kommentare/Umlaute/Docstrings angefasst, keine neue
  Assertion außer dem Umbau von T4s eigenem Test auf einen relationalen Check statt
  zweier hartkodierter Werte).

## Sprintziel: 4 lang offene "Bekannte Einschränkungen" geschlossen

| EPIC | Prüfung | Ergebnis |
|---|---|---|
| D-057 | `#tab-profil table *`-Flächenschlag entschärft | Sessions-Tabelle (profil.j2:82) trägt `.sessions-table`, `tabs.css:168` zielt darauf statt auf `table`/`table *`. Golden-Render-Diff (Fix-Runde 2): `render_dashboard(build_context(...))` bei `253876f` (vor) vs. `5eca7d5` (nach) — SHA256 unterschiedlich, aber nur 3 Zeilen Differenz (Selector-Text, Kommentar, `class="sessions-table"`-Attribut), sonst byte-identisch |
| D-058a | Probe-Spalte im Druck einzeilig (Zauber-Tab) | `.spell`-Grid-fr-Anteile verschoben (Probe 1,4→1,9fr, Kosten 1→0,7fr, Wirkung 2,2→2fr, Summe unverändert 6,4fr). Playwright/Print-Emulation @703/718/615px: `scrollWidth` identisch vor/nach (662/677/574px), **keine Überlauf-Regression**. Probe einzeilig für 25/25 reale Zeilen @703/718px (615px war nie Ziel, nur Überlauf-Sicherheit) |
| D-058a (Gesamt-Review-Fixwelle) | Zeilenhöhen-Nebenwirkung nachgemessen | Nicht in T2 geprüft (nur horizontal). Nachgemessen: Summe 25 Zeilenhöhen 1733,70→1810,95px (**+77,25px/+4,5%**), 6/25 Zeilen höher, größter Einzelzuwachs +24,49px. Ursache: Kosten-Spalte wrapt öfter (13/25 Zeilen) **und** Wirkung-Spalte unerwartet auf 3 Zeilen (von T2 nicht vorhergesehen). Kein Rollback — Kernziel (einzeilige Probe, kein Überlauf) bleibt erreicht, Effekt klein und dokumentiert |
| D-058b | Ritual-/SF-Karten-Grid-Stretch (Zauber-Tab-scoped) | Neue `.grid.align-top{align-items:start}`-Modifier-Klasse, nur an `zauber.j2:91`. Gemessen: SF-Karte blieb bei 1626,9px statt auf 7122,6px zu stretchen (10 Ritual-`<details>` offen). `.cols-2`-Basisregel und die 3 anderen Tabs (profil/inventar/kampf) unverändert, per Test gepinnt |
| D-059 | PATCH-Pfad „Verlauf speichern" end-to-end getestet | Neue `tests/test_server.py`: Erfolgsfall mit On-Disk-Verifikation, `camp`-Guard (3 parametrisierte Verletzungen), Malformed-JSON→400 — alles gegen `tmp_path`-Fixture-`VAULT_ROOT`, echter Vault nie berührt (verifiziert per `git status`/`git show --stat`). Umfang präzisiert (Gesamt-Review-Fixwelle): getestet ist Routen-Wiring + `camp`-Guard + JSON-Handling, **nicht** das `file`-Feld selbst (→ D-061 im Tracker) |
| D-060 | Footer-Transition beim Einblenden geglättet | `transition:bottom 0.2s ease` auf `#footer-bar` (base.css), synchron zur `.dice-panel`-Transition (0,2s ease). Test liest jetzt die reale Panel-Dauer per Regex und vergleicht relational statt zwei Werte hart zu kodieren (Fund der Gesamt-Review) — Mutationsprobe bestätigt: Test schlägt fehl, wenn die Dauern auseinanderlaufen |

## Static Render

- `python render-held.py illaen-baernhold` **einmal gesammelt** nach T1+T2+T4 ausgeführt
  (Ruling: T1 und T2 hatten das Artefakt einzeln nicht nachgezogen, statt 3× wurde 1×
  aktualisiert) — Diff enthielt ausschließlich die erwarteten Deltas aus D-057/D-058/D-060,
  committed als `3aa835a`.
- Gesamt-Review verifizierte unabhängig: `render_dashboard(build_context('illaen-baernhold'))`
  im Speicher neu gerendert und mit dem getrackten `output/illaen-baernhold-dashboard.html`
  verglichen — **byte-identisch** (Zeilenende-normalisiert), alle 6 erwarteten Marker
  vorhanden (`.grid.align-top`, `transition:bottom 0.2s ease`, neue `.spell`-fr-Werte,
  `#tab-profil .sessions-table`, `class="sessions-table"`, `class="grid cols-2 align-top"`).

## Unberührte Bereiche

- `wiki/`, `helden/illaen-baernhold/`, `abenteuer/` — kein Task dieses Sprints hat
  Dateien außerhalb `helden/_tools/` und `output/illaen-baernhold-dashboard.html`
  verändert (alle Commits waren pfadbegrenzt auf `helden/_tools/**` + das eine
  Static-Render-Artefakt).
- D-059 explizit verifiziert: kein Test schreibt in den echten `abenteuer/`- oder
  `helden/<slug>/`-Baum (nur `tmp_path`-Fixtures).

## Reviews

- **T1 (D-057):** Task-Review fand 1 Important (Golden-Render-Diff-Pflicht nicht wirklich
  erfüllt, nur Post-Change-Inspektion behauptet) → 2 Fix-Runden nötig (Runde 1 diffte
  weiterhin nur Quelltext statt gerendertem Output — vom Controller selbst vor Re-Review
  erkannt, kein Reviewer-Zyklus verschwendet), Runde 2 rendert echt via
  `render_dashboard()`/`build_context()` und hasht/diffed den Output — ADDRESSED. 2 Minor
  deferred (Tippfehler, Docstring-Sprache) → in Gesamt-Review-Fixwelle behoben.
- **T2 (D-058):** Task-Review Approved, 0 Critical/Important im eigenen Scope — 1 Important
  zum Static-Render-Artefakt als sprintübergreifendes Prozessthema erkannt und vom
  Controller bewusst auf T5 verschoben statt T1 erneut zu öffnen oder T2 eine Fix-Runde
  aufzuerlegen (Ruling, s. `progress.md`). 1 Minor (Arithmetik-Tippfehler im Report) deferred.
- **T3 (D-059):** Spec ✅ / Approved, 0 Findings beim ersten Durchgang — Vault-Sicherheit
  Zeile für Zeile gegen `_resolve_base()`/`create_app()` verifiziert. 2 Minor deferred →
  in Gesamt-Review-Fixwelle behoben.
- **T4 (D-060):** Task-Review fand 1 Critical (Report behauptete "volle Test-Suite", lief
  aber nur `test_rendering.py` — 140 statt 662 Tests) → 1 Fix-Runde (echter Voll-Lauf,
  662 bestätigt), Re-Review: ADDRESSED, keine neue Regression.
- **Gesamt-Review (Opus):** *Ready to merge: With fixes* — 0 Critical, 2 Important
  (D-058 Zeilenhöhen-Nebenwirkung nie gemessen; T3-Commit-Nachricht "abgesichert"
  überzeichnet den tatsächlichen Umfang, ungeschütztes `file`-Feld nicht getrackt),
  4 Minor. Unabhängig nachgerechnet statt Reports übernommen (Render-Byte-Vergleich,
  fr-Summen-Mathematik, `scrollWidth`-Plausibilität). 1 gebündelte Fix-Runde (alle 7 Funde
  in einem Dispatch statt einzeln), gescopter Re-Review: alle 7 ADDRESSED, keine neue
  Regression.
- Reviewer haben durchgehend **selbst nachgemessen/nachgerechnet** statt Berichte zu
  übernehmen — u. a. fr-Summen-Mathematik unabhängig nachgerechnet (T2-Review), Render-Byte-
  Vergleich unabhängig wiederholt statt der Controller-Behauptung geglaubt (Gesamt-Review),
  `_client()`-Aufrufstellen neu gegrept statt Diff-Zählung vertraut (Fixwelle-Re-Review).

## Methodenbefund (neu, Sprint 028)

**Ein Fix, der nur eine Dimension (horizontal) misst, kann eine andere (vertikal) unbeachtet
lassen.** D-058s `scrollWidth`-Messung bewies zuverlässig "kein horizontaler Überlauf",
sagte aber nichts über Zeilenhöhen-Zuwachs durch stärkeren Zeilenumbruch in einer
schmaler gewordenen Spalte — ein Grid-Row nimmt die Höhe seiner höchsten Zelle an, das ist
eine orthogonale Eigenschaft zur Spaltenbreite. Folge fürs Verfahren: bei
fr-Anteilsverschiebungen künftig auch Zeilenhöhen (nicht nur Spaltenbreiten/`scrollWidth`)
vor/nach vergleichen, wenn eine Spalte mit variabler Zeilenzahl (wie Kosten/Wirkung hier)
schmaler wird.

**Statische Render-Artefakte, die pro Task committet werden sollen, brauchen eine explizite
Prüfung im Task-Review — sonst driftet das Artefakt unbemerkt über mehrere Tasks.** T1 und
T2 ließen `output/illaen-baernhold-dashboard.html` beide unangetastet, obwohl Sprint 027s
Konvention war, es pro Commit mitzuziehen. Der Controller entschied bewusst, es einmal
gesammelt statt dreimal einzeln nachzuziehen — korrekt für dieses Sprint, aber ein Task-
Review-Checkpunkt "wurde das Render-Artefakt aktualisiert, falls betroffen?" hätte die
Drift früher sichtbar gemacht statt sie bis zur Gesamt-Review liegen zu lassen.
