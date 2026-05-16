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

## Drucken

Im Browser `Strg+P` → Druckvorschau zeigt das klassische DSA-4.1-Charakterblatt
(4 Seiten A4, Cream-Hintergrund). Direkt aus dem Browser-Druckdialog drucken
oder als PDF speichern.

## Dateistruktur

```
helden/_tools/
  render-held.py          ← Einstiegspunkt (dieser Befehl)
  watcher.py              ← File-Watcher (nur für --watch)
  parsers/
    held.py               ← liest die 9 Held-MD-Dateien
    kampagne.py           ← liest abenteuer/<kampagne>/
  templates/
    dashboard.html.j2     ← Jinja2-Template (Screen + Print CSS inline)
```
