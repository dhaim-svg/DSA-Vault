# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

_(keine)_

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-041 | Wundregel-/Zustände-Audit gegen das Wiki (Wund-Mali, Schwellen, Zustandswerte) | M | ready | Browser-Check D-038, 19.09.2026 |
| D-044 | Mobile/Touch-Feinschliff: Banner-Titel bei 400 px, Footer-Leiste, Scroll-Container-Zugänglichkeit | S | ready | Browser-Check D-040, 19.09.2026 |
| D-045 | Chronik-Druck: Ansichten-Konsistenz + Register-Filter im Druck | S | ready | Review D-036, 19.09.2026 |
| D-046 | Zauberliste: Bestandsränder — Druck-Kontrast (Name-Link, ZfW, ZD, Kosten hell auf Papier) + Grid-Überstand bei 1071–~1130 px | S | ready | Browser-Check D-018, 19.09.2026 |

### Gestrichen

| EPIC | Title | Gestrichen am | Grund |
|------|-------|----------------|-------|
| D-033 | Quick-Capture in Footer-Bar | 19.09.2026 | Kein Live-Schreibpfad mehr (D-030-Fallback: Drive bleibt Quelle) |
| D-034 | Ereignis-Auto-Log | 19.09.2026 | Dito — hätte auf demselben Live-Schreibpfad wie D-033 aufgebaut |

Details siehe Beschreibung unten (D-033/D-034 wurden nicht einfach vergessen — bewusst gestrichen, s. D-030).

### Beschreibungen

**D-033 / D-034 — Quick-Capture & Ereignis-Auto-Log — *entfallen 19.09.2026***
Beide Live-Editing-Features setzten eine synchron beschreibbare Chronik-Datei im Vault voraus. Da Drive Quelle bleibt (D-030-Fallback, Junction-Ansatz gescheitert), gibt es keinen Live-Schreibpfad mehr, in den das Dashboard schreiben könnte, ohne beim nächsten Import überschrieben zu werden. Ersatzlos gestrichen — der User schreibt weiterhin direkt in Google Drive, keine Dashboard-Interaktion während des Spiels vorgesehen.

**D-041 — Wundregel-/Zustände-Audit**
`static/session.js:29` trägt seit Mai 2026 ein `TODO: verify exact rules in wiki/dsa-4.1/ (zones, thresholds)`. Aktuell: −2 je Wunde (`computeWundPenalty`), Zustands-Mali fest (Schmerz −2, Furcht −2, Betäubt −4, Verwirrt −2, Erschöpft −2), und das Overlay zieht pauschal von **allen** `[data-attr]`-Werten ab (203 Stück, auch dort, wo die Regel es nicht verlangt). Nichts davon ist gegen DSA 4.1 geprüft — erst mit D-038 (Sprint 016) läuft der Code überhaupt im Browser. Umfang: Wundregeln/Zustände im Wiki nachlesen (`wiki/dsa-4.1/grundregeln/`), Abweichungen auflisten, Werte/Geltungsbereich korrigieren, Python-Würfelmathe und JS-Spiegel (`dice.js`) angleichen, ggf. `wiki-luecken.md`-Eintrag.

**D-044 — Mobile/Touch-Feinschliff**
Beim Browser-Check zu D-040 (Sprint 017) offen geblieben: (1) Banner-Titel „ILLAEN BAERNHOLD" ist bei 400 px rechts abgeschnitten; (2) Footer-Leiste (`#footer-bar`, `position:fixed`) hat ~33-px-Buttons (< 44 px Touch-Ziel) und verdeckt ~82 px Viewport — Alternative `position:static` unter 480 px; (3) Steigern-Tabelle scrollt ≤ 600 px im Container ohne `tabindex="0"` (per Tastatur nicht scrollbar), und der „auswählen"-Hinweis ist erst nach dem Scrollen sichtbar; (4) `.inv-add-input:first-child` hängt an der DOM-Reihenfolge — besser eine Klasse. (5) Zauber-Tab: Summary „▸ Artikel" der Artikelvorschau (Sprint 018) hat im Kompaktlayout nur ≈ 18 px Tap-Höhe (< 44 px), Sortier-Button hat bereits 44 px. Messmethode wie in D-040: `scrollWidth`/Rects bei verifiziertem `innerWidth === 400` (Playwright im served-Modus).

**D-045 — Chronik-Druck**
Der Print-Block in `static/chronik.css` druckt Roh und Kompiliert immer (`.chronik-view{display:block !important}`), das Register nur wenn es aktiv ist. Ein aktiver Register-Filter bleibt im Druck bestehen (`entry.hidden`), während Suchfeld und Umschalter ausgeblendet sind — der Ausdruck zeigt still eine Teilmenge. Zu klären: nur die aktive Ansicht drucken oder alle drei; Filter bei `beforeprint` zurücksetzen (analog zum `<details>`-Handling in `chronik.js`).

**D-046 — Zauberliste: Bestandsränder**
Beim Browser-Check zu D-018 (Sprint 018) gefunden, beide **vor** Sprint 018 vorhanden: (1) Druck: `.spell .nlink` und `.zfw-num` berechnen sich im Print-Block auf `--ink` (rgb 232,220,195) auf Papier rgb(236,228,208) — Kontrast ≈ 1,1:1; `.zd` (rgb 95,107,122) und `.kosten`/`.wirkung` (rgb 154,166,180) ebenfalls zu hell. `tabs.css`-Print-Block überschreibt nur `.spell .merk, .spell .probe`. (2) Bei exakt 1071 px (Desktop-Grid) ragt die letzte Zelle geschlossener Zeilen — und die Artikelvorschau (`grid-column:1/-1`) — 14 px aus der `.spell`-Box (feste Spaltenbreiten 958 px > 934 px Inhaltsbreite), bleibt aber in der Karte; 1072–1130 px nicht durchgemessen. Fix-Skizze: Print-Farben ergänzen; Breakpoint neu messen (Rect-Vergleich, nicht `scrollWidth`) oder Spalten als `minmax`.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
| D-043 | Zauber: ZfW-Sortierung im Kompaktlayout erreichbar — Toolbar-Button (Standard → ZfW ↓ → ↑, Tastatur/ARIA, ≥ 44 px), `static/zauber-sort.js` statt Inline-Skript, Zeilen-Wrapper `[data-spell-list]` (Legende bleibt hinter der Liste) | S | 018 |
| D-018 | Zauber: Artikelvorschau als `<details>` in der Zauberzeile — 25 Artikel zur Render-Zeit eingebettet (`parsers/wikiartikel.py`, mistune `escape=True`, Wikilinks → `obsidian://`), Fallback-Parser für 103/268 Artikel mit ungültigem Frontmatter-YAML; Static-Render 379 → 434 KB | L | 018 |
| D-042 | Chronik-Parser erkennt `Datum: 13. Phex -> Start` als IG-Datum (`13. Phex (Start)`), 5 Tests | S | 017 |
| D-040 | Mobile 400 px: Überlauf in Zauber/Steigern/Inventar/Profil beseitigt — alle 8 Tabs ≤ 400 px, Zauber-Kompaktlayout ≤ 1070 px, Footer-Leiste umbricht | S | 017 |
| D-036 | NSC-/Orts-Register: `parsers/register.py`, 3. Ansicht „Register" im Chronik-Tab (55 Einträge), clientseitige Suche, zur Render-Zeit generiert | M | 017 |
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
