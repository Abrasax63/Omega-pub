"""Audit of which certificate failures remain under the frozen policy.

Retrospective upper bound is an explanatory diagnostic, never a competing
policy. It has access to test method outcomes, and was NOT preregistered as
a prospective arm. It must not be used to retune the fitted strategies.
"""
import json
from collections import defaultdict

from certification_methods_v01 import METHODS, cases, run_method
from certificate_aware_selector_v01 import evaluate, best_fixed, execute_fixed


def audit():
    report=evaluate()
    by_case=defaultdict(dict)
    for row in report["traces"]:
        by_case[row["case"]][row["arm"]]=row
    holdout=[t for t in cases() if t["partition"]=="test"]
    unsolved={}
    paired=[]
    has_certificate=0
    for t in holdout:
        plausible=[m for m in METHODS
                   if run_method(t,m)["observation"] in ("yes","no")]
        if plausible:has_certificate+=1
        c=by_case[t["id"]]["C_certificate"]
        b=by_case[t["id"]]["B_subtype"]
        d=by_case[t["id"]]["D_conditioned"]
        e=by_case[t["id"]]["E_original"]
        if c["verdict"]=="abstain":
            unsolved[t["id"]]={
                "kind":t["kind"],
                "certificate_available_among_four_methods":bool(plausible),
                "methods_that_can_certify":plausible,
                "attempted": [x["method"] for x in c["trace"]],
            }
        paired.append({
            "case":t["id"],"kind":t["kind"],
            "C_matches_B":(c["answer"]==b["answer"] and c["trace"]==b["trace"]),
            "C_matches_D":(c["answer"]==d["answer"] and c["trace"]==d["trace"]),
            "C_certified_not_original":c["verdict"]=="correct" and e["verdict"]!="correct",
            "original_certified_not_C":e["verdict"]=="correct" and c["verdict"]!="correct",
        })
    # HINDSIGHT: best per subtype on the test data (for diagnostic ONLY).
    grouped=defaultdict(list)
    for t in holdout:grouped[t["kind"]].append(t)
    hindsight={}
    for kind,group in sorted(grouped.items()):
        order=best_fixed(group)
        calls=0; successes=0
        for t in group:
            result,trace=execute_fixed(t,order)
            successes+=result is not None
            calls+=len(trace)
        hindsight[kind]={"order":list(order),"certificates":successes,
                         "attempts":calls}
    return {
        "status":"POST_RESULT_DIAGNOSTIC_NOT_A_PRECOMMITTED_ARM",
        "max_certifiable_by_any_single_method":has_certificate,
        "C_abstentions":unsolved,
        "C_vs_B_all_24_paired_identical":all(r["C_matches_B"] for r in paired),
        "C_vs_D_all_24_paired_identical":all(r["C_matches_D"] for r in paired),
        "C_improved_cases_vs_E":[r["case"] for r in paired if r["C_certified_not_original"]],
        "E_improved_cases_vs_C":[r["case"] for r in paired if r["original_certified_not_C"]],
        "retrospective_best_subtype_orders":hindsight,
        "retrospective_total_certified":sum(r["certificates"] for r in hindsight.values()),
        "retrospective_total_attempts":sum(r["attempts"] for r in hindsight.values()),
        "no_automatic_claim_of_generalization":True,
    }


if __name__=="__main__":
    print(json.dumps(audit(),indent=2,sort_keys=True,ensure_ascii=False))
