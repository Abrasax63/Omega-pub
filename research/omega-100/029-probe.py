"""Measure exact-AST binding false rejections without changing the reference."""
from copy import deepcopy
from time import perf_counter
from hashlib import sha256
import json
from source_ast_contract import accepts

TRAIN=[('train',['A: n est pair.','B: n >= 0.','C: n*n >= 0.'],[['eq',['mod','n',2],0],['le',0,'n']],['le',0,['square','n']],lambda n:n%2==0 and n>=0)]
RESERVE=[('five',['A: n est multiple de cinq.','B: n <= 10.','C: n*n >= 0.'],[['eq',['mod','n',5],0],['le','n',10]],['le',0,['square','n']],lambda n:n%5==0 and n<=10),
         ('seven',['A: n est multiple de sept.','B: n >= -7.','C: n*n >= 0.'],[['eq',['mod','n',7],0],['le',-7,'n']],['le',0,['square','n']],lambda n:n%7==0 and n>=-7)]

def evaluate(cases):
    data=[];rows=[]
    for name,lines,asts,con,oracle in cases:
        raw=('\n'.join(lines)+'\n').encode();digest=sha256(raw).hexdigest()
        c=dict(source_sha256=digest,premises=[dict(id=k,line=i+1,literal=lines[i],ast=asts[i]) for i,k in enumerate(('A','B'))],conclusion=dict(line=3,literal=lines[2],ast=con))
        faithful=deepcopy(c)
        order=deepcopy(c);order['premises'].reverse()
        equivalent=deepcopy(c);equivalent['premises'][0]['ast']=['eq',asts[0][2],asts[0][1]]
        bad=deepcopy(c);bad['premises'][0]['ast']=['eq',asts[0][1],1]
        # Independent predicate checks for the changed equality and contradiction.
        divisor=asts[0][1][2]
        assert all(oracle(n)==(0==n%divisor and (n<=10 if name=='five' else n>=-7 if name=='seven' else n>=0)) for n in range(-16,17))
        assert any((n%divisor==0)!=(n%divisor==1) for n in range(-16,17))
        for label,t,expected in [('faithful',faithful,True),('premise_order',order,True),('commuted_equality',equivalent,True),('changed_residue',bad,False)]:
            got=accepts(raw,c,t)
            rows.append(dict(source=name,variant=label,expected_semantic_contract=expected,accepted=got))
            data.append((raw,c,t))
    # Compare the same calls: original reference before its anchor-only diagnostic.
    times=[]
    for bind in (True,False):
        start=perf_counter()
        for _ in range(1000):
            for raw,c,t in data:accepts(raw,c,t,bind_ast=bind)
        times.append(perf_counter()-start)
    assert all(not r['accepted'] for r in rows if r['variant']=='changed_residue')
    return dict(rows=rows,false_rejections=sum(r['expected_semantic_contract'] and not r['accepted'] for r in rows),
                false_accepts=sum(not r['expected_semantic_contract'] and r['accepted'] for r in rows),seconds_1000_strict_anchor_only=times)
if __name__=='__main__':
    for split,cases in [('train',TRAIN),('reserve',RESERVE)]:
        result=evaluate(cases)
        assert result['false_rejections']==len(cases) and result['false_accepts']==0
        print(json.dumps(dict(split=split,**result),sort_keys=True),flush=True)
