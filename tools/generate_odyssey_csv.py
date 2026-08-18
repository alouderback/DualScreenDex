import json, csv, os, collections, unicodedata

SRC = 'talrega-dex/data.json'
d = json.load(open(SRC))
species, types = d['species'], d['types']

TID = {int(k): v['name'] for k, v in types.items()}
RAW = {int(k): v['matchup'] for k, v in types.items()}
DECODE = {0: 1.0, 5: 0.5, 20: 2.0, 1: 0.0}

# Column order mirrors the stock vanilla_matchup.csv, with the 18th slot holding Aether.
ORDER = ['Normal','Fire','Water','Electric','Grass','Ice','Fighting','Poison','Ground',
         'Flying','Psychic','Bug','Rock','Ghost','Dragon','Dark','Steel','Aether']
assert sorted(ORDER) == sorted(TID.values()), 'type set mismatch'
NAME2ID = {v: k for k, v in TID.items()}

def mult(atk, dfn):
    return DECODE[RAW[NAME2ID[atk]][NAME2ID[dfn]]]

# OCR strips everything outside [A-Za-z -]; write names the scanner can actually produce.
SPECIAL = {'Nidoran♀': 'Nidoran-F', 'Nidoran♂': 'Nidoran-M',
           'Farfetch’d': 'Farfetchd', 'Sirfetch’d': 'Sirfetchd', 'Mr. Mime': 'Mr Mime'}
def clean(n):
    return SPECIAL.get(n, n)

by_name = collections.defaultdict(list)
for v in species.values():
    by_name[v['name']].append(v)

base_rows, variant_rows = [], []
for name, forms in by_name.items():
    if len(forms) == 1:
        base_rows.append((forms[0], None))
        continue
    aether = [f for f in forms if 24 in f['type']]
    plain  = [f for f in forms if 24 not in f['type']]
    if len(aether) == 1 and len(plain) == 1:
        base, var, label = plain[0], aether[0], 'Aether'
    else:                                    # Farfetch'd: Kanto base + Galarian form
        forms = sorted(forms, key=lambda f: f['dexID'])
        base, var, label = forms[0], forms[1], 'Galarian'
    base_rows.append((base, None))
    variant_rows.append((var, label, base['dexID']))

base_rows.sort(key=lambda r: r[0]['dexID'])
variant_rows.sort(key=lambda r: r[2])

def typenames(f, aether_as):
    t = [TID[x] for x in f['type']]
    t = [aether_as if x == 'Aether' else x for x in t]
    return t[0].lower(), (t[1].lower() if len(t) > 1 else '')

def emit(outdir, aether_as):
    os.makedirs(outdir, exist_ok=True)
    with open(f'{outdir}/odyssey_pokedex.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['id','name','type1','type2'])
        for f, _ in base_rows:
            t1, t2 = typenames(f, aether_as)
            w.writerow([f['dexID'], clean(f['name']), t1, t2])
    with open(f'{outdir}/odyssey_regional.csv', 'w', newline='') as fh:
        w = csv.writer(fh); w.writerow(['id','region','type1','type2'])
        for f, label, baseid in variant_rows:
            t1, t2 = typenames(f, aether_as)
            w.writerow([baseid, label, t1, t2])
    with open(f'{outdir}/odyssey_matchup.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        hdr = [aether_as if x == 'Aether' else x for x in ORDER]
        w.writerow(['ATTACK/DEFENSE'] + [h.upper() for h in hdr])
        for atk in ORDER:
            label = aether_as.upper() if atk == 'Aether' else atk.upper()
            row = [label]
            for dfn in ORDER:
                m = mult(atk, dfn)
                row.append(str(int(m)) if m in (0.0, 1.0, 2.0) else '0.5')
            w.writerow(row)

emit('out/csv-only', 'Fairy')   # stock app: Aether rides in the unused Fairy slot
emit('out/fork',     'Aether')  # forked app: real Aether type

print('base entries   :', len(base_rows))
print('variant entries:', len(variant_rows))
print('total dex       :', len(base_rows) + len(variant_rows), '(expected 409)')
