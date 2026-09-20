# Sprint 026 Handoff — Druck-Kontrast der übrigen 7 Tabs (D-053), Gewichts-Tests (B-026)

## Fertig (alle Tasks abgeschlossen)

- ✅ **T0** Scaffold — `3131626`
- ✅ **T1 D-053 Vermessung** (Browser, nur lesend): **37 Gruppen / 495 Elemente** von 1503 Textknoten; **Überlauf 0**
  bei 794/718/615 px. Baseline `screen-baseline.json` (3840 Knoten je Viewport), Screenshots. Kein Commit.
- ✅ **T2 D-053 Fix** — `9cd072c` (37 Gruppen), `d2b1b84` (Pfeil-Bindung), `a24686b` (`.sg-erf` entkleidet),
  Fix-Runden `a41c6ff` (Kaskade + Chronik-Ansichten), `2a4ba34` (`.journal-verlauf`), `6f02095` (`.sg-cart`),
  Fixwelle `c888d62` (cap-warn-Familie + Wächter-Härtung). Alle Re-Reviews ADDRESSED.
- ✅ **T3 Nachmessung**: **BESTANDEN** — 0 Restgruppen, Chronik alle 3 Ansichten 0, Zauber 0/500 unverändert,
  Bildschirm 0 Abweichungen, PDF-Stichprobe. Kein Commit.
- ✅ **T4 B-026** — `a0fbb8a`, Review beim ersten Durchgang sauber.
- ✅ Polish (Controller inline, Re-Review-Minors) — `177f712`
- ✅ **T5** Verifikation, Tracker, dieses Dokument.
- Commits liegen **lokal** auf `master`: **nichts seit Sprint 022 (ab T2) ist gepusht.**

## Was funktioniert

- **Druck aller 8 Tabs ist kontrastseitig sauber** (0 Restgruppen von 1503 Knoten, nachgemessen), Chronik in
  allen drei Ansichten, Zauber-Tab ohne Regression nach der Entpräfixierung.
- **Bildschirm nachweislich unverändert**: 3840 Knoten je Viewport (1280/400 px), 0 Abweichungen; Golden-Diff
  ausschließlich Druck-CSS.
- **Neuer Wächter**: jedes künftige `position:sticky`/`fixed`-Element wird automatisch gegen die
  Druck-Neutralisierung geprüft — dynamisch aus dem CSS abgeleitet, nicht gepinnt, nach Review-Fund gehärtet.
- **Tests:** 615 → **633**, auch mit `-W error`. Gewichtsparsing läuft über den echten `load_held`.

## Verifikation

Zahlen und Belege: `verification.md` im selben Ordner.

## Als nächstes (Sprint 027)

- **D-054** (S–M, ready) — **Vitalwerte fehlen im Ausdruck.** Die Falle steht im BACKLOG: der naheliegende Fix
  druckt auf der servierten Seite einen *veralteten* Wert. Design-Entscheidung nötig.
- **D-055** (S–M, ready) — **Verlaufstext zu 80–89 % abgeschnitten** (`<textarea>` druckt nur den sichtbaren
  Ausschnitt). Im Druck `<pre>`/`<div>` statt `<textarea>`.
- **D-056** (S, ready) — **Getönte Papieroptik druckt weiß.** Entscheiden, ob `print-color-adjust:exact` gesetzt
  wird (dann alle Kontraste gegen `#ece4d0` neu bewerten) oder Weiß der Zielzustand ist.
- **B-027** (S) — redundante Bedingung `parsers/held.py:539`.
- Reihenfolge = Empfehlung. D-055 und D-056 sind unabhängig; D-054 ist der inhaltlich wichtigste
  (ein Charakterbogen ohne LeP/AsP/AuP ist im Spiel unbrauchbar).

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **„D-053 done" heißt Kontrast, nicht Vollständigkeit des Ausdrucks** — siehe D-054/D-055/D-056.
  Diese Unterscheidung steht auch in `plan.md` („Out of Scope", Vorbemerkung) und im BACKLOG-Done-Eintrag.
- **`#tab-profil table *`** (`tabs.css:170`) ist ein Flächenschlag für jede künftige Tabelle in diesem Tab;
  Umbau hätte Regressionsrisiko, verschoben.
- **Rest-Lücke im Wächter:** eine Druck-`!important`-`static`-Regel in einem Ahnenkontext, der gar nicht
  zutrifft (`.gibtsnicht .zz`), zählt weiter als Nachweis (Heuristik statt Spezifitäts-Parser). Auslöser wäre
  eine wirkungslose `!important`-Druckregel — bewusst so belassen.
- **Echter Druckdialog weiterhin ungeprüft.** Die PDF-Stichprobe (`page.pdf()`) ist der bisher nächste Ersatz
  und hat den `.sg-cart`-Fund geliefert; ein echter Druckerausdruck wurde nie gemacht.
- **Messung nur an einem Charakter** (illaen-baernhold). Datenabhängige Zustände (Badges, leeres Register,
  gefüllte Slots) wurden per DOM-Injektion simuliert, nicht aus echten Daten erzeugt.
- **Aus Sprint 017–025 unverändert offen:** Register hängt am Session-Format; `Verlauf`-Speichern nie im Browser
  angeklickt; inhaltliche Sichtung der vier Sessions; Kommando-Mängel von `/session-compile`;
  Static-Render-Schreibaktionen liefern unter `file://` Fake-Erfolg; Sprint-013-Erbe; Tooltips auf Touch;
  Desktop-Footer ≤ 480 px statisch; Footer springt beim Einblenden; SF-Vorschau-Randfälle; Zustands-Chips =
  Hausregel; Grid-Stretch der Ritual-/SF-Karte; Probe-Spalte im Zauber-Tab; echter PATCH-Pfad ungeprüft.

## Lehren (Process)

- **Der Methodenbefund ist die wichtigste Erkenntnis des Sprints:** `page.screenshot()` unter
  `emulateMedia('print')` — seit Sprint 018 die Verifikationsmethode dieses Projekts — **ist nicht der echte
  Druck.** Chromium druckt Hintergründe ohne `print-color-adjust:exact` nicht und dunkelt helle Vordergrundfarben
  im PDF-Pfad ab. Folgen für diesen Sprint: keine (gegen Weiß wird alles besser, per Scan über alle Druckblöcke
  belegt). Folge fürs Verfahren: **Druck-Verifikation braucht zusätzlich `page.pdf()` + Rasterung** — der
  `.sg-cart`-Fund war nur dort sichtbar, weil die Emulation keine Seitenumbrüche auslöst.
- **Ein Messauftrag muss die Persistierung der vollständigen Rohliste verlangen.** T1s Bericht enthielt nur einen
  17-Zeilen-Auszug der 37 Gruppen; der Rest lag in einer Browser-Konsole und war weg. T2 musste neu messen.
- **Ein Zustand ist nicht gemessen, nur weil der Default-Zustand gemessen wurde.** Die Chronik galt als sauber,
  bis alle drei Ansichten geprüft wurden — „Kompiliert" hatte 3 Gruppen.
- **Übernommene Tracker-Zahlen stimmten erneut nicht:** `.journal-readonly` stand mit ~3,3 : 1 im Backlog,
  gemessen 4,282 : 1 (dritter Sprint in Folge mit solchen Korrekturen).
- **Einstufungen von Implementierern sind Hypothesen.** `.journal-verlauf` galt als unkritisch, bis der Reviewer
  1,072 : 1 maß. Der Widerspruch löste sich erst über den PDF-Pfad — beide Beobachtungen waren richtig.
- **Halbe Konsequenz ist ein Mangel:** R6 fixte eine nicht ausgelöste Falle vorsorglich, ließ drei gleichartige
  offen. Der Gesamt-Review hat das zu Recht gerügt; R16 hat alle drei nachgezogen.
- **Der Brief ist eine Fehlerquelle:** die Pfeil-Bindung fiel beim Befüllen aus dem Rahmen heraus und wurde nie
  beauftragt; der Implementierer meldete die Lücke, statt sie eigenmächtig zu schließen — richtig so.
- **Tracker-Umbau per Skript erneut mit Restzeilen** (Abschnitt an `---` ausgerichtet, wie in Sprint 025) —
  sofort per Diff gefunden und repariert. Umbauten immer diffen.
- **Ein Test, der eine Selektor-Schreibweise pinnt, ist kein Wirkungstest.** Der Re-Review fand einen solchen
  Fall, obwohl die Geschwistertests direkt daneben echt rechnen; der Umbau macht ihn scharf (Mutationsprobe
  scheitert jetzt mit dem berechneten 4,282 statt mit „Variable nicht gefunden").

## Process-Notizen

- Briefs/Ledger/Reports unter `.superpowers/sdd/sprint-026/` (git-ignoriert), sprint-qualifiziert wegen der
  `plan.md`-Namenskollision. Reviewer-Verdikt zuoberst, < 3500 Zeichen — kein Bericht abgeschnitten.
- Implementierer/Task-Reviews/Browser Sonnet, Gesamt-Review Opus. T4 lief parallel zur T1-Messung (disjunkt).
- Browser-Agent hielt die Nur-Lesen-Liste ein, Server-PIDs beendet und per `Get-NetTCPConnection` verifiziert,
  `.playwright-mcp/` gelöscht. Zustände nur per DOM/JS simuliert, nie in den Vault geschrieben.
- **Für den nächsten Reviewer-Brief:** ein Re-Reviewer setzte seine Mutationsprobe per `git checkout --` zurück —
  seit Sprint 024 ausgeschlossen (Kopie + Hash). Hier ohne Schaden, gehört aber in den Brief.
- Kein Worktree, Commits direkt auf `master` (R1), kein Push.
