# Sprint 026 — Druck-Kontrast-Sweep der übrigen 7 Tabs (D-053) + Test-Replik Gewicht (B-026)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`BACKLOG.md` D-053 → in-progress, Vault-`backlog.md` B-026 → in-progress, `plan.md` anlegen) | ⬜ todo | `helden/_tools/BACKLOG.md`, `backlog.md`, `sprints/sprint-026/plan.md` |
| T1 | **D-053 Vermessung** (Browser, nur lesend): Print-Emulation über Static-`http.server` bei 794/718/615 px; je Tab (`profil`, `talente`, `kampf`, `steigern`, `inventar`, `sprachen`, `chronik`) WCAG-Sweep über alle Elemente mit eigenem Text, Gruppen nach Selektor-Signatur **mit Ursprungsregel Datei:Zeile**, dazu `docScrollWidth` je Tab und Bildschirm-Baseline als JSON. Kein Commit, keine Repo-Spuren | ✅ done (kein Commit) | — (Messbericht unter `.superpowers/sdd/sprint-026/`) |
| T2 | **D-053 Fix**: `@media print` in `static/tabs.css` (+ `base.css` / `chronik.css`, wo die Ursprungsregel liegt) — alle in T1 gemessenen Gruppen auf `var(--paper-ink)`; bekannte Anhaltspunkte `.card-title .meta` / `.card > h4` (1,59–1,95 : 1), AP-Zahlen der Zeile „AP & Steigerung", `.journal-readonly` (~3,3 : 1, Altbestand seit Sprint 017). Zusätzlich Pfeil ↗ des Namenslinks per geschütztem Leerzeichen an den Namen binden. Tests im Druckblock von `test_rendering.py` | ⬜ todo | `static/tabs.css`, ggf. `static/base.css`, `static/chronik.css`, Template der Namenszelle, `tests/test_rendering.py` |
| T3 | **Browser-Nachmessung** im selben Agenten-Kontext (`SendMessage` an T1): 0 Kontrast-Restgruppen über alle 7 Tabs, `docScrollWidth` unverändert oder besser, Bildschirm-Gegenprobe 0 Abweichungen gegen die T1-Baseline | ⬜ todo | — |
| T4 | **B-026**: `tests/test_inventar_model.py::test_inventar_gewicht` auf `load_held(write_mini_held(tmp_path, ausruestung=…))` umstellen (Tabelle mit Gewicht in Unzen, `—`/leer → 0, Summe `inventar_gewicht_unzen`); Replik der Schleife aus `parsers/held.py:534–540` streichen; Mutationsprobe am Parser | ✅ done (`a0fbb8a`; 618 Tests, Review clean) | `tests/test_inventar_model.py`, ggf. `tests/heldfixtures.py` |
| T5 | Verifikation + `/sprint-wrap` | ⬜ todo | `sprints/sprint-026/verification.md`, `handoff.md`, Tracker |

## Key Design Decisions

- **Messen vor Fixen.** D-052 hat in Sprint 025 die Backlog-Zuordnung widerlegt (Überlauf kam aus dem `.spell`-Grid, nicht aus „Spontane Modifikationen"; 20 Kontrast-Gruppen statt der 3 bekannten Werte). T2 wird erst nach den T1-Zahlen geschnitten; die im BACKLOG genannten Werte sind Anhaltspunkte, keine Sollmenge.
- **Ursprungsregel je Verstoß belegen.** Ein Kind mit eigener Bildschirm-`color` erbt das `!important` des Elterns nicht, und Inline-Styles schlägt nur `!important` mit passendem Selektor. Jede gemessene Gruppe bekommt in T1 Datei:Zeile der verursachenden Regel — kein Raten in T2.
- **Zauber-Tab bleibt unangetastet.** Die vier `#tab-zauber`-präfixierten Selektoren des D-052-Fixes (`tabs.css:105–110`) werden nicht verallgemeinert; andere Tabs bekommen eigene Regeln, damit der in Sprint 025 vermessene Zustand nicht unbemerkt kippt.
- **Bildschirm darf sich nicht ändern.** Golden-Render-Vergleich (LF-normalisiert, `git show <commit>:output/…` ist LF, Working Tree CRLF) plus Bildschirm-Gegenprobe im Browser gegen die T1-Baseline.
- **Chronik ist im Sweep** (User-Entscheidung): eigener Print-Block `chronik.css:68` und D-045-Drucklogik werden mitgemessen und mitgefixt, inkl. des alten `.journal-readonly`-Werts.
- **Überlauf wird gemessen, aber nur nach Befund gefixt** (User-Entscheidung): zeigt sich ein Überlauf, entscheidet die gemessene Zahl, ob der Fix in T2 passt oder als eigener EPIC ins BACKLOG geht. Grid-Umbauten waren im Zauber-Tab ein eigener Task.
- **Browser nur lesend**, Static über `python -m http.server --directory output` auf freiem Port, `sha256` der servierten Datei prüfen, eigene PID am Ende beenden, `.playwright-mcp/` löschen. Der Controller sieht die Screenshots selbst an (Sprint-024/025-Lehre: der Nebenbefund der unsichtbaren AP-Zahlen stand nur im Bild).
- **Kein Worktree**, Commits direkt auf `master`, kein Push (wie Sprint 023–025, CLAUDE.md-Workflow).
- **Reviews:** zwei-stufig (Spec + Code Quality) je Feature-Task; Verdikt-Zeile zuoberst, Bericht < 3500 Zeichen, Vollbericht in Datei unter `.superpowers/sdd/sprint-026/`.

## Out of Scope

- **Probe-Spalte im Zauber-Tab** (bricht in 25/25 Zeilen zweizeilig, Spalte schmaler/einzeilig) — würde das in Sprint 025 frisch vermessene Druck-Grid erneut verschieben; geht als eigener S-EPIC ins `BACKLOG.md`. *(Die Pfeil-Bindung ↗ ist dagegen in T2 enthalten — 5 von 25 Namen @ 703 px.)*
- **Echter Druckdialog / PDF**: die Print-Emulation kennt `@page`-Ränder nicht, die echte Seitenbreite (≈ 703 px) wird über einen 718-px-Viewport nachgestellt. Unverändert offen seit Sprint 020.
- **Gefüllte Zauberspeicher-Slots im Druck**: im Ist-Render alle 3 leer, die Slot-Klassen sind nur vorsorglich abgedeckt (Sprint 025).
- **Grid-Stretch der Ritual-/SF-Karte**, **echter PATCH-Pfad im Browser**, **Footer-Transition beim Einblenden** — Kandidaten ohne EPIC, bleiben unberührt.
- **Wiki- und User-Domäne** (`wiki/`, `helden/illaen-baernhold/`, `abenteuer/`) werden nicht angefasst; Beleg in `verification.md` per `git diff --numstat`.

## Rulings

- **R1** — Kein Worktree; Commits direkt auf `master` (CLAUDE.md-Workflow, wie Sprint 023–025).
- **R2** — Die Pfeil-Bindung ↗ passiert per `content:"\00a0↗"` im `@media print`-Block, **nicht im Template**: der Pfeil ist ein CSS-`::after` (`base.css:400`, `base.css:637`) und steht im Template gar nicht. Die Plan-Zeile „Template der Namenszelle" in T2 ist damit gegenstandslos. Druckblock statt `base.css`, damit der Bildschirm unverändert bleibt.
- **R3** — `.journal-readonly` liegt in `static/journal.css:7` (Datei **ohne** `@media print`-Block), nicht in `chronik.css` wie im Plan vermutet. Gefixt wird, wo T1 die Ursprungsregel misst.
- **R4** — T2 darf die `#tab-zauber`-Präfixe (`tabs.css:109/110`) entfernen, wenn T1 belegt, dass dieselben Klassen in allen Tabs denselben Fix brauchen. Bedingung: T3 misst den Zauber-Tab gegen die Sprint-025-Werte nach (0 Regressionen).
- **R5** — T4 (B-026) lief parallel zu T1 (nur lesende Messung); disjunkte Dateien, beide Commits pfadbegrenzt.

- **R6** — `kampf.j2:93-94` (dieselbe Inline-Style-Falle wie `profil.j2:84-93`, von diesem Charakter-Datensatz nicht ausgelöst, per Grep gefunden) wird in T2 vorsorglich mitgefixt und im CSS als *ungemessen* gekennzeichnet.
- **R7** — `<select>`-Dropdowns in `#tab-steigern` (drucken als schwarze Kästen) werden im Druck ausgeblendet; Präzedenz ist der Sprint-025-Fix für die Slot-Bedienelemente (`tabs.css:117`).
- **R8** — Die im Druck vollständig fehlenden LeP/AsP/AuP-Zahlen sind **nicht** Teil dieses Sprints → neuer EPIC **D-054**. Begründung unter „Funde für das Backlog".
- **R9 (ersetzt R7)** — `.sg-erf` wird im Druck **nicht ausgeblendet, sondern entkleidet** (`appearance:none`, transparenter Grund, `paper-ink`). Grund: der Implementierer belegte per Grep, dass die gewählte Erfahrungsstufe **nirgendwo sonst** im Ausdruck steht; der schwarze Kasten kam aus der Bildschirm-Optik, nicht daraus, dass `<select>` unbedruckbar wäre. Gemessen: alle drei Zustände 14,62 : 1.
- **R10** — Die Chronik gilt **nicht** als gemessen, nur weil T1 im Default-Zustand 0 Verstöße fand: seit D-045 druckt die **aktive** Ansicht. Fix-Runde 1 maß alle drei Ansichten — „Kompiliert" hatte **3 versteckte Gruppen** (1,95 : 1 und 4,28 : 1).
- **R11 → R12 (zurückgenommen)** — `.journal-verlauf` wurde zunächst als reiner Kosmetikfall ausgelagert („dunkler Kasten, kein Kontrastverstoß"). Die unabhängige Messung des Re-Reviewers ergab **1,072 : 1** und widerlegte die Einstufung → zurück in den Sprint und gefixt (**18,52 : 1** gegen den echten weißen Druckgrund).
- **R13** — Das `<textarea>` druckt nur ~11–20 % seines Inhalts (clientHeight 140 px gegen scrollHeight 716–1244 px, **80–89 % des Verlaufstexts fehlen**). Braucht eine Design-Entscheidung (im Druck `<pre>` statt `<textarea>`) → eigener EPIC **D-055**.
- **R14** — Die Konvention „Papier #ece4d0" setzt einen gedruckten Hintergrund voraus, den es ohne `print-color-adjust:exact` nicht gibt; der echte Ausdruck wird weiß statt getönt. Kein Defekt (Kontrast wird dadurch nur besser) → Design-Frage, eigener EPIC **D-056**.
- **R15** — `.sg-cart` überdeckte bei der echten PDF-Paginierung eine Tabellenzeile und druckte als schwarze Leiste. **Im Sprint gefixt**, obwohl kein Kontrastfall: ein Bedienelement, das im Ausdruck Inhalt verdeckt, trifft das Sprintziel, und der Fix ist ein Eintrag in eine bereits gepflegte Ausschlussliste — nicht der Design-Aufwand, der D-054/D-055/D-056 nach draußen verwies.

## Methodenbefund (sprintübergreifend)

**`page.screenshot()` unter `emulateMedia('print')` ist nicht der echte Druck.** Chromium druckt farbige Hintergründe standardmäßig nicht (kein `print-color-adjust:exact` im Projekt) und dunkelt helle Vordergrundfarben im PDF-Pfad zusätzlich ab. Belegt durch isolierte Testseite → `page.pdf()` (Default `printBackground:false`) → `pdftoppm`, von Implementierer und Reviewer unabhängig reproduziert.

- **Folgen für diesen Sprint: keine.** Gegen echtes Weiß wird jede verwendete Farbe besser (`--paper-ink` 18,52 statt 14,62 : 1, `--paper-rule` 4,32 statt 3,41 : 1); ein Scan über **alle** `@media print`-Blöcke fand keinen `background:`-Wert außer `transparent`/`none`/`var(--paper…)`. Keine gefixte Gruppe trägt ihren Kontrast über einen gemalten Hintergrund.
- **Folge fürs Verfahren:** Druck-Verifikation braucht zusätzlich den echten PDF-Pfad. Der `.sg-cart`-Fund (R15) war **nur** dort sichtbar — die Emulation löst keine Seitenumbrüche aus.

## T1-Messergebnis (bestimmt den T2-Zuschnitt)

- **37 Kontrast-Gruppen / 495 Elemente** von 1503 geprüften Textknoten: steigern 10, inventar 10, profil 9, sprachen 6, talente 3, kampf 1, chronik 0. **Zauber-Tab 0** — der Sprint-025-Fix hält und dient als Regressions-Baseline.
- **Überlauf: 0** bei 794/718/615 px in allen Tabs (`scrollWidth` = `innerWidth`). Die D-052-Grid-Ursache war zauber-spezifisch; die Plan-Option „Überlauf nach Befund fixen" entfällt damit ersatzlos.
- Schlimmster Bereich: `steigern.j2` (Steigerungstabelle), nahezu aller Text bei ~1 : 1.

## Funde für das Backlog

- **D-055 (neu, Dashboard, S–M)** — **Der Verlaufstext wird im Ausdruck zu 80–89 % abgeschnitten.** Das `<textarea>` `.journal-verlauf` druckt nur seinen sichtbaren Ausschnitt: über alle 4 Sessions gemessen clientHeight 140 px gegen scrollHeight 716–1244 px, also 30–58 von 39–67 Zeilen je Session fehlen. Behebung verlangt eine Design-Entscheidung (im Druck `<pre>`/`<div>` statt `<textarea>` rendern) mit eigener Verifikation. Gefunden in Sprint-026-Fix-Runde 2 beim Kontrastfix desselben Elements.
- **D-056 (neu, Dashboard, S)** — **Die getönte Papieroptik erscheint im echten Ausdruck weiß.** Die Konvention „Papier #ece4d0" aus Sprint 025/026 setzt einen gedruckten Hintergrund voraus; ohne `print-color-adjust:exact` (projektweit nirgends gesetzt) druckt Chromium Hintergründe bei Standardeinstellungen nicht. **Kein Defekt** — der Kontrast wird gegen Weiß durchweg besser —, sondern die Frage, ob die Optik so gewollt ist oder `print-color-adjust` gesetzt werden soll. Siehe Methodenbefund oben.
- **D-054 (neu, Dashboard, S–M)** — **Die LeP/AsP/AuP-Zahlen fehlen im Ausdruck vollständig.** `tabs.css:275` setzt `.vital::after { content: attr(data-current) " / " attr(data-max) }`, aber `data-max` steht am verschachtelten `.vital-stepper` (`kampf.j2:21/35/49`) und **`data-current` existiert projektweit nicht** (Grep über `static/*.js`: kein Schreiber); `tabs.css:273` blendet den Stepper im Druck zusätzlich aus. Der Ausdruck zeigt Balken ohne Zahlen — das hat nie funktioniert. **Warum nicht in Sprint 026:** der naheliegende Fix (Attribute auf `.vital` ausgeben) druckt auf der *servierten* Seite einen veralteten Wert, weil `.vital-input` live editierbar ist und nichts `data-current` nachführt; eine falsche Zahl auf dem Charakterbogen ist schlechter als eine fehlende. Braucht eigenes Design (wer führt den Wert nach — JS, oder druckt der Druck das Eingabefeld?) und eigene Verifikation. Gefunden in T1, nur im Screenshot sichtbar.
- `parsers/held.py:539` — die Bedingung `gew_raw.strip() not in ('—','','-')` ist gegenüber `safe_int` (`held.py:171–177`) redundant; `safe_int` bildet alle drei Werte selbst auf 0 ab. Von Implementierer **und** Reviewer unabhängig nachgerechnet (T4). Kein Verhaltensfehler — Cleanup-Kandidat.
