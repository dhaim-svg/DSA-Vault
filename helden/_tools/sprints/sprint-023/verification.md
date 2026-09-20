# Sprint 023 — Verifikation

Stand: 2026-09-20, HEAD `4698da1` (12 Commits seit `de837ab`, lokal, **nicht gepusht**; 21 Commits vor `origin/master`).

## Tests

- `python -m pytest -q -W error` nach Löschen aller `__pycache__`: **563 passed** (Sprint-022-Stand 464: +2 T1 [Apport], +32 T2, +26 T3, +23 T4, +12 T5, +3 T6, +1 Polish). Normaler Lauf ebenfalls 563.
- Hinweis: `python -W error -m pytest` scheitert in dieser Umgebung schon beim Plugin-Import an einer ipykernel-Warnung, nicht an unserem Code — `-W error` als pytest-Option nutzen.
- Mutationsproben je neuem Assert-Block in den Task-Reports (`.superpowers/sdd/sprint-023/task-N-report.md`, git-ignoriert): alle Mutanten rot, Dateien per Hash byte-genau zurück. Im Polish zusätzlich: Fallback im Speicher abgeschaltet → `test_empty_frontmatter_quelle_falls_back_to_the_quote_block` rot.

## Wiki

- `raw/pdf-extracted/_tools/check-frontmatter.py`: 828 Dateien, 682 mit Frontmatter, **0 fehlerhaft**.
- `stabzauber.md`: alle **12** `##`-Anker über `load_wiki_artikel` ladbar — je 1 Eintrag, HTML nicht leer, kein `<hr`, kein wörtliches `**` im Text, Quelle `WdZ S. 105–115 (Aktivierungsregel S. 105, Apport S. 106, Stabzauber S. 107–111, Kristallkugel S. 111–115)`, keine Log-Warnung.
- Buchtreue: Task-Reviews T1/T2 prüften > 55 Werte gegen den Rohtext, das Gesamt-Review alle 12 Kopfblöcke gegen das Transkript (0 Abweichungen). Bei der Prüfung fiel u. a. auf: die Regel „Erschaffungsproben um Anzahl vorhandener Stabzauber erschwert“ stammte aus dem Ring des Lebens (Geoden), nicht aus den Stabzaubern; die Tabelle „Holzarten für Stäbe“ (Esche 24 / Eiche 18 / Ulme 15 / Eibe 27) hat im Buch keine Grundlage — 24/18/15/27 ist das Stab-Fassungsvermögen.
- Rohsternchen: `grep 'ZfP\*\*\*'` ohne vorgeschaltetes `\` → **0** Treffer (vorher 7 bekannte + 33 weitere Zeilen); verbleibende `***`/`**` im Korpus sind Fußnotenmarken (`bewegung-reisen`, `sprachen-schriften`, `invokation-grundregeln`, `kampf-referenztabellen`, `halbelfen`).

## Static Render

- `render-held.py illaen-baernhold` erfolgreich; `output/illaen-baernhold-dashboard.html` **481 641 B** (Sprint 022: 481 589 B, +52 B); 0× `<script src>`, **40×** `class="artikel-details`.
- **Diff gegen die Golden-Baseline** (Stand `bd4f364`): genau **8 Zeilen** = die 4 Aufzählungszeilen des Odem-Arcanum-Vorschaublocks (`<li>**N ZfP***…` → `<li><strong>N ZfP*</strong>…`, T3). T1, T2, T4, T5, T6 und Polish: byte-identisch (T4: gemessen 129 Artikel bekommen eine Quelle, aber keiner davon ist eingebettet; T6: `load_held(...)['rituale']`-JSON und Render vor/nach byte-identisch).
- Browser-Runde: **entfallen** (Ruling R9) — kein Template-/CSS-/JS-Diff, einziger Render-Effekt sind die 4 fett gesetzten Zeilen, im HTML-Diff geprüft.

## Repo / Domänen

- `git status` sauber; Steuerbytes 0x08/0x0C in allen geänderten Dateien: keine; Zeilenenden je Datei wie vorgefunden (Python-Dateien überwiegend CRLF, Wiki/Tracker/neue Testdateien LF).
- **Domänen-Grenze:** unter `helden/illaen-baernhold/` nur `rituale.md` (User-Freigabe für diese Änderung): 9 Namenszellen → Anker-Links (Anzeigetext wortgleich) + 1 Halbsatz („Zuordnung bestätigt … semantisch, kein Buchname“). `abenteuer/` unberührt. `raw/` nicht committet.
- Reviews: Task-Reviews T1–T6 (Sonnet) je Spec ✅ / Approved (0 Critical, 0 Important); Gesamt-Review (Opus) **Ready to merge: With fixes** — 0 Critical, 1 Important (L25(b) noch „offen“), 3 Minor; alle drei Fixes inline behoben (`4698da1`). Berichte: `.superpowers/sdd/sprint-023/task-N-review.md`, `final-review-full.md`.

## Ergebnis-Zusammenfassung je Task

| Task | Commit(s) | Ergebnis |
|------|-----------|----------|
| T0 | `bd4f364` (+ `78a9e1c` Plan-Korrektur) | Scaffold, B-022 neu |
| T1 | `8cd44de` | `stabzauber.md`: 12 Rituale / 4 Gruppen, Apport, Fehlwerte, Fassungsvermögen; L24 ✅; L25(c) bestätigt |
| T2 | `87119f9` | Detailregeln der 7 knappen Abschnitte; L9/L10 ✅; 32 Tests |
| T3 | `8cd062f` | Rohsternchen in 10 Dateien (39 Zeilen) escaped; 26 Tests; Render-Diff = Odem Arcanum |
| T4 | `2556bd4` | Quelle-Fallback im Parser; 23 Tests; Render byte-identisch |
| T5 | `270bae4`, `939ca0e`, `75f9312` | `WIKILINK_RE`-Anzeigetext, Kampf-Hooks/`.index`-Härtung, `test_steigerbar.py` synthetisch (`tests/heldfixtures.py`) |
| T6 | `4f289aa` | 9 Anker-Links in `rituale.md` + 3 Tests |
| Polish | `7fa707e` | 9 Minor-Funde der Task-Reviews |
| Final-Fixes | `4698da1` | L25 geschlossen, Quelle S. 105–115, Anführungszeichen |
