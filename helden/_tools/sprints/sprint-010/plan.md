# Sprint 010 — Steigern-Tab Umbau (Warenkorb-Modus + eigene Tabelle)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-019+D-020 → in-progress, plan.md anlegen) | ⬜ todo | BACKLOG.md, sprints/sprint-010/plan.md |
| T1 | **D-020** — Steigerungsspalte als eigene Tabelle: `.sg-row`-Flex-Zeilen → `<table class="steiger-table">` nach Vorbild `.lang-table`. `renderRow`/`renderSteigernTab` rendern `<tr>` mit Spalten (Name, Wert→nächster, Kosten, Aktion). | ⬜ todo | static/steigern.js, templates/dashboard.html.j2 |
| T2 | **D-019** — Warenkorb-Modus: Auswahl-Toggle pro Zeile statt Sofort-Commit; laufende AP-Summe gegen `window.DSA.steigern.ap.verfuegbar`; Sammel-Commit-Button führt die `doSteigern`-PATCH-Sequenz pro ausgewähltem Item aus, ein Reload am Ende. | ⬜ todo | static/steigern.js, templates/dashboard.html.j2 |
| T3 | **Polish** — `.dp-result.success/fail/crit/patzer`: hartcodierte dunkle Hex-Farben durch auf `#131c28`-Panel (D-012) lesbare Werte ersetzen. | ⬜ todo | templates/dashboard.html.j2 (CSS) |
| T4 | **Polish** — `\| e` Escaping auf `s.name` / `v.name` / `n.name` (Vor-/Nachteile, Schlechte Eig.). | ⬜ todo | templates/dashboard.html.j2 |
| T5 | Verifikation + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **Reihenfolge T1 (D-020) vor T2 (D-019)** — bewusste Abweichung von der Handoff-
  Reihenfolge ("D-020 nach D-019"). Begründung: Beide schreiben `renderRow` neu. Erst
  die Tabellen-Struktur etablieren, dann die Auswahl-/Warenkorb-Spalte additiv
  einhängen. Andersrum würde die Cart-Logik auf Flex-Zeilen gebaut und bei D-020
  nochmal umgezogen — das Doppel-Refactoring, das die Kopplung vermeidet.
- **Commit-Mechanik unverändert (D-019):** Die bestehende 4×-PATCH-Sequenz pro Item
  (`steigern.js:doSteigern` ~52-116: Tabellen-Wert, `ap_verfuegbar`, `ap_eingesetzt`,
  `steigerungs-log.md`-Append) bleibt die atomare Einheit. Der Warenkorb iteriert nur
  sequentiell über die ausgewählten Items und löst **einen** Reload am Ende aus statt
  pro Zeile. Keine neue Server-Route nötig (`PATCH /api/held/<slug>/value` reicht).
- **`window.DSA.steigern.ap.verfuegbar`** ist die maßgebliche AP-Quelle für die
  laufende Summe; der Affordability-Check (heute `renderRow:120`) wird auf die
  **kumulierte** Auswahl-Summe statt pro Einzelzeile umgestellt.
- **`.lang-table` als CSS-Vorlage** (Markup ~1816-1838, CSS ~1074-1084) — neue
  `.steiger-table` übernimmt Header-/Zellen-Stil für Konsistenz mit dem Sprachen-Tab.
- **Subagent-Driven Development** + zwei-stufige Review (spec + code quality) pro
  Feature-Task (T1–T4) gemäß CLAUDE.md.

## Out of Scope

- **D-021** (Session-Erfahrungs-Kostenmodifikator, M) — eigener Session-State
  (localStorage); auf Sprint 011 verschoben, um den Steigern-Umbau fokussiert zu halten.
- **D-018** (Zauber: Inline-Vorschau, L) — unabhängiger Flask-Endpoint-Umbau; Handoff
  hat ihn hinter den Steigern-Block gestellt.
- **`kampagne_slug` hardcoded** (`server.py:27`) und **Guided Stufen-Aufstieg** —
  bleiben offen wie im Sprint-009-Handoff vermerkt.
