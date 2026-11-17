"""Bounded active disagreement: each new paid output refines the hypothesis set."""
from __future__ import annotations
import argparse
from collections import deque
from hashlib import sha256
from itertools import product
from pathlib import Path
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-state-split-01"))
import state_split as s

EXPERIMENT="OMEGA-STATE-SPLIT-ACTIVE-02"
PREREG="a70c231753a2112dc0bc0501dd742b5aff4072ce"
SAMPLE_SEED=53117
TEST_N=24
BASE=(((0,0),), ((0,0),))


def distinguishable(model):
    """Exact pair-product BFS, used solely for structural filtering."""
    transitions,outputs=model
    n=len(transitions)
    for left in range(n):
        for right in range(left+1,n):
            queue=deque([(left,right)])
            seen={(left,right)}
            found=False
            while queue and not found:
                u,v=queue.popleft()
                for symbol in s.ALPHABET:
                    if outputs[u][symbol]!=outputs[v][symbol]:
                        found=True
                        break
                    pair=(transitions[u][symbol],transitions[v][symbol])
                    if pair not in seen:
                        seen.add(pair)
                        queue.append(pair)
            if not found:
                return False
    return True


def new_cohort(models):
    """Freeze machine selection independent of any policy outcomes."""
    historical={s.canonical(s.delayed_marker(p))
                for p in product(s.ALPHABET,repeat=3)}
    eligible=[model for model in models
              if len(model[0])==3 and distinguishable(model)
              and model not in historical]
    if len(eligible)<TEST_N:
        raise AssertionError("NOT_ENOUGH_STRUCTURAL_TEST_MACHINES")
    worlds=random.Random(SAMPLE_SEED).sample(eligible,TEST_N)
    if len(set(worlds))!=TEST_N or any(x in historical for x in worlds):
        raise AssertionError("PR143_SOURCE_LEAK")
    return worlds,len(eligible)


def paid_query(hidden,word):
    """Simulator-only query; the selector itself never receives hidden."""
    return s.trace(hidden,word)


def run_policy(arm,hidden,observations,space,static_schedule):
    known=[{"inputs":list(row["inputs"]),"outputs":list(row["outputs"])}
           for row in observations]
    remaining=space[:]
    query_log=[]
    if arm=="FIXED_PREFIX":
        schedule=s.seed_words()
    elif arm=="STATIC_DIVERSITY":
        schedule=static_schedule
    else:
        assert arm=="ACTIVE_DISAGREEMENT"
        schedule=None
    limit=8 if arm=="FIXED_PREFIX" else 32
    status="BUDGET_EXHAUSTED_WITHOUT_DISCRIMINATION"
    for attempt in range(limit):
        if arm=="ACTIVE_DISAGREEMENT":
            representative,_=s.diversify(remaining)
            ranked,details=s.rank_queries(representative,known)
            if not ranked:
                status="NO_IDENTIFIABLE_DISAGREEMENT"
                break
            word=ranked[0]
            classes=details[0]["predicted_output_classes"]
        else:
            word=schedule[attempt]
            classes=None
        if len(word)!=10:
            raise AssertionError("INVALID_EQ_WORD_LENGTH")
        outputs=paid_query(hidden,word)
        known.append({"inputs":list(word),"outputs":list(outputs)})
        survivors=[candidate for candidate in remaining
                   if s.trace(candidate,word)==outputs]
        query_log.append({"word":list(word),"observed_outputs":list(outputs),
                          "consistent_before":len(remaining),
                          "consistent_after":len(survivors),
                          "predicted_output_classes":classes,
                          "cost":10})
        # Scientific audit assertion ONLY AFTER observing the paid answer.
        if not survivors or hidden not in survivors:
            raise AssertionError("INCONSISTENT_PAID_OBSERVATION")
        remaining=survivors
        if outputs != s.trace(BASE,word):
            status="DETECTED_DIVERGENCE"
            break
    return {"arm":arm,"status":status,"detected":status=="DETECTED_DIVERGENCE",
            "queries_paid":len(query_log),"symbols_paid":len(query_log)*10,
            "query_log":query_log,"last_consistent_models":len(remaining)}


def conduct():
    observations=s.six_zero_observations()
    space,_=s.enumerate_consistent_models(s.validate_observations(observations))
    cohort,eligible=new_cohort(space)
    reps,_=s.diversify(space)
    static,_=s.rank_queries(reps,observations)
    methods=["STATIC_DIVERSITY","FIXED_PREFIX","ACTIVE_DISAGREEMENT"]
    trials=[]
    for index,hidden in enumerate(cohort):
        arms={name:run_policy(name,hidden,observations,space,static)
              for name in methods}
        trials.append({"index":index,"canonical_machine":hidden,"arms":arms})
    scores={
        name:{
            "detected":sum(t["arms"][name]["detected"] for t in trials),
            "total_paid_symbols":sum(t["arms"][name]["symbols_paid"] for t in trials),
            "mean_paid_symbols":sum(t["arms"][name]["symbols_paid"] for t in trials)/TEST_N,
        } for name in methods
    }
    candidate=scores["ACTIVE_DISAGREEMENT"]
    positive=(candidate["detected"]==TEST_N
              and candidate["mean_paid_symbols"]<scores["FIXED_PREFIX"]["mean_paid_symbols"]
              and candidate["mean_paid_symbols"]<scores["STATIC_DIVERSITY"]["mean_paid_symbols"])
    return {
        "experiment":EXPERIMENT,"preregistered_commit":PREREG,
        "status":"DESCRIPTIVE_ACTIVE_BENEFIT" if positive else "NO_ACTIVE_BENEFIT_DEMONSTRATED",
        "training_observations":observations,"world_count":TEST_N,
        "structurally_eligible_worlds":eligible,"sample_seed":SAMPLE_SEED,
        "all_from_binary_3_state_finite_models":True,
        "fixed_cost_cap":80,"adaptive_and_static_cost_cap":320,
        "policies":methods,"runs":trials,"summary":scores,
        "no_paid_api":True,"main_modified":False,"generalization_proven":False,
        "limitations":[
            "Synthetic machines from the same bounded three-state family.",
            "Twenty-four test machines are not representative of external software.",
            "Fixed policy uses only eight probes; compare realized costs, not cap alone.",
            "Detection of a divergence from one state is not full model identification.",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    report=conduct()
    a.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(report,sort_keys=True,indent=2)+"\n").encode()
    a.output.write_bytes(raw)
    print(json.dumps({"experiment":EXPERIMENT,"status":report["status"],
                      "summary":report["summary"],
                      "report_sha256":sha256(raw).hexdigest()},sort_keys=True))


if __name__=="__main__":
    main()
