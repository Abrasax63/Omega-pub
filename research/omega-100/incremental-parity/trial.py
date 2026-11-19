"""Compare budgeted parity solvers against an independent exact oracle."""
from collections import Counter
from itertools import combinations
from pathlib import Path
from statistics import median
from time import perf_counter_ns
import json
import sys

from incremental import route, upper_bound
from rule import choose
from solver import solve, truth, verify


def reference(case):
    return solve(case,choose(case))


def unguarded(case):
    return route(case,guarded=False)


def controls():
    historic = dict(kind='parity',n=10,
        edges=[(a,b,0) for a,b in combinations(range(2,10),2)][:24]+[(2,3,1)])
    stress = dict(kind='parity',n=12,edges=[(0,1,0)]
        +[(a,b,0) for a,b in combinations(range(2,12),2)]*1
        +[(2,i,0) for i in range(3,12)]+[(0,1,1)])
    bad = dict(kind='parity',n=3,edges=[(1,0,1),(0,1,0)])
    good = dict(kind='parity',n=4,edges=[(2,1,1),(0,3,1),(1,0,0),(3,2,0)])
    output = {}
    for name,case,wanted in [('historic',historic,False),('stress',stress,False),
                             ('small_contradiction',bad,False),('small_coherent',good,True)]:
        assert truth(case) is wanted
        record = {}
        for arm,runner in [('reference',reference),('raw',unguarded),('guarded',route)]:
            run = runner(case)
            record[arm] = dict(status=verify(case,run,wanted),steps=run['steps'],
                read_edges=run.get('read_edges'),source=run.get('source','reference'))
            assert run['steps']<=64
        assert record['guarded']['status'] == 'correct'
        output[name] = dict(edges=len(case['edges']),bound=upper_bound(case['n'],len(case['edges'])),**record)
    assert output['stress']['raw']['status']=='abstain'
    return output


def audit(entries):
    diagnostics = controls()
    cases = [row['case'] for row in entries]
    labels = [truth(case) for case in cases]
    arms = ('reference','raw','guarded')
    methods = dict(zip(arms,(reference,unguarded,route)))
    results = {name:[fn(case) for case in cases] for name,fn in methods.items()}
    assert all(r['steps']<=64 for batch in results.values() for r in batch)
    times = {name:[] for name in arms}
    for i in range(300):
        for name in arms[i%3:]+arms[:i%3]:
            start=perf_counter_ns()
            for case in cases:
                methods[name](case)
            times[name].append(perf_counter_ns()-start)
    status = {name:[verify(c,r,label) for c,r,label in zip(cases,batch,labels,strict=True)]
              for name,batch in results.items()}
    report = {}
    for name,batch in results.items():
        counts = Counter(status[name])
        report[name] = dict(**{q:counts[q] for q in ('correct','error','abstain')},
            work=sum(row['steps'] for row in batch),
            paths=dict(Counter(row.get('source','reference') for row in batch)),
            median_ns=median(times[name]),
            gains=sum(a!='correct' and b=='correct' for a,b in zip(status['reference'],status[name])),
            losses=sum(a=='correct' and b!='correct' for a,b in zip(status['reference'],status[name])))
    by_type = {group:dict(cases=sum(x['group']==group for x in entries),
                **{arm:sum(row['group']==group and s=='correct'
                           for row,s in zip(entries,status[arm])) for arm in arms})
               for group in sorted({item['group'] for item in entries})}
    selected=report['guarded']
    return dict(controls=diagnostics,cases=len(cases),policies=report,by_type=by_type,
        threshold_passed=selected['gains']>=2 and selected['losses']==0 and selected['error']==0)


if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text())),indent=2))
