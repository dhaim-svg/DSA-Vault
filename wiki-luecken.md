# Wiki-Lücken — DSA 4.1

Audit-Logbuch: Wiki-Inhalte, die beim praktischen Einsatz (Helden, Abenteuer, Steigerung) als unvollständig oder fehlend auffallen.

Format pro Eintrag: Datum · betroffene Wiki-Datei · Befund · Vorschlag.

---

## 2026-05-15 — Audit-Lauf 1 (ausgelöst durch Illaen-Erstellung)

### L1: Stoerrebrandt-Kolleg — Detail-Artikel ✅ *behoben 2026-05-15*

- **Neue Datei:** `wiki/dsa-4.1/professionen/akademien/stoerrebrandt-kolleg-riva.md` (WdH S. 192–193)
- **Inhalt:** Beide Zweige (Berater + Leibwächter) mit Voraussetzungen, V/N, SF, Hauszaubern, Startausrüstung, SO-Rahmen, Startgeld.
- **Noch offen:** Restliche ~38 Akademien — keine Priorität für Illaen, künftiger Audit-Lauf.

### L2: Startgeld-Generierungsregel ✅ *behoben 2026-05-15*

- **Geänderte Datei:** `wiki/dsa-4.1/grundregeln/generierung.md` — neuer Abschnitt `## Startgeld`
- **Formel:** `(SO × SO) Silbertaler`; Adlig verdoppelt; Ausrüstungsvorteil addiert; Profession kann abweichen.
- **Quelle:** WdH S. 22.

### L3: Kulturartikel ohne Standardkleidung ✅ *behoben 2026-05-15 (Mittelländische Städte)*

- **Geänderte Datei:** `wiki/dsa-4.1/kulturen/mittellaender-kulturen.md` — neue Sektion `## Typische Ausrüstung`
- **Befund:** WdH hat „Tracht und Bewaffnung"-Abschnitte pro Kultur (S. 40). Mittelländer: einfache Kleidung, Gugel/Kapuze, Dolch, Grundlagen Hellebarde/Armbrust.
- **Systemisch offen:** Andere Kulturen noch nicht nachgepflegt — bei Bedarf (nächster Held oder Audit).

### L5: Magische SF — Einzel-Artikel fehlten ✅ *behoben 2026-05-15*

- **Neue Datei:** `wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten.md` — 11 SF vollständig (Astrale Meditation, Große Meditation, Meisterliche Regeneration, Konzentrationsstärke, Kraftkontrolle, Merkmalskenntnis, Repräsentation, Ritualkenntnis Gildenmagie, Verbotene Pforten, Zauber bereithalten, Zauberkontrolle).
- **Offen (nicht in Scope):** Allgemeine SF (Aufmerksamkeit, Kulturkunde, Ortskenntnis, Regeneration I/II) — Quelle WdH, noch nicht extrahiert.

### L6: Stabzauber-Detailregeln (Kraftfokus, Merkmalsfokus, Modifikationsfokus) ✅ *behoben 2026-05-15*

- **Geänderte Datei:** `wiki/dsa-4.1/rituale/stabzauber.md` — neuer Abschnitt `## Detail-Regeln: Fokus-Stabzauber` mit vollständigem Regeltext für alle drei.
- **Erkenntnisse:** Kraftfokus gilt immer automatisch, min. 1 AsP/Zauber. Merkmalsfokus: Merkmal bei Erschaffung fest gewählt; erleichtert Probe (nicht ZfP*). Modifikationsfokus: stapelbar; erster Fokus erlaubt bereits Stab als Berührungsersatz.
- **Neu entdeckte Lücken in stabzauber.md** (außerhalb Scope — als neue Einträge vermerkt → L8/L9/L10).

### L8: Stabzauber Zauberspeicher — Detailregeln ✅ *behoben 2026-05-15*

- **Geänderte Datei:** `wiki/dsa-4.1/rituale/stabzauber.md` — neuer Block `### Zauberspeicher — Vollständige Regeln`
- **Inhalt:** Speichervorgang (+2 Erschwernis, AsP beim Einlegen), Auslösung (MU/IN/KL 1 Aktion), Patzer-Kettenauslösung, Berührungspflicht bei (A)-Zaubern, Mehrfach-Speicher mit steigender Erschwernis, Volumensplit.

### L9: Stabzauber Schuppenhaut — Risiko-Mechanik fehlt

- **Wiki-Datei:** `wiki/dsa-4.1/rituale/stabzauber.md`
- **Befund:** Schuppenhaut hat eine W20-Würfelmechanik pro Runde mit Misslingenfolgen bis permanente Gefangenschaft im Stab — spielrelevant, fehlt im 1-Zeiler.
- **Quelle:** WdZ, kapitel-09-rituale.txt Z. 461–489.
- **Priorität:** niedrig (Illaen hat Schuppenhaut nicht).

### L10: Stabzauber Flammenschwert — Misslingens-Tabelle fehlt

- **Wiki-Datei:** `wiki/dsa-4.1/rituale/stabzauber.md`
- **Befund:** Flammenschwert hat eine 1W6-Misslingens-Tabelle (6 Ergebnisse) und Wechsel-Mechanik zwischen schwebendem und gehaltenem Schwert — fehlt in der Tabelle.
- **Quelle:** WdZ, kapitel-09-rituale.txt (Flammenschwert-Block).
- **Priorität:** niedrig (Illaen hat Flammenschwert nicht).

### L7: Vor-/Nachteile & Schlechte Eigenschaften — Detailtiefe für Live-Nachschlagen unzureichend *(niedrige Priorität)*

- **Wiki-Dateien:** `wiki/dsa-4.1/vor-nachteile/schlechte-eigenschaften.md`, `nachteile.md`, `vorteile.md`
- **Befund:** Die Artikel haben tabellarische Übersichten (Name, GP, Auslöser, Haupteffekt), aber die Einträge bleiben zu kurz für schnelles Live-Nachschlagen:
  - **SE-Mechanik (systemisch):** Der Artikel erklärt das allgemeine System (Automatisch / Probe), aber pro SE fehlt: genaue Probe (auf welche Eigenschaft?), Eskalationsstufen, typische Konfliktsituationen.
  - **Beispiele Illaen:** `Neugier 12` — was passiert genau bei Wert 12, wenn sie feuert? `Arroganz 6` — ist die Probe MU/KO/CH? `Prinzipientreue 10` — welche Konsequenz bei Misserfolg konkret?
  - **Vorteile:** Astrale Regeneration 3 z.B. — wie berechnet sich der genaue Bonus, gibt es Einschränkungen (nur Schlaf? Meditation?)?
- **Systemische Ursache:** Das Wiki wurde mit dem Ziel "Key Takeaways + Regelüberblick" extrahiert, nicht "vollständige Regelreferenz für Spieltisch". Für Live-Einsatz fehlt der Schritt von Zusammenfassung → vollständiger Regeltext.
- **Vorschlag (niedrige Priorität):** Pro SE/Vor-/Nachteil die Haupteffekt-Spalte um eine aufklappbare Detail-Zeile oder Fußnoten-Mechanik ergänzen. Alternativ: nur die im Bogen des aktiven Helden enthaltenen Einträge auf volles Regeltext-Niveau heben (taktisch priorisiert).

---

## 2026-05-15 — Audit-Lauf 2 (ausgelöst durch Illaen-Backstory)

### L11: Drachenchronik-Aufhänger nicht dokumentiert

- **Wiki-Datei:** `abenteuer/drachenchronik/_drachenchronik.md`
- **Befund:** Kampagnen-Synopse leer — kein Startort, kein Auftraggeber-NSC, keine Mit-Helden, kein Hook dokumentiert.
- **Vorschlag:** SL-Briefing-Sektion ergänzen (Kampagnenquelle, Startort, NSC-Roster) sobald die offizielle Quelle bekannt ist.
- **Priorität:** mittel (Kampagne läuft aktiv).

### L12: Geographie-Artikel "Riva / Svellttal" fehlt

- **Wiki-Datei:** (noch nicht existent) `wiki/dsa-4.1/geographie/riva.md`
- **Befund:** Riva wird in mind. 4 Wiki-Artikeln referenziert (`stoerrebrandt-kolleg-riva.md`, `nivesen.md`, `mittellaender-kulturen.md`, `illaen-baernhold/vorgeschichte.md`), hat aber keinen eigenen Artikel. Auch das Svellttal als geographischer Kontext fehlt.
- **Vorschlag:** `wiki/dsa-4.1/geographie/riva.md` — Stadt, Stoerrebrandt-Imperium, geopolitischer Kontext, Klimaprofil (Nordmeer).
- **Priorität:** niedrig (kein akuter Spielbedarf, aber häufig verlinkt).

### L13: "Siedlerstadt-Nivese" als Sub-Kultur unbeschrieben

- **Wiki-Datei:** `wiki/dsa-4.1/rassen/nivesen.md` oder `wiki/dsa-4.1/kulturen/mittellaender-kulturen.md`
- **Befund:** `nivesen.md` erwähnt urbanisierte Nivesen in Siedlerstädten des Nordens nur als möglich (Z. 46), erklärt aber nicht, wie ein Nivese in einer Mittelländischen Stadt sozialisiert wird: Akkulturation, Spannung Nomaden-Erbe vs. Stadt-Alltag, typische Familienpraktiken (Speisegebote, mündliche Überlieferung), gesellschaftliche Stellung.
- **Vorschlag:** Kurzer Abschnitt `### Siedler-Nivesen in Mittelländischen Städten` in `nivesen.md` (oder Cross-Note in `mittellaender-kulturen.md`).
- **Priorität:** niedrig, aber relevant sobald weitere Nivesen-Charaktere erstellt werden.

---

---

## 2026-05-15 — Audit-Lauf 3 (Held-Daten Konsistenz)

### L14: Astrale Regeneration I/II im SF-Bogen falsch kategorisiert

- **Wiki-Datei:** `helden/illaen-baernhold/sonderfertigkeiten.md`
- **Befund:** Illaens SF-Tabelle unter "Magische Sonderfertigkeiten" enthält `Astrale Regeneration I` und `Astrale Regeneration II`. Laut `allgemeine-sonderfertigkeiten.md` sind das **Vorteile**, nicht SF. In `wiki/dsa-4.1/vor-nachteile/` fehlt ein entsprechender Eintrag für Astrale Regeneration als Vorteil.
- **Vorschlag:** Astrale Regeneration I/II aus dem SF-Bogen in `vor-nachteile.md` verschieben. Wiki-Artikel für Astrale Regeneration als Vorteil anlegen (Quelle: WdH).
- **Priorität:** mittel (korrekte Kategorisierung für Steigerungskosten-Berechnung relevant).

---

---

## 2026-05-31 — Sprint 007 (D-009 Stufen-Aufstieg)

### L15: Fehlender Wiki-Artikel zu Stufe / Stufenaufstieg

- **Wiki-Datei:** fehlt (vorgeschlagen: `wiki/dsa-4.1/grundregeln/stufenaufstieg.md`)
- **Befund:** Kein Artikel definiert was Stufe bedeutet, wie Stufenaufstieg funktioniert, welche AP-Schwellen gelten, und was ein Charakter pro Stufe erhält. `erfahrung.md` und `steigerung.md` decken AP-Ausgaben ab, aber nicht das Stufen-Konzept.
- **Datenkonflikt:** `held.py::AP_STUFEN` sagt Stufe 4 = 1500 AP kumulativ. Die handgeschriebene Notiz in `helden/illaen-baernhold/steigerungs-log.md` Z. 31 nennt „Stufe 4 = 4.200 AP" — das entspricht laut Code Stufe 6. Welche Quelle korrekt ist, muss per Regelwerk geklärt und dann im Code / Log korrigiert werden.
- **Weiterer Befund (aus Code):** `held.py:57-64` dokumentiert, dass Stufenaufstieg in DSA 4.1 GM-Freigabe erfordert, nicht automatisch bei AP-Schwelle passiert — diese Regel fehlt im Wiki.
- **Vorschlag:** Neuen Artikel anlegen mit: AP-Schwellen-Tabelle (aus Regelwerk verifiziert), Mechanik (GM-Grant), was eine Stufe bringt (falls im Regelwerk beschrieben). Datenkonflikt im steigerungs-log bereinigen.
- **Priorität:** mittel (Dashboard-Stufen-Feature funktioniert ohne Wiki-Artikel; Korrektheit der AP-Schwellen relevant für Spielerberatung).

### L4: Rassen-Artikel ohne Volkstracht — *geschlossen (kein WdH-Quellmaterial)*

- **Befund:** Das WdH-Rassen-Kapitel enthält **keine „Tracht und Bewaffnung"-Abschnitte** für die Rassen (nur Startwerte). Diese Information liegt im Kulturen-Kapitel (→ L3), nicht im Rassen-Kapitel.
- **Nivesen spezifisch:** Kein separater Tracht-Block im WdH für die Rasse Nivesen. Illaen ist durch die Stoerrebrandt-Ausrüstung vollständig versorgt; kulturspezifische Kleidung unter L3 (Mittelländische Städte) abgedeckt.
- **Ergebnis:** Lücke geschlossen — keine Quelle vorhanden, kein Handlungsbedarf.

---

## 2026-09-16 — Sprint 013 (D-025…D-029, ausgelöst durch vier Spielsessions)

### L16: Stabzauber-Aktivierung — Artikel widersprach sich selbst ✅ *behoben 2026-09-16*

- **Wiki-Datei:** `wiki/dsa-4.1/rituale/stabzauber.md`, Sektion `### Aktivierung der Stabzauber`
- **Befund:** Die Sektion behauptete pauschal „Aktivierung = freie Aktion (kein Zauberwurf)", nannte aber im selben Absatz „Probe auf Aktivierung für Wirkung (sofern angegeben)" — Selbstwiderspruch. `rituale-grundregeln.md` sagt zusätzlich generisch „Aktivierung: Separat geprobt", was der Kernaussage ebenfalls widerspricht. Ursache: die ursprüngliche Extraktion hatte die Stabzauber-Aktivierung fälschlich pauschalisiert, obwohl sie im Quellbuch pro Ritual individuell geregelt ist.
- **Quellenprüfung:** `raw/pdf-extracted/wege-der-zauberei/kapitel-09-rituale.txt` (WdZ S. 106–110) gegengelesen. Ergebnis: die generische Objektritual-Regel („Aktivierungsprobe auf Ritualkenntnis, volle Aktion, sofern nicht anders angegeben") ist korrekt — `rituale-grundregeln.md` stimmte bereits. Die Stabzauber selbst weichen aber unterschiedlich stark davon ab: Bindung/Ewige Flamme/Hammer des Magus/Seil des Adepten brauchen keine Probe, kosten aber je 1 AsP; die drei Foki (Kraft/Merkmal/Modifikation) sind passiv ohne jede Aktivierung; Flammenschwert (MU/IN/GE) und Schuppenhaut (MU/IN/KO) haben eigene Aktivierungsproben; der Zauberspeicher hat die bereits korrekt dokumentierte Probe MU/IN/KL.
- **Behoben:** `stabzauber.md` — Sektion durch korrekte Vergleichstabelle ersetzt (Probe/Kosten/Wirkungsdauer pro Stabzauber), Quelle zitiert. `rituale-grundregeln.md` — Formulierung „sofern beim Ritual nicht anders angegeben" ergänzt, um den Bezug zu den Stabzauber-Ausnahmen klarzustellen.
- **Nicht behoben (User-Domäne, außerhalb Wiki-Scope):** `helden/illaen-baernhold/rituale.md` nennt zwei Stabzauber abweichend vom Wiki — „Stabzauber: Fackel" (Wiki: „Ewige Flamme") und „Stabzauber: Stabverlängerung" (deckt sich funktional mit „Doppeltes Maß"). Datei ist bereits mit eigenem Hinweis dazu versehen (Z. 30); keine Umbenennung ohne explizite User-Freigabe.

---

## 2026-09-19 — /session-compile 04.06.2026 (ausgelöst durch Spielabend 04.06.2026)

### L17: Ort-/Regionsartikel für Punin, Yaquir-Gegend und Briglo fehlen

- **Wiki-Datei:** fehlt (vorgeschlagen: neuer Ordner oder Artikel für Aventurien-Orte/Regionen; Pfad noch offen)
- **Befund:** Session 01 (Fundstelle: „Sightseeing in Punin“, „Wissensaufbau im Hesindetempel“, „Punin Akademie am 15. Phex“) spielt komplett in Punin und nennt den Yaquir mit seinen Dörfern und Städten sowie Briglo (Austragungsort der 2. Dämonenkriege). Das Wiki hat dazu keinen Ort-/Regionsartikel (Glob und Grep über `wiki/dsa-4.1`); Punin und der Yaquir kommen nur als Nebenbemerkung in Fließtexten anderer Artikel vor (z. B. `goetter/hesinde.md`, `geographie/fortbewegung.md`).
- **Vorschlag:** Regionalbeschreibung Punin und Yaquir-Region anlegen (Stadt, Akademie, Hesindetempel, Flusslauf bis Briglo). Quellbuch nicht geprüft.

---

### L18: Wüstenwissen (Khôm) — Fauna und Oasen nur als Stichwort

- **Wiki-Datei:** `wiki/dsa-4.1/geographie/terraintypen.md`, Abschnitt „Wüste (S. 36–38)“
- **Befund:** Session 01 (Fundstelle: „Infos generell zu Wüste“) nennt Khormasbestien, Skorpione (Faustformel „je kleiner desto gefährlicher“; Stiefel am Morgen ausleeren) sowie Oasen und deren Distanzen. `terraintypen.md` erwähnt Skorpione und Oasen nur als Stichwort in der Liste der Bewohner (Z. 227); „Khormasbestie“ hat im gesamten `wiki/dsa-4.1` keinen Treffer.
- **Vorschlag:** Wüsten-Fauna (Khormasbestie, Skorpione mit Gefahrenregel) und Oasen-Distanzen als eigenen Abschnitt bzw. Artikel ergänzen. Quellbuch nicht geprüft.

---

## 2026-09-19 — /session-compile 27.06.2026 (ausgelöst durch Spielabend 27.06.2026)

### L19: Reichshof und Reichsämter 1025 BF (Kumrath, Königin Rohaya, Reichskanzler, Reichs(erz)marschall)

- **Wiki-Datei:** fehlt (vorgeschlagen: Hintergrundartikel zu Reichshof/Reichsämtern, Pfad noch offen)
- **Befund:** Session 02 (Fundstelle: „19. Phex“) — Empfang in Kumrath durch Reichskanzler (Name=Rafik), Königin (Rohaya) und Reichs(erz)marschall im Heraldiksaal, Anreden „Eure königliche Hoheit“ / „Eure allerdurchlauchteste Hoheit“ bzw. „Eure Excellenz“. Zusätzlich Omlad („zurückeroberte Stadt“) und Bactrinn als Stationen der Flussfahrt. Dazu gibt es im Wiki keinen Treffer (Grep auf Kumrath, Cumrat, Rohaya, Reichskanzler, Reichsmarschall, Omlad, Bactrinn); `grundregeln/sozialstatus.md` und `goetter/religion-alltag.md` enthalten keine Anredeformen für diese Ämter.
- **Vorschlag:** Hintergrundartikel zu Reichshof und Ämtern (Personen, Sitz, Anredeformen) sowie Kurzbeschreibung der Flussstationen Omlad und Bactrinn. Quellbuch nicht geprüft.

---

## 2026-09-19 — /session-compile 18.07.2026 (ausgelöst durch Spielabend 18.07.2026)

### L20: Brig-Lo — Schlachtfeld, Tempel der Vier und Grabanlage der Leonore von Berg

- **Wiki-Datei:** fehlt (vorgeschlagen: Ortsartikel Brig-Lo; Pfad noch offen)
- **Befund:** Session 03 (Fundstelle: „22. Phex — Brig-Lo“) beschreibt Brig-Lo ausführlich: Schlachtfeld mit Geistern und grauen, toten Feldern, Tempel der 4 (Praios, Rondra, Efferd, Ingerimm; später von einer Praios-Geweihten geschleift), Mausoleum der Leonore von Berg, Garnison in der Baronie Südpforte am Fluss Brigella. Im Wiki kommt Brig-Lo nur als Nebenbemerkung vor: `goetter/kor.md` Z. 71 (Heiliger Ort) und `goetter/bund-wahren-glaubens.md` Z. 87 (Diamant von Brig-Lo). Die „2. Dämonenkriege“ (Session 01) haben ebenfalls keinen eigenen Artikel.
- **Vorschlag:** Ortsartikel Brig-Lo (Schlacht, Tempel der Vier, Baronie/Garnison) samt Einordnung der 2. Dämonenkriege. Quellbuch nicht geprüft.

---

## 2026-09-19 — /session-compile 22.08.2026 (ausgelöst durch Spielabend 22.08.2026)

### L21: Novadis als Volk sowie Amhallah

- **Wiki-Datei:** `wiki/dsa-4.1/kulturen/tulamidisch-kulturen.md` (bzw. neuer Ortsartikel Amhallah)
- **Befund:** Session 04 (Fundstellen: „Novadi Lager“, „Zurück nach Brig-Lo“) — Novadi-Lager mit ca. 20 Personen, Herkunft Amhallah, Mittelsmann ist der Besitzer des Teehauses der Koramsbestie; nächstes Reiseziel der Gruppe ist Amhallah. Das Wiki kennt Novadis nur als Kultur-Charakteroption (Novadi Männer/Frauen in `tulamidisch-kulturen.md`) und über den Rastullah-Glauben, aber nicht als Volk mit Stämmen und Siedlungsweise. Zu Amhallah gibt es nur die Profession „al-Halan / Farisim von Amhallah“ in `professionen/schwertgeselle.md`, keinen Ortsartikel.
- **Vorschlag:** Ortsartikel Amhallah anlegen und die Novadis als Volk (Stämme, Lager, Gebräuche) ergänzen. Quellbuch nicht geprüft.

---

---

## 2026-09-19 — Dashboard Sprint 018 (ausgelöst durch D-018 Artikelvorschau im Zauber-Tab)

### L22: Zauberartikel — Frontmatter-YAML bei 103 von 268 Artikeln ungültig

- **Wiki-Dateien:** `wiki/dsa-4.1/zauber/*.md` (Beispiel `abvenenum.md`, Zeile 9: `kosten: 4 AsP pro Mahlzeit für bis zu 10 Personen (Ach: 3 AsP)`)
- **Befund:** Werte in `kosten:`, `zauberdauer:` (u. a. `probe:`) enthalten ein unquotiertes `: ` (Repräsentations-Zusätze wie `(Ach: 3 AsP)`, `(Sch: 5 AsP)`). `yaml.safe_load` bricht mit „mapping values are not allowed here" ab — 103 der 268 Zauberartikel sind betroffen (Stichprobe per `parsers.held.parse_frontmatter` am 19.09.2026: 165 ok / 103 fehlerhaft). Folgen: Obsidian-Properties/Dataview lesen diese Artikel nicht, maschinelles Auslesen scheitert; das Dashboard umgeht es seit Sprint 018 mit einem zeilenweisen Fallback-Parser (`parsers/wikiartikel.py`).
- **Vorschlag:** Betroffene Werte in Anführungszeichen setzen (`kosten: "4 AsP … (Ach: 3 AsP)"`) — per Skript prüfbar (`yaml.safe_load` über alle Artikel; Ziel 0 Fehler) und mit Diff-Stichprobe umsetzen. Danach den Fallback-Parser im Dashboard entfernen. Ggf. Extraktions-Konvention in `raw/pdf-extracted/EXTRACTION-PLAN.md` ergänzen („Frontmatter-Werte mit `:` immer quoten").

---

## 2026-09-19 — Dashboard Sprint 019 (ausgelöst durch D-041 Wund-/Zustände-Audit)

### L23: Zustände Schmerz/Furcht/Betäubung/Verwirrung/Erschöpfung — nicht als Probenmalus belegt

- **Wiki-Datei:** `wiki/dsa-4.1/grundregeln/zustaende.md` (neu)
- **Befund:** Die fünf Zustands-Chips des Dashboards (Schmerz −2, Furcht −2, Betäubt −4, Verwirrt −2, Erschöpft −2) sind in den extrahierten Büchern WdS/WdH/WdE **nicht als Probenmalus gefunden** worden. Belegt sind nur: Wunden als Basiswert-Abzug (WdS S. 57), Schmerz-Probe nach Wunde (optional, WdS S. 82), Ängste als Schlechte Eigenschaften (WdH S. 268), Betäubungsschlag mit Bewusstlosigkeit (WdS S. 61, 86), Erschöpfung/Überanstrengung als Ressource (WdS S. 139) sowie optionale Probenmali durch niedrige LE (WdS S. 57) und AU (WdS S. 83). „Verwirrt" hat keine Regelgrundlage außer Spezialfällen (Überraschung WdS S. 78, Patzer-Desorientierung WdS S. 85). Die Chip-Werte sind demnach Hausregeln.
- **Vorvorhandener Fehler (behoben):** `grundregeln/eigenschaften.md` schrieb „SP ≥ WS = Wunde"; WdS S. 57 sagt „mehr Schadenspunkte als die Wundschwelle" (SP > WS). Zwei Zeilen korrigiert. `grundregeln/proben.md` Z. 64 enthielt dieselbe Formulierung „SP ≥ Wundschwelle" und wurde ebenfalls korrigiert (Review Task 1).
- **Vorschlag:** Bei Bedarf weitere Bände auf eine allgemeine Zustandsregel prüfen (z. B. Wege der Zauberei, Zoo-Botanica Aventurica). Suchmuster in WdS/WdH/WdE: Schmerz, Furcht/Ängst/Panik/Schreck, Betäub/bewusstlos, Verwirr, Erschöpf/Überanstreng, Zustände (ohne Professionen-Kapitel und Indizes).
