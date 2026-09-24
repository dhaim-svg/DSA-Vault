---
name: design-audit
description: Read-only Design-Audit des Illaen-Dashboards (helden/_tools/) mit der Diagnose-Checkliste aus taste-skill/redesign-skill, gefiltert durch die etablierten Projekt-Entscheidungen. Liefert eine priorisierte Befundliste, ändert keinen Code. Nutzen bei "/design-audit", "Dashboard-Design prüfen", "UI-Review".
disable-model-invocation: true
---

# /design-audit

Audit-Linse für das Dashboard. **Nur Diagnose** — Ergebnis ist eine Befundliste, aus der der
User D-EPICs macht. Kein Code, keine Änderung an `helden/`, `output/` oder Templates.

Quelle der Checkliste: `Leonxlnx/taste-skill` → `skills/redesign-skill/SKILL.md` (MIT-Lizenz,
Copyright 2026 Leonxlnx), hier auf ein dichtes, druckoptimiertes Charakterbogen-Dashboard
zugeschnitten. Kontext: das Dashboard ist **kein** Marketing-/SaaS-Auftritt.

---

## Phase 1: Scan

1. Static-Render frisch erzeugen: `python helden/_tools/render-held.py illaen-baernhold`.
2. Stack lesen: `helden/_tools/templates/` (Jinja-Partials), `static/*.css`, `static/*.js`.
   Vanilla CSS, kein Framework, **keine neuen Libraries** (kein CDN-Font, kein npm).
3. Seite im Browser ansehen, wie in `.claude/skills/sprint-run/references/browser-verify.md`
   beschrieben (sicher lesend gegen den Static-Render per HTTP, nichts zurückschreiben).
   Alle 8 Tabs, mindestens bei 1280 px und 400 px Breite, plus Druckansicht.

## Phase 2: Diagnose — anwendbare Prüfpunkte

Nur diese Bereiche der Vorlage sind hier relevant:

- **Typografie:** Schriften mit/ohne Charakter, Hierarchie über Gewichte 500/600, `tabular-nums`
  für Zahlenspalten (Proben, Kosten, Gewicht, Geld), Zeilenlänge langer Artikelvorschauen
  (~65 Zeichen), Umbruch-Waisen (`text-wrap: pretty`), Versal-Überschriften überall.
- **Farbe/Flächen:** ein Akzent, eine Grau-Familie (warm vs. kalt gemischt?), Sättigung,
  Schattenrichtung/-tönung, Konsistenz Hell/Dunkel.
- **Layout:** Rhythmus und Ausrichtung nebeneinanderliegender Karten (Titel/Werte/Buttons auf
  gleicher Höhe), Abstände, max-width, Grid statt Flex-Prozentrechnung, `100vh` vs. `100dvh`.
- **Zustände:** Hover/Active/Fokus-Ring (Barrierefreiheit, **Pflicht**), Leer-/Fehlerzustände,
  Fehlermeldungen ohne `alert()`, aktive Tab-Kennzeichnung, Transition nur über
  `transform`/`opacity`.
- **Komponenten:** generische Karten (Rand+Schatten+Fläche überall), Modals, Badge-Formen.
- **Code:** Div-Suppe vs. semantisches HTML, Inline-Styles, feste Pixelbreiten, willkürliche
  `z-index`-Werte (Skala vorhanden?), toter/auskommentierter Code, `<title>`/Meta.

**Nicht anwenden (Marketing-Themen ohne Bezug):** Hero-/Pricing-/Testimonial-/FAQ-Muster,
Footer-Linkfarm, Legal-Links, Cookie-Consent, 404-Seite, Fake-Namen/-Zahlen, AI-Phrasen-Bans,
Lucide-vs-Phosphor, Parallax/Scroll-Reveals/Glasmorphismus/Grain, Hintergrundfotos,
Sidebar-Verbot, „mehr Weißraum" (das Dashboard ist bewusst dicht).

## Phase 3: Projektfilter — was NICHT als Mangel gilt

Vor jedem Befund gegenprüfen. Diese Entscheidungen sind bewusst und dokumentiert:

- **Papier-Optik** (getönte Fläche) — Ruling D-056: Druck ist weiß, `print-color-adjust:exact`
  wird **nicht** gesetzt.
- **Druck-Kontraste** sind gemessen (`--paper-ink` 14,62 : 1 / 18,52 : 1, `--paper-rule`); jede
  Farbänderung braucht Neumessung über den echten PDF-Pfad, nicht nur Print-Emulation.
- **Informationsdichte** ist Absicht (Charakterbogen), Touch-Ziele ≥ 44 px nur ≤ 480 px.
- Etablierte Layout-Entscheidungen: siehe Memory `feedback_frontend_design_planning.md`
  (Design-Entscheidungen für illaen-dashboard) und `helden/_tools/BACKLOG.md` (Done-Einträge).
  Was dort entschieden wurde, nicht erneut als Befund führen — höchstens als Rückfrage.
- Zustands-Chips-Werte sind Hausregel (D-048), Wund-Malus regelkonform (D-041).

## Phase 4: Befundliste

Ausgabe als Tabelle, absteigend nach Nutzen/Risiko:

| # | Bereich | Befund (mit Fundstelle Datei:Zeile bzw. Tab/Breite) | Beleg (Messung/Screenshot) | Vorschlag | Effort S/M/L | Druck-/Kontrast-Risiko |
|---|---------|------------------------------------------------------|----------------------------|-----------|--------------|------------------------|

Regeln:
- Jeder Befund mit **Beleg** (gemessen oder gesehen), nicht geschätzt.
- Am Ende Fix-Reihenfolge nach der Vorlage: Schrift → Farbe → Hover/Fokus → Layout/Abstand →
  Komponenten → Leer-/Fehlerzustände → Feinschliff — nur die tatsächlich befundenen.
- Ergebnis nach `output/design-audit-YYYY-MM-DD.md` schreiben; User entscheidet, welche Funde
  als D-EPICs in `helden/_tools/BACKLOG.md` gehen. Kein Sprint-Start, kein Code.
