# Browser-Verifikation des Illaen-Dashboards

Playwright-MCP (`claude-in-chrome` oder das `playwright`-Plugin) läuft **gegen das Static-Render über
einen einfachen Dateiserver**, nie gegen den Flask-„served"-Modus — sonst schreiben Stepper, Wunden-
Widget, Steigern, Inventar, Zauberspeicher und Journal per PATCH real in Vault-Dateien zurück.
`session.js`/`app.js` schalten ihre Client-Logik nur an `location.protocol`, laufen also identisch über
`python -m http.server`; PATCH-Requests scheitern dort harmlos (501).

## Ablauf

1. Static-Render frisch erzeugen: `python helden/_tools/render-held.py illaen-baernhold` (Slug ist
   Pflicht). Nach jeder Fix-Runde neu rendern, sonst prüft der Browser veralteten Code.
2. Verifikations-Agent (benannt) startet `python -m http.server <freier Port> --directory output` im
   Hintergrund, öffnet `http://localhost:<port>/illaen-baernhold-dashboard.html`.
3. **Nur-Lesen-Liste** im Brief: nichts anklicken, das schreibt (Sichern, Commit, Steigern-Bestätigung,
   Inventar-Hinzufügen, Journal-Speichern, Session-Reset). `git status --short` vorher/nachher muss
   identisch sein. Wunden lassen sich lesend simulieren (`dataset.wunden` im Speicher setzen, Chip
   togglen) statt per PATCH.
4. sha256 der servierten Datei gegen die Datei auf der Platte abgleichen — ein liegen gebliebener
   Server auf demselben Port kann eine andere Datei ausliefern, als man denkt.
5. Nach der Messung: eigene PID beenden, `Get-Process` gegenprüfen, `.playwright-mcp/` löschen.
   Einen fremden Prozess selbst zu beenden verweigert der Permission-Klassifizierer — dem User melden
   (`! taskkill /PID <pid> /F`), nicht umgehen.
6. Bericht als Datei (Tabelle Prüfpunkt · Erwartung · gemessen · PASS/FAIL), Antwort ≤ 12 Zeilen,
   erste Zeile `GESAMT: X PASS / Y FAIL / Z NICHT MESSBAR`. Erwartete Konsole: `favicon.ico` 404,
   `/api/…/mtime` 404, PATCH 501 — jede andere Meldung ist ein Befund.
7. Messauftrag muss die **vollständige Rohliste als Datei** verlangen, nicht nur Beispiele im Bericht
   — sonst ist die Sollmenge für Fix/Nachmessung/Gesamt-Review weg, sobald die Session endet.

## Fallstricke

- **Jeden UI-Zustand messen**, nicht nur die Default-Ansicht (Tabs, Umschalter, datenabhängige Badges
  per DOM-Injektion herstellen — kein Vault-Schreibzugriff nötig).
- **Layout-Messung:** `getBoundingClientRect`-Vergleich statt `scrollWidth`; bei 400 px Viewport liegt
  `clientWidth` wegen Scrollbar bei ~385.
- **Eingebetteter Inhalt** (Markdown/HTML in einer Komponente): Bare-Element-Regeln (`li`, `td`, `p`,
  `a`) gehören auf den Kind-Selektor `>`; verschachtelte Elemente separat messen.
- **Print-Emulation ≠ echter Druck.** `page.emulateMedia('print')` + Screenshot bildet Hintergründe
  (fehlendes `print-color-adjust:exact`) und Farbabdunklung falsch ab, und löst `beforeprint`/
  `afterprint` NICHT aus. Verbindlicher Nachweis ist **ausschließlich `page.pdf()` + Rasterung**
  (z. B. `pdftoppm`). Kontrast-Sweeps per `getComputedStyle` bleiben zusätzlich sinnvoll (Alpha ×
  Opazität der Ahnenkette gegen das Papier rechnen), sind aber gegen echtes Weiß **konservativ** —
  gefährlich ist nur, was seine Lesbarkeit über einen gemalten Hintergrund trägt.
- **Echte Druckbreite:** Die A4-`@page`-Ränder kennt die Emulation nicht (~703 px statt Viewport-Breite).
  Bei druckbreitenabhängigem JS (Zeilenumbruch, `scrollHeight`) mindestens zwei Fensterbreiten prüfen —
  eine einzelne Näherungsbreite kann den Fehler strukturell verdecken.
- Für echte Schreibpfade (Flask-PATCH) gibt es einen gesonderten, bewussten Test mit anschließendem
  `git checkout` der betroffenen Held-Datei — nicht Teil dieser Static-Verifikation.
