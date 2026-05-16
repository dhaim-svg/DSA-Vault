"""Parser for DSA 4.1 hero markdown files."""
import re
import yaml
from pathlib import Path

WIKILINK_RE = re.compile(r'\[\[([^\]|\\]+)(?:[\\]?\|([^\]]+))?\]\]')

EIGENSCHAFT_MAP = {
    'Mut': 'MU', 'Klugheit': 'KL', 'Intuition': 'IN', 'Charisma': 'CH',
    'Fingerfertigkeit': 'FF', 'Gewandtheit': 'GE', 'Konstitution': 'KO',
    'Körperkraft': 'KK', 'Geschwindigkeit': 'GS', 'Sozialstatus': 'SO',
}
EIGENSCHAFT_FULL = {v: k for k, v in EIGENSCHAFT_MAP.items()}

BASISWERT_MAP = {
    'Lebensenergie': 'LE', 'Ausdauer': 'AU', 'Astralenergie': 'AE',
    'Karmaenergie': 'KE', 'Magieresistenz': 'MR', 'Initiative': 'INI',
    'Attacke': 'AT', 'Parade': 'PA', 'Fernkampf-Basis': 'FK',
}

HAUPTEIGENSCHAFTEN = ['MU', 'KL', 'IN', 'CH', 'FF', 'GE', 'KO', 'KK']


def strip_wikilink(s: str) -> str:
    def repl(m):
        path, display = m.group(1), m.group(2)
        if display:
            return display.strip()
        return path.split('/')[-1].replace('-', ' ')
    return WIKILINK_RE.sub(repl, str(s)).strip()


def extract_wiki_path(s: str) -> str | None:
    m = WIKILINK_RE.search(str(s))
    return m.group(1).strip() if m else None


def strip_markdown(s: str) -> str:
    s = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
    s = re.sub(r'\*(.+?)\*', r'\1', s)
    s = re.sub(r'_(.+?)_', r'\1', s)
    return s.strip()


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith('---'):
        return {}, text
    parts = text.split('---', 2)
    if len(parts) < 3:
        return {}, text
    return (yaml.safe_load(parts[1]) or {}), parts[2]


def _split_table_row(line: str) -> list[str]:
    """Split a markdown table row on | while treating \| as a literal pipe."""
    PLACEHOLDER = '\x00PIPE\x00'
    line = line.replace(r'\|', PLACEHOLDER)
    cells = [c.replace(PLACEHOLDER, '|').strip() for c in line.strip('|').split('|')]
    return cells


def parse_md_table(block: str) -> list[dict]:
    """Parse the first markdown table in block into a list of dicts."""
    lines = []
    in_table = False
    for line in block.splitlines():
        if re.match(r'\s*\|', line):
            lines.append(line)
            in_table = True
        elif in_table:
            break
    if len(lines) < 2:
        return []
    headers = _split_table_row(lines[0])
    rows = []
    for line in lines[2:]:  # skip separator
        cells = _split_table_row(line)
        if any(c for c in cells):
            row = {headers[i]: (cells[i] if i < len(cells) else '') for i in range(len(headers))}
            rows.append(row)
    return rows


def split_sections(text: str, level: int = 2) -> dict[str, str]:
    prefix = '#' * level + ' '
    sections: dict[str, list[str]] = {'__pre__': []}
    current = '__pre__'
    for line in text.splitlines():
        if line.startswith(prefix):
            current = line[level + 1:].strip()
            sections.setdefault(current, [])
        else:
            sections.setdefault(current, []).append(line)
    return {k: '\n'.join(v) for k, v in sections.items()}


def safe_int(s, default=0) -> int:
    if s is None:
        return default
    try:
        return int(str(s).replace('+', '').replace('−', '-').replace('—', '0').strip() or '0')
    except ValueError:
        return default


def load_held(vault_root: Path, slug: str) -> dict:
    base = vault_root / 'helden' / slug

    # ------------------------------------------------------------------ #
    # _illaen.md: frontmatter + Eigenschaften + Basiswerte
    # ------------------------------------------------------------------ #
    text = (base / '_illaen.md').read_text(encoding='utf-8')
    fm, rest = parse_frontmatter(text)
    h2 = split_sections(rest, 2)

    eig_bw_text = h2.get('Eigenschaften & Basiswerte', '')
    h3 = split_sections(eig_bw_text, 3)

    eigenschaften: dict[str, dict] = {}
    for row in parse_md_table(h3.get('Eigenschaften', '')):
        raw = strip_wikilink(row.get('Eigenschaft', ''))
        m = re.search(r'\(([A-Z]{2,3})\)', raw)
        if m:
            abbr = m.group(1)
        else:
            abbr = next((v for k, v in EIGENSCHAFT_MAP.items() if k in raw), raw)
        aktuell = safe_int(row.get('Aktuell', 0))
        start = safe_int(row.get('Start', 0))
        mod_raw = row.get('Mod.', '0').replace('—', '0').replace('−', '-')
        eigenschaften[abbr] = {
            'aktuell': aktuell,
            'start': start,
            'mod': safe_int(mod_raw),
            'full': EIGENSCHAFT_FULL.get(abbr, abbr),
        }

    basiswerte: dict[str, dict] = {}
    for row in parse_md_table(h3.get('Basiswerte', '')):
        raw = strip_wikilink(row.get('Basiswert', ''))
        m = re.search(r'\(([A-Z]{1,3})\)', raw)
        if m:
            abbr = m.group(1)
        else:
            abbr = next((v for k, v in BASISWERT_MAP.items() if k in raw), raw)
        aktuell_raw = row.get('Aktuell', '') or ''
        basiswerte[abbr] = {
            'aktuell': safe_int(aktuell_raw),
            'formel': row.get('Formel', ''),
        }

    # ------------------------------------------------------------------ #
    # talente.md
    # ------------------------------------------------------------------ #
    text = (base / 'talente.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    tal_secs = split_sections(rest, 2)

    talente: dict[str, list[dict]] = {}
    for sec_name, sec_content in tal_secs.items():
        if sec_name.startswith('__'):
            continue
        rows = parse_md_table(sec_content)
        if not rows:
            continue
        is_kampf = 'Kampftechnik' in sec_name
        is_sprache = 'Sprach' in sec_name
        is_schrift = 'Schrift' in sec_name
        grp = []
        for r in rows:
            name_raw = (
                r.get('Kampftechnik', '')
                or r.get('Sprache', '')
                or r.get('Schrift', '')
                or r.get('Talent', '')
            )
            name = strip_wikilink(name_raw).strip('*').strip()
            if not name or name == '—':
                continue
            entry: dict = {'name': name}
            if is_kampf:
                entry['at'] = safe_int(r.get('AT'))
                pa_raw = r.get('PA', '—')
                entry['pa'] = safe_int(pa_raw) if pa_raw not in ('—', '', '-') else None
                entry['stk'] = r.get('Stk', '')
            if is_sprache or is_schrift:
                entry['probe'] = 'K ' + (r.get('Komplexität', '') or '')
            else:
                entry['probe'] = r.get('Probe', '') or r.get('Komplexität', '')
            entry['taw'] = safe_int(r.get('TaW', 0))
            grp.append(entry)
        if grp:
            talente[sec_name] = grp

    # ------------------------------------------------------------------ #
    # zauber.md
    # ------------------------------------------------------------------ #
    text = (base / 'zauber.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    zau_secs = split_sections(rest, 2)

    # Parse Spontane Modifikationen section
    spontane_mods: list[dict] = []
    illaen_mods_max: int = 0
    spmod_sec = zau_secs.get('Spontane Modifikationen', '')
    if spmod_sec:
        for row in parse_md_table(spmod_sec):
            mod_name = row.get('Modifikation', '').strip()
            if mod_name:
                spontane_mods.append({
                    'name': mod_name,
                    'zfp': row.get('ZfP-Kosten', ''),
                    'probe': row.get('Probe-Mod', ''),
                    'zd': row.get('ZD+', ''),
                })
        # Parse Illaen sub-section for mods_max
        h3_zau = split_sections(spmod_sec, 3)
        illaen_sub = h3_zau.get('Illaen — effektive Werte', '')
        if illaen_sub:
            for row in parse_md_table(illaen_sub):
                if 'Max. Modifikationen' in (row.get('', '') or ''):
                    # table has two columns with empty header; look for the row
                    pass
            # Try to find the max from raw text
            m_max = re.search(r'Max\. Modifikationen.*?=\s*\*\*(\d+)\*\*', illaen_sub)
            if m_max:
                illaen_mods_max = int(m_max.group(1))

    zauber: list[dict] = []
    for row in parse_md_table(zau_secs.get('Zauberliste', '')):
        name_raw = row.get('Zauber', '')
        wiki_path = extract_wiki_path(name_raw)
        name = strip_wikilink(name_raw)
        if not name or name.startswith('---'):
            continue
        notizen = strip_wikilink(row.get('Notizen', '') or '')
        zauber.append({
            'name': name,
            'wiki_path': wiki_path,
            'probe': row.get('Probe', ''),
            'zfw': safe_int(row.get('ZfW', 0)),
            'merkmale': row.get('Merkmale', ''),
            'haus': (row.get('Haus', '') or '').strip() == '×',
            'komp': row.get('Komp', ''),
            'desc': notizen,
            'zd': row.get('ZD', ''),
            'kosten': row.get('Kosten', ''),
            'wirkung': strip_wikilink(row.get('Wirkung', '') or ''),
            'mods': row.get('Modifikationen', ''),
        })

    # ------------------------------------------------------------------ #
    # rituale.md
    # ------------------------------------------------------------------ #
    text = (base / 'rituale.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    rit_secs = split_sections(rest, 2)

    stabzauber: list[dict] = []
    for sec_name, sec_content in rit_secs.items():
        if 'Stabzauber' in sec_name:
            for row in parse_md_table(sec_content):
                name = strip_wikilink(row.get('Stabzauber', ''))
                if name:
                    stabzauber.append({
                        'name': name,
                        'vol': row.get('Vol', ''),
                        'effekt': strip_wikilink(row.get('Effekt (Kurzform)', '') or row.get('Effekt', '')),
                    })
            break

    # Parse Zauberspeicher-Inhalt (### sub-section inside Stabzauber)
    zauberspeicher_slots: list[dict] = []
    for sec_name, sec_content in rit_secs.items():
        if 'Stabzauber' in sec_name:
            h3_rit = split_sections(sec_content, 3)
            for row in parse_md_table(h3_rit.get('Zauberspeicher-Inhalt', '')):
                zauberspeicher_slots.append({
                    'slot': row.get('Slot', ''),
                    'asp': row.get('AsP', ''),
                    'zauber': row.get('Gespeicherter Zauber', ''),
                    'mods': row.get('Erschwernis-Mods', ''),
                    'erneuerung': row.get('Letzte Erneuerung', ''),
                })
            break

    andere_rituale: list[dict] = []
    for row in parse_md_table(rit_secs.get('Andere Rituale', '')):
        name = strip_wikilink(row.get('Ritual', ''))
        if name:
            andere_rituale.append({
                'name': name,
                'effekt': strip_wikilink(row.get('Effekt (Kurzform)', '') or row.get('Effekt', '')),
            })

    # ------------------------------------------------------------------ #
    # sonderfertigkeiten.md
    # ------------------------------------------------------------------ #
    text = (base / 'sonderfertigkeiten.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    sf_secs = split_sections(rest, 2)

    sf_magisch: list[dict] = []
    for row in parse_md_table(sf_secs.get('Magische Sonderfertigkeiten', '')):
        name_raw = row.get('Sonderfertigkeit', '')
        wiki_path = extract_wiki_path(name_raw)
        name = strip_wikilink(name_raw)
        if name:
            sf_magisch.append({'name': name, 'wiki_path': wiki_path, 'desc': strip_wikilink(row.get('Beschreibung / Nutzen', ''))})

    sf_allg: list[dict] = []
    for row in parse_md_table(sf_secs.get('Allgemeine Sonderfertigkeiten', '')):
        name_raw = row.get('Sonderfertigkeit', '')
        wiki_path = extract_wiki_path(name_raw)
        name = strip_wikilink(name_raw)
        if name:
            sf_allg.append({'name': name, 'wiki_path': wiki_path, 'desc': strip_wikilink(row.get('Beschreibung / Nutzen', ''))})

    # ------------------------------------------------------------------ #
    # vor-nachteile.md
    # ------------------------------------------------------------------ #
    text = (base / 'vor-nachteile.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    vn_secs = split_sections(rest, 2)

    def parse_vn_table(sec_name: str, name_col: str, stufe_col: str, detail_col: str) -> list[dict]:
        result = []
        for row in parse_md_table(vn_secs.get(sec_name, '')):
            name = strip_wikilink(row.get(name_col, ''))
            if not name:
                continue
            anm_raw = row.get(detail_col, '') or ''
            result.append({
                'name': strip_markdown(strip_wikilink(name)),
                'stufe': row.get(stufe_col, '').replace('—', ''),
                'anmerkung': strip_markdown(strip_wikilink(anm_raw)),
            })
        return result

    vorteile = parse_vn_table('Vorteile', 'Vorteil', 'Stufe/Wert', 'Anmerkung')
    nachteile = parse_vn_table('Nachteile', 'Nachteil', 'Stufe/Wert', 'Details')
    schlecht = []
    for row in parse_md_table(vn_secs.get('Schlechte Eigenschaften', '')):
        name = strip_markdown(strip_wikilink(row.get('Schlechte Eigenschaft', '')))
        if name:
            schlecht.append({
                'name': name,
                'stufe': row.get('Stufe', ''),
                'konsequenz': strip_markdown(strip_wikilink(row.get('Konsequenz', ''))),
            })

    # Extract Wahrer Name from raw rows (before stripping)
    wahrer_name = ''
    wahrer_name_bedeutung = ''
    stigma = ''
    for row in parse_md_table(vn_secs.get('Nachteile', '')):
        name_plain = strip_wikilink(row.get('Nachteil', ''))
        detail_raw = row.get('Details', '') or ''
        if 'Wahrer Name' in name_plain:
            m_name = re.search(r'\*\*([^*]+)\*\*', detail_raw)
            m_bed = re.search(r'[„"]([^"„"]+)["""]', detail_raw)
            if m_name:
                wahrer_name = m_name.group(1)
            if m_bed:
                wahrer_name_bedeutung = m_bed.group(1)
        if 'Stigma' in name_plain:
            # e.g. "Stigma · Hexensträhne" or "Stigma"
            stigma = name_plain.replace('Stigma', '').replace('·', '').strip() or 'Stigma'

    # ------------------------------------------------------------------ #
    # ausruestung.md
    # ------------------------------------------------------------------ #
    text = (base / 'ausruestung.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    aus_secs = split_sections(rest, 2)

    waffen: list[dict] = []
    for row in parse_md_table(aus_secs.get('Nahkampfwaffen', '')):
        name = strip_wikilink(row.get('Waffe', ''))
        if not name:
            continue
        waffen.append({
            'name': strip_markdown(name),
            'typ_be': row.get('Typ/BE', ''),
            'dk': row.get('DK', ''),
            'tp': row.get('TP', ''),
            'ini': row.get('Ini', ''),
            'at': row.get('AT', ''),
            'pa': row.get('PA', ''),
            'wm': row.get('WM', ''),
            'bf': row.get('akt. BF', '') or row.get('akt.BF', ''),
        })

    inventar: list[dict] = []
    for row in parse_md_table(aus_secs.get('Inventar', '')):
        name = strip_wikilink(row.get('Gegenstand', ''))
        if name:
            inventar.append({
                'name': name,
                'anzahl': row.get('Anzahl', ''),
            })

    reise: list[dict] = []
    for row in parse_md_table(aus_secs.get('Reiseausrüstung', '')):
        name = strip_wikilink(row.get('Gegenstand', ''))
        if name:
            reise.append({
                'name': name,
                'menge': row.get('Menge', '') or row.get('Anzahl', ''),
                'anmerkung': strip_wikilink(row.get('Anmerkung', '')),
            })

    geld = ''
    for line in aus_secs.get('Geld', '').splitlines():
        stripped = line.strip()
        if stripped.startswith('**Startgeld'):
            geld = re.sub(r'\*+', '', stripped)
            geld = re.sub(r'\s+', ' ', geld).strip()
            break
        elif 'Dukaten' in stripped and not geld:
            geld = strip_markdown(strip_wikilink(stripped))

    # ------------------------------------------------------------------ #
    # steigerungs-log.md
    # ------------------------------------------------------------------ #
    text = (base / 'steigerungs-log.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    log_secs = split_sections(rest, 2)

    steigerungslog: list[dict] = []
    for row in parse_md_table(log_secs.get('Protokoll', '')):
        datum = (row.get('Datum', '') or '').strip()
        if datum and datum != '—':
            steigerungslog.append({
                'datum': datum,
                'aktion': strip_wikilink(row.get('Aktion', '')),
                'kosten': row.get('Kosten', ''),
                'begruendung': strip_wikilink(row.get('Begründung', '') or ''),
            })
    steigerungslog.reverse()

    # ------------------------------------------------------------------ #
    # vorgeschichte.md
    # ------------------------------------------------------------------ #
    text = (base / 'vorgeschichte.md').read_text(encoding='utf-8')
    _, rest = parse_frontmatter(text)
    vg_lines = []
    for line in rest.splitlines():
        if line.startswith('# ') or line.startswith('→ ') or line.strip() == '---':
            continue
        vg_lines.append(line)
    vorgeschichte = '\n'.join(vg_lines).strip()
    # Split into paragraphs
    paragraphs = [p.strip() for p in re.split(r'\n{2,}', vorgeschichte) if p.strip()]

    # ------------------------------------------------------------------ #
    # Assemble and return
    # ------------------------------------------------------------------ #
    ap_gesamt = fm.get('ap_gesamt', 0)
    stufe = int(fm.get('stufe', 1))
    # DSA 4.1 AP thresholds per stage
    AP_STUFEN = {2: 300, 3: 750, 4: 1500, 5: 2700, 6: 4200, 7: 6300, 8: 9450,
                 9: 13500, 10: 18900}
    next_stufe_ap = AP_STUFEN.get(stufe + 1)
    ap_bis_naechste = (next_stufe_ap - ap_gesamt) if next_stufe_ap else None

    # Short profession (strip parenthetical)
    profession_raw = fm.get('profession', '')
    kolleg = ''
    m_kol = re.search(r'\(([^)]+)\)', profession_raw)
    if m_kol:
        kolleg = m_kol.group(1)
    profession_short = re.sub(r'\s*\([^)]*\)', '', profession_raw).strip()

    return {
        'meta': {
            'name': fm.get('name', slug),
            'rasse': fm.get('rasse', ''),
            'kultur': fm.get('kultur', ''),
            'profession': profession_raw,
            'profession_short': profession_short,
            'kolleg': kolleg,
            'tradition': fm.get('tradition', ''),
            'stufe': stufe,
            'ap_gesamt': ap_gesamt,
            'ap_eingesetzt': fm.get('ap_eingesetzt', 0),
            'ap_verfuegbar': fm.get('ap_verfuegbar', 0),
            'wahrer_name': wahrer_name,
            'wahrer_name_bedeutung': wahrer_name_bedeutung,
            'stigma': stigma,
        },
        'eigenschaften': eigenschaften,
        'basiswerte': basiswerte,
        'talente': talente,
        'zauber': zauber,
        'rituale': {'stabzauber': stabzauber, 'andere': andere_rituale, 'zauberspeicher_slots': zauberspeicher_slots},
        'spontane_mods': spontane_mods,
        'mods_max': illaen_mods_max,
        'sf': {'magisch': sf_magisch, 'allgemein': sf_allg},
        'vor_nachteile': {'vorteile': vorteile, 'nachteile': nachteile, 'schlecht': schlecht},
        'ausruestung': {'waffen': waffen, 'inventar': inventar, 'reise': reise, 'geld': geld},
        'steigerungslog': steigerungslog,
        'vorgeschichte': vorgeschichte,
        'vorgeschichte_paragraphs': paragraphs,
        '_ap_bis_naechste_stufe': ap_bis_naechste,
    }
