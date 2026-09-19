# Sprint 018 — Zauber-Block: Artikelvorschau + Sortierung im Kompaktlayout

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-018/D-043 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-018/plan.md |
| T1 | **D-043** Sortierung aus dem Inline-Block nach `static/zauber-sort.js` (IIFE, `JS_FILES`), Bedienelement in beiden Layouts erreichbar, Tastatur/ARIA, 3. Zustand „Standard" | ✅ done | templates/dashboard.html.j2, templates/partials/zauber.j2, static/zauber-sort.js (neu), static/base.css, rendering.py, tests/test_rendering.py |
| T2 | **D-018a** Artikel-Loader: `parsers/wikiartikel.py` (Frontmatter ab, Markdown→HTML via mistune, `[[wikilinks]]` → Obsidian-Links, Kopf-Metadaten), `zauber_artikel` als Top-Level-Key in `build_context` | ✅ done | parsers/wikiartikel.py (neu), rendering.py, requirements.txt, tests/test_wikiartikel.py (neu), tests/test_rendering.py |
| T3 | **D-018b** Vorschau im Zauber-Tab: `<details class="artikel-details">` je Zauberzeile mit Panel-Kopf (Name, Quelle/Seite, `↗`), Styles inkl. Kompaktlayout ≤ 1070 px und Druckregel | ✅ done | templates/partials/zauber.j2, static/base.css, tests/test_rendering.py |
| T4 | Verifikation (pytest inkl. `-W error`, Static-Render + Größe, Browser served **und** `file://`, Domänen-Grenze `abenteuer/`) + Gesamt-Review, danach `/sprint-wrap` | ✅ done (Verifikation + Review; `/sprint-wrap` steht aus) | — |

**Reihenfolge:** T1 → T2 → T3 sequenziell (T1 und T3 fassen beide `zauber.j2`/`base.css` an,
T3 braucht T2s Datenmodell). T2 ist inhaltlich unabhängig von T1, wird aber wegen der
gemeinsamen `rendering.py` nicht parallel gefahren.

## Key Design Decisions

Vom User entschieden (19.09.2026): Scope = D-018 + D-043 · Artikel werden **zur Render-Zeit
eingebettet** (served *und* `file://`) · Vorschau als **native `<details>`-Aufklappzeile** ·
Markdown→HTML mit **mistune**.

- **T1 — der Bug ist der Selektor, nicht die Sortierung.** `.spell:first-child` /
  `.spell:not(:first-child)` (`dashboard.html.j2:158-160`) greift dokumentweit und setzt
  voraus, dass die Kopfzeile sichtbar ist (≤ 1070 px ist sie `display:none`,
  `base.css:399`). Neu: expliziter Hook innerhalb `#tab-zauber` (`[data-spell-list]` für den
  Container, `.spell` für die Zeilen), Bedienung über einen echten `<button>` in einer
  schmalen Toolbar über der Liste, die in **beiden** Layouts sichtbar bleibt
  (`aria-pressed`/`aria-label`, tastaturbedienbar). Der Klick auf die Kopfzeile bleibt als
  Zusatz-Affordanz auf Desktop bestehen. Zustände zyklisch **ZfW ↓ → ZfW ↑ → Standard**; die
  Ursprungsreihenfolge wird beim Laden gemerkt. Kein `sessionStorage` — Ad-hoc-Sicht, keine
  Einstellung.
- **T1 — Inline-Skript raus.** `tests/test_static_js.py:5-7` schließt Inline-Blöcke von der
  Kollisionsprüfung aus; ausgelagert läuft der Code durch IIFE-Zwang und
  Namenskollisionstest (Bug-Klasse D-038). Eintrag in `JS_FILES` (`rendering.py:26`) ist
  Pflicht — `test_rendering.py:214` erzwingt ihn. Der `window.DSA`-Datenblock
  (`dashboard.html.j2:196-235`) bleibt unangetastet.
- **T2 — Einbettung statt Endpoint.** Artikel wird beim Render gelesen und ins HTML
  geschrieben; **kein** neuer Flask-Endpoint, kein `fetch`, kein `file://`-Sonderfall, ein
  Codepfad für served und static. `zauber_artikel` als eigener Top-Level-Key in
  `build_context` (Muster `register`, Sprint 017) — die `held=…`-Test-Stubs bleiben
  unberührt. Pfadquelle ist `z.wiki_path` (`parsers/held.py:77`, z. B.
  `wiki/dsa-4.1/zauber/armatrutz`); gelesen wird `VAULT_ROOT / (wiki_path + '.md')`,
  eingeschränkt auf `wiki/dsa-4.1/` (Pfad-Whitelist nach dem Muster `server.py:49-58`). Fehlt
  die Datei, entsteht kein Eintrag → keine Aufklappzeile, der `↗`-Link bleibt.
- **T2 — mistune, `escape=True`.** mistune 3.2.0 ist importierbar, steht aber nicht in
  `requirements.txt` → `mistune>=3.0` ergänzen. `escape=True` verhindert rohes HTML aus dem
  Wiki — wichtig, weil `make_env()` mit **`autoescape=False`** läuft (`rendering.py:68`).
  Frontmatter vor dem Rendern abtrennen (`parse_frontmatter`, `parsers/held.py:115`,
  wiederverwenden); es liefert die Kopfzeile des Panels (`quelle`/`seite`, `probe`, `kosten`,
  `zauberdauer`, `wirkungsdauer`). H1 und der `> **Quelle:** …`-Blockquote fliegen aus dem
  Body, damit nichts doppelt erscheint. `[[pfad|Text]]`/`[[pfad]]` → `<a href="obsidian://…">`
  über `obsidian_uri()` (`rendering.py:30`); `strip_wikilink` (`held.py:74`) als Referenz.
- **T3 — native `<details>`, kein JavaScript.** Aufklappen, Drucken und `file://` ohne Code.
  Der Würfel-Klick-Guard schließt `e.target.closest('details')` bereits aus
  (`static/dice.js:592`) — ein Klick auf die Vorschau öffnet **kein** Würfelpanel; per Test
  festgenagelt statt vorausgesetzt. Gleiches Muster wie die „Modifikationen"-Details
  (`zauber.j2:32-35`). Kompaktlayout (≤ 1070 px): Block über die volle Zeilenbreite. Druck:
  nur aufgeklappte Artikel (Standardverhalten von `<details>`).
- **T3 — Escaping bleibt manuell.** Einzig das Artikel-HTML geht bewusst roh ins Template;
  Name, Quelle, Seite und Links weiter mit `| e`. Testfall: `<script>` im Artikel-Markdown
  darf nur escaped im Output landen.
- **Größe im Blick:** ~30 Zauber × ~1,2–1,8 KB ≈ +60–90 KB im Static-Render (heute 379 KB).
  Wird in T4 gemessen; liegt der Zuwachs deutlich darüber, in der Handoff festhalten.

## Out of Scope

- **D-041** (Wundregel-/Zustände-Audit, M), **D-044** (Mobile/Touch-Feinschliff, S),
  **D-045** (Chronik-Druck, S) — bleiben im Backlog, Reihenfolge unverändert.
- **Vorschau für Rituale/Stabzauber und Sonderfertigkeiten** — Mechanik übertragbar, D-018
  nennt aber den Zauber-Tab; erst nachziehen, wenn sich das Muster bewährt hat.
- **Popover / CSS Anchor Positioning** (Backlog-Skizze zu D-018) — durch die
  `<details>`-Entscheidung gegenstandslos; kein `@position-try`-Fallback nötig.
- **Volltextsuche über die eingebetteten Artikel**, Wiki-Verlinkung der Register-Namen,
  `.playwright-mcp/`-Gitignore-Zeile und die übrigen offenen Punkte aus dem Sprint-017-Handoff.

## Verifikation

1. `pytest` aus `helden/_tools/` — Baseline **243 grün**, neue Tests additiv, auch mit `-W error`.
2. `python render-held.py illaen-baernhold` → exit 0; Größe von
   `output/illaen-baernhold-dashboard.html` gegen 379 KB vergleichen; Stichprobe: ein
   Artikel-Panel im HTML, `0` `<script src>`, Inline-Sortierblock verschwunden.
3. **Browser served** (Playwright wie in Sprint 017): Artikel aufklappen bei 1280 px und bei
   verifiziertem `innerWidth === 400`; Klick auf das Panel öffnet kein Würfelpanel, Klick auf
   die Zeile daneben weiterhin schon; `↗` zeigt weiter auf `obsidian://`; Sortier-Button in
   beiden Breiten sichtbar und bedienbar (Maus **und** Tastatur), Zyklus ZfW ↓ / ↑ / Standard;
   Konsole ohne neue Fehler.
4. **Static-Render im Browser**: Vorschau und Sortierung funktionieren (Playwright-MCP blockt
   `file:` — über einen lokalen `http.server` auf `output/` prüfen, zusätzlich manuell
   gegenlesen).
5. `git status --short` zeigt **keine** Änderung unter `abenteuer/` oder `wiki/`.
6. Druck-Emulation: aufgeklappte Artikel erscheinen, zugeklappte nicht; Zauberliste intakt.

## Stand am Sprint-Ende

- **T1–T4 fertig, 333/333 Tests** (Baseline 243, `-W error` sauber). Commits ab `dda1dd0`: T1 `a4cfae6`; T2 `c6639a4` + `658b094` (Fallback-Parser); Tracker `68c0895`; T3 `d4d740d`; Static-Render `95cc6a3`; Final-Review-Fixes `51780bf`, `8e82c70`; Tabellen-Fix `bd59ad7` (+ Render). **Nichts gepusht.**
- **Gesamt-Review (Opus): „With fixes"** — 0 Critical, 2 Important (Artikel-Render-Fehler crasht das Dashboard → pro Artikel isoliert; Live-Vault-Test mit strikter Mengengleichheit → entkoppelt), beide sowie zwei empfohlene Einzeiler (Druck: geschlossene Summaries, Label-in-Name am Sortier-Button) direkt vom Controller gefixt (je mit Negativprobe, Suite grün).
- **Browser-Verifikation (Playwright, served + Static über `http.server`):** PASS. 25 Vorschauen; Klick auf Panel/Summary öffnet kein Würfelpanel, Klick auf die Zelle daneben schon; Sortier-Zyklus Standard → ZfW ↓ → ↑ → Standard inkl. Tastatur, Legende bleibt hinter der Liste, offene Vorschau wandert mit; bei verifiziertem 400 px alle 8 Tabs `scrollWidth == clientWidth` (385), alle 25 Artikel offen: −33 px zur Karte (kein Überstand); 1071/1280 px: −9/−33 px; Konsole nur `favicon.ico 404`; nur GET-Requests. Beim Nachmessen fiel eine Regression dieses Sprints auf (erste Tabellenspalte in Artikeln kollabierte bei 400 px, `overflow-wrap:anywhere` geerbt) → `bd59ad7`, im Browser nachgeprüft (27×69 → 40×22 px).
- **Größe:** Static-Render 379 → 434 KB (+55 KB, 25 eingebettete Artikel, ≈ 29 KB Artikel-HTML).
- **Abweichungen von der Planskizze:** (1) Zeilen-Wrapper `[data-spell-list]` (behebt zusätzlich den Bestandsfehler „Legende wandert beim Sortieren nach oben"); (2) `parsers/wikiartikel.py` bekommt `link_fn` injiziert (Zirkelimport); (3) **Fallback-Parser für kaputtes Wiki-Frontmatter** — 103 von 268 Zauberartikeln haben ungültiges YAML (unquotiertes `: ` in `kosten:`/`zauberdauer:`), ohne Fallback hätten 10 von 25 Helden-Zaubern keine Vorschau; Wiki-Reparatur als `wiki-luecken.md` L22 / `backlog.md` B-013 vorgemerkt, danach Fallback entfernen.
- **Für `/sprint-wrap` vormerken:** D-018 + D-043 → Done (Sprint 018). Offene Kleinigkeiten (bewusst nicht in diesem Sprint):
  - Druck: `.spell .nlink`/`.zfw-num` sind auf Papier hell auf hellem Grund (kontrast ≈ 1,1:1, Bestand vor Sprint 018) → zu D-045/Druck-Themen.
  - Zauberliste bei exakt 1071 px: Artikel-Panel (`grid-column:1/-1`) ragt 14 px aus der `.spell`-Box, bleibt in der Karte — derselbe Bestandsüberstand wie die letzte Zelle geschlossener Zeilen (D-040-Breakpoint-Kante); 1072–1130 px nicht durchgemessen.
  - Summary-Tap-Ziel „▸ Artikel" im Kompaktlayout ≈ 18 px (< 44 px) → D-044 (Touch-Feinschliff).
  - Deferred Minors: T1 aria-live/`aria-pressed`, Zeilen-Snapshot beim Laden, stale Testkommentar, formatierungsabhängige Regexe; T2 `ValueError` um `parse_frontmatter` (Fallback nur bei `yaml.YAMLError`), Wikilinks in Code-Spans, Test-Nits; T3 `== 1` auf ersten live `wiki_path`, Guard-Test-Slice.
  - Nicht im Browser gegengeprüft: `file://` direkt (Playwright blockt `file:`) — Static-Render wurde über `http.server` geprüft; die Vorschau braucht kein JS, die Sortierung keine Protokollprüfung.
- **Unverändert offen (Out of Scope):** D-041, D-044, D-045; Vorschau für Rituale/SF; die übrigen Punkte aus dem Sprint-017-Handoff.
