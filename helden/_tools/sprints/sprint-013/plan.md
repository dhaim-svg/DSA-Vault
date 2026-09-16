# Sprint 013 — Bug-Reste aus vier Spielabenden (Eig-Werte, Stabzauber-Aktivierung, Aussehen)

## Ausgangslage

Nutzer hat vier Spielabende (04.06., 27.06., 18.07., 22.08.2026) mit dem
Dashboard gespielt. Drei Notizen aus der Spielmitschrift wurden zwar in
Sprint 012 als D-022/023/024 "erledigt", lassen aber jeweils einen echten
Rest offen — das ist der Ursprung dieses Sprints. Details, Quellen und
Zeilenverweise siehe `C:\Users\David\.claude\plans\ich-habe-jetzt-die-mellow-beaver.md`.

Abweichung von Sprint-012-Handoff-Empfehlung: dort wurde D-018 als nächstes
vorgeschlagen ("Reihenfolge = Empfehlung, nicht Pflicht"). Nutzer hat diesen
Sprint-Scope explizit freigegeben (Plan-Mode-Approval) — D-018 bleibt im
Backlog.

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (BACKLOG.md D-025…D-029 → in-progress, D-019…D-024-Beschreibungsblöcke bereinigen, plan.md anlegen) | ⬜ todo | BACKLOG.md, sprints/sprint-013/plan.md |
| T1 | **D-025** Eigenschafts-Leiste über Talente-/Zauber-Tab | ⬜ todo | templates/dashboard.html.j2, static/session.js |
| T2 | **D-026** Inline-Eigenschaftswerte vervollständigen (Kampftechniken, Spontane Mods, Wunden-/Zustandsabzug sichtbar) | ⬜ todo | templates/dashboard.html.j2 |
| T3 | **D-027** Zauberspeicher-Auslöseprobe (MU/IN/KL, +1 Erschwernis/Slot) | ⬜ todo | templates/dashboard.html.j2, static/dice.js, static/zauberspeicher.js |
| T4 | **D-028** Erschaffungsprobe je Stabzauber | ⬜ todo | helden/illaen-baernhold/rituale.md, parsers/held.py, templates/dashboard.html.j2 |
| T5 | **D-029** Aussehen vervollständigen (Augenfarbe/Größe/Statur/Gewicht-Felder, "offen"-Markierung) | ⬜ todo | helden/illaen-baernhold/_illaen.md, templates/dashboard.html.j2 |
| T6 | **W-001** Wiki-Widerspruch Stabzauber-Aktivierung klären (kein Dashboard-Task, kein Subagent-Feature-Task) | ⬜ todo | wiki/dsa-4.1/rituale/stabzauber.md, wiki/dsa-4.1/rituale/rituale-grundregeln.md, wiki-luecken.md |
| T7 | Verifikation + `/sprint-wrap` | ⬜ todo | — |

## Key Design Decisions

- **D-025/D-026 nutzen denselben JS-Hook**: die Eigenschafts-Leiste (T1) und
  der Wund-/Zustandsabzug in Proben (T2) hängen beide von den aktiven
  Zuständen aus `session.js` (`localStorage dsa:<slug>:session`) ab. Ein
  gemeinsamer Update-Callback nach `renderZustandChips()`, nicht zwei
  getrennte.
- **D-026 Probe-Spalte**: die feste `150px` aus D-023 wird zum Bottleneck,
  sobald AT/PA-Werte + Wundabzug dazukommen. Umstellung auf `minmax()` statt
  fixer Breite (siehe bekannte Einschränkung aus Sprint-012-Handoff).
- **D-027 bindet an bestehenden Würfler statt Duplikat**: `dice.js` bindet
  Klick-Handler heute nur auf `.talent-row[data-probe]` / `.spell[data-probe]`
  — Selektor erweitern, keine zweite Würfellogik einführen.
- **D-028 ist reine Nachschlage-Info**: Erschaffungsprobe kommt aus
  `wiki/dsa-4.1/rituale/stabzauber.md`, wird 1:1 in `rituale.md` übernommen.
  Ändert nichts an der Aktivierung selbst (die bleibt laut D-024 freie
  Aktion) — Abgrenzung zu T3 im Task-Briefing klarstellen, damit kein
  Subagent versehentlich eine Aktivierungsprobe pro Stabzauber einführt.
  T6 (Wiki-Klärung) kann die Werte in `stabzauber.md` noch vor T4 korrigieren
  — Reihenfolge daher T6 vor T4 in der Ausführung, auch wenn in der Tabelle
  danach gelistet.
- **D-029 erfindet keine Werte**: Größe/Statur/Gewicht/exakte Augenfarbe
  bleiben leer bis der Nutzer sie einträgt (Sprint-012-Präzedenzfall). Neu
  ist nur die visuelle "offen"-Markierung statt stillem `—`.
- **T6 kein Subagent-Feature-Task**: Wiki-Pflege ist LLM-Bibliothekars-Domäne
  (kein Held/Dashboard-Scope), läuft daher direkt in der Hauptsession statt
  über Subagent-Driven-Development mit zweistufiger Review.

## Ausführungsreihenfolge (abweichend von Tabellennummerierung)

T0 → **T6 (Wiki zuerst)** → T4 (braucht ggf. korrigierte Werte aus T6) →
T1 → T2 → T3 → T5 → T7

## Task Details (exakte Werte, nach T0+T6-Recherche)

### T4 — D-028 Erschaffungsprobe je Stabzauber

**Wiki-Werte** (aus `wiki/dsa-4.1/rituale/stabzauber.md`, verifiziert gegen WdZ S. 108-110 im Rahmen von W-001):

| Illaens Stabzauber (Name in `rituale.md`) | Erschaffungsprobe | AsP |
|---|---|---|
| Stabzauber: Bindung | KL / CH / FF (+3) | 22 |
| Stabzauber: Fackel | KL / KL / FF (+4) | 23 |
| Stabzauber: Hammer des Magus | MU / CH / KK (+6) | 27 |
| Stabzauber: Kraftfokus | KL / IN / CH (+7) | 27 |
| Stabzauber: Merkmalsfokus | KL / IN / IN (+9) | 23 |
| Stabzauber: Modifikationsfokus | KL / KL / IN (+9) | 27 |
| Stabzauber: Seil (des Adepten) | KL / IN / GE (+5) | 21 |
| Stabzauber: Zauberspeicher | KL / KL / IN (+11) | 31 |
| Stabzauber: Stabverlängerung | **unklar** — siehe unten | — |

**Stabverlängerung-Ausnahme:** Kein Stabzauber dieses Namens existiert im Wiki-Artikel. Funktional deckungsgleich mit „Doppeltes Maß" (KL/FF/GE (+4), 19 AsP — „Zauberstab kann auf das Doppelte seiner Länge anwachsen"), aber **nicht umbenennen** — `helden/` ist User-Domäne. Stattdessen: Erschaffungsprobe/AsP-Zellen für diese Zeile leer/„?" lassen und eine Fußnote im selben Stil wie die bestehende Z.30-Fußnote („Hinweis: Im Heldendokument...") ergänzen, die auf die vermutete Identität mit „Doppeltes Maß" hinweist — Formulierung als Vermutung, nicht als Fakt.

**Implementierung:**
- `helden/illaen-baernhold/rituale.md:18-19` — Tabellenkopf um zwei Spalten erweitern: `| Stabzauber | Erschaffungsprobe | AsP | Vol | Effekt (Kurzform) |`, Werte aus obiger Tabelle einsetzen.
- `parsers/held.py:390-394` — im `stabzauber.append({...})`-Dict zwei neue Keys ergänzen: `'erschaffungsprobe': row.get('Erschaffungsprobe', '')`, `'asp': row.get('AsP', '')`.
- `dashboard.html.j2:1456` — in der `<li>` für jeden Stabzauber die neuen Felder neben dem `vol-badge` anzeigen (z.B. als kleine `<span class="meta">` mit Probe + AsP), `| e`-escaped, nur rendern wenn vorhanden (`{% if r.erschaffungsprobe %}`).
- Tests: `tests/test_held_writer.py` oder neuer Parser-Test verifiziert, dass `held.rituale.stabzauber[i]['erschaffungsprobe']` und `['asp']` korrekt aus der erweiterten Tabelle gelesen werden (Fixture mit den neuen Spalten).

### T1 — D-025 Eigenschafts-Leiste

- Neues Jinja-Macro `eig_leiste(eig, basis)` direkt nach `probe_eig` in `dashboard.html.j2` (aktuell endet bei `:1127` mit `{%- endmacro -%}`).
- Rendert eine Zeile: `MU {{eig.MU.aktuell}} · KL {{eig.KL.aktuell}} · IN {{eig.IN.aktuell}} · CH {{eig.CH.aktuell}} · FF {{eig.FF.aktuell}} · GE {{eig.GE.aktuell}} · KO {{eig.KO.aktuell}} · KK {{eig.KK.aktuell}}` gefolgt von `LE {{basis.LE.akt}} · AE {{basis.AE.akt}} · MR {{basis.MR.akt}}` (exakte Feldnamen in `held.eigenschaften`/`held.basiswerte` vor dem Schreiben mit `parsers/held.py:194-210` gegenprüfen — Feldnamen dort verbindlich, nicht raten).
- Aufruf am Anfang von `#tab-talente` (`:1327` Bereich) und `#tab-zauber` (`:1368` Bereich), jeweils direkt nach dem öffnenden `<div>`.
- CSS: `position: sticky; top: 0; z-index: 5;` (über der Tab-Content-Scrollregion), eine Zeile hoch, `--mono`-Font, Hintergrund `--bg-inset` o.ä. damit sie beim Scrollen nicht durchsichtig wird.
- JS-Hook: neue exportierte Funktion in `static/session.js` (z.B. `updateEigLeisteBadge()`), aufgerufen aus `renderZustandChips()` nach jedem Toggle — schreibt aktive Mali als Badge-Text in ein `<span id="eig-leiste-mods">` neben der Leiste. Kein Award für D-026-Vorwegnahme: Badge zeigt nur *dass* ein Malus aktiv ist (z.B. „−2 Schmerz"), nicht die verschobenen Einzelwerte — das ist T2.

### T2 — D-026 Inline-Eigenschaftswerte vervollständigen

- `probe_eig`-Macro (`dashboard.html.j2:1117-1127`) NICHT umschreiben — stattdessen an den drei neuen Stellen aufrufen bzw. erweitern:
  - Kampftechniken-Zeile `:1354`: aktuell rendert `AT / PA` bare. Ersetzen durch `AT {{ held.basiswerte.AT.akt }} / PA {{ held.basiswerte.PA.akt }}` (Feldnamen vor Implementierung gegen `parsers/held.py` verifizieren).
  - `.mod-probe`-Tabelle `:1440` (Spontane Modifikationen): `probe_eig`-Aufruf ergänzen wie bei der Zauberzeile `:1391`.
  - Wund-/Zustandsabzug: JS-seitig nach dem Laden (oder bei jedem `toggleZustand`/`changeWunden`) alle `.t-probe`/`.probe`-Elemente mit aktivem Malus um den Effektivwert ergänzen, z.B. Text von `GE 13` zu `GE 13→11` ändern. Nutzt denselben Update-Callback wie T1 (`updateEigLeisteBadge`-Nachbar-Funktion, z.B. `applyWundModsToProben()`, aus demselben Hook in `session.js` aufgerufen).
- CSS `:346` — feste `150px`-Spaltenbreite der Zauberliste auf `minmax(150px, max-content)` o.ä. umstellen, damit `GE 13→11`-Text nicht umbricht (Sprint-012-Regression aus dem Handoff vermeiden — die Follow-up-Fix von Sprint 012 hatte bewusst `nowrap` + fixe Breite gewählt, siehe Handoff „Bei künftig deutlich längeren Probe-Strings müsste die 150px angepasst werden" — genau dieser Fall tritt jetzt ein).

### T3 — D-027 Zauberspeicher-Auslöseprobe

- Regelzeile in der Speicher-Box (`dashboard.html.j2:1462-1473`, vor oder nach `speicher-summary`): „Auslösung: 1 Aktion, Probe MU/IN/KL (kostet keine AsP), +1 Erschwernis je weiterem belegten Speicher. Misslingen = Zauber verpufft. Patzer = alle gespeicherten Zauber lösen aus." — als `.meta`-Hinweiszeile analog D-024/T1-Vorbild, `| e`-escaped.
- Pro belegtem Slot (`:1477-1494`, `{% if not is_leer %}`-Zweig) einen Button `<button class="slot-ausloesen-btn" data-slot="{{ slot.slot }}" data-probe="MU/IN/KL" data-erschwernis="{{ ... }}" type="button">Auslösen</button>` neben dem bestehenden `slot-entleeren-btn` (`:1484`). Erschwernis serverseitig berechnen: Anzahl noch belegter Slots minus 1 (der auszulösende selbst zählt nicht mit) — Formel im Template mit Jinja `{% set belegte = held.rituale.zauberspeicher_slots | rejectattr('zauber', 'in', ['', '— frei —']) | list | length %}` grob nachbilden (an tatsächliche `is_leer`-Logik `:1476` anpassen, nicht neu erfinden).
- `static/dice.js:507` und `:520` — Klick-Handler-Selektor um `.slot-ausloesen-btn[data-probe]` erweitern (bestehende Funktion wiederverwenden, keine zweite Würfellogik).
- Erfolg → bestehenden Entleeren-Pfad in `static/zauberspeicher.js` aufrufen (denselben PATCH-Call wie der `slot-entleeren-btn`, nicht duplizieren). Patzer → `confirm()`-Dialog „Patzer! Alle gespeicherten Zauber lösen sich ebenfalls aus. Alle Slots entleeren?" und bei Bestätigung alle belegten Slots entleeren.

### T5 — D-029 Aussehen vervollständigen

- `helden/illaen-baernhold/_illaen.md:34-39` — bestehende Zeilen „Augen" (Z.35, aktuell „Farbe nicht festgelegt"), „Größe" (Z.36), „Statur" (Z.37) bleiben inhaltlich unverändert (keine Werte erfinden, User trägt sie nach) — NEU: eine Zeile „Gewicht | — (nicht festgelegt)" ergänzen, die bisher komplett fehlt.
- `dashboard.html.j2:1677-1685` (aussehen-list-Loop) — Werte, die `—` oder „nicht festgelegt" enthalten, mit einer CSS-Klasse `aussehen-row--offen` (gedimmte Opacity, z.B. `opacity: .55; font-style: italic;`) rendern statt wie ausgefüllten Text; Erkennung serverseitig im Template via Jinja-String-Test (`'nicht festgelegt' in a.beschreibung or a.beschreibung == '—'`), kein neuer Parser-Flag nötig.
- Portrait-Slot: NUR das `{% if %}`-Grundgerüst für ein optionales Bild (`helden/illaen-baernhold/portrait.*`, z.B. via neuem `held.portrait_path`-Feld, das der Parser auf Existenz prüft) — kein Bild einfügen, kein Pflichtteil. Wenn die Existenzprüfung Zusatzarbeit über den S-Effort hinaus bedeutet, als optionalen Stretch behandeln und im Report vermerken statt den Task zu blockieren.

## Out of Scope

- **D-018** (Zauber-Inline-Vorschau) — bleibt einziger offener Backlog-EPIC,
  nächster Sprint-014-Kandidat falls Chronik-Modus nicht zuerst kommt.
- **Chronik-Modus** (D-030…D-035) — eigener Sprint 014, erst nach
  Nutzer-Feedback zu Sprint 013 geplant.
- **D-036/D-037** (NSC-Register, Template-Zerlegung) — Backlog, kein
  Sprint-013-Umfang.
