# Golden-Render-Baseline für reine Refactorings

Bei rein verschiebenden Refactorings am Dashboard (CSS/Template-Auslagerung ohne Verhaltensänderung):
**vor der ersten Änderung** ein Golden-Rendering beider Modi erzeugen (Server-Render über
`server._render_dashboard`, Static-Render über `render-held.py`; zweimal rendern + `cmp` prüfen, dass
das Rendering selbst deterministisch ist). Jeder Refactoring-Task schließt mit `cmp baseline after`
**ohne Ausgabe** ab. Der Controller wiederholt den `cmp` selbst, nicht nur der Implementierer.

**Why:** Ein Reviewer kann tausend verschobene Zeilen nicht sinnvoll „ansehen"; der Byte-Vergleich
beweist Gleichheit in Sekunden und deckt Whitespace-Fallen auf (Jinja `trim_blocks` verschluckt eine
fehlende Leerzeile am Ende eines Partials).

**Zusätzlich statisch prüfen:** `jinja2.meta.find_undeclared_variables` je Partial gegen (Render-
Kontext ∪ im Elternteil vor dem `include` definierte Macros/`set`s) — Includes leaken kein `{% set %}`
ins Elternteil, ein reiner Byte-Vergleich mit EINEM Helden fängt Variablen-Leaks in nicht ausgeführten
Zweigen nicht.

Ändert ein Task die Ausgabe absichtlich, die Baseline bewusst und nachvollziehbar aktualisieren (Diff
zeigt genau die erwartete Zeile).

**Zusätzlich mindestens ein Render-Level-Test in pytest** (`render_dashboard(build_context(…))` gegen
den Live-Vault, `skip` falls die Held-Datei fehlt) — ein ad-hoc-`cmp` allein sichert die Zerlegung
dauerhaft nicht ab.
