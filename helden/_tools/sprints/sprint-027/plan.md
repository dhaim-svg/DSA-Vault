# Sprint 027 — Druck-Vollständigkeit: Vitalwerte (D-054), Verlaufstext (D-055), Papieroptik-Ruling (D-056), Cleanup (B-027)

## Tasks

| # | Task | State | Files |
|---|------|-------|-------|
| T0 | Sprint scaffold (`BACKLOG.md` D-054/D-055/D-056 → in-progress, Vault-`backlog.md` B-027 → in-progress, `plan.md` anlegen) | ✅ done (`1cef602`) | `helden/_tools/BACKLOG.md`, `backlog.md`, `sprints/sprint-027/plan.md` |
| T1 | **D-054** — `.vital-input` im Druck sichtbar statt ausgeblendet (entkleidet: `border:none`, `background:transparent`, `color:var(--paper-ink)`), `.vital-max`/`.vital-sep` bekommen eigene Druckfarbe statt im ausgeblendeten `.vital-stepper` unterzugehen, totes `.vital::after` (`tabs.css:329`) entfernen. Verifikation: Screenshot (Print-Emulation) **und** `page.pdf()`-Raster, Zahlenspinner-Unterdrückung im Druck prüfen | ✅ done (`7b070b0`, Fix-Runde 1 `9997bfb` — `.vital-max`/`.vital-sep` verloren `opacity:0.7`; beide Reviews sauber) | `static/tabs.css`, `tests/test_rendering.py` |
| T2 | **D-055** — `beforeprint`/`afterprint`-Paar in `static/chronik.js` (Vorlage: bestehende `<details>`-Logik Z.31–44) zieht jede `.journal-verlauf` auf `scrollHeight` auf, Rückbau danach. Verifikation über die volle Bandbreite (kürzeste + längste Session, scrollHeight 716–1244px lt. Sprint-026-Messung) per Screenshot + PDF-Raster | ✅ done (`d13223b`, Task-Review clean; Gesamt-Review fand Breiten-Mismatch → Fix-Runde `8e5b150` auf Druck-Mirror umgestellt, R4; Re-Review sauber) | `static/chronik.js`, `static/journal.css`, `tests/test_chronik_js.py`, `tests/test_rendering.py` |
| T3 | **D-056** — Ruling dokumentieren (Weiß bleibt Zielzustand, kein Code-Change): `BACKLOG.md`-Done-Eintrag mit Begründung. Kein Subagent — Controller inline | ✅ done (`662c5f8`) | `helden/_tools/BACKLOG.md` |
| T4 | **B-027** — redundante Bedingung `held.py:539` entfernen (`gew = safe_int(gew_raw)`), Docstring `tests/test_inventar_model.py:138` anpassen, Mutationsprobe am Parser | ✅ done (`082b088`, Review clean beim ersten Durchgang) | `parsers/held.py`, `tests/test_inventar_model.py` |
| T5 | Verifikation + `/sprint-wrap` | 🔄 laufend | `sprints/sprint-027/verification.md`, `handoff.md`, Tracker |

## Key Design Decisions

- Die drei D-054/055/056-Rulings (siehe unten) sind bindend für die Subagent-Briefings.
- **Druck-Verifikation** für T1/T2 folgt der Sprint-026-Lehre: Print-Emulation-Screenshot allein reicht nicht (Chromium druckt Hintergründe ohne `print-color-adjust:exact` nicht, dunkelt Vordergrundfarben im PDF-Pfad ab) — zusätzlich `page.pdf()` + Rasterung (`pdftoppm`), Browser nur lesend über `python -m http.server --directory output` auf freiem Port.
- **T1, T2 und T4 sind dateidisjunkt** (`tabs.css` / `chronik.js`+`journal.css` / `held.py`+`test_inventar_model.py`) und können parallel laufen, analog zu T1/T4 in Sprint 026.
- **T3 läuft ohne Subagent** — reine Tracker-Dokumentation ohne Code-Änderung.
- Zwei-stufige Review (Spec + Code Quality) für T1/T2/T4.
- Kein Worktree, Commits direkt auf `master`, kein Push (bisheriger Workflow, CLAUDE.md).

## Out of Scope

- Voller Kontrast-Sweep gegen `#ece4d0` — wäre nur bei D-056-Option „getönt" nötig gewesen, entfällt durch die Ruling (Weiß bleibt Zielzustand).
- `#tab-profil table *` Flächenschlag (`tabs.css:170`) — unverändert seit Sprint 026 verschoben (Regressionsrisiko).
- Probe-Spalte im Zauber-Tab, Grid-Stretch der Ritual-/SF-Karte, echter PATCH-Pfad im Browser, Footer-Transition beim Einblenden — unverändert offen (Sprint-026 „Bekannte Einschränkungen").
- Echter Druckdialog (nur PDF-Raster als bisher bester Ersatz) — unverändert offen seit Sprint 020.
- Wiki- und User-Domäne (`wiki/`, `helden/illaen-baernhold/`, `abenteuer/`) bleiben unberührt.

## Rulings

- **R1 (D-054)** — Druck zeigt das reale Eingabefeld (`.vital-input`, im Druck sichtbar statt ausgeblendet, optisch entkleidet) + den vorhandenen `.vital-max`-Text direkt. Kein JS-Sync: der Browser druckt den aktuell angezeigten Formularwert ohnehin live mit, kein Synchronisationsrisiko. (User-Entscheidung, Sprint-Planung)
- **R2 (D-055)** — `beforeprint`/`afterprint` in `static/chronik.js` (gleiches Muster wie die bestehende `<details>`-Logik) zieht jede `.journal-verlauf` auf `scrollHeight` auf und setzt nach dem Druck zurück. Kein Duplikat-Element, liest immer den Live-DOM-Wert. (User-Entscheidung, Sprint-Planung)
- **R3 (D-056)** — Weiß bleibt Zielzustand. Kein `print-color-adjust:exact`, keine Kontrast-Neubewertung. Reine Dokumentationsaufgabe. (User-Entscheidung, Sprint-Planung)
- **R4 (ersetzt Teil von R2)** — Die Gesamt-Review (gemessen, nicht argumentiert) fand: `beforeprint` maß `scrollHeight` im **Bildschirm**-Layout (`.journal-verlauf` clientWidth 1081px @ 1280px-Fenster), die echte Druckbreite ist aber viel schmaler (~584px) — derselbe Text bricht dort auf mehr Zeilen um. Zwei echte `page.pdf()`-Läufe (1280px vs. 718px Fenster) unterschieden sich um **48 Zeilen**: bei normaler Fensterbreite fehlten weiterhin ~17 % des Verlaufstexts (keine Regression ggü. vorher, aber am Sprintziel vorbei). Die eigene T2-Verifikation nutzte durchgängig 718px, wo Druckbreite zufällig der Bildschirmbreite entspricht — das hat den Fehler strukturell versteckt. **Fix:** statt die Textarea selbst zu vergrößern, zeigt der Druck ein `<pre class="journal-verlauf-print">`-Element, das bei `beforeprint` per `textContent = t.value` aus dem Live-Wert befüllt wird — R2s Kernanliegen („kein serverseitig veralteter Mirror") bleibt damit erfüllt, auch wenn es technisch ein zusätzliches Element ist: ein normales Fließelement wird vom Druck-Layout selbst korrekt umbrochen, unabhängig von der Spaltenbreite. (Gesamt-Review + Fix-Runde, Sprint-Ausführung)
