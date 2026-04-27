# /dsa-buch

Verarbeitet ein ganzes DSA-Buch in einer Session via Sub-Agent-Dispatch (Long-Session-Modus).

**Argument:** `$ARGUMENTS`
(Buch-Kürzel: `LL` = Liber Liturgium, `WDG` = Wege der Götter, `WDA` = Wege der Alchimie, `WDE` = Wege des Entdeckers)

---

## Phase 1: Setup

1. Buch-Kürzel aus `$ARGUMENTS` → PDF-Pfad und Buch-Slug aus DSA-STATUS.md ermitteln.

2. **full.txt prüfen:** `raw/pdf-extracted/<buch-slug>/full.txt`
   - Falls fehlt: pdftotext ausführen:
     `"D:/Projects/Tools/poppler-25.12.0/Library/bin/pdftotext.exe" -layout -enc UTF-8 "<pdf-pfad>" raw/pdf-extracted/<buch-slug>/full.txt`
   - Ausgabe: Dateigröße + geschätzte Zeilenzahl melden.

3. **Kapitel-Splits oder Batch-Plan:**
   - Kapitelbasierte Bücher (WdG, WdA, WdE): `python raw/pdf-extracted/_tools/split-chapters.py <buch-slug>`
     - Falls Profil fehlt: Kapitelüberschriften aus `full.txt` grep-en, PROFILE ergänzen, dann splitten.
   - Alphabetische Bücher (LL): Buchstaben-Batches à ~25–35 Einträge planen.
     Batches jetzt auflisten (A-Liturgien, B-Liturgien, …) und User kurz zeigen.

4. Kapitel-Queue aufstellen: alle zu verarbeitenden Kapitel/Batches in Reihenfolge.

---

## Phase 2: Hauptschleife (Hybrid-Modus)

### Kapitel 1 — Sanity-Check

- `/dsa-naechstes-kapitel` Ablauf ausführen (Sub-Agent dispatchen, verifizieren).
- Report + Stichprobe an User.
- **⏸ STOP — Warte auf User-OK.**
- Erst nach OK weitergehen.

### Kapitel 2+ — Autonom

Für jedes weitere Kapitel/Batch:
1. Sub-Agent dispatchen (Briefing wie in `/dsa-naechstes-kapitel` Schritt 3 beschrieben)
2. `git status --short` + DSA-STATUS.md-Diff prüfen
3. Kapitel-Fortschritt intern merken (nicht bei User abfragen)

**Unterbreche und frage den User NUR bei:**
- Fehlenden Pflicht-Frontmatter-Feldern in mehr als 3 Artikeln eines Kapitels
- Unklarer Quellenseite (PDF-Seitennummer nicht aus Text ableitbar)
- Errata-Konflikten (neuer Fund widerspricht bestehendem Artikel)
- Kapitel-Split schlägt fehl (Datei nicht gefunden, Profil fehlt)

---

## Phase 3: Abschluss

Wenn alle Kapitel/Batches verarbeitet:
1. `git status --short` ausführen
2. DSA-STATUS.md: Buch auf ✅ setzen
3. `wiki/_master-index.md`: Buch-Zeile Status auf ✅ aktualisieren
4. **Gesamtreport** an User:
   - Anzahl Kapitel verarbeitet
   - Anzahl neuer Artikel gesamt
   - Neue Dateien (git status)
   - Offene Punkte (falls vorhanden)
   - Empfehlung für nächsten Schritt (z.B. Errata-Durchgang, Stichproben-Review)
