# Sprint 012 Handoff — Anzeige-Verbesserungen aus Spielsession (Zauber/Talent + Profil)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-024 + D-023 + D-022 → in-progress, plan.md angelegt)
- ✅ T1: **D-024** Stabzauber-Aktivierungsregel als Hinweiszeile — neuer modul-level Parser-Helper `extract_section_intro(sec_content)` in `held.py` (sammelt Nicht-Tabellen-Zeilen vor der ersten Tabellenzeile, strippt Wikilinks, dokumentiert die break-on-table-Invariante); `load_held` legt die Regel als `held.rituale.stabzauber_regel` ab. Template rendert sie als kursive `.meta`-Hinweiszeile zwischen Card-Header und `sf-list`, guarded + `| e`-escaped. Single-source aus `rituale.md` (nicht hardcoded). 3 Parser-Tests rufen die echte Funktion.
- ✅ T2: **D-023** Eigenschaftswerte inline bei Talent-/Zauber-Proben — neues Jinja-Macro `probe_eig(probe, eig)` rendert Probe-Kürzel mit aktuellen Eigenschaftswerten (`MU 14 / GE 13 / KK 12`); angewandt auf Talent-Zeilen (non-kampf) und Zauber-Zeilen, Kampftechniken (AT/PA) ausgenommen. `**`-Wildcards + unbekannte Kürzel degradieren graceful; else-Zweig `| e`-escaped. CSS: neues Token `--ink-probe` (#b8c4d0) für `.t-probe`/`.spell .probe` + `font-weight:600` (Prominenz). **Follow-up:** Probe-Spalte der Zauberliste auf 150px verbreitert + `white-space:nowrap` (die längeren Werte, headless gemessen 136px, brachen vorher die fixe 90px-Spalte 2-zeilig um).
- ✅ T3: **D-022** Profil-Sektion „Aussehen & Kleidung" — neue strukturierte `## Aussehen`-Sektion in `_illaen.md` (6 Zeilen: Haarfarbe, Augen, Größe, Statur, Besondere Merkmale, Typische Kleidung; aus den verstreuten Quellen kuratiert, undokumentierte Felder explizit „nicht festgelegt" — keine Fakten erfunden). Modul-level Parser-Helper `parse_aussehen(section_text)` → `held.aussehen`; neue Profil-Card (oben im Profil-Tab) mit `<dl>`/`dt`/`dd`-Layout, vollständig tokenisiertes CSS, `| e`-escaped. 4 Parser-Tests inkl. Merkmal-Guard-Coverage.
- ✅ T4: Verifikation (93/93 Tests, Static-Render exit 0, `node --check` für dice.js+steigern.js) + zweistufige Review (Spec ✅ + Code-Quality) pro Feature-Task + finale Gesamt-Review „Ready to merge".

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia (Stepper einreihig), Wunden, Zustände, Eigenschaften, AT/PA (Kampftechnik-Proben weiterhin bare AT/PA, von D-023 ausgenommen), Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
  - **Probe-Zellen zeigen jetzt Eigenschaftswerte inline** (`MU 12 / GE 13 / KK 11`, D-023)
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher-Slots
  - **Probe-Spalte zeigt Eigenschaftswerte inline, einzeilig** (150px-Spalte, D-023 + Follow-up)
  - **Stabzauber-Abschnitt: allgemeine Aktivierungsregel als Hinweiszeile** (D-024)
- ⭐ Steigern-Tab: Warenkorb (sektionsübergreifend, Gesamtkosten gegen AP, Sammel-Commit, D-019), Steiger-Tabellen pro Sektion (D-020), Erfahrungs-Modifikator als SKT-Spaltenverschiebung (D-021), Komplexitätsgrenze-Warnung, Stufen-Aufstieg-Button
- 🗣️ Sprachen-Tab: Sprachen + Schriften mit Komplexität/TaW, rechtsbündig (D-017)
- 🎒 Inventar-Tab: Münzbeutel, Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung; Anmerkungen vollständig (D-015)
- 📋 Profil-Tab:
  - **Neue Card „Aussehen & Kleidung" oben** (Haarfarbe/Augen/Größe/Statur/Merkmale/Kleidung, D-022)
  - Vor/Nachteile, Schlechte Eigenschaften (Konsequenz vollständig, D-016), Kampagne, Steigerungs-Log, Vorgeschichte; Namen HTML-escaped
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/`; `## Verlauf` editierbar + Persistenz
- ⬆️ Stufen-Aufstieg: GM-Grant-Button im Steigern-Tab
- 💾 Commit-Button: Commit-Feld + 💾 im Footer (D-014)
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 93/93 Testfälle bestanden (Baseline 86 → +7 echte Parser-Tests: 3× `extract_section_intro`, 4× `parse_aussehen` inkl. Merkmal-Guard; alle rufen Produktionscode, keine Logik-Mirrors)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **`node --check`:** `static/dice.js` + `static/steigern.js` ok
- **Layout:** Probe-Spalte Zauberliste headless gemessen (136px Inhalt < 150px Spalte) → garantiert einzeilig
- **Review:** Spec ✅ + Code-Quality („Approved with minor issues" → Important-Findungen gefixt) pro Task; finale Gesamt-Review „Ready to merge" — Escaping durchgängig, keine Regressionen, Scope sauber (5 Produktionsdateien, einzige Held-Datei-Änderung = autorisierte Aussehen-Sektion)

## Als nächstes (Sprint 013)

- **D-018** (Zauber: Inline-Vorschau des Artikels, L) — der letzte offene Backlog-EPIC; eigenständiger Backend-Umbau: neuer Flask-Read-Endpoint liest Zauber-`.md` + rendert HTML, Inline-Panel/Modal im Zauber-Tab (`dashboard.html.j2` Zauberliste-Region), Klick-Guard in `static/dice.js:520-532` beachten (`if (e.target.closest('details') || e.target.closest('a')) return;`). `↗`-Obsidian-Link bleibt.
- (Reihenfolge = Empfehlung, nicht Pflicht)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **D-022: Größe / Statur / exakte Augenfarbe nicht festgelegt** — diese Felder sind in den Held-Daten nirgends dokumentiert und wurden bewusst NICHT erfunden, sondern als „— (nicht festgelegt)" belassen. User kann sie jederzeit in `_illaen.md` (`## Aussehen`) nachtragen — der Parser/Render zieht sie automatisch.
- **D-023: Eigenschaftswerte nur bei 3-teiligen `/`-Proben** — Macro `probe_eig` rendert Werte nur für `ABBR/ABBR/ABBR`-Proben; `**`-Wildcards bleiben `**`, unbekannte Kürzel fallen auf bare Kürzel zurück. Spontane-Modifikationen-Tabelle (`mod-probe`) bewusst nicht angefasst (andere Struktur).
- **D-023: Probe-Spaltenbreite fix 150px** — gewählt statt `max-content`, weil jede `.spell`-Zeile ein eigener Grid-Container ist (max-content würde pro Zeile unterschiedlich rechnen → Spalten unausgerichtet). Bei künftig deutlich längeren Probe-Strings (theoretisch) müsste die 150px angepasst werden.
- **D-023-Layout-Follow-up ohne eigene Subagent-Review** — die 2-Zeilen-CSS-Anpassung (Spaltenbreite + nowrap) entstand nach der finalen Gesamt-Review auf User-Wunsch; vom User visuell bestätigt, aber nicht durch die zweistufige Review gelaufen.
- **Steigerungs-Log vermerkt Erfahrungs-Modifikator nicht** (Sprint-011-Restposten, S-Kandidat: `item.erfShift` → `aktion`-String) und **`.sg-erf` `display:block`-Polish** bleiben offen.
- **Vereinfachtes lineares SKT-Modell**, **kein Vorrat/Zähler für Erfahrungen**, **`kampagne_slug` hardcoded** (`server.py:27`), **Guided Stufen-Aufstieg**, **kein Rollback bei Teil-Commit** — bleiben offen wie zuvor.
