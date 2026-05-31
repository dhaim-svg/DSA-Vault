# Sprint 3 Handoff — Tab-Navigation + AP & Steigerung

## Fertig (alle Tasks abgeschlossen)

- ✅ Task 1: Project management scaffold (BACKLOG.md, sprint retros, CLAUDE.md)
- ✅ Task 2: held_writer.py — table_append_row locator kind
- ✅ Task 3: held.py — steigerbar_talente + steigerbar_zauber + _skt_for_section
- ✅ Task 4: tabs.js — client-side tab controller
- ✅ Task 5: dashboard.html.j2 — 5-tab layout + window.DSA.steigern + script tags
- ✅ Task 6: steigern.js — cost math + render + 4-PATCH chain

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten
- ⭐ Steigern-Tab: AP-Übersicht, Eigenschaften/Talente/Zauber steigerbar
- 📋 Profil-Tab: Vor/Nachteile, Ausrüstung, Vorgeschichte
- Tab-Persistenz via sessionStorage (bleibt nach Browser-Reload)

## Verifikation

- **Test Suite:** 44/44 Testfälle bestanden (14 writer + 7 steigerbar + 23 dice)
- **Static Render:** illaen-baernhold-dashboard.html erfolgreich generiert
- **Tab-Struktur:** Alle 5 Tab-IDs vorhanden (kampf, talente, zauber, steigern, profil)
- **JavaScript:** tabs.js, steigern.js, dice.js erfolgreich geladen
- **AP-Daten:** verfuegbar=5, eingesetzt=3845, gesamt=3850, stufe=3 ✓

## Offene Punkte / bekannte Einschränkungen

- `ap_bis_naechste` zeigt negativen Wert (-2350) — AP_STUFEN-Thresholds in held.py stimmen nicht mit Illaens frontmatter-Stufe überein (pre-existing)
- Sprachen mit Komplexitäts-Grenze (TaW ≤ Komplexität) noch nicht implementiert → D-008
- Stufen-Aufstieg → D-009
- Partial-failure bei Steigerung (PATCH 1 OK, PATCH 2 fail): Stat schon erhöht, AP nicht abgezogen → git revert als Recovery

## Als nächstes (Sprint 4)

- D-004: Inventar / Geld / Verbrauch
- D-005: Zauberspeicher im Stab
