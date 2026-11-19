#!/usr/bin/env python3
"""Generation-only script: freezes worlds before experiment; no policy code."""
from itertools import product
import hashlib, json, random
from pathlib import Path

N=16
VALUES=range(4)
SEED=20261119

def library():
    def uniq(rows):
        return sorted(set(rows))
    return {
        'constant': uniq([tuple([a]*N) for a in VALUES]),
        'affine_mod4': uniq([tuple((a*x+b)%4 for x in range(N)) for a,b in product(VALUES,repeat=2)]),
        'even_odd': uniq([tuple(a if x%2==0 else b for x in range(N)) for a,b in product(VALUES,repeat=2)]),
        'threshold': uniq([tuple(a if x<t else b for x in range(N)) for t in range(1,N) for a,b in product(VALUES,repeat=2)]),
        'xor_bits': uniq([tuple(a if (x&mask).bit_count()%2==0 else b for x in range(N)) for mask in range(1,N) for a,b in product(VALUES,repeat=2)]),
        'periodic': uniq([tuple(pattern[x%p] for x in range(N)) for p in [2,3,4] for pattern in product(VALUES,repeat=p)]),
    }

def generate():
    rng=random.Random(SEED)
    lib=library()
    records=[]
    for family in ('constant','affine_mod4','even_odd','threshold','xor_bits','periodic'):
        rows=lib[family]
        draw=rng.sample(rows,12) if len(rows)>=12 else [rng.choice(rows) for _ in range(12)]
        for k,row in enumerate(draw):
            records.append({'id':f'{family}-{k+1:02}','kind':family,'y':list(row)})
    known=set.union(*[set(rows) for rows in lib.values()])
    for k in range(24):
        for _ in range(10000):
            row=tuple(rng.randrange(4) for _ in range(N))
            if row not in known:break
        else:raise RuntimeError('OOD sampling exhausted')
        records.append({'id':f'out_of_library-{k+1:02}','kind':'out_of_library','y':list(row)})
    return {'protocol':'APERCEPT01','seed':SEED,'alphabet_size':4,'input_size':16,'observation_budget':5,'problems':records}

if __name__=='__main__':
    output=Path(__file__).with_name('FROZEN_WORLDS.json')
    content=json.dumps(generate(),ensure_ascii=False,sort_keys=True,indent=2)+'\n'
    output.write_text(content,encoding='utf8')
    print(f'{output} {len(content.encode())} bytes sha256={hashlib.sha256(content.encode()).hexdigest()}')
    print('Unique functions per representation family:',{k:len(v) for k,v in library().items()})
