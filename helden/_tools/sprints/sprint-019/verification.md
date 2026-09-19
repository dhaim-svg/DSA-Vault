# Task 6 — Browser-Verifikation Sprint 019 (D-041 · D-046 · D-044)

Methode: statische Seite `output/illaen-baernhold-dashboard.html` über `python -m http.server 8765` (kein Flask), Playwright/Chromium, Fenstergröße jeweils per `browser_resize` gesetzt und über `window.innerWidth` geprüft (1280 / 1071 / 1070 / 1100 / 1130 / 400). Bei 400 px ist `clientWidth` = 385 (15 px klassische Scrollleiste), `innerWidth` = 400 verifiziert. Alle Werte gemessen, nichts geschätzt. Screenshot-Beleg: `C:\Users\David\AppData\Local\Temp\claude\D--Projects-KnowledgeBase-DSA-Vault\7820160b-a643-4d1c-b728-15e888d6df0b\scratchpad\c1-banner-400.png`.

Ausgangswert Wunden: 0 (`[data-wunden]` = 0). Für Teil A zweimal `#wunden-plus`, am Ende zweimal `#wunden-minus`, Schmerz-Chip wieder aus. Der Dateiserver antwortet auf PATCH mit 501 — nichts geschrieben.

## Teil A — D-041 Wund-Malus (1280 px, 2 Wunden)

| Prüfpunkt | Erwartung | gemessen | Ergebnis |
|---|---|---|---|
| A1 Eigenschaften-Overlay | nur GE `base→base−4`, Rest unverändert | MU 12, KL 14, IN 15, CH 13, FF 12, **GE 13→9**, KO 13, KK 11; von 203 `[data-attr]` tragen 14 einen Pfeil, alle 14 sind `GE 13→9` | PASS |
| A2 Basiswert-Anzeigen `[data-wund-stat]` | AT/PA/FK/INI −4, GS −2, Waffe AT/PA −4 | INI 10→6, GS 8→6, AT 7→3, PA 8→4, FK 8→4; Waffenkarte AT 13→9, PA 9→5. MR/SO (`5MR`, `8SO`) ohne Pfeil | PASS |
| A2b `—`-Werte unverändert | `—` bleibt `—` | 0 `[data-wund-stat]` mit `—` auf dieser Seite (Held hat alle Werte) | NICHT MESSBAR (kein Element mit `—`) |
| A3 `#dp-mod` (Sentinel 99 vor jedem Klick) | GE −4, MU 0, KK 0, AT −4, PA −4, Talent 0, Zauber 0, Schaden 0 | GE −4, MU 0, KK 0, AT −4, PA −4, Talent 0, Zauber 0, Schaden 0 | PASS |
| A4 Widget/Badge | `(AT/PA/FK/INI/GE −4, GS −2)` / `Wunden ×2: GE −4` | `#wunden-penalty` = `(AT/PA/FK/INI/GE −4, GS −2)`; beide `.eig-leiste-mods` = `Wunden ×2: GE −4` | PASS |
| A5a Chip Schmerz Titel/Klasse | Titel „(Hausregel)“ + Regelwerk-Hinweis, Klasse `hausregel` | title = `Schmerz: −2 auf Proben (Hausregel) — Regelwerk: nur optionale SB-Probe nach Wunde (WdS S. 82)`; class = `zustand-chip hausregel active` | PASS |
| A5b Badge mit Chip | `Wunden ×2: GE −4 · Schmerz −2 (Hausregel)` | beide Badges exakt dieser Text | PASS |
| A5c Panel mit Chip | AT −6, GE −6, MU −2, Talent −2, Zauber −2, Schaden 0 | AT −6, GE −6, MU −2 (KK −2), Talent −2, Zauber −2, Schaden 0 | PASS |
| A5d Basiswerte mit Chip | `[data-wund-stat]` unverändert ggü. A2 | identisch zu A2 (INI 10→6, GS 8→6, AT 7→3, PA 8→4, FK 8→4, Waffe 13→9 / 9→5) | PASS |
| A5e Chip wieder aus | Klasse ohne `active`, Badge zurück | class = `zustand-chip hausregel`, Badge `Wunden ×2: GE −4` | PASS |
| A6 Wunden zurück auf 0 | keine Pfeile, GE = 0 | `#wunden-count` 0, 0 Pfeile in `[data-attr]`, 0 in `[data-wund-stat]`, `#dp-mod` GE = 0, `#wunden-penalty` leer, 0 aktive Chips | PASS |
| A7 Legende | `.zustand-legend` sichtbar | Rect 704,7 × 33,7 px, `display:block`; Text: „Zustände = Hausregel-Schalter (im Regelwerk kein fester Probenmalus). Wunden wirken regelkonform: AT/PA/FK/INI/GE −2, GS −1 je Wunde (WdS S. 57). Details →“ | PASS |

## Teil B — D-046 Zauberliste

Papier-Hintergrund (print): `body` = rgb(236, 228, 208) (nicht transparent). Kontrast nach WCAG (relative Luminanz), je erstes Element; Anzahl in Klammern.

| Prüfpunkt | Erwartung | gemessen | Ergebnis |
|---|---|---|---|
| B1 `.spell .name .nlink` (25) | ≥ 4,5:1 | color rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.zfw-num` (25) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.spell .zd` (25) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.spell .kosten` (25) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.spell .wirkung` (25) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.spell .submeta` (25) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.spell .probe` (25) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 `.spell .name .haus` (7) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** | PASS |
| B1 Stichprobe (nur berichten) | – | `.spell.spell-head` rgb(154,166,180) → **1,95:1**; `.mods-details .mods-list` (23) rgb(95,107,122) → **4,28:1** | Bericht, s. Befunde |
| B2 Grid-Überstand 1071 px | ≤ 0 px | zu: max Überstand 0 px, 0 von 181 Kindern > 0,5 px; offen (25 `.artikel-details`): 0 px, 0 von 181. Zeilenbreite 954 px; Spalten `190.25 240 38 80 111.9 223.8` | PASS |
| B2 Grid-Überstand 1100 px | ≤ 0 px | zu: 0 px / 0; offen: 0 px / 0. Zeilenbreite 983 px | PASS |
| B2 Grid-Überstand 1130 px | ≤ 0 px | zu: 0 px / 0; offen: 0 px / 0. Zeilenbreite 1013 px | PASS |
| B2 Grid-Überstand 1280 px | ≤ 0 px | zu: 0 px / 0; offen: 0 px / 0. Zeilenbreite 1098 px | PASS |
| B2 Kopfzeile `.spell-head` | 1071 sichtbar (Grid), 1070 nicht | 1071: `display:grid`, Höhe 34 px, Zeilen `display:grid`; 1070: `display:none`, Höhe 0, Zeilen `display:flex` (Breite 953 px) | PASS |
| B3 Umbruch in flexiblen Spalten (1071 px, Zeilen 1–5) | kein Overflow | in allen 5 Zeilen: `.name` 190,3 px (scrollWidth 190 / clientWidth 190), `.kosten` 111,9 px (112/112), `.wirkung-cell` 223,8 px (224/224), `.wirkung` 224/224; nirgends scrollWidth > clientWidth | PASS |

## Teil C — D-044 Mobile (verifiziert `innerWidth` = 400)

| Prüfpunkt | Erwartung | gemessen | Ergebnis |
|---|---|---|---|
| 8 Tabs: kein horizontaler Überlauf | `scrollWidth` = `clientWidth` | kampf, talente, zauber, steigern, inventar, profil, chronik, sprachen: je scrollWidth 385 = clientWidth 385 (auch `body.scrollWidth` 385). Zusätzlich Rect-Prüfung (jedes Element in jedem Tab, Rect.right > 385 außerhalb scrollender Container): 0 Treffer in allen 8 Tabs | PASS |
| C1 `.title-block h1` | left ≥ 0, right ≤ 400, kein Überlauf, Titel ganz sichtbar | left 45, right 340, Höhe 68 px, scrollWidth 295 = clientWidth 295, Schrift 34 px, Text „Illaen Baernhold“ (Screenshot: zweizeilig ILLAEN / BAERNHOLD vollständig) | PASS |
| C1 `.identity-stats` / `.crest` vs `.banner` (`overflow:hidden`) | innerhalb Banner | Banner l 28 / r 357 / t 208,9 / b 731,9; identity l 56,5 / r 328,5 / t 480,9 / b 541,9; crest l 164,5 / r 220,5 / t 233,9 / b 289,9 | PASS |
| C1 Gegenprobe 1280 px | 3 Spuren | `.banner-inner` `gridTemplateColumns` = `84px 606.094px 323.906px` | PASS |
| C2 `#footer-bar` position 400 px | `static` | `static` | PASS |
| C2 `#footer-bar` position 1280 px | `fixed` | `fixed` | PASS |
| C2 Höhe Footer-Controls 400 px | ≥ 44 px | `.print-btn` 44 / 44 / 44, `.commit-input` 44 | PASS |
| C2 Footer verdeckt nichts (400 px) | Footer unterhalb des Inhalts | letzter Inhalts-Rect-Bottom 1857, Footer top 1873 / bottom 1975 (Höhe 102), Dokumenthöhe 1991 | PASS |
| C3 `.steiger-scroll` (3 Stück) | `tabindex`, `role`, `aria-label`, `overflow-x`, scrollbar | alle: `tabindex="0"`, `role="region"`, `aria-label` = „Eigenschaften (Zielwert × 15 AP)“ / „Talente & Kampftechniken“ / „Zauber“, `overflow-x:auto`; scrollWidth/clientWidth 340/283, 391/283, 370/283 (Überlauf ja) | PASS |
| C3 Tastatur | `focus()` → aktiv; ArrowRight erhöht `scrollLeft` | alle 3: `document.activeElement === el`; scrollLeft 0 → 40 nach ArrowRight | PASS |
| C3 `<table class="steiger-table">` | kein `role` | 0 von 3 Tabellen haben `role` | PASS |
| C3 `.sg-scroll-hint` 400 px | sichtbar | 3 Stück, je Höhe 30,8 px, `display:block`; Text „← Tabelle seitlich scrollen: Kosten, Aktion, „auswählen“ →“ | PASS |
| C3 `.sg-scroll-hint` 1280 px | `display:none` | 3 Stück, alle `display:none`, Höhe 0 | PASS |
| C4 Inventar-Formular 400 px | Name `flex-basis:100%`, Anzahl `max-width` 80 px, ids | `.inv-add-input--name`: `flex-basis:100%`, Breite 283 px = Formularbreite 283 px (`.inv-add-form`), id `inv-add-name`; `.inv-add-input--anzahl`: `max-width:80px`, Breite 80 px, id `inv-add-anzahl` (nichts eingetippt/abgesendet) | PASS |
| C5 `summary.artikel-toggle` 400 px | ≥ 44 px | erste 5: 44 / 44 / 44 / 44 / 44; alle 25: Mittel 44, min 44, max 44 | PASS |
| C5 `summary.artikel-toggle` 1280 px | unverändert (~18 px) | erste 5: je 19 px; alle 25: Mittel 19 | PASS |
| C6 `.zustand-legend` 400 px | scrollWidth ≤ clientWidth, im Viewport | scrollWidth 283 = clientWidth 283, l 51 / r 334, Höhe 67,4 px | PASS |
| C6 `#zustand-chips` 400 px | umbrechen ohne Überlauf | `flex-wrap:wrap`, 2 Zeilen (Top-Werte −153 / −122), größter Chip-right 268,1 ≤ 334, Container scrollWidth 283 = clientWidth 283 | PASS |

GESAMT: 36 PASS / 0 FAIL / 1 NICHT MESSBAR

## Befunde (nur Auffälligkeiten, keine FAILs)

- **A2b NICHT MESSBAR:** Es gibt auf dieser Seite kein `[data-wund-stat]`-Element mit `—` (Held hat für AT/PA/FK/INI/GS/Waffe alle Werte). Verhalten „`—` bleibt `—`“ daher nicht prüfbar.
- **Schmerz-Chip und Eigenschaften-Overlay:** Mit aktivem Schmerz-Chip (2 Wunden) zeigen alle 8 Eigenschaften einen Pfeil (203 `[data-attr]`-Spans mit `→`, z. B. `GE 13→7`, `KO 13→11`, `MU 12→10`). Passt zu den −2 im Würfelpanel; die Brief-Erwartung für A5 nannte nur Panel und `[data-wund-stat]`, das Overlay wurde nicht spezifiziert.
- **Leeres Badge:** Bei 0 Wunden und ohne Chip sind beide `.eig-leiste-mods` leer, haben aber `display:block` (Textinhalt leer).
- **B1 Bestandsränder:** `.spell.spell-head` hat in Druckmedien color rgb(154,166,180) = 1,95:1 auf Papier rgb(236,228,208) (ob die Kopfzeile im Druck sichtbar ist, wurde nicht gemessen); `.mods-details .mods-list` 4,28:1 (knapp unter 4,5). Beide nicht Teil von D-046.
- **Touch-Ziele außerhalb der Brief-Erwartung (400 px):** Inventar-Eingaben `.inv-add-input--name` / `--anzahl` und „+ Hinzufügen“ je 30 px hoch; Zustands-Chips 25 px hoch. Brief verlangt dort keine 44 px.
- **B2 Messgrenze:** Der größte Überstand ist überall exakt 0 (das letzte Kind schließt bündig an der Innenkante ab); kein Kind steht > 0,5 px über.
- **Footer 1280 px (Stichprobe):** `.print-btn` 47 px, `.commit-input` 25 px hoch.

## Konsole

Keine Meldung außer den erwartbaren (40–42 Fehlereinträge insgesamt, alle „Failed to load resource“):
- `favicon.ico` 404
- `/api/held/illaen-baernhold/mtime` 404 (35 Mal, Polling)
- `/api/held/illaen-baernhold/value` 501 `Unsupported method ('PATCH')` (4 Mal, die 4 Wunden-Klicks)

Keine JS-Exceptions, keine Warnungen, keine sonstigen Fehler.

## git status --short

Vorher:
```
 M .obsidian/workspace.json
 M Welcome.md
?? .claude/settings.json
```
Nachher (identisch):
```
 M .obsidian/workspace.json
 M Welcome.md
?? .claude/settings.json
```

Aufgeräumt: Browser geschlossen, Dateiserver (Port 8765) beendet, `.playwright-mcp\` gelöscht.

## Teil D — A8 (Nachtragsrunde nach Commit b98c547, 1280 px, `innerWidth` = 1280 verifiziert)

Statische Seite neu über `http.server 8765` ausgeliefert, Browser neu gestartet. Das Würfelpanel zeigt die verwendeten Eigenschaftswerte in `#dp-eig-row .dp-eig-slot` (`.dp-eig-abbr` + `.dp-eig-val`); bei einer Einzelprobe (`.hex`) steht dort `GE(13)`. Vor jedem Öffnen wurde `#dp-mod` auf den Sentinel 99 gesetzt. Ausgangswert Wunden 0, kein Chip aktiv.

| Prüfpunkt | Erwartung | gemessen | Ergebnis |
|---|---|---|---|
| D1 Talent mit GE (0 Wunden, `data-probe="GE/KO/KK"`, Athletik) | GE 13, `#dp-mod` 0 | Slots `GE=13, KO=13, KK=11`, `#dp-mod` 0 | PASS |
| D1 Zauber mit GE (`IN/GE/KO`, Armatrutz) | GE 13, `#dp-mod` 0 | Slots `IN=15, GE=13, KO=13`, `#dp-mod` 0 | PASS |
| D2 Talent mit GE (2 Wunden) | GE 9, Rest unverändert, `#dp-mod` 0 | Slots `GE=9, KO=13, KK=11`, `#dp-mod` 0 | PASS |
| D2 Zauber mit GE (2 Wunden) | GE 9, Rest unverändert, `#dp-mod` 0 | Slots `IN=15, GE=9, KO=13`, `#dp-mod` 0 | PASS |
| D2 Talent ohne GE (`MU/KO/KK`, Selbstbeherrschung) | unverändert, `#dp-mod` 0 | Slots `MU=12, KO=13, KK=11`, `#dp-mod` 0 | PASS |
| D3 Talent mit GE (2 Wunden + Schmerz-Chip; Klasse `zustand-chip hausregel active`, Badge `Wunden ×2: GE −4 · Schmerz −2 (Hausregel)`) | GE weiter 9, `#dp-mod` −2 | Slots `GE=9, KO=13, KK=11`, `#dp-mod` −2 (zusätzlich Zauber `IN=15, GE=9, KO=13` −2; Talent ohne GE `MU=12, KO=13, KK=11` −2) | PASS |
| D3 `.hex[data-eigenschaft="GE"]` (kein Doppelabzug) | `#dp-mod` −6, GE-Basis 13 | `#dp-mod` −6, Panel „GE-Probe“ mit `GE(13)` (Ergebnis „Erfolg (5 ≤ 13)“) | PASS |
| D3 Chip wieder aus | Klasse ohne `active` | `zustand-chip hausregel`, 0 aktive Chips | PASS |
| D4 `.zustand-legend-chips` bei `#zustand-chips.innerHTML=''` | `display:none` | `display:none`, Rect 0 × 0 (vorher, Chips vorhanden: `inline`, Höhe 19) | PASS |
| D4 `.zustand-legend` ohne Chips | sichtbar, Höhe > 0, Wundsatz sichtbar | `display:block`, Höhe 16,8 px, Breite 704,7 px; `innerText` = „Wunden wirken regelkonform: AT/PA/FK/INI/GE −2, GS −1 je Wunde (WdS S. 57). Details →“ | PASS |
| D5 `.spell.spell-head` (print, Papier rgb(236,228,208)) | ≥ 4,5:1 | color rgb(26,18,8) → **14,62:1** (gegen Weiß 18,52:1), `display:grid`, Höhe 32,5 px | PASS |
| D5 `.spell.spell-head > *` (erstes Kind-Span, 6 Kinder) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1**, Höhe 13,5 px | PASS |
| D5 `.mods-details .mods-list` (23) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1** (vorher 4,28:1); Höhe 0 (Details geschlossen), Farbe daher nur aus `getComputedStyle` | PASS |
| D5 `.mods-details summary.mods-toggle` (23) | ≥ 4,5:1 | rgb(26,18,8) → **14,62:1**, Höhe 12,1 px | PASS |
| D5 `.zustand-legend` in print | `display:none` | `display:none`, Höhe 0 | PASS |
| D6 A1 (2 Wunden, kein Chip) | nur GE mit Pfeil | MU 12, KL 14, IN 15, CH 13, FF 12, **GE 13→9**, KO 13, KK 11; 14 von 203 `[data-attr]` mit Pfeil, alle `GE 13→9` | PASS |
| D6 A2 | INI/GS/AT/PA/FK Pfeile | INI 10→6, GS 8→6, AT 7→3, PA 8→4, FK 8→4; Waffe AT 13→9, PA 9→5 | PASS |
| D6 A3 `#dp-mod` | GE −4, MU 0, AT −4, PA −4, Talent 0, Zauber 0, Schaden 0 | GE −4, MU 0, AT −4, PA −4, Talent 0, Zauber 0, Schaden 0 | PASS |
| D6 Wunden zurück auf 0 | 0 Pfeile, GE 0, Probe-GE = Basis | `#wunden-count` 0; 0 Pfeile in `[data-attr]` / `[data-wund-stat]`; `.hex` GE `#dp-mod` 0; Talent-Panel `13, 13, 11` | PASS |

A8: 19 PASS / 0 FAIL / 0 NICHT MESSBAR

Konsole (Teil D): nur `favicon.ico` 404, `/api/held/illaen-baernhold/mtime` 404 (11 Mal) und `/api/held/illaen-baernhold/value` 501 PATCH (4 Mal, die 4 Wunden-Klicks); keine sonstigen Meldungen. `git status --short` vor und nach der Runde unverändert (` M .obsidian/workspace.json`, ` M Welcome.md`, `?? .claude/settings.json`). Browser geschlossen, Dateiserver beendet, `.playwright-mcp\` gelöscht.
