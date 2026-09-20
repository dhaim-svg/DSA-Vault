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

- **Geänderte Datei:** `wiki/dsa-4.1/rituale/stabzauber.md` — neuer Abschnitt `## Detail-Regeln: Fokus-Stabzauber` mit vollständigem Regeltext für alle drei. *(Sprint 022 T4: Sammelabschnitt aufgelöst — die Foki stehen jetzt als eigene `## Kraftfokus` / `## Merkmalsfokus` / `## Modifikationsfokus`, siehe L25.)*
- **Erkenntnisse:** Kraftfokus gilt immer automatisch, min. 1 AsP/Zauber. Merkmalsfokus: Merkmal bei Erschaffung fest gewählt; erleichtert die Zauberprobe „um einen Punkt“ (Buchwortlaut; die frühere Auslegung „nicht ZfP\*“ ist im Artikel entfernt, Sprint 023). Modifikationsfokus: stapelbar; erster Fokus erlaubt bereits Stab als Berührungsersatz.
- **Neu entdeckte Lücken in stabzauber.md** (außerhalb Scope — als neue Einträge vermerkt → L8/L9/L10).

### L8: Stabzauber Zauberspeicher — Detailregeln ✅ *behoben 2026-05-15*

- **Geänderte Datei:** `wiki/dsa-4.1/rituale/stabzauber.md` — neuer Block `### Zauberspeicher — Vollständige Regeln` *(Sprint 022 T4: jetzt eigener Abschnitt `## Zauberspeicher`, siehe L25.)*
- **Inhalt:** Speichervorgang (+2 Erschwernis, AsP beim Einlegen), Auslösung (MU/IN/KL 1 Aktion), Patzer-Kettenauslösung, Berührungspflicht bei (A)-Zaubern, Mehrfach-Speicher mit steigender Erschwernis, Volumensplit.

### L9: Stabzauber Schuppenhaut — Risiko-Mechanik fehlt ✅ *behoben 2026-09-20 (Sprint 023 T2)*

- **Wiki-Datei:** `wiki/dsa-4.1/rituale/stabzauber.md`
- **Befund:** Schuppenhaut hat eine W20-Würfelmechanik pro Runde mit Misslingenfolgen bis permanente Gefangenschaft im Stab — spielrelevant, fehlt im 1-Zeiler.
- **Quelle:** WdZ, kapitel-09-rituale.txt Z. 461–489.
- **Priorität:** niedrig (Illaen hat Schuppenhaut nicht).
- **Behoben in Sprint 023 (T2):** `## Schuppenhaut` trägt jetzt die Buchregeln (WdZ S. 110–111): Chamäleon/Speikobra mit LeP 15 und RS RkP\*/2, Form bei Erschaffung fest, Ritual zweimal sprechbar (je 5 Vol), kein Zaubern in Tiergestalt, Körper wie unter PARALYSIS.
- **Risiko-Mechanik (Behoben in Sprint 023):** W20 während der Verwandlung, bei 20 Ritualkenntnisprobe auf (MU/IN/KO) + 7, Misslingen = in der Reptiliengestalt gefangen (nur VERWANDLUNG BEENDEN befreit; Schuppenhaut danach 20 – RkW Monate unbenutzbar), Tod des Tieres = 4W6 SP und Stab für immer verloren. Der Buchtext lässt offen, ob je Spielrunde oder je RkP\* Runden gewürfelt wird; das Wiki gibt den Wortlaut wieder. Die Formulierung „permanente Gefangenschaft im Stab“ trifft das Buch nicht: der Magier ist im Tier gefangen und befreibar.

### L10: Stabzauber Flammenschwert — Misslingens-Tabelle fehlt ✅ *behoben 2026-09-20 (Sprint 023 T2)*

- **Wiki-Datei:** `wiki/dsa-4.1/rituale/stabzauber.md`
- **Befund:** Flammenschwert hat eine 1W6-Misslingens-Tabelle (6 Ergebnisse) und Wechsel-Mechanik zwischen schwebendem und gehaltenem Schwert — fehlt in der Tabelle.
- **Quelle:** WdZ, kapitel-09-rituale.txt (Flammenschwert-Block).
- **Priorität:** niedrig (Illaen hat Flammenschwert nicht).
- **Behoben in Sprint 023 (T2):** `## Flammenschwert` enthält die 1W6-Misslingens-Tabelle (Buch: vier Ergebniszeilen 1–3 / 4 / 5 / 6, zusammen die sechs W6-Werte; WdZ S. 110) und den Wechsel zwischen gehaltenem und schwebendem Schwert (neue Aktivierungsprobe + Aktion, keine erneuten Umwandlungskosten).
- **Ergänzend (Behoben in Sprint 023):** Basisschaden 1W6+4, RkP\*-Steigerung (TP, AT, Parade-Erschwernis, GS mit Grenzen), gehalten vs. dirigiert (AT 12, GS 3, DK HN, Davonlaufen, Einschränkungen des Magiers, Simultanzaubern), Anfälligkeit FEUERBANN / BEWEGUNG STÖREN, Varianten.

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

### L22: Zauberartikel — Frontmatter-YAML bei 103 von 268 Artikeln ungültig ✅ *behoben 2026-09-19*

- **Wiki-Dateien:** `wiki/dsa-4.1/zauber/*.md` (Beispiel `abvenenum.md`, Zeile 9: `kosten: 4 AsP pro Mahlzeit für bis zu 10 Personen (Ach: 3 AsP)`)
- **Befund:** Werte in `kosten:`, `zauberdauer:` (u. a. `probe:`) enthalten ein unquotiertes `: ` (Repräsentations-Zusätze wie `(Ach: 3 AsP)`, `(Sch: 5 AsP)`). `yaml.safe_load` bricht mit „mapping values are not allowed here" ab — 103 der 268 Zauberartikel sind betroffen (Stichprobe per `parsers.held.parse_frontmatter` am 19.09.2026: 165 ok / 103 fehlerhaft). Folgen: Obsidian-Properties/Dataview lesen diese Artikel nicht, maschinelles Auslesen scheitert; das Dashboard umgeht es seit Sprint 018 mit einem zeilenweisen Fallback-Parser (`parsers/wikiartikel.py`).
- **Vorschlag:** Betroffene Werte in Anführungszeichen setzen (`kosten: "4 AsP … (Ach: 3 AsP)"`) — per Skript prüfbar (`yaml.safe_load` über alle Artikel; Ziel 0 Fehler) und mit Diff-Stichprobe umsetzen. Danach den Fallback-Parser im Dashboard entfernen. Ggf. Extraktions-Konvention in `raw/pdf-extracted/EXTRACTION-PLAN.md` ergänzen („Frontmatter-Werte mit `:` immer quoten").
- **Behoben:** 103 Zauberartikel + `wiki/dsa-4.1/goetter/bund-wahren-glaubens.md` (1 Zeile `kirchenstruktur`) — 114 Zeilen in Anführungszeichen gesetzt, Werte unverändert (Round-Trip gegen den Fallback-Parser: 0 Abweichungen bei den quotierten Zeilen; einzige Differenz sind die unveränderten Flow-Listen `aspekte`/`farben` in `bund-wahren-glaubens.md`, die YAML als Liste statt als String liest). Verifizierer `raw/pdf-extracted/_tools/check-frontmatter.py` (682 Artikel, 0 Fehler); Konvention in `raw/pdf-extracted/EXTRACTION-PLAN.md` ergänzt; Fallback-Parser im Dashboard folgt in Sprint 021 Task 2.

---

## 2026-09-19 — Dashboard Sprint 019 (ausgelöst durch D-041 Wund-/Zustände-Audit)

### L23: Zustände Schmerz/Furcht/Betäubung/Verwirrung/Erschöpfung — nicht als Probenmalus belegt

- **Wiki-Datei:** `wiki/dsa-4.1/grundregeln/zustaende.md` (neu)
- **Befund:** Die fünf Zustands-Chips des Dashboards (Schmerz −2, Furcht −2, Betäubt −4, Verwirrt −2, Erschöpft −2) sind in den extrahierten Büchern WdS/WdH/WdE **nicht als Probenmalus gefunden** worden. Belegt sind nur: Wunden als Basiswert-Abzug (WdS S. 57), Schmerz-Probe nach Wunde (optional, WdS S. 82), Ängste als Schlechte Eigenschaften (WdH S. 268), Betäubungsschlag mit Bewusstlosigkeit (WdS S. 61, 86), Erschöpfung/Überanstrengung als Ressource (WdS S. 139) sowie optionale Probenmali durch niedrige LE (WdS S. 57) und AU (WdS S. 83). „Verwirrt" hat keine Regelgrundlage außer Spezialfällen (Überraschung WdS S. 78, Patzer-Desorientierung WdS S. 85). Die Chip-Werte sind demnach Hausregeln.
- **Vorvorhandener Fehler (behoben):** `grundregeln/eigenschaften.md` schrieb „SP ≥ WS = Wunde"; WdS S. 57 sagt „mehr Schadenspunkte als die Wundschwelle" (SP > WS). Zwei Zeilen korrigiert. `grundregeln/proben.md` Z. 64 enthielt dieselbe Formulierung „SP ≥ Wundschwelle" und wurde ebenfalls korrigiert (Review Task 1).
- **Vorschlag:** Bei Bedarf weitere Bände auf eine allgemeine Zustandsregel prüfen (z. B. Wege der Zauberei, Zoo-Botanica Aventurica). Suchmuster in WdS/WdH/WdE: Schmerz, Furcht/Ängst/Panik/Schreck, Betäub/bewusstlos, Verwirr, Erschöpf/Überanstreng, Zustände (ohne Professionen-Kapitel und Indizes).

---

## 2026-09-20 — Dashboard Sprint 022 (ausgelöst durch B-018 Vorbereitung der Ritual-Artikelvorschau)

### L24: Stabzauber — Zählung „13 Rituale“ nicht belegt; Tabellenwerte weichen teils vom Buch ab ✅ *behoben 2026-09-20 (Sprint 023 T1)*

- **Wiki-Datei:** `wiki/dsa-4.1/rituale/stabzauber.md`
- **Befund:** Überschrift und Einleitungstext sagen „13 Rituale“ / „alle 13 Stabzauber“, die Tabelle führt aber nur **11 distinkte Namen** plus eine Doppelzeile „Bindung des Stabes (Vol-Angaben)“ (12 Tabellenzeilen). Abgleich mit `raw/pdf-extracted/wege-der-zauberei/kapitel-09-rituale.txt` (lokal, gitignored; Seitenzählung nach den Fußzeilen der Textdatei): WdZ S. 108 gliedert die Stabzauber in vier Gruppen — Meta (Bindung des Stabes, **Apport**), profan (Ewige Flamme, Seil des Adepten, Doppeltes Maß, Hammer des Magus), arkan (Kraftfokus, Modifikationsfokus, Zauberspeicher, Merkmalsfokus), esoterisch (Flammenschwert, Schuppenhaut) — das sind **12 Rituale inkl. Apport**, ausgeführte Regelblöcke gibt es für 11 (S. 109–111; der Apport steht als allgemeines Objektritual auf S. 106 und gilt als „immer das letzte Stabritual“). Eine 13. Angabe ist im Buch nicht zu finden; die Tabelle nennt den **Apport nicht**.
  - **Namen:** „Fackel“ und „Stabverlängerung“ sind **keine Buchnamen** — im Buch beschreibt „Fackel“ die Wirkung der *Ewigen Flamme* (Feuer „wie eine gewöhnliche Fackel“) und S. 108 nennt den Stab „verlängert oder zu einem Seil oder einer Fackel verwandelt“; „Stabverlängerung“ passt zum *Doppelten Maß* (Stab wächst auf die doppelte Länge, Variante *Halbes Maß*), ist aber ein Heldendokument-Kürzel, kein Buchtitel.
  - **Tabellenwerte gegen das Buch (Stichprobe der Übersichtstabelle):** *Doppeltes Maß* — Buch: Stab wächst auf doppelte Länge (ca. 3 Schritt), Volumen 1 Punkt; die Tabelle nennt stattdessen „+3 auf FF, +2 auf KL“ und Vol „—“ (Effekt nicht im Buch gefunden). *Schuppenhaut* — Buch: Erschaffungsprobe MU / IN / CH (+7); die Tabelle nennt „MU / IN / KO (+varies)“ (MU / IN / KO ist im Buch die Aktivierungsprobe). *Bindung des Stabes* — Buch: Volumen 0 Punkte (22 AsP, davon 1 permanent); die Tabelle nennt „1 pAsP“ in der Vol-Spalte. Die Doppelzeile „Vol-Angaben 24/18/15/27“ entspricht dem Stab-Fassungsvermögen (24 gewöhnlich / 18 kurz / 15 sehr kurz / 27 mit Kristallkugel, WdZ S. 108), nicht einem Vol je Holzart. Übrige Zeilen (Erschaffungsproben, AsP, Vol) stimmen mit dem Buch überein.
- **Behoben in Sprint 023 (T1):** `stabzauber.md` gegen WdZ S. 106–111 neu aufgesetzt (Transkript der dreispaltigen Rohseiten: Spalten einzeln rekonstruiert).
  - Zählung **12** in vier Gruppen (Gruppen-Spalte in der Übersichtstabelle), **Apport** als 12. Zeile und eigener `## Apport`-Abschnitt; „13“ überall entfernt (auch `rituale/_rituale.md`).
  - Werte korrigiert: *Doppeltes Maß* (Vol 1, Effekt doppelte Länge, Variante Halbes Maß, Aktivierung 1 AsP ohne Probe), *Schuppenhaut* (Erschaffung MU / IN / CH (+7)), *Bindung des Stabes* (Vol 0; 22 AsP, davon 1 permanent; keine Aktivierung), außerdem *Hammer des Magus* (Aktivierung MU / CH / KK, 3 AsP, augenblicklich; Effekt Strukturschaden statt „erhöhte TP“), *Seil des Adepten* (Effekt) und die Aktivierungsprobe des *Zauberspeichers* (Komplexität des Zaubers).
  - „Vol je Holzart“ ersetzt durch Abschnitt „Fassungsvermögen & Eigenvolumen“ (24 / 18 / 15 / 27 je Stabform); die Holzarten-Tabelle entfernt (WdZ nennt keine, nur den Verweis SRD 117f.); die unbelegte Regel „Erschaffungsproben um die Zahl vorhandener Stabzauber erschwert“ entfernt; Fettwert-Zeilen als Listen, Sternchen-Markup im Merkmalsfokus korrigiert.
- **Vorschlag (Rest):** Detailregeln der sieben knappen Abschnitte nachziehen (siehe L25a, Flammenschwert-Misslingens-Tabelle → L10, Schuppenhaut-Risiko → L9). *Erledigt in Sprint 023 T2.*

### L25: Ritual-Artikelvorschau — Voraussetzungen im Wiki und im Heldendokument

- **Wiki-Dateien:** `wiki/dsa-4.1/rituale/stabzauber.md` (+ User-Domäne `helden/illaen-baernhold/rituale.md`, nur lesend betrachtet)
- **Befund / Stand:**
  - (a) **Wiki-Seite erledigt (Sprint 022 T4, Sprint 023 T1/T2):** `stabzauber.md` hat je Stabzauber einen `##`-Abschnitt (**12 Anker** inkl. Apport: Bindung des Stabes, Doppeltes Maß, Ewige Flamme, Flammenschwert, Hammer des Magus, Kraftfokus, Merkmalsfokus, Modifikationsfokus, Schuppenhaut, Seil des Adepten, Zauberspeicher, Apport), damit ein Anker-Link `[[…/stabzauber#<Name>]]` genau einen Abschnitt lädt. Die **sieben** zunächst knappen Abschnitte (alle außer den vier Foki/Zauberspeicher und dem Apport) tragen seit **Sprint 023 T2** die Buchregeln (WdZ S. 109–111; Flammenschwert-Misslingens-Tabelle → L10, Schuppenhaut-Risiko → L9, beide behoben); Foki, Zauberspeicher und Apport waren bereits ausgeführt.
  - (b) **Offen, User-Domäne:** `helden/illaen-baernhold/rituale.md` verlinkt `[[…/stabzauber]]` ohne Anker. Für die Vorschau bräuchte jede Stabzauber-Zeile einen Anker-Link der Form `[[wiki/dsa-4.1/rituale/stabzauber#<Name>\|<Anzeige>]]`. Kein Eingriff durch die Bibliothekarin — Änderung liegt beim User.
  - (c) **Namensabgleich Held ↔ Wiki:** Held „Fackel“ = Wiki „Ewige Flamme“; „Stabverlängerung“ = „Doppeltes Maß“ (siehe unten); „Bindung“ = „Bindung des Stabes“; „Seil (des Adepten)“ = „Seil des Adepten“. Die Anker müssen den Wiki-Namen exakt tragen, Anzeigetext darf der Heldenname bleiben. **Prüfung Sprint 023 T1:** „Stabverlängerung“ ist **kein Buchname**; die Zuordnung zum „Doppelten Maß“ ist eine semantische und gilt als **bestätigt** — WdZ S. 108 nennt die Stabformen „verlängert oder zu einem Seil oder einer Fackel verwandelt“, und als einziger der 12 Stabzauber lässt das Doppelte Maß den Stab wachsen (S. 109: „auf das Doppelte seiner Länge … anwachsen“).
- **Vorschlag:** (b) und (c) beim nächsten Rituale-Pflegedurchgang des Users; die Detailregeln der sieben knappen Abschnitte sind seit Sprint 023 T2 nachgezogen.
