"""Detect finite vacuity against the frozen 024 reference and independent predicates."""
from time import perf_counter
import json
from finite_reference import check as reference
from finite_oracle import check as candidate

def case(name,premise,conclusion,p,c):
    return dict(name=name,spec=dict(domain=[-16,16],**{'if':premise,'then':conclusion}),p=p,c=c)
TRAIN=[
 case('empty_interval',['and',['le','n',-1],['le',0,'n']],['eq',0,1],lambda n:n<=-1 and n>=0,lambda n:False),
 case('nonempty_square',['le',0,'n'],['le',0,['square','n']],lambda n:n>=0,lambda n:n*n>=0)]
# Constructed only after candidate SHA df5f8664... was frozen.
RESERVE=[
 case('incompatible_parity',['and',['eq',['mod','n',2],0],['eq',['mod','n',2],1]],['eq',0,1],lambda n:n%2==0 and n%2==1,lambda n:False),
 case('outside_domain',['eq','n',18],['eq',0,1],lambda n:n==18,lambda n:False),
 case('bounded_multiples',['and',['le',-8,'n'],['le','n',8],['eq',['mod','n',4],0]],['le',['square','n'],64],lambda n:-8<=n<=8 and n%4==0,lambda n:n*n<=64),
 case('counterexample',['le',0,'n'],['le','n',7],lambda n:n>=0,lambda n:n<=7)]

def audit(cases):
    rows=[];true_empty=flagged_empty=false_empty=missed_empty=0
    # Baseline results are computed before candidate or oracle for this split.
    baseline=[reference(c['spec']) for c in cases]
    for c,old in zip(cases,baseline):
        new=candidate(c['spec'])
        allowed=[n for n in range(-16,17) if c['p'](n)]
        bad=next((n for n in allowed if not c['c'](n)),None)
        expected=('NO_ADMISSIBLE_INPUT_WITHIN_DOMAIN' if not allowed else 'COUNTEREXAMPLE' if bad is not None else 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN')
        assert new['status']==expected and new['admissible_inputs']==len(allowed)
        assert new.get('witness')==bad and not new['universal_proof']
        assert old['status']==('COUNTEREXAMPLE' if bad is not None else 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN')
        empty=not allowed;flagged=new['status']=='NO_ADMISSIBLE_INPUT_WITHIN_DOMAIN'
        true_empty+=empty;flagged_empty+=empty and flagged;false_empty+=not empty and flagged;missed_empty+=empty and not flagged
        rows.append(dict(name=c['name'],reference=old,candidate=new,oracle_admissible=len(allowed),oracle_witness=bad))
    times=[]
    for fn in (reference,candidate):
        start=perf_counter()
        for _ in range(1000):
            for c in cases:fn(c['spec'])
        times.append(perf_counter()-start)
    return dict(rows=rows,empty_detection=dict(TP=flagged_empty,FP=false_empty,FN=missed_empty),seconds_1000_reference_candidate=times)

if __name__=='__main__':
    # First falsification control: the old common status hides a zero-entry test.
    assert reference(TRAIN[0]['spec'])['status']==reference(TRAIN[1]['spec'])['status']
    assert candidate(TRAIN[0]['spec'])['status']!=candidate(TRAIN[1]['spec'])['status']
    unsupported=dict(domain=[-16,16],**{'if':['eq',0,1],'then':['cube','n']})
    assert reference(unsupported)['status']==candidate(unsupported)['status']=='ABSTAIN'
    for split,cases in [('train',TRAIN),('reserve',RESERVE)]:
        print(json.dumps(dict(split=split,**audit(cases)),sort_keys=True),flush=True)
