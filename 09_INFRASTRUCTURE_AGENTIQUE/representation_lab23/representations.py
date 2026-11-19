#!/usr/bin/env python3
"""Omega LAB23: explicit 'pas de côté' in finite dynamical-system observability.

Generate alternative representations, independently falsify them against raw
state traces, retain real minimal counterexamples, and inspect structural
invariants.  No generative model, novel theory, automated scientific promotion,
or claim of independent discovery is made here.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import random
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from read import safe_read

SOURCE_PATH = ROOT / "02_MATHEMATIQUES/observabilite_temporelle/OBS-V8-FACT-INF.md"
SOURCE_BLOB = "6d7f6b44c683852871b08a37f814bae5381de11f"
SEED = 20261119
RECIPES = (
    ("pair_pullback", "relational", "R0=X^2; R[h+1]=eq(pi) and pullback_T(R[h])"),
    ("partition_refinement", "partition", "P0=0; P[h+1]=code(pi,P[h] after T)"),
    ("unordered_histogram", "frequency", "frequency of pi on first h orbit positions"),
    ("current_only", "projection", "pi at t=0, ignoring the rest of the orbit"),
    ("future_only", "temporal_shift", "pi on times 1,...,h; omit time 0"),
)
FAMILIES = tuple(x[0] for x in RECIPES)
EXPECTED_EXACT = frozenset(("pair_pullback", "partition_refinement"))
EXPECTED_ADVERSARIAL = frozenset(("unordered_histogram", "current_only", "future_only"))


def pairs_from_signatures(signatures: list[object]) -> frozenset[tuple[int,int]]:
    n = len(signatures)
    return frozenset((i, j) for i in range(n) for j in range(i+1, n)
                     if signatures[i] == signatures[j])


def direct_oracle(t: tuple[int,...], pi: tuple[int,...], h: int) -> frozenset:
    """Separate reference, direct state by state trajectory inspection."""
    n = len(t)
    indistinguishable = set()
    for x in range(n):
        for y in range(x+1,n):
            a,b=x,y
            same=True
            for _ in range(h):
                if pi[a] != pi[b]:
                    same=False
                    break
                a,b=t[a],t[b]
            if same:
                indistinguishable.add((x,y))
    return frozenset(indistinguishable)


def direct_words(t: tuple[int,...], pi: tuple[int,...], h: int,
                 state: int) -> tuple[int,...]:
    ans=[]
    for _ in range(h):
        ans.append(pi[state])
        state=t[state]
    return tuple(ans)


def pair_pullback(t: tuple[int,...], pi: tuple[int,...], h: int) -> frozenset:
    n=len(t)
    relation=[[True for _ in range(n)] for _ in range(n)]
    for _ in range(h):
        relation=[[pi[x]==pi[y] and relation[t[x]][t[y]]
                   for y in range(n)] for x in range(n)]
    return frozenset((x,y) for x in range(n) for y in range(x+1,n)
                     if relation[x][y])


def partition_refinement(t: tuple[int,...], pi: tuple[int,...], h: int) -> frozenset:
    n=len(t)
    group=[0]*n
    for _ in range(h):
        labels={}
        next_groups=[]
        for x in range(n):
            label=(pi[x],group[t[x]])
            if label not in labels:
                labels[label]=len(labels)
            next_groups.append(labels[label])
        group=next_groups
    return pairs_from_signatures(group)


def unordered_histogram(t: tuple[int,...], pi: tuple[int,...], h: int) -> frozenset:
    return pairs_from_signatures([sum(direct_words(t,pi,h,x)) for x in range(len(t))])


def current_only(t: tuple[int,...], pi: tuple[int,...], h: int) -> frozenset:
    return pairs_from_signatures(list(pi))


def future_only(t: tuple[int,...], pi: tuple[int,...], h: int) -> frozenset:
    signatures=[]
    for x in range(len(t)):
        state=t[x]
        signatures.append(direct_words(t,pi,h,state))
    return pairs_from_signatures(signatures)


OPERATORS = {
    "pair_pullback": pair_pullback,
    "partition_refinement": partition_refinement,
    "unordered_histogram": unordered_histogram,
    "current_only": current_only,
    "future_only": future_only,
}


def propose_alternative_views(t: tuple[int,...], pi: tuple[int,...]) -> list[dict]:
    """Representation-grammar generator (no oracle outputs, labels or gold passed).

    This is programmatic generation from a predefined grammar, NOT free-form
    innovation or a trained model.
    """
    n=len(t)
    if not 2 <= n <= 6 or len(pi)!=n or any(v<0 or v>=n for v in t):
        raise ValueError("TRANSITION_OUT_OF_SCOPE")
    if any(c not in (0,1) for c in pi):
        raise ValueError("OUTPUT_OUT_OF_SCOPE")
    shared={"n":n,"states":list(range(n)),
            "observation_alphabet":[0,1],
            "observed_color_count":len(set(pi))}
    return [
        {"id":name,"representation_space":space,"recipe":rule,
         "scope":shared, "candidate_only":True,
         "certified_without_check":False}
        for name,space,rule in RECIPES
    ]


def make_counterexample(n: int, t: tuple[int,...], pi: tuple[int,...],
                        h: int, expected: frozenset, observed: frozenset) -> dict:
    pair=min(expected.symmetric_difference(observed))
    i,j=pair
    return {
        "n":n,"T":list(t),"pi":list(pi),"horizon":h,
        "pair":[i,j],
        "oracle_equivalent":pair in expected,
        "candidate_equivalent":pair in observed,
        "oracle_trace_first":list(direct_words(t,pi,h,i)),
        "oracle_trace_second":list(direct_words(t,pi,h,j)),
        "oracle_relation_pairs":len(expected),
        "candidate_relation_pairs":len(observed),
    }


def exhaustive_cases():
    for n in (2,3,4):
        for t in itertools.product(range(n),repeat=n):
            for pi in itertools.product((0,1),repeat=n):
                yield t,pi


def reserved_cases():
    rng=random.Random(SEED)
    for n in (5,6):
        for index in range(64):
            t=tuple(rng.randrange(n) for _ in range(n))
            pi=tuple(rng.randrange(2) for _ in range(n))
            yield (n,index,t,pi)


def evaluate_phase(cases, label: str) -> dict:
    counts=Counter()
    mismatch=Counter()
    first={name:None for name in FAMILIES}
    invariant_failures=[]
    stabilization_depths=Counter()
    reached_bound_witness=None
    corrected_n_minus_one_witness=None
    transition_counts=Counter()
    start=time.perf_counter()
    for case in cases:
        if len(case)==4:
            n, _,t,pi=case
        else:
            t,pi=case
            n=len(t)
        generated=propose_alternative_views(t,pi)
        if tuple(x["id"] for x in generated)!=FAMILIES:
            raise AssertionError("GRAMMAR_REGISTRY_DRIFT")
        counts["systems"]+=1
        previous=None
        all_expected=[]
        for h in range(1,n+2):
            expected=direct_oracle(t,pi,h)
            all_expected.append(expected)
            counts["horizon_cases"]+=1
            if previous is not None:
                if not expected.issubset(previous):
                    invariant_failures.append({"type":"MONOTONE_REFINEMENT","n":n,
                                               "T":t,"pi":pi,"h":h})
                if previous == expected:
                    transition_counts["stable_steps"]+=1
                else:
                    transition_counts["strict_splits"]+=1
            previous=expected
            for recipe in FAMILIES:
                got=OPERATORS[recipe](t,pi,h)
                counts["candidate_evaluations"]+=1
                if got!=expected:
                    mismatch[recipe]+=1
                    if first[recipe] is None:
                        first[recipe]=make_counterexample(n,t,pi,h,expected,got)
        if all_expected[-2]!=all_expected[-1]:
            invariant_failures.append({"type":"N_STEP_BOUND","n":n,
                                       "T":t,"pi":pi})
        stable_next=min((h for h in range(1,n+1)
                         if all_expected[h-1]==all_expected[h]),default=None)
        if stable_next is None:
            invariant_failures.append({"type":"NO_FIXED_POINT_BY_N","n":n,
                                       "T":t,"pi":pi})
        else:
            stabilization_depths[str(stable_next)]+=1
            if reached_bound_witness is None and stable_next==n:
                # Kept to expose the originally preregistered but falsified expectation.
                reached_bound_witness={
                    "n":n, "T":list(t),"pi":list(pi),
                    "first_stable_horizon":stable_next,
                }
            if corrected_n_minus_one_witness is None and n>=3 and stable_next==n-1:
                corrected_n_minus_one_witness={
                    "n":n, "T":list(t),"pi":list(pi),
                    "first_stable_horizon":stable_next,
                    "last_nonstable_relation_size":len(all_expected[n-3]),
                    "stable_relation_size":len(all_expected[n-2])
                }
            if any(s!=all_expected[stable_next-1]
                   for s in all_expected[stable_next:]):
                invariant_failures.append({"type":"STABILITY_NOT_PERMANENT","n":n,
                                           "T":t,"pi":pi,"stable_h":stable_next})
    return {
        "phase":label,
        "counts":dict(counts),
        "mismatches":{name:mismatch[name] for name in FAMILIES},
        "minimal_counterexamples":first,
        "invariant_failure_count":len(invariant_failures),
        "invariant_failures_first_5":invariant_failures[:5],
        "stabilization_depth_histogram":dict(stabilization_depths),
        "first_example_tight_n_bound":reached_bound_witness,
        "first_example_tight_n_minus_1_bound":corrected_n_minus_one_witness,
        "transitions":dict(transition_counts),
        "wall_clock_seconds_observed_not_benchmark":round(time.perf_counter()-start,3),
    }


def perform() -> dict:
    raw=safe_read(SOURCE_PATH,SOURCE_BLOB)
    source_lines=raw.decode("utf-8").splitlines()
    if not any("génératrice" in s for s in source_lines):
        raise ValueError("MATH_SOURCE_CONTENT_NOT_THE_EXPECTED_CONTEXT")
    candidates=propose_alternative_views((1,0),(0,1))
    calibration=evaluate_phase(exhaustive_cases(),"EXHAUSTIVE_N2_N3_N4")
    validation=evaluate_phase(reserved_cases(),"FIXED_SEED_RESERVED_N5_N6")
    zero_errors={name:calibration["mismatches"][name]==0
                 and validation["mismatches"][name]==0
                 for name in FAMILIES}
    exact=[name for name in FAMILIES if zero_errors[name]]
    falsified=[name for name in FAMILIES if not zero_errors[name]]
    tests_ok=(
        calibration["counts"]["systems"]==4328
        and calibration["counts"]["horizon_cases"]==21392
        and validation["counts"]["systems"]==128
        and validation["counts"]["horizon_cases"]==832
        and set(exact)==EXPECTED_EXACT
        and set(falsified)==EXPECTED_ADVERSARIAL
        and calibration["invariant_failure_count"]==0
        and validation["invariant_failure_count"]==0
        and calibration["first_example_tight_n_bound"] is None
        and calibration["first_example_tight_n_minus_1_bound"] is not None
    )
    return {
        "experiment":"OMEGA_REPRESENTATION_LAB23_FINITE_OBSERVABILITY",
        "result_status":"PASS_RESTRICTED_REPRESENTATION_TEST" if tests_ok else "FAIL_OR_INDETERMINATE",
        "math_source_git_blob":SOURCE_BLOB,
        "math_source_path":SOURCE_PATH.relative_to(ROOT).as_posix(),
        "scope":"BINARY_OBSERVATIONS_DETERMINISTIC_FINITE_TRANSITIONS_ONLY",
        "calibration_has_seen_all_n_le_4":True,
        "reserved_cases_are_synthetic_not_independent_external":True,
        "test_seed":SEED,
        "generated_candidate_count":len(candidates),
        "generator_type":"PREPROGRAMMED_REPRESENTATION_GRAMMAR",
        "generated_representations":candidates,
        "calibration":calibration,
        "reserved_validation":validation,
        "recipes_empirically_equivalent":exact,
        "recipes_falsified":falsified,
        "invariants_tested":[
            "E[h+1] subset E[h]",
            "E[h]=E[h+1] implies permanence for later h up to n+1",
            "E[n]=E[n+1] on n states",
            "original prereg n-horizon optimum refuted; n-1 bound is tight for witness n<=4",
        ],
        "falsified_preregistered_claim":{
            "claim":"the n-step stabilization bound is achieved",
            "status":"REFUTED_ON_EXHAUSTIVE_N2_N4",
            "falsification_run":44495078554,
            "corrected_sharp_bound":"n-1 for n>=2, by partition class counting",
            "document":"ERRATUM_FALSIFICATION.md",
        },
        "novel_theorem_discovered":False,
        "general_formal_proof_automated":False,
        "independent_creativity_of_llm_demonstrated":False,
        "scientific_autopromotions":0,
        "paid_api_calls":0,
        "main_branch_modified":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    try:
        result=perform()
    except Exception:
        result={"result_status":"TECHNICAL_FAILURE",
                "error":traceback.format_exc(),
                "scientific_autopromotions":0}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("LAB23",result["result_status"],
          "equivalent",result.get("recipes_empirically_equivalent"),
          "falsified",result.get("recipes_falsified"),flush=True)
    if result["result_status"]!="PASS_RESTRICTED_REPRESENTATION_TEST":
        raise SystemExit(1)


if __name__=="__main__":
    main()
