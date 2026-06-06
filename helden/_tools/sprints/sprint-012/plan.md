# Sprint 012 — Anzeige-Verbesserungen aus Spielsession (Zauber/Talent + Profil)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-024 + D-023 + D-022 → in-progress, plan.md anlegen) | ⬜ todo | BACKLOG.md, sprints/sprint-012/plan.md |
| T1 | **D-024** (S) — Stabzauber: allgemeine Aktivierungsregel als Hinweiszeile im Abschnitt | ⬜ todo | parsers/held.py (rituale.md-Parse, ~351-362), templates/dashboard.html.j2 (~1428) |
| T2 | **D-023** (M) — Talente/Zauber: Eigenschaftswerte inline neben Probe-Kürzel + prominentere Probe | ⬜ todo | templates/dashboard.html.j2 (talent-row ~1327-1334, spell ~1359-1380), static/dice.js (parseProbe/eig), CSS |
| T3 | **D-022** (M) — Profil: strukturierte Sektion „Aussehen & Kleidung" (Schema + Parser + Karte) | ⬜ todo | helden-Datei (neue `## Aussehen`-Sektion), parsers/held.py, templates/dashboard.html.j2 (Profil ~1645-1757) |
| T4 | Verifikation (Tests + Static-Render + node --check) + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **Priorität = Backlog-Reihenfolge.** Das Sprint-011-Handoff empfahl D-018, aber die Spielsession 06.06.2026 hat D-024/D-023/D-022 **darüber** einsortiert (BACKLOG.md autoritativ). D-018 (L, Inline-Vorschau) bleibt damit der letzte offene EPIC → eigener Sprint.
- **D-024 — Datenquelle:** Aktivierungsregel als Intro-Text aus `rituale.md` (~Z.16, „Alle Stabzauber an Illaens gebundenen Magierstab … freie Aktion") parsen und als `held.rituale.stabzauber_regel` o.ä. ins Dict legen — **nicht** im Template hardcoden, damit die Regel single-source in der Held-Datei bleibt. Render als Hinweiszeile unter dem Header (`dashboard.html.j2:1428`). Keine Probe pro Einzelzauber.
- **D-023 — server- vs. client-seitig:** Eigenschaftswerte sind im Template über `held.eigenschaften` server-seitig verfügbar → bevorzugt **server-seitig** inline rendern (kein JS-Reflow beim Laden, kein FOUC). Probe-Kürzel + konkrete Werte z.B. als `MU 14 / GE 13 / KK 12`. Kampftechniken (AT/PA, `is_kampf`) **ausgenommen** — die haben keine `/`-Probe. CSS für Lesbarkeit/Prominenz der `.t-probe` / `.probe`.
- **D-022 — User-Domäne (autorisiert):** Diese EPIC verlangt **neue Daten in einer Held-Datei** (`## Aussehen`: Haar-/Augenfarbe, Größe, Statur, Merkmale, typische Kleidung). `helden/` ist User-Domäne — der User hat den Schreibzugriff für diesen Sprint **explizit freigegeben** (2026-06-06). Heute liegen die Daten verstreut (Haar/Augen `vorgeschichte.md`, silberne Strähne `vor-nachteile.md`, Kleidung `ausruestung.md`); diese werden in die neue Sektion konsolidiert (single-source), die verstreuten Quellen bleiben unverändert. Die Held-Datei-Änderung wird dem User zum Review vorgelegt.
- **Subagent-Driven Development** + zweistufige Review (Spec + Code-Quality) pro Feature-Task; triviale Quality-Fixes inline durch den Controller.

## Out of Scope

- **D-018** (Zauber: Inline-Vorschau, L) — eigenständiger Backend-Umbau (neuer Flask-Read-Endpoint + Modal). Zu groß, um mit drei Anzeige-Tasks zu bündeln; nächster Sprint.
- **Steigerungs-Log-Modifikator-Vermerk** (`item.erfShift` → Log) und **`.sg-erf` `inline-block`-Polish** — Sprint-011-Restposten, S/Polish-Kandidaten, hier nicht eingeplant.
- **Authentisches SKT-Modell**, **Eigenschaften-Spaltenverschiebung**, **`kampagne_slug`-Hardcoding** — unverändert offen.
