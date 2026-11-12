
"""Exact verification when one provenance group can be systematically wrong."""
from functools import cache
from itertools import combinations
from math import inf
from pathlib import Path
import json

from benchmark import CUBE, CHECKS, SELECTOR, Check, solve
from bounded_search import verify_plan


def build(checks, provenance, source_costs):
    return tuple((f"{check.name}_{label}",group,index,check.cost*source_costs[group])
                 for label,group in provenance
                 for index,check in enumerate(checks))


def expanded_worlds(verdicts, checks, probes):
    groups=sorted({group for _,group,_,_ in probes})
    # An arbitrary subset of control values may be flipped by the faulty group.
    faults=[(-1,0)]+[(g,m) for g in groups for m in range(1,1<<len(checks))]
    worlds=[(i,g,m) for i in range(len(verdicts)) for g,m in faults]
    observations=tuple(Check(name,cost,tuple(
        checks[k].values[i]^int(g==group and bool(mask&(1<<k))) for i,g,mask in worlds
    )) for name,group,k,cost in probes)
    return tuple(verdicts[i] for i,_,_ in worlds),observations


def fixed_oracle(verdicts,checks,probes):
    # Radius-one corruption in provenance blocks requires three differing blocks.
    opposing=[(a,b) for a,b in combinations(range(len(verdicts)),2) if verdicts[a]!=verdicts[b]]
    groups=sorted({g for _,g,_,_ in probes})
    if opposing and len(groups)<3:
        return inf
    return min(
        (sum(p[3] for p in subset)
         for k in range(len(probes)+1) for subset in combinations(probes,k)
         if all(len({g for _,g,t,_ in subset if checks[t].values[a]!=checks[t].values[b]})>=3
                for a,b in opposing)),default=inf)


def game_oracle(verdicts,checks,probes):
    groups=sorted({g for _,g,_,_ in probes})
    # For each original world, track which group could explain all mismatches.
    initial=((1<<len(groups))-1,)*len(verdicts)
    group_bits={g:1<<i for i,g in enumerate(groups)}
    @cache
    def value(candidates,remaining):
        if len({verdicts[i] for i,m in enumerate(candidates) if m})<=1:
            return 0
        best=inf
        for j in range(len(probes)):
            if not remaining&(1<<j):
                continue
            _,g,k,cost=probes[j]
            bit=group_bits[g]
            branches=[]
            for y in (0,1):
                new=tuple(m if checks[k].values[i]==y else m&bit for i,m in enumerate(candidates))
                if any(new):
                    branches.append(value(new,remaining^(1<<j)))
            best=min(best,cost+max(branches))
        return best
    # Mirrors read an identical value. Keep one representative before playing.
    unique={}
    for probe in probes:
        key=probe[1:3]
        if key not in unique or probe[3]<unique[key][3]:
            unique[key]=probe
    probes=tuple(unique.values())
    out=value(initial,(1<<len(probes))-1)
    return out,value.cache_info().currsize


def evaluate(verdicts,checks,probes):
    labels,obs=expanded_worlds(verdicts,checks,probes)
    optimum=solve(labels,obs)
    fixed=fixed_oracle(verdicts,checks,probes)
    adaptive,states=game_oracle(verdicts,checks,probes)
    assert optimum["fixed"]==(fixed if fixed<inf else None)
    assert optimum["adaptive"]==(adaptive if adaptive<inf else None)
    if optimum["tree"]:
        assert verify_plan(optimum["tree"],labels,obs)==adaptive
    else:
        assert any(labels[a]!=labels[b] and all(c.values[a]==c.values[b] for c in obs)
                   for a,b in combinations(range(len(labels)),2))
    return {**optimum,"expanded_worlds":len(labels),"game_states":states}


def main():
    independent=(("A",0),("B",1),("C",2))
    two=(("A",0),("B",1))
    mirrored=(("A",0),("B",0),("C",1))
    source_costs=(1,1,1)
    complete=build(CHECKS,independent,source_costs)
    missing=tuple(p for p in complete if p[1:3]!=(2,0))
    parity=tuple(sum(w)%2 for w in CUBE)
    cases={
        "selector_three_groups":evaluate(SELECTOR,CHECKS,complete),
        "selector_three_groups_weighted":evaluate(SELECTOR,CHECKS,build(CHECKS,independent,(1,2,3))),
        "parity_three_groups":evaluate(parity,CHECKS,complete),
        "selector_two_groups":evaluate(SELECTOR,CHECKS,build(CHECKS,two,source_costs)),
        "selector_two_groups_three_labels":evaluate(SELECTOR,CHECKS,build(CHECKS,mirrored,source_costs)),
        "selector_third_group_missing_note":evaluate(SELECTOR,CHECKS,missing),
    }
    assert cases["selector_three_groups"]["fixed"]==9
    assert all(cases[k]["adaptive"] is None for k in ("selector_two_groups","selector_two_groups_three_labels","selector_third_group_missing_note"))
    report={"faulty_provenance_groups":1,"cases":cases}
    Path("finite_source_fault_results.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({k:{a:b for a,b in v.items() if a!="tree"} for k,v in cases.items()},indent=2))


if __name__=="__main__":
    main()
