"""Test identity typing, uniqueness and permutation at the 032 boundary."""
import argparse
import copy
import hashlib
import json
from time import perf_counter

from line_guard import route as incumbent

ACCEPT = 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN'
REJECT = 'REJECTED_SOURCE_AST_BINDING'


def fixture(limit, mod, ids):
    lines = [f'n est au moins {limit}',f'n est un multiple de {mod}',f'n est au moins {limit-1}']
    raw = ('\n'.join(lines)+'\n').encode()
    premises = [
        dict(id=ids[0],line=1,literal=lines[0],ast=['le',limit,'n']),
        dict(id=ids[1],line=2,literal=lines[1],ast=['eq',['mod','n',mod],0]),
    ]
    contract = dict(source_sha256=hashlib.sha256(raw).hexdigest(), premises=premises,
        conclusion=dict(line=3,literal=lines[2],ast=['le',limit-1,'n']))
    allowed = [n for n in range(-16,17) if n>=limit and n%mod==0]
    assert allowed and all(n>=limit-1 for n in allowed)
    return raw, contract, copy.deepcopy(contract)


def oracle(contract, translation):
    def keys(collection):
        ids = [row['id'] for row in collection]
        if any(type(item) not in (int,str) for item in ids):
            return None
        typed = {(type(item),item) for item in ids}
        return typed if len(typed)==len(ids) else None
    expected, actual = keys(contract['premises']), keys(translation['premises'])
    return ACCEPT if expected is not None and expected==actual else REJECT


def set_id(obj, value):
    obj['premises'][0]['id'] = value


def reserved():
    cases = []
    for i,(limit,mod,ids) in enumerate([(-3,7,(1,4)),(4,3,(1,'P2'))]):
        args = fixture(limit,mod,ids)
        cases.append((f'valid-{i}',args))
        permuted = copy.deepcopy(args)
        permuted[2]['premises'].reverse()
        cases.append((f'permuted-{i}',permuted))
        for label,value in [('bool',True),('float',1.0),('duplicate',ids[1]),('list',[1]),('text','1')]:
            bad = copy.deepcopy(args)
            set_id(bad[2],value)
            cases.append((f'{label}-{i}',bad))
        missing = copy.deepcopy(args)
        missing[2]['premises'].pop()
        cases.append((f'missing-{i}',missing))
        bad_contract = copy.deepcopy(args)
        set_id(bad_contract[1],1.0)
        cases.append((f'contract-{i}',bad_contract))
    return cases


def main(reproduce):
    raw, contract, translation = fixture(0,5,(1,'P2'))
    set_id(translation,True)
    got=incumbent(raw,contract,translation)['status']
    assert oracle(contract,translation)==REJECT and got==ACCEPT
    set_id(translation,'P2')
    assert incumbent(raw,contract,translation)['status']==REJECT
    if reproduce:
        print(json.dumps(dict(boolean_reference=got,expected=REJECT,duplicate='rejected')))
        return
    from premise_guard import route as candidate
    cases = reserved()
    labels = [oracle(c,t) for _,(_,c,t) in cases]
    report = {}
    for label,fn in [('reference',incumbent),('candidate',candidate)]:
        start=perf_counter()
        for _ in range(1000):
            result = [fn(*args) for _,args in cases]
        elapsed=perf_counter()-start
        assert elapsed<30 and not any(item['universal_proof'] for item in result)
        observed=[item['status'] for item in result]
        report[label]=dict(seconds=elapsed,total=len(labels),correct=sum(a==b for a,b in zip(observed,labels)),
            false_pass=sum(a==ACCEPT and b==REJECT for a,b in zip(observed,labels)),
            false_reject=sum(a!=ACCEPT and b==ACCEPT for a,b in zip(observed,labels)),
            abstentions=observed.count('ABSTAIN'),promotions=0,
            rows=[dict(case=name,expected=target,observed=actual)
                  for (name,_),target,actual in zip(cases,labels,observed)])
    print(json.dumps(report,sort_keys=True))
    assert report['reference']['false_pass']==6
    assert report['candidate']['correct']==len(labels)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--reproduce',action='store_true')
    main(parser.parse_args().reproduce)
