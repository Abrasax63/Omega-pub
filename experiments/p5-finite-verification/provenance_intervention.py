
"""One controlled provenance intervention on an observed public dossier."""
from dataclasses import dataclass, replace
from itertools import combinations, product
from pathlib import Path
import json


@dataclass(frozen=True)
class Claim:
    name: str
    group: str
    verdict: int


def structural_count():
    # With strict advantage, every first outcome must select a different
    # remaining coordinate. A constant branch would use only two coordinates.
    cube=tuple(product(range(2),repeat=3))
    signatures=set()
    for root in range(3):
        rest=tuple(k for k in range(3) if k!=root)
        for branch_order in (rest,rest[::-1]):
            for signs in product(range(2),repeat=2):
                signatures.add(tuple(w[branch_order[w[root]]]^signs[w[root]] for w in cube))
    return len(signatures)


def admissible(rows):
    return {
        truth:sorted({x.group for x in rows if x.verdict!=truth})
        for truth in (0,1)
        if len({x.group for x in rows if x.verdict!=truth})<=1
    }


def explain_affine(rows):
    # Binary specialization of the group core: each group supplies x=b.
    names={r.name:r for r in rows}
    for a,b in combinations(rows,2):
        if a.group==b.group or a.verdict==b.verdict:
            continue
        certificate={"lines":[a.name,b.name],"xor":[0,1],
                     "removal_witnesses":{a.group:b.verdict,b.group:a.verdict}}
        x,y=(names[k] for k in certificate["lines"])
        assert (1^1,x.verdict^y.verdict)==tuple(certificate["xor"])
        for removed,truth in certificate["removal_witnesses"].items():
            assert all(r.verdict==truth for r in (x,y) if r.group!=removed)
        return certificate
    return None


def inspect(rows):
    viable=admissible(rows)
    answer=next(iter(viable)) if len(viable)==1 else None
    core=explain_affine(rows)
    direct_conflict=next(([a.name,b.name] for a,b in combinations(rows,2)
                          if a.group!=b.group and a.verdict!=b.verdict),None)
    assert (core["lines"] if core else None)==direct_conflict
    assert viable==admissible(rows)
    return {"claims":[vars(r) for r in rows],"compatible_verdicts":viable,
            "certified_verdict":answer,"affine_conflict":core,
            "pairwise_baseline_conflict":direct_conflict}


def main():
    count=structural_count()
    # Values read from the pinned public console and JSON archive.
    observed={"workflow_log":24,"workflow_json":24}
    assert count==observed["workflow_log"]==observed["workflow_json"]
    clean=[
        Claim("workflow_log","run_43314308694",int(observed["workflow_log"]==24)),
        Claim("workflow_json","run_43314308694",int(observed["workflow_json"]==24)),
        Claim("structural_recount","combinatorial_recount",int(count==24)),
    ]
    corrupted=[replace(r,verdict=0) if r.group=="run_43314308694" else r for r in clean]
    def split_mirror(rows):
        return [replace(r,group="fake_independent_json") if r.name=="workflow_json" else r for r in rows]
    cases={
        "observed_correct_grouping":inspect(clean),
        "observed_split_mirror":inspect(split_mirror(clean)),
        "injected_error_correct_grouping":inspect(corrupted),
        "injected_error_split_mirror":inspect(split_mirror(corrupted)),
    }
    assert [x["certified_verdict"] for x in cases.values()]==[1,1,None,0]
    result={"claim":"exactly 24 rules have fixed cost 3 and adaptive cost 2",
            "observed":observed,"structural_count":count,
            "intervention":"In the two derivative views only, replace the count 24 by 23.",
            "sources":{"run":43314308694,"job":131518180401,"artifact":13987073340,
                       "producer_commit":"d4fddfab98e344941451d61f26534be498e67a04"},
            "cases":cases}
    Path("finite_provenance_intervention.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
