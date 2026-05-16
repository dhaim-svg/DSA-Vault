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

### L4: Rassen-Artikel ohne Volkstracht — *geschlossen (kein WdH-Quellmaterial)*

- **Befund:** Das WdH-Rassen-Kapitel enthält **keine „Tracht und Bewaffnung"-Abschnitte** für die Rassen (nur Startwerte). Diese Information liegt im Kulturen-Kapitel (→ L3), nicht im Rassen-Kapitel.
- **Nivesen spezifisch:** Kein separater Tracht-Block im WdH für die Rasse Nivesen. Illaen ist durch die Stoerrebrandt-Ausrüstung vollständig versorgt; kulturspezifische Kleidung unter L3 (Mittelländische Städte) abgedeckt.
- **Ergebnis:** Lücke geschlossen — keine Quelle vorhanden, kein Handlungsbedarf.
