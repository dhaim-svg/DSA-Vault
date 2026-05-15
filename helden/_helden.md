# Helden

Spielerdaten-Bereich des Vaults. **User-Domäne** — wird vom Spieler gepflegt, nicht automatisch durch den LLM-Bibliothekaren überschrieben.

## Helden-Roster

| Held | Rasse | Profession | Tradition | Stufe | AP gesamt | AP verfügbar | Status |
|------|-------|------------|-----------|-------|-----------|--------------|--------|
| [[helden/illaen-baernhold/_illaen\|Illaen Baernhold]] | Nivese | Mag. Leibwächter | Gildenmagier | 3 | 3.850 | 3.845 | aktiv |

---

## Konventionen

### Ordner-Aufteilung pro Held

Jeder Held bekommt einen eigenen Unterordner `helden/<name>/` mit folgenden Dateien:

| Datei | Inhalt |
|-------|--------|
| `_<name>.md` | Charakterbogen-Übersicht (Personendaten, Eigenschaften, Basiswerte, AP, Navigation) |
| `vor-nachteile.md` | Vorteile, Nachteile, Schlechte Eigenschaften |
| `sonderfertigkeiten.md` | Alle Sonderfertigkeiten, verlinkt |
| `talente.md` | Alle Talentgruppen mit TaW, verlinkt |
| `zauber.md` | Alle Zauber — volle Tabelle + Wiki-Links + Notizen-Spalte |
| `rituale.md` | Alle Rituale, verlinkt |
| `ausruestung.md` | Nahkampfwaffen, Inventar, Geld |
| `steigerungs-log.md` | Chronologisches AP-Logbuch |

### YAML-Frontmatter-Schema

```yaml
---
typ: held
name: Vorname Nachname
rasse: Rasse
kultur: Kultur
profession: Profession (Schule/Akademie)
tradition: Gildenmagier | Hexe | Geode | …
stufe: 3
ap_gesamt: 3850
ap_verfuegbar: 3845
spieler: Name
---
```

### Wiki-Links

- Format: `[[wiki/dsa-4.1/<topic>/<slug>|Anzeigename]]`
- Immer prüfen, ob der Ziel-Artikel existiert. Falls nicht → Eintrag ohne Link + `## Offene Wiki-Verweise` am Ende der Datei.

### Steigerung

Bei jeder Steigerung:
1. `steigerungs-log.md` → neue Zeile eintragen
2. Betroffene Datei (`talente.md`, `zauber.md`, `_<name>.md`) → Wert aktualisieren
3. `_helden.md` (hier) → AP-Spalte aktualisieren
