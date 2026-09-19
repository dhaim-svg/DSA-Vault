# Sprint 018 — Zauber-Block: Artikelvorschau + Sortierung im Kompaktlayout

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-018/D-043 → in-progress, plan.md anlegen) | ✅ done | BACKLOG.md, sprints/sprint-018/plan.md |
| T1 | **D-043** Sortierung aus dem Inline-Block nach `static/zauber-sort.js` (IIFE, `JS_FILES`), Bedienelement in beiden Layouts erreichbar, Tastatur/ARIA, 3. Zustand „Standard" | ⬜ todo | templates/dashboard.html.j2, templates/partials/zauber.j2, static/zauber-sort.js (neu), static/base.css, rendering.py, tests/test_rendering.py |
| T2 | **D-018a** Artikel-Loader: `parsers/wikiartikel.py` (Frontmatter ab, Markdown→HTML via mistune, `[[wikilinks]]` → Obsidian-Links, Kopf-Metadaten), `zauber_artikel` als Top-Level-Key in `build_context` | ⬜ todo | parsers/wikiartikel.py (neu), rendering.py, requirements.txt, tests/test_wikiartikel.py (neu), tests/test_rendering.py |
| T3 | **D-018b** Vorschau im Zauber-Tab: `<details class="artikel-details">` je Zauberzeile mit Panel-Kopf (Name, Quelle/Seite, `↗`), Styles inkl. Kompaktlayout ≤ 1070 px und Druckregel | ⬜ todo | templates/partials/zauber.j2, static/base.css, tests/test_rendering.py |
| T4 | Verifikation (pytest inkl. `-W error`, Static-Render + Größe, Browser served **und** `file://`, Domänen-Grenze `abenteuer/`) + Gesamt-Review, danach `/sprint-wrap` | ⬜ todo | — |

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
