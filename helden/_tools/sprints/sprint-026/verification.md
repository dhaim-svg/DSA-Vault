# Sprint 026 — Verifikation

Stand: HEAD nach Polish-Commit. Alle Zahlen sind gemessen oder nachgerechnet, keine übernommen.

## Test-Suite

- `python -m pytest tests/ -q` aus `helden/_tools/`: **633 passed** (Ausgangsstand Sprint 025: 615).
- Auch mit `-W error` als pytest-Option, nach Löschen aller `__pycache__` (sonst nicht aussagekräftig).
- Zuwachs: +5 T4 (B-026), +13 T2 über fünf Commits (Haupt-Fix, Pfeil-Bindung, Select, Fix-Runden 1–3, Fixwelle).
- **Jeder neue Assert-Block mutationsgeprüft** (Kopie + sha256, nie `git checkout --`). Der Controller hat die
  Polish-Änderung selbst mutationsgeprüft: Mutation von `.register-*` auf `--ink-dim` lässt den umgebauten Test
  mit dem **berechneten** Wert 4,282 scheitern — der vorherige Literalvergleich hätte das nicht gesehen.

## Druck (das Sprintziel)

| Prüfung | Ergebnis |
|---|---|
| Kontrast-Restgruppen, 7 Tabs | **0** von 1503 geprüften Textknoten (T3, gleiche Methode wie T1) |
| Chronik, alle drei Ansichten | Roh 0 / Kompiliert 0 / Register 0 |
| Zauber-Tab (Regression nach Entpräfixierung, R4) | **0/500, unverändert** gegen T1 |
| Bildschirm gegen Baseline | **0 Abweichungen**, je 3840/3840 Knoten bei 1280 px und 400 px |
| Überlauf | **0** bei 794/718/615 px in allen Tabs |
| Echter PDF-Pfad (Stichprobe) | Kontrast einwandfrei; fand zusätzlich den `.sg-cart`-Überlappungsfehler |

Ausgangslage laut Messung: **37 Gruppen / 495 Elemente** (Sollmenge persistiert als
`.superpowers/sdd/sprint-026/task-2-gruppen.md`, 38 Signatur-Zeilen mit Ursprungsregel Datei:Zeile).

## Static Render

- `python render-held.py illaen-baernhold` erfolgreich; `git status` nach dem Render sauber.
- Golden-Diff über alle Fix-Commits: **ausschließlich** Zeilen im eingebetteten Druck-CSS
  (Zeilenenden vor dem Vergleich normalisiert — `git show <commit>:output/…` ist LF, Working Tree CRLF).

## Unberührte Bereiche

- `git diff --numstat 26aeeb6..HEAD -- wiki helden/illaen-baernhold abenteuer` → **leer**.
  Weder Wiki noch User-Domäne wurden angefasst.
- `parsers/held.py` per sha256 vor/nach allen Mutationsproben identisch.

## Reviews

- **T4 (B-026):** Spec ✅ / Approved, 0 Critical, 0 Important — beim ersten Durchgang.
- **T2 (D-053):** Spec ✅ / Approved mit 2 Important → **3 Fix-Runden**, jede mit gescoptem Re-Review,
  alle Funde ADDRESSED.
- **Gesamt-Review (Opus):** *Ready to merge: With fixes* — 0 Critical, 3 Important, 6 Minor.
  Alle Important behoben, Re-Review bestätigt alle als ADDRESSED; die zwei dort neu gefundenen Minors
  (N1 Kommentar, N2 Testname/Wirkung) vom Controller inline behoben.
- Reviewer haben durchgehend **selbst nachgemessen** statt Berichte zu übernehmen — mehrfach mit
  abweichendem Ergebnis (s. u.).

## Was die Verifikation korrigiert hat

- **`.journal-readonly`:** Backlog führte ~3,3 : 1, nachgerechnet **4,282 : 1**.
- **Chronik „sauber":** T1 maß 0 — aber nur im Default-Zustand; „Kompiliert" hatte 3 Gruppen (R10).
- **`.journal-verlauf`:** vom Implementierer als unkritisch eingestuft, vom Reviewer mit **1,072 : 1**
  gemessen → zurück in den Sprint (R11 → R12).
- **Methodenbefund:** `page.screenshot()` unter Print-Emulation ist nicht der echte Druck (Chromium druckt
  Hintergründe ohne `print-color-adjust:exact` nicht). Folgen für die gefixten Gruppen: **keine** —
  gegen echtes Weiß wird jeder verwendete Wert besser; belegt durch Scan über alle `@media print`-Blöcke.
- **`.sg-cart`:** nur im echten PDF sichtbar, in der Emulation nicht (keine Seitenumbrüche).

## Bekannte Grenzen

Gefixt ist der **Kontrast**. Die **Vollständigkeit** des Ausdrucks ist es nicht: keine LeP/AsP/AuP-Zahlen
(**D-054**), Verlaufstext zu 80–89 % abgeschnitten (**D-055**), getönte Papieroptik druckt weiß (**D-056**).
Alle drei sind in `BACKLOG.md` angelegt. Ein echter Druckdialog wurde nie geprüft; die PDF-Stichprobe ist
der bisher nächste Ersatz.
