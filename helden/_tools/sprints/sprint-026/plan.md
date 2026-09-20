# Sprint 026 — Druck-Kontrast-Sweep der übrigen 7 Tabs (D-053) + Test-Replik Gewicht (B-026)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`BACKLOG.md` D-053 → in-progress, Vault-`backlog.md` B-026 → in-progress, `plan.md` anlegen) | ⬜ todo | `helden/_tools/BACKLOG.md`, `backlog.md`, `sprints/sprint-026/plan.md` |
| T1 | **D-053 Vermessung** (Browser, nur lesend): Print-Emulation über Static-`http.server` bei 794/718/615 px; je Tab (`profil`, `talente`, `kampf`, `steigern`, `inventar`, `sprachen`, `chronik`) WCAG-Sweep über alle Elemente mit eigenem Text, Gruppen nach Selektor-Signatur **mit Ursprungsregel Datei:Zeile**, dazu `docScrollWidth` je Tab und Bildschirm-Baseline als JSON. Kein Commit, keine Repo-Spuren | ⬜ todo | — (Messbericht unter `.superpowers/sdd/sprint-026/`) |
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

## Funde für das Backlog

- `parsers/held.py:539` — die Bedingung `gew_raw.strip() not in ('—','','-')` ist gegenüber `safe_int` (`held.py:171–177`) redundant; `safe_int` bildet alle drei Werte selbst auf 0 ab. Von Implementierer **und** Reviewer unabhängig nachgerechnet (T4). Kein Verhaltensfehler — Cleanup-Kandidat.
