"""Independent auditor of the frozen provenance-oracle report.

Uses a distinct exhaustive recursion; never imports the experimental solver.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random

EXPECTED_ID = "OMEGA-PROVENANCE-ORACLE-06"
PREREG = "ce03dc1af00af9521a3ca7ddc80993d2718d5091"
QUESTIONS = [(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
POLICIES = ("EXACT_VERDICT_ORACLE","CHEAP_FIRST",
            "PARTITION_SPLIT_PER_COST","DECISION_GAIN_PER_COST")


def digest(v):
    return sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()


def truth(world):
    return len(set(world)) >= 3


def independent_minimum(worlds, questions, prices):
    outputs = tuple(tuple(int(world[i]==world[j]) for i,j in questions)
                    for world in worlds)
    labels = tuple(truth(world) for world in worlds)
    @lru_cache(None)
    def brute(indices):
        if len({labels[i] for i in indices}) == 1:
            return 0
        valid = []
        for j,cost in enumerate(prices):
            zero = tuple(i for i in indices if outputs[i][j] == 0)
            one = tuple(i for i in indices if outputs[i][j] == 1)
            if zero and one:
                valid.append(len(indices)*cost+brute(zero)+brute(one))
        if not valid:
            raise ValueError("UNRESOLVED_CLASSIFICATION")
        return min(valid)
    return brute(tuple(range(len(worlds))))


def audit(report):
    assert report["experiment"] == EXPECTED_ID
    assert report["preregistered_commit"] == PREREG
    assert report["mode"] in ("calibration", "holdout")
    ids = list(range(12)) if report["mode"] == "calibration" else list(range(100,124))
    assert report["case_ids"] == ids
    assert report["questions"] == [list(q) for q in QUESTIONS]
    assert report["policies"] == list(POLICIES)
    assert report["no_paid_api"] and not report["main_modified"]
    assert not report["trained_policies"]
    assert not report["actual_github_provenance_verified"]
    assert not report["generalization_proven"]
    worlds = [tuple(p) for p in report["partitions"]]
    assert len(worlds)==15 and len(set(worlds))==15
    assert sum(truth(row) for row in worlds)==7
    assert sum(not truth(row) for row in worlds)==8
    assert report["partition_sha256"]==digest(worlds)
    assert len(report["trials"])==len(ids)
    costs_in_order = []
    for item,ident in zip(report["trials"],ids):
        assert item["index"]==ident
        rng=random.Random(58301+ident)
        cost=[rng.randint(1,12) for _ in QUESTIONS]
        assert item["pair_costs"]==cost
        costs_in_order.append(cost)
        assert item["partitions_sha256"]==digest(worlds)
        assert item["states_evaluated"]>0
        expected_opt=independent_minimum(worlds,QUESTIONS,cost)
        assert expected_opt==item["optimal_cost_numerator"]
        score=item["cost_sums_all_15_partitions"]
        depths=item["max_probe_depth"]
        assert set(score)==set(POLICIES)
        assert set(depths)==set(POLICIES)
        assert score["EXACT_VERDICT_ORACLE"]==expected_opt
        for policy in POLICIES:
            paths=item["paths"][policy]
            assert len(paths)==15
            assert {p["hidden_index"] for p in paths}==set(range(15))
            sum_cost=0
            max_depth=0
            decisions={}
            for path in paths:
                h=path["hidden_index"]
                assert path["status"]=="CERTIFIED"
                assert path["actual_distinct_origins"]==len(set(worlds[h]))
                assert path["verdict_at_least_three_origins"]==truth(worlds[h])
                mask=set(range(15))
                examined=set()
                for step in path["log"]:
                    q=tuple(step["question"])
                    assert q in QUESTIONS and q not in examined
                    examined.add(q)
                    idx=QUESTIONS.index(q)
                    assert step["price_paid"]==cost[idx]
                    assert step["belief_before"]==sorted(mask)
                    actual=int(worlds[h][q[0]]==worlds[h][q[1]])
                    assert step["answer_same_origin"]==actual
                    new={i for i in mask if int(worlds[i][q[0]]==worlds[i][q[1]])==actual}
                    assert 0<len(new)<len(mask)
                    assert step["belief_after"]==sorted(new)
                    state=frozenset(mask)
                    assert state not in decisions or decisions[state]==q
                    decisions[state]=q
                    mask=new
                assert len({truth(worlds[i]) for i in mask})==1
                assert truth(worlds[h])==truth(worlds[min(mask)])
                assert path["remaining_hypotheses"]==sorted(mask)
                assert path["queries_paid"]==len(path["log"])<=6
                actual_cost=sum(step["price_paid"] for step in path["log"])
                assert path["total_price"]==actual_cost
                sum_cost+=actual_cost
                max_depth=max(max_depth,len(path["log"]))
            assert sum_cost==score[policy]
            assert max_depth==depths[policy]
            assert abs(item["uniform_expected_cost"][policy]-score[policy]/15)<1e-10
        assert tuple(item["paths"]["EXACT_VERDICT_ORACLE"][0]["log"][0]["question"])==tuple(item["optimal_first_question"])
        assert all(score["EXACT_VERDICT_ORACLE"]<=score[p] for p in POLICIES)
    assert report["benchmark_identity"]==digest({
        "partitions": worlds,"questions": QUESTIONS,
        "case_ids": ids,"costs": costs_in_order})

    totals = report["summary"]
    assert totals["cases"]==len(ids)
    assert totals["worlds_per_case"]==15
    assert totals["max_probes_across_all_trajectories"]<=6
    assert totals["total_bellman_states"]==sum(r["states_evaluated"] for r in report["trials"])
    for policy in POLICIES:
        actual=sum(t["cost_sums_all_15_partitions"][policy] for t in report["trials"])/(15*len(ids))
        assert abs(totals["cost_mean_uniform"][policy]-actual)<1e-10
    bests = [min(row["cost_sums_all_15_partitions"][p] for p in POLICIES
                 if p!="EXACT_VERDICT_ORACLE") for row in report["trials"]]
    optimum = [row["optimal_cost_numerator"] for row in report["trials"]]
    deltas=[best-opt for best,opt in zip(bests,optimum)]
    count=sum(gap*10>=opt for gap,opt in zip(deltas,optimum))
    strict=sum(gap*10>opt for gap,opt in zip(deltas,optimum))
    assert totals["headroom_at_least_10pct"]==count
    assert totals["headroom_strictly_over_10pct"]==strict
    assert abs(totals["best_baseline_mean_uniform"]-sum(bests)/(15*len(ids)))<1e-10
    assert abs(totals["mean_headroom_to_best_baseline"]-sum(deltas)/(15*len(ids)))<1e-10
    assert abs(totals["max_headroom_to_best_baseline"]-max(deltas)/15)<1e-10
    expected=("MEASURABLE_PROVENANCE_HEADROOM" if count>=6 else
              "NEAR_BEST_BASELINE_IN_THIS_SYNTHETIC_BENCHMARK" if strict==0 else
              "MIXED_HEADROOM")
    assert report["status"]==expected
    return {
        "mode":report["mode"], "status":expected,
        "cases":len(ids), "full_paths":15*len(ids)*4,
        "mean_optimum":totals["cost_mean_uniform"]["EXACT_VERDICT_ORACLE"],
        "mean_best_baseline":totals["best_baseline_mean_uniform"],
        "cases_at_least_10pct":count,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("report",type=Path)
    args=parser.parse_args()
    raw=args.report.read_bytes()
    result=audit(json.loads(raw))
    print("RAW_REPORT_SHA256",sha256(raw).hexdigest())
    print("INDEPENDENT_BRUTE_FORCE_AUDIT",json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
