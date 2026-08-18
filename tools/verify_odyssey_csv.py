import json, collections

# ---- Reimplementation of the app's Kotlin logic ------------------------------
ENUM = ['NORMAL','FIRE','WATER','ELECTRIC','GRASS','ICE','FIGHTING','POISON','GROUND','FLYING',
        'PSYCHIC','BUG','ROCK','GHOST','DRAGON','STEEL','DARK','FAIRY','UNKNOWN']          # PokemonType.kt
ENUM_FORK = ENUM[:-1] + ['AETHER', 'UNKNOWN']                                              # fork adds AETHER

def from_string(v, enum):                      # PokemonType.fromString
    v = (v or '').strip().upper()
    return v if v in enum else 'UNKNOWN'

def parse_pokedex(path, enum):                 # CsvParsers.parsePokedex
    out = []
    for line in open(path):
        tok = line.split(',')
        if not tok or not tok[0].strip().lstrip('-').isdigit():
            continue                           # header skipped exactly as the app does
        t2 = from_string(tok[3], enum) if len(tok) > 3 and tok[3].strip() != '' else 'UNKNOWN'
        out.append((int(tok[0]), tok[1].strip(), from_string(tok[2], enum), t2))
    return out

def parse_regional(path, enum):                # CsvParsers.parseRegionalForms
    out = []
    for line in open(path):
        tok = line.split(',')
        if not tok or not tok[0].strip().lstrip('-').isdigit():
            continue
        t2 = from_string(tok[3], enum) if len(tok) > 3 and tok[3].strip() != '' else 'UNKNOWN'
        out.append((int(tok[0]), tok[1].strip(), from_string(tok[2], enum), t2))
    return out

def parse_matchup(path):                       # CsvParsers.parseMatchupChart
    lines = [l.rstrip('\n') for l in open(path) if l.strip()]
    headers = [h.strip().upper().replace('﻿','') for h in lines[0].split(',')]
    table = {}
    for line in lines[1:]:
        tok = line.split(',')
        atk = tok[0].strip().upper().replace('﻿','')
        for j in range(1, len(tok)):
            if j >= len(headers): break
            s = tok[j].strip()
            m = 0.5 if s == '1/2' else (1.0 if s == '' else float(s))
            table[f'{atk}_{headers[j]}'] = m
    return table

def multiplier(atk, dfn, chart):               # TypeMatchup.getMultiplier, custom profile branch
    return chart.get(f'{atk}_{dfn}', 1.0)      # (applyMechanics skipped: custom + matchupFilePath)

def matchups(t1, t2, chart, enum):             # MainViewModel.calculateMatchups
    weak, resist = {}, {}
    for atk in enum:
        if atk == 'UNKNOWN': continue
        m = multiplier(atk, t1, chart) * (multiplier(atk, t2, chart) if t2 != 'UNKNOWN' else 1.0)
        if m > 1.0: weak[atk] = m
        if m < 1.0: resist[atk] = m
    return weak, resist

# ---- Ground truth straight from talrega-dex data.json ------------------------
d = json.load(open('talrega-dex/data.json'))
species, types = d['species'], d['types']
TID = {int(k): v['name'].upper() for k, v in types.items()}
RAW = {int(k): v['matchup'] for k, v in types.items()}
DEC = {0: 1.0, 5: 0.5, 20: 2.0, 1: 0.0}
N2I = {v: k for k, v in TID.items()}

def truth(t1, t2):
    weak, resist = {}, {}
    for atk_id, atk in TID.items():
        m = DEC[RAW[atk_id][N2I[t1]]]
        if t2: m *= DEC[RAW[atk_id][N2I[t2]]]
        if m > 1.0: weak[atk] = m
        if m < 1.0: resist[atk] = m
    return weak, resist

# ---- Compare, for every one of the 409 dex entries ---------------------------
def run(tag, folder, enum, aether_slot):
    dex   = parse_pokedex(f'out/{folder}/odyssey_pokedex.csv', enum)
    reg   = parse_regional(f'out/{folder}/odyssey_regional.csv', enum)
    chart = parse_matchup(f'out/{folder}/odyssey_matchup.csv')

    unknown = [r for r in dex + reg if r[2] == 'UNKNOWN']
    entries = [(r[1], r[2], r[3]) for r in dex] + [(f'{r[0]}/{r[1]}', r[2], r[3]) for r in reg]

    # map every real Odyssey species onto the CSV slot naming
    def slot(n): return aether_slot if n == 'AETHER' else n
    by_types = collections.Counter()
    mismatches = []
    for v in species.values():
        tn = [TID[x] for x in v['type']]
        t1, t2 = tn[0], (tn[1] if len(tn) > 1 else None)
        exp_w, exp_r = truth(t1, t2)
        got_w, got_r = matchups(slot(t1), slot(t2) if t2 else 'UNKNOWN', chart, enum)
        exp_w = {slot(k): x for k, x in exp_w.items()}
        exp_r = {slot(k): x for k, x in exp_r.items()}
        if exp_w != got_w or exp_r != got_r:
            mismatches.append((v['name'], t1, t2, exp_w, got_w, exp_r, got_r))
        by_types[(t1, t2)] += 1

    print(f'--- {tag} ---')
    print(f'  dex rows parsed        : {len(dex)}   regional rows: {len(reg)}   total {len(dex)+len(reg)}')
    print(f'  rows with UNKNOWN type1: {len(unknown)}  {"OK" if not unknown else unknown[:5]}')
    print(f'  chart cells            : {len(chart)} (expect 324)')
    print(f'  species checked        : {len(species)}')
    print(f'  matchup MISMATCHES     : {len(mismatches)}  {"ALL CORRECT" if not mismatches else ""}')
    for m in mismatches[:5]: print('    ', m)
    return len(mismatches)

a = run('CSV-ONLY (stock app, Aether -> Fairy slot)', 'csv-only', ENUM,      'FAIRY')
print()
b = run('FORK (real AETHER enum)',                    'fork',     ENUM_FORK, 'AETHER')
print()
print('RESULT:', 'both paths numerically exact' if a == 0 and b == 0 else 'FAILURES PRESENT')
