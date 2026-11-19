"""Public manual contracts: source anchors plus exact AST association."""
from copy import deepcopy
from hashlib import sha256
from time import perf_counter
from collections import Counter
import json
from source_ast_contract import accepts
from finite_oracle import check

TRAIN=[('dev',['Hypothese A: n >= 0.','Hypothese B: n <= 3.','Conclusion: n*n <= 9.'],
        [['le',0,'n'],['le','n',3]],['le',['square','n'],9])]
# Created after source_ast_contract.py was frozen, SHA 081111de...33920.
RESERVE=[('bounds',['Hypothese A: n >= -3.','Hypothese B: n <= 3.','Conclusion: n*n <= 9.'],
          [['le',-3,'n'],['le','n',3]],['le',['square','n'],9]),
         ('congruence',['Hypothese A: n >= 0.','Hypothese B: n est multiple de cinq.','Conclusion: n*n >= 0.'],
          [['le',0,'n'],['eq',['mod','n',5],0]],['le',0,['square','n']])]

def fixtures(cases):
    out=[]
    for name,lines,asts,con in cases:
        raw=('\n'.join(lines)+'\n').encode();digest=sha256(raw).hexdigest()
        contract=dict(source_sha256=digest,premises=[dict(id=label,line=i+1,literal=lines[i],ast=asts[i]) for i,label in enumerate(('A','B'))],
                      conclusion=dict(line=3,literal=lines[2],ast=con))
        faithful=deepcopy(contract)
        variants=[('faithful',faithful,True)]
        missing=deepcopy(faithful);missing['premises']=missing['premises'][:1];variants.append(('missing_B',missing,False))
        swapped=deepcopy(faithful);swapped['premises'][0]['ast'],swapped['premises'][1]['ast']=swapped['premises'][1]['ast'],swapped['premises'][0]['ast'];variants.append(('swapped_AST',swapped,False))
        changed=deepcopy(faithful);changed['conclusion']['ast']=['eq',0,1];variants.append(('changed_conclusion_AST',changed,False))
        stale=deepcopy(faithful);stale['source_sha256']='stale';variants.append(('stale_source',stale,False))
        for label,tr,expected in variants:out.append((name,raw,contract,label,tr,expected))
        # Arithmetic is a separate downstream check, not the oracle of source fidelity.
        obligation=dict(domain=[-16,16],**{'if':['and']+asts,'then':con})
        assert check(obligation)['status']=='NO_COUNTEREXAMPLE_WITHIN_DOMAIN'
    return out

def audit(cases):
    data=fixtures(cases);reports=[];metrics=[];seconds=[]
    # Source-anchor + identifier reference is evaluated before exact AST binding.
    for binding in (False,True):
        counts=Counter();rows=[]
        for name,raw,contract,label,tr,expected in data:
            got=accepts(raw,contract,tr,bind_ast=binding)
            counts['TP']+=got and expected;counts['FP']+=got and not expected
            counts['FN']+=not got and expected;counts['TN']+=not got and not expected
            rows.append(dict(source=name,variant=label,accepted=got,expected_manual=expected,source_sha256=sha256(raw).hexdigest()))
        start=perf_counter()
        for _ in range(1000):
            for _,raw,contract,_,tr,_ in data:accepts(raw,contract,tr,bind_ast=binding)
        seconds.append(perf_counter()-start);metrics.append(dict(counts));reports.append(rows)
    assert metrics[1]['FP']==metrics[1]['FN']==0
    return dict(reference=metrics[0],candidate=metrics[1],seconds_1000_reference_candidate=seconds,rows=reports)
if __name__=='__main__':
    first=fixtures(TRAIN)[2]
    _,raw,contract,_,swapped,_=first
    assert accepts(raw,contract,swapped,bind_ast=False) and not accepts(raw,contract,swapped)
    for split,cases in [('train',TRAIN),('reserve',RESERVE)]:
        print(json.dumps(dict(split=split,**audit(cases)),sort_keys=True),flush=True)
