# Sprint 027 — Verifikation

Stand: HEAD nach Gesamt-Review-Fixwelle (`8e5b150`). Alle Zahlen sind gemessen oder
nachgerechnet, keine übernommen.

## Test-Suite

- `python -m pytest -W error -q` aus `helden/_tools/`, nach Löschen aller `__pycache__`:
  **652 passed** (Ausgangsstand Sprint 026: 633).
- Zuwachs: +4 T1 (D-054, davon 1 in Fix-Runde 1), +11 T2 (D-055, davon 4 Netto in
  Fix-Runde 1 gegenüber v1's 7 — v1 komplett ersetzt statt geflickt), +3 T4 (B-027,
  Mutationsprobe parametrisiert).

## Druck (das Sprintziel)

| EPIC | Prüfung | Ergebnis |
|---|---|---|
| D-054 | LeP/AsP/AuP im Ausdruck sichtbar | Alle drei Zeilen `rgb(26,18,8)` auf `rgb(236,228,208)` = **14,62:1**, Print-Emulation + echter `page.pdf()`+`pdftoppm`-Pfad |
| D-054 (Fix-Runde 1) | `.vital-max`/`.vital-sep`-Opazität | Vorher `rgb(88,81,68)` = 6,20:1 (verdünnt durch un-zurückgesetztes `opacity:0.7`), nachher 14,62:1, identisch zu `.vital-input` |
| D-055 | Verlaufstext vollständig im Ausdruck | v1 (Textarea-Resize) verlor bei normaler Fensterbreite (1280px) weiterhin **48 Zeilen / ~17 %** gegenüber der bei 718px verifizierten Fassung — Breiten-Mismatch Bildschirm- vs. Druck-Layout |
| D-055 (Fix-Runde 1) | Druck-Mirror statt Resize | `page.pdf()`+`pdftotext` bei **1280px UND 718px**: vollständiger Kopf+Ende-Text aller 4 Sessions, inkl. längster (3647 Zeichen) |
| D-056 | Getönte Papieroptik | Kein Code-Change (Ruling: Weiß bleibt Zielzustand) — reine Tracker-Dokumentation |
| B-027 | Redundante Bedingung | Entfernt, Verhalten für `'—'`/`''`/`'-'`/Zahl/`'abc'` unverändert (Mutationsprobe) |

## Static Render

- `python render-held.py illaen-baernhold` nach jedem Fix erfolgreich; `output/illaen-baernhold-dashboard.html`
  bei jedem Commit mit aktualisiert (T1, T2 v1, T2 Fix-Runde 1 — T4 unverändert, da B-027 keinen
  beobachtbaren Render-Unterschied erzeugt).
- Gesamt-Review bestätigte den finalen Render-Stand intern konsistent: kein `vital::after`/`data-current`
  mehr enthalten, eingebettetes CSS trägt das finale `opacity:1 !important`, `chronik.js`-Inline-Kopie
  passt zum Quellstand (4 `wasHeight`/Mirror-Vorkommen abgeglichen).

## Unberührte Bereiche

- `git diff --numstat f07b6f1..HEAD -- wiki helden/illaen-baernhold abenteuer` → **leer**.
  Weder Wiki noch User-Domäne wurden angefasst.

## Reviews

- **T1 (D-054):** Task-Review fand 1 Important (`.vital-max`/`.vital-sep`-Opazität nie zurückgesetzt) →
  1 Fix-Runde, Re-Review: ADDRESSED, keine neue Regression. 2 Minor deferred (Font-Weight-DRY,
  unreset `border-radius` — beide harmlos).
- **T2 (D-055):** Task-Review Approved (0 Critical/Important) — die Gesamt-Review fand danach den
  Breiten-Mismatch, den eine Diff-only-Review strukturell nicht sehen konnte (er verlangte einen
  echten `page.pdf()`-Lauf bei einer zweiten Fensterbreite). 2 Minor aus dem Task-Review wurden durch
  den Mirror-Fix gegenstandslos.
- **T4 (B-027):** Spec ✅ / Approved, 0 Findings — beim ersten Durchgang.
- **Gesamt-Review (Opus):** *Ready to merge: With fixes* — 0 Critical, 1 Important (D-055
  Breiten-Mismatch), 2 Minor (beide durch denselben Fix gegenstandslos). 1 Fix-Runde, gescopter
  Re-Review: alle 3 Punkte ADDRESSED, keine neue Regression.
- Reviewer haben durchgehend **selbst nachgemessen** statt Berichte zu übernehmen — die Gesamt-Review
  maß eigenständig bei zwei Fensterbreiten und widerlegte damit die "vollständig sichtbar"-Behauptung
  von T2 v1.

## Methodenbefund (neu, Sprint 027)

**`beforeprint` misst im Bildschirm-Layout, nicht im Druck-Layout.** Ein Fix, der zum Messzeitpunkt
(Bildschirmbreite) korrekte Werte berechnet (`scrollHeight`, Höhe, o. ä.) und sie dann als feste
Inline-Werte für den Druck setzt, kann bei einer anderen Druckbreite falsch sein — und die eigene
Verifikation bei einer zufällig breitenneutralen Viewport-Größe (718px, wo Druck- und Bildschirmbreite
zusammenfallen) sieht den Fehler strukturell nicht. Ein print-only Element, das der Browser selbst im
Druck-Layout umbricht (statt eine im Bildschirm-Layout berechnete Zahl mitzugeben), ist robuster gegen
genau diese Klasse Fehler. Folge fürs Verfahren: Breiten-Verifikation muss **mindestens zwei
unterschiedliche** Fensterbreiten prüfen, nicht nur die etablierte 718-px-Druckbreiten-Annäherung.
