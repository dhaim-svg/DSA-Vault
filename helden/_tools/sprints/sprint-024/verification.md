# Sprint 024 — Verifikation

Stand: 2026-09-20, HEAD `fd28413` (8 Commits seit `fd6f593`/T0-Scaffold, lokal, **nicht gepusht**; 32 Commits vor `origin/master` vor dem Wrap-Commit).

## Tests

- `python -m pytest -q -W error` nach Löschen aller `__pycache__`: **586 passed** (Sprint-023-Stand 563: +6 T2, +5 T3, +7 T4, +4 T5, +1 Fix-Runde; Polish ändert nur einen Kommentar). Normaler Lauf ebenfalls grün. `-W error` als pytest-Option (nicht `python -W error`).
- Mutationsproben je neuem Assert-Block in den Task-Reports (`.superpowers/sdd/sprint-024/task-N-report.md`, git-ignoriert): alle Mutanten rot, Dateien per Kopie + Hash byte-genau zurück (nie `git checkout --`). Zusätzlich: T5 zeigte, dass die drei bestehenden Live-Kampf-Wund-Tests bei `{% if false %}` auf der Waffenkarte **grün bleiben** (`0 == 0`, vakuös), die neuen synthetischen Tests dagegen rot werden.
- Live-gekoppelt bleiben bewusst genau zwei Tests: `test_build_context_wiki_artikel_smoke_live_vault` (Ritual-Pfade jetzt zugelassen, keine Werte gepinnt) und `test_held_stabzauber_anchor_links_hit_a_section_of_the_wiki_article` (erfasst ab T1 automatisch auch `#Apport`).

## Static Render

- `render-held.py illaen-baernhold` erfolgreich (exit 0); `output/illaen-baernhold-dashboard.html` **508 457 B** (Sprint 023: 481 641 B), sha256 `a322d4d8…`; 0× `<script src>`, **50×** `class="artikel-details` (40 + 9 Stabzauber + 1 Apport); `git status` nach dem Render sauber.
- **Golden-Vergleich** (Baseline = getrackter Render bei `fd6f593`, `.superpowers/sdd/sprint-024/golden-baseline.html`): außerhalb der Karte „Stabzauber & Rituale“ byte-identisch (T4-Controller-Gegenprobe und Gesamt-Review unabhängig); in der Karte nur 10 Namenslinks + 10 `<details>`-Blöcke; die Karte ohne diese beiden = Baseline-Karte. Die Fix-Runde ändert nur den eingebetteten CSS-Block (4 Zeilen).
- T1–T3 und T5 lassen den Render byte-identisch (sha256 `52ba2885…` = Baseline, je Task vom Controller nachgemessen).

## Browser-Runde (T6, Static über `python -m http.server`, Playwright-MCP, nur lesend)

- Setup: freier Port, sha256 der servierten Datei == Datei auf der Platte (beide Läufe), nur eigene PID beendet, Port danach frei, Arbeitsbaum sauber. Geklickt wurden nur Tab „Zauber“ und die 10 Summaries.
- **Bestanden (1280 und 400 px):** kein Seitenüberlauf; `details.left` liegt in allen 10 Zeilen exakt auf der Textspalte (0,0 px); Sprint-021-Falle: 137 Artikel-`li`, 0× `display:grid`, 0 Rahmen, kleinstes li/body-Verhältnis 0,97 (1280) / 0,92 (400); längster Artikel Zauberspeicher **962 px @1280** (Referenz SF 808 px, Schwelle 1500) und 1829 px @400 (Body 232 px breit); lange Quelle (105 Zeichen) bricht auf 2 Zeilen @1280 / 4 Zeilen @400 um, kein Überlauf, keine Überschneidung mit „↗ Obsidian“; `<summary>` 44 px @400 in 10/10 Zeilen; `.speicher-box` und SF-Karte unbehelligt; Konsole 0 Warnungen (nur 404 auf `/favicon.ico` und den `mtime`-Poll der Static-Seite, vorbestehend).
- **Auffälligkeit → Fix-Runde:** Druck-Emulation (794×1123): Namenslink `.sf-list li .sf-name a` **1,07 : 1** (Soll ≥ 4,5) — eigene Bildschirm-`color` auf dem `<a>` erbte die Druckfarbe von `.sf-name` nicht (D-046-Falle). Für die 10 Ritualzeilen eine **neue Regression** (Namen waren vorher Text), die 15 SF-Links hatten denselben Fehler seit D-050. Fix `8b522e5` (2 Regeln im `@media print`-Block von `tabs.css` + 1 Test). **Nachmessung: 14,62 : 1** für Link und Pfeil (10/10 Ritual-, 15/15 SF-Links), Bildschirmfarbe unverändert (`--ink`, Pfeil `--accent-cold` bei opacity .6); Screenshot `f-print-kraftfokus-nach-fix.png` vom Controller angesehen.
- **Nicht gemessen:** echter Druckdialog (nur Print-Emulation), echter `PATCH`-Pfad, `file://`.
- Vorbestehende Auffälligkeiten, bewusst **nicht** im Sprint (Ruling R9, → D-052): `.meta` 1,95 : 1 und `.vol-badge` 4,12 : 1 im Druck, `.speicher-box` 1,04 : 1 (seit Sprint 005), Druck-Überlauf `docScrollWidth` 881 gegen 779 (Karte „Spontane Modifikationen“, `wirkung-cell`/`mods-details`), Grid-Stretch (bei allen 10 offenen Artikeln ~7 123 px Ritual-Karte, SF-Karte gleich hoch mit Leerfläche).

## Wiki / Repo / Domänen

- `raw/pdf-extracted/_tools/check-frontmatter.py`: 828 Dateien, 682 mit Frontmatter, **0 fehlerhaft**. `wiki/` in diesem Sprint unberührt.
- **Domänen-Grenze:** `git diff --numstat fd6f593 HEAD -- helden/illaen-baernhold abenteuer wiki` = genau `1 1 helden/illaen-baernhold/rituale.md` (Apport-Namenszelle → `[[wiki/dsa-4.1/rituale/stabzauber#Apport\|Apport]]`, einmalige User-Freigabe, Anzeigetext wortgleich, Effekt-Zelle byte-gleich). `load_held(...)['rituale']` vorher/nachher: Diff ausschließlich neue `wiki_path`-Schlüssel (9 Stabzauber-Anker + `…#Apport`).
- Steuerbytes 0x08/0x0C in allen geänderten Dateien: keine. Zeilenenden je Datei wie vorgefunden (`held.py`, `rendering.py`, `zauber.j2`, `tabs.css`, `test_rendering.py`, `output/*.html` CRLF im Working Tree; `test_held.py`, `test_inventar_model.py`, `rituale.md`, Tracker LF); Index durchgängig LF.
- **Reviews:** Task-Reviews T1–T5 (Sonnet) je Spec ✅ / Approved (0 Critical, 0 Important); Re-Review Fix-Runde 1 (Sonnet): ADDRESSED, kein neuer Bruch; Gesamt-Review (Opus): **Ready to merge: Yes**, 0 Critical, 0 Important, 7 Minor (1 inline behoben `fd28413`, Rest deferred/getriaged). Escaping des neuen `href` geprüft: `obsidian_uri` quotet mit `quote(safe='/')`, byte-gleiches Verhalten wie die SF-Links, kein neues Loch. Berichte: `.superpowers/sdd/sprint-024/`.

## Ergebnis-Zusammenfassung je Task

| Task | Commit(s) | Ergebnis |
|------|-----------|----------|
| T0 | `fd6f593` | Scaffold: D-051 als EPIC angelegt, B-024 → In Progress, plan.md |
| T1 | `9b04c9d` | Apport-Namenszelle im Bogen als Anker-Link (User-Freigabe), 1 Zeile |
| T2 | `82a8654` | Parser: `wiki_path` für Stabzauber-/Ritual-Zeilen (nur Namensspalte), 2 Sprint-023-Tests angepasst, +6 Tests |
| T3 | `6fe96a6` | `build_context` lädt die 10 Ritual-Artikel; Live-Smoke erlaubt Ritual-Pfade (R2); +5 Tests |
| T4 | `209cbc9`, Fix `8b522e5` | Template nach SF-Muster (Namenslink + `<details>` als direktes `li`-Kind), Render 40 → 50 Vorschauen, +7 Tests; Fix-Runde: Druck-Kontrast Namenslink 1,07 → 14,62 : 1, +1 Test |
| T5 | `ed0a51a` | B-024: Geld-Integration synthetisch, Kampf-Wund-Hooks mit Waffe synthetisch (nicht-vakuös), `_pos`-Helfer an den zwei benannten Stellen, +4 Tests |
| T6 | — (Messung) | Browser-Runde 1280/400/Druck; Befund → Fix-Runde; Nachmessung bestanden |
| Polish | `fd28413` | Kommentar zur Fixture-Vorbelegung (Final-Review-Minor) |
| T7 | (dieser Commit) | `verification.md`, plan.md-Stand + Rulings R1–R9, Vault-`backlog.md`, D-052 |
