"""Falsify semantic sufficiency of the unchanged 022 manual contract filter."""
from collections import Counter
from time import perf_counter
import json
from gate import gate
from read import packetize
from premise_contract import filter_contract

TRAIN=(['Hypothese : n est positif ou nul.','Hypothese : n est au plus trois.','Hypothese : n est entier.'], 'Conclusion : n au carre est au plus neuf.',lambda n:0<=n<=3,lambda n:n*n<=9)
RESERVE=(['Hypothese : n est multiple de quatre.','Hypothese : n est non nul.'], 'Conclusion : n au carre est au moins seize.',lambda n:n%4==0 and n!=0,lambda n:n*n>=16)

def measure(case,use_filter):
    premises,conclusion,condition,predicate=case
    assert all(not condition(n) or predicate(n) for n in range(-12,13))
    raw=('\n'.join(premises+[conclusion])+'\n').encode()
    inventory=packetize(raw,'synthetic.md'); pid=inventory['packets'][0]['packet_id']
    def e(role,line,literal): return dict(role=role,line=line,literal=literal,packet_id=pid)
    ev=[e('premise',i+1,p) for i,p in enumerate(premises)]
    con=e('conclusion',len(premises)+1,conclusion)
    # Three separate evaluations: faithful + correct contract; unconditional + correct
    # contract; last condition omitted + incomplete contract. No model is used.
    variants=[('faithful',ev,ev,condition),('unconditional',[],ev,lambda n:True),
              ('incomplete',ev[:-1],ev[:-1],lambda n:(0<=n) if len(ev)==3 else n%4==0)]
    out=Counter(); witnesses={}
    for name,given,required,scope in variants:
        if name=='incomplete' and len(ev)==3:
            # Omit upper bound rather than redundant integrality condition.
            given=ev[:1]+ev[2:];required=given;scope=lambda n:n>=0
        claim=dict(claim_id='Ccase',packet_id=pid,evidence=given+[con])
        result=gate(raw,'synthetic.md',dict(source_blob=inventory['source_blob'],claims=[claim]))
        contract=dict(source_blob=inventory['source_blob'],requirements={(con['line'],conclusion):[(x['line'],x['literal']) for x in required]})
        accepted=filter_contract(result,contract)['eligible'] if use_filter else result['accepted']
        bad=next((n for n in range(-12,13) if scope(n) and not predicate(n)),None)
        is_true=bad is None
        out['TP']+=bool(accepted) and is_true
        out['FP']+=bool(accepted) and not is_true
        out['FN']+=not accepted and is_true
        out['abstentions']+=not accepted
        if bad is not None:witnesses[name]=bad
        assert not result['horn_rules'] and result['automatic_promotions']==0
        assert all(c['semantic_fidelity']=='NOT_VERIFIED' for c in accepted)
    return dict(out),witnesses

if __name__=='__main__':
    for split,case in [('train',TRAIN),('reserve',RESERVE)]:
        for candidate in (False,True):
            observed=measure(case,candidate);t=perf_counter()
            for _ in range(1000): measure(case,candidate)
            print(json.dumps(dict(split=split,candidate=candidate,observed=observed,seconds_1000=perf_counter()-t),sort_keys=True))
            assert observed[0]['FP']==(1 if candidate else 2)
            assert observed[0]['TP']==1 and observed[0]['FN']==0
