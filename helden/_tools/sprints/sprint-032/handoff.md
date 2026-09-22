# Sprint 032 Handoff — Pfad-Leak im `api_commit`-Fehlerpfad schließen (D-064)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `c89c301` (D-064 → in-progress, plan.md).
- ✅ **T1** (`api_commit`-Fehlerpfad: rohen Git-Stderr-Text nicht mehr
  durchreichen, Muster D-063) — `9ea3694`, Task-Review (Sonnet): Spec ✅,
  0 Findings, Approved — kein Fix-Loop nötig.
- ✅ **Gesamt-Review** (Opus) — „Ready to merge, Yes"; reproduzierte Leak +
  Fix unabhängig in einer Scratch-Kopie (Projekt-Tree nie berührt), 3 Minor
  (1 per Controller-Polish behoben, 2 neu gefiled: **D-065**, **D-066**).
- ✅ **T2** Verifikation — `verification.md`, `722682c` (D-065/D-066-Filing);
  Polish-Commit `cadcfc6` (1 Gesamtreview-Minor); `deccf28`
  (plan.md-Checkbox).
- Commits liegen **lokal** auf `master`: 5 neue Commits (`c89c301`,
  `9ea3694`, `deccf28`, `cadcfc6`, `722682c`) + dieser Wrap-Commit,
  **weiterhin nichts gepusht seit Sprint 022**.

## Was funktioniert

- **`api_commit` leakt keinen rohen Git-Stderr-Text mehr in der Fehler-JSON.**
  Fix an der HTTP-Grenze (`server.py:149`), identisches Muster zu D-063
  (`except FileNotFoundError` → 404 bei `api_held`): `git_ops.commit_helden()`s
  Rückgabe-Kontrakt (roher Stderr in `error`) bleibt intern unverändert —
  nur der HTTP-Response liest ihn nicht mehr aus. Status bleibt 500 (kein
  Client-Fall wie bei D-063s 404, ein Git-Fehler ist weiterhin ein echter
  Server-Fehler).
- **D-062 (`slug_param`-Traversal, Sprint 030) + D-063 (`api_held`-Fehler-
  JSON-Leak, Sprint 031) + D-064 (`api_commit`-Fehler-JSON-Leak, Sprint 032)**
  sind jetzt die dritte Iteration derselben Fehlerklasse — jedes Mal ein
  vorbestehender, nicht durch den jeweils aktuellen Fix eingeführter Fund an
  einem anderen Endpunkt/Feld.
- **Tests belegen die Diskriminierung empirisch, nicht nur behauptet:** die
  Gesamtreview maß die Dual-Assertion selbst nach — `str(tmp_path) not in
  body` besteht vakuos gegen den ungefixten Code (git nutzt Forward-Slashes,
  `Path` Backslashes), nur die Windows-Laufwerksbuchstaben-Regex
  diskriminiert korrekt. Bestätigt die Sprint-031-Lehre ein zweites Mal,
  unabhängig gemessen.
- **Tests:** 687 → **688** (+1 aus T1).
- **Neu entdeckt, nicht mitgefixt:** `POST /api/commit` hat keinen
  CSRF-Schutz — als **D-065** gefiled. Verschluckte Fehler (D-063s
  `FileNotFoundError`, D-064s verworfener Git-Stderr) landen nirgends im
  Server-Log, akkumuliert sich sprintübergreifend — als **D-066** gefiled.

## Verifikation

- **Test Suite:** 688/688 bestanden (`pytest tests/ -v` und
  `-q -W error` nach `__pycache__`-Löschen), vom Controller zweimal selbst
  gegengelaufen (T2 + dieser Wrap).
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert
  (exit 0) ✓ — inhaltlich unverändert (`git status --short` zeigt keine
  Diff auf `output/`), da D-064 ausschließlich einen Fehlerpfad in
  `server.py` ändert, kein Rendering-/Template-Code.
- Zahlen und Belege im Detail: `verification.md` im selben Ordner.

## Als nächstes (Sprint 033)

- **D-065**: `POST /api/commit` CSRF-Schutz — direkt startbar, kein
  Blocker, Effort S. Vorbestehend, von der Sprint-032-Gesamtreview
  gefunden; Impact begrenzt (kein Datenverlust, reversibler lokaler Commit,
  Antwort bleibt Cross-Origin durch fehlende CORS-Header ohnehin unlesbar).
- **D-066**: konsolidiertes Logging für verschluckte Fehler (D-063+D-064)
  — direkt startbar, kein Blocker, Effort S. Verhindert, dass die
  Logging-Frage bei jedem künftigen Pfad-Leak-Fix erneut aufgeschoben wird.
- Vault-`backlog.md` bleibt leer — kein B-Task in Sprint 032.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **`api_patch_value`/`api_patch_kampagne` wurden von der Gesamtreview auf
  dieselbe Fehlerklasse geprüft und explizit als nicht betroffen
  bestätigt** (`held_writer.patch()`s komplettes Fehler-Vokabular enthält
  keine absoluten Pfade) — kein offener Punkt, sondern eine verifizierte
  Nicht-Betroffenheit, kein neues Ticket nötig.
- **Aus Sprint 020–031 unverändert offen** (keine dieser Punkte in
  Sprint 032 berührt): echter Druckdialog (Papier-Ausdruck) ungeprüft;
  D-058-Zeilenhöhen-Zuwachs → echter Seitenumbruch-Effekt ungeprüft; Messung
  nur an einem Charakter (illaen-baernhold); Register hängt am
  Session-Format; echter Browser-Klick gegen eine echte Session-Datei nie
  ausgelöst; inhaltliche Sichtung der vier Sessions; Kommando-Mängel von
  `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://`
  Fake-Erfolg; Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch;
  SF-Vorschau-Randfälle; Zustands-Chips = Hausregel; `api_patch_kampagne`s
  Inline-Campaign-Regex-DRY-Nit (Sprint 030, „defensible as-is").

## Lehren (Process)

- **Dieselbe Fehlerklasse kann sich über mehrere Sprints hinweg an
  verschiedenen Endpunkten wiederholen, bis eine Review sie explizit als
  vollständig abgedeckt bestätigt.** D-062 → D-063 → D-064 war die dritte
  Iteration; erst die Sprint-032-Gesamtreview prüfte aktiv nach, ob noch
  weitere Endpunkte betroffen sind (statt nur den einen gefileten Fund zu
  fixen), und bestätigte empirisch, dass `api_patch_value`/
  `api_patch_kampagne` nicht zur selben Klasse gehören. Diese aktive
  Nicht-Betroffenheits-Prüfung ist wertvoller als ein reflexhaftes neues
  Ticket „Rest der Klasse auch prüfen".
- **Zwei unabhängige Reviews (Sprint 031 und 032) haben jetzt denselben
  Vakuositäts-Effekt bei Pfad-Leak-Tests auf Windows gemessen** (git
  Forward-Slashes vs. `Path`-Backslashes lassen eine reine
  `str(tmp_path) not in body`-Prüfung durchrutschen) — die
  Dual-Assertion-Regel (Substring **+** Laufwerksbuchstaben-Regex) ist
  damit kein Einzelfall-Fund mehr, sondern eine feste Konvention für
  jeden künftigen Pfad-Leak-Test in diesem Projekt.
- **Reviewer-gefundene, aber Scope-fremde Beobachtungen (hier: CSRF)
  gehören als eigenes Ticket ins Backlog, nicht in eine Fußnote.** D-065
  entstand aus einer Sicherheitsbeobachtung, die nichts mit D-064s Diff zu
  tun hatte — die Gesamtreview prüfte sie trotzdem, weil „Security,
  specifically" explizit im Reviewer-Auftrag stand.

## Process-Notizen

- Kein SDD-Workspace mehr vorhanden — `.superpowers/sdd/sprint-032/` wurde
  nach der sauberen Gesamtreview gelöscht (Projekt-Konvention: Workspace
  nur bei offenen Findings behalten). Sprint-qualifizierter Pfad
  (`sprint-032` statt `plan`) erneut manuell gewählt — `plan.md`-Basename-
  Kollision besteht in jedem Sprint seit 022.
- `task-brief`-Skript passt weiterhin nicht zu diesem Projekts `plan.md`-
  Format (Tabellenzeilen statt `## Task N`-Überschriften) — Brief von Hand
  geschrieben (Konvention seit Sprint 025).
- Dieser Sprint nutzte `/sprint-plan` im Plan-Mode (12. Vorkommen dieser
  Kombination) — Recherche (Explore-Agent-Dispatch übersprungen,
  Quelldateien direkt gelesen: `server.py`, `git_ops.py`,
  `tests/test_commit.py`) bestätigte den exakten Fix-Ansatz vor
  `ExitPlanMode`, keine Überraschung während der Umsetzung.
- Implementierer: Sonnet für T1 (kleiner, gut gescopter Security-Fix, 1
  Route + 1 Test). Reviews: Sonnet für den Task-Review, Opus für die
  Gesamtreview.
- 1 trivialer Gesamtreview-Minor direkt vom Controller gefixt
  (Test-Kommentar, < 10 Zeilen) statt per Implementierer-Dispatch —
  Projekt-Konvention für triviale Review-Funde, re-verifiziert (688/688)
  vor Commit.
- Kein Worktree, Commits direkt auf `master` per CLAUDE.md-Workflow, kein
  Push. `superpowers:finishing-a-development-branch` erneut nicht genutzt
  (kein Branch/PR in diesem Projekt) — `/sprint-wrap` ist der tatsächliche
  Abschluss-Schritt.
- Sprint-Umfang bewusst auf 1 EPIC beschränkt (D-064 war der einzige
  startbare Backlog-Eintrag nach Sprint 031) — kein Auffüll-Task nötig.

**Nächster Schritt:** `/sprint-plan` ausführen, um Sprint 033 einzuleiten
(primäre Kandidaten: D-065, D-066).
