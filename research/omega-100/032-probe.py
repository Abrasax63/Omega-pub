"""Reproduce line types that bypass the source/AST binding at the route boundary."""
import argparse
import copy
import hashlib
import json
from time import perf_counter

from route import route as reference

REJECT = 'REJECTED_SOURCE_AST_BINDING'
HOLDS = 'NO_COUNTEREXAMPLE_WITHIN_DOMAIN'


def fixture(first, goal, premise_ast, goal_ast):
    raw = f'{first}\n{goal}\n'.encode()
    contract = dict(source_sha256=hashlib.sha256(raw).hexdigest(),
        premises=[dict(id='P1',line=1,literal=first,ast=premise_ast)],
        conclusion=dict(line=2,literal=goal,ast=goal_ast))
    return raw, contract, copy.deepcopy(contract)


def development():
    args = fixture('n vaut 3','n est au plus 5',['eq','n',3],['le','n',5])
    assert reference(*args)['status'] == HOLDS
    args[2]['premises'][0]['line'] = True
    got = reference(*args)['status']
    print(json.dumps({'development_bool_expected':REJECT,'observed':got}))
    assert got == HOLDS


def reserved():
    specs = [
        ('n est au moins 8','n est au moins 6',['le',8,'n'],['le',6,'n'],lambda n:n>=8,lambda n:n>=6),
        ('n est au plus -4','n est au plus 0',['le','n',-4],['le','n',0],lambda n:n<=-4,lambda n:n<=0),
    ]
    cases=[]
    for index,(first,goal,ast,end,pred,claim) in enumerate(specs):
        assert any(pred(n) for n in range(-16,17))
        assert all(not pred(n) or claim(n) for n in range(-16,17))
        args=fixture(first,goal,ast,end)
        cases.append((f'valid-{index}',args,HOLDS))
        for name, value, field in [('bool',True,'premises'),('float',2.0,'conclusion'),('wrong',3,'premises')]:
            raw, contract, translation = copy.deepcopy(args)
            entry = translation[field][0] if field=='premises' else translation[field]
            entry['line'] = value
            assert type(value) is not int or value != 1
            cases.append((f'{name}-{index}',(raw,contract,translation),REJECT))
        raw, contract, translation = copy.deepcopy(args)
        translation['premises']=[]
        cases.append((f'empty-{index}',(raw,contract,translation),REJECT))
        raw, contract, translation = copy.deepcopy(args)
        deep='n'
        for _ in range(32):
            deep=['square',deep]
        translation['conclusion']['ast']=['le',deep,1]
        contract['conclusion']['ast']=copy.deepcopy(translation['conclusion']['ast'])
        cases.append((f'deep-{index}',(raw,contract,translation),'ABSTAIN'))
    return cases


def audit():
    from line_guard import route as candidate

    cases=reserved()
    report={}
    for name,fn in [('reference',reference),('candidate',candidate)]:
        t=perf_counter()
        for _ in range(1000):
            got=[fn(*args) for _,args,_ in cases]
        elapsed=perf_counter()-t
        assert elapsed<30
        report[name]=dict(correct=sum(r['status']==expected for r,(_,_,expected) in zip(got,cases)),
            cases=len(cases),seconds=elapsed,
            abstentions=sum(r['status']=='ABSTAIN' for r in got),
            rejected=sum(r['status']==REJECT for r in got),
            promotions=sum(r['universal_proof'] for r in got),
            cases_by_status={label:dict(got=r['status'],expected=expected,source_sha256=hashlib.sha256(args[0]).hexdigest())
                             for r,(label,args,expected) in zip(got,cases)})
    print(json.dumps(report,sort_keys=True))
    assert report['reference']['correct']==8
    assert report['candidate']['correct']==len(cases)
    assert not any(r['promotions'] for r in report.values())


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--reproduce',action='store_true')
    development() if p.parse_args().reproduce else audit()
