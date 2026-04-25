# DSA-Vault

Eine KI-gepflegte Regelwerk-Referenz für **Das Schwarze Auge 4.1**, strukturiert als [Obsidian](https://obsidian.md)-Vault.

Die Wiki-Artikel werden systematisch aus den offiziellen DSA-4.1-Hardcover-Regelwerken extrahiert und thematisch geordnet abgelegt. Einstiegspunkt ist [`wiki/_master-index.md`](wiki/_master-index.md).

---

## Enthaltene Regelwerke

| Buch | Status |
|------|--------|
| Wege der Helden (WdH) | ✅ fertig |
| Wege des Schwertes (WdS) | ✅ fertig |
| Wege der Zauberei (WdZ) | 🟢 in Arbeit |
| Wege der Götter (WdG) | ⚪ offen |
| Liber Liturgium (LL) | ⚪ offen |
| Wege der Alchimie (WdA) | ⚪ offen |
| Wege des Entdeckers (WdE) | ⚪ offen |

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
    ├── talente/          Talentregeln, Talentliste, Meta-Talente, Sprachen & Schriften
    ├── kampf/            Kampfmechanik, Manöver, SF, Referenztabellen, Waffenherstellung
    ├── magie/            Zauberregeln, Repräsentationen, Metamagie, Artefakte, Alchimie …
    ├── rituale/          Alle Ritualtradtionen (Hexe, Druide, Geode, Schamane …)
    ├── invokation/       Dämonen, Elementare, Geister, Untote, Chimären, Golems
    ├── liturgien/        (folgt mit WdG)
    ├── zauber/           (folgt mit Liber Cantiones)
    └── buecher/          Buchprofile der extrahierten Regelwerke
```

Jeder Unterordner enthält eine `_<ordnername>.md` mit einer Übersichtstabelle aller Artikel.

---

## Hinweise

- **Artikel-Sprache:** Deutsch
- **Wiki-Links:** Obsidian-Format `[[artikel]]`
- **PDF-Rohdaten** (`raw/pdf-extracted/`) sind gitignored — nur die aufbereiteten Wiki-Artikel sind im Repo.
- Extraktions-Fortschritt und Konventionen: [`DSA-STATUS.md`](DSA-STATUS.md)
