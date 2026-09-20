# Sprint 025 — Verification

Stand: 2026-09-20, nach dem letzten Code-Commit `076421b` (Polish) auf `master` (Sprint-Start `faf478b`, 10 Commits bis dahin, alle lokal, kein Push).

## Test Suite

| Lauf | Ergebnis |
|------|----------|
| `python -m pytest tests -q` (nach Löschen aller `__pycache__`) | **615 passed** (~16 s) |
| `python -m pytest tests -q -W error` (pytest-Option, nach Löschen aller `__pycache__`) | **615 passed** |

Verlauf: 586 (Sprint-024-Stand) → **604** (T1 B-023, +18) → **610** (T3 D-052, +6) → **615** (T4 B-025, +5); der Polish-Commit erweitert einen bestehenden Test, ohne die Zahl zu ändern. Mutationsproben je neuem Assert-Block (T1: 7, T3: 17, T4: 3, Polish: 2 per Monkeypatch); Berichte unter `.superpowers/sdd/sprint-025/` (git-ignoriert).

## Static Render

- `python render-held.py illaen-baernhold` → Exit 0, `output/illaen-baernhold-dashboard.html` (Working Tree CRLF 511 374 B; LF-normalisiert 502 929 B, Sprint 024: 500 039 B).
- 50× `class="artikel-details`, 0× `<script src`, `<em>` 16 → **14** (Ruling R5); `git status` nach dem Render sauber.
- **Golden-Vergleich (Baseline `cf2206b`, LF-normalisiert):** genau **27 eingefügte Zeilen** (T3: der Zauber-Tab-Block im `@media print`) und **2 geänderte Zeilen** (T1: Lichtblitz und Antimagie, nur `<em>` → `*`); außerhalb davon byte-identisch — Bildschirm-CSS, HTML-Body und JS unverändert.

## B-023 — Buch-Sternchen

- **Ganzdatei-Stern-Bilanz** (Notation in der Quelle == literale Notation im gerenderten HTML) an allen 508 Wiki-Dateien mit Notation: **82 falsch → 0** (Ruling R4). Der Pre-flight hatte 123 Zeilen in 85 Dateien gezählt (isolierte Zeilen, ungenau).
- Prototypen am Korpus (Scratchpad) widerlegten den geplanten Weg (mistune-Inline-Regel) und trugen den Platzhalter-Weg; der Implementierer fand zusätzlich den Lookahead `(?!\*)` (schützt `**LkP**`), den der Prototyp nur zufällig verdeckt hatte.
- U+E000 kommt in keiner Wiki-Datei vor (Korpus-Test); Platzhalter-Leck in Link-URLs wird erkannt (Polish, Final-Review M1; heute 0 Vorkommen).
- Korpus-Test kostet ~3,1 s (≈ 20 % der Suite) — bewusst akzeptiert.

## D-052 — Druck des Zauber-Tabs

- **Vermessung vor dem Fix (T2, Print-Emulation über Static-`http.server`, sha256 abgeglichen):** Überlauf-Quelle = `.spell`-Grid der Zauberliste (Minima 858 px inkl. Gaps gegen 733 px Innenbreite), **nicht** „Spontane Modifikationen“; **20 Kontrast-Gruppen** 1,04–4,28 : 1 (die Backlog-Zahlen waren teils falsch zugeordnet, Ruling R8).
- **Nachmessung (T5):** `scrollWidth` Druck **881 → 779** (Viewport 794), **703** (718, = echte A4-Seitenbreite), **600** (615); überstehende Elemente 120 → 0; alle 8 Tabs auf `clientWidth`; Kontrast: **0 Gruppen < 4,5 : 1** (alle 14,62 : 1); Namenslink-Unterstrich 1,13 → 14,62 : 1; Vol-Badge-/Speicherkasten-Rand 1,08 → 3,41 : 1; sichtbare Slot-Schaltflächen 0; mit 3 offenen Artikeln kein Überlauf, `break-inside:auto`; kein Wort mitten im Wort @718 (825 Wörter).
- **Bildschirm unverändert:** 400 Werte gegen die T2-Baseline (`color`, `background`, `border-bottom*`, `opacity`, `display`, `fontSize`, Breite × Höhe), **0 Abweichungen**; kein Seitenüberlauf @1280 / @400; Grid @400 = `display:flex`.
- **Optik (vom Controller an den Screenshots gesehen):** Kopfzeile fluchtet mit den Daten, nichts abgeschnitten oder überlappend, Zauberspeicher als Kasten mit dunklem Text; kosmetisch: die Probe bricht in 25/25 Zeilen zweizeilig um (Zeilen höher), der Pfeil ↗ steht @ 703 px bei 5 von 25 Namen allein in der Folgezeile (@ 794 px: 1).
- **Grenze:** nur der **Zauber-Tab** — die übrigen 7 Tabs wurden nicht vermessen (Ruling R7 → BACKLOG.md D-053); der Screenshot zeigte dort z. B. die AP-Zahlen „3845“/„3858“ fast unsichtbar. Echter Druckdialog mit `@page`-Rändern, gefüllte Zauberspeicher-Slots (im Render alle 3 leer) und `file://` bleiben ungeprüft.

## B-025 — Geld-Unittests

- `_make_geld_dict` gestrichen; `test_geld_structure`, `test_gesamt_kreuzer_math`, `test_geld_fallback` (5 Fälle) und neu `test_geld_krumme_werte` rufen `load_held` über den Mini-Helden. Fallback-Zweige belegt: fehlender Schlüssel/kein Frontmatter → erster Zweig (`{}`), `geld:` null/skalar/Liste → `else`-Zweig (der Brief nahm für „kein Frontmatter“ irrtümlich `else` an; Implementierer und Reviewer haben es am Parser bestätigt).
- Mutationsproben: Kurs `*100 → *10`, `else → {}`, `int` statt `safe_int` — jeweils genau die zuständigen Tests rot.

## Wiki / Domänen-Grenze

- `raw/pdf-extracted/_tools/check-frontmatter.py` → **828 Dateien geprüft, 682 mit Frontmatter, 0 fehlerhaft** (unverändert).
- `git diff --numstat faf478b..HEAD -- wiki helden/illaen-baernhold abenteuer` → **leer**: weder Wiki noch User-Domäne wurden angefasst.

## Reviews

- Task-Reviews (Sonnet, Spec + Quality): **T1** ✅ Approved (0 Critical, 0 Important, 3 Minor); **T3** ✅ Approved (0/0/4); **T4** ✅ Approved (0/0/2). Kein Fix-Round nötig.
- **Gesamt-Review (Opus):** *Ready to merge: With fixes* — 0 Critical, **1 Important** (Scope-Grenze von D-052 für den User unsichtbar; behoben: `plan.md` Out of Scope, `BACKLOG.md` D-052 mit R8-korrigierten Zahlen, neues D-053), 7 Minor (M1 Platzhalter-Leck → **behoben** per Polish-Commit; M2–M5 bleiben deferred: Korpus-Test-Laufzeit, Über-Parametrisierung ×4, redundante Regel `.slot-befuellen-toggle/-form` unter `-area`, toter Assert `test_rendering.py:503-504`). Rulings R2, R6, R7, R9 bestätigt.
- Deferred Minors der Task-Reviews (T1 ×3, T3 ×4, T4 ×2) stehen im Ledger und im Handoff.

## Browser-Runden

- **T2** (Vermessung, vor dem Fix) und **T5** (Nachmessung) über Static-`http.server` (freie Ports, sha256 abgeglichen, nur die eigene PID beendet, `.playwright-mcp/` gelöscht, `git status` vor = nach); nur `[data-tab="zauber"]` und `summary.artikel-toggle` angeklickt. Ein Implementierer (T3) hat zusätzlich selbst einmal per Print-Emulation gemessen (über den Brief hinaus, ohne Repo-Spuren) — ersetzt T5 nicht.
