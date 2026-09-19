# /session-compile

Überführt einen Spielabend aus der Roh-Mitschrift `abenteuer/drachenchronik/chronik.md` in eine
strukturierte Session-Datei (`YYYY-MM-DD-session-NN.md`) nach der Konvention aus
`abenteuer/_abenteuer.md` (Abschnitt „Session-Datei-Format"). Die Roh-Chronik bleibt unangetastet.

**Argument:** `$ARGUMENTS`
- leer → den **ältesten unkompilierten** Abend bearbeiten
- `<DD.MM.YYYY>` (z. B. `27.06.2026`) → genau diesen Abend
- `alle` → alle unkompilierten Abende chronologisch nacheinander, ohne Zwischenrückfragen

Das Kommando ist für den autonomen Ablauf geschrieben: **keine Rückfragen** an den User, außer wo
ausdrücklich „stoppen" steht. Unsicheres wird markiert und im Report gemeldet, nicht erraten.

---

## Grenzen (gelten für jeden Schritt)

- `abenteuer/drachenchronik/chronik.md` **nie ändern** (auch nicht Formatierung/Tippfehler).
- `helden/` **nie ändern**.
- In `abenteuer/` **nur** schreiben: (1) die neuen Session-Dateien, (2) die zwei beschriebenen Stellen
  in `abenteuer/drachenchronik/_drachenchronik.md` (Schritt 4).
- **Nichts löschen** — auch nicht den Platzhalter `2025-10-04-session-01.md` (er zählt zu keinem
  Abend; das Aufräumen ist ein einmaliger Schritt außerhalb dieses Kommandos und braucht User-Freigabe).
- **Keine Git-Commits.** Commit erst nach Sichtung durch den User (`abenteuer/` ist User-Domäne).
- Außerhalb der Session-Dateien und `_drachenchronik.md` nur `wiki-luecken.md` (Schritt 5) ergänzen.

---

## Schritt 1: Import (Drive → Vault)

Aus dem Vault-Root:

```bash
python helden/_tools/chronik_import.py
```

Was das Skript tut (Quelltext gelesen): kopiert **einseitig** `C:\Users\David\Google Drive\DSA\Helden\Drachenchronik.md`
nach `abenteuer/drachenchronik/chronik.md` (überschreibt komplett, kein Merge) und neue/geänderte
Bilder aus `…\drachenchronik-daten\` nach `abenteuer/drachenchronik/drachenchronik-daten/`. Es schreibt
nie nach Drive. Ausgabe bei Erfolg (Exit 0): `chronik.md aktualisiert: <vorher> -> <nachher> Zeilen (±Δ)`
plus Liste kopierter Bilder oder `keine neuen/geänderten Bilder`.

**Quelle nicht erreichbar** (Exit 1, stderr `Fehler: Chronik-Import fehlgeschlagen — Quelldatei nicht
gefunden: …`): **nicht abbrechen, nicht raten.** Klar melden („Drive-Quelle nicht erreichbar, arbeite mit der
vorhandenen `chronik.md`") und mit Schritt 2 weitermachen — **außer** der User hat ausdrücklich „mit frischem
Import" verlangt: dann stoppen und den Fehler melden. Der Fehler-Hinweis kommt später auch in den Report (Schritt 6).

---

## Schritt 2: Unkompilierte Abende bestimmen

Ein Abend ist ein H2 der Form `## DD.MM.YYYY` in `chronik.md`. Er gilt als **kompiliert**, wenn im Ordner
`abenteuer/drachenchronik/` eine Datei `*-session-*.md` existiert, deren Frontmatter `datum:` dem ISO-Datum
des Abends entspricht (`DD.MM.YYYY` → `YYYY-MM-DD`). Es gibt keinen separaten Status-Tracker. Andere H2
(`## Nützliche SF`, `## Vorbereitung`, `## Für später`, `## Bugs in der Charackter Ansicht` …) sind **keine**
Abende und werden ignoriert.

```bash
python - <<'EOF'
import sys
from pathlib import Path
sys.path.insert(0, 'helden/_tools')
from parsers.chronik import load_chronik
from parsers.held import parse_frontmatter

root = Path('.')
iso = lambda d: '{2}-{1:0>2}-{0:0>2}'.format(*d.split('.'))
abende = sorted((a['datum'] for a in load_chronik(root)['spielabende']), key=iso)
done = set()
for f in sorted((root / 'abenteuer' / 'drachenchronik').glob('*-session-*.md')):
    fm, _ = parse_frontmatter(f.read_text(encoding='utf-8'))
    done.add(str(fm.get('datum', '')))
for rang, d in enumerate(abende, 1):
    print(f'{rang:02d}  {d}  {iso(d)}  ' + ('kompiliert' if iso(d) in done else 'OFFEN'))
EOF
ls abenteuer/drachenchronik/*-session-*.md
grep -nE "^## " abenteuer/drachenchronik/chronik.md
```

Ausgabe: pro Abend `NN  DD.MM.YYYY  YYYY-MM-DD  OFFEN|kompiliert`. **NN = Rang des Abends** (chronologisch,
1-basiert) — das ist die Session-Nummer für Dateiname und Frontmatter, **unabhängig** von vorhandenen Dateien.
Das `grep` liefert die Zeilennummern der H2 → Abschnitt eines Abends = von seiner `## `-Zeile bis (exklusiv)
zur nächsten `## `-Zeile (bzw. Dateiende).

Auswahl:
- leeres Argument → erster Abend mit `OFFEN`; gibt es keinen: melden „alle Abende kompiliert", Ende.
- `<DD.MM.YYYY>` → dieser Abend; nicht in der Liste → melden und Ende; schon `kompiliert` → melden und Ende
  (nichts überschreiben).
- `alle` → alle `OFFEN`-Abende in Rangfolge.

Für jeden gewählten Abend führe Schritt 3–5 aus (bei `alle`: nacheinander, damit „neue NSCs" gegen die
zuvor erzeugten Session-Dateien geprüft werden können), dann Schritt 6.

---

## Schritt 3: Session-Datei erzeugen (pro Abend)

Lies den Abschnitt des Abends aus `chronik.md` (Read mit `offset`/`limit` aus den Zeilennummern von Schritt 2).

**Zieldatei:** `abenteuer/drachenchronik/YYYY-MM-DD-session-NN.md` (`NN` zweistellig). Existiert sie schon →
**nicht überschreiben**; melden und zum nächsten Abend.

**Frontmatter (exakt so):**

```yaml
---
typ: session
abenteuer: Drachenchronik
session: <NN als Zahl, z. B. 2>
datum: YYYY-MM-DD
helden:
  - "[[helden/illaen-baernhold/_illaen|Illaen]]"
---
```

**H1:** `# Drachenchronik · Session NN · YYYY-MM-DD`

**Body: genau diese H2 in genau dieser Reihenfolge** (Dashboard-Parser `parsers/kampagne.py` und Chronik-Tab
lesen sie unter diesen Namen; **jede** Zeile, die mit `## ` beginnt, trennt Sektionen — im Inhalt daher nur
H3/H4/fett verwenden):

1. `## Zusammenfassung`
2. `## Verlauf`
3. `## AsP/LeP-Verlauf`
4. `## Neue NSCs / Orte`
5. `## Offene Fäden / Cliffhanger`
6. `## Loot / AP-Vergabe`

Direkt unter H1 folgt sofort `## Zusammenfassung`; die **erste Textzeile** der Zusammenfassung ist ein
vollständiger, eigenständiger Satz (das Dashboard zeigt diese Zeile als Kurzinhalt der Session; keine
Blockquote-, `---`- oder `→`-Zeile davor).

### Inhaltstreue (oberstes Gebot)

- Nur verwenden, was in der Roh-Mitschrift dieses Abends steht. **Nichts hinzudichten, nichts „glätten",
  was Bedeutung ändert**, keine Regelwerk-Ergänzungen, keine Vermutungen über Motive oder Zusammenhänge.
  Wiki-Wissen dient nur zum Verlinken, nie zum Auffüllen von Inhalt.
- Fehlt zu einer Sektion **jede** Quelle → die Sektion enthält nur die Zeile `—`.
- Unsichere Lesarten (unklare Namen, Abkürzungen, mehrdeutige Sätze, offensichtliche Tippfehler bei Namen)
  in der Session-Datei mit `(?)` direkt hinter dem Wort markieren; die Roh-Schreibweise beibehalten.
  Alle `(?)`-Stellen im Report (Schritt 6) auflisten.

### Sektionen im Detail

**Zusammenfassung** — 2–5 Sätze, ausschließlich aus dem Verlauf abgeleitet.

**Verlauf** — verdichtete, aber vollständige Wiedergabe der Ereignisse in Quellreihenfolge; kein Ereignis
weglassen, nichts umsortieren.
- **IG-Tag-Gliederung:** Eine Zeile, die *ausschließlich* ein Ingame-Datum ist (`Datum: 13. Phex -> Start`,
  `**17. Phex**`, ebenso `Namenloser Tag`-Formen), beginnt einen IG-Tag → `### <IG-Datum wörtlich>`
  (Zusatz wie `-> Start` als `(Start)` anhängen). Kommt dasselbe IG-Datum später erneut als eigene Zeile vor,
  eigene `###` mit Zusatz `(Fortsetzung)` — nicht zusammenführen. Steht Text **vor** dem ersten Datums-Marker
  oder hat der Abend **gar keinen** Marker: `### IG-Datum nicht genannt` als erste Überschrift; **kein Datum
  ableiten oder aus dem Vorabend fortschreiben**.
- Fett/kursiv gesetzte Zeilen, die *nicht* ausschließlich ein IG-Datum sind (`**Wissensaufbau im Hesindetempel**`,
  `**Punin Akademie am 15. Phex**`, `*Zurück im Dorf*`, `Sightseeing in Punin`), sind Szenen-Titel → als eigene
  Zeile `**Titel**` innerhalb des laufenden IG-Tags übernehmen, darunter die zugehörigen Bullets. Nicht in
  IG-Tage umwandeln, auch wenn ein Datum im Titel vorkommt.
- Unterpunkte der Quelle bleiben als eingerückte Bullets erhalten (Verdichten ja, Struktur verflachen nein).
- **Reines Markdown, keine HTML-Tags** (der Chronik-Tab schreibt `Verlauf` per Write-back zurück).
  Bilder (`<img src="…">`) nicht einbetten, stattdessen eine Zeile `(Bild: <dateiname> — siehe Roh-Chronik)`
  an der Stelle des Bildes (Dateiname = Teil hinter dem letzten `\` bzw. `/`).

**AsP/LeP-Verlauf** — nur Werte, die die Roh-Chronik für diesen Abend nennt (Format wie in `_abenteuer.md`:
`Illaen: AsP 38 → 24 → 30 (Reg)`); sonst `—`.

**Neue NSCs / Orte** — Bullets `- **Name** — Rolle/Beschreibung (nur was die Chronik sagt)`.
Getrennt in `### NSCs` und `### Orte` (leere Untergruppe weglassen; ist beides leer: nur `—`). „Neu" = in
diesem Abend erstmals vorkommend: vorher die `## Neue NSCs / Orte`-Sektionen bereits vorhandener früherer
Session-Dateien (`abenteuer/drachenchronik/*-session-*.md` mit früherem `datum`) lesen und Bekannte nicht
erneut als neu listen (neue Information zu einem Bekannten gehört in den Verlauf). Die Roh-Schreibweise der
Namen übernehmen.

**Offene Fäden / Cliffhanger** — Bullets nur für Dinge, die die Chronik selbst als offen ausweist
(ungeklärte Fragen, ausdrückliche Entscheidungen/Pläne/Ideen für später, Abbruch mitten in einer Szene);
nichts ableiten. Sonst `—`.

**Loot / AP-Vergabe** — nur Genanntes (AP, Gegenstände, Geld, Empfehlungen/Belohnungen); sonst `—`.

### Wiki-Links

- Begriffe (Zauber, Götter, Orte, Kulturen, Regelbegriffe, Sonderfertigkeiten), zu denen im `wiki/` ein Artikel
  existiert, als `[[wiki/dsa-4.1/<ordner>/<datei>|Text]]` verlinken (Pfad ab Vault-Root, ohne `.md`, wie in
  `helden/illaen-baernhold/`). **Vorher per Glob/Grep prüfen, dass der Artikel bzw. die Heading existiert;
  nie auf Verdacht verlinken.** Prüf-Beispiele:
  `Glob wiki/dsa-4.1/**/*<begriff>*.md` und `Grep -i "^#+ .*<begriff>" wiki/dsa-4.1`.
- Magische Sonderfertigkeiten und andere Sammelartikel: Anker-Link
  `[[wiki/dsa-4.1/sonderfertigkeiten/magische-sonderfertigkeiten#Astrale Meditation|Astrale Meditation]]`
  (User-Konvention, kein Einzel-Artikel pro SF).
- Nur Begriffe mit echtem Nachschlagewert verlinken, **je Begriff einmal pro Session** (erste Erwähnung).
  Nicht jedes Wort verlinken; Links nur in Fließtext/Bullets, nicht in Überschriften.

---

## Schritt 4: Kampagnen-Index `_drachenchronik.md` aktualisieren

Datei: `abenteuer/drachenchronik/_drachenchronik.md`. **Nur diese zwei Stellen** ändern; Status, Kurz-Synopse,
Helden-Roster und Session-Template bleiben unverändert (Bereinigung ist ein separater Schritt).

**(a) Tabelle unter `## Sessions`** (Kopf `| # | Datum | Kurzinhalt |` beibehalten). Pro kompiliertem Abend
eine Zeile, aufsteigend nach `#`:

```
| NN | YYYY-MM-DD | [[abenteuer/drachenchronik/YYYY-MM-DD-session-NN\|<Kurztitel>]] — <1 Satz> |
```

- `NN` in der Tabelle als Zahl ohne Vornull (`1`, `2`, …), Kurztitel 2–5 Wörter, 1 Satz aus der
  Zusammenfassung; keine `|` im Text (Link-Pipe ist `\|`).
- Die Platzhalterzeile `| — | — | Noch keine Sessions gespielt |` entfernen, sobald die erste echte Zeile steht.
- Idempotent: existiert bereits eine Zeile mit gleicher Nr **oder** gleichem Datum → diese Zeile ersetzen,
  nicht anhängen.

**(b) `## Offene Fäden`:** die Punkte aus dem Abschnitt „Offene Fäden / Cliffhanger" der neuen Session als
Bullets `- <Text> *(Session NN)*` ergänzen. Bestehende Einträge nicht löschen/ändern; inhaltlich schon
vorhandene nicht doppelt anlegen. Den Platzhalter `*(Leer — wächst pro Session.)*` entfernen, sobald echte
Einträge stehen. Stand die Session-Sektion auf `—`: nichts ergänzen.

---

## Schritt 5: Wiki-Lücken melden

Begriffe/Regeln aus dem Abend, die für das Spiel relevant sind und zu denen im `wiki/` **kein** Artikel existiert
(per Glob/Grep geprüft — dieselben Prüfungen wie bei den Links; z. B. Orte, Kulturen, Regelmechaniken),
kommen in `wiki-luecken.md` (Vault-Root). Format der Datei: Datum · betroffene Wiki-Datei · Befund · Vorschlag.

1. Kopf und letzte Abschnitte lesen; höchste bisherige `L<Zahl>` bestimmen: `grep -oE "^### L[0-9]+" wiki-luecken.md`.
2. Neuen Abschnitt **am Ende** anhängen (heutiges Datum: `date +%F`):

```markdown
## YYYY-MM-DD — /session-compile DD.MM.YYYY (ausgelöst durch Spielabend DD.MM.YYYY)

### L<nächste Zahl>: <Kurztitel der Lücke>

- **Wiki-Datei:** `<betroffene bzw. vorgeschlagene Datei>`
- **Befund:** <was im Abend vorkam und was im Wiki fehlt; Fundstelle im Abend nennen>
- **Vorschlag:** <konkret, mit Quellbuch falls bekannt>

---
```

3. Keine Lücke → **keinen** Abschnitt anlegen. Bei `alle`: ein Abschnitt pro Abend (mit Lücken), fortlaufend
   nummeriert. Bestehende Einträge nicht ändern.

---

## Schritt 6: Report

Pro Abend melden:
- erzeugte Datei (Pfad) — oder „übersprungen: existiert bereits"
- Anzahl Verlauf-IG-Tage (`###` in `## Verlauf`), NSC-Anzahl, Orts-Anzahl
- alle `(?)`-Stellen (Zitat + Grund)
- neue Wiki-Links (Liste) und neue Wiki-Lücken (L-Nummern)
- Import-Status aus Schritt 1 (inkl. Hinweis, falls die Drive-Quelle nicht erreichbar war)

Zum Schluss:

```bash
git status --short
```

Die neuen Session-Dateien dem User zur **Sichtung** vorlegen (`.obsidian/workspace.json` und `Welcome.md`
sind dauerhaft dirty und gehören nicht dazu). **Nicht committen** — Commit erst nach User-Sichtung.
