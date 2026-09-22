# Sprint 031 Handoff — Pfad-Leak im `api_held`-Fehlerhandler schließen (D-063)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `704d3cc` (D-063 → in-progress, plan.md).
- ✅ **T1** (`api_held`-Fehlerhandler: `FileNotFoundError` → 404, Muster
  `api_etag`) — `995c0d1`, Task-Review (Sonnet) fand 1 Minor (toter
  `mkdir()`-Testsetup), kein Fix-Loop nötig (Minor, direkt geparkt).
- ✅ **Gesamt-Review** (Opus) — „Ready to merge, Yes"; reproduzierte Leak +
  Fix unabhängig durch eine Scratch-Kopie beider Commits (`git archive`,
  kein Worktree/HEAD-Wechsel), fand 1 Important außerhalb des D-063-Scopes
  (neu gefiled als D-064) + 3 Minor (2 per Controller-Polish behoben, 1
  dokumentiert).
- ✅ **T2** Verifikation — `verification.md`, `d73bb5f` (D-064-Filing);
  Polish-Commit `fee5167` (2 Gesamtreview-Minors); `8e8aa05`
  (plan.md-Checkbox).
- Commits liegen **lokal** auf `master`: 6 neue Commits (704d3cc, 995c0d1,
  8e8aa05, fee5167, d73bb5f, + dieser Wrap-Commit), **weiterhin nichts
  gepusht seit Sprint 022**.

## Was funktioniert

- **`api_held` leakt keine Dateisystempfade mehr in der Fehler-JSON.** Bare
  `except Exception: str(exc)` ersetzt durch `except FileNotFoundError`
  (404, `'not found'`) — identisch zu `api_etag`s bestehendem Muster im
  selben File. Jede andere Exception fällt jetzt auf Flasks eigenen,
  sicheren 500-Handler durch (`debug=False` → kein Traceback, kein Pfad).
- **Sprint-030s D-062 (`slug_param`-Traversal) + Sprint-031s D-063
  (Fehler-JSON-Leak) schließen zusammen den kompletten bisher bekannten
  Informations-Leak in `api_held`** — sowohl der Eingabepfad (Traversal)
  als auch der Fehlerausgabepfad (Exception-Message) sind jetzt gehärtet.
- **Tests belegen die Diskriminierung empirisch, nicht nur behauptet:**
  die Gesamtreview lief den neuen Testfile selbst gegen den ungefixten
  Stand — Testfälle (a) und (c) schlagen dort fehl (= fangen den Bug
  korrekt), (b) besteht beidseitig (echte Erfolgspfad-Regression). Zudem
  eine echte, empirische Leak-Messung: `GET /api/held/does-not-exist`
  gegen `c42d46e` (vor Fix) lieferte den vollen Windows-Pfad im 500-Body,
  gegen `8e8aa05` (nach Fix) ein sauberes 404 ohne Pfad.
- **Tests:** 684 → **687** (+3, alle aus T1; keine weiteren aus den
  Polish-Fixes).
- **Neu entdeckt, nicht mitgefixt:** `api_commit` (`server.py:149`) leakt
  rohen Git-Stderr-Text nach demselben Muster wie D-063 — als **D-064**
  gefiled, direkt startbar.

## Verifikation

- **Test Suite:** 687/687 bestanden (`pytest tests/ -v` und
  `-q -W error` nach `__pycache__`-Löschen), unabhängig vom
  Implementierer-Report zweimal selbst gegengelaufen (T2 + dieser Wrap).
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert
  (exit 0) ✓ — inhaltlich unverändert (`git status --short` zeigt keine
  Diff auf `output/`), da D-063 ausschließlich einen Fehlerpfad in
  `server.py` ändert, kein Rendering-/Template-Code.
- Zahlen und Belege im Detail: `verification.md` im selben Ordner.

## Als nächstes (Sprint 032)

- **D-064**: `api_commit`s Fehlerpfad (`server.py:149`) leakt rohen
  Git-Stderr-Text — direkt startbar, kein Blocker, Effort S. Gleiche
  Fehlerklasse wie D-063, von der Sprint-031-Gesamtreview beim
  empirischen Fix-Vergleich gefunden (isoliertes Wegwerf-Repo, gemessen).
- Vault-`backlog.md` bleibt leer — kein B-Task in Sprint 031.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **1 Minor aus der Gesamtreview bewusst nicht gefixt** (kein Code-Fix
  nötig, nur dokumentiert): `FileNotFoundError` wird nach dem Fix ohne
  Server-Log verschluckt — konsistent mit der bewussten
  „Kein Logging-Ausbau"-Entscheidung im Sprint-031-Plan (kein bestehendes
  Logging-Setup im Projekt).
- **Aus Sprint 020–030 unverändert offen** (keine dieser Punkte in
  Sprint 031 berührt): echter Druckdialog (Papier-Ausdruck) ungeprüft;
  D-058-Zeilenhöhen-Zuwachs → echter Seitenumbruch-Effekt ungeprüft; Messung
  nur an einem Charakter (illaen-baernhold); Register hängt am
  Session-Format; echter Browser-Klick gegen eine echte Session-Datei nie
  ausgelöst; inhaltliche Sichtung der vier Sessions; Kommando-Mängel von
  `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://`
  Fake-Erfolg; Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch;
  SF-Vorschau-Randfälle; Zustands-Chips = Hausregel; `api_patch_kampagne`s
  Inline-Campaign-Regex-DRY-Nit (Sprint 030, „defensible as-is").

## Lehren (Process)

- **Eine Gesamtreview kann den nächsten Fund derselben Fehlerklasse an
  einem völlig anderen Endpunkt liefern.** D-062 → D-063 → D-064 ist jetzt
  die dritte Iteration desselben Musters (Path-Traversal → Fehler-JSON-Leak
  in `api_held` → Fehler-JSON-Leak in `api_commit`). Jedes Mal war der Fund
  vorbestehend, nicht durch den jeweils aktuellen Fix eingeführt, und jedes
  Mal war „ganze Fehlerklasse an diesem Endpunkt fixen, verwandte Endpunkte
  als Folge-Ticket filen" die richtige Scope-Grenze — ein einzelner Sprint
  sollte trotzdem nicht versuchen, die ganze Klasse projektweit auf einmal
  zu jagen, ohne dass eine Review sie konkret benennt.
- **Empirische Verifikation eines Fehlerhandler-Fixes braucht Produktions-
  Semantik, nicht nur den Testclient.** Die Gesamtreview nutzte bewusst
  `app.testing=False`/`debug=False` (statt der `TESTING=True`-Konfiguration
  der Unit-Tests) für ihre Scratch-Kopie-Messung — nur so bestätigt sich,
  dass „nicht abgefangene Exceptions fallen auf Flasks sicheren
  500-Handler durch" auch real beim Endnutzer gilt, nicht nur im
  Testclient-Kontext, der abweichendes Exception-Propagation-Verhalten hat.
- **Ein Assert kann formal bestehen und trotzdem nicht diskriminieren.**
  Der `str(tmp_path) not in body`-Check in Testfall (a) besteht auf Windows
  auch gegen den ungefixten Leak (der Pfad landet im `str(exc)`-Errno-Text
  doppelt escaped) — nur der zusätzliche Regex-Assert auf Windows-
  Laufwerksbuchstaben fängt den Bug wirklich. Lehre: bei
  Pfad-Leak-Assertions mehrere unabhängige Prüfmethoden kombinieren, nicht
  nur eine String-Containment-Prüfung, deren Serialisierungsform man nicht
  kontrolliert.

## Process-Notizen

- Briefs/Ledger/Reports liegen unter `.superpowers/sdd/sprint-031/`
  (gitignored, sprint-qualifiziert wie seit Sprint 022, manuell nach
  Abschluss umbenannt aus `.superpowers/sdd/plan/` — `plan.md`-Basename-
  Kollision erneut manuell umgangen, wie in jedem Sprint seit 022).
  Workspace bewusst behalten, nicht gelöscht.
- `task-brief`-Skript passt nicht zu diesem Projekts `plan.md`-Format
  (Tabellenzeilen `| T1 | ... |` statt `## Task N`-Überschriften) — Brief
  erneut von Hand geschrieben (Konvention seit Sprint 025).
- Dieser Sprint nutzte `/sprint-plan` im Plan-Mode (11. Vorkommen dieser
  Kombination) — Recherche (Explore-Agent-Dispatch übersprungen,
  Quelldateien direkt gelesen: `server.py`, `held.py`, `kampagne.py`)
  bestätigte den exakten Fix-Ansatz vor `ExitPlanMode`, keine Überraschung
  während der Umsetzung.
- Implementierer: Sonnet für T1 (kleiner, gut gescopter Security-Fix, 1
  Route + 3 Tests). Reviews: Sonnet für den Task-Review, Opus für die
  Gesamtreview.
- 2 triviale Gesamtreview-Minors direkt vom Controller gefixt (Kommentar +
  toter Testcode, < 10 Zeilen gesamt) statt per Implementierer-Dispatch —
  Projekt-Konvention für triviale Review-Funde, re-verifiziert (687/687)
  vor Commit.
- Kein Worktree, Commits direkt auf `master` per CLAUDE.md-Workflow, kein
  Push. `superpowers:finishing-a-development-branch` erneut nicht genutzt
  (kein Branch/PR in diesem Projekt) — `/sprint-wrap` ist der tatsächliche
  Abschluss-Schritt.
- Sprint-Umfang bewusst auf 1 EPIC beschränkt (D-063 war der einzige
  startbare Backlog-Eintrag nach Sprint 030) — kein Auffüll-Task nötig.

**Nächster Schritt:** `/sprint-plan` ausführen, um Sprint 032 einzuleiten
(primärer Kandidat: D-064).
