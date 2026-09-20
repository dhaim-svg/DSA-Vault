# Sprint 027 Handoff — Druck-Vollständigkeit (D-054/D-055), Papieroptik-Ruling (D-056), Cleanup (B-027)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `1cef602`
- ✅ **T1 D-054** (Vitalwerte im Druck) — `7b070b0`, Fix-Runde 1 `9997bfb` (`.vital-max`/`.vital-sep`
  verloren `opacity:0.7`). Task-Review + Re-Review clean.
- ✅ **T2 D-055** (Verlaufstext im Druck) — `d13223b` (v1: Textarea-Resize), Fix-Runde 1 `8e5b150`
  (Gesamt-Review fand Breiten-Mismatch, v1 komplett auf Druck-Mirror umgestellt statt geflickt).
  Task-Review clean, Gesamt-Review-Fixwelle: Re-Review clean.
- ✅ **T3 D-056** (Papieroptik-Ruling, kein Code) — `662c5f8`, Controller inline.
- ✅ **T4 B-027** (Parser-Cleanup) — `082b088`, Review clean beim ersten Durchgang.
- ✅ **T5** Verifikation, Tracker (BACKLOG.md D-054/D-055 noch "in-progress" — Done-Umzug ist
  `/sprint-wrap`s Aufgabe), dieses Dokument.
- Commits liegen **lokal** auf `master`: **nichts seit Sprint 022 (ab T2) ist gepusht**, Sprint 027
  fügt 7 weitere lokale Commits hinzu.

## Was funktioniert

- **LeP/AsP/AuP sind im Ausdruck sichtbar** — das reale Eingabefeld druckt seinen aktuellen,
  live editierten Wert direkt (kein JS-Sync nötig), `.vital-max`/`.vital-sep` mit korrekt
  zurückgesetzter Opazität, alle drei bei 14,62:1 gemessen (Print-Emulation + echter PDF-Pfad).
- **Der Verlaufstext druckt vollständig** — bei **beiden** getesteten Fensterbreiten (1280px und
  718px), nicht nur bei der einen, bei der der ursprüngliche Fix zufällig funktionierte. Ein
  `<pre>`-Mirror wird bei `beforeprint` aus dem Live-`t.value` befüllt und vom Druck-Layout selbst
  umbrochen — keine manuelle Höhen-/Breitenrechnung mehr im Spiel.
- **Die redundante Gewichts-Bedingung ist weg**, mit Mutationsprobe direkt auf `safe_int`
  statt nur auf der Integrationsebene.
- **Tests:** 633 → **652**, auch mit `-W error`.

## Verifikation

Zahlen und Belege: `verification.md` im selben Ordner.

## Als nächstes (Sprint 028)

- **Beide Tracker (`BACKLOG.md`, Vault-`backlog.md`) sind nach diesem Sprint leer** — keine
  sofort startbaren EPICs mehr vorrätig. `/sprint-plan` für Sprint 028 muss entweder aus den
  „Bekannten Einschränkungen" unten neue EPICs schneiden, oder der User bringt neuen Input
  (Wiki-Lücken, neue Dashboard-Wünsche, o. ä.).
- Naheliegende Kandidaten ohne EPIC-Nummer (aus „Bekannte Einschränkungen", unverändert seit
  mehreren Sprints offen): `#tab-profil table *`-Flächenschlag entschärfen, Probe-Spalte im
  Zauber-Tab (bricht zweizeilig), Grid-Stretch der Ritual-/SF-Karte, echter PATCH-Pfad im
  Browser verifizieren, Footer-Transition beim Einblenden.
- Kein EPIC verlangt zwingend eine Design-Entscheidung wie D-054/055/056 — falls der User
  einen der Kandidaten priorisiert, kann `/sprint-plan` ihn direkt schneiden.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Echter Druckdialog weiterhin ungeprüft** — `page.pdf()` ist die bisher beste Näherung, aber
  kein Papier-Ausdruck wurde je gemacht. Unverändert seit Sprint 020.
- **Messung nur an einem Charakter** (illaen-baernhold). Unverändert seit mehreren Sprints.
- **`#tab-profil table *`** (`tabs.css:170`) bleibt ein Flächenschlag für jede künftige Tabelle
  in diesem Tab — unverändert seit Sprint 026 verschoben.
- **Aus Sprint 017–026 unverändert offen:** Register hängt am Session-Format; `Verlauf`-Speichern
  nie im Browser angeklickt (der Save-Button existiert und die PATCH-Route auch, aber der
  End-to-End-Pfad wurde nie im Browser ausgelöst); inhaltliche Sichtung der vier Sessions;
  Kommando-Mängel von `/session-compile`; Static-Render-Schreibaktionen liefern unter `file://`
  Fake-Erfolg; Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch; Footer springt beim
  Einblenden; SF-Vorschau-Randfälle; Zustands-Chips = Hausregel; Grid-Stretch der Ritual-/
  SF-Karte; Probe-Spalte im Zauber-Tab.

## Lehren (Process)

- **Der Methodenbefund ist wieder die wichtigste Erkenntnis:** `beforeprint` misst im
  **Bildschirm**-Layout, nicht im Druck-Layout. Ein Fix, der zum Messzeitpunkt korrekte Werte
  berechnet (hier: `scrollHeight` bei Bildschirmbreite) und sie als feste Zahl in den Druck
  mitgibt, kann bei einer anderen Druckbreite falsch sein. Die etablierte 718px-Verifikations-
  Viewport-Größe (seit Sprint 020 die Druckbreiten-Näherung dieses Projekts) versteckte diesen
  Fehler strukturell, weil bei 718px Druck- und Bildschirmbreite zufällig zusammenfallen. Folge
  fürs Verfahren: **Breiten-Verifikation braucht mindestens zwei unterschiedliche Fensterbreiten**,
  nicht nur die eine etablierte Näherung — ein Element, das der Browser selbst im Druck-Layout
  umbricht, ist robuster als eine im Bildschirm-Layout vorausberechnete Zahl.
- **Ein „vollständig"-Claim ohne Gegenprobe bei zweiter Breite war zu früh.** T2s eigener Report
  behauptete „vollständig sichtbar" nach Verifikation bei nur einer Fensterbreite — dieselbe
  Klasse Fehler wie in früheren Sprints (übernommene Zahlen, ungeprüfte Einstufungen). Die
  Gesamt-Review fing es, aber ein Task-Review mit zwei Breiten hätte es früher gefangen.
- **Ein Task-Review kann strukturell nicht alles sehen.** Der T2-Task-Review war zu Recht
  „Approved" — er kann keine neue Browser-Session mit anderer Fensterbreite aufmachen, um eine
  Behauptung nachzumessen, die der Diff selbst nicht zeigt. Genau dafür existiert die
  Gesamt-Review als zweite, mit mehr Handlungsspielraum ausgestattete Stufe.
- **Ein „kein Duplikat-Element"-Ruling (R2) wurde während der Ausführung korrekt gebrochen.**
  Der Fix-Runde-Mirror ist technisch ein zusätzliches Element — aber R2s eigentliches Anliegen
  (kein serverseitig veralteter Text) blieb erfüllt, weil der Mirror aus dem Live-DOM-Wert im
  Druckmoment befüllt wird. Eine Ruling wörtlich zu befolgen, obwohl die Messung zeigt, dass ihr
  Mechanismus das Ziel verfehlt, wäre falsch gewesen — die Ruling wurde als R4 korrigiert, nicht
  stillschweigend übergangen.
- **Tracker-Kollision (`plan.md`-Basename) bestätigt sich als Dauerzustand:** `sdd-workspace`
  leitet weiterhin `.superpowers/sdd/plan/` ab; jeder Sprint braucht den manuellen
  sprint-qualifizierten Pfad. `task-brief` funktioniert zusätzlich nicht mit diesem Projekts
  Tabellen-Format (ein Task pro Zeile statt `## Task N`-Überschrift) — Briefs wurden von Hand
  geschrieben, `review-package` (rein git-range-basiert) funktionierte unverändert mit
  explizitem OUTFILE-Argument.

## Process-Notizen

- Briefs/Ledger/Reports unter `.superpowers/sdd/sprint-027/` (git-ignoriert), sprint-qualifiziert
  wegen der `plan.md`-Namenskollision (wie alle Sprints seit 023). Workspace bewusst behalten
  (nicht gelöscht), wie Sprint 025/026.
- Implementierer T1/T2 Sonnet, T4 Haiku (mechanische Cleanup-Aufgabe), Task-Reviews Sonnet/Haiku
  je nach Diff-Größe, Gesamt-Review Opus, gescopte Re-Reviews Sonnet/Haiku.
- Implementierer dienten gleichzeitig als eigene Browser-Verifikations-Agenten (kein separater
  Mess-Agent wie in Sprint 026 nötig — der Umfang war von Anfang an eng geschnitten, im
  Gegensatz zu D-053s offenem 7-Tab-Sweep).
- Kein Worktree, Commits direkt auf `master` (CLAUDE.md-Workflow), kein Push. Die generische
  `finishing-a-development-branch`-Stufe von `subagent-driven-development` entfällt strukturell
  (kein separater Branch zu integrieren) — `/sprint-wrap` übernimmt diese Rolle projektspezifisch.
- Alle drei Design-Entscheidungen (D-054/055/056) wurden **während der Sprint-Planung** per
  `AskUserQuestion` eingeholt, nicht erst während der Ausführung — dadurch enthielten die
  Subagent-Briefs von Anfang an bindende Rulings statt offener Fragen.
