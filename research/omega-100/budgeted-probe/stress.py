"""Falsify non-regression when rejected masks consume the fallback budget."""
import json
from itertools import combinations

from candidate import solve_budgeted
from probe_trial import reference
from solver import truth, verify


def audit():
    edges = [(a,b,0) for a,b in combinations(range(2,10),2)][:24]
    edges.append((2,3,1))
    case = dict(kind='parity', n=10,edges=edges)
    assert not truth(case)
    output={}
    for name,method in [('reference',reference),('candidate',solve_budgeted)]:
        result=method(case)
        output[name]=dict(status=verify(case,result,False),steps=result['steps'],
                          probe_steps=result.get('probe_steps',0))
    assert output['reference']['status']=='correct'
    assert output['candidate']['status']=='abstain'
    return dict(vertices=case['n'],edges=len(edges),**output)


if __name__=='__main__':
    print(json.dumps(audit(),indent=2))
