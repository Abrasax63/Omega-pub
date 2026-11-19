"""Compare manual quarantine/filter with a finite manual-AST arithmetic oracle."""
from time import perf_counter
from collections import Counter
import json
from gate import gate
from read import packetize
from premise_contract import filter_contract
from finite_oracle import check

def case(label,premise,conclusion,p,c,oracle_p,oracle_c):
    return dict(label=label,premise=premise,conclusion=conclusion,
                spec=dict(domain=[-16,16],**{'if':p,'then':c}),op=oracle_p,oc=oracle_c)
TRAIN=[
 case('even_square','Hypothese : n est pair.','Conclusion : n au carre est pair.',
      ['eq',['mod','n',2],0],['eq',['mod',['square','n'],2],0],lambda n:n%2==0,lambda n:n*n%2==0),
 case('nonzero_missing','Hypothese : n est entier.','Conclusion : n au carre est au moins un.',
      ['eq','n','n'],['le',1,['square','n']],lambda n:True,lambda n:n*n>=1)]
# These four specifications were created after finite_oracle.py was frozen.
RESERVE=[
 case('nonnegative_square','Hypothese : n est positif ou nul.','Conclusion : n au carre est positif ou nul.',
      ['le',0,'n'],['le',0,['square','n']],lambda n:n>=0,lambda n:n*n>=0),
 case('multiple_five','Hypothese : n est multiple de cinq.','Conclusion : n au carre est au moins vingt-cinq.',
      ['eq',['mod','n',5],0],['le',25,['square','n']],lambda n:n%5==0,lambda n:n*n>=25),
 case('boundary','Hypothese : n est positif ou nul.','Conclusion : n est au plus quinze.',
      ['le',0,'n'],['le','n',15],lambda n:n>=0,lambda n:n<=15),
 case('outside_language','Hypothese : n est positif ou nul.','Conclusion : n au cube est positif ou nul.',
      ['le',0,'n'],['le',0,['cube','n']],lambda n:n>=0,lambda n:n**3>=0)]

def baseline(c):
    raw=(c['premise']+'\n'+c['conclusion']+'\n').encode()
    inv=packetize(raw,'fixture.md');pid=inv['packets'][0]['packet_id']
    ev=[dict(role=role,line=i,literal=lit,packet_id=pid) for role,i,lit in [('premise',1,c['premise']),('conclusion',2,c['conclusion'])]]
    data=dict(source_blob=inv['source_blob'],claims=[dict(claim_id='C1',packet_id=pid,evidence=ev)])
    result=gate(raw,'fixture.md',data)
    filt=filter_contract(result,dict(source_blob=inv['source_blob'],requirements={(2,c['conclusion']):[(1,c['premise'])]}))
    assert len(filt['eligible'])==1 and not result['horn_rules'] and result['automatic_promotions']==0
    assert filt['eligible'][0]['semantic_fidelity']=='NOT_VERIFIED'
    return filt

def pipeline(c,candidate):
    baseline(c)
    return check(c['spec']) if candidate else dict(status='ELIGIBLE_MANUAL_CONTRACT_ONLY')

def run(cases):
    reports=[]
    for c in cases:
        b=pipeline(c,False);r=pipeline(c,True)
        witnesses=[n for n in range(-16,17) if c['op'](n) and not c['oc'](n)]
        expected='ABSTAIN' if c['label']=='outside_language' else ('COUNTEREXAMPLE' if witnesses else 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN')
        assert r['status']==expected and not r['universal_proof']
        if expected=='COUNTEREXAMPLE':assert r['witness']==witnesses[0]
        reports.append(dict(label=c['label'],baseline=b['status'],result=r,oracle_witness=witnesses[0] if witnesses else None))
    times=[]
    for candidate in (False,True):
        start=perf_counter()
        for _ in range(1000):
            for c in cases:pipeline(c,candidate)
        times.append(perf_counter()-start)
    start=perf_counter()
    for _ in range(1000):
        for c in cases:check(c['spec'])
    return dict(reports=reports,seconds_1000_baseline_candidate=times,seconds_1000_oracle_only=perf_counter()-start)

if __name__=='__main__':
    # Falsification controls precede measured runs, including a hidden invalid branch.
    for c in [dict(domain=[-16,16],**{'if':['eq','n','n'],'then':['cube','n']}),
              dict(domain=[-16,16],**{'if':['and',['eq',0,1],['sin','n']],'then':['eq',1,1]}),
              dict(domain=[-17,16],**{'if':['eq',1,1],'then':['eq',1,1]})]:
        assert check(c)['status']=='ABSTAIN'
    for split,cases in [('train',TRAIN),('reserve',RESERVE)]:
        print(json.dumps(dict(split=split,**run(cases)),sort_keys=True))
