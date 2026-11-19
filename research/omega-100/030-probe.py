"""Held-out eq commutation, including asymmetric-order negative controls."""
from hashlib import sha256
from copy import deepcopy
from time import perf_counter
from collections import Counter
import json
from strict_reference import accepts as reference
from source_ast_contract import accepts as candidate

TRAIN=[('three',3,0)]
# New sources, prepared only after candidate 72e865c7... was frozen.
RESERVE=[('eleven',11,-11),('thirteen',13,-13)]

def fixtures(cases):
    out=[]
    for name,k,lower in cases:
        lines=[f'A: n est multiple de {k}.',f'B: n >= {lower}.','C: n*n >= 0.']
        raw=('\n'.join(lines)+'\n').encode();digest=sha256(raw).hexdigest()
        eq=['eq',['mod','n',k],0];le=['le',lower,'n']
        c=dict(source_sha256=digest,premises=[dict(id='A',line=1,literal=lines[0],ast=eq),dict(id='B',line=2,literal=lines[1],ast=le)],conclusion=dict(line=3,literal=lines[2],ast=['le',0,['square','n']]))
        faithful=deepcopy(c);order=deepcopy(c);order['premises'].reverse()
        swapped=deepcopy(c);swapped['premises'][0]['ast']=['eq',0,['mod','n',k]]
        residue=deepcopy(c);residue['premises'][0]['ast']=['eq',['mod','n',k],1]
        inequality=deepcopy(c);inequality['premises'][1]['ast']=['le','n',lower]
        # Independent integer oracle: equality is symmetric; the changed relations differ.
        assert all((n%k==0)==(0==n%k) for n in range(-16,17))
        assert any((n%k==0)!=(n%k==1) for n in range(-16,17))
        assert any((n>=lower)!=(n<=lower) for n in range(-16,17))
        for label,tr,expected in [('faithful',faithful,True),('premise_order',order,True),('eq_commuted',swapped,True),('residue_changed',residue,False),('le_reversed',inequality,False)]:
            out.append((name,raw,c,label,tr,expected))
    return out

def audit(cases):
    data=fixtures(cases);metrics=[];rows=[];seconds=[]
    for fn in (reference,candidate):
        counts=Counter();observed=[]
        for name,raw,c,label,tr,expected in data:
            got=fn(raw,c,tr)
            counts['TP']+=got and expected;counts['FP']+=got and not expected
            counts['FN']+=not got and expected;counts['TN']+=not got and not expected
            observed.append(dict(source=name,variant=label,accepted=got,expected=expected))
        start=perf_counter()
        for _ in range(1000):
            for _,raw,c,_,tr,_ in data:fn(raw,c,tr)
        seconds.append(perf_counter()-start);metrics.append(dict(counts));rows.append(observed)
    assert metrics[1]['FP']==metrics[1]['FN']==0
    return dict(reference=metrics[0],candidate=metrics[1],seconds_1000_reference_candidate=seconds,rows=rows)
if __name__=='__main__':
    data=fixtures(TRAIN)
    _,raw,c,_,bad,_=data[-1]
    assert not candidate(raw,c,bad)
    for split,cases in [('train',TRAIN),('reserve',RESERVE)]:
        print(json.dumps(dict(split=split,**audit(cases)),sort_keys=True),flush=True)
