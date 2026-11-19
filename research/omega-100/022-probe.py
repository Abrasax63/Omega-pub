"""Public synthetic manual-contract experiment; fixtures are not model output."""
import json
from collections import Counter
from time import perf_counter
from gate import gate
from read import packetize
from premise_contract import filter_contract

TRAIN=[(['Hypothese : n est pair.'],'Conclusion : n au carre est pair.',lambda n:n%2==0,lambda n:n*n%2==0),
       (['Hypothese : n est non nul.'],'Conclusion : n au carre est au moins un.',lambda n:n!=0,lambda n:n*n>=1)]
# Created after premise_contract.py was frozen at SHA256 87d4c8cb...216e4c7.
RESERVE=[(['Hypothese : n est multiple de trois.'],'Conclusion : n au cube est multiple de vingt-sept.',lambda n:n%3==0,lambda n:n**3%27==0),
         (['Hypothese : n est positif ou nul.','Hypothese : n est au plus deux.'],'Conclusion : n au carre est au plus quatre.',lambda n:0<=n<=2,lambda n:n*n<=4)]

def evaluate(cases,candidate):
    counts=Counter(); witnesses=[]
    for premises,conclusion,condition,predicate in cases:
        assert all(not condition(n) or predicate(n) for n in range(-8,9))
        witnesses.append(next(n for n in range(-8,9) if not predicate(n)))
        raw=('\n'.join(premises+[conclusion])+'\n').encode()
        inv=packetize(raw,'synthetic.md'); packet=inv['packets'][0]['packet_id']
        def evidence(role,line,literal):
            return dict(role=role,line=line,literal=literal,packet_id=packet)
        ev=[evidence('premise',i+1,p) for i,p in enumerate(premises)]
        con=evidence('conclusion',len(premises)+1,conclusion)
        claims=[dict(claim_id='Cfaithful',packet_id=packet,evidence=ev+[con]),
                dict(claim_id='Comitted',packet_id=packet,evidence=ev[:-1]+[con]),
                dict(claim_id='Crole',packet_id=packet,evidence=ev[:-1]+[dict(ev[-1],role='limitation'),con])]
        result=gate(raw,'synthetic.md',dict(source_blob=inv['source_blob'],claims=claims))
        assert len(result['accepted'])==3 and not result['horn_rules'] and result['automatic_promotions']==0
        contract=dict(source_blob=inv['source_blob'],requirements={(len(premises)+1,conclusion):[(i+1,p) for i,p in enumerate(premises)]})
        accepted=filter_contract(result,contract)['eligible'] if candidate else result['accepted']
        ids={c['claim_id'] for c in accepted}
        counts['TP']+='Cfaithful' in ids; counts['FN']+='Cfaithful' not in ids
        counts['FP']+=sum(x in ids for x in ('Comitted','Crole'))
        counts['abstentions']+=3-len(ids)
        if candidate:
            assert not filter_contract(result,dict(contract,source_blob='stale'))['eligible']
            assert not filter_contract(result,dict(contract,requirements={}))['eligible']
            assert all(c['hypothesis_scope']=='NOT_ESTABLISHED' for c in accepted)
    return dict(counts),witnesses

def main():
    for name,cases in [('train',TRAIN),('reserve',RESERVE)]:
        for candidate in (False,True):
            observed=evaluate(cases,candidate)
            t=perf_counter()
            for _ in range(1000): evaluate(cases,candidate)
            print(json.dumps(dict(split=name,candidate=candidate,observed=observed,seconds_1000=perf_counter()-t),sort_keys=True))
            if candidate: assert observed[0]==dict(TP=2,FN=0,FP=0,abstentions=4)
if __name__=='__main__': main()
