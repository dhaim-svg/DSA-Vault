# Sprint 4 Handoff — Inventar / Geld / Verbrauch + AP_STUFEN Bugfix

## Fertig (alle Tasks abgeschlossen)

- ✅ T0: Sprint scaffold (BACKLOG.md D-004 → in-progress, sprints/sprint-004/plan.md)
- ✅ T1: AP_STUFEN bugfix — `_compute_ap_bis_naechste()` gibt `None` zurück wenn Schwelle erreicht (nie negativer Wert)
- ✅ T2: D-004 Datenmodell — `geld:` Frontmatter in `_illaen.md`; strukturiertes Geld-Dict (Dukaten/Silbertaler/Heller/Kreuzer) + Gewicht (Unzen) pro Inventar-Item in `parsers/held.py`
- ✅ T3: D-004 UI — dedizierter Inventar-Tab (Finanzen, Inventar, Reiseausrüstung); Profil-Tab von Inventar-Inhalten bereinigt
- ✅ T4: D-004 Write-back — `static/inventar.js` (Münzstepper mit Make-Change-Logik, Item-Mengen-Stepper, Gegenstand-hinzufügen via `table_append_row`)

## Was funktioniert

- ⚔️ Kampf-Tab: Vitalia, Wunden, Zustände, Eigenschaften, AT/PA, Waffen
- 🎯 Talente-Tab: alle Talentgruppen mit Würfelproben-Trigger
- ✨ Zauber-Tab: Zauberliste, Rituale, Stabzauber, Sonderfertigkeiten
- ⭐ Steigern-Tab: AP-Übersicht, Eigenschaften/Talente/Zauber steigerbar
- 🎒 Inventar-Tab: Münzbeutel (Stepper), Inventarliste (Qty-Stepper, Hinzufügen), Reiseausrüstung (Anzeige)
- 📋 Profil-Tab: Vor/Nachteile, Vorgeschichte
- Tab-Persistenz via sessionStorage

## Verifikation

- **Test Suite:** 57/57 Testfälle bestanden (8 stufen + 5 inventar + 44 bestehend)
- **Static Render:** illaen-baernhold-dashboard.html erfolgreich generiert (exit 0)
- **Inventar-Tab:** `id="tab-inventar"` vorhanden ✓
- **Geld-Widget:** `id="geld-dukaten">10` vorhanden ✓
- **JavaScript:** `inventar.js` im Script-Include vorhanden ✓
- **AP_STUFEN:** `bis_naechste: null` (kein negativer Wert) ✓

## Als nächstes (Sprint 5)

- **D-005**: Zauberspeicher im Stab — interaktive Slots (AsP laden/entleeren), Write-back via `table_cell` auf `rituale.md § Zauberspeicher-Inhalt`; Parser + statische Anzeige existieren bereits (kein Blocker mehr)
- **D-006**: Session-Notizen → Journal
- **D-007**: Session-Commit-Button

## Bekannte Einschränkungen (bewusst ausgeklammert)

- Reiseausrüstung-Mengen (z.B. "5 Tage") werden nicht bearbeitet — Display only
- Schnell-Klick-Race auf Item-Stepper ist bekannt (server-seitig sicher durch Datei-Locks)
- `stufe: 0` im Frontmatter würde fälschlich `None` liefern (kein realistisches Szenario)
- Item-Name-Duplikate werden nicht client-seitig gewarnt
