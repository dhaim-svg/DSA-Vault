# Sprint 014 — Chronik-Fundament: Vault-Migration + Parser

## Ausgangslage

Sprint-013-Handoff empfiehlt den Chronik-Modus als „Als nächstes"; Nutzer hat
explizit grünes Licht für die restlichen Tasks aus dem Gesamtplan gegeben.
Voller Umfang laut Plan (`C:\Users\David\.claude\plans\ich-habe-jetzt-die-mellow-beaver.md`,
Abschnitt „Sprint 014 — Chronik-Modus"): D-030…D-035, sechs EPICs (1×S + 5×M) —
deutlich über dem Richtwert „1–2 M-EPICs pro Sprint".

**Scope-Abweichung von der ursprünglichen Grobplanung, zur Freigabe:**
Dieser Plan schlägt vor, Sprint 014 auf **D-030 + D-031** zu beschränken
(Fundament: Chronik in den Vault holen + Parser), aus drei Gründen:
1. D-030 hat ein im Plan selbst benanntes, ungeklärtes Risiko (Google-Drive-
   Junction könnte vom Sync übersprungen werden) — muss vor allem Weiteren
   verifiziert sein, sonst bauen D-032/033/034 auf einem Dateipfad, der sich
   noch ändern könnte.
2. D-032 (Chronik-Tab), D-033 (Quick-Capture) und D-034 (Auto-Log) sind alle
   UI-/Schreibpfad-Arbeit auf derselben Datei — passen eher als eigener,
   dichter Sprint 015 zusammen, wenn das Fundament steht.
3. D-035 verlangt laut Plan explizit die Freigabe des Nutzers fürs Aufräumen
   von `abenteuer/`-Dateien — kein Task, den man einfach mitlaufen lässt.

D-030…D-037 werden in diesem Sprint vollständig ins Backlog aufgenommen
(mit Beschreibungen aus dem Plan-File), damit `BACKLOG.md` autoritativ bleibt —
nur D-030/D-031 wandern nach „In Progress".

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-030…D-037 anlegen, D-030+D-031 → in-progress, plan.md) | ⬜ todo | BACKLOG.md, sprints/sprint-014/plan.md |
| T1 | **D-030** Chronik in den Vault holen (Junction-Risiko zuerst verifizieren, dann verschieben) | ⬜ todo | abenteuer/drachenchronik/chronik.md (neu), abenteuer/drachenchronik/drachenchronik-daten/ |
| T2 | **D-031** `parsers/chronik.py` (Spielabend/IG-Tag/Szenen-Marker-Parser) | ⬜ todo | parsers/chronik.py, tests/test_chronik.py |
| T3 | Verifikation + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **D-030 läuft NICHT als Subagent-Feature-Task** — Verzeichnis-Junctions,
  Dateiverschiebung außerhalb des Repos (`C:\Users\David\Google Drive\...`)
  und die Sync-Verifikation sind Dateisystem-Operationen mit echtem
  Störungsrisiko für den Nutzer (Google Drive), keine reine Code-Änderung.
  Läuft direkt in der Hauptsession, mit Rückfrage vor dem eigentlichen
  Verschieben der Live-Datei — analog zu W-001 in Sprint 013 (Wiki-Fix
  auch kein Dashboard-Subagent-Task).
- **Verifikationsreihenfolge bei D-030**: (1) Junction anlegen, (2) Testdatei
  hineinschreiben, (3) User bittet, in der Google-Drive-Weboberfläche
  nachzusehen, ob sie synct — **erst danach** die eigentliche
  `Drachenchronik.md` verschieben. Bei Fehlschlag: Fallback-Optionen aus dem
  Plan (robocopy-Mirror, Git-Zugriff) vorschlagen, nicht selbst entscheiden
  welche — das ist Nutzer-Workflow, nicht Code.
- **D-031 braucht KEINE echte Nutzerdaten-Fixture im Repo** — die reale
  Chronik enthält private Kampagnendetails; Testfixture ist ein synthetischer,
  aber strukturell identischer Auszug (Datumsformate, IG-Tage, Szenen-Marker,
  Bild-Tag), analog zu `tests/test_kampagne.py`. `parsers/chronik.py` selbst
  liest zur Laufzeit die echte Datei aus `abenteuer/drachenchronik/`, sobald
  D-030 sie dorthin verschoben hat — falls D-030 in diesem Sprint nicht zum
  Verschieben kommt (Junction-Risiko schlägt fehl), parst D-031 testweise
  gegen eine Kopie/den synthetischen Fixture-Pfad, und der Anschluss ans
  Dashboard (D-032) verschiebt sich in Sprint 015.
- **`parsers/chronik.py` parst nur — kein Rendering, kein Dashboard-Tab.**
  D-032 (Chronik-Tab) ist expliziter Sprint-015-Kandidat und hängt von einem
  stabilen `chronik.md`-Pfad ab.

## Out of Scope

- **D-032** (Chronik-Tab), **D-033** (Quick-Capture), **D-034** (Ereignis-
  Auto-Log), **D-035** (`/session-compile` + Aufräumen) — Sprint-015-
  Kandidaten, ins Backlog aufgenommen aber nicht gestartet. D-032/033/034
  brauchen D-030 (stabiler Dateipfad) + D-031 (Parser) als Voraussetzung.
- **D-036** (NSC-/Orts-Register), **D-037** (Template-Zerlegung) — laut
  Gesamtplan „Danach", nicht Teil des Chronik-Fundaments.
- **D-018** (Zauber-Inline-Vorschau) — weiterhin im Backlog, unverändert.
