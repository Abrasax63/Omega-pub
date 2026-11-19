"""Audit strict typing for the optional premise line policy."""
import argparse
import json
from time import perf_counter
from probe034 import fixture, HOLD, REJECT
from distinct_guard import route as incumbent


def development():
    for policy,wanted in [(1,HOLD),(True,REJECT),(False,HOLD),(0,HOLD)]:
        assert incumbent(*fixture(1,2,True,policy))['status']==wanted
    return dict(reference_numeric=HOLD,expected_numeric=REJECT)


def cases():
    field='distinct_premise_lines'
    for i,(lo,modulus) in enumerate([(2,3),(-5,8)]):
        for condensed in (False,True):
            for j,policy in enumerate([0,1,None,[],{},'true','false',0.0,True,False]):
                args=fixture(lo,modulus,condensed,None)
                args[1][field]=policy
                expected = REJECT if type(policy) is not bool or (policy and condensed) else HOLD
                yield f'{i}-{int(condensed)}-{j}',args,expected
            args=fixture(lo,modulus,condensed,None)
            args[2][field]=1
            yield f'{i}-{int(condensed)}-absent',args,HOLD


def audit():
    from policy_guard import route as candidate
    reserve=list(cases())
    report={}
    for name,route in [('reference',incumbent),('candidate',candidate)]:
        start=perf_counter()
        for _ in range(1000):
            results=[route(*args) for _,args,_ in reserve]
        elapsed=perf_counter()-start
        assert elapsed<30
        got=[item['status'] for item in results]
        expected=[target for _,_,target in reserve]
        report[name]=dict(n=len(reserve),correct=sum(a==b for a,b in zip(got,expected)),
            false_passes=sum(a==HOLD and b==REJECT for a,b in zip(got,expected)),
            false_rejects=sum(a!=HOLD and b==HOLD for a,b in zip(got,expected)),
            abstentions=got.count('ABSTAIN'),promotions=sum(r['universal_proof'] for r in results),seconds=elapsed)
    assert report['reference']['false_passes']==32
    assert report['candidate']['correct']==len(reserve)
    assert not any(r['promotions'] for r in report.values())
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reproduce',action='store_true')
    print(json.dumps(development() if parser.parse_args().reproduce else audit(),sort_keys=True))
