# Sprint 013 Handoff — Bug-Reste aus vier Spielabenden (Eig-Werte, Stabzauber-Aktivierung, Aussehen)

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-025…D-029 → in-progress, plan.md angelegt, veraltete D-019…D-024-Beschreibungsblöcke bereinigt)
- ✅ T6/W-001 (kein Dashboard-Task, direkt in Hauptsession): **Wiki-Korrektur Stabzauber-Aktivierung** — `wiki/dsa-4.1/rituale/stabzauber.md` behauptete pauschal „Aktivierung = freie Aktion (kein Zauberwurf)", widersprach sich im selben Absatz selbst. Gegen `raw/pdf-extracted/wege-der-zauberei/kapitel-09-rituale.txt` (WdZ S. 106–110) geprüft und durch eine korrekte Vergleichstabelle ersetzt: die „einfachen" Stabzauber (Bindung, Ewige Flamme, Hammer des Magus, Seil des Adepten) brauchen keine Probe, kosten aber je 1 AsP; die drei Foki sind passiv ohne jede Aktivierung; Flammenschwert/Schuppenhaut haben eigene Aktivierungsproben; der Zauberspeicher hat die bereits korrekt dokumentierte MU/IN/KL-Probe. `rituale-grundregeln.md` präzisiert entsprechend. `wiki-luecken.md` L16 protokolliert den Befund.
- ✅ T4: **D-028** Erschaffungsprobe + AsP je Stabzauber — `rituale.md`-Tabelle um zwei Spalten erweitert (Werte aus dem korrigierten Wiki), Parser (`held.py`) liest sie mit, Template zeigt sie neben dem Vol-Badge. „Stabverlängerung" (keine bestätigte Wiki-Entsprechung) bleibt bewusst leer mit hedged Fußnote statt stillschweigender Gleichsetzung mit „Doppeltes Maß". Review clean, kein Fix-Round nötig.
- ✅ T1: **D-025** Eigenschafts-Leiste über Talente-/Zauber-Tab — neues Macro `eig_leiste(eig, basis)`, sticky am oberen Rand beider Tabs (`top: 46px`, unter der fixed Tab-Bar). JS-Hook `updateEigLeisteBadge()` in `session.js`. Zwei vom Implementierer selbst geflaggte und vom Reviewer unabhängig verifizierte Abweichungen vom Brief: Mod-Badge nutzt eine **Klasse** `.eig-leiste-mods` statt `id` (Macro rendert in beide Tabs gleichzeitig, geteilte `id` wäre ungültiges HTML), `top: 46px` statt `top: 0` (sonst verschwindet die Leiste unter der fixed Tab-Bar). Review clean.
- ✅ T2: **D-026** Inline-Eigenschaftswerte vervollständigen — Kampftechniken-Zeile zeigt jetzt beschriftete `AT`/`PA`-Werte (behielt die bereits vorhandenen, akkuraten Pro-Kampftechnik-Werte statt sie durch generische `held.basiswerte` zu ersetzen — Implementierer-Korrektur einer falschen Brief-Annahme, verifiziert via `git log -S`). Wund-/Zustandsabzug jetzt sichtbar (`GE 13→11`) über geteiltes `computeActiveEffects()`. `.mod-probe`-Tabelle bewusst **nicht** angefasst — enthält Modifikator-Formeln (`je –1 / 1/2/4/8/16 … AsP`), keine Attribut-Proben; `probe_eig` hätte die Notation zerhackt. **1 Fix-Round**: Probe-Spalte `minmax(150px, max-content)` verursachte zeilenweise Spaltenversätze (jede `.spell`-Zeile ist ein eigener Grid-Container) → auf feste `240px` korrigiert (rechnerisch für den Worst-Case-String hergeleitet, nicht geschätzt).
- ✅ T3: **D-027** Zauberspeicher-Auslöseprobe — Regelzeile + „Auslösen"-Button pro belegtem Slot, Probe MU/IN/KL, Erschwernis serverseitig berechnet (+1 je weiterem belegten Slot), an bestehenden Würfler angebunden (`openPanel` um additives `baseMod` erweitert, alle 6 bisherigen Call-Sites unverändert). Erfolg → bestehender Entleeren-Pfad; Patzer → alle Slots entleeren nach Bestätigung. **1 Fix-Round**: Patzer-Mehrfach-Entleerung hatte eine Race — jeder `handleEntleeren()`-Call reloadete sofort nach eigenem PATCH-Erfolg und brach die anderen laufenden Requests ab (nur 1 von N Slots wurde real geleert). Fix: additives `skipReload`-Flag + `Promise.all` + einmaliger Reload danach. Implementierer baute einen Wegwerf-Node-Harness als Negativkontrolle, um den Bug am alten Code zu reproduzieren und den Fix zu bestätigen.
- ✅ T5: **D-029** Aussehen vervollständigen — Gewicht-Zeile ergänzt (auch offen, keine erfundenen Werte), offene Felder visuell gedimmt/kursiv statt wie normaler Inhalt gerendert, Portrait-Plumbing (`held.portrait_path`, guardeter `<img>`-Block, kein Platzhalterbild). Review clean bis auf eine triviale `| e`-Lücke im neuen `<img src>` — direkt vom Controller gefixt (< 10 Zeilen, kein Subagent, projektübliches Vorgehen für triviale Reviewer-Findings).
- ✅ **Finale Gesamt-Review** (Opus, ganzer Sprint-Diff d9888ad..2488422): „Ready to merge — with fixes". **1 Fix-Wave** (3 Important + 1 Minor, in einem Durchgang statt Einzel-Dispatches):
  1. **Zauberspeicher-Probe war bei aktiver Erschwernis/Wunde praktisch unschlagbar** — `calcTalentProbe`'s `tap = effTaw - totalFehl` wurde bei negativem `effTaw` (T3 war der erste Call-Site mit `taw:0`) für **jeden** Würfelwurf negativ, widersprach der eigenen Wiki-Regel (`proben.md:33`, `talentregeln.md:24`: negativer effektiver TaW wird als Erschwernis auf die drei Einzelproben angewendet, nicht pauschal von TaP* abgezogen). Fix: Overflow bei negativem `effTaw` fließt jetzt pro Würfel in die Einzelprobe statt in `tap`; bei `effTaw ≥ 0` byte-identisch zum alten Verhalten (per Hand nachgerechnet + 3 neue Tests). Höchstes Risiko der Fix-Wave, unabhängig durch Re-Review verifiziert.
  2. **Angezeigter Zustands-Malus erreichte den tatsächlichen Würfelwurf nicht** — `getWundMod()` (Würfel-Panel) las nur Wunden, `computeActiveEffects()` (Anzeige) auch Zustände. Fix: `session.js` exportiert `window.DSASession.computeActiveEffects`, `getWundMod()` nutzt es (mit `file://`-Fallback-Guard).
  3. **Test gegen Live-Vault-Datei** — `test_held_writer.py` prüfte exakte Zeilenanzahl/-werte gegen `illaen-baernhold` statt eine Fixture; wäre bei jeder User-Bearbeitung des eigenen Charakterbogens rot geworden. Auf isolierte `tmp_path`-Fixture umgestellt.
  4. **`| e`-Lücke** in den neuen `data-attr`/`data-base`/`Stk`-Interpolationen (D-026) — ergänzt.
  Scoped Re-Review (Opus): alle 4 Findings ADDRESSED, keine neue Critical/Important-Breakage, Tests unabhängig nachvollzogen.

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
  - **Sticky Eigenschafts-Leiste oben** (D-025), Inline-Eigenschaftswerte in Probe-Zellen inkl. Kampftechniken (D-023 + D-026)
  - **Wund-/Zustandsabzug sichtbar in Probe-Zellen** (`GE 13→11`, D-026), und dieser Malus **erreicht jetzt auch den Würfelwurf selbst** (Finale-Review-Fix 2)
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten, Zauberspeicher
  - **Sticky Eigenschafts-Leiste oben** (D-025), Probe-Spalte fest 240px (D-026-Fix-Round)
  - Stabzauber-Liste zeigt jetzt **Erschaffungsprobe + AsP** neben dem Vol-Badge (D-028), allgemeine Aktivierungsregel-Hinweiszeile (D-024, Sprint 012)
  - **Zauberspeicher-Slots sind jetzt würfelbar**: „Auslösen"-Button mit MU/IN/KL-Probe, korrekt berechneter Erschwernis, funktionierendem Patzer-Mehrfach-Entleeren (D-027)
- ⭐ Steigern-Tab: Warenkorb, Steiger-Tabellen, Erfahrungs-Modifikator, Stufen-Aufstieg-Button
- 🗣️ Sprachen-Tab: Sprachen + Schriften mit Komplexität/TaW
- 🎒 Inventar-Tab: Münzbeutel, Inventarliste, Reiseausrüstung
- 📋 Profil-Tab:
  - „Aussehen & Kleidung"-Card: **Gewicht-Zeile ergänzt, offene Felder visuell als offen markiert** statt wie ausgefüllter Inhalt (D-029), optionale Portrait-Anzeige geplumbt (aktuell inert, s.u.)
  - Vor-/Nachteile, Kampagne·Steigerung, Steigerungs-Log, Vorgeschichte
- 📓 Journal-Tab: Session-Notizen aus `abenteuer/`, `## Verlauf` editierbar
- 💾 Commit-Button, Tab-Persistenz via sessionStorage
- **Würfel-Panel unterstützt jetzt korrekt negative effektive TaW** (jede Talent-/Zauber-/Aktivierungsprobe, nicht nur der Zauberspeicher — profitiert vom Finale-Review-Fix 1)

## Verifikation

- **Test Suite:** 99/99 Testfälle bestanden (Baseline 93 → +6: 3× negative-effTaW-Fälle in `test_dice.py`, Rest aus D-028s Parser-Test verrechnet gegen die zwischenzeitliche Live-Vault-Test-Umstellung)
- **Static Render:** `illaen-baernhold-dashboard.html` erfolgreich generiert (exit 0) ✓
- **`node --check`:** `dice.js`, `session.js`, `zauberspeicher.js` ok
- **Review:** 5 Task-Reviews (T4/T1 clean ohne Fix-Round, T2/T3 je 1 Fix-Round, T5 clean + 1 triviale Inline-Korrektur) + finale Gesamt-Review mit 1 Fix-Wave (3 Important + 1 Minor), alle unabhängig re-verifiziert — „Ready to merge" nach Fix-Wave
- Alle Commits direkt auf `master`, kein Worktree/Branch (projektkonform, wie alle 12 Vorgänger-Sprints)

## Als nächstes (Sprint 014)

- **Chronik-Modus** (D-030…D-035, siehe Plan `C:\Users\David\.claude\plans\ich-habe-jetzt-die-mellow-beaver.md`) — User nutzt das Journal-Tab derzeit nicht, schreibt stattdessen in einer eigenen MD-Datei außerhalb des Vaults mit. Noch nicht in BACKLOG.md aufgenommen (wird bei `/sprint-plan` für Sprint 014 aus dem Plan-File ausgearbeitet, sofern der User nach diesem Sprint grünes Licht gibt).
- **D-018** (Zauber-Inline-Vorschau, L) — einziger länger offener Backlog-EPIC, jetzt günstiger dank `popover` + CSS Anchor Positioning (Baseline seit Jan. 2026).
- (Reihenfolge = Empfehlung, nicht Pflicht)

## Bekannte Einschränkungen (bewusst ausgeklammert)

- **Kampf-Header-Wortlaut mehrdeutig** — Kampftechniken-Gruppenkopf liest weiterhin „AT / PA · TaW", Zeilen zeigen jetzt aber „AT 12 / PA 8 · Stk D" — das unbriefte `Stk`-Feld führt einen zweiten `·` ein, der wie eine Beschriftung von „Stk" statt „TaW" wirkt. Kosmetisch, S-Kandidat.
- **AT/PA bekommen keinen Wund-Overlay** — `applyWundModsToProben()` annotiert nur Felder mit `data-attr`/`data-base`; Kampftechniken haben das (noch) nicht, zeigen bei aktiver Wunde also statisch `AT 12` während Talent-Zeilen daneben `GE 13→11` zeigen. Reines Anzeige-Artefakt — das Würfel-Panel selbst wendet `getWundMod()` für AT/PA korrekt an.
- **`.talent-row`-Grid hat mildere Version der `.spell`-Rasterung** — gleiches Pro-Zeile-Grid-Problem wie bei D-026s `.spell`-Fix, aber die nachfolgende Spalte ist rechtsbündig und bleibt dadurch optisch gerade. Nur beheben falls es im Spiel stört.
- **Portrait-Plumbing inert** — weder der Live-Server (keine Route für `helden/<slug>/`) noch der Static-Render (relativer Pfad löst sich gegen `output/`, nicht Vault-Root, auf) liefern ein Portrait tatsächlich aus. Kein Nutzerschaden heute (kein Portrait-File vorhanden), aber „einfach eine Flask-Route ergänzen" reicht als künftiger Fix nicht — der Static-Render-Pfad braucht eine eigene Lösung (kontextabhängiger Pfad oder Kopie/Symlink in `output/`).
- **`.mod-probe` (Spontane Modifikationen) bewusst außerhalb von D-026** — enthält Modifikator-Formeln (z.B. „+MR", „–3", „je –1 / 1/2/4/8/16 … AsP"), keine Attribut-Proben; `probe_eig` wäre hier fachlich falsch. In BACKLOG.md als „intentionally N/A" vermerkt, nicht versehentlich weggelassen.
- **Weitere Tests lesen weiterhin live gegen `illaen-baernhold`** — `test_steigerbar.py` (7 Stellen) und `test_inventar_model.py:124` haben dieselbe Fragilität wie der in diesem Sprint gefixte `test_held_writer.py`-Fund (würden bei User-Bearbeitung der eigenen Helden-Dateien rot werden). Nicht in diesem Sprint behoben — Umfang würde den Fix-Wave sprengen, S/M-Kandidat für einen künftigen Hygiene-Sprint.
- **Python/JS-Würfel-Mathe-Mirror ohne automatischen Drift-Check** — `test_dice.py`s `calc_talent_probe` ist eine handgepflegte Kopie von `dice.js`s `calcTalentProbe`; beide stimmen heute nachweislich überein, aber nichts erzwingt das bei künftigen Änderungen.
- **Stabzauber „Stabverlängerung"** — keine bestätigte Wiki-Entsprechung (vermutlich „Doppeltes Maß", aber nicht umbenannt, `helden/` ist User-Domäne). Erschaffungsprobe/AsP bleiben dort leer mit hedged Fußnote.
- Vererbte Einschränkungen aus Sprint 012 (vereinfachtes lineares SKT-Modell, `kampagne_slug` hardcoded, kein Guided Stufen-Aufstieg, kein Rollback bei Teil-Commit) bleiben unverändert offen.
