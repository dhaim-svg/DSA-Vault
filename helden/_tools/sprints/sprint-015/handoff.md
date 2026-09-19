# Sprint 015 Handoff — Template-Zerlegung + Chronik-Tab

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-037+D-032 → in-progress, plan.md; D-032-Beschreibung an die Entscheidung „Journal wird eingezogen statt ersetzt" angepasst)
- ✅ T1 (**D-037a**): CSS (1125 Zeilen) aus `dashboard.html.j2` nach `static/{base,tabs,journal,sprachen}.css`. **Wird zur Render-Zeit eingebettet** (`rendering.py::css_bundle()` als Jinja-Env-Global, geordnete Liste `CSS_FILES`), **nicht** per `<link>` — sonst wäre der Static-Render (`output/*.html`, file://) komplett entstylt. Byte-identisch zur Vorher-Ausgabe verifiziert (Server- und Static-Render).
- ✅ T2 (**D-037b**): acht Tab-Bodies nach `templates/partials/<tab>.j2`; `dashboard.html.j2` 2094 → 242 Zeilen. Fund beim Vorab-Scan: der `window.DSA`-Script-Block nutzt `le/ae/au`, die im Kampf-Tab gesetzt wurden — Includes leaken keine Variablen ins Elternteil → die drei `{% set %}` wurden ins Elternteil gehoben. Statische Analyse (`jinja2.meta`) aller Partials: keine weitere Elternteil-Abhängigkeit. Byte-identisch verifiziert.
- ✅ T3 (**D-037c**, Controller inline): `build_context`/`render_dashboard` in `rendering.py` geteilt; behebt die Divergenz, dass der Static-Render `kampagne_slug: ""` lieferte (einziger Unterschied Server↔Static, jetzt keiner mehr).
- ✅ T4 (**D-032a**): `chronik_paths.py` (geteilte Pfad-Konstanten für Import + Parser + Route), `chronik`/`chronik_bild_prefix` im Render-Kontext, Route `GET /chronik-bild/drachenchronik-daten/<datei>` (nur png/jpg/jpeg/gif/webp, kein svg, gewurzelt im Bilder-Ordner selbst — der Implementierer fand per Test, dass `safe_join` ein `x/../y.png` wegnormalisiert und sonst ein Bild außerhalb des Ordners lieferbar gewesen wäre), Parser-Fix „Zeile mit Bild UND Text verliert den Text" (Text-Block, dann `bild`-Block), Render-Level-Smoke-Tests.
- ✅ T5 (**D-032b**): 📜-Chronik-Tab (`partials/chronik.j2`, `static/chronik.css`, `static/chronik.js`): **Roh** (Standard; importierte Spielmitschrift, strikt read-only, neuester Abend offen/ältere `<details>`, IG-Tage, Szenen, Bullets mit Tiefe, Bilder inline, Meta-Sektionen als Karten) + **Kompiliert** (das alte Journal-Markup unverändert, inkl. `Verlauf`-Write-back; `journal.js`/`journal.css` unangetastet). Alle Chronik-Werte per `| e`, Bild-URL zusätzlich `urlencode`. `tabs.js`: gespeicherter Tab `'journal'` → `'chronik'`, unbekannte ID → Default.
- ✅ T6: Verifikation (s. unten) + Final-Review (Opus, Range 2ae5533..f0a0915): „With fixes", 0 Critical → **eine** Fix-Welle (3 Funde, alle behoben, gescopte Re-Review): (1) `<img>`-`src` wird jetzt an beliebiger Attribut-Position/Quote/Schreibweise erkannt, `src`-lose Tags bleiben als Text sichtbar statt lautlos zu verschwinden; (2) `README.md` auf Ist-Zustand (Partials, `CSS_FILES`-Regel, Chronik); (3) geschlossene Chronik-`<details>` werden beim Drucken aufgeklappt (`beforeprint`/`afterprint`).

## Was funktioniert

- Alle Dashboard-Features aus Sprint 013/014 unverändert (Eigenschafts-Leiste, Inline-Werte, Zauberspeicher-Auslöseprobe, Aussehen, Würfel, Steigern, Inventar, Sprachen …) — alle 8 Tabs schalten im Browser um.
- **Chronik-Tab** (📜): siehe T5. Zeigt aktuell 4 Spielabende (04.06., 27.06., 18.07., 22.08.2026), 12 IG-Tage, 5 Meta-Karten, 1 Bild. Frische Daten kommen weiter nur per `python helden/_tools/chronik_import.py` (Einweg-Import aus Drive) — der Tab liest die importierte Kopie.
- Der 📓-Journal-Tab existiert nicht mehr als eigener Tab; er lebt als „Kompiliert"-Ansicht im Chronik-Tab (zeigt bis D-035 nur die Platzhalter-Session `2025-10-04-session-01.md`).
- Neue Struktur (Details in `helden/_tools/README.md`): `dashboard.html.j2` = Gerüst, `templates/partials/*.j2` = Tabs, `static/*.css` (Reihenfolge in `rendering.py::CSS_FILES` ist Kaskaden-relevant; **jede neue CSS-Datei dort eintragen** — ein Test erzwingt es).

## Verifikation

- **Test Suite:** 186/186 bestanden, auch mit `-W error` (Baseline 120 → +66: T1 +5, T2 +4, T4 +34, T5 +17, Fix-Welle +6). Enthält jetzt erstmals **Render-Level-Tests** (Live-Vault-Smoke: ein `<style>`, alle Tab-IDs einmal, `LE: { current: <Zahl>`, Bild-Prefix je Modus) und Route-Sicherheitstests (Traversal, `.md`, `.svg`, Case).
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0), neu committet (getrackte Datei) ✓
- **Byte-Vergleich gegen Golden-Baselines** (vor Sprintbeginn erzeugt, deterministisch): T1, T2, T4 identisch in Server- und Static-Modus; T3 unterscheidet sich nur in der Zeile `kampagne_slug`.
- **Browser-Smoke:** 19/19 Prüfungen (Headless-Chrome per DevTools-Protokoll, weil die Chrome-Extension nicht verbunden war): 8 Tabs, Roh-Ansicht (4 Abende, nur neuester offen, kein „None", keine Schreib-Controls), Bild lädt über die Route, Umschalter + `aria-selected`, Reload-Persistenz, veraltete/unbekannte gespeicherte Tab-IDs, kein horizontales Scrollen bei 400 px, `beforeprint`/`afterprint`, Print-Media, **keine neuen Konsolenfehler**. Screenshots visuell geprüft.
- **Sicherheit:** Bildroute vom Reviewer mit ~30 Angriffsvektoren (Windows/werkzeug) geprüft — keiner entkommt; Escaping-Vollständigkeit im Chronik-Partial geprüft.

## Als nächstes (Sprint 016)

- **D-038** (Bug, S) — **zuerst**: `session.js` wird im Browser nie ausgeführt (s. u.). Betrifft auch den in Sprint 013 gelieferten Zustand-aware Wurf-Modifikator. Kleiner Fix, aber danach bewusst im Browser gegenprüfen.
- **D-035** (`/session-compile` + Aufräumen, M) — jetzt sinnvoll: füllt die „Kompiliert"-Ansicht mit echten Sessions; das Löschen der Platzhalter-Session braucht weiterhin explizite User-Freigabe.
- **D-036** (NSC-/Orts-Register, M) — hängt an D-035.
- **D-018** (Zauber-Inline-Vorschau, L) — unverändert im Backlog; die Zauber-Markup liegt jetzt in `partials/zauber.j2`.

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **⚠ Altbug, NICHT aus diesem Sprint (→ D-038):** `static/app.js:7` und `static/session.js:9` deklarieren beide top-level `const IS_SERVED` → `session.js` bricht beim Parsen ab, `window.DSASession` ist `undefined`. Zustände-Chips, Wunden-Overlay und der Zustand-aware Wurf-Modifikator (`dice.js:205`, guarded → lautlos wirkungslos) laufen im Browser nicht. Seit Mai 2026 vorhanden; Sprint 015 hat beide Dateien nicht berührt. Nicht gefixt (Scope: würde bisher tote Codepfade aufwecken).
- **`Verlauf`-Speichern (Kompiliert-Ansicht) im Browser nicht angeklickt** — schreibt in `abenteuer/` (User-Domäne). Abgesichert nur indirekt: Markup, `journal.js` und `journal.css` sind unverändert (Reviews von T2/T5), der Save-Button ist im DOM vorhanden. Beim ersten echten Speichern kurz gegenprüfen.
- **Chronik-Meta-Sektionen** werden als Rohtext angezeigt (kein Markdown-Rendering, Links nicht klickbar).
- **Static-Render:** Bilder zeigen relativ auf `../abenteuer/drachenchronik/…` (funktioniert nur, solange `output/` im Vault liegt); die Tab-Umschaltung im Static-Render war schon vorher inaktiv (Skripte laden per `file://` nicht).
- **Leerer IG-Tag** (Überschrift ohne Inhalt) wird vom Parser weiterhin verworfen — bleibt Design-Frage (aus Sprint 014).
- Aus Sprint 014 weiterhin offen: `chronik_import.py` ohne Schutz gegen leeren/kurzen Quell-Read; Bild-Änderungserkennung nur per mtime. (Erledigt in diesem Sprint: „Bullet mit Bild UND Text" und die geteilte Pfad-Konstante.)
- Zurückgestellte Minors aus den Reviews (alle nicht blockierend): `tabs.css` heißt irreführend (enthält Print-Layout); Überschriften-Ebenen im Chronik-Partial springen (h2→h4/h5); `role="tab"`-Umschalter ohne Pfeiltasten; kurzes Aufblitzen der Standardansicht beim Reload (Restore erst bei `DOMContentLoaded`, wie `tabs.js`); „0 IG-Tage" bei einem Abend ohne IG-Tage; Bildroute: trailing Slash liefert 200, Präfix-Prüfung case-sensitiv; kein `tests/conftest.py` (jede neue Testdatei muss `sys.path.insert(TOOLS_DIR)` selbst wiederholen); Live-Vault-Tests koppeln an Held-/Chronik-Daten (Bild-Dateiname, numerisches LE); Shared-Constants-Test near-tautologisch; kein `&`-Roundtrip-Test; CSS-Politur.
- Kosmetik-Altbestand: bei 400 px überlappen Banner-Titel und die feste Fußleiste (nicht Sprint 015).
- Hinweis zu Sprint-014-Zahlen: das Handoff nannte „13 IG-Tage" — die tatsächliche Zählung der echten Chronik ist 12 (vor und nach den Parser-Änderungen identisch).
- Vererbte Einschränkungen aus Sprint 013 (Kampf-Header-Wortlaut, AT/PA ohne Wund-Overlay, `.talent-row`-Grid-Raggedness, Portrait-Plumbing inert, weitere Tests gegen Live-Vault-Datei, Python/JS-Würfel-Mathe-Mirror ohne Drift-Check) bleiben offen — die Erkenntnis zu D-038 verschärft den letzten Punkt: die JS-Seite der Würfelmathe wird von keinem Test ausgeführt.
