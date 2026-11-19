"""Metamorphic and out-of-domain tests for the unchanged 024 oracle."""
from itertools import permutations
from time import perf_counter
from copy import deepcopy
import json
from finite_oracle import check

# Independent Python predicates accompany public manually constructed ASTs.
TRAIN=[
 ('dev_true',[['le',0,'n'],['le','n',5]],['le',['square','n'],25],lambda n:0<=n<=5,lambda n:n*n<=25),
 ('dev_false',[['le',0,'n'],['eq',['mod','n',3],0]],['le',9,['square','n']],lambda n:n>=0 and n%3==0,lambda n:n*n>=9)]
RESERVE=[
 ('reserved_true',[['le',-3,'n'],['le','n',3],['eq','n','n']],['le',['square','n'],9],lambda n:-3<=n<=3,lambda n:n*n<=9),
 ('reserved_false',[['le',0,'n'],['eq',['mod','n',7],0],['le','n',16]],['le',49,['square','n']],lambda n:0<=n<=16 and n%7==0,lambda n:n*n>=49)]

def spec(terms,conclusion):return dict(domain=[-16,16],**{'if':['and']+terms,'then':conclusion})
def summary(r):return (r['status'],r.get('witness'),r['universal_proof'])
def audit(cases):
    rows=[];base_specs=[];changed_specs=[]
    for label,terms,conclusion,p,c in cases:
        original=spec(terms,conclusion)
        base=check(original)
        witness=next((n for n in range(-16,17) if p(n) and not c(n)),None)
        assert base['status']==('COUNTEREXAMPLE' if witness is not None else 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN')
        assert base.get('witness')==witness and not base['universal_proof']
        variants=[]
        for order in permutations(terms):
            for extra in ([],[order[0]]):
                variant=spec(list(order)+extra,conclusion)
                assert summary(check(variant))==summary(base)
                variants.append(variant)
        base_specs.append(original);changed_specs.extend(variants)
        rows.append(dict(label=label,variants=len(variants),status=base['status'],witness=witness,disagreements=0))
    # Equal call budget: repeat originals to exactly the number of transformed calls.
    seconds=[]
    for collection in ([base_specs[i%len(base_specs)] for i in range(len(changed_specs))],changed_specs):
        start=perf_counter()
        for _ in range(1000):
            for obligation in collection:check(obligation)
        seconds.append(perf_counter()-start)
    return dict(rows=rows,calls_per_1000_lots=len(changed_specs)*1000,seconds_original_transformed=seconds)

if __name__=='__main__':
    # First test is the preregistered boundary counterexample to universal reading.
    boundary=spec([['le',0,'n'],['eq','n','n']],['le','n',16])
    bounded=check(boundary)
    assert bounded['status']=='NO_COUNTEREXAMPLE_WITHIN_DOMAIN' and not bounded['universal_proof']
    enlarged=next(n for n in range(-20,21) if n>=0 and not n<=16)
    assert enlarged==17
    print(json.dumps(dict(boundary=bounded,independent_extended_witness=enlarged),sort_keys=True),flush=True)
    for name,cases in [('train',TRAIN),('reserve',RESERVE)]:
        print(json.dumps(dict(split=name,**audit(cases)),sort_keys=True),flush=True)
