# Kampfregeln (WdS)

> **Quelle:** Wege des Schwertes (WdS), S. 44–114 · **Thema:** Vollständige Kampfregeln DSA 4.1 – Grundmechanik, Manöver, Sonderfertigkeiten, Waffenloser Kampf, Fernkampf, Reiterkampf, Trefferzonensystem.

---

## Kampfwerte

| Wert | Formel |
|------|--------|
| AT-Basis | (MU + GE + KK) / 5 |
| PA-Basis | (IN + GE + KK) / 5 |
| FK-Basis | (IN + FF + KK) / 5 |
| INI-Basis | (MU + MU + IN + GE) / 5 |

**TaW-Aufteilung:** TaW wird auf AT und PA verteilt (Unterschied max. 5 Punkte). Maximaler TaW = max(GE, KK) + 3; für Fernkampftalente max(FF, GE, KK) + 3.

---

## Kampfrunde & Initiative

- **Kampfrunde** ≈ 3 Sekunden. Jeder Kämpfer hat in der Regel **1 Angriffsaktion + 1 Abwehraktion** pro Runde.
- **Initiative:** INI-Basis + 1W6. Bei Überzahl: +1 INI pro Kopf Überzahl (max. +4).
- **eBE:** effektive Behinderung = BE der Rüstung minus Waffenmodifikator. INI = INI-Basis − BE (dann + 1W6).

### Aktionstypen

| Typ | Beschreibung |
|-----|-------------|
| Freie Aktion | Schritt, Rufen, Waffe fallen lassen, kurze Geste; 2 pro Runde |
| Reguläre Aktion | AT, PA, Position, Orientieren, 1 Kampfrunde Arbeit |
| Längerfristige Aktion | Zaubern, Sprinten; nimmt mehrere KR in Anspruch |

---

## Angriff (AT) und Verteidigung (PA)

- **Probe:** W20 ≤ AT-Wert (Basis + TaW-Anteil − eBE − Situationsmodifikatoren).
- **Parade:** W20 ≤ PA-Wert. Misslingt → Schaden trifft den Verteidiger.
- **Ausweichen (Freie Aktion):** Probe auf PA-Basis (−1 pro zusätzlichem Gegner über den ersten); kostet INI−4.
- **Gezieltes Ausweichen (Reguläre Aktion):** wie Ausweichen, aber INI−8.

### Schaden

| Begriff | Bedeutung |
|---------|-----------|
| TP | Trefferpunkte (echter Schaden, geht von LE ab) |
| SP | Schadenspunkte = TP − RS |
| TP(A) | Ausdauerschaden: zuerst von AU abgezogen, dann ½ von LE |

---

## Rüstung

- **RS:** schützt pro Treffer (SP = TP − RS; min. 0).
- **BE:** Behinderungswert; jede Waffe hat einen WM, der BE für eBE-Berechnung senkt.
- **eBE:** BE − WM der Waffe (min. 0). Zieht von AT und PA ab (bei ungerade: PA −1 mehr).
- **INI:** −BE (voller BE-Wert, nicht eBE).

### Rüstungsgewöhnung

| SF | Effekt |
|----|--------|
| Rüstungsgewöhnung I | Bestimmter Rüstungstyp: BE −1 |
| Rüstungsgewöhnung II | Alle Rüstungen: BE −1 (nicht kumulativ mit I) |
| Rüstungsgewöhnung III | Alle Rüstungen: BE −2 + INI-Abzug nur (BE−2)/2 |

---

## Lebensenergie-Schwellen & Wunden

| Schwelle | Folge |
|----------|-------|
| LE ≤ 5 | Kampfunfähig (optional: ignorierbar per SB-Probe +12) |
| LE = 0 | Lebensbedrohend: stirbt in W6 KR × KO ohne Erste Hilfe |
| LE < −KO | Tot |

**Optional – LE-Abzüge:**
- LE < ½: +1 Erschwernis auf AT/PA/Eigenschaften, +3 auf Talente/Zauber
- LE < 1/3: +2 / +6
- LE < 1/4: +3 / +9

### Wunden

Entstehen wenn SP > KO/2 (Wundschwelle):

| SP-Überschreitung | Wunden |
|-------------------|--------|
| SP > KO/2 | 1 Wunde |
| SP > KO | 2 Wunden |
| SP > 1,5×KO | 3 Wunden |

**Auswirkung pro Wunde:** AT, PA, FK, INI, GE je −2; GS −1.

Im Waffenlosen Kampf ist die Wundschwelle um 2 erhöht (Wunden seltener).

---

## Besondere Kampfsituationen (Modifikationstabelle)

| Situation | AT | PA |
|-----------|----|----|
| Blindkampf / totale Dunkelheit | +8 | +8 |
| Schlechte Sicht / Dämmerung | +2 bis +4 | +2 bis +4 |
| Knie-/hüfttiefes Wasser | +2 / +4 | +2 / +4 |
| Schultertiefes Wasser | +8 | +8 |
| Falscher Hand (unausgebildet) | +9 | +6 |
| Pro Gegner über den ersten | – | +1 PA |
| Liegend / kniend | +4 | +4 |
| Gegner liegt / kniet | −4 | – |
| Rückenwind | −2 | – |
| Unbekannte Waffe | +2 | +2 |

---

## Angriffsmanöver

Alle Manöver basieren auf dem **Ansage-System:** Der Kämpfer erschwert sich freiwillig die AT um X Punkte und gewinnt bei Gelingen X Punkte Bonus-Effekt. Misslingt ein angesagtes Manöver → Erschwernis auf nächste Aktion in Höhe der Ansage.

| Manöver | Ansage / Erschwernis | Effekt | SF nötig |
|---------|---------------------|--------|----------|
| **Wuchtschlag** | frei wählbar | +Ansage auf TP | KK 12 |
| **Finte** | frei wählbar | gegnerische PA −Ansage | GE 12, AT-Basis ≥ 8 |
| **Ausfall** | – | Abwehraktion → Angriff (kein Malus); Gegner muss 2× parieren | KO 12, SF Finte |
| **Niederwerfen** | +4 | Gegner muss KK-Probe, sonst zu Boden; weitere Ansage erschwert Probe | SF Wuchtschlag |
| **Betäubungsschlag** | variabel | TP(A), kann Gegner k.o. schlagen | SF Finte + Wuchtschlag |
| **Gezielter Stich** | +4 | Umgeht RS, erzeugt automatisch Wunde | SF Finte |
| **Hammerschlag** | +8 | TP stark erhöht | MU 15, SF Niederwerfen |
| **Todesstoß** | +8 + halber RS | Leichte Wunden + automatische Wunden | MU 15, SF Gezielter Stich |
| **Klingensturm** | − | AT-Wert aufgespalten auf 2 Gegner | AT-Basis 9, SF Ausfall + Kampfreflexe |
| **Befreiungsschlag** | +4 | Rundumschlag gegen bis zu 3 Gegner | KK 15, MU 12, SF Niederwerfen |
| **Sturmangriff** | +4 AT | +TP(GS/2 +4) aus vollem Lauf | MU 12, SF Wuchtschlag |
| **Schildspalter** | − | Gezielter Angriff auf Schild; kann Schild zerstören | KK 15, SF Niederwerfen |
| **Umreißen** | − | Gegner zu Boden, kein Schaden | KK 12, SF Finte |
| **Festnageln** | − | Gegner am Boden halten | GE 13, KK 13 |
| **Entwaffnen (AT)** | +8 | Waffe aus Hand schlagen | KK 12, SF Binden |
| **Meisterliches Entwaffnen** | +8 | auch Zweihandwaffen entwaffnen | GE 15, SF Entwaffnen |
| **Doppelangriff** | +4 AT | gleichzeitig beide Waffen; Gegner braucht 2 PA | SF Beidhändiger Kampf I |
| **Tod von Links** | − | Zusatzangriff mit Parierwaffe | SF BK I + Parierwaffen II |
| **Schild-Attacke** | − | Angriff mit Schild (Raufen-AT) | SF Schildkampf I |
| **Stumpfer Schlag** | variabel | TP(A) statt TP; Betäubung möglich | SF Betäubungsschlag |

---

## Abwehrmanöver

| Manöver | Erschwernis | Effekt | SF nötig |
|---------|------------|--------|----------|
| **Parade** | −eBE | Normale Abwehraktion | – |
| **Ausweichen (Freie Aktion)** | – (−1/Gegner) | PA auf PA-Basis; INI −4 | – |
| **Gezieltes Ausweichen** | variabel | PA auf PA-Basis; INI −8; Flucht möglich | – |
| **Binden** | +Ansage | Gegnerische Waffe binden: nächste feindliche PA −Ansage, eigene AT +Ansage | IN+GE ≥ 12, SF Meisterparade od. Parierwaffen I |
| **Defensiver Kampfstil** | – | Angriff → Parade ohne −4 Malus; 2 PA pro Runde | GE 12, SF Meisterparade |
| **Meisterparade** | +Ansage | Erschwerte PA → nächste Aktion um Ansage erleichtert | PA-Basis ≥ 8 |
| **Klingenwand** | − | PA aufgespalten auf 2 Gegner | SF Klingenwand |
| **Gegenhalten** | +4 AT (Gegner) | Abwehraktion = simultaner Gegenangriff; bei Unentschieden gilt bessere AT | MU 15, GE 12, SF Meisterparade |
| **Formationsparade** | − | Kämpfer in Formation pariert auch für Nachbarn | SF Formation |
| **Windmühle** | +8 oder mehr | Gegnerischen Wuchtschlag auffangen und als eigenen Angriff zurücklenken | SF Gegenhalten + Wuchtschlag |
| **Entwaffnen aus Parade** | +8 PA | Waffe des Angreifers fangen und entwaffnen | KK 12, PA-Basis 9, SF Binden |
| **Waffe zerbrechen** | +8 PA | Gegnerische Klinge zerbrechen (+ KK-Probe) | KK 12, SF Parierwaffen I |
| **Parade mit Parierwaffe** | – | PA = Hauptwaffe PA − Linkhand-Abzug + WM Parierwaffe | SF Linkhand (+ Parierwaffen I/II) |
| **Parade mit Schild** | − | PA-Wert des Schilds; WM Schild gilt für AT | SF Linkhand (+ Schildkampf I/II) |
| **Zweite Parierwaffen-Parade** | – | Zusätzliche PA mit Parierwaffe pro KR | SF Parierwaffen II |
| **Zweite Schildparade** | – | Zusätzliche Schildparade pro KR | SF Schildkampf II, BE ≤ 4 |

---

## Sonderfertigkeiten im bewaffneten Nahkampf (Auswahl)

| SF | Kurzbeschreibung | AP |
|----|-----------------|-----|
| Aufmerksamkeit | INI auf Maximum in 1 Aktion; Passierschlag gegen ihn +4 erschwert | 200 |
| Ausfall | Ermöglicht Ausfall-Manöver | 200 |
| Ausweichen I/II/III | Ausweichen +3/+6/+9 | 300/200/200 |
| Beidhändiger Kampf I | Umwandeln ohne −4 Malus; KK-Bonus für linke Hand | 100 |
| Beidhändiger Kampf II | Zusätzliche AT oder PA pro Runde mit Zweitwaffe | 400 |
| Befreiungsschlag | Rundumschlag-Manöver | 100 |
| Betäubungsschlag | Betäubungsschlag-Manöver | 200 |
| Binden | Binden-Manöver | 200 |
| Blindkampf | Abzüge durch Dunkelheit max. −2/−2 | 200 |
| Defensiver Kampfstil | Umwandeln ohne −4 Malus | 100 |
| Doppelangriff | Doppelangriff-Manöver | 100 |
| Entwaffnen | Entwaffnungs-AT oder -PA | 200 |
| Festnageln | Festnageln-Manöver | 200 |
| Finte | Finte-Manöver verbessert | 200 |
| Formation | Formationsparade-Manöver | 100 |
| Gegenhalten | Gegenhalten-Manöver | 200 |
| Gezielter Stich | Gezielter-Stich-Manöver | 100 |
| Halbschwert | Waffe in kürzerer DK ohne volle Abzüge | 150 |
| Hammerschlag | Hammerschlag-Manöver | 200 |
| Improvisierte Waffen | Improvisierte Waffen wie reguläre nutzen | 100 |
| Kampfgespür | INI +2; PA frei aufspalten (mit Klingensturm/-wand) | 300 |
| Kampfreflexe | INI +4 (BE ≤ 4) | 300 |
| Klingensturm | AT aufgespalten auf 2 Gegner | 100 |
| Klingentänzer | INI-Basis + 2W6; halbierte Ansage-Strafe; PA auf 3 Gegner | 400 |
| Klingenwand | PA aufgespalten auf 2 Gegner | − |
| Linkhand | PA-Basis +1; −AT/PA nur −6/−6 mit falscher Hand | 300 |
| Meisterliches Entwaffnen | Auch Zweihandwaffen entwaffnen | 100 |
| Meisterparade | Meisterparade-Manöver | 200 |
| Niederwerfen | Niederwerfen-Manöver | 100 |
| Parierwaffen I/II | Parierwaffe effektiver einsetzen; II: Zusatz-PA | 200/200 |
| Rüstungsgewöhnung I/II/III | BE-Reduktion 1/1/2 | 150/300/450 |
| Schildkampf I/II | PA mit Schild +3 / +5; II: zweite Schildparade | 200/200 |
| Schnellziehen | Waffe als Freie Aktion ziehen (Gürteldolch) | 200 |
| Spießgespann | Pike von 2 Personen gemeinsam führen | 100 |
| Sturmangriff | Sturmangriff-Manöver | 100 |
| Tod von Links | Zusatzangriff mit Parierwaffe | 100 |
| Todesstoß | Todesstoß-Manöver | 200 |
| Umreißen | Umreißen-Manöver | 100 |
| Unterwasserkampf | Keine Abzüge unter Wasser | 200 |
| Waffe zerbrechen | Gegnerische Klinge zerbrechen | 200 |
| Waffenmeister (Waffe) | Zugang zu Waffenmeister-Sonderfähigkeiten | 400 |
| Waffenspezialisierung | +1/+1 AT/PA mit Waffe; mehrere möglich | 20×AF |
| Windmühle | Windmühle-Manöver | 200 |
| Wuchtschlag | Wuchtschlag-Manöver verbessert | 200 |

---

## Optionale Kampfregeln (Nahkampf)

### Überraschung und Hinterhalt
- Überraschung: Start mit INI-Basis (kein W6); IN-Probe zum Einwürfeln (alle 2 KR um 2 erleichtert).
- Hinterhalt: Verteidiger braucht IN-Probe (−3 bei Fernwaffen) um überhaupt parieren zu dürfen.

### Distanzklassen (DK)
Vier Klassen: **H** (Handgemenge), **N** (Nahkampf), **S** (Stangenwaffe), **P** (Pike).

| Situation | AT | PA |
|-----------|----|----|
| Waffe 1 Klasse zu kurz | −6 | +/−0 |
| Waffe 1 Klasse zu lang | −6 | −6 |
| Waffe 2+ Klassen zu kurz | unmöglich | +/−0 |
| Waffe 2+ Klassen zu lang | unmöglich | unmöglich |

Annäherung (DK verringern): Nicht parierte AT nötig. Entfernung (DK vergrößern): AT +4 (kein Treffer).

### Umwandeln von Aktionen
AT → PA oder PA → AT: Umgewandelte Aktion um −4 erschwert. Findet bei INI−8 statt. Nicht möglich mit: Kettenwaffen, Peitsche, Zweihandflegel, Zweihand-Hiebwaffen, allen improvisierten Waffen (>2 Schritt) — außer bei SF Defensiver Kampfstil / Aufmerksamkeit / Kampfgespür.

### TP/KK (Körperkraft-Bonus)
- Schwellenwert (z.B. 11): Kämpfer mit KK < Schwelle: −1 TP pro Schadensschritt unter Schwelle; KK > Schwelle: +1 TP pro Schadensschritt darüber.
- Auch bei Unterschreitung: −1 AT/PA pro Schadensschritt unter Schwelle.

### Glückliche Schläge und Patzer
- **Glückliche Attacke:** Würfelergebnis 1 → immer Treffer; Prüfwurf → Kritischer Treffer (TP verdoppelt, automatisch 1 Wunde).
- **Glückliche Parade:** Würfelergebnis 1, Prüfwurf → Freie Aktion (Parade verbraucht nichts).
- **Patzer (AT/PA 20):** Prüfwurf; misslingt → Tabelle 2W6 (Sturz, Waffe verloren, Eigentreffer, Zerstörung).
- Patzer: Verlust aller weiteren Aktionen der Runde.

### Bruchfaktor (BF)
Ausgelöst bei: Kritischem Treffer mit Parade; Wuchtschlag/Hammerschlag-Ansage ≥ +10 mit Parade; Schildspalter/Waffe zerbrechen.
- Würfle 2W6: ≤ BF → Waffe/Schild zerbricht; > BF (nicht 12) → BF steigt +1; 12 → unverändert.

### Meucheln und Betäuben
- Voraussetzung: Opfer ahnungslos (Schleichen-Probe).
- **Töten:** AT +5/+8 erleichtert; TP ×3, ignorieren RS, +Wunde. Nur mit Dolch/Fechtwaffe/Schwert.
- **Betäuben:** Kurze Hiebwaffe oder Raufen; TP(A), ignorieren RS; bei AU-Verlust > WS → KO-Probe.

### Wunden und Schmerzen (optional)
Bei Wunde: SB-Probe (um SP über WS erschwert) oder W6+3 KR am Boden.

### Ausdauer im Kampf (optional)
- Schwere Manöver kosten 1 AuP (Wuchtschlag, Hammerschlag, Sturmangriff, Ausweichen, etc.)
- Schwere Rüstung: +1 AuP pro Aktion × (BE−3) / 3.
- Wunde: +1W6 AuP-Verlust.
- AU < 1/3: +1 Eigenschaft, +3 Talent; AU < 1/4: +2/+6; AU = 0: kampfunfähig.

### Passierschlag
Gegen Kämpfer, der sich durch Kontrollbereich bewegt (rennt, lässt los, landet aus Ausweichen): Freie Aktion, AT +4 erschwert, nicht parierbar; senkt INI des Opfers um 1W6.

---

## Waffenloser Kampf

### Grundregeln
- AT/PA wie im bewaffneten Kampf berechnet (TaW aufgeteilt, max. 5 Diff.).
- eBE = BE (voller Wert, kein WM-Abzug).
- INI-Modifikator: 0 (waffenlos gegen waffenlos); −2 (gegen Bewaffnete).
- DK: Handgemenge.
- Schaden: TP(A) (AU −1, LE −½); TP/KK 10/3 (Wundschwelle +2).

### Raufen
Schläge, Tritte, Kopfstöße, Bisse usw. – 1W6 TP(A) (Knauf: 1W6+2 TP(A)).

### Ringen
Griffe, Klammern, Würfe, Schwitzkasten – 1W6 TP(A) oder Positionsnachteil für Gegner.

### Waffenlose Kampfstile (Sonderfertigkeiten)

| Stil | Voraussetzungen | Manöver-Bonus | Kosten |
|------|----------------|---------------|--------|
| Bornländisch | Raufen + Ringen je 5 | +1 PA Ringen | 100 AP |
| Gladiatorenstil | Raufen + Ringen je 7 | +1 AT/PA Raufen oder Ringen | 150 AP |
| Hammerfaust | Raufen 7 | +1 AT/PA Raufen | 150 AP |
| Hruruzat | Raufen 10, Ringen 7 | +1 AT/PA Raufen; Tritte 2W6 TP(A) | 200 AP |
| Mercenario | Raufen 10, Ringen 7 | +1 AT/PA Raufen | 200 AP |
| Unauer Schule | Ringen 10 | +1 AT/PA Ringen; Entwinden +2 | 150 AP |

Alle Stile: +1 AT/PA; max. +2 AT/PA durch mehrere Stile.

### Waffenlose Manöver (Auswahl)

| Manöver | Typ | Effekt | AP |
|---------|-----|--------|-----|
| Auspendeln | Raufen/Ringen-PA | Ohne: PA gegen Gerade/Schwinger/Schmetterschlag +4 | 30 |
| Beinarbeit | Raufen/Ringen-PA | Ohne: PA gegen Fußfeger/Knie/Tritt +4 | 30 |
| Biss | Raufen-AT | Ansage → +TP(A); Parade mit Waffe → voller echter Schaden | 40 |
| Block | Raufen-PA | Waffenloser Binden; Ansage → nächste PA des Gegners erschwert | 30 |
| Doppelschlag | Raufen-AT | Beide Fäuste, +4; Verteidiger braucht 2 PA | 50 |
| Eisenarm | Raufen-PA | Bewaffneten Angriff ohne Selbstschaden parieren | 60 |
| Fußfeger | Raufen-AT | Ansage; Gegner muss GE-Probe sonst zu Boden (−2W6 INI) | 40 |
| Gerade | Raufen-AT | Ansage → +TP(A) | 30 |
| Griff | Ringen-AT | Gegner erhält Erschwernisse in Höhe halber Ansage auf alle Aktionen | 30 |
| Handkante | Raufen-AT | Ansage → +TP; SP > KO/2 → echte Wunde (kein WS-Bonus) | 60 |
| Halten | Ringen-AT/PA | Ansage → nächste Gegneraktion erschwert | 40 |
| Hoher Tritt | Raufen-AT | DK N; ohne Auspendeln/Kreuzblock PA +4 | 40 |
| Klammer | Ringen-AT | Gegner kann nur Biss/Knie/Schwitzkasten/Würgegriff | 40 |
| Knie | Raufen-AT | 1W6+2 TP(A); bei Männern: WS-Überschreitung → kampfunfähig W3 KR | 30 |
| Knaufschlag | Raufen-AT | 1W6+2 TP(A) mit Waffenknauf | 50 |
| Kopfstoß | Raufen-AT | 1W6 TP(A); Parade mit Waffe → voller echter Schaden | 40 |
| Kreuzblock | Raufen-PA | Waffenlose Meisterparade; Punkte für PA-Erschwernis und AT-Erleichterung | 50 |
| Niederringen | Ringen-AT | Beide zu Boden; Angreifer −1W6 INI, Gegner −2W6 INI | 40 |
| Schmetterschlag | Raufen-AT | Verstärkte Gerade; SP(A) > WS → KO-Probe oder 1W6 SR bewusstlos | 50 |
| Schmutzige Tricks | Raufen/Ringen-AT | 1W6 AU/INI-Verlust; ignoriert Rüstung | 60 |
| Schwitzkasten | Ringen-AT | Automatisch +1W6+n TP(A) pro KR; folgende PA des Angreifers +n erleichtert | 20 |
| Sprungtritt | Raufen-AT | AT +4; 2W6 TP(A); DK N möglich; misslungene Waffenparade → voller Schaden | 50 |
| Tritt | Raufen-AT | Ansage → +TP(A) | 30 |
| Versteckte Klinge | Raufen-AT | DK-H-Waffe mit Raufen-Werten führen | 50 |
| Würgegriff | Ringen-AT | Automatisch 1W6+2 TP(A)/KR, nicht parierbar | 30 |
| Wurf | Ringen-AT | AT +4; 1W6 TP(A); Gegner zu Boden (−2W6 INI) | 40 |

### Unbewaffnet gegen Bewaffnet
- PA-WM: −2; gelungene PA = halber Schaden des Angreifers.
- Misslungene PA: voller Schaden.
- AT-WM: −1; bei parierter Waffe (nicht Schild): halber Schaden für Angreifer.

---

## Fernkampf

### Grundmechanik
- **Probe:** W20 ≤ FK-Wert (FK-Basis + TaW − alle Modifikatoren).
- Ist Summe aller Modifikatoren > FK-Wert → automatischer Fehlschuss (kein Automatiker bei 1).
- Für jeden Schuss: Laden + 1 Aktion Anvisieren (ohne = Schnellschuss +2).

### Zielgröße-Modifikatoren

| Kategorie | Modifikator |
|-----------|------------|
| Winzig (Münze, Maus) | +8 |
| Sehr klein (Schlange, Katze) | +6 |
| Klein (Wolf, Schaf) | +4 |
| Mittel (Mensch, Ork) | +2 |
| Groß (Pferd, Troll) | +/−0 |
| Sehr groß (Drache, Elefant) | −2 |

**Deckung:** Halbkörper = 1 Klasse kleiner; Kopf = 2 Klassen kleiner. Großer Schild = 1 Klasse kleiner, sehr großer Schild = 2 Klassen.
**Bewegung:** Stillstehend = 1 Klasse größer; schnell/Zickzack = 2 Klassen kleiner.
**Sicht:** Dämmerung +2, Mondlicht +4, Sternenlicht +6, Finsternis/Unsichtbar +8.

### Entfernungsklassen (nach Waffe)

| Klasse | Modifikator |
|--------|------------|
| Sehr nah | −2 |
| Nah | +/−0 |
| Mittel | +4 |
| Weit | +8 |
| Extrem weit | +12 |

### Weitere Modifikatoren

| Situation | Modifikator |
|-----------|------------|
| Schnellschuss | +2 (+1 Scharfschütze, +0 Meisterschütze) |
| 2. Schuss pro KR | +4 |
| Steilschuss nach unten | +2 |
| Steilschuss nach oben | +4 (+8 Wurfwaffe) |
| Böiger Seitenwind | +4 |
| Starker böiger Seitenwind | +8 |
| Schuss ins Kampfgetümmel (S/N-DK) | +2 pro Beteiligtem |
| Schuss ins Handgemenge | +3 pro Beteiligtem |
| Vom galoppierenden Reittier | +8 (Schuss) / +4 (Wurf) |

### Sonderfertigkeiten im Fernkampf

| SF | Effekt | AP |
|----|--------|-----|
| Berittener Schütze | Nur halbe Reittier-Erschwernis; kein Reiten-Probe nötig | 200 |
| Eisenhagel | Bis zu 5 Wurfscheiben/-sterne gleichzeitig | 150 |
| Scharfschütze | Schnellschuss nur +1; Gezielte Schüsse Zuschlag ×0,66; Zielen −1/Aktion | 300 |
| Meisterschütze | Kein Schnellschuss-Abzug; Zielen −1/Aktion; Gezielter Schuss ×½ | 300 |
| Schnellladen (Bogen/Armbrust) | Ladezeit −1 Aktion (Bogen) / ×0,75 (Armbrust) | 200 |
| Schnellziehen | Wurfwaffe als Freie Aktion aus Gürtelscheide | 200 |

### Optionale Fernkampfregeln

- **Fernkampfangriff mit Ansage:** Selbst erschwert um X → +X/2 TP bei Treffer.
- **Zielen:** Pro 2 Aktionen (1 Aktion für Scharf-/Meisterschütze) −1 Erschwernis (max. −4).
- **Glückstreffer (1):** Prüfwurf → Kritischer Fernkampftreffer (TP ×2, +1 Wunde).
- **Patzer (20):** Patzertabelle Fernkampf: Waffe zerstört / beschädigt / Fehlschuss / Kameraden getroffen.
- **Körperkraft:** Wurfwaffen TP/KK: Diskus/Wurfbeil 13/3, Wurfmesser 13/5, Wurfspeer 12/3.

### Fernkampf abwehren
- **Ausweichen:** +4 (Wurfwaffen), +8 (Pfeile/Bolzen/Kugeln).
- **Schildparade:** +4 (Wurfwaffen), +8 (Pfeile/Bolzen).
- Nicht ausweichen oder mit Schild parieren, wenn man im Nahkampf ist.

---

## Reiterkampf

### Grundregeln
- Reiten-Probe zu Kampfbeginn: TaP*/2 → INI-Bonus.
- Misslingt INI-Probe: Keine Angriffsaktionen in dieser KR.
- **eBE für Reiter:** halbe BE (beim Lanzenangriff: 0 BE).

### Reiten-Probe-Modifikatoren

| Situation | Modifikator |
|-----------|------------|
| Ungearbeitetes Pferd | +6 |
| Unerfahrenes Pferd | +3 |
| Erprobtes Pferd | +/−0 |
| Geschultes Pferd | −3 |
| Ohne Sattel/Steigbügel | +6 |
| Freihändig lenken | +4 |
| Pro Gegner beim Anreiten | +3 |
| Nach Reiter-Treffer | + erlittene SP |
| Nach Pferd-Treffer | + erlittene SP |

Sturz: 2W6+4 SP(A); mit KO-Probe (GE, be−eBE): 1W6+4 SP(A). Danach: −5 INI.

### Sonderfertigkeiten Reiterkampf

| SF | Effekt | AP |
|----|--------|-----|
| Reiterkampf | Reiten-Proben halbiert; AT gegen Fußkämpfer +3 erleichtert | 200 |
| Kriegsreiterei | Reiten-Proben geviertelt; ermöglicht Niederreiten, Hufschlag, Trampeln | 300 |
| Turnierreiterei | Lanzenreiten +5; Reiten-Probe nach Treffer halbe Erschwernis | 100 |

### Manöver zu Pferd

| Manöver | Regeln |
|---------|--------|
| **Sturmangriff** | Galopp-Strecke = GS Schritt; Reiten +6 und AT +4; +GS/2 TP extra | Reiterkampf |
| **Niederreiten** | Reiten +6 anstatt AT; automatisch Angriff zum Niederwerfen; TP nach Tabelle | Kriegsreiterei |
| **Hufschlag/Auskeilen** | Reiten +6; TP wie Tier; Schildparade möglich; zählt als Niederwerfen | Kriegsreiterei |
| **Trampeln** | Gegen liegende Gegner; TP ×2; Ausweichen +8 | Kriegsreiterei |
| **Lanzenangriff (Fußkämpfer)** | Reiten-Probe + Lanzenreiten-AT; Erschwernis nach Zielgröße | Reiterkampf |
| **Lanzengang** | Beide Reiter gleichzeitig; Anlaufstrecken addiert; Reiten-Probe zum Anreiten | Reiterkampf |

### Treffertabelle Reiterangriffe

| Angriff | bis 5 Schritt | bis 15 Schritt | ab 16 Schritt |
|---------|-------------|---------------|--------------|
| Niederreiten / Turnierlanze (A) | 1W6 | 2W6 | 2W6+2 (TP(A)) |
| Dschadra | 1W6+4 | 2W6+4 | 3W6+4 (A) |
| Kriegslanze | 1W6+5 | 2W6+5 | 3W6+5 |
| Kriegslanze (Spitze) | 1W6+6 | 2W6+8 | – |

---

## Trefferzonensystem (Optional)

Bei jeder Attacke: gleichzeitig W20-Würfelwurf für Trefferzone (zusätzlicher Würfel).

### Trefferzonen und Wundauswirkungen

| Zone | Zufall (W20) | 1.–2. Wunde | 3. Wunde |
|------|-------------|------------|---------|
| Kopf | 19–20 | MU/KL/IN/INI-Basis −2, INI −2W6 | +2W6 SP, bewusstlos, Blutverlust |
| Brust | 15–18 | AT/PA/KO/KK −1; +1W6 SP | bewusstlos, Blutverlust |
| Arme | 9–14 | AT/PA/KK/FF −2 (betroffener Arm) | Arm handlungsunfähig |
| Bauch | 7–8 | AT/PA/KO/KK/GS/INI-Basis −1; +1W6 SP | bewusstlos, Blutverlust |
| Beine | 1–6 | AT/PA/GE/INI-Basis −2; GS −1 | Sturz, kampfunfähig |

### Gezielter Schlag
AT-Erschwernis = 2 + Zonen-Zuschlag (Kopf +4, Brust/Bauch +2, Arme +4/+6, Beine +2). Erfordert SF Finte.

---

## Kampf gegen Tiere

### Größenklassen

| Klasse | Beispiele | AT-Erschwernis | PA-Einschränkung | FK |
|--------|-----------|---------------|-----------------|-----|
| Winzig | Maus, Ratte | +4–+8 | Keine PA, nur Ausweichen | +8 |
| Sehr klein | Katze, Rabe | +2–+4 | Waffen-PA +4–+8 | +6 |
| Klein | Wolf, Schaf | +/−0 | Normal | +4 |
| Mittel | Mensch, Orc | +/−0 | Normal | +2 |
| Groß | Pferd, Troll | +/−0 | Nur Schild-PA | +/−0 |
| Sehr groß | Drache, Riese | +/−0 | Keine PA, nur Ausweichen | −2 |

### Besonderheiten
- Gelungene Waffenparade gegen Tier: Tier erleidet halbe TP der Waffe (kein TP/KK).
- Tier kämpft in seiner Umgebung ohne Abzüge; Helden erleiden Wasser/Luft/Dunkel-Modifikatoren.
- Tiere fliehen bei ≤ 1/3 LE (Vögel früher); bei 0 LE tot.
- Nicht möglich gegen Tiere: Ausfall, Entwaffnen, Finte, Schildspalter, Waffe zerbrechen.

---

## Key Takeaways

- Das **Ansage-System** (freiwillige AT-Erschwernis für Manöver-Bonus) ist das Herzstück aller Kampfmanöver.
- **eBE** vermindert AT und PA; **BE** allein reduziert INI – wichtig: verschiedene Werte.
- **Wunden** entstehen ab SP > KO/2 und geben kumulative −2 Malus auf alle Kampfwerte.
- Der **Waffenlose Kampf** verursacht primär TP(A); echte Lebenspunkt-Schäden entstehen kaum ohne Spezialtechniken (Handkante, Würgegriff).
- **Fernkampf:** Keine automatischen Treffer bei 1 (wenn Summe Modifikatoren > FK-Wert); Schüsse ins Kampfgetümmel sind sehr riskant.
- **Reiterkampf:** eBE halbe BE; Reiten-Probe bei jedem Schaden fällig; Streitrösser kämpfen eigenständig.
- Das **Trefferzonensystem** ist optional, verlangsamt Kämpfe kaum, bietet aber deutlich mehr taktischen Detailgrad.
- Die Kapitel-Struktur folgt dem **Baukastensystem:** Grundregeln ohne optionale Regeln funktionieren; Optionale Regeln in beliebiger Kombination hinzufügbar.

---

## Verwandte Artikel

- [[talentliste|Talentübersicht]] — Kampftalente mit AT/PA/FK-Werten und eBE
- [[talentregeln|Talentregeln (WdS)]] — Probenregeln, Kritikergebnisse
- [[sonderfertigkeiten|Sonderfertigkeiten-Übersicht]] — SF-Kosten und Voraussetzungen
- [[rüstungsliste|Waffenliste & Rüstungstabelle]] *(geplant)* — Waffen-WM, BF, TP-Werte, Rüstungs-RS/BE
- [[waffenmeister|Waffenmeister-Sonderfähigkeiten]] *(geplant)* — S. 190ff.
