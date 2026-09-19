# Helden-Dashboard Generator

Liest die Markdown-Charakterdateien eines DSA-4.1-Helden und erzeugt daraus
eine statische HTML-Seite in `output/` — mit modernem Dashboard-Layout am
Bildschirm und einem druckbaren DSA-Charakterblatt (Strg+P im Browser).

## Setup (einmalig)

Vom Vault-Root aus:

```powershell
pip install -r requirements.txt
```

## Verwendung

Alle Befehle vom **Vault-Root** aus ausführen:

```powershell
# Nur rendern
python helden\_tools\render-held.py illaen-baernhold

# Rendern + Browser öffnen
python helden\_tools\render-held.py illaen-baernhold --open

# Live-Reload: Dashboard aktualisiert sich automatisch bei Dateiänderungen
python helden\_tools\render-held.py illaen-baernhold --watch --open
```

**`slug`** = Name des Unterordners in `helden/` (z.B. `illaen-baernhold`).
Output landet immer in `output/<slug>-dashboard.html`.

## Wann neu rendern?

Nach jeder Änderung an einer der Held-Dateien:

| Datei geändert | Betroffener Dashboard-Bereich |
|---|---|
| `helden/<slug>/_<slug>.md` | Header (Name, AP, Stufe, Basiswerte) |
| `helden/<slug>/talente.md` | Talent-Tabelle |
| `helden/<slug>/zauber.md` | Zauberliste |
| `helden/<slug>/rituale.md` | Stabzauber / Rituale |
| `helden/<slug>/sonderfertigkeiten.md` | SF-Liste |
| `helden/<slug>/vor-nachteile.md` | Vor-/Nachteile |
| `helden/<slug>/ausruestung.md` | Ausrüstung / Geld |
| `helden/<slug>/steigerungs-log.md` | Aktivitäts-Feed |
| `abenteuer/drachenchronik/_drachenchronik.md` | Kampagnen-Card |
| `abenteuer/drachenchronik/chronik.md` | Chronik-Tab (Roh) |

## Drucken

Im Browser `Strg+P` → Druckvorschau zeigt das klassische DSA-4.1-Charakterblatt
(4 Seiten A4, Cream-Hintergrund). Direkt aus dem Browser-Druckdialog drucken
oder als PDF speichern.

## Dateistruktur

```
helden/_tools/
  render-held.py          ← Einstiegspunkt (dieser Befehl)
  rendering.py            ← Jinja-Env, build_context/render_dashboard, css_bundle
  watcher.py              ← File-Watcher (nur für --watch)
  chronik_paths.py        ← geteilte Pfad-Konstanten der Chronik
  chronik_import.py       ← Einweg-Import Drive → Vault (python helden/_tools/chronik_import.py)
  parsers/
    held.py               ← liest die 9 Held-MD-Dateien
    kampagne.py           ← liest abenteuer/<kampagne>/
    chronik.py            ← load_chronik: liest abenteuer/drachenchronik/chronik.md
  templates/
    dashboard.html.j2     ← schlankes Gerüst: Head, Macros, Banner, Tab-Leiste,
                            Includes, Footer, Scripts
    partials/<tab>.j2     ← je ein Tab-Body: kampf, talente, zauber, steigern,
                            inventar, profil, chronik, sprachen
      journal.j2          ← Sub-Partial der Chronik-Ansicht „Kompiliert"
  static/
    *.css                 ← Stylesheets inkl. Print (base, tabs, journal, sprachen, chronik)
    chronik.js/.css       ← Roh/Kompiliert-Umschalter und Styles des Chronik-Tabs
    *.js                  ← Client-Skripte (Tabs, Würfel, Steigern, Inventar, Journal, …)
```

**CSS wird eingebettet, nicht verlinkt:** `rendering.py::css_bundle()` fügt die
`static/*.css` beim Rendern inline in die HTML-Seite ein (der Static-Render kann
`/static/…` nicht laden). Die Reihenfolge von `CSS_FILES` in `rendering.py` ist
Kaskaden-relevant, und jede neue `static/*.css` muss dort eingetragen werden
(ein Test erzwingt das).

## Chronik-Bilder

Der Chronik-Tab zeigt Bilder aus `abenteuer/drachenchronik/drachenchronik-daten/`.
Im Server-Modus (`render-held.py serve <slug>`) liefert die Route
`GET /chronik-bild/drachenchronik-daten/<datei>` ausschließlich Bilder
(png/jpg/jpeg/gif/webp) aus diesem Ordner. Im Static-Render zeigen die Bilder
relativ auf `../abenteuer/drachenchronik/…`.
