"""Audit opt-in independence of premise citations."""
import argparse
import copy
import hashlib
import json
from time import perf_counter

from premise_guard import route as reference

HOLD = 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN'
REJECT = 'REJECTED_SOURCE_AST_BINDING'


def fixture(lo, modulus, condensed, policy):
    first, second = f'n est au moins {lo}', f'n est multiple de {modulus}'
    goal = f'n est au moins {lo-1}'
    lines = [first+' et '+second, goal] if condensed else [first,second,goal]
    raw = ('\n'.join(lines)+'\n').encode()
    second_line = 1 if condensed else 2
    contract = dict(source_sha256=hashlib.sha256(raw).hexdigest(), premises=[
            dict(id='A',line=1,literal=lines[0],ast=['le',lo,'n']),
            dict(id='B',line=second_line,literal=lines[second_line-1],ast=['eq',['mod','n',modulus],0])],
        conclusion=dict(line=len(lines),literal=goal,ast=['le',lo-1,'n']))
    if policy is not None:
        contract['distinct_premise_lines'] = policy
    translation = copy.deepcopy(contract)
    translation.pop('distinct_premise_lines', None)
    allowed = [n for n in range(-16,17) if n>=lo and n%modulus==0]
    assert allowed and all(n>=lo-1 for n in allowed)
    return raw, contract, translation


def main(reproduce):
    observed=reference(*fixture(1,2,True,True))['status']
    assert observed==HOLD
    if reproduce:
        print(json.dumps(dict(development=observed,expected=REJECT)))
        return
    from distinct_guard import route as candidate

    expected = [HOLD,REJECT,HOLD,HOLD,HOLD,HOLD]
    variants = [(False,True),(True,True),(True,None),(True,False),(False,None),(False,False)]
    cases=[]
    for lo,modulus in [(3,5),(-2,7)]:
        for i,(condensed,policy) in enumerate(variants):
            args=fixture(lo,modulus,condensed,policy)
            if i in (0,3):
                args[2]['premises'].reverse()
            cases.append((args,expected[i]))
    report={}
    for name,fn in [('reference',reference),('candidate',candidate)]:
        t=perf_counter()
        for _ in range(1000):
            got=[fn(*args) for args,_ in cases]
        elapsed=perf_counter()-t
        assert elapsed<30 and not any(r['universal_proof'] for r in got)
        report[name]=dict(seconds=elapsed,total=len(cases),
            correct=sum(r['status']==target for r,(_,target) in zip(got,cases)),
            false_passes=sum(r['status']==HOLD and target==REJECT for r,(_,target) in zip(got,cases)),
            false_rejects=sum(r['status']!=HOLD and target==HOLD for r,(_,target) in zip(got,cases)),
            abstentions=sum(r['status']=='ABSTAIN' for r in got),promotions=0)
    print(json.dumps(report,sort_keys=True))
    assert report['reference']['correct']==10 and report['candidate']['correct']==len(cases)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--reproduce',action='store_true')
    main(p.parse_args().reproduce)
