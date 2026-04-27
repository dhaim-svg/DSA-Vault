# /dsa-naechstes-kapitel

Verarbeitet das nächste offene Kapitel (oder den nächsten Buchstaben-Batch)
des aktiven DSA-Buchs via Sub-Agent-Dispatch.

## Ablauf

### 1. Status lesen
- `DSA-STATUS.md` lesen: aktives Buch + nächstes offenes Kapitel (Status ⚪ oder 🟢).
- Falls kein aktives Buch: User fragen.

### 2. Kapitel-Datei / Batch lokalisieren
- **Kapitelbasierte Bücher (WdH, WdS, WdZ, WdG):**
  Datei: `raw/pdf-extracted/<buch-slug>/kapitel-NN-<slug>.txt`
  Falls noch nicht vorhanden: `python raw/pdf-extracted/_tools/split-chapters.py <buch-slug>`
- **Alphabetische Bücher (LC-Stil, z.B. Liber Liturgium):**
  Nächsten noch nicht verarbeiteten Buchstaben-Batch aus `full.txt` bestimmen
  (analog LC-01 bis LC-10 — ~25–35 Einträge pro Batch).

### 3. Sub-Agent dispatchen
Agent-Typ: `general-purpose`. Briefing enthält zwingend:
- Exakter Pfad zur Kapitel-/Batch-Datei
- Ziel-Ordner in `wiki/dsa-4.1/` (z.B. `liturgien/`)
- Frontmatter-Schema für diesen Artikel-Typ (Pflichtfelder: `typ`, `quelle`, `seite` + typspezifische wie `lkw`, `aspekte`, `grad`)
- Alle Konventionen aus DSA-STATUS.md → "Zentrale Design-Entscheidungen"
- Liste bereits vorhandener Artikel in diesem Ordner (keine Duplikate)
- Expliziter Auftrag:
  1. Alle Einträge im Kapitel identifizieren
  2. Pro Eintrag: Artikel mit korrektem Frontmatter schreiben
  3. `_<ordner>.md` Übersichtstabelle aktualisieren (Zeilen ergänzen)
  4. DSA-STATUS.md updaten: Kapitel auf ✅, "Letzte Aktivität" Zeile ergänzen
  5. Kurzreport zurückgeben: neue Dateinamen + offene Fragen

### 4. Verifikation nach dem Sub-Agent
- `git status --short` ausführen — neue Dateien sichtbar?
- 1 Stichproben-Artikel lesen: Frontmatter vollständig, Wiki-Links ok?
- DSA-STATUS.md: Kapitel wirklich auf ✅ gesetzt?

### 5. Report an den User
Format: "**Kapitel [Name] ✅** — X neue Artikel: [Dateiliste]. Stichprobe ok.
[Offene Fragen des Sub-Agents, falls vorhanden.]"
