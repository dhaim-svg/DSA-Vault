# Errata-Durchgang DSA-4.1-Wiki — Audit-Report

**Datum:** 2026-05-15  
**Scope:** Offizielle Ulisses-Errata für 5 Bücher (WdH, WdS, WdZ, WdG, WdA) eingearbeitet.  
**LC, LL, WdE:** Keine Errata-PDFs vorhanden — ausgeschlossen.

---

## Gesamtübersicht

| Buch | Errata-Quelle | APPLY | ADD | SKIP | NOT-IN-WIKI | Dateien | Commit |
|------|---------------|------:|----:|-----:|------------:|--------:|--------|
| WdH | Errata-2007-08 | 29 | 10 | 12 | 22 | 37 | `9ef8896` |
| WdS | Errata-2008-11 | 30 | 14 | 4 | 14 | 7 | `af3b61c` |
| WdZ | Errata-2011-08 | 22 | 13 | 16 | 16 | 15 | `c7bbc8e` |
| WdG | Errata-2009-12 | 18 | 4 | 2 | 6 | 22 | `4d7183b` |
| WdA | Errata-v2.1 | 40 | 12 | 15 | 6 | 14 | `5543013` |
| **Gesamt** | | **139** | **53** | **49** | **64** | **~95** | 5 Commits |

**Errata-Fußnoten im Wiki nach Abschluss:** 186 (`grep "(Errata " wiki/dsa-4.1/`)

---

## Triage-Definitionen

| Klasse | Bedeutung |
|--------|-----------|
| **APPLY** | Regel-, Zahlen-, Tabellen-Korrektur — inline `*(Errata <jahr>)*` |
| **ADD** | Fehlender Satz / neue Klarstellung — `## Errata`-Block am Artikelende |
| **SKIP** | Reiner Typo/Layout/Verweis-Fix im Original — kein Wiki-Edit |
| **NOT-IN-WIKI** | Inhalt nicht extrahiert (Index, Einzelakademien, Charakterbogen, …) |

---

## WdH — Wege der Helden (Errata 2007)

**Quelle:** `raw/pdf-extracted/errata/wdh-2007.txt` (304 Zeilen)  
**Wichtigste Korrekturen:**
- Kulturen-Mapping: "Yaquirien" → "Almada" in 5 Rassen-/Kulturdateien
- GP-Werte: Resistenz gegen alle Gifte = 25 GP, Vorteil Geweiht nichtmenschlich = 16 GP
- SF-Kosten: Gefäß der Sterne 250 AP, Zauberkontrolle 100 AP (Elfen 50 AP)
- Rassen: Wilde Zwerge FF+1 gestrichen; Stammeskrieger 3× Vorteile gestrichen
- Sonderfertigkeiten: 9 Korrekturen in `sonderfertigkeiten-allgemein.md`
- Vorteile: Begabung [Sprachen] gilt auch für Schriften; Begabung [Zauber] nur Kultur/Prof-Zauber
- Eigenbau: Fremdsprachen Spalte A

**NOT-IN-WIKI-Hauptgruppen:** Einzelakademien (9×), keine GP-Tabellen für Nicht-Menschen-Kulturen, Charakterbogen

---

## WdS — Wege des Schwertes (Errata 2008)

**Quelle:** `raw/pdf-extracted/errata/wds.txt` (237 Zeilen, zweispaltig)  
**Wichtigste Korrekturen:**
- TaW-Maximum: "0 bis 24" (statt 25)
- Manöver: Ausfall −4/−8 auf PA; Entwaffnen vollständige Talent-Liste; Meucheln TP(A) echt gerundet
- Kampf mit mehreren: Ausweichen +2/Gegner (nicht +1), max. +4
- SF Linkhand: 225 AP (Linkshänder) / 150 AP (Beidhändig)
- SF Aufmerksamkeit: Verbreitung 6; SF Unterwasserkampf: Verbreitung 2
- Ausweichen-Tabelle: Athletik → Akrobatik (S. 66/197)
- Heilkunde Wunden: mind. 2 KR Dauer; 7 TaP* nur bei Erstversorgung

**NOT-IN-WIKI-Hauptgruppen:** Waffentabellen-Einzeleinträge, Rüstungstabelle, Panzerstecher, Fernwaffentabelle

---

## WdZ — Wege der Zauberei (Errata 2011)

**Quelle:** `raw/pdf-extracted/errata/wdz-2011.txt` (209 Zeilen)  
**Wichtigste Korrekturen:**
- SF Zauberkontrolle (S. 17): "unabhängig von ZfW bereits nach 1 Aktion"
- Magische Waffen (S. 56): Natürliche Waffen zauberkundiger Wesen = magische Angriffe
- Große Meditation: Formel präzisiert (Leiteigenschaft/3 AsP)
- pAsP-Rückkauf: Basis-AE vs. Kapazität-Klarstellung
- SF Tierischer Begleiter (S. 76): vollständiger Beschreibungstext ersetzt
- Invokation: 13 Punkte in `invokation-grundregeln.md` (Rudel, Dienste, Kosten)
- Bannakademie Ysilia: Gildenzugehörigkeit Weiß→Grau→aufgelöst

**NOT-IN-WIKI-Hauptgruppen:** LUCIFERI-Referenzen in Freitext, Gegenstände verfluchen, Rahjas-Begehren-Tanz

---

## WdG — Wege der Götter (Errata 2009)

**Quelle:** `raw/pdf-extracted/errata/wdg-2009.txt` (102 Zeilen)  
**Hinweis:** Errata trotz 2. Auflage nicht eingedruckt (internes Missverständnis beim Drucker).  
**Wichtigste Korrekturen:**
- Sonnenlegion Gründungsdatum: "um 200 v.BF" → "um BF" (`praios.md`)
- Dritte Dämonenschlacht: 1022 BF → 23./24. ING 1021 BF (`religion-alltag.md`)
- Swafnir Primärliturgie: Tranksegen (nicht Speisesegen) (`swafnir.md`)
- Liturgie-Grundregeln: 6 Korrekturen (zweite Liturgiekenntnis −7, Modifikatoren, Varianten, Aufstufung)
- 5 Liturgien: Zielobjekt G→P korrigiert
- Lykanthropie: Ansteckungsregel 5% pro SP ergänzt
- Kor-Kirche: Purgation nicht vorhanden, Zauberer trotzdem unerwünscht

**NOT-IN-WIKI-Hauptgruppen:** Hermelinmaske (Artefakt), Keta-ajaban-kud'a (Abenteuer-Liturgie)

---

## WdA — Wege der Alchimie (Errata v2.1)

**Quelle:** `raw/pdf-extracted/errata/wda-2.1.txt` (439 Zeilen) — einzige verwertbare Version (wda-alt.txt war kein gültiges PDF)  
**Wichtigste Korrekturen:**
- Alchimie-Grundregeln: Zurückhalten-Formel (1,5 × Brau-Schwierigkeit − Labormodifikator)
- Gegenstands-Elixiere: Stabilisatum Qual. F (nur "temporäre" Verzauberung)
- Artefaktherstellung: Zaubertalisman ZfP*-Division nach Komplexität; Wiederaufladen vollständig neu; Matrixgeber+Kraftspeicher als Kombinationsartefakt
- Artefakt-Experten: Kristallomanten Thesiskristall, Gemeinschaftliche Erschaffung (UNITATIO-Mechanik), 22 SFs vollständig
- Arkanoglyphen: 6 Korrekturen (Gezücht des Meisters, Hermetisches Siegel, Zeichen der Zauberschmiede)
- Bannkreise: Transportabilitätseinschränkung, Wahrer Name +7-Wert
- Runen: Salzwasserrune, Waffenrune (Verkleinerungsregel), Wogensturmrune
- Register Artefakte: Artefaktpreise neu (~200 D/pAsP), 6 Artefakt-Korrekturen

**NOT-IN-WIKI-Hauptgruppen:** Satinavs Siegel Grafik, Zhayad Grafik, Index-Markierungen

---

## Offene Punkte nach dem Errata-Durchgang

1. **LC/LL/WdE-Errata:** Keine Errata-PDFs existieren für diese 3 Bücher — kein Handlungsbedarf.
2. **Halbelf-Varianten-Check** (aus altem Folge-TODO): Ob Auelf/Firnelf/Waldelf korrekt differenziert sind.
3. **Dataview-Schema** (optional): `gp_m`/`gp_f` statt String für bessere Queries.
4. **Errata-Index:** Für schnellen Zugriff auf alle korrigierten Werte könnte `output/errata-index.md` als Grep-Referenz dienen (`grep "(Errata" wiki/ -rn`).
