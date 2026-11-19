"""Charge structural inspections against the same cap in a sensitivity analysis."""
import json
import sys
from pathlib import Path

import solver
from rule import choose


def inspections(case):
    if case['kind']=='parity':
        return next((i for i,edge in enumerate(case['edges'],1) if edge[2]),len(case['edges']))
    return next((i for i,v in enumerate(case['values'],1) if v==case['target']),len(case['values']))


def audit(cases):
    total=solver.CAP
    report=dict(cases=len(cases),correct=0,errors=0,abstentions=0,gained_vs_B=0,lost_vs_B=0,
                inspections=0)
    for case in cases:
        label=solver.truth(case)
        fixed=solver.verify(case,solver.solve(case,'B'),label)
        charge=inspections(case)
        report['inspections']+=charge
        assert 0<=charge<=total
        try:
            solver.CAP=total-charge
            result=solver.solve(case,choose(case))
        finally:
            solver.CAP=total
        assert charge+result['steps']<=total
        got=solver.verify(case,result,label)
        report[{'correct':'correct','error':'errors','abstain':'abstentions'}[got]]+=1
        report['gained_vs_B']+=got=='correct' and fixed!='correct'
        report['lost_vs_B']+=got!='correct' and fixed=='correct'
    return report


if __name__=='__main__':
    print(json.dumps(audit(json.loads(Path(sys.argv[1]).read_text())),indent=2))
