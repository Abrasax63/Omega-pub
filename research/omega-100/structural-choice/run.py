"""Verify exact outcomes and time deterministic and model policies separately."""
import argparse
import json
import statistics
import time
from collections import Counter
from pathlib import Path

from rule import choose
from solver import select, solve, truth, verify

POLICIES = ('A','B','rule','Qwen')


def dispatch(case, name):
    start = time.perf_counter()
    if name == 'Qwen':
        method, _, tokens = select(case)
    else:
        method = choose(case) if name == 'rule' else name
        tokens = {}
    decision = time.perf_counter()-start
    result = solve(case,method)
    return dict(result, method=method,tokens=tokens,decision_seconds=decision,
                total_seconds=time.perf_counter()-start)


def control():
    # An inconsistent parity pair and a numerically impossible subset sum.
    negatives=[dict(kind='parity', n=2, edges=[[0,1,0],[0,1,1]]),
               dict(kind='subset', values=[8,12,16],target=5)]
    for case in negatives:
        assert truth(case) is False
        for arm in POLICIES[:-1]:
            result=dispatch(case,arm)
            assert result['answer'] is False and verify(case,result,False)=='correct'


def timed_batch(cases, name):
    measurements=[]
    for _ in range(200):
        start=time.perf_counter_ns()
        for case in cases:
            dispatch(case,name)
        measurements.append(time.perf_counter_ns()-start)
    return statistics.median(measurements)/1e9


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('cases')
    parser.add_argument('--development',action='store_true')
    args=parser.parse_args()
    control()
    cases=json.loads(Path(args.cases).read_text())
    if not args.development:
        assert len(cases)==24
        assert Counter(c['kind'] for c in cases)=={'parity':12,'subset':12}
    labels=[truth(c) for c in cases]
    arms=POLICIES[:-1] if args.development else POLICIES
    output={}
    outcomes={}
    for arm in arms:
        runs=[dispatch(case,arm) for case in cases]
        statuses=[verify(c,r,y) for c,r,y in zip(cases,runs,labels,strict=True)]
        outcomes[arm]=statuses
        output[arm]={
            'outcomes': {s:statuses.count(s) for s in ('correct','error','abstain')},
            'correct_by_family': {f:sum(c['kind']==f and s=='correct' for c,s in zip(cases,statuses))
                                  for f in ('parity','subset')},
            'choices': dict(Counter(r['method'] for r in runs)),
            'selection_seconds': sum(r['decision_seconds'] for r in runs),
            'solve_seconds': sum(r['seconds'] for r in runs),
            'total_seconds': sum(r['total_seconds'] for r in runs),
            'solver_steps': sum(r['steps'] for r in runs),
            'input_tokens': sum(r['tokens'].get('prompt_tokens',0) for r in runs),
            'output_tokens': sum(r['tokens'].get('completion_tokens',0) for r in runs),
        }
        elapsed=output[arm]['total_seconds'] if arm=='Qwen' else timed_batch(cases,arm)
        correct=statuses.count('correct')
        output[arm]['comparison_seconds']=elapsed
        output[arm]['seconds_per_correct']=elapsed/correct if correct else None
        print(json.dumps(dict(arm=arm,**output[arm])),file=__import__('sys').stderr,flush=True)
    output['rule_vs_B'] = dict(
        gained=sum(a!='correct' and r=='correct' for a,r in zip(outcomes['B'],outcomes['rule'])),
        lost=sum(a=='correct' and r!='correct' for a,r in zip(outcomes['B'],outcomes['rule'])),
    )
    output['solver_ceiling'] = sum(a=='correct' or b=='correct' for a,b in zip(outcomes['A'],outcomes['B']))
    print(json.dumps(output,indent=2))


if __name__=='__main__':
    main()
