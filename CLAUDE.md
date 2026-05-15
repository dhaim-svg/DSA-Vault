# Knowledge Base Rules

- This is an LLM-maintained knowledge base. You are the librarian.
- The wiki/ folder is YOUR domain — you write and maintain everything in it.
  I rarely edit wiki files directly.
- raw/ is the inbox. When I dump files here, you process them into the wiki
  during a "compile" step.
- wiki/_master-index.md is the entry point. It lists every topic folder with
  a one-line description. Always keep this up to date.
- Each topic gets its own subfolder in wiki/ (e.g., wiki/ai-agents/) with its
  own _<foldername>.md that lists all articles in that topic with brief descriptions.
  Example: wiki/rassen/_rassen.md, wiki/kulturen/_kulturen.md.
  The underscore prefix keeps the file at the top of the folder in Obsidian's explorer
  and gives each index a unique, readable name in the graph view.
- Always use [[wiki links]] to connect related concepts across topics.
- When compiling raw material:
  1. Read the raw file
  2. Decide which topic it belongs to (or create a new one)
  3. Write a wiki article with key takeaways and relevant links
  4. Update that topic's _<foldername>.md
  5. Update wiki/_master-index.md
  6. If a raw file spans multiple topics, create articles in both and cross-link
- Keep articles concise — bullet points over paragraphs.
- Include a ## Key Takeaways section in every wiki article.
- output/ is for query results and generated reports.
- When answering questions, read _master-index.md first to navigate, then
  drill into the relevant topic _<foldername>.md (e.g. _rassen.md), then read specific articles.
- When I ask you to "compile", process everything in raw/ that hasn't been
  compiled yet into the wiki.
- When I ask you to "audit" or "lint", review the wiki for inconsistencies,
  broken links, gaps, and suggest improvements.

# Helden und Abenteuer

`helden/` und `abenteuer/` sind **User-Domäne** (persönliche Spieldaten) — kein automatisches LLM-Schreiben ohne explizite Anfrage.

## Grundregel

- `wiki/` = LLM-Bibliothek (Regelwerk, Referenz) — du pflegst das.
- `helden/` = Charakterbögen des Spielers — du liest, du änderst NUR auf explizite Anfrage.
- `abenteuer/` = Spieltagebuch — du liest, du hilfst bei Strukturierung, du schreibst NUR auf Anfrage.

## Helden-Workflow

- Konventionen (Datei-Aufteilung, YAML-Frontmatter) → `helden/_helden.md`
- Beim Hinzufügen neuer Zauber/SF/Talente: Wiki-Artikel-Existenz prüfen (Glob/Grep), fehlende als `## Offene Wiki-Verweise` am Ende notieren.
- **Steigerung**: auf Anfrage `steigerungs-log.md` + betroffene Datei + `_helden.md`-Index aktualisieren.

## Session-Workflow

- Konventionen (Format, Frontmatter, Sections) → `abenteuer/_abenteuer.md`
- Session-Dateien: `YYYY-MM-DD-session-NN.md` direkt im Kampagnen-Ordner.

## Wiki-Lücken

Wiki-Mängel, die beim Spielereinsatz auffallen, werden in `wiki-luecken.md` (Vault-Root) gesammelt — jeder Eintrag mit Datum, betroffener Wiki-Datei, Befund, Vorschlag.

# DSA-Regelwerk PDF-Extraktion

DSA-Regelwerke liegen als PDFs unter:
  `C:\Users\David\Google Drive\DSA\DSA_Buecher\001. Regelwerke\005. DSA4.1\`

Statt raw/ zu nutzen, werden PDFs systematisch in wiki/ extrahiert.

## Session-Start: Status lesen

**Bei jeder neuen Session zuerst DSA-STATUS.md lesen**, um zu sehen welches Buch/Kapitel als nächstes dran ist und welche Konventionen bereits festgelegt wurden:
- `DSA-STATUS.md` (Vault-Root) — aktueller Fortschritt, Kapitel-Checklist, offene Punkte
- `raw/pdf-extracted/EXTRACTION-PLAN.md` — permanenter Langzeit-Plan (Pipeline, Templates, Buch-Reihenfolge)

Am Ende jedes Kapitels `DSA-STATUS.md` aktualisieren: Kapitel auf ✅ setzen, nächstes auf 🟢, "Letzte Aktivität" ergänzen.

## Ordnerstruktur (topic-basiert)
wiki/dsa-4.1/ enthält Unterordner pro Thema (rassen/, zauber/, rituale/, …),
nicht pro Quellenbuch. Jeder Unterordner hat ein _<ordnername>.md mit Übersichtstabelle
(z.B. rassen/_rassen.md, kulturen/_kulturen.md). Unterstrich-Prefix = Top-Sortierung + eindeutiger Graph-Name.

## Extraktions-Workflow pro Buch
1. pdftotext -layout -enc UTF-8 "<pdf>" raw/pdf-extracted/<buch>/full.txt
2. raw/pdf-extracted/_tools/split-chapters.py zerlegt full.txt in Kapitel-Dateien
3. Pro Kapitel interaktiv: Ankündigung → OK vom User → Extraktion → Artikel schreiben → Report

## Artikel-Templates
- Kapitelartikel: kein Frontmatter, Zitatblock mit Quelle+Seite, ## Key Takeaways, ## Verwandte Artikel
- Nachschlage-Einheit (Rasse, Zauber, Ritual, …): YAML-Frontmatter (typ, gp, quelle, seite, …)
- _<ordnername>.md pro Ordner: Übersichtstabelle mit [[wiki links]] (z.B. _kulturen.md, _rassen.md)

## Errata
Errata-PDFs (001. Errata/) direkt in betroffene Artikel einarbeiten, Fußnote *(Errata <jahr>)*.

## Rituale vs. Zauber vs. Liturgien
- zauber/ — einzelne Zauber
- rituale/ — alle Rituale (flach, Frontmatter tradition: stabzauber/kugelzauber/…)
- liturgien/ — einzelne Liturgien

## Gitignore
raw/pdf-extracted/** ist gitignored (urheberrechtliches Material), außer raw/pdf-extracted/_tools/.

## Compile-Befehl für DSA
Wenn ich "compile DSA" oder "nächstes Kapitel" sage:
- Nächstes unbearbeitetes Kapitel aus dem aktiven Buch ankündigen
- Auf OK warten
- Artikel schreiben, _<ordnername>.md aktualisieren, _master-index.md aktualisieren
- Abschlussreport mit neuen Dateien und offenen Fragen

## Long-Session-Modus für ganze Bücher

Wenn der User "ganzes Buch in einer Session", `/dsa-buch <kürzel>`, oder explizit
"ohne Stops durchziehen" sagt: **Long-Session-Modus** aktivieren.

**Kernidee:** Bulk-Texte (30k+ Zeilen) passen nicht in einen einzelnen Kontext.
Lösung: Pro Kapitel (oder Buchstaben-Batch) einen `general-purpose` Sub-Agent
dispatchen. Der Sub-Agent liest seinen Abschnitt und schreibt die Artikel selbst.
Die Hauptsession orchestriert nur — der Bulk-Text liegt nie im Hauptkontext.

### Setup (einmalig pro Buch)
1. `full.txt` prüfen — falls fehlt: `pdftotext` ausführen (PDF-Pfad aus DSA-STATUS.md)
2. Kapitel-Splits prüfen — falls fehlen UND Buch ist kapitelbasiert:
   `python raw/pdf-extracted/_tools/split-chapters.py <buch-slug>`
3. Alphabetische Bücher (LC-Stil, z.B. Liber Liturgium): kein Split nötig.
   Stattdessen: Buchstaben-Batches à ~25–35 Einträge direkt aus `full.txt`.

### Sub-Agent-Briefing (Pflichtinhalt)
Jedes Briefing muss enthalten:
- Exakter Pfad zur Kapitel-/Batch-Datei
- Ziel-Ordner und Frontmatter-Schema (Pflichtfelder: typ, quelle, seite, …)
- Konventionen aus DSA-STATUS.md → "Zentrale Design-Entscheidungen"
- Liste bereits vorhandener Artikel (keine Duplikate)
- Auftrag: Artikel schreiben + `_<ordner>.md` updaten + DSA-STATUS.md updaten + Kurzreport

### Interaktivitäts-Modus (Hybrid)
- **Kapitel 1:** Sub-Agent dispatchen → Stichprobe → **User-OK einholen**
- **Kapitel 2+:** Autonom durchziehen ohne Rückfragen
- **Unterbrechen NUR bei:** fehlenden Pflicht-Frontmatter-Feldern in >3 Artikeln,
  unklarer Quellenseite, Errata-Konflikten, fehlgeschlagenem Kapitel-Split

### Verifikation nach jedem Sub-Agent
- `git status --short` — neue Dateien vorhanden?
- `_<ordner>.md` — neue Zeilen eingetragen?
- DSA-STATUS.md — Kapitel auf ✅ gesetzt?
- 1 Stichproben-Artikel: Frontmatter korrekt, Wiki-Links syntaktisch ok?
