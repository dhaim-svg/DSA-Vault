# Sprint 033 Handoff — CSRF-Schutz + Logging verschluckter Fehler (D-065, D-066)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `4bdb25f` (D-065/D-066 → in-progress, plan.md).
- ✅ **T1** (D-065: JSON-Pflicht auf `/api/commit` + app-weiter
  `before_request`-Origin-Check) — `3c8bb89`, Task-Review (Sonnet): Spec ✅,
  0 Findings, Approved — kein Fix-Loop.
- ✅ **T2** (D-066: Logging der 4 verschluckten Fehlerstellen) — `b46ac14`,
  Task-Review (Sonnet): Spec ✅, 0 Findings, Approved — kein Fix-Loop.
- ✅ **Gesamt-Review** (Opus) — „Ready to merge, Yes"; reproduzierte den
  CSRF-Exploit empirisch gegen echte Flask-Server in einer Scratch-Kopie
  (nie den Projekt-Tree berührt), 3 neue Minor (kein Blocker, keine
  Fix-Runde nötig), fand DNS-Rebinding als vorbestehende, bewusst
  ausgeklammerte Lücke → **D-067** neu gefiled.
- ✅ **T3** Verifikation — `verification.md`, BACKLOG.md (D-065/D-066 →
  Done, D-067 neu → ready), CLAUDE.md-Sprint-Nr. → 33.
- Commits liegen **lokal** auf `master`: 3 neue Commits (`4bdb25f`,
  `3c8bb89`, `b46ac14`) + dieser Wrap-Commit, **weiterhin nichts gepusht
  seit Sprint 022**.

## Was funktioniert

- **`POST /api/commit` verlangt `application/json` (415 sonst).**
- **App-weiter `before_request`-Hook lehnt jede schreibende Methode
  (alles außer GET/HEAD/OPTIONS) mit einem gesetzten, fremden `Origin`
  ab (403) — fehlender Origin-Header wird durchgelassen** (Tests/CLI).
  Schützt `/api/commit`, `/api/held/<slug>/value` und
  `/api/kampagne/<camp>/value` gleichermaßen, weil der Hook nicht
  routen-gescoped ist.
- **4 vorher verschluckte Fehlerstellen loggen jetzt den vollen Grund
  ins Server-Log (stderr, `app.logger`), ohne die JSON-Antwort zu
  ändern:** `api_held`/`api_etag`s `FileNotFoundError`, `api_commit`s
  Git-Stderr, der CSRF-Hooks 403/415-Ablehnungen.
- **D-062 → D-063 → D-064 → jetzt D-065/D-066** — die Pfad-Leak-/
  Verschluckt-Fehler-Fehlerklasse aus Sprint 030–032 ist mit diesem
  Sprint um Logging ergänzt; die Dual-Assertion-Testkonvention
  (`str(tmp_path)`/`tmp_path.name` + Windows-Laufwerksbuchstaben-Regex)
  wurde hier erstmals auch auf Log-Nachrichten statt nur Response-Bodies
  angewendet — trägt jetzt über 4 Sprints.
- **Tests:** 688 → **693** (T1) → **698** (T2).
- **Neu entdeckt, bewusst nicht mitgefixt:** DNS-Rebinding umgeht den
  Origin-Check vollständig (Host und Origin stammen beim Rebinding von
  derselben Angreifer-Hostname) — empirisch von der Gesamtreview bestätigt
  (echter Commit + echtes Datei-Überschreiben, zusätzlich ein Lese-Leak
  über same-origin gewordene GETs nach dem Rebind) — als **D-067**
  gefiled, war bereits in der Sprint-Planung per User-Entscheidung aus
  D-065 ausgeklammert.

## Verifikation

- **Test Suite:** 698/698 bestanden (`pytest tests/ -v` und
  `-q -W error` nach `__pycache__`-Löschen).
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert
  (exit 0) ✓ — inhaltlich unverändert (`git status --short` zeigt keine
  Diff auf `output/`), da dieser Sprint ausschließlich `server.py`/Tests
  ändert, kein Rendering-/Template-Code.
- Zahlen und Belege im Detail: `verification.md` im selben Ordner.

## Als nächstes (Sprint 034)

- **D-067**: DNS-Rebinding-Schutz (Host-Allowlist im selben
  `before_request`-Hook) — direkt startbar, kein Blocker, Effort S.
  Vorbestehend, bewusst aus Sprint 033 ausgeklammert, von der
  Sprint-033-Gesamtreview empirisch als real exploitierbar bestätigt
  (nicht nur theoretisch) — Lese- **und** Schreib-Impact.
- Optionaler Polish-Kandidat (kein eigenes Ticket, klein genug für
  Controller-Inline-Fix bei Gelegenheit): ein Test, der `%r`-Escaping
  eines Origin-Headers mit eingebettetem CR/LF in den D-066-Logzeilen
  pinnt — aktuell ungetestet, aber in der Praxis sicher.
- Vault-`backlog.md` bleibt leer — kein B-Task in Sprint 033.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **DNS-Rebinding** (s. oben) → D-067, kein neuer Punkt hier.
- **Aus Sprint 020–032 unverändert offen** (keine dieser Punkte in
  Sprint 033 berührt): echter Druckdialog (Papier-Ausdruck) ungeprüft;
  D-058-Zeilenhöhen-Zuwachs → echter Seitenumbruch-Effekt ungeprüft; Messung
  nur an einem Charakter (illaen-baernhold); Register hängt am
  Session-Format; echter Browser-Klick gegen eine echte Session-Datei nie
  ausgelöst; inhaltliche Sichtung der vier Sessions; Kommando-Mängel von
  `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://`
  Fake-Erfolg; Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch;
  SF-Vorschau-Randfälle; Zustands-Chips = Hausregel; `api_patch_kampagne`s
  Inline-Campaign-Regex-DRY-Nit (Sprint 030, „defensible as-is").

## Lehren (Process)

- **Die Dual-Assertion-Pfad-Leak-Testkonvention (Substring +
  Laufwerksbuchstaben-Regex) trägt jetzt auch auf Log-Nachrichten,
  nicht nur Response-Bodies.** T2s Implementierer erkannte selbstständig,
  dass `str(tmp_path)` in Log-Nachrichten aus denselben Gründen wie in
  Response-Bodies (Sprint 031/032) nie verbatim erscheint, und wich
  begründet auf `tmp_path.name` aus, statt die Konvention blind zu
  kopieren — vom Task-Review explizit als richtige Anpassung statt
  „neue Idiom-Erfindung" bestätigt.
- **Ein app-weiter `before_request`-Hook deckt künftige schreibende
  Routen automatisch ab, statt die Fehlerklasse endpunktweise nachzuziehen
  (wie D-062→D-063→D-064 es taten).** Die Gesamtreview bestätigte das
  empirisch: `api_patch_kampagne` profitiert vom Hook, ohne selbst
  angefasst worden zu sein.
- **Ein Security-Fix kann eine neue, verwandte Lücke aufdecken, die
  bewusst außerhalb des Sprint-Scopes bleibt, wenn die Sprint-Planung
  das bereits vorwegnimmt.** DNS-Rebinding (D-067) wurde in der
  Sprint-033-Planung als Trade-off explizit per `AskUserQuestion`
  entschieden (Host-Allowlist separates EPIC), nicht erst nachträglich
  entdeckt — die Gesamtreview bestätigte lediglich empirisch, dass die
  bewusste Auslassung eine reale (nicht nur theoretische) Lücke ist.
- **Eine Gesamtreview kann gezielt einzelne Fix-Bestandteile deaktivieren,
  um zu prüfen, ob jeder Teil eigenständig durch mindestens einen Test
  abgedeckt ist** (statt nur den Gesamt-Diff gegen den ungefixten Stand
  zu prüfen) — hier: Logging-Calls einzeln entfernt → genau die 5
  D-066-Tests schlagen fehl; Origin-Check deaktiviert → 4 Tests; JSON-Check
  deaktiviert → 2 Tests. Stärkere Evidenz als ein einzelner
  Vorher/Nachher-Vergleich.

## Process-Notizen

- SDD-Workspace `.superpowers/sdd/sprint-033/` wird nach dieser sauberen
  Gesamtreview gelöscht (Projekt-Konvention seit Sprint 032: Workspace nur
  bei offenen Findings behalten). Sprint-qualifizierter Pfad manuell
  gewählt (Ledger, Briefs, Review-Pakete alle unter
  `.superpowers/sdd/sprint-033/`, nicht `.superpowers/sdd/plan/`) — die
  `plan.md`-Basename-Kollision der Skill-Skripte (`sdd-workspace`,
  `review-package`) besteht weiterhin in jedem Sprint seit 022; die vom
  Skript erzeugten Review-Pakete wurden nach jedem Dispatch manuell aus
  `.superpowers/sdd/plan/` in den sprint-qualifizierten Ordner verschoben.
- Implementierer: Sonnet für T1 und T2 (beide klar gescopte Security-/
  Logging-Fixes, je 1-3 Dateien). Reviews: Sonnet für beide Task-Reviews,
  Opus für die Gesamtreview.
- Kein Worktree, Commits direkt auf `master` per CLAUDE.md-Workflow, kein
  Push. `superpowers:finishing-a-development-branch` erneut nicht genutzt
  (kein Branch/PR in diesem Projekt) — `/sprint-wrap` ist der tatsächliche
  Abschluss-Schritt.
- Dieser Sprint nutzte `/sprint-plan` im Plan-Mode (13. Vorkommen dieser
  Kombination) — beide EPICs waren bereits präzise vorformuliert im
  Backlog (aus der Sprint-032-Gesamtreview), Planungsaufwand lag vor
  allem in den beiden `AskUserQuestion`-Rulings zum Umfang (CSRF-Breite,
  Logging-Breite inkl. `api_etag`, das nicht im Ticket-Wortlaut stand).
- Sprint-Umfang bewusst auf 2 EPICs beschränkt (D-065 + D-066 waren die
  einzigen sofort startbaren Backlog-Einträge) — kein Auffüll-Task nötig.

**Nächster Schritt:** `/sprint-plan` ausführen, um Sprint 034 einzuleiten
(primärer Kandidat: D-067).
