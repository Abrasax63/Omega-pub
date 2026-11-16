"""OMEGA-COVER-REPLICATION-05: fixed algorithms, 48 fresh worlds, paired exact inference.

Imports four unmodified AALpy L* strategies from PR138/139, tests a new
isomorphism-disjoint structural holdout, and calculates exact paired McNemar
directional probabilities + Holm correction and stratified paired bootstrap.
No oracle results are used during learning or to adjust the strategies.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from math import comb
from pathlib import Path
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"omega-cover-constrained-04"))
import constrained_lab as q  # unchanged policies: calls cover_lab
from mealy_lab import Mealy,digest

c=q.c
EXPERIMENT="OMEGA-COVER-REPLICATION-05"
PREREG="8ba60bd44553b439d109302f9a6d0a07c99e7188"
GENERATORS=((4,38104,16),(5,38105,16),(6,38106,16))
CAPS=(300,500)
PRIMARY=500
ARMS=tuple(q.ARMS)
TARGET="COVER_DISTINGUISH_LEN10"
REFS=tuple(x for x in ARMS if x!=TARGET)
BOOTSTRAP_SEED=48319
BOOTSTRAP_REPS=5000
ALPHA=0.05
RESERVED_WORDS=128


def historical_signatures():
    """Known, now-public machines through PR #139, without rerunning learners."""
    existing=set(q.old_signatures())
    for entry in q.fresh_worlds():
        if entry["signature"] in existing:
            raise AssertionError("EXISTING_PR139_COLLIDES_WITH_PRIOR")
        existing.add(entry["signature"])
    if len(existing)!=1148:
        raise AssertionError(f"PRIOR_WORLD_MANIFEST_DRIFT:{len(existing)}")
    return existing


def fresh_worlds():
    """Pre-filter ONLY full reachability, state distinguishability and isomorphism."""
    seen=historical_signatures()
    result=[]
    for n,seed,count in GENERATORS:
        rng=random.Random(seed)
        accepted=draws=unreachable=nonminimal=duplicates=0
        while accepted<count:
            draws+=1
            if draws>300000:
                raise AssertionError("STRUCTURALLY_ADMISSIBLE_WORLD_EXHAUSTED")
            machine=Mealy(
                tuple(tuple(rng.randrange(n) for _ in c.b.ALPHABET)
                      for _ in range(n)),
                tuple(tuple(rng.randrange(3) for _ in c.b.ALPHABET)
                      for _ in range(n)),
            )
            if len(c.reachable(machine))!=n:
                unreachable+=1
                continue
            if not c.distinguishable(machine):
                nonminimal+=1
                continue
            signature=machine.signature()
            if signature in seen:
                duplicates+=1
                continue
            seen.add(signature)
            result.append({
                "name":f"N{n}_{accepted}","size":n,"index":accepted,
                "seed":seed,"signature":signature,
                "attempts_cumulative":draws,
                "unreachable_rejections":unreachable,
                "nonminimal_rejections":nonminimal,
                "duplicate_rejections":duplicates,
                "world":machine,
            })
            accepted+=1
    if len(result)!=48 or len(seen)!=1196:
        raise AssertionError("NEW_REPLICATION_MACHINE_SIGNATURE_DRIFT")
    return result


def reserved_words(n,index):
    """Independent of learning; same words for every arm and budget."""
    rng=random.Random(990000+100*n+index)
    words=set()
    while len(words)<RESERVED_WORDS:
        length=rng.randint(12,20)
        words.add(tuple(rng.choice(c.b.ALPHABET) for _ in range(length)))
    return sorted(words)


def exact_one_sided_mcnemar(wins,losses):
    """H0 exchangeability of discordances; P[Binomial(n,.5) >= wins]."""
    if not all(isinstance(x,int) and x>=0 for x in (wins,losses)):
        raise ValueError("INVALID_DISCORDANCE_COUNTS")
    n=wins+losses
    if n==0:
        return 1.0
    return sum(comb(n,k) for k in range(wins,n+1))/2**n


def holm_adjust(p_values):
    """Holm step-down familywise p-adjustment for 3 paired comparisons."""
    if set(p_values)!=set(REFS):
        raise ValueError("EXPECTED_THREE_REFERENCES")
    ordered=sorted(p_values.items(),key=lambda x:(x[1],x[0]))
    m=len(ordered)
    result={}
    running=0.0
    for index,(name,p) in enumerate(ordered):
        if not 0<=p<=1:
            raise ValueError("INVALID_P_VALUE")
        running=max(running,min(1.0,(m-index)*p))
        result[name]=min(1.0,running)
    return {arm:result[arm] for arm in REFS}


def paired_stratified_bootstrap(machines,comparison,seed,replications=BOOTSTRAP_REPS):
    """Paired resampling of machines *within each 4/5/6 state stratum*."""
    if replications!=5000:
        raise ValueError("PRECOMMITTED_BOOTSTRAP_REPLICATION_COUNT_CHANGED")
    by_size={n:[x for x in machines if x["size"]==n] for n in (4,5,6)}
    if any(len(x)!=16 for x in by_size.values()):
        raise AssertionError("STRATIFIED_BOOTSTRAP_HAS_WRONG_COHORT_SIZE")
    if comparison not in REFS:
        raise ValueError("UNEXPECTED_COMPARATOR")
    rng=random.Random(seed)
    res=[]
    for _ in range(replications):
        delta=0
        for n in (4,5,6):
            strata=by_size[n]
            for _ in range(16):
                row=strata[rng.randrange(16)]
                # Status values are already exact, never a surrogate by accuracy.
                delta+=(int(row["exact"][TARGET])-int(row["exact"][comparison]))
        res.append(delta/48)
    res.sort()
    lower=res[int((replications-1)*0.025)]
    upper=res[int((replications-1)*0.975)]
    return {"lower_95":lower,"upper_95":upper,"seed":seed,
            "replications":replications}


def summarize_comparison(cases,cap):
    """One paired statistical observation per machine, not per query or word."""
    if len(cases)!=48:
        raise AssertionError("STATISTICAL_UNIT_IS_MACHINE_48_EXPECTED")
    records=[]
    for case in cases:
        allarms=case["budgets"][str(cap)]
        exact={arm:allarms[arm]["exact_equivalence"]["status"]=="EXACT_EQUIVALENT"
               for arm in ARMS}
        accuracy={arm:allarms[arm]["reserved"]["whole_word_accuracy"]
                  for arm in ARMS}
        records.append({"size":case["size"],"name":case["name"],
                        "exact":exact,"accuracy":accuracy})
    scores={
        arm:{
            "exact":sum(row["exact"][arm] for row in records),
            "accuracy":sum(row["accuracy"][arm] for row in records)/48,
            "interrupted":sum(
                case["budgets"][str(cap)][arm]["training"]["status"].startswith(
                    "BUDGET_INTERRUPTED")
                for case in cases
            ),
            "spent":sum(case["budgets"][str(cap)][arm]["training"]["ledger"]["spent_symbols"]
                        for case in cases),
            "eq_words":sum(case["budgets"][str(cap)][arm]["training"]["eq_words_tested"]
                           for case in cases),
        } for arm in ARMS
    }
    differences={}
    pvals={}
    for ref in REFS:
        wins=sum(r["exact"][TARGET] and not r["exact"][ref] for r in records)
        losses=sum(r["exact"][ref] and not r["exact"][TARGET] for r in records)
        pval=exact_one_sided_mcnemar(wins,losses)
        pvals[ref]=pval
        differences[ref]={
            "cover_only_exact":wins,
            "reference_only_exact":losses,
            "concordant_exact":sum(r["exact"][TARGET] and r["exact"][ref]
                                   for r in records),
            "concordant_inexact":sum(not r["exact"][TARGET] and not r["exact"][ref]
                                     for r in records),
            "exact_count_delta":wins-losses,
            "exact_rate_delta":(wins-losses)/48,
            "one_sided_exact_mcnemar_p":pval,
            "mean_reserved_word_accuracy_delta":(
                scores[TARGET]["accuracy"]-scores[ref]["accuracy"]
            ),
            # Deterministic seed derived by canonical comparison order.
            "stratified_paired_bootstrap_95":paired_stratified_bootstrap(
                records,ref,BOOTSTRAP_SEED+REFS.index(ref),
            ),
        }
        if sum(differences[ref][name] for name in (
            "cover_only_exact","reference_only_exact",
            "concordant_exact","concordant_inexact"))!=48:
            raise AssertionError("PAIRED_CONTINGENCY_BAD_ACCOUNTING")
    adj=holm_adjust(pvals)
    for ref in REFS:
        differences[ref]["holm_adjusted_p"]=adj[ref]
        differences[ref]["unadjusted_descriptive_advantage"]=(
            differences[ref]["exact_count_delta"]>0 and
            differences[ref]["mean_reserved_word_accuracy_delta"]>=-1e-12
        )
        differences[ref]["strong_condition"]=(
            differences[ref]["exact_count_delta"]>0 and
            differences[ref]["holm_adjusted_p"]<=ALPHA and
            differences[ref]["stratified_paired_bootstrap_95"]["lower_95"]>0 and
            differences[ref]["mean_reserved_word_accuracy_delta"]>=-1e-12
        )
    return {
        "budget_cap":cap,
        "independent_machine_units":48,
        "stratum_sizes":{"4":16,"5":16,"6":16},
        "policy_scores":scores,
        "paired":differences,
        "all_three_strong":all(differences[x]["strong_condition"] for x in REFS),
        "all_three_descriptive":all(differences[x]["unadjusted_descriptive_advantage"]
                                     for x in REFS),
    }


def conduct():
    if c.b.version("aalpy")!="1.6.2":
        raise RuntimeError("AALPY_VERSION_DRIFT")
    worlds=fresh_worlds()
    cases=[]
    for meta in worlds:
        machine=meta["world"]
        n,j=meta["size"],meta["index"]
        words=reserved_words(n,j)
        trials={}
        for cap in CAPS:
            trials[str(cap)]={}
            for idx,arm in enumerate(ARMS):
                seed=940000+1000*n+30*j+idx
                trial=c.evaluate_one(machine,arm,cap,seed,words)
                # Evaluation only; no exact truth supplied to AALpy.
                ledger=trial["training"]["ledger"]
                if ledger["spent_symbols"]>cap:
                    raise AssertionError("SUL_COST_CEILING_VIOLATION")
                if sum(x["charge"] for x in ledger["query_log"])!=ledger["spent_symbols"]:
                    raise AssertionError("NONRECONCILED_SUL_COST")
                eqrows=[x for x in ledger["query_log"] if x["phase"]=="EQ"]
                if len(eqrows)!=trial["training"]["eq_words_tested"]:
                    raise AssertionError("EQ_QUERY_COUNT_DRIFT")
                if any(len(x["inputs"])!=10 for x in eqrows):
                    raise AssertionError("EQ_LENGTH_NOT_TEN")
                if trial["exact_equivalence"]["status"]=="EXACT_EQUIVALENT":
                    if trial["reserved"]["whole_word_accuracy"]!=1.0:
                        raise AssertionError("EXACT_CERTIFIED_BUT_FAILED_TEST")
                trials[str(cap)][arm]=trial
        cases.append({
            "name":meta["name"],"size":n,"index":j,
            "canonical_signature":meta["signature"],
            "world_generation_seed":meta["seed"],
            "generator_attempts":meta["attempts_cumulative"],
            "unreachable_rejections":meta["unreachable_rejections"],
            "nonminimal_rejections":meta["nonminimal_rejections"],
            "isomorphism_rejections":meta["duplicate_rejections"],
            "accessible_states":len(c.reachable(machine)),
            "pairwise_distinguishable":c.distinguishable(machine),
            "reserved_words_sha256":digest(words),
            "evaluator_only_truth":{"transitions":machine.transitions,
                                    "outputs":machine.outputs,"initial_state":0},
            "budgets":trials,
        })
    primary=summarize_comparison(cases,PRIMARY)
    secondary=summarize_comparison(cases,CAPS[0])
    status=("REPLICATED_STRONG_QUERY_GAIN"
            if primary["all_three_strong"] else
            "NO_ROBUST_QUERY_GAIN_DEMONSTRATED")
    return {
        "experiment":EXPERIMENT,
        "preregistered_commit":PREREG,
        "status":status,
        "methods":list(ARMS),
        "comparison_refs":list(REFS),
        "budgets":list(CAPS),
        "primary_budget":PRIMARY,
        "worlds":len(cases),
        "eq_word_length":10,
        "max_eq_per_round":32,
        "learning_backend":"unchanged_AALpy_1.6.2_Lstar_from_PR138",
        "same_algorithm_and_hyperparameters_as_PR139":True,
        "same_rng_seed_across_budgets":True,
        "exact_oracle_evaluation_only":True,
        "paired_unit":"Mealy machine",
        "bootstrap_reps":BOOTSTRAP_REPS,
        "bootstrap_seed":BOOTSTRAP_SEED,
        "alpha":ALPHA,
        "statistical_tests":"one-sided exact McNemar plus Holm over three baselines, and 95pct stratified paired machine bootstrap",
        "no_paid_api":True,"main_modified":False,
        "generalization_certified":False,
        "cases":cases,
        "primary":primary,"secondary":secondary,
        "limitations":[
            "48 new minimal/reachable simulated systems but only one generator family per size.",
            "The 128 reserved words within one machine are correlated; statistical unit is machine.",
            "Confidence intervals are paired bootstrap summaries, not finite-sample coverage guarantees.",
            "Exact McNemar probabilities are conditional on discordant pairs; Holm controls three tested references.",
            "Identical capped budgets and ten-symbol EQ tests do not imply identical paid total or membership-query information.",
            "AALpy L* is a published baseline; Omega-guided cover is only an EQ scheduling heuristic.",
            "All exact equivalence labels are computed by independent evaluator after the learner terminates.",
            "No learned general scientific intelligence or autonomous self-programming is demonstrated.",
        ],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps({
        "experiment":EXPERIMENT,"status":result["status"],
        "primary_scores":result["primary"]["policy_scores"],
        "primary_paired":result["primary"]["paired"],
        "secondary_scores":result["secondary"]["policy_scores"],
        "secondary_paired":result["secondary"]["paired"],
        "report_sha256":sha256(raw).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
