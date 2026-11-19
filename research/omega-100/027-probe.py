"""Separate source-premise fidelity from mathematical validity using manual AST pairs."""
from time import perf_counter
from hashlib import sha256
import json
from finite_oracle import check

def row(name,text,a,b,conclusion,pa,pb,pc):
    return dict(name=name,source=text,terms=[a,b],conclusion=conclusion,pa=pa,pb=pb,pc=pc)
TRAIN=[
 row('essential','Hypothese A: n >= 0.\nHypothese B: n <= 2.\nConclusion: n*n <= 4.\n',
     ['le',0,'n'],['le','n',2],['le',['square','n'],4],lambda n:n>=0,lambda n:n<=2,lambda n:n*n<=4),
 row('valid_generalization','Hypothese A: n >= 0.\nHypothese B: n est multiple de trois.\nConclusion: n*n >= 0.\n',
     ['le',0,'n'],['eq',['mod','n',3],0],['le',0,['square','n']],lambda n:n>=0,lambda n:n%3==0,lambda n:n*n>=0)]
# Reserved pairs are manual fixtures, never model output.
RESERVE=[
 row('lost_lower_bound','Hypothese A: n <= 5.\nHypothese B: n >= -5.\nConclusion: n*n >= 0.\n',
     ['le','n',5],['le',-5,'n'],['le',0,['square','n']],lambda n:n<=5,lambda n:n>=-5,lambda n:n*n>=0),
 row('lost_congruence','Hypothese A: n >= 0.\nHypothese B: n est multiple de cinq.\nConclusion: n*n >= 0.\n',
     ['le',0,'n'],['eq',['mod','n',5],0],['le',0,['square','n']],lambda n:n>=0,lambda n:n%5==0,lambda n:n*n>=0)]

def specs(c):
    return [dict(domain=[-16,16],**{'if':['and']+c['terms'],'then':c['conclusion']}),
            dict(domain=[-16,16],**{'if':c['terms'][0],'then':c['conclusion']})]

def audit(cases):
    results=[]
    for c in cases:
        entries=[]
        for i,spec in enumerate(specs(c)):
            observed=check(spec)
            allowed=[n for n in range(-16,17) if c['pa'](n) and (i==1 or c['pb'](n))]
            witness=next((n for n in allowed if not c['pc'](n)),None)
            assert allowed and observed['admissible_inputs']==len(allowed)
            assert observed.get('witness')==witness
            assert observed['status']==('COUNTEREXAMPLE' if witness is not None else 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN')
            assert not observed['universal_proof']
            retained={'A','B'} if i==0 else {'A'}
            complete={'A','B'}<=retained
            entries.append(dict(translation='faithful' if i==0 else 'omitted_B',source_premises_complete=complete,result=observed))
        assert entries[0]['result']['admissible_inputs']!=entries[1]['result']['admissible_inputs']
        results.append(dict(name=c['name'],source=c['source'],source_sha256=sha256(c['source'].encode()).hexdigest(),translations=entries))
    timings=[]
    calls=[s for c in cases for s in specs(c)]
    start=perf_counter()
    for _ in range(1000):
        for spec in calls:check(spec)
    timings.append(perf_counter()-start)
    start=perf_counter()
    for _ in range(1000):
        for c in cases:
            for retained in ({'A','B'},{'A'}):bool({'A','B'}<=retained)
    timings.append(perf_counter()-start)
    return dict(rows=results,seconds_1000_arithmetic_manual_completeness=timings)

if __name__=='__main__':
    # Essential missing premise is a falsification control before reserved cases.
    assert check(specs(TRAIN[0])[1])['witness']==3
    for split,cases in [('train',TRAIN),('reserve',RESERVE)]:
        r=audit(cases)
        if split=='reserve':
            assert all(x['result']['status']=='NO_COUNTEREXAMPLE_WITHIN_DOMAIN' for c in r['rows'] for x in c['translations'])
            assert all(not c['translations'][1]['source_premises_complete'] for c in r['rows'])
        print(json.dumps(dict(split=split,**r),sort_keys=True),flush=True)
