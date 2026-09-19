# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

_(keine)_

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-018 | Zauber: Inline-Vorschau des Artikels (Obsidian-Link bleibt) | L | ready | Manual-Test 01.06.2026 |
| D-032 | Chronik-Tab (read-only Viewer des letzten Imports) | M | ready | Chronik-Modus-Plan 16.09.2026 |
| D-035 | /session-compile Kommando (ruft Import D-030 zuerst) + Aufräumen (User-Freigabe nötig) | M | ready | Chronik-Modus-Plan 16.09.2026 |
| D-036 | NSC-/Orts-Register aus kompilierten Sessions | M | ready | Chronik-Modus-Plan 16.09.2026 |
| D-037 | dashboard.html.j2 in Partials + eigenes CSS zerlegen | L | ready | Chronik-Modus-Plan 16.09.2026 |

### Gestrichen

| EPIC | Title | Gestrichen am | Grund |
|------|-------|----------------|-------|
| D-033 | Quick-Capture in Footer-Bar | 19.09.2026 | Kein Live-Schreibpfad mehr (D-030-Fallback: Drive bleibt Quelle) |
| D-034 | Ereignis-Auto-Log | 19.09.2026 | Dito — hätte auf demselben Live-Schreibpfad wie D-033 aufgebaut |

Details siehe Beschreibung unten (D-033/D-034 wurden nicht einfach vergessen — bewusst gestrichen, s. D-030).

### Beschreibungen

**D-018 — Zauber: Inline-Vorschau**
Klick auf Link öffnet Obsidian (gut). Gewünscht: kleine Ansicht im Dashboard, die den Artikel direkt anzeigt; `↗`-Obsidian-Link bleibt. Heute: nur `obsidian://`-URI via `rendering.py:obsidian_uri()`; kein Read-Endpoint. Umfang: neuer Flask-Endpoint liest Zauber-`.md` + rendert HTML; Inline-Panel/Modal im Zauber-Tab (`dashboard.html.j2:1311-1506`); Klick-Guard in `static/dice.js:520-532` beachten. Seit Sprint 012 günstiger: `popover` + CSS Anchor Positioning sind seit Firefox 147 (Jan. 2026) Baseline — spart die JS-Positionierung; `@position-try` (Flip bei Overflow) braucht noch einen sinnvollen Fallback (Safari 18.4+).

**D-032 — Chronik-Tab (read-only Viewer)** *(Umfang reduziert 19.09.2026 — Junction-Ansatz für D-030 verworfen, Drive bleibt Quelle, s. Sprint-014-Handoff für Details)*
Ersetzt den Journal-Tab (`dashboard.html.j2:1799-1861`, `static/journal.js`), der ohne echte Session-Dateien leerläuft. Zeigt den zuletzt importierten Stand von `chronik.md` (D-030-Import, kein Live-Sync mehr) — **rein lesend**, kein „Neuer Spielabend"-Button und kein Zurückschreiben (jeder nächste Import würde eigene Einträge sonst überschreiben). Timeline-Render: IG-Tage als Gruppen, Szenen-Marker als Zwischenüberschriften, Bilder inline. Ältere Abende eingeklappt (`<details>`). Meta-Sektionen als eigene Karten. Hygiene-Auflage: neuer Tab in `templates/partials/chronik.j2`, eigenes CSS in `static/chronik.css` — `dashboard.html.j2` (2035+ Zeilen) nicht weiter aufblähen. Braucht D-030 (Import) + D-031 (Parser).

**D-033 / D-034 — Quick-Capture & Ereignis-Auto-Log — *entfallen 19.09.2026***
Beide Live-Editing-Features setzten eine synchron beschreibbare Chronik-Datei im Vault voraus. Da Drive Quelle bleibt (D-030-Fallback, Junction-Ansatz gescheitert), gibt es keinen Live-Schreibpfad mehr, in den das Dashboard schreiben könnte, ohne beim nächsten Import überschrieben zu werden. Ersatzlos gestrichen — der User schreibt weiterhin direkt in Google Drive, keine Dashboard-Interaktion während des Spiels vorgesehen.

**D-035 — /session-compile + Aufräumen**
Neues Kommando `.claude/commands/session-compile.md`. Ruft zuerst den Import (D-030, `chronik_import.py`) auf, um den aktuellen Stand aus Drive zu holen, dann: nimmt einen Spielabend aus `chronik.md`, erzeugt strukturierte Session-Datei nach `abenteuer/_abenteuer.md`-Konvention, verlinkt ins Wiki, aktualisiert `_drachenchronik.md`, trägt Wiki-Lücken ein. Rohchronik bleibt unangetastet. Aufräumen (**braucht explizite User-Freigabe**, `abenteuer/` ist User-Domäne): Platzhalter `2025-10-04-session-01.md` löschen (Testdaten), `_drachenchronik.md` Status/Sessions-Tabelle korrigieren.

**D-036 — NSC-/Orts-Register**
Aus den per D-035 kompilierten Sessions extrahiert (`nsc.md`, `orte.md`), plus Suche im Chronik-Tab. Mehrwert gegenüber flacher MD-Datei — die Chronik nennt allein in vier Spielabenden ~15 NSCs und ~8 Orte. Braucht D-035.

**D-037 — Template-Zerlegung**
`dashboard.html.j2` vollständig in Partials + ausgelagertes CSS zerlegen (Technik-Schuld-Aufräumen, kein User-Feature). Sinnvoll bevor D-032 (Chronik-Tab) den Umfang weiter erhöht, aber kein Blocker.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-031 | parsers/chronik.py (Spielabend/IG-Tag/Szenen-Parser, verifiziert gegen echte Chronik) | M | 014 |
| D-030 | Chronik-Import-Skript (Drive → Vault, einseitig — Junction-Ansatz verworfen, s. Sprint-014-Handoff) | S | 014 |
| D-029 | Aussehen vervollständigen (Gewicht-Feld, offene Felder visuell markiert, Portrait-Plumbing) | S | 013 |
| D-028 | Erschaffungsprobe + AsP je Stabzauber (Nachschlage-Info) | S | 013 |
| D-027 | Zauberspeicher-Auslöseprobe (MU/IN/KL, würfelbar, +1 Erschwernis/Slot) | M | 013 |
| D-026 | Inline-Eigenschaftswerte vervollständigen (Kampftechniken, Wundabzug; `.mod-probe` bewusst ausgenommen — Modifikator-Formeln, keine Attribut-Proben) | M | 013 |
| D-025 | Eigenschafts-Leiste über Talente-/Zauber-Tab (sticky, mit Wund-/Zustandsbadge) | M | 013 |
| D-024 | Stabzauber: allgemeine Aktivierungsregel als Hinweiszeile | S | 012 |
| D-023 | Talente/Zauber: Eigenschaftswerte inline + Probe prominenter | M | 012 |
| D-022 | Profil: Aussehen & Kleidung als strukturierte Sektion | M | 012 |
| D-021 | Steigern: Session-Erfahrungs-Modifikator (SKT-Spaltenverschiebung) | M | 011 |
| D-020 | Steigern: Steigerungsspalte in eigene Tabelle (steiger-table) | M | 010 |
| D-019 | Steigern: Experiment-/Auswahl-Modus (Warenkorb) | L | 010 |
| D-017 | Sprachen: Komplexitäts-Spalte ausrichten | S | 009 |
| D-016 | Profil: Schlechte Eigenschaften / Prinzipientreue ohne Truncation | S | 009 |
| D-015 | Inventar: Formatierung & abgeschnittener Text | S | 009 |
| D-014 | Footer-Layout: Session/Sichern-Überlappung + Commit-Feld gruppieren | S | 009 |
| D-013 | Vitalia-Stepper in einer Reihe | S | 009 |
| D-012 | Würfel-Panel Lesbarkeit (tab-übergreifend) | S | 009 |
| D-011 | showIndicator-Dedup | S | 008 |
| D-010 | Commit-Message-Input | S | 008 |
| D-009 | Stufen-Aufstieg | M | 007 |
| D-008 | Sprachen mit Komplexitäts-Grenze | S | 007 |
| D-007 | Session-Commit-Button | S | 006 |
| D-006 | Session-Notizen → Journal | M | 006 |
| D-005 | Zauberspeicher im Stab | M | 005 |
| D-004 | Inventar / Geld / Verbrauch | M | 004 |
| D-003 | Tab-Navigation + AP & Steigerung | L | 003 |
| D-001 | Flask-Server + Vitalia Write-back + Wunden + Zustände | L | 001 |
| D-002 | Würfelintegration (3W20 Proben, Schaden, Panel) | L | 002 |
