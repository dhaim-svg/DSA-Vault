# Dashboard Backlog — Illaen Dashboard

> EPIC-Tracker für Dashboard-Entwicklung. D-NNN-IDs.
> Format: state = ready | in-progress | done | blocked

## In Progress

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-025 | Eigenschafts-Leiste über Talente-/Zauber-Tab | M | in-progress | Spielsession-Feedback 16.09.2026 |
| D-026 | Inline-Eigenschaftswerte vervollständigen (Kampftechniken, Spontane Mods, Wundabzug) | M | in-progress | Spielsession-Feedback 16.09.2026 |
| D-027 | Zauberspeicher-Auslöseprobe (MU/IN/KL) | M | in-progress | Spielsession-Feedback 16.09.2026 |
| D-028 | Erschaffungsprobe je Stabzauber | S | in-progress | Spielsession-Feedback 16.09.2026 |
| D-029 | Aussehen vervollständigen (Augenfarbe/Größe/Statur/Gewicht) | S | in-progress | Spielsession-Feedback 16.09.2026 |

## Backlog

| EPIC | Title | Effort | State | Quelle |
|------|-------|--------|-------|--------|
| D-018 | Zauber: Inline-Vorschau des Artikels (Obsidian-Link bleibt) | L | ready | Manual-Test 01.06.2026 |

### Beschreibungen

**D-018 — Zauber: Inline-Vorschau**
Klick auf Link öffnet Obsidian (gut). Gewünscht: kleine Ansicht im Dashboard, die den Artikel direkt anzeigt; `↗`-Obsidian-Link bleibt. Heute: nur `obsidian://`-URI via `rendering.py:obsidian_uri()`; kein Read-Endpoint. Umfang: neuer Flask-Endpoint liest Zauber-`.md` + rendert HTML; Inline-Panel/Modal im Zauber-Tab (`dashboard.html.j2:1311-1506`); Klick-Guard in `static/dice.js:520-532` beachten. Seit Sprint 012 günstiger: `popover` + CSS Anchor Positioning sind seit Firefox 147 (Jan. 2026) Baseline — spart die JS-Positionierung; `@position-try` (Flip bei Overflow) braucht noch einen sinnvollen Fallback (Safari 18.4+).

**D-025 — Eigenschafts-Leiste über Talente-/Zauber-Tab**
Die Eigenschaften-Karte liegt nur im Kampf-Tab; beim Talent-/Zauberwürfeln sind die Werte nicht sichtbar. Gewünscht: sticky Leiste am oberen Rand von `#tab-talente` und `#tab-zauber` mit allen acht Eigenschaften (`aktuell`-Wert) plus LE/AE/MR, aus `held.eigenschaften`/`held.basiswerte` (`parsers/held.py:194-210`, kein Parser-Eingriff nötig). Neues Jinja-Macro `eig_leiste(eig, basis)` neben `probe_eig` (`dashboard.html.j2:1116`). Aktive Zustands-/Wundmodifikatoren als Badge rechts, gespeist aus `session.js`/`dice.js:185 getWundMod()`. Quelle: Spielsession-Feedback 16.09.2026, Plan `C:\Users\David\.claude\plans\ich-habe-jetzt-die-mellow-beaver.md`.

**D-026 — Inline-Eigenschaftswerte vervollständigen**
`probe_eig` (D-023, Sprint 012) greift nur bei 3-teiligen `/`-Proben. Gewünscht: Kampftechniken (`dashboard.html.j2:1354`, AT/PA-Werte statt bare Kürzel), Spontane-Modifikationen-Tabelle (`.mod-probe` `:1440`) und sichtbarer Wunden-/Zustandsabzug (z.B. `GE 13 → 11`) bei aktivem Malus. Probe-Spalte fix `150px` (`:346`) muss auf `minmax()` umgestellt werden. Selber JS-Hook wie D-025.

**D-027 — Zauberspeicher-Auslöseprobe**
Quelle: `wiki/dsa-4.1/rituale/stabzauber.md:119-125` — Aktivierungsdauer 1 Aktion, Probe MU/IN/KL, kostet keine AsP, Misslingen = Zauber verpufft, Patzer = alle gespeicherten Zauber lösen aus, +1 Erschwernis je weiterem belegten Slot. Heute nirgends im Dashboard, obwohl es die einzige real definierte Aktivierungsprobe im Regelwerk ist. Umfang: Regelzeile in der Speicher-Box (`dashboard.html.j2:1462-1473`), „Auslösen"-Button pro belegtem Slot mit `data-probe="MU/IN/KL"` + errechneter Erschwernis, Anbindung an bestehenden Würfler (`dice.js:507/520`, Selektor erweitern statt duplizieren), Erfolg/Patzer-Handling über bestehenden `zauberspeicher.js`-Entleeren-Pfad.

**D-028 — Erschaffungsprobe je Stabzauber**
`helden/illaen-baernhold/rituale.md` hat nur `| Stabzauber | Vol | Effekt |`; `wiki/dsa-4.1/rituale/stabzauber.md` führt zusätzlich Erschaffungsprobe + AsP. Spalte ergänzen (Werte aus dem Wiki, nach W-001-Klärung), `parsers/held.py:382-395` liest mit, Template `:1456` zeigt sie neben dem Vol-Badge. Reine Nachschlage-Info — ändert nichts an der (probenfreien) Aktivierung selbst.

**D-029 — Aussehen vervollständigen**
`_illaen.md:30-39` hat Größe/Statur/exakte Augenfarbe als „— (nicht festgelegt)" (Sprint-012-Präzedenzfall: keine erfundenen Werte). Gewünscht: Felder ergänzen sobald der User sie festlegt, plus Template-Anpassung (`:1677`) sodass offene Felder visuell als *offen* markiert statt wie ausgefüllter Inhalt gerendert werden. Optional Portrait-Slot.

## Done

| EPIC | Title | Effort | Sprint |
|------|-------|--------|--------|
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
