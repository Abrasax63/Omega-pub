"""Audit a budget-shared direct probe followed by a graph fallback."""
from collections import Counter
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import json
import sys

from candidate import solve_budgeted
from rule import choose
from solver import solve, truth, verify


def fixed_a(case):
    return solve(case,'A')


def reference(case):
    return solve(case,choose(case))


def control():
    # Contradiction seen early by B even though the graph is dense.
    edges = [(0,1,0),(0,1,1)] + [(i,j,0) for i in range(1,8) for j in range(i+1,8)]
    case = dict(kind='parity',n=8,edges=edges)
    assert not truth(case)
    for method in (reference,solve_budgeted):
        result = method(case)
        assert result['steps']<=64 and verify(case,result,False)!='error'
    assert reference(case)['answer'] is False


def audit(entries):
    control()
    cases = [entry['case'] for entry in entries]
    labels = [truth(case) for case in cases]
    names = ('reference','A','candidate')
    methods = dict(zip(names,(reference,fixed_a,solve_budgeted)))
    produced = {name:[method(case) for case in cases] for name,method in methods.items()}
    elapsed={name:[] for name in names}
    for repeat in range(300):
        for name in names[repeat%3:]+names[:repeat%3]:
            t = perf_counter_ns()
            for case in cases:
                methods[name](case)
            elapsed[name].append(perf_counter_ns()-t)
    stats={}
    outcomes={}
    for name, rows in produced.items():
        assert all(r['steps']<=64 for r in rows)
        outcomes[name]=[verify(c,r,y) for c,r,y in zip(cases,rows,labels,strict=True)]
        counts=Counter(outcomes[name])
        stats[name]=dict(**{s:counts[s] for s in ('correct','abstain','error')},
                         steps=sum(r['steps'] for r in rows),
                         median_batch_ns=median(elapsed[name]),
                         median_ns_per_correct=median(elapsed[name])/counts['correct'] if counts['correct'] else None)
    paired=Counter()
    groups={}
    for entry,ref,new,row in zip(entries,outcomes['reference'],outcomes['candidate'],produced['candidate'],strict=True):
        outcome = 'gained' if ref!='correct' and new=='correct' else 'lost' if ref=='correct' and new!='correct' else 'same'
        paired[outcome]+=1
        grp=groups.setdefault(entry['group'],Counter())
        grp['cases']+=1
        grp['reference_correct']+=ref=='correct'
        grp['candidate_correct']+=new=='correct'
        grp[outcome]+=1
        grp['probe_steps']+=row['probe_steps']
    return dict(n=len(entries),policies=stats,paired=dict(paired),groups={k:dict(v) for k,v in groups.items()},
                phases=dict(Counter(r['phase'] for r in produced['candidate'])),
                total_probe_steps=sum(r['probe_steps'] for r in produced['candidate']),
                threshold_passed=paired['gained']>=2 and paired['lost']==0 and stats['candidate']['error']==0)


if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text())),indent=2))
