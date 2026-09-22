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

## Dashboard Sprint-Workflow

Dashboard-Entwicklung (`helden/_tools/`) läuft in Sprint-Sessions.
- **EPIC-Tracker:** `helden/_tools/BACKLOG.md` (D-NNN-IDs, State, Effort)
- **Sprint-Pläne:** `helden/_tools/sprints/sprint-NNN/plan.md`
- **Handoff-Notes:** am Session-Ende `sprints/sprint-NNN/handoff.md` schreiben (fertig / als nächstes / Blocker)
- **Laufende Sprint-Nr.:** 33
- **Ablauf:** `/sprint-plan` (Skill) → Freigabe → `/sprint-run` (Skill, Subagent-Driven Development mit
  den Projekt-Agents `sprint-implementer`, `sprint-task-reviewer`, `sprint-final-reviewer` in
  `.claude/agents/`, zwei-stufige Review spec + code quality pro Task) → `/sprint-wrap` (Skill).
  Details je Skill-Datei, nicht hier.

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

# Backlog

Übergreifender Aufgaben-Tracker liegt in `backlog.md` (Vault-Root).

- Spezialisierte Tracker bleiben: `wiki-luecken.md` (Wiki-Mängel mit Buchquelle), `DSA-STATUS.md` (Buch-Extraktion).
- Neue Tasks, die nicht sofort erledigt werden, kommen ins Backlog (Priorität = Position von oben in `## Backlog`).
- Tasks die mehrere Bereiche betreffen (z.B. Held + Dashboard) werden in einer Zeile geführt.
- LLM-Pflege: Status-Updates beim Start/Ende von Tasks, Done-Umzug mit Datum.
- Kategorien: `wiki` / `held` / `dashboard` / `abenteuer` / `tooling` / `meta`

# DSA-Regelwerk PDF-Extraktion

DSA-Regelwerke liegen als PDFs unter `C:\Users\David\Google Drive\DSA\DSA_Buecher\001. Regelwerke\005. DSA4.1\`
und werden systematisch in `wiki/dsa-4.1/` extrahiert (topic-basierte Unterordner, nicht pro Buch;
Übersichtstabelle je Ordner in `_<ordnername>.md`). Alle 6 Bücher + Errata sind ✅ abgeschlossen
(Stand siehe `DSA-STATUS.md`). Session-Start-Check, Kapitel-Workflow, Templates, Errata-Vorgehen und
der Long-Session-Modus für ganze Bücher (`/dsa-buch`) stehen im Skill **`dsa-extraktion`** —
wird bei Bedarf automatisch geladen ("compile DSA", "nächstes Kapitel", neues Buch/Errata).

- `zauber/` — einzelne Zauber · `rituale/` — alle Rituale (flach, `tradition:`-Frontmatter) ·
  `liturgien/` — einzelne Liturgien.
- `raw/pdf-extracted/**` ist gitignored (urheberrechtliches Material), außer `_tools/`.
