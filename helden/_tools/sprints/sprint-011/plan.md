# Sprint 011 — Steigern: Session-Erfahrungs-Kostenmodifikator (D-021) + Status-Farb-Polish

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-021 → in-progress, plan.md anlegen) | ⬜ todo | BACKLOG.md, sprints/sprint-011/plan.md |
| T1 | **D-021** Session-Erfahrungs-Modifikator (SKT-Spaltenverschiebung) — pro Warenkorb-Zeile Toggle „Erfahrung: — / gut (−1 Spalte) / schlecht (+1 Spalte)"; gilt nur für Talente+KT & Zauber (nicht Eigenschaften); verschiebt Spalte in `calcApCost` über `shiftSktColumn`, geklammert A…H; modifizierte Kosten fließen in `renderRow`-`item.cost` → Warenkorb-Summe automatisch; freie Anwendung (kein Vorrat/Zähler); Auswahl transient (Cart-State, beim Commit verbraucht) | ⬜ todo | static/steigern.js, dashboard.html.j2 |
| T2 | **Polish** `.dp-result.fail`-Kontrast: neues helleres Fail-Status-Rot-Token statt `--accent-blood` (WCAG-grenzwertig ~2,7:1); stale Fallback `#8b1c2a` in `.dp-die-fehl` entfernen | ⬜ todo | dashboard.html.j2 (CSS-Tokens) |
| T3 | Verifikation (Test-Suite, Static-Render, `node --check`, Strukturchecks) + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **Mechanik = SKT-Spaltenverschiebung, kein flacher AP-Delta** (WdS *Wege des Schwertes*, Kap. 6, S. 167, Z. 163–172): Gute/Spezielle Erfahrung verschiebt die Steigerungsspalte um **1 nach links** (billiger), schlechte um **1 nach rechts** (teurer). Verrechnung am Ende, Klammerung A*…H.
- **Nur Talente+KT & Zauber, nicht Eigenschaften:** WdS S. 167 — „Eigenschaften werden immer nach Spalte H gesteigert; Veränderungen der Spalte … sind nicht möglich." → kein Toggle in der Eigenschaften-Sektion.
- **Implementierung im bestehenden (vereinfachten) Kostenmodell:** `SKT_COSTS` ist ein lineares Modell (Faktor = Spalten-Ordnungszahl A=1…H=8, **ohne A* und ohne die echten Faktoren 8/10/20**). Neuer Helper `shiftSktColumn(skt, shift)`: Spaltenbuchstabe → Index, ±shift, **links auf A geklammert** (≈ WdS „nicht billiger als A*"), rechts auf H. `calcApCost(skt, taw, shift=0)` ruft intern `shiftSktColumn` vor dem Bracket-Lookup auf — Ziel-TaW-Bracket-Logik bleibt unangetastet.
- **A*-Lücke = bewusste Vereinfachung:** Das echte A* (links von A) wird nicht nachgezogen; linker Klammerwert ist A. Als bekannte Einschränkung dokumentieren (authentische SKT mit echten Faktoren wäre separater Backlog-Punkt).
- **State pro Zeile, transient im Cart:** Erfahrungs-Auswahl (`— / gut / schlecht`) hängt an der jeweiligen ausgewählten Warenkorb-Zeile (bestehendes Cart-Auswahlmodell aus D-019), nicht persistent nach Markdown. Beim Sammel-Commit verbraucht; ein Reload setzt zurück. Kein Vorrat/Zähler — **freie Anwendung (Vertrauensmodell)** nach SL-Ansage.
- **Warenkorb-Konsistenz:** Modifizierte Kosten fließen über `renderRow`-`item.cost` in die kumulierte Cart-Summe + Affordability-Guard (D-019) — eine einzige Berechnungsquelle, Guard-Logik unverändert.
- **T2-Token statt One-off-Hex:** Neues semantisches Token (z.B. `--accent-fail-bright`) im `:root`, kein Inline-Hex — Konsistenz mit der T3-Token-Refaktorierung aus Sprint 010.

## Out of Scope

- **D-018** (Zauber: Inline-Vorschau, L) — eigenständiger Umbau (neuer Flask-Read-Endpoint + Inline-Panel), unabhängig vom Steigern-Code. Bewusst auf Sprint 012 verschoben, um den Sprint fokussiert (1× M-Feature + Polish) zu halten.
- **Authentische SKT** (echte Faktoren 8/10/20 + A*-Spalte) — das Dashboard nutzt weiter das lineare Näherungsmodell; eigener Backlog-Kandidat.
- **Vorrat/Zähler & GM-Grant** für Erfahrungen, sowie **Eigenschaften-Spaltenverschiebung** — bewusst weggelassen.
- **Cost-Cell `affordable`/`expensive` pro-Zeile-vs-Warenkorb** (Sprint-010-Einschränkung) — kosmetisch, separat; nur anfassen falls die D-021-Cost-Änderung es ohnehin berührt.
