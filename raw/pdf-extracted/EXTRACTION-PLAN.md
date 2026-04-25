# DSA 4.1 – Extraktions-Plan (permanent)

> Langfristiger Referenzplan für die systematische Extraktion der DSA-4.1-Regelwerke.
> Fortschrittsverfolgung läuft über [../../DSA-STATUS.md](../../DSA-STATUS.md).

## Kontext

Ziel: Die offiziellen DSA-4.1-Regelwerk-PDFs (Ulisses Spiele) werden **Teil für Teil** in eine granulare, topic-basierte Wiki-Referenz überführt. Ergebnis soll beim Spielen schnelles Nachschlagen ermöglichen, mit sauberen Verlinkungen und eingearbeiteten Errata.

Quelle der PDFs:
```
C:\Users\David\Google Drive\DSA\DSA_Buecher\001. Regelwerke\005. DSA4.1\
```

Die Rohmaterialien sind urheberrechtlich geschützt. `raw/pdf-extracted/**` ist daher `.gitignore`d (außer `_tools/`).

## Zielarchitektur

```
wiki/
├── _master-index.md
├── dsa-4.1/
│   ├── _dsa-4.1.md
│   ├── buecher/                 # Kurzprofil pro Quellenbuch
│   ├── grundregeln/             # eigenschaften, proben, generierung, steigerung
│   ├── rassen/                  # je Rasse eine Seite
│   ├── kulturen/                # gruppiert nach geogr./rass. Verwandtschaft
│   ├── professionen/
│   ├── vor-nachteile/
│   ├── sonderfertigkeiten/
│   ├── talente/
│   ├── kampf/                   # Manöver, Waffen, Rüstungen
│   ├── magie/                   # Traditionen, Merkmale, Meta-Regeln
│   ├── zauber/                  # je Zauber eine Seite (LC)
│   ├── rituale/                 # flach, Frontmatter tradition:
│   ├── liturgien/               # je Liturgie eine Seite (LL)
│   ├── goetter/
│   ├── alchimie/
│   └── geographie/              # Aventurien (WdE)
```

Jeder Unterordner hat `_<ordnername>.md` als Übersicht.

## Artikel-Templates

**A) Kapitel-/Themenartikel** (z.B. `grundregeln/proben.md`)
- Kein YAML-Frontmatter
- Zitatblock mit Quelle + Seiten
- Fließtext mit H2/H3-Sektionen
- `## Key Takeaways`, `## Verwandte Artikel`

**B) Nachschlage-Einheit** (z.B. `rassen/auelf.md`, `zauber/ignifaxius.md`)
- YAML-Frontmatter (`typ`, `gp`, `quelle`, `seite`, `modifikatoren`) für Dataview-Queries
- Kurzbeschreibung, Modifikator-Tabelle, Pflicht-Vor-/Nachteile (verlinkt), kombinierbare Kulturen (verlinkt)
- `## Errata` nur wenn vorhanden
- `## Verwandte Artikel`

**C) Ordner-Index** (`_<ordnername>.md`)
- Übersichtstabelle: Name → Kurzbeschreibung → Quelle + Seite
- Alle Einträge als `[[wiki links]]`

**Wiki-Links:** Immer ohne `.md`-Endung. Cross-Topic mit relativem Pfad.

## Extraktions-Pipeline

Einmalig pro Buch (Bulk-Text):
```bash
mkdir -p raw/pdf-extracted/<buch-slug>
pdftotext -layout -enc UTF-8 \
  "C:/Users/David/Google Drive/DSA/DSA_Buecher/001. Regelwerke/005. DSA4.1/DSA 4.1 - <Buchname>.pdf" \
  raw/pdf-extracted/<buch-slug>/full.txt
```

Kapitel-Split:
- `raw/pdf-extracted/_tools/split-chapters.py` — splittet `full.txt` per Regex in `kapitel-NN-<slug>.txt`
- Regex-Profile pro Buch parametrisiert

Pro Kapitel – Dual-Lesung:
1. Bulk-Text `kapitel-XX.txt` lesen → Inhaltsverständnis
2. Für tabellenlastige Seiten (Waffentabellen, Zauberboxen, Professionsboxen): PDF-Seiten direkt mit Read-Tool visuell lesen (bis 20 Seiten pro Aufruf)
3. Artikel gemäß Template schreiben

**Errata-Merge:** Errata-PDFs aus `001. Errata/` mit `pdftotext` extrahieren, Korrekturen direkt in betroffene Artikel einarbeiten mit `*(Errata <jahr>)*`-Fußnote.

## Workflow pro Kapitel (interaktiv)

1. **Status lesen:** `DSA-STATUS.md` → nächstes offenes Kapitel identifizieren
2. **Ankündigung:** "Starte Kapitel N — *Titel*. Geplante Artikel: X, Y, Z. OK?"
3. **OK vom User abwarten** (kein Autopilot)
4. **Extraktion:** Bulk-Text + gezieltes Read-Tool für Tabellen
5. **Artikel schreiben** + betroffene `_<ordner>.md` + `wiki/_master-index.md` aktualisieren
6. **Status aktualisieren:** Kapitel auf ✅ setzen, nächstes auf 🟢 markieren, "Letzte Aktivität" ergänzen
7. **Abschlussreport:** neue Dateien, getroffene Entscheidungen, offene Fragen

## Bücher-Reihenfolge

1. **Wege der Helden (WdH)** – Pilotbuch: Charaktererschaffung, Rassen, Kulturen, Professionen, Vor-/Nachteile
2. **Wege des Schwertes (WdS)** – Kampf & Talente
3. **Wege der Zauberei (WdZ) + Liber Cantiones (LC)** – Magie-Regelwerk + Zauber
4. **Wege der Götter (WdG) + Liber Liturgium (LL)** – Geweihte + Liturgien
5. **Wege der Alchimie (WdA)** – Alchimie
6. **Wege des Entdeckers (WdE)** – Geographie & Aventurien

Jedes neue Buch startet mit einem Mini-Pilot (Kapitel 1) als Checkpoint.

## Rituale vs. Zauber vs. Liturgien (Struktur-Entscheidung)

- `zauber/` — einzelne Zauber (flach, Frontmatter `haus`/`komplexität`/`merkmale`)
- `rituale/` — einzelne Rituale aller Traditionen (Stabzauber, Kugelzauber, Hexenflüche, Schelmenzauber, Alchimie, Beschwörungen, Bann-/Schutzkreise, …), flach mit Frontmatter `tradition:`
- `liturgien/` — einzelne Liturgien der Gottgeweihten
- Mechanische Meta-Regeln der drei Kategorien in `magie/` bzw. `goetter/` (z.B. `magie/rituale-grundlagen.md`, `magie/zauberprobe.md`, `goetter/liturgien-grundlagen.md`)
- Ritualkenntnis-SF (z.B. *Ritualkenntnis: Stabzauber*) in `sonderfertigkeiten/`, verlinken auf ihre Ritual-Artikel

## Verifikation pro Kapitel

- [ ] Alle geplanten Artikel existieren und folgen dem Template
- [ ] `_<ordner>.md` des betroffenen Topics listet die neuen Artikel
- [ ] `wiki/_master-index.md` ist aktualisiert, falls neuer Topic-Ordner hinzukam
- [ ] Mindestens ein Deep-Link-Test in Obsidian (Klick auf `[[wiki link]]` springt korrekt)
- [ ] Stichprobenvergleich: zwei zufällige Artikel-Inhalte gegen die PDF-Seite prüfen
- [ ] `DSA-STATUS.md` aktualisiert (Kapitel ✅, neue Aktivität ergänzt)
