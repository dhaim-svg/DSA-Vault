# Sprint 029 Handoff — Path-Traversal-Fix (D-061)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `0288f46` (D-061 → in-progress, D-062 neu gefiled, plan.md).
- ✅ **T1 D-061** (Path-Traversal-Guard in `held_writer.py`) — `2124114`, 1 Task-Review-
  Fix-Runde (`992629a`: Null-Byte-Crash in `_safe_join`), dann 1 Gesamt-Review-Fixwelle
  (`5f03455`: 5 vakuose Tests diskriminierend gemacht + Verzeichnis-als-Datei-Crash
  gefixt). Beide Re-Reviews: ADDRESSED, keine neue Breakage.
- ✅ **Gesamt-Review** (Opus) — „Ready to merge, with fixes"; Produktionsfix unabhängig
  reverifiziert (Scratch-Revert + Re-Test aller 4 Traversal-Vektoren, echtes
  Datei-Überschreiben pre-fix bestätigt).
- ✅ **T2** Verifikation — `verification.md`, dieses Dokument; `dcd0663`
  (plan.md-Checkbox, D-062-Beleg).
- Commits liegen **lokal** auf `master`: 5 neue Commits, **weiterhin nichts gepusht
  seit Sprint 022** (unverändert seit mehreren Sprints).

## Was funktioniert

- **Die PATCH-Routen lehnen Path-Traversal jetzt ab** — sowohl über das `file`-Feld
  (relative `../`-Traversal UND absolute Pfade, inkl. UNC/Cross-Drive auf Windows) als
  auch über das `campaign`-Feld, und zwar unabhängig davon, über welche Route der
  Request kommt (`/api/kampagne/<camp>/value`s Routen-Level-Regex UND
  `/api/held/<slug>/value`s ungefilterter JSON-Body landen beide bei derselben
  zentralen `_resolve_base()`-Prüfung). `etag_for()` ist über denselben Helper
  (`_safe_join`) mitabgesichert.
- **Robust gegen Rand-Input**: leerer `file`-Wert, Null-Byte im Pfad, ein Verzeichnis
  statt einer Datei als `file`-Wert — alle drei kollabieren jetzt sauber zur
  bestehenden „nicht gefunden"-Fehlerantwort statt einer unbehandelten Exception
  (500). Beide Fälle wurden erst in Review-Runden gefunden, nicht im ursprünglichen
  Implementierungsdurchgang.
- **Tests belegen die Sicherheitseigenschaft tatsächlich**, nicht nur behauptet: nach
  der Gesamtreview-Fixwelle hat jeder Traversal-Test eine Opfer-Fixture mit echtem,
  erreichbarem Inhalt UND eine Assertion auf die konkrete Fehlermeldung — nicht nur
  `ok is False`, was auch aus unabhängigen Gründen zutreffen könnte.
- **Tests:** 662 → **671** (+9 netto: 7 aus T1, 1 aus Fix-Runde 1, 1 aus Fix-Runde 2 —
  die 5 in Fix-Runde 2 umgeschriebenen Tests ersetzen bestehende, keine Netto-Änderung
  dadurch).

## Verifikation

Zahlen und Belege: `verification.md` im selben Ordner. Kurzfassung: 671/671 (beide
`pytest tests/ -q` und `-q -W error` nach `__pycache__`-Löschen, Controller-Gegenprobe
unabhängig vom Implementierer-Report), Git-Baum sauber, kein Static-Render betroffen
(reiner Backend-Fix).

## Als nächstes (Sprint 030)

- **`BACKLOG.md` hat nach diesem Sprint genau 1 Eintrag**: **D-062** (`slug_param` in
  `/api/held/<slug_param>/...` ungeprüft gegen Path-Traversal, `state=ready`,
  Effort S) — direkt startbar, kein Blocker. **Priorität jetzt höher begründet** als
  bei seiner Entdeckung: die Sprint-029-Gesamtreview hat es empirisch (nicht nur
  theoretisch) als HTTP-erreichbar bestätigt — `PATCH /api/held/../value` → 200, echtes
  Überschreiben einer `.md`-Datei im Vault-Root. D-061s neuer `_safe_join`-Guard prüft
  nur relativ zu der Basis, die `slug_param` vorgibt — bleibt also wirkungslos, solange
  D-062 offen ist. Fix-Richtung analog zur bestehenden Campaign-Regex
  (`re.fullmatch(r'[a-z0-9_-]+', ...)`), muss aber echte Slug-Formate abdecken
  (Bindestriche, evtl. Ziffern) — kein neuer Design-Entscheidungsbedarf, `/sprint-plan`
  kann direkt schneiden.
- Vault-`backlog.md` bleibt leer — kein B-Task in Sprint 029.
- Falls D-062 allein zu klein für einen ganzen Sprint ist: dieselbe „Bekannte
  Einschränkungen"-Liste wie seit mehreren Sprints (unten) hat weiterhin unbenannte
  Kandidaten.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Zwei Minor-Funde aus der Gesamtreview bewusst nicht gefixt** (nicht dieser
  Sprint-Scope, kein Folge-Ticket nötig — echte Randfälle ohne praktische Relevanz):
  (1) nicht-string `file`-Werte (int/bool/list/dict) lösten schon vor D-061 einen
  `TypeError` aus — unverändertes Verhalten, kein Regressionsrisiko; (2) kein Test für
  `scope='kampagne'` mit komplett fehlendem `campaign`-Schlüssel (nur `'../../x'`
  getestet) — reine Coverage-Lücke, kein Verhaltensrisiko.
- **D-062 (slug_param-Traversal)** — s. oben, jetzt mit stärkerer Priorisierung.
- **Aus Sprint 020–028 unverändert offen** (keine dieser Punkte in Sprint 029
  berührt): echter Druckdialog (Papier-Ausdruck) ungeprüft; D-058-Zeilenhöhen-Zuwachs
  → echter Seitenumbruch-Effekt ungeprüft; Messung nur an einem Charakter
  (illaen-baernhold); Register hängt am Session-Format; echter Browser-Klick gegen
  eine echte Session-Datei nie ausgelöst; inhaltliche Sichtung der vier Sessions;
  Kommando-Mängel von `/session-compile`; Static-Render-Schreibaktionen liefern unter
  `file://` Fake-Erfolg; Tooltips auf Touch; Desktop-Footer ≤ 480 px statisch;
  SF-Vorschau-Randfälle; Zustands-Chips = Hausregel.

## Lehren (Process)

- **Ein defensiver Fix kann selbst einen neuen unbehandelten Exception-Pfad öffnen.**
  `_safe_join` wurde gebaut, um `patch()`/`etag_for()` gegen Crashes von untrustworthy
  Input abzusichern — aber `.resolve()` selbst kann bei bestimmtem Input (Null-Byte)
  eine unbehandelte Exception werfen, wenn man nicht jeden Aufruf innerhalb des neuen
  Helpers genauso absichert wie den, den er ersetzt. Lehre: bei einem neuen
  „fängt-alles"-Helper jeden einzelnen darin aufgerufenen OS-Call auf seine eigene
  Exception-Oberfläche prüfen, nicht nur den offensichtlichen Fehlerfall (hier:
  Traversal-Ausbruch) den der Helper ursprünglich adressieren sollte.
- **Ein Traversal-Test, der nur `ok is False` prüft, kann für den falschen Grund
  bestehen.** 5 von 8 neuen Tests bestanden unverändert auch gegen den ungefixten
  Code, weil die Opfer-Fixture vom hypothetischen ungeschützten Zugriff gar nicht
  sinnvoll erreicht/verändert worden wäre (fehlende Sektion / nicht existente Datei) —
  der Test maß „scheitert aus irgendeinem Grund", nicht „wurde vom Guard geblockt".
  Bestätigt exakt die Sprint-020-Konvention (Mutationsprobe je Assert) an einem neuen
  Fall: bei Security-/Traversal-Tests IMMER (a) eine Opfer-Fixture mit echtem,
  eindeutig erkennbarem Inhalt an der Zielstelle UND (b) eine Assertion auf die
  konkrete Fehlermeldung/das konkrete Fehlerfeld, nicht nur einen Boolean/Status-Code.
- **Die Gesamtreview hat den Produktionsfix selbst re-verifiziert statt nur den Diff zu
  lesen** — Revert in einer Scratch-Kopie + Re-Test aller 4 Vektoren gegen den
  ungefixten Code, inklusive Nachweis eines echten Datei-Überschreibens. Dieses Muster
  (aktiv den Vorher-Zustand reproduzieren statt nur den Nachher-Diff zu lesen) fing den
  einzigen Fund, den beide vorherigen, diff-basierten Reviews verpasst hatten
  (vakuose Tests) — bei künftigen Security-Fixes explizit anfordern.
- **Ein Backlog-Item kann seine Priorität durch die Gesamtreview eines ANDEREN Tasks
  ändern.** D-062 wurde bei D-061s Planung nur theoretisch benannt; erst D-061s
  Gesamtreview maß seine tatsächliche HTTP-Erreichbarkeit (200, echtes Überschreiben).
  Bestätigt erneut die Konvention „Einstufungen sind Hypothesen, bis gemessen" — auch
  für Backlog-Einträge, nicht nur für Implementierer-Behauptungen.

## Process-Notizen

- Briefs/Ledger/Reports liegen unter `.superpowers/sdd/sprint-029/` (gitignored,
  sprint-qualifiziert wie seit Sprint 022/023). Workspace bewusst behalten (Konvention
  seit Sprint 023/025/027/028), nicht gelöscht.
- `sdd-workspace`/`review-package`-Basename-Kollision (`plan.md` in jedem Sprint)
  erneut manuell umgangen — Dateien nach dem jeweiligen Skript-Lauf in den
  sprint-qualifizierten Ordner verschoben.
- Implementierer: Sonnet für T1 (Judgment-lastig — Security-Fix, Windows-Pfadsemantik,
  2 Fix-Runden). Reviews: Sonnet für den Task-Review UND die finale Fixwellen-
  Re-Review (größerer Diff, 5 einzeln geprüfte Tests), Haiku für die schlanke
  Fix-Runde-1-Re-Review (1 mechanischer try/except-Zusatz), Opus für die Gesamtreview.
- Kein Worktree, Commits direkt auf `master` per CLAUDE.md-Workflow, kein Push.
- Gesamtreview-Fixwelle war die einzige (kein zweiter Durchgang nötig, wie im Prozess
  vorgesehen) — beide Funde beim ersten Versuch vollständig adressiert.
- Sprint-Umfang bewusst schlank gehalten (nur D-061) — User-Entscheidung in der
  Sprint-Planung (`AskUserQuestion`, Option „Nur D-061" gewählt statt eines
  zusätzlichen Auffüll-Tasks).

**Nächster Schritt:** `/sprint-wrap` ausführen (BACKLOG.md D-061 → Done, CLAUDE.md
Sprint-Nr. 28 → 29).
