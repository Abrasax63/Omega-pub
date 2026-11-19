"""Compare ordinary and duplicate-rejecting JSON decoding before guard 035."""
import argparse
import json
from time import perf_counter
from policy_guard import route as incumbent
from probe034 import fixture, HOLD, REJECT

BAD = 'REJECTED_INVALID_JSON'
DUP = 'REJECTED_DUPLICATE_JSON_KEY'


def failure(status):
    return dict(status=status, universal_proof=False)


def reference(raw, contract, translation):
    try:
        decoded = json.loads(contract),json.loads(translation)
    except (ValueError, TypeError, RecursionError):
        return failure(BAD)
    return incumbent(raw,*decoded)


def envelope(lo,modulus,policy=False):
    raw, contract, translation = fixture(lo,modulus,False,policy)
    return raw, json.dumps(contract), json.dumps(translation)


def duplicate(text, original, first, second):
    assert text.count(original)==1
    return text.replace(original, first + ', ' + second, 1)


def development():
    raw,c,t = envelope(1,2)
    c = duplicate(c,'"distinct_premise_lines": false',
                  '"distinct_premise_lines": true','"distinct_premise_lines": false')
    status = reference(raw,c,t)['status']
    assert status == HOLD
    return dict(reference=status,expected=DUP)


def reserve():
    field = '"distinct_premise_lines": false'
    for lo,modulus in [(5,3),(-6,5)]:
        raw,c,t = envelope(lo,modulus)
        for mutant in [
            duplicate(c,field,field,field),
            duplicate(c,field,'"distinct_premise_lines": true',field),
            duplicate(c,field,r'"distinct_premise_lin\u0065s": 0',field),
            duplicate(c,'"id": "A"','"id": null','"id": "A"'),
        ]:
            yield (raw,mutant,t),DUP
        for mutant in [
            duplicate(t,'"line": 1','"line": true','"line": 1'),
            duplicate(t,'"line": 1',r'"lin\u0065": -1','"line": 1'),
            duplicate(t,'"id": "B"','"id": "B"','"id": "B"'),
            t[:-1]+', "meta": [{"revision": 1, "revision": 2}]}',
        ]:
            yield (raw,c,mutant),DUP
        yield (raw,c,t),HOLD
        yield (raw,c,t[:-1]+', "meta": [{"revision": 1},{"revision":2}]}'),HOLD
        yield (raw,c,t[:-1]+', "é": 1,"e\u0301":2}'),HOLD
        yield (raw,c,t[:-1]),BAD
        yield (raw,c.replace(field,'"distinct_premise_lines": 1'),t),REJECT


def audit():
    from wire_guard import route as candidate
    assert development()['reference']==HOLD
    data=list(reserve())
    report={}
    for label,fn in [('reference',reference),('candidate',candidate)]:
        start=perf_counter()
        for _ in range(500):
            outputs=[fn(*args) for args,_ in data]
        elapsed=perf_counter()-start
        actual=[r['status'] for r in outputs]
        expected=[s for _,s in data]
        assert elapsed<30 and not any(r['universal_proof'] for r in outputs)
        report[label]=dict(total=len(data),correct=sum(a==b for a,b in zip(actual,expected)),
            duplicates_that_pass=sum(a==HOLD and b==DUP for a,b in zip(actual,expected)),
            false_rejects=sum(a!=HOLD and b==HOLD for a,b in zip(actual,expected)),
            abstentions=actual.count('ABSTAIN'),promotions=0,seconds=elapsed)
    assert report['reference']['duplicates_that_pass']==16
    assert report['candidate']['correct']==len(data)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reproduce',action='store_true')
    print(json.dumps(development() if parser.parse_args().reproduce else audit(),sort_keys=True))
