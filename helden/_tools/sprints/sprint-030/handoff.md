# Sprint 030 Handoff — slug_param-Traversal schließen (D-062)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `36bb140` (D-062 → in-progress, plan.md).
- ✅ **T1** (`slug_param`-Guard auf allen 5 Routen) — `5ca5dde`, 1 pre-emptiver
  Fix-Round (`bcce11e`: `'../outside'` als eigener Parametrize-Fall auf
  `held_page` statt `/value` — Controller-Ruling während der Implementierung,
  vor Review-Fund), Task-Review + Scoped-Re-Review beide ADDRESSED/clean.
- ✅ **Gesamt-Review** (Opus) — „Ready to merge, with fixes"; reproduzierte
  Exploit + Fix unabhängig in einem Scratch-Worktree bei `eeb8736`, fand 1
  Important (dokumentationsbezogen, kein Code-Fix nötig) + 3 Minor (2
  geparkt, 1 als D-063 neu gefiled).
- ✅ **T2** Verifikation — `verification.md`, dieses Dokument; `c925b36`
  (plan.md-Checkbox, D-063-Filing), `7b897eb` (BACKLOG.md-Doku-Fix).
- Commits liegen **lokal** auf `master`: 6 neue Commits, **weiterhin nichts
  gepusht seit Sprint 022** (unverändert seit mehreren Sprints).

## Was funktioniert

- **Alle 5 `/api/held/<slug_param>/...`- und `/held/<path:s>`-Routen lehnen
  Path-Traversal über den Slug/URL-Parameter jetzt ab** — inklusive des
  Windows-spezifischen Backslash-Vektors (`%5C`), den Werkzeugs Routing
  anders als `/` (`%2F`) nicht selbst abfängt. `_valid_slug()` ist eine
  Allowlist (`[a-z0-9_-]+`), kein `/`-spezifisches Denylist — deckt damit
  jeden Separator gleichermaßen ab.
- **D-061 (Sprint 029) + D-062 (dieser Sprint) zusammen schließen jetzt alle
  bekannten HTTP-erreichbaren Path-Traversal-Vektoren** in `server.py`:
  `file`-Feld, `campaign`-Feld (auch über den JSON-Body-Bypass), und
  `slug_param`/`s` (URL-Segment, alle 5 Routen inkl. der bisher nicht im
  Ticket-Titel genannten Seiten-Route).
- **Tests belegen die Diskriminierung tatsächlich**, nicht nur behauptet:
  die Gesamtreview kopierte den kompletten neuen Testfile auf den
  ungefixten Stand und lief ihn dort — 11 von 13 neuen Tests schlagen dort
  fehl (= fangen den Bug korrekt), die übrigen 2 sind bewusst beidseitig
  grüne Regressionstests mit echten Inhalts-Assertions. **0 vakuose Tests**
  (Gegensatz zu 5 von 8 in Sprint 029).
- **Tests:** 671 → **684** (+13 netto: 12 aus T1, 1 aus dem Fix-Round).

## Verifikation

- **Test Suite:** 684/684 bestanden (`pytest tests/ -q` und
  `-q -W error` nach `__pycache__`-Löschen), unabhängig vom
  Implementierer-Report zweimal selbst gegengelaufen.
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert
  (exit 0) ✓ — inhaltlich unverändert (`git status --short` zeigt keine
  Diff), da D-062 ausschließlich Routen-Guards in `server.py` ändert, kein
  Rendering-/Template-Code.
- Zahlen und Belege im Detail: `verification.md` im selben Ordner.

## Als nächstes (Sprint 031)

- **D-063**: `api_held`s Exception-Handler (`server.py:78-79`) leakt absolute
  Dateisystempfade in der Fehler-JSON bei jeder Exception aus
  `load_held()`/`load_kampagne()` — direkt startbar, kein Blocker, Effort S.
  Von der Sprint-030-Gesamtreview beim Scratch-Worktree-Test gefunden
  (vorbestehend, nicht durch D-062 eingeführt).
- Vault-`backlog.md` bleibt leer — kein B-Task in Sprint 030.
- Falls D-063 allein zu klein für einen ganzen Sprint ist: die „Bekannte
  Einschränkungen"-Liste unten hat weiterhin unbenannte Kandidaten.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **2 Minor-Funde aus der Gesamtreview bewusst nicht gefixt** (nicht dieser
  Sprint-Scope, kein Folge-Ticket nötig): (1) `'..%5Csub'` fehlt als
  expliziter Testfall im `/value`-Parametrize + eine Docstring-Formulierung
  in `test_valid_slug_rejects_embedded_slash_traversal` überzeichnet den
  Geltungsbereich leicht — Mutationsprobe zeigt aber, dass keine echte
  Diskriminierungslücke besteht (jede Schwächung, die `%5C` wieder öffnet,
  wird auch von einem bestehenden Test gefangen); (2) `api_patch_kampagne`s
  Inline-Campaign-Regex könnte `_valid_slug()` wiederverwenden (reiner
  DRY-Nit, vom Reviewer selbst als „defensible as-is" eingestuft).
- **Aus Sprint 020–029 unverändert offen** (keine dieser Punkte in
  Sprint 030 berührt): echter Druckdialog (Papier-Ausdruck) ungeprüft;
  D-058-Zeilenhöhen-Zuwachs → echter Seitenumbruch-Effekt ungeprüft; Messung
  nur an einem Charakter (illaen-baernhold); Register hängt am
  Session-Format; echter Browser-Klick gegen eine echte Session-Datei nie
  ausgelöst; inhaltliche Sichtung der vier Sessions; Kommando-Mängel von
  `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://`
  Fake-Erfolg; Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch;
  SF-Vorschau-Randfälle; Zustands-Chips = Hausregel.

## Lehren (Process)

- **„Werkzeugs Routing schließt Pfad-Separatoren aus" ist auf Windows
  falsch.** Der Default-`string`-Converter schließt nur `/` (bzw. dessen
  `%2F`-Kodierung) aus — `\` (`%5C`) passiert ihn ungehindert, und Windows'
  Pfadauflösung behandelt Backslash als Separator. Diese (falsche) Annahme
  stand wörtlich sowohl im ursprünglichen D-062-Ticket-Text als auch in
  einem neuen Test-Docstring — beide korrigiert. Jede künftige Route, die
  sich auf Werkzeugs Routing als alleinigen Trennzeichen-Schutz verlässt,
  erbt dieselbe Lücke auf diesem Betriebssystem. Eine Allowlist-Regex (wie
  hier `[a-z0-9_-]+`) umgeht das Problem grundsätzlich, weil sie nicht
  darauf angewiesen ist, alle gefährlichen Zeichen einzeln zu kennen.
- **Ein Controller-Ruling während der Implementierung kann eine bereits
  dispatchte Review überholen, bevor deren Bericht zurückkommt.** Die
  `held_page`-Testergänzung (`bcce11e`) wurde direkt nach dem Ruling
  committet, während der Task-Reviewer noch gegen den älteren Diff-Snapshot
  arbeitete — der Reviewer fand danach korrekt „fehlt", obwohl es zu dem
  Zeitpunkt bereits behoben war. Kein Prozessfehler (der Reviewer kann nur
  sehen, was zum Dispatch-Zeitpunkt existierte), aber es lohnt sich, nach
  einem Ruling, das eine Code-/Test-Änderung nach sich zieht, kurz zu prüfen,
  ob eine bereits laufende Review davon betroffen ist, bevor man ihr
  Ergebnis als vollständig behandelt.
- **Ein Gesamtreview-Fund kann rein dokumentationsbezogen sein, ohne
  Code-Fix zu brauchen** — hier maß die Review eine reale, größere
  Angriffsfläche als der Ticket-Text behauptete, aber der bereits
  implementierte Fix deckte sie durch Zufall (Allowlist statt Denylist)
  bereits vollständig ab. Trotzdem den Tracker-Text korrigieren, damit die
  historische Aufzeichnung (das Done-Eintrag) nicht die ursprünglich zu
  enge Einschätzung fortschreibt.
- **Ein vorbestehender Fund, der beim Scratch-Worktree-Test einer
  Gesamtreview auftaucht (nicht Teil des eigentlichen Fixes), verdient ein
  eigenes Backlog-Ticket** statt nur einer Ledger-Notiz — hier D-063, exakt
  nach demselben Muster, wie D-062 selbst aus D-061s Review heraus gefiled
  wurde.

## Process-Notizen

- Briefs/Ledger/Reports liegen unter `.superpowers/sdd/sprint-030/`
  (gitignored, sprint-qualifiziert wie seit Sprint 022). Workspace bewusst
  behalten (Konvention seit Sprint 023/025/027/028/029), nicht gelöscht.
- `sdd-workspace`/`review-package`-Basename-Kollision (`plan.md` in jedem
  Sprint) erneut manuell umgangen — Dateien nach dem jeweiligen Skript-Lauf
  in den sprint-qualifizierten Ordner verschoben.
- Dieser Sprint nutzte `/sprint-plan` im Plan-Mode (10. Vorkommen dieser
  Kombination) — Recherche (Explore-Agent-Dispatch übersprungen, Quelldateien
  direkt gelesen) deckte die `held_page`-Scope-Erweiterung auf und wurde
  transparent vor `ExitPlanMode` in den Plan geschrieben, nicht später still
  ergänzt.
- Implementierer: Sonnet für T1 (Security-Fix, mehrere Routen + Tests).
  Reviews: Sonnet für den Task-Review, Haiku für die schlanke
  Scoped-Re-Review (1 mechanischer Test-Diff), Opus für die Gesamtreview.
- Kein Worktree, Commits direkt auf `master` per CLAUDE.md-Workflow, kein
  Push. `superpowers:finishing-a-development-branch` erneut nicht genutzt
  (kein Branch/PR in diesem Projekt) — `/sprint-wrap` ist der tatsächliche
  Abschluss-Schritt.
- Sprint-Umfang bewusst auf 1 EPIC beschränkt (D-062 war der einzige
  startbare Backlog-Eintrag nach Sprint 029) — kein Auffüll-Task nötig, da
  kein zweiter konkret scoped Kandidat vorlag.

**Nächster Schritt:** `/sprint-plan` ausführen, um Sprint 031 einzuleiten
(primärer Kandidat: D-063).
