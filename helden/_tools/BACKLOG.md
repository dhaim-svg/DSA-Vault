# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-030 | Chronik in den Vault holen (Google-Drive-Junction) | S | in-progress | Chronik-Modus-Plan 16.09.2026 |
| D-031 | parsers/chronik.py (Spielabend/IG-Tag/Szenen-Parser) | M | in-progress | Chronik-Modus-Plan 16.09.2026 |

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-018 | Zauber: Inline-Vorschau des Artikels (Obsidian-Link bleibt) | L | ready | Manual-Test 01.06.2026 |
| D-032 | Chronik-Tab (ersetzt Journal-Tab) | M | blocked | Chronik-Modus-Plan 16.09.2026 |
| D-033 | Quick-Capture in Footer-Bar | M | blocked | Chronik-Modus-Plan 16.09.2026 |
| D-034 | Ereignis-Auto-Log (Würfel/LeP/AsP/Steigerung → Chronik) | M | blocked | Chronik-Modus-Plan 16.09.2026 |
| D-035 | /session-compile Kommando + Aufräumen (User-Freigabe nötig) | M | blocked | Chronik-Modus-Plan 16.09.2026 |
| D-036 | NSC-/Orts-Register aus kompilierten Sessions | M | ready | Chronik-Modus-Plan 16.09.2026 |
| D-037 | dashboard.html.j2 in Partials + eigenes CSS zerlegen | L | ready | Chronik-Modus-Plan 16.09.2026 |

### Beschreibungen

**D-018 — Zauber: Inline-Vorschau**
Klick auf Link öffnet Obsidian (gut). Gewünscht: kleine Ansicht im Dashboard, die den Artikel direkt anzeigt; `↗`-Obsidian-Link bleibt. Heute: nur `obsidian://`-URI via `rendering.py:obsidian_uri()`; kein Read-Endpoint. Umfang: neuer Flask-Endpoint liest Zauber-`.md` + rendert HTML; Inline-Panel/Modal im Zauber-Tab (`dashboard.html.j2:1311-1506`); Klick-Guard in `static/dice.js:520-532` beachten. Seit Sprint 012 günstiger: `popover` + CSS Anchor Positioning sind seit Firefox 147 (Jan. 2026) Baseline — spart die JS-Positionierung; `@position-try` (Flip bei Overflow) braucht noch einen sinnvollen Fallback (Safari 18.4+).

**D-030 — Chronik in den Vault holen**
User schreibt real in `C:\Users\David\Google Drive\DSA\Helden\Drachenchronik.md`, außerhalb des Vaults — der Journal-Tab läuft dadurch komplett leer. Umfang: Datei nach `abenteuer/drachenchronik/chronik.md` verschieben (Bilderordner `drachenchronik-daten/` daneben), `_drachenchronik.md` bleibt strukturierter Index. Google-Drive-Anbindung per Verzeichnis-Junction (`mklink /J`). **Risiko, vor dem Verschieben verifizieren:** Google Drive for Desktop überspringt Junctions/Symlinks je nach Version — erst Junction + Testdatei anlegen, User bestätigt Sync in der Web-Oberfläche, erst dann verschieben. Fallback falls Sync nicht greift: robocopy-Mirror aus `watcher.py`, oder Zugriff unterwegs über Git statt Drive. Kein reiner Dashboard-Task — läuft direkt in der Hauptsession (Dateisystem-Operation mit echtem Störungsrisiko), nicht als Subagent. Quelle/Details: Plan `C:\Users\David\.claude\plans\ich-habe-jetzt-die-mellow-beaver.md`, Abschnitt „Sprint 014".

**D-031 — parsers/chronik.py**
Neuer Parser für das reale Chronik-Format (abgeleitet aus der echten Datei): H2 mit Datumsformat `TT.MM.JJJJ` → Spielabend, jedes andere H2 → Meta-Sektion (`Nützliche SF`, `Für später`, …). Innerhalb eines Spielabends: `**TT. <DSA-Monat>**` → IG-Datum, sonstige alleinstehende `**…**`/`*…*` → Szenen-Marker, Rest = Bullets/Bilder. Rückgabe: `{spielabende: [...], meta: {...}}`. Bestehende Helfer aus `parsers/held.py` wiederverwenden (`split_sections`, `parse_frontmatter`, `strip_wikilink`). Tests analog `tests/test_kampagne.py`, Fixture synthetisch (keine echten Kampagnendetails im Repo). Reines Parsing — kein Rendering, kein Dashboard-Tab (das ist D-032).

**D-032 — Chronik-Tab**
Ersetzt den Journal-Tab (`dashboard.html.j2:1799-1861`, `static/journal.js`), der ohne echte Session-Dateien leerläuft. Oben: aktueller Spielabend + Button „Neuer Spielabend" (legt `## <heute>` an). Timeline-Render: IG-Tage als Gruppen, Szenen-Marker als Zwischenüberschriften, Bilder inline. Ältere Abende eingeklappt (`<details>`). Meta-Sektionen als eigene Karten. Hygiene-Auflage: neuer Tab in `templates/partials/chronik.j2`, eigenes CSS in `static/chronik.css` — `dashboard.html.j2` (2035+ Zeilen) nicht weiter aufblähen. Braucht D-030 (stabiler Dateipfad) + D-031 (Parser).

**D-033 — Quick-Capture**
Eingabezeile in der Footer-Bar, auf allen Tabs sichtbar. Enter → hängt `- <text>` an den aktuellen Spielabend an, kein Tab-Wechsel nötig. `#`-Präfix → neuer Szenen-Marker, `@`-Präfix → neuer IG-Tag. Zwei neue Locator-Kinds in `writers/held_writer.py`: `section_append` (Zeile an H2-Body anhängen) und `section_create` (neue H2-Sektion anlegen), beide mit vorhandenem ETag-/Lock-Mechanismus. `PATCH /api/kampagne/<camp>/value` trägt bereits `scope=kampagne` — keine neue Route nötig. `field-sizing: content` fürs Eingabefeld. Braucht D-030+D-031+D-032.

**D-034 — Ereignis-Auto-Log**
Toggle „Ereignisse mitschreiben" im Chronik-Tab (localStorage, analog `session.js`). Hooks: Würfelergebnis (`dice.js`), LeP/AsP-Änderung, Steigerung (`steigern.js`), Geld-/Inventar-Änderung (`inventar.js`) → automatischer Chronik-Eintrag. Gepuffert schreiben (Append alle ~5s), sonst zu viele PATCHes. Optional: Diktat-Knopf über Web Speech API. Braucht D-030+D-031+D-032+D-033.

**D-035 — /session-compile + Aufräumen**
Neues Kommando `.claude/commands/session-compile.md`. Nimmt einen Spielabend aus `chronik.md`, erzeugt strukturierte Session-Datei nach `abenteuer/_abenteuer.md`-Konvention, verlinkt ins Wiki, aktualisiert `_drachenchronik.md`, trägt Wiki-Lücken ein. Rohchronik bleibt unangetastet. Aufräumen (**braucht explizite User-Freigabe**, `abenteuer/` ist User-Domäne): Platzhalter `2025-10-04-session-01.md` löschen (Testdaten), `_drachenchronik.md` Status/Sessions-Tabelle korrigieren.

**D-036 — NSC-/Orts-Register**
Aus den per D-035 kompilierten Sessions extrahiert (`nsc.md`, `orte.md`), plus Suche im Chronik-Tab. Mehrwert gegenüber flacher MD-Datei — die Chronik nennt allein in vier Spielabenden ~15 NSCs und ~8 Orte. Braucht D-035.

**D-037 — Template-Zerlegung**
`dashboard.html.j2` vollständig in Partials + ausgelagertes CSS zerlegen (Technik-Schuld-Aufräumen, kein User-Feature). Sinnvoll bevor D-032 (Chronik-Tab) den Umfang weiter erhöht, aber kein Blocker.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
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
