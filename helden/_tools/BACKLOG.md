# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

| EPIC | Title | Effort | State | Sprint |
|------|-------|--------|-------|--------|
| D-042 | Chronik-Parser: `Datum: 13. Phex -> Start`-Zeile als IG-Datum erkennen | S | in-progress | 017 |
| D-036 | NSC-/Orts-Register aus kompilierten Sessions (generiert zur Render-Zeit, 3. Ansicht im Chronik-Tab, clientseitige Suche; keine Dateien in `abenteuer/`) | M | in-progress | 017 |
| D-040 | Mobile 400 px: horizontaler Überlauf in Zauber-/Steigern-/Inventar-/Profil-Tab | S | in-progress | 017 |

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-018 | Zauber: Inline-Vorschau des Artikels (Obsidian-Link bleibt) | L | ready | Manual-Test 01.06.2026 |
| D-041 | Wundregel-/Zustände-Audit gegen das Wiki (Wund-Mali, Schwellen, Zustandswerte) | M | ready | Browser-Check D-038, 19.09.2026 |

### Gestrichen

| EPIC | Title | Gestrichen am | Grund |
|------|-------|----------------|-------|
| D-033 | Quick-Capture in Footer-Bar | 19.09.2026 | Kein Live-Schreibpfad mehr (D-030-Fallback: Drive bleibt Quelle) |
| D-034 | Ereignis-Auto-Log | 19.09.2026 | Dito — hätte auf demselben Live-Schreibpfad wie D-033 aufgebaut |

Details siehe Beschreibung unten (D-033/D-034 wurden nicht einfach vergessen — bewusst gestrichen, s. D-030).

### Beschreibungen

**D-018 — Zauber: Inline-Vorschau**
Klick auf Link öffnet Obsidian (gut). Gewünscht: kleine Ansicht im Dashboard, die den Artikel direkt anzeigt; `↗`-Obsidian-Link bleibt. Heute: nur `obsidian://`-URI via `rendering.py:obsidian_uri()`; kein Read-Endpoint. Umfang: neuer Flask-Endpoint liest Zauber-`.md` + rendert HTML; Inline-Panel/Modal im Zauber-Tab (`templates/partials/zauber.j2`, seit Sprint 015); Klick-Guard in `static/dice.js:520-532` beachten. Seit Sprint 012 günstiger: `popover` + CSS Anchor Positioning sind seit Firefox 147 (Jan. 2026) Baseline — spart die JS-Positionierung; `@position-try` (Flip bei Overflow) braucht noch einen sinnvollen Fallback (Safari 18.4+).

**D-033 / D-034 — Quick-Capture & Ereignis-Auto-Log — *entfallen 19.09.2026***
Beide Live-Editing-Features setzten eine synchron beschreibbare Chronik-Datei im Vault voraus. Da Drive Quelle bleibt (D-030-Fallback, Junction-Ansatz gescheitert), gibt es keinen Live-Schreibpfad mehr, in den das Dashboard schreiben könnte, ohne beim nächsten Import überschrieben zu werden. Ersatzlos gestrichen — der User schreibt weiterhin direkt in Google Drive, keine Dashboard-Interaktion während des Spiels vorgesehen.

**D-036 — NSC-/Orts-Register**
Aus den per D-035 kompilierten Sessions extrahiert (`nsc.md`, `orte.md`), plus Suche im Chronik-Tab. Mehrwert gegenüber flacher MD-Datei — die Chronik nennt allein in vier Spielabenden ~15 NSCs und ~8 Orte. D-035 ist erledigt (Sprint 016): die vier Spielabende liegen als Session-Dateien vor (`abenteuer/drachenchronik/2026-*-session-0N.md`, Abschnitte „Neue NSCs / Orte").

**D-040 — Mobile 400 px: horizontaler Überlauf**
Beim Browser-Check zu D-039 (Static-Render unter `file://`, 400 px Breite) scrollt die Seite in vier Tabs horizontal: Zauber (1019 px, `.wirkung`/`.wirkung-cell`), Steigern (442 px, `.steiger-table`), Inventar (485 px, `.inv-add-btn`), Profil (450 px, `SECTION.card`). Kampf/Talente/Chronik/Sprachen bleiben ≤ 400 px. Rein CSS, im Server-Modus identisch; vorher unter `file://` nur unsichtbar, weil dort nie ein Tab angezeigt wurde. Zusätzlich bekannt (Sprint 015): bei 400 px überlappen Banner-Titel und die feste Fußleiste. Fix-Skizze: `overflow-wrap`/`min-width:0` bzw. Tabellen in `overflow-x:auto`-Container, danach per Headless-Chrome `scrollWidth ≤ 400` je Tab prüfen.

**D-041 — Wundregel-/Zustände-Audit**
`static/session.js:29` trägt seit Mai 2026 ein `TODO: verify exact rules in wiki/dsa-4.1/ (zones, thresholds)`. Aktuell: −2 je Wunde (`computeWundPenalty`), Zustands-Mali fest (Schmerz −2, Furcht −2, Betäubt −4, Verwirrt −2, Erschöpft −2), und das Overlay zieht pauschal von **allen** `[data-attr]`-Werten ab (203 Stück, auch dort, wo die Regel es nicht verlangt). Nichts davon ist gegen DSA 4.1 geprüft — erst mit D-038 (Sprint 016) läuft der Code überhaupt im Browser. Umfang: Wundregeln/Zustände im Wiki nachlesen (`wiki/dsa-4.1/grundregeln/`), Abweichungen auflisten, Werte/Geltungsbereich korrigieren, Python-Würfelmathe und JS-Spiegel (`dice.js`) angleichen, ggf. `wiki-luecken.md`-Eintrag.

**D-042 — Chronik-Parser: `Datum:`-Zeile**
Der 04.06.2026-Abend beginnt mit `Datum: 13. Phex -> Start`. `parsers/chronik.py::IG_DATUM_RE` erkennt nur fette Zeilen der Form `**17. Phex**`; die `Datum:`-Zeile landet daher als Textblock in einem IG-Tag **ohne** Datum (verifiziert 19.09.2026: erster IG-Tag `ig_datum=None`). Betrifft die Roh-Ansicht im Chronik-Tab. Fix-Skizze: zusätzliches Muster `^Datum:\s*(\d{1,2}\.\s+<Monat>)(?:\s*->\s*(.+))?$`, Zusatz („Start") als Suffix; Test mit der echten Zeile. Design-Frage: Leerer IG-Tag (Überschrift ohne Inhalt) wird weiterhin verworfen.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-039 | Static-Render interaktiv: JS wird eingebettet (`JS_FILES`/`js_files()`/`inline_js`), Hinweis-Banner `#static-hinweis`, README — Tabs/Würfel unter `file://` | S | 016 |
| D-038 | Bug: `session.js` lief nie (`IS_SERVED`-Kollision) → IIFE + Top-Level-Kollisionstest, Browser-Gegenprüfung 9/9 | S | 016 |
| D-035 | `/session-compile`-Kommando + 4 Spielabende kompiliert (Session 1–4), Platzhalter-Session entfernt | M | 016 |
| D-037 | dashboard.html.j2 in Partials + eigenes CSS zerlegen (CSS → static/*.css, zur Render-Zeit eingebettet; 8 Tab-Partials; geteilter Render-Kontext) | L | 015 |
| D-032 | Chronik-Tab (📜, Roh/Kompiliert-Umschalter, read-only Roh-Ansicht, /chronik-bild-Route, Parser-Fix Bild+Text) | M | 015 |
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
