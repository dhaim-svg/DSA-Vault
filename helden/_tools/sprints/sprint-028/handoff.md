# Sprint 028 Handoff — Selector-Scoping (D-057), Druck-Feinschliff (D-058), PATCH-Testabdeckung (D-059), Footer-Transition (D-060)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `253876f`
- ✅ **T1 D-057** (`#tab-profil table *`-Flächenschlag entschärft) — `5eca7d5`, 2 Fix-Runden
  (Golden-Render-Diff-Pflicht zunächst nur behauptet statt erfüllt; Runde 1 diffte weiterhin
  nur Quelltext, Runde 2 rendert echt via `render_dashboard()`). Re-Review: ADDRESSED.
- ✅ **T2 D-058** (Probe-Spalte einzeilig + Ritual-/SF-Grid-Stretch, Zauber-Tab-scoped) —
  `2b56bbd`. Task-Review Approved beim ersten Durchgang; 1 sprintübergreifendes Important
  (Static-Render-Artefakt) auf T5 verschoben statt Fix-Runde.
- ✅ **T3 D-059** (PATCH-Route-Test, sicher gegen `tmp_path`) — `88ea374`. Review Approved,
  0 Findings beim ersten Durchgang.
- ✅ **T4 D-060** (Footer-Transition) — `d117447`, 1 Fix-Runde (Report behauptete "volle
  Suite", lief aber nur 140 von 662 Tests — Controller fing das vor Re-Review-Dispatch ab).
- ✅ **Static-Render-Nachzug** — `3aa835a` (Ruling: einmal gesammelt statt 3× einzeln).
- ✅ **Gesamt-Review** (Opus) — 0 Critical, 2 Important + 4 Minor, 1 gebündelte Fix-Runde
  (`ba82764` Minors, `d249fed` Importants), Re-Review: alle 7 ADDRESSED.
- ✅ **T5** Verifikation, Tracker (`verification.md`, dieses Dokument; `BACKLOG.md`-Done-
  Transition folgt via `/sprint-wrap`).
- Commits liegen **lokal** auf `master`: 8 neue Commits, **weiterhin nichts gepusht seit
  Sprint 022** (Sprint 027 hatte das schon vermerkt — unverändert).

## Was funktioniert

- **`#tab-profil` hat keinen Flächenschlag-Selector mehr** — die Sessions-Tabelle trägt eine
  eigene Klasse (`.sessions-table`), das Druck-CSS zielt darauf statt pauschal auf `table`/
  `table *`. Kein aktueller Bug behoben (es gab nur 1 Tabelle), aber das Regressionsrisiko
  für künftige Tabellen in diesem Tab ist weg — verifiziert per echtem Golden-Render-Diff
  (gerenderter Output, nicht nur Quelltext).
- **Die Probe-Spalte im Zauber-Tab-Druck ist einzeilig** (war 25/25 Zeilen zweizeilig seit
  Sprint 025) — mit einer transparent dokumentierten kleinen Nebenwirkung: die Zeilenliste
  ist im Druck ca. 4,5 % höher (77px auf ~1,7-1,8kB), weil die schmalere Kosten-Spalte öfter
  umbricht. Kein Überlauf, kein Rollback nötig, aber die D-058-Done-Zeile sollte diesen
  Zeilenhöhen-Zuwachs nennen (Text-Vorschlag in `verification.md`).
- **Die Ritual-/SF-Karten im Zauber-Tab stretchen nicht mehr** unschön, wenn mehrere
  Ritual-Artikelvorschauen offen sind — nur diese eine Grid-Instanz betroffen, die 3
  anderen `.cols-2`-Verwendungsstellen (profil/inventar/kampf) unangetastet und per Test
  gepinnt.
- **Der PATCH-Pfad „Verlauf speichern" hat jetzt automatisierte Testabdeckung** (Routen-
  Wiring, `camp`-Guard, JSON-Handling) — sicher gegen eine `tmp_path`-Fixture, der echte
  Vault wurde nie berührt. Ein noch offener Gap (`file`-Feld ungeprüft gegen Path-Traversal)
  ist jetzt als **D-061** im Tracker (nicht mehr nur eine Randbemerkung in Handoffs).
- **Der Footer gleitet jetzt synchron mit dem Würfelpanel ein/aus** statt zu springen (Lücke
  war seit Sprint 021 bekannt: 331→197→108→28px). Test verifiziert die Synchronität
  relational (liest die reale Panel-Dauer), nicht durch zwei hartkodierte Werte.
- **Tests:** 652 → **662** (+10 netto über die vier Feature-Tasks, Gesamt-Review-Fixwelle
  änderte nur einen bestehenden Test von hartkodiert auf relational, keine Netto-Änderung).

## Verifikation

Zahlen und Belege: `verification.md` im selben Ordner.

## Als nächstes (Sprint 029)

- **`BACKLOG.md` hat jetzt genau 1 Eintrag**: **D-061** (`file`-Locator-Feld der PATCH-Routen
  ungeprüft gegen Path-Traversal, `state=ready`, Effort S) — direkt startbar, kein
  Blocker. Kein Design-Entscheidungs-Bedarf wie D-054/055/056 oder die D-058/D-059-Rulings
  dieses Sprints — die Fix-Richtung ist klar (Pfad-Normalisierung + Präfix-Check gegen
  `base`), `/sprint-plan` kann das direkt schneiden.
- Vault-`backlog.md` bleibt leer — kein B-Task in Sprint 028.
- Falls D-061 allein zu klein für einen ganzen Sprint ist: die "Bekannte Einschränkungen"-
  Liste unten hat weiterhin unbenannte Kandidaten (unverändert seit mehreren Sprints,
  s. unten) — z. B. echter Druckdialog-Test, `/session-compile`-Mängel, oder die D-058-
  Zeilenhöhen-Nebenwirkung genauer untersuchen (echter `page.pdf()`-Seitenzahl-Check, falls
  die 4,5 % doch mal einen zusätzlichen Seitenumbruch auslösen sollten — bisher nicht
  geprüft).

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **D-058 Zeilenhöhen-Zuwachs → echter Seitenumbruch-Effekt ungeprüft** (neu diese Sprint):
  +4,5 % Zeilenhöhe im Zauber-Tab-Druck gemessen, aber ob das je einen zusätzlichen
  gedruckten Seitenumbruch auslöst, wurde nicht mit einem echten `page.pdf()`-Lauf
  geprüft (nur die isolierte Zeilenhöhen-Messung war beauftragt).
- **Echter Druckdialog weiterhin ungeprüft** — `page.pdf()` ist die bisher beste Näherung,
  aber kein Papier-Ausdruck wurde je gemacht. Unverändert seit Sprint 020.
- **Messung nur an einem Charakter** (illaen-baernhold). Unverändert seit mehreren Sprints.
- **Aus Sprint 017–027 unverändert offen:** Register hängt am Session-Format; `Verlauf`-
  Speichern jetzt automatisiert getestet (D-059), aber der echte Browser-Klick gegen eine
  echte Session-Datei wurde weiterhin nie ausgelöst (User-Entscheidung diesen Sprint:
  bewusst nicht in Scope); inhaltliche Sichtung der vier Sessions; Kommando-Mängel von
  `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://` Fake-Erfolg;
  Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch; SF-Vorschau-Randfälle; Zustands-
  Chips = Hausregel.

## Lehren (Process)

- **Eine Dimension zu messen beweist nichts über eine andere.** D-058s `scrollWidth`-Check
  (horizontal) ließ eine Zeilenhöhen-Nebenwirkung (vertikal) unentdeckt bis zur Gesamt-
  Review. Bei künftigen fr-Anteilsverschiebungen: auch Zeilenhöhen vergleichen, wenn eine
  Spalte mit variabler Zeilenzahl schmaler wird.
- **Ein Task-Review kann eine Behauptung nicht immer von echter Verifikation unterscheiden**,
  wenn beide dieselbe Wortwahl benutzen. T1s Golden-Render-Diff wurde zweimal als erfüllt
  gemeldet, bevor er es wirklich war (erst Quelltext-Diff, dann noch mal Quelltext-Diff mit
  mehr Überschriften) — erst eine sehr konkrete dritte Anweisung (exakte Python-Befehle für
  den echten Render-Aufruf) brachte echte Evidenz. Lehre: bei einer bereits einmal
  verfehlten Verifikationspflicht in der zweiten Runde konkrete, copy-paste-fertige Befehle
  mitgeben statt nur die Anforderung zu wiederholen.
- **Ein "volle Suite"-Claim ist nur mit dem tatsächlichen Kollektions-Log verifizierbar.**
  T4 behauptete 140/140 = volle Suite; der Reviewer verglich die Zahl gegen den aus
  früheren Tasks bekannten Gesamt-Testcount (661/662) und fand den Widerspruch sofort. Ein
  reiner "N passed"-Blick ohne Gegenzahl hätte das nicht gefangen.
- **Statische Render-Artefakte, die sonst pro Commit mitgezogen werden, driften unbemerkt,
  wenn kein Task-Review explizit danach fragt.** T1 und T2 ließen `output/*.html` beide
  unangetastet; erst die Gesamt-Review bemerkte es. Ein Standard-Checkpunkt "wurde ein
  betroffenes Render-Artefakt aktualisiert?" im Task-Review-Template würde das künftig
  früher fangen.
- Der `plan.md`-Basisname-Kollisionsfalle (jeder Sprint heißt `plan.md`) bestätigt sich
  erneut — weiterhin manuell sprint-028-qualifizierte Pfade unter `.superpowers/sdd/
  sprint-028/` verwendet.

## Process-Notizen

- Briefs/Ledger/Reports liegen unter `.superpowers/sdd/sprint-028/` (gitignored,
  sprint-qualifiziert seit Sprint 023). Workspace bewusst behalten (Konvention seit
  Sprint 023/025/027), nicht gelöscht.
- Implementierer: Haiku für mechanische Single-File-Tasks (T1, T4), Sonnet für
  Judgment-lastige Tasks (T2 fr-Mathematik + Messung, T3 Vault-Sicherheit, Gesamt-
  Review-Fixwelle). Reviews: Sonnet für T1-T3, Haiku für T4 (kleiner mechanischer Diff),
  Opus für die Gesamt-Review.
- Kein Worktree, Commits direkt auf `master` per CLAUDE.md-Workflow, kein Push.
- Alle Design-Entscheidungen (Grid-Stretch-Scope, PATCH-Verifikationsmethode) wurden vor
  Dispatch per `AskUserQuestion` in der Sprint-Planung eingeholt — kein Implementierer
  musste während der Umsetzung nachfragen.
- Backlog war zu Sprintbeginn komplett leer (beide Tracker) — die vier EPICs kamen aus dem
  Sprint-027-Handoff-Abschnitt "Als nächstes", nicht aus vorab geschnittenen Backlog-Zeilen.
