# DSA 4.1 – Extraktions-Status

> **Handoff-Dokument.** Single source of truth für den Fortschritt der DSA-4.1-Regelwerk-Extraktion. Am Anfang jeder Session lesen, am Ende jedes Kapitels aktualisieren.

- **Original-Plan (permanent):** [raw/pdf-extracted/EXTRACTION-PLAN.md](raw/pdf-extracted/EXTRACTION-PLAN.md)
- **Konventionen:** [CLAUDE.md](CLAUDE.md)

---

## Bücher-Queue

Reihenfolge: Pilot → Kampf → Magie → Götter → Alchimie → Aventurien.

| # | Buch | Kürzel | PDF | Status |
|---|------|--------|-----|--------|
| 1 | Wege der Helden | WdH | `DSA 4.1 - Wege der Helden.pdf` | ✅ fertig |
| 2 | Wege des Schwertes | WdS | `DSA 4.1 - Wege des Schwertes.pdf` | ✅ fertig |
| 3 | Wege der Zauberei | WdZ | `DSA 4.1 - Wege der Zauberei.pdf` | 🟢 in Arbeit |
| 3a | Liber Cantiones | LC | `C01 - Liber Cantiones.pdf` | ⚪ offen (parallel zu WdZ) |
| 4 | Wege der Götter | WdG | `DSA 4.1 - Wege der Goetter.pdf` | ⚪ offen |
| 4a | Liber Liturgium | LL | `C02 - Liber Liturgium.pdf` | ⚪ offen (parallel zu WdG) |
| 5 | Wege der Alchimie | WdA | `DSA 4.1 - Wege der Alchimie.pdf` | ⚪ offen |
| 6 | Wege des Entdeckers | WdE | `DSA 4.1 - Wege des Entdeckers.pdf` | ⚪ offen |

Legende: 🟢 in Arbeit · 🟡 pausiert · ✅ fertig · ⚪ offen · ⏭️ übersprungen

---

## Aktives Buch: Wege des Schwertes

PDF: `C:\Users\David\Google Drive\DSA\DSA_Buecher\001. Regelwerke\005. DSA4.1\DSA 4.1 - Wege des Schwertes.pdf`  
Bulk-Text: `raw/pdf-extracted/wege-des-schwertes/full.txt`  
Kapitel-Splits: `raw/pdf-extracted/wege-des-schwertes/kapitel-*.txt`

### Kapitel-Fortschritt (WdS)

| Kapitel | Text-Datei | Ziel-Artikel | Status |
|---------|------------|--------------|--------|
| 01 Vorwort | `kapitel-01-vorwort.txt` | `buecher/wege-des-schwertes.md` | ⚪ offen |
| 02 Spielregeln in Kürze | `kapitel-02-spielregeln.txt` | ⏭️ überspringen (Kurzreferenz) | ⏭️ übersprungen |
| 03 Talente | `kapitel-03-talente.txt` | `talente/talentregeln.md` | ✅ fertig (Session WdS-01) |
| 04 Kampfregeln | `kapitel-04-kampf.txt` | `kampf/*.md` | ✅ fertig (Session WdS-02) |
| 05 Umfassende Regeln | `kapitel-05-umfassend.txt` | `grundregeln/*.md` | ✅ fertig (Session WdS-03) |
| 06 Abenteuerpunkte/Erfahrung | `kapitel-06-erfahrung.txt` | `grundregeln/erfahrung.md` | ✅ fertig (Session WdS-04) |
| 07–13 Anhänge | `kapitel-07-anhang-1-so.txt` u.a. | Sozialstatus, Waffen-/Rüstungstabellen, Meta-Talente, SF-Überblick, Strukturpunkte, Alterung, Tabellen | ✅ fertig (Session WdS-05) |
| 14 Index | `kapitel-14-index.txt` | — | ⏭️ überspringen |

### Wdh-Kapitel-Fortschritt (WdH — abgeschlossen)

| Kapitel | Text-Datei | Ziel-Artikel | Status |
|---------|------------|--------------|--------|
| 01 Inhaltsverzeichnis | `kapitel-01-inhalt.txt` | — | ⏭️ übersprungen (TOC) |
| 02 Vorwort | `kapitel-02-vorwort.txt` | `buecher/wege-der-helden.md` | ✅ fertig |
| 03 Charaktererschaffung / Grundregeln | `kapitel-03-erschaffung.txt` | `grundregeln/_grundregeln.md`, `proben.md`, `generierung.md`, `eigenschaften.md`, `steigerung.md` | ✅ fertig |
| 04 Rassen | `kapitel-04-rassen.txt` | `rassen/*.md` (16 Artikel) | ✅ fertig |
| 05 Kulturen | `kapitel-05-kulturen.txt` | `kulturen/*.md` (15 Artikel) | ✅ fertig |
| 06 Professionen | `kapitel-06-professionen.txt` | `professionen/*.md` (87 Dateien) | ✅ fertig (Sessions 06a–06f) |
| 07 Vor-/Nachteile | `kapitel-07-vor-nachteile.txt` | `vor-nachteile/*.md` | ✅ fertig (07a+07b+07c) |
| 08 Zwanzig Fragen | `kapitel-08-zwanzig-fragen.txt` | `grundregeln/zwanzig-fragen.md` | ✅ fertig |
| 09–14 Anhänge | `kapitel-09-anhang-1.txt` + `full.txt` L19982–23412 | Anh. 1–6: Exotik-Essay, Eigenbau, Namen, Talentliste, Zauber-/Liturgielisten | ✅ fertig (Anh. 1–4 extrahiert; Anh. 5+6 → WdZ/WdG) |
| 15 Index | `kapitel-15-index.txt` | — | ⏭️ überspringen (Stichwortindex) |

---

## Zentrale Design-Entscheidungen

| Thema | Entscheidung |
|-------|--------------|
| Ordnerstruktur | Topic-basiert (`rassen/`, `kulturen/`, `zauber/`, …), nicht buch-basiert |
| Index-Dateien | `_<ordnername>.md` pro Ordner (z.B. `_kulturen.md`), Unterstrich für Top-Sortierung + eindeutiger Graph-Name |
| Kulturen-Gruppierung | Gruppiert nach geographisch/rassischer Verwandtschaft (z.B. `nordaventurien-kulturen.md` mit 7 Kulturen), H2-Sektion pro Einzelkultur. Einzelartikel nur für prominente Stand-Alones (`norbardensippe.md`, `trollzacken-kultur.md`) |
| Rassen-Gruppierung | Eine Datei pro Rasse |
| Frontmatter | Nachschlage-Artikel: `typ`, `gp`, `quelle`, `seite`, `modifikatoren`. Kulturgruppen-Dateien: `typ: kulturgruppe` + `kulturen:` Liste |
| Geschlechtsspezifische GP | Im `gp`-Feld als String (`"4 (Männer) / 5 (Frauen)"`) — Dataview-Sortierung dadurch eingeschränkt |
| Wiki-Links | Immer `[[name]]` ohne `.md`-Suffix. Cross-Topic mit relativem Pfad: `[[../rassen/auelf]]` |
| Zitatblock | Jeder Kapitelartikel beginnt mit Quelle + Seiten als `> **Quelle:**`-Zeile |
| Errata | Direkt eingearbeitet, Fußnote `*(Errata <jahr>)*` |

---

## Offene Punkte / Folge-TODOs

- **Errata-Durchgang:** Sobald WdH komplett ist, `001. Errata/`-PDFs extrahieren und in betroffene Artikel einarbeiten.
- **Dataview-Schema:** Falls User Dataview nutzen will — `gp_m`/`gp_f` statt String für Novadi/Goblin; `leittalente:` Liste im elfischen Kultur-Frontmatter.
- **Zwanzig Fragen (Kap. 08):** Mit User klären, ob als Artikel gewünscht (Roleplay-Tool, keine Regel).
- **Anhänge (Kap. 09–14):** Vor Bearbeitung kurz prüfen, welche Listen drinstehen — sollen evtl. in WdS oder direkt in `talente/`/`sonderfertigkeiten/` einfließen.
- **Halbelf als Einzelartikel:** Gelegentlich prüfen, ob die Varianten-Differenzierung (Auelf/Firnelf/Waldelf) sauber genug umgesetzt ist.

---

## Workflow-Erinnerung

Pro Kapitel (interaktiv):

1. Status-Datei lesen → nächstes offenes Kapitel identifizieren
2. Ankündigung: "Starte Kapitel N — *Titel*. Geplante Artikel: X, Y, Z. OK?"
3. OK vom User abwarten
4. Bulk-Text + Read-Tool (für Tabellen-Seiten) → Artikel gemäß Template schreiben
5. `_<ordner>.md` und `_master-index.md` aktualisieren
6. **DSA-STATUS.md aktualisieren:** Kapitel auf ✅ setzen, nächstes auf 🟢
7. Abschlussreport: neue Dateien + offene Fragen

Details → [raw/pdf-extracted/EXTRACTION-PLAN.md](raw/pdf-extracted/EXTRACTION-PLAN.md).

---

## Kapitel 06 – Professionen: Sub-Session-Fortschritt

| Session | Kategorie | Artikel-Dateien | Status |
|---------|-----------|-----------------|--------|
| 06a | Kämpferische Professionen (L17–2051) | amazone, faehnrich, gladiator, gardist, jahrmarktskaempfer, ritter, krieger, schwertgeselle, soeldner, soldat, stammeskrieger, wuestenkrieger, tempelwache-rssah | ✅ fertig |
| 06b | Reisende + Wildnis (L2052–2825) | botenreiter, entdecker, fernhaendler, fischer, fuhrmann, grenzjaeger, grosswildjaeger, hirte, jaeger, karawanenfuehrer, kundschafter, prospektor, schiffer, schmuggler, seefahrer, strassenraeuber | ✅ fertig |
| 06c | Gesellschaftlich (L2826–3555) | ausrufer, barde, bettler, dieb, einbrecher, gaukler, haendler, herold, hofkuenstler, hoefling, kurtisane, privatlehrer, schriftsteller, spitzel, streuner, taugenichts, wirt | ✅ fertig |
| 06d | Handwerk + Wissen (L3556–4236) | bader, bauer, bergmann, domestik, edelhandwerker, gelehrte, handwerker, rattenfaenger, schreiber, tageloehner, tierbaendiger, wundarzt | ✅ fertig |
| 06e-1 | Magisch Block 1 (L4237–5224) | alchimistin, derwisch, druide, durro-dun, elfische-professionen, ferkina-besessene, geode | ✅ fertig |
| 06e-2 | Magisch Block 2 (L5225–7863) | hexe, kristallomantin, magier, scharlatan, schelm, zaubertaenzer, zibilja | ✅ fertig |
| 06f | Geweihte (L7864–10291) | praios-geweihter, rondra-geweihte, efferd-geweihter, travia-geweihte, boron-geweihte, hesinde-geweihte, firun-geweihter, tsa-geweihte, phex-geweihter, peraine-geweihte, ingerimm-geweihter, rahja-geweihte, halbgoetter-geweihte, nicht-alveranische-geweihte, rur-gror-priester, schamanische-professionen, ork-goblin-schamanen | ✅ fertig |

---

## Letzte Aktivität

- **2026-04-25:** Session WdZ-09 abgeschlossen — 3 neue Artikel aus WdZ Kapitel 14 (S. 369–386): `magie/satinav-zeitmagie.md` (Zeitempfinden der Rassen, Satinav-Mythologie Schiff der Zeit/Ymra/Fatas, Zeitgesetze keine Paradoxe, CHRONONAUTOS-Zeitreise-Regeln, 7 Formeln der Zeit, historische Zeitfrevel, vollst. Zeiteinheiten-Tabelle), `magie/elemente-hexalogien.md` (6 Elemente Essenz/Zuordnung, Zitadellen, Affinitäten/Gegensatzpaare, Paramanthus-Analogien-Tabelle, 7-stufige Reinheitsskala, Traditionen-Übersicht, Hexalogien-Mechanik + vollst. Hexalogien-Katalog ~12 Einträge, element. Sekundärschäden-Tabelle, Mindergeister), `magie/edelsteine-wahre-namen.md` (Kristallomantie-Geschichte, spieltechn. Nutzung, Edelstein-Katalog 21 Steine mit Gott/Wirkung/Heilkunde, Wahre Namen: MR 0/¾ AsP, Wesen-Übersicht: Kobolde/Einhörner/Gargyle/Drachen). `_magie.md` aktualisiert. WdZ Kapitel 14 ✅.
- **2026-04-25:** Session WdZ-08 abgeschlossen — 1 neuer Artikel aus WdZ Kapitel 13 (S. 354–368): `magie/welt-sphaeren.md` (Weltbilder 10+ Völker, Sieben-Sphären-Modell vollständig mit allen 7 Sphären, Limbus-Spielregeln: Schaden/AsP/Kampf/Magie-Tabellen, 6-Ebenen-Struktur, Globulen + 7 Beispiele inkl. Tharun/Lichtwelt/Feenwelten, Parallelwelten 3 Beispiele, Kraftlinien: LS/KS-System SF Kraftlinienmagie I/II, 5 bedeutende Linien, Kritische Essenz-Tabelle 26-Stufen). `_magie.md` aktualisiert. WdZ Kapitel 13 ✅.
- **2026-04-25:** Session WdZ-07 abgeschlossen — 2 neue Artikel aus WdZ Kapitel 12 (S. 252–297): `magie/chronica-magica.md` (Epochen-Zeitstrahl Vorzeit bis 1029 BF, Chal'ashtarra-Zyklus, berühmte Zauberer, Tabelle untergegangener Magierschulen), `magie/magische-gilden.md` (Weiße/Graue/Schwarze Gilde mit Philosophie/Akademien/Mitgliedschaft, Magiersiegel-System, Gildenwechsel/Gildenlose ~600, Borbaradianer, 5 magische Orden-Profile, Akademiephasen Eleve/Novize/Studiosus). `_magie.md` aktualisiert. WdZ Kapitel 12 ✅.
- **2026-04-25:** Session WdZ-06 abgeschlossen — 7 neue Artikel aus WdZ Kapitel 10 (S. 175–232) und Kapitel 11 (S. 250–251): `invokation/invokation-grundregeln.md` (Anrufungsprobe, Kontrollwert-Formeln, vollst. Dienste-Katalog 20+ Einträge, Bannung, misslungene Beschwörung/Beherrschung-Tabellen, SF-Liste), `invokation/elementarwesen.md` (6 Elemente × 3 Stufen Stat-Blöcke, AsP-Bereitschaft, Beschwörungsregeln), `invokation/geister.md` (5 Geistertypen mit Stat-Blöcken, Geisterruf-Regeln), `invokation/daemonen.md` (Allgemeine Dämoneneigenschaften, I.INTEGRA, Pandämonium-Kompakttabelle ~30 Dämonen, Erzdämonen-Übersicht), `invokation/untote-nekromantie.md` (SKELETTARIUS vs. TOTES HANDLE, 5 Untoten-Typen + Tierkadaver, Nephazz-Belebung, Freie Untote-Regeln), `invokation/chimaeren-golems.md` (Erschaffungsthesis, Wert-Berechnung, 6 Chimären-Beispiele inkl. Harpyie/Mantikor/Schlangenmensch, Daimonide, Golem-Material-Tabelle, 3 Golem-Beispiele), `invokation/besessenheit.md` (Körperlich vs. geistig, Willenskraftproben, Probenintervalle nach MR, Austreibungsmethoden). `invokation/_invokation.md` angelegt, `_dsa-4.1.md` aktualisiert. Kapitel 10+11 ✅.
- **2026-04-25:** Session WdZ-05 abgeschlossen — 7 neue Artikel aus WdZ Kapitel 09 (S. 128–174): `rituale/geoden-rituale.md` (Ring des Lebens, 10 Rituale, Gestalt aus Rauch, Trank des ungehinderten Weges), `rituale/druiden-rituale.md` (5 Herrschaftsrituale mit Mondphasen-Tabelle, 12 Dolchzauber-SF), `rituale/zibilja-rituale.md` (14 Rituale, Sippen-Mechanik, Seffer Manich/Neroth), `rituale/schamanenrituale.md` (4 Ritualfertigkeiten, Modifikatoren, Grade I–VI, ~30 Rituale 10 Kulturen, Knochenkeule 10 SF), `rituale/durro-dun-rituale.md` (5 Odûn-Stufen Hauch/Haut/Blut/Ruf/Seele, 9 Odûn-Tiergestalten mit Vollbeschreibung), `rituale/ferkina-rituale.md` (Anach-Nûr-System, Kontrollmechanik, 15 Tierarten-Tabelle mit KW/MH/ÜB), `rituale/derwisch-trommelrituale.md` (Dabla-Probenmechanik, 5 Trommelrituale, Glaubensbindung). `_rituale.md` aktualisiert. WdZ Kapitel 09 komplett.
- **2026-04-25:** Session WdZ-04 abgeschlossen — 7 neue Artikel: `magie/zauberer-steigerung.md` (ZfW-Lernschwierigkeit, Leiteigenschaften KL/IN-Tabelle, RK-Spalten D/E/G, Große Meditation 400 AP Leiteigenschaft/3 AsP, Gefäß der Sterne SF, pAsP-Rückkauf 50 AP/25 ZE, Zweitstudium Adeptus Maior, Imitationslernen Schelme IN+7, 5 weitere SF), `magie/magische-bibliothek.md` (Bücher als Lehrmeister/Thesis/Rekonstruktion, Format V/K/Wert, Rekonstruktions-Code-Erklärung, Bücherkatalog 25+ Werke), `rituale/_rituale.md` (neuer Ordner-Index), `rituale/rituale-grundregeln.md` (Apport/Bannschwert/Druidenrache, allg. Objektritual-Regeln), `rituale/stabzauber.md` (alle 13 Stabzauber + Kristallkugel-Kugelzauber), `rituale/hexenrituale.md` (Hexenbesen, Vertrautenbindung 12 Tierarten + Tiersinne-Tabelle, 11 Vertrautenzauber), `rituale/elfenlieder.md` (5 Elfenlieder + 10 Zaubertänze Nov/Tul/Maj/Haz), `rituale/kristallomanten-rituale.md` (Schliff-Tabelle, Kristallbindung/Formung/Thesiskristall/Madakristall/Matrixkristall/Kristallkraft bündeln/Schuppenbeutel). Kapitel 08–09 (WdZ) teils abgeschlossen. Noch offen: Geoden-, Druiden-, Zibilja-, Schamanenrituale → WdZ-05.
- **2026-04-25:** Session WdZ-03 abgeschlossen — 3 neue Artikel: `magie/artefakte.md` (ARCANOVI-Herstellungsmechanik mit ZfP*-Tabelle und pAsP-Kosten-Formel, Analyse-Tabelle ANALYS 0–19+ ZfP*, Entzauberungs-Modifikatoren DESTRUCTIBO, Zauberwaffen magisch/geweiht/dämonisch alle Kategorien, Glyphenmagie + Runenzauberei Grundregeln, 8 Beispielglyphen/-runen mit Komplexität/AP-Kosten, Bann/Schutzkreise, 10 SF Artefaktherstellung), `magie/alchimie.md` (Brauen mit Qualitätszahl-Formel, Qualitätsstufen A–F, Zauber in Alchimie, astrales Aufladen AsP-Tabelle, Analyse-Methoden, 14 Rezepturen mit Probe/Wirkung/Preis/Haltbarkeit), `magie/traummagie.md` (8 Definitionen, RD-Berechnungsformel mit Dämonentabelle, Traumwelt-Eigenschaften Ersetzungstabelle, Probe Heilkunde Seele Modifikatoren, Kampf/Schaden-RD-Tabellen, Zaubern-Tabelle, Traumbrechen-Zauber, Traumdrogen-Tabelle mit 8 Substanzen, SF Traumgänger 150 AP). Kapitel 06–07 (WdZ) abgeschlossen.
- **2026-04-24:** Session WdZ-02 abgeschlossen — 2 neue Artikel: `magie/zauber-sonderregeln.md` (Bann des Eisens mit Rüstungs-/Waffen-/Fesselungs-/Koschbasalt-Tabellen, Verbotene Pforten SF mit LeP→AsP-Mechanik, Blutmagie mit allen Quellarten und Nebenwirkungen, Magiedilettanten alle 3 Formen: Meisterhandwerk/Schutzgeist/Übernatürliche Begabung), `magie/metamagie.md` (Kleine und Große Modifikations-Tabellen mit allen Zuschlägen, schrittweise Forschungsmechanik mit Monatsproben, Fixierungskosten AF×20/40 AP, Kostenveränderungen, Repräsentations-Vor/Nachteile-Tabelle, SF Matrixkontrolle 300 AP, Freizauberei). Kapitel 04–05 (WdZ) abgeschlossen.
- **2026-04-24:** Session WdZ-01 gestartet — 3 neue Artikel: `buecher/wege-der-zauberei.md` (Buchprofil, Dreifach-Staffelung, was nicht enthalten ist), `magie/magie-grundlagen.md` (Astralenergie, AsP, Basis-AE-Berechnung, vollst. Regen.-Tabelle, Astrale Meditation, pAsP-Rückkauf, Arten der Zauberei), `magie/zauberregeln.md` (ZfW-System, Zauberprobe, Erschwernisse-Tabelle, 9 Repräsentationen mit Leiteigenschaften, vollst. Spontane-Mod.-Tabelle mit allen 14 Modifikationstypen inkl. Reichweiten-Stufen, Wechselwirkungen, Ausdauer beim Zaubern, 11 SF). Kapitel 01–03 (WdZ) abgeschlossen.
- **2026-04-24:** Session WdS-05 abgeschlossen — **Wege des Schwertes komplett.** 8 Artikel aus Anhängen 1–7: `grundregeln/sozialstatus.md` (SO 1–21, Lebensstil, Feste, Veränderungsregeln), `grundregeln/strukturpunkte.md` (StP/Härte/Struktur, Objektbeispiele, Strukturproben), `grundregeln/alterung.md` (7 Rassen × 6 Stufen + weitere, Eigenschaftsverluste, Elfen-Ausnahme), `talente/meta-talente.md` (Pirschjagd, Ansitzjagd, Nahrung Sammeln, Kräuter Suchen), `kampf/waffen-herstellung.md` (TaP\*-Formel, Zeitbedarfstabelle, Verbesserungen, Material/Technik-Tabelle mit Endurium/Titanium/Zwergenstahl/Geflämmt u.a., Reparaturregeln), `kampf/kampf-referenztabellen.md` (Ausweichen, Distanzklassen, Bruchtest, Trefferzonen, Patzer NK/FK, vollständige Fernkampf- und Reiterkampf-Tabellen), `sonderfertigkeiten/waffenmeister.md` (400 AP, 15-Punkte-Baukasten, Waffenmeister-Schild), `talente/sprachen-schriften.md` (~35 Sprachen in Familien + ~24 Schriften). Nächstes Buch: WdZ (Wege der Zauberei).
- **2026-04-24:** Session WdS-04 abgeschlossen — `grundregeln/erfahrung.md` mit vollständiger SKT (Spalten A*–H, TaW –3 bis 31+, Spalten-Zuordnung aller Talente/Werte), AP-Konto-Mechanik, AP-Vergabe-Richtlinien, Steigerungsregeln für Talente/Eigenschaften/LeP/AuP/AsP/MR/SF, alle 4 Lernmethoden (SE, Lehrmeister, gegenseitiges Lehren, Selbststudium), Nachteilsabbau, späterer Vorteils-Erwerb, Zauberer-Erweiterungen (ZfW, RK, Große Meditation, Rückkauf pAsP, Zweitstudium, Schamanenrituale) und Geweihten-Erweiterungen (LkP, KaP-Queste, Liturgien erlernen/verfassen/rekonstruieren mit Mirakelproben-Tabelle). Nächste Session: WdS-05 Anhänge.
- **2026-04-24:** Session WdS-03 abgeschlossen — `grundregeln/bewegung-reisen.md` (Zeit/Maße, taktische Bewegung mit GS/Sprint/Dauerlauf/Schwimmen/Tauchen/Sprung, vollständige Reisegeschwindigkeits-Tabellen mit Gelände/Wetter/Boden-Modifikatoren, Last & Tragkraft, optionale Erschöpfungs-Regeln) und `grundregeln/umfassende-regeln.md` (6 Schadensquellen: Sturz/Kälte/Hitze/Feuer/Ersticken/Verdursten/Verhungern mit vollständigen Tabellen; ~20 Gifte mit Vollmechanik; ~20 Krankheiten inkl. Wundfieber-Tabelle; Suchtkrankheiten; vollständige Heilungs-/Regenerations-Tabellen). Nächste Session: WdS-04 Abenteuerpunkte/Erfahrung.
- **2026-04-24:** Session WdS-02 abgeschlossen — `kampf/kampfregeln.md` mit vollständiger Kampfmechanik (WdS S. 44–114): AT/PA/FK-Formulas, Initiative-System, alle ~35 Angriffs-/Abwehrmanöver mit SF-Voraussetzungen, vollständige Kampf-SF-Tabelle, optionale Regeln (Distanzklassen, Wunden/Schmerzen, Ausdauer, Passierschlag, Bruchfaktor, Glückliche Schläge/Patzer, Meucheln/Betäuben), Waffenloser Kampf mit allen Kampfstilen und Manövern, Fernkampf mit Modifikator-Tabellen, Reiterkampf, Trefferzonensystem, Kampf gegen Tiere. Nächste Session: WdS-03 Umfassende Regeln (Kapitel 05).
- **2026-04-24:** Session WdS-01 abgeschlossen — `talente/talentregeln.md` mit vollständigen Talentbeschreibungen aller 7 Gruppen (Körperlich, Gesellschaftlich, Natur, Wissen, Sprachen/Schriften, Handwerk), Probendetails (offene Probe, vergleichende Probe, TaP*-Ansammlung, Kritikergebnisse), Werkzeug-Modifikatoren, Heilkunde-Wunden-Detail-System mit Zuschlag-Tabelle, Sprachfamilien-Übersicht, Schriften-Tabelle und 10 Talent-SF (Berufsgeheimnis, Fälscher, Geländekunde, Kulturkunde, Meister der Improvisation, Nandusgefälliges Wissen, Ortskenntnis, Rosstäuscher, Standfest, Talentspezialisierung). Nächste Session: WdS-02 Kampfregeln.
- **2026-04-24:** Kapitel 09–14 (Anhänge) abgeschlossen — 4 neue Artikel: `talente/talentliste.md` (alle ~80 Talente, 7 Kategorien), `grundregeln/exotik-kombinationen.md` (Ork/Goblin/Achaz-Spielbarkeit, Sonderfälle), `grundregeln/eigenbau.md` (GP-Formeln für eigene Rassen/Kulturen/Professionen), `grundregeln/aventurische-namen.md` (~25 Kulturen Namenskonventionen). Anhänge 5+6 (Zauber-/Liturgielisten) zurückgestellt auf WdZ/WdG-Sessions. **Wege der Helden komplett.**
- **2026-04-24:** Kapitel 08 abgeschlossen — `grundregeln/zwanzig-fragen.md` mit allen 20 Fragen als kompakte Tabelle.
- **2026-04-24:** Session 07c abgeschlossen — `sonderfertigkeiten-allgemein.md` mit allen 4 SF-Typen (~11 allgemeine, ~55 Kampf-SF inkl. Waffenloser Kampftechniken, ~55 magische inkl. aller Traditions-SF, 8 klerikale). Kapitel 07 Vor-/Nachteile komplett. Nächste Session: Klärung Kapitel 08 (Zwanzig Fragen) und Sichtung Kapitel 09–14 (Anhänge).
- **2026-04-24:** Session 07b abgeschlossen — `nachteile.md` mit ~65 Nachteilen (allgemeine, körperliche Behinderungen, ~25 magische) + `schlechte-eigenschaften.md` mit SE-Mechanik und ~30 SE-Einträgen.
- **2026-04-24:** Session 07a abgeschlossen — `vorteile.md` mit ~70 Vorteilen (allgemeine, magische, Gaben, Geweiht-Tabelle). `_vor-nachteile.md` mit Platzhaltern für 07b+07c angelegt.
- **2026-04-24:** Session 06f abgeschlossen — 17 Artikel für alle Geweihten-Professionen (12 Zwölfgötter, Halbgötter, Nicht-alveranische, Rur-Gror/Hadjinim, schamanische Professionen, Ork/Goblin-Schamanen). Kapitel 06 Professionen komplett. _professionen.md mit vollständiger Geweihten-Sektion aktualisiert. Nächste Session: 07 Vor-/Nachteile.
- **2026-04-24:** Session 06e-2 abgeschlossen — 7 Artikel (Hexe, Kristallomantin, Magier, Scharlatanin, Schelmin, Zaubertänzer, Zibilja) in `professionen/`. Magische Professionen Block 2 (L5225–L7863) fertig. Alle ~40 Magier-Akademien als Übersichtstabelle in magier.md.
- **2026-04-24:** Session 06e-1 abgeschlossen — 7 Artikel (Alchimistin, Derwisch, Druide, Durro-Dûn, Elfische Professionen, Ferkina-Besessene, Geode) in `professionen/`. Magische Professionen Block 1 (L4237–L5224) fertig.

- **2026-04-23:** Session 06d abgeschlossen — 12 Profession-Artikel für ~70 Professionen und Varianten (Handwerks- und Wissens-Professionen) in `professionen/`. Kategoriesektion in `_professionen.md` eingetragen.
- **2026-04-23:** Session 06c abgeschlossen — 17 Profession-Artikel für ~35 Professionen und Varianten (Gesellschaftliche Professionen) in `professionen/`. Kategoriesektion Gesellschaftliche Professionen in `_professionen.md` eingetragen.
- **2026-04-23:** Session 06b abgeschlossen — 16 Profession-Artikel für ~60 Professionen und Varianten (Reisende & Wildnis) in `professionen/`. Kategoriesektion Reisende & Wildnis in `_professionen.md` eingetragen.
- **2026-04-22:** Session 06a abgeschlossen — 13 Profession-Artikel für ~70 Professionen und Varianten in `professionen/`. Kategoriesektion Kämpferische Professionen in `_professionen.md` eingetragen.
- **2026-04-22 (früher):** 17× `_index.md` umbenannt zu `_<ordner>.md`, 84 Wiki-Links aktualisiert, CLAUDE.md angepasst.
- **Davor:** Kapitel 5 (Kulturen) abgeschlossen — 14 Artikel-Dateien für ~50 Kulturen in `kulturen/`.
