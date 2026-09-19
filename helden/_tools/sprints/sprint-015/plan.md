# Sprint 015 — Template-Zerlegung + Chronik-Tab

## Ausgangslage

Sprint 014 hat das Chronik-Fundament gelegt (`chronik_import.py`, `parsers/chronik.py::load_chronik()`),
aber noch nichts konsumiert den Parser. `dashboard.html.j2` ist auf 2094 Zeilen gewachsen (1125 davon
ein einziger `<style>`-Block). User-Entscheidung: **D-037 (Template-Zerlegung) vorziehen, dann D-032
(Chronik-Tab)** auf sauberer Basis. D-035 (`/session-compile`) rutscht nach Sprint 016.

**Scope-Warnung:** L + M liegt über dem Richtwert. Fallback: D-037 allein ist ein abschließbarer
Sprint; D-032 (T4/T5) rutscht dann nach 016 — Entscheidung beim Wrap, nicht vorher.

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-037 + D-032 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-015/plan.md |
| T1 | **D-037a** CSS aus `<style>` in `static/*.css` auslagern + Render-Zeit-Bundling in `rendering.py` | ⬜ todo | rendering.py, templates/dashboard.html.j2, static/{base,tabs,journal,sprachen}.css (neu), tests/test_rendering.py (neu) |
| T2 | **D-037b** Tab-Bodies in `templates/partials/<tab>.j2` zerlegen | ⬜ todo | templates/dashboard.html.j2, templates/partials/*.j2 (8 neu) |
| T3 | **D-037c** Render-Kontext konsolidieren (`kampagne_slug`-Divergenz) — klein, Controller inline | ⬜ todo | render-held.py, server.py |
| T4 | **D-032a** Chronik-Kontext + Bild-Auslieferung + Parser-Härtung + geteilte Pfad-Konstante | ⬜ todo | render-held.py, server.py, parsers/chronik.py, chronik_import.py, tests/test_chronik.py |
| T5 | **D-032b** Chronik-Tab: Partial + `static/chronik.css` + Roh/Kompiliert-Umschalter | ⬜ todo | templates/partials/chronik.j2 (neu), static/chronik.css (neu), static/chronik.js (neu), templates/dashboard.html.j2 |
| T6 | Verifikation + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

1. **CSS in `static/*.css`, aber zur Render-Zeit eingebettet** (`css_bundle()` in `rendering.py`, explizit
   geordnete Liste; Template behält einen `<style>{{ css }}</style>`-Block). Grund: `<link href="/static/…">`
   würde den gesamten Static-Render (`output/*.html`) entstylen. Server rendert pro Request neu → kein
   Verlust gegenüber `<link>`. Abweichung vom Wortlaut der User-Antwort, im Plan-Review offengelegt und
   freigegeben.
2. **CSS-Split entlang der Kommentar-Banner:** `base.css` · `tabs.css` · `journal.css` · `sprachen.css`
   (später `chronik.css`). Bundle-Reihenfolge = eine Liste an einer Stelle. **Harte Auflage T1:** gerenderter
   `<style>`-Inhalt vor/nach Auslagerung per Diff belegt identisch (abgesehen von Datei-Grenzen-Whitespace).
3. **Partials pro Tab** `templates/partials/{kampf,talente,zauber,steigern,inventar,profil,journal,sprachen}.j2`
   via `{% include %}`. Reines Verschieben, keine Umformulierung.
4. **Chronik-Bilder:** neue Route `/chronik-bild/<path:name>` (`send_from_directory`, Traversal-Guard);
   Kontext-Feld `chronik_bild_prefix` (Server: `/chronik-bild/`, Static-Render:
   `../abenteuer/drachenchronik/`).
5. **Ein 📜-Chronik-Tab, zwei Unteransichten:** *Roh* (geparste `chronik.md`, read-only, ältere Abende in
   `<details>`, Meta-Sektionen als Karten) und *Kompiliert* (bestehende Journal-Markup wortwörtlich verschoben,
   inkl. Write-back; `journal.js` unverändert). Umschalter in `static/chronik.js`, Zustand in `sessionStorage`.
   Alter `data-tab="journal"`-Button entfällt; gespeichertes `'journal'` in `sessionStorage` muss sauber
   zurückfallen.
6. **Parser-Härtung:** Bullet mit Bild UND Text (Text geht verloren) → fixen. Leerer IG-Tag → nur
   dokumentieren (Design-Frage). Geteilte Pfad-Konstante `chronik_import.py` ↔ `parsers/chronik.py` → in T4
   einführen (Handoff nennt genau diesen Zeitpunkt).
7. **⚠ `autoescape=False`** (`rendering.py:40`): jedes Chronik-Feld im Template braucht explizit `| e`.
   Ausnahme: `<img src>` (Pfad, über Route validiert).
8. **Prozess:** Subagent-Driven Development + zwei-stufige Review (spec + quality). Triviale Reviewer-Funde
   (< 10 Zeilen) inline. Nach jedem Implementierer `git status`/`git show` prüfen. Sprint-Pfade explizit
   `sprint-015`-qualifiziert übergeben (sdd-workspace-Kollision, alle Pläne heißen `plan.md`).

## Out of Scope

- **D-035** (`/session-compile` + Aufräumen) — Top-Kandidat Sprint 016. Platzhalter
  `2025-10-04-session-01.md` bleibt (User-Domäne, braucht Freigabe).
- **D-036** (NSC-/Orts-Register) — hängt an D-035.
- **D-018** (Zauber-Inline-Vorschau) — unverändert im Backlog.
- **Schreibpfad in die Chronik** — gestrichen mit D-033/D-034; Chronik-Tab bleibt read-only.
- **Google-Drive-Junction** — verifiziert gescheitert, nicht erneut versuchen.
- **`chronik_import.py`-Härtung** (leerer Quelldatei-Read, Bild-Größenvergleich) — Recovery = `git checkout`.
