"""OMEGA-COVER-CONSTRAINED-04: *untouched* PR138 learners on NEW tight-budget holdout.

Uses cover_lab.MatchOracle/train/evaluate_one exactly as implemented in PR138.
Only fresh data seeds and 300/500 query budgets differ from the precommitted
pilot; oracle truth remains available only to the independent evaluator.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from pathlib import Path
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-cover-03"))
import cover_lab as c  # unchanged reference methods
from mealy_lab import Mealy,digest

EXPERIMENT="OMEGA-COVER-CONSTRAINED-04"
PREREG="ae6a29814d8678e969c903cbc013ae895a80bfe5"
GENERATORS=((4,37104,4),(5,37105,4),(6,37106,4))
CAPS=(300,500)
PRIMARY=500
ARMS=c.ARMS
RESERVED_WORDS=128


def old_signatures():
    used=c.old_signatures()
    old=c.new_worlds()
    for row in old:
        if row["sig"] in used:
            raise AssertionError("PREVIOUS_PILOT_SIGNED_COLLISION")
        used.add(row["sig"])
    if len(used)!=1136:
        raise AssertionError(f"OLD_HOLDOUT_INVENTORY_INVALID:{len(used)}")
    return used


def fresh_worlds():
    seen=old_signatures()
    rows=[]
    for n,seed,count in GENERATORS:
        rng=random.Random(seed)
        draws=filtered_reach=filtered_minimal=filtered_dup=0
        accepted=0
        while accepted<count:
            draws+=1
            if draws>100000:
                raise RuntimeError("STRUCTURAL_GENERATOR_EXHAUSTION")
            world=Mealy(
                tuple(tuple(rng.randrange(n) for _ in c.b.ALPHABET)
                      for _ in range(n)),
                tuple(tuple(rng.randrange(3) for _ in c.b.ALPHABET)
                      for _ in range(n)),
            )
            if len(c.reachable(world))!=n:
                filtered_reach+=1
                continue
            if not c.distinguishable(world):
                filtered_minimal+=1
                continue
            sig=world.signature()
            if sig in seen:
                filtered_dup+=1
                continue
            seen.add(sig)
            rows.append({
                "name":f"N{n}_{accepted}","n":n,"index":accepted,
                "seed":seed,"signature":sig,"world":world,
                "draws":draws,"unreachable_rejections":filtered_reach,
                "nonminimal_rejections":filtered_minimal,
                "isomorphism_rejections":filtered_dup,
            })
            accepted+=1
    if len(rows)!=12 or len(seen)!=1148:
        raise AssertionError("NEW_TEST_WORLD_OVERLAP")
    return rows


def reserved_words(n,j):
    rng=random.Random(970000+100*n+j)
    words=set()
    while len(words)<RESERVED_WORDS:
        length=rng.randint(12,20)
        words.add(tuple(rng.choice(c.b.ALPHABET) for _ in range(length)))
    return sorted(words)


def experiment():
    if c.b.version("aalpy")!="1.6.2":
        raise RuntimeError("EXTERNAL_LSTAR_VERSION_DRIFT")
    worlds=fresh_worlds()
    entries=[]
    for meta in worlds:
        n,j=meta["n"],meta["index"]
        true_world=meta["world"]
        words=reserved_words(n,j)
        trials={}
        for cap in CAPS:
            trials[str(cap)]={}
            for i,arm in enumerate(ARMS):
                seed=920000+1000*n+30*j+i
                trials[str(cap)][arm]=c.evaluate_one(
                    true_world,arm,cap,seed,words)
        entries.append({
            "name":meta["name"],"size":n,
            "canonical_signature":meta["signature"],
            "generation_seed":meta["seed"],
            "attempts":meta["draws"],
            "unreachable_rejections":meta["unreachable_rejections"],
            "nonminimal_rejections":meta["nonminimal_rejections"],
            "isomorphism_rejections":meta["isomorphism_rejections"],
            "reachable_states":len(c.reachable(true_world)),
            "distinguishable_states":c.distinguishable(true_world),
            "evaluator_only_truth":{
                "transitions":true_world.transitions,
                "outputs":true_world.outputs,"initial_state":0,
            },
            "heldout_words_sha256":digest(words),
            "arms_by_budget":trials,
        })
    summaries={}
    for cap in CAPS:
        scores={}
        for arm in ARMS:
            data=[row["arms_by_budget"][str(cap)][arm] for row in entries]
            scores[arm]={
                "behavioral_exact":sum(
                    x["exact_equivalence"]["status"]=="EXACT_EQUIVALENT"
                    for x in data
                ),
                "hypotheses_produced":sum(
                    x["training"]["hypothesis_states"] is not None
                    for x in data
                ),
                "budget_interrupted":sum(
                    x["training"]["status"].startswith("BUDGET_INTERRUPTED")
                    for x in data
                ),
                "mean_heldout_word_accuracy":sum(
                    x["reserved"]["whole_word_accuracy"] for x in data
                )/len(data),
                "paid_total_symbols":sum(
                    x["training"]["ledger"]["spent_symbols"] for x in data
                ),
                "paid_EQ_symbols":sum(
                    x["training"]["ledger"]["by_phase_spent"]["EQ"]
                    for x in data
                ),
                "eq_words_tested":sum(
                    x["training"]["eq_words_tested"] for x in data
                ),
                "counterexamples_found":sum(
                    x["training"]["eq_counterexamples"] for x in data
                ),
            }
        summaries[str(cap)]=scores
    primary=summaries[str(PRIMARY)]
    guided=primary["COVER_DISTINGUISH_LEN10"]
    baselines=[primary[x] for x in ARMS if x!="COVER_DISTINGUISH_LEN10"]
    success=(
        all(guided["behavioral_exact"]>x["behavioral_exact"] for x in baselines)
        and all(guided["mean_heldout_word_accuracy"]+1e-12>=
                x["mean_heldout_word_accuracy"] for x in baselines)
    )
    status=("DESCRIPTIVE_CONSTRAINED_COVER_GAIN"
            if success else "NO_DEMONSTRATED_CONSTRAINED_GAIN")
    report={
        "experiment":EXPERIMENT,"preregistered_commit":PREREG,
        "status":status,
        "models":list(ARMS),"budgets":list(CAPS),"primary":PRIMARY,
        "learning_engine":"unchanged_PR138_AALpy_1.6.2_run_Lstar",
        "EQ_word_length":c.EQ_LENGTH,
        "max_EQ_words_per_round":c.EQ_ROUND_WORDS,
        "same_algorithms_as_PR138":True,
        "same_seed_across_budgets":True,
        "evaluator_only_truth_access":True,
        "no_paid_api":True,"main_modified":False,
        "generalization_proven":False,
        "new_worlds":len(entries),"cases":entries,"scores":summaries,
        "limitations":[
            "This pilot uses fresh seeds and an isomorphism-disjoint holdout after observing the nonbinding PR138 budgets.",
            "All four arms use real AALpy L* and matched ten-symbol EQ candidates.",
            "A paused learner can expose a provisional candidate, which is not a certificate.",
            "Actual total query costs and MQ information content can differ.",
            "Twelve synthetic models cannot certify general superiority of an autonomous agent.",
            "The true Mealy tables were not supplied to the learning algorithms.",
        ],
    }
    for case in entries:
        for budget in CAPS:
            for arm in ARMS:
                record=case["arms_by_budget"][str(budget)][arm]
                cost=record["training"]["ledger"]["spent_symbols"]
                if cost>budget:
                    raise AssertionError("LEARNER_BUDGET_OVERRUN")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=experiment()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    payload=(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(payload)
    print(json.dumps({
        "experiment":EXPERIMENT,"status":report["status"],
        "primary":report["scores"]["500"],
        "secondary":report["scores"]["300"],
        "sha256":sha256(payload).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
