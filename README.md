# DSA-Vault

Eine KI-gepflegte Regelwerk-Referenz für **Das Schwarze Auge 4.1**, strukturiert als [Obsidian](https://obsidian.md)-Vault.

Die Wiki-Artikel werden systematisch aus den offiziellen DSA-4.1-Hardcover-Regelwerken extrahiert und thematisch geordnet abgelegt. Einstiegspunkt ist [`wiki/_master-index.md`](wiki/_master-index.md).

---

## Enthaltene Regelwerke

| Buch | Kürzel | Artikel | Status |
|------|--------|---------|--------|
| Wege der Helden | WdH | ~160 | ✅ fertig |
| Wege des Schwertes | WdS | ~15 | ✅ fertig |
| Wege der Zauberei | WdZ | ~35 | ✅ fertig |
| Liber Cantiones | LC | ~200 Zauber | ✅ fertig |
| Wege der Götter | WdG | ~52 | ✅ fertig |
| Liber Liturgium | LL | ~236 Liturgien | ✅ fertig |
| Wege der Alchimie | WdA | ~22 | ✅ fertig |
| Wege des Entdeckers | WdE | — | ⚪ offen |

---

## Struktur

```
wiki/
└── dsa-4.1/
    ├── grundregeln/      Charaktererschaffung, Proben, Steigerung, Reisen, Heilung …
    ├── rassen/           Alle spielbaren Rassen (Mittelländer, Elfen, Zwerge, Orks …)
    ├── kulturen/         ~50 Kulturen, geographisch gruppiert
    ├── professionen/     ~130 Professionen (kämpferisch, magisch, geweihte …)
    ├── vor-nachteile/    Vorteile, Nachteile, Schlechte Eigenschaften, SF-Listen
    ├── sonderfertigkeiten/ SF-Übersichten (allgemein, Kampf, magisch, klerikale)
    ├── talente/          Talentregeln, Talentliste, Meta-Talente, Sprachen & Schriften
    ├── kampf/            Kampfmechanik, Manöver, SF, Referenztabellen, Waffenherstellung
    ├── magie/            Zauberregeln, Repräsentationen, Metamagie, Artefakte, Invokation …
    ├── zauber/           Alle ~200 Zauber alphabetisch (WdZ + Liber Cantiones)
    ├── rituale/          Alle Ritualtradtionen (Hexe, Druide, Geode, Schamane …)
    ├── invokation/       Dämonen, Elementare, Geister, Untote, Chimären, Golems
    ├── goetter/          Zwölf Götter, Volksreligionen, Liturgieregeln, Kulte
    ├── liturgien/        ~236 Liturgien alphabetisch (Liber Liturgium)
    ├── alchimie/         Brauregeln, Elixiere, Artefakte, Zauberzeichen, Materialien
    ├── geographie/       (folgt mit Wege des Entdeckers)
    └── buecher/          Buchprofile der extrahierten Regelwerke
```

Jeder Unterordner enthält eine `_<ordnername>.md` mit einer Übersichtstabelle aller Artikel.

---

## Hinweise

- **Artikel-Sprache:** Deutsch
- **Wiki-Links:** Obsidian-Format `[[artikel]]`
- **PDF-Rohdaten** (`raw/pdf-extracted/`) sind gitignored — nur die aufbereiteten Wiki-Artikel sind im Repo.
- Extraktions-Fortschritt und Konventionen: [`DSA-STATUS.md`](DSA-STATUS.md)
