#!/usr/bin/env python3
"""Two POST-HOC finite countermodels to Qwen hypotheses on FOLIO 062 and 064.

All semantics from English to predicates have been transcribed manually for
this audit. This is a REAL executable counterexample test *under those clauses*,
not an automatic natural language proof or a certified scientific theorem.
"""
import json
from pathlib import Path
import proposer

def pred(model, individual, name):
    return bool(model[individual].get(name,False))

def satisfies(model, clause):
    kind=clause["kind"]
    people=tuple(model)
    if kind=="fact":
        return pred(model,clause["individual"],clause["predicate"])
    if kind=="forall_imp":
        return all(not all(pred(model,x,k) for k in clause["if_all"]) or
                   any(pred(model,x,k) for k in clause["then_any"])
                   for x in people)
    if kind=="exists_and":
        return any(all(pred(model,x,k) for k in clause["predicates"]) for x in people)
    if kind=="forall_disjoint":
        return all(not (pred(model,x,clause["left"]) and
                        pred(model,x,clause["right"])) for x in people)
    if kind=="person_imp":
        x=clause["individual"]
        return not all(pred(model,x,k) for k in clause["if_all"]) or (
            any(pred(model,x,k) for k in clause["then_any"]))
    raise ValueError("unsupported explicit audit clause kind: "+str(kind))

def case62():
    # Manually transcribed from the original unmodified English FOLIO premises.
    return {
        "row":62,
        "candidate_id":"333202f3d7e3f4431e64c5c8d1931bdb",
        "claim":"F1(Mike)",
        "claim_must_be":True,
        "claim_actual":False,
        "witness":{
            "Mike":{"student":True,"j1":True,"f1":False,
                    "wants_work":True,"cpt":True,"opt":False}
        },
        "clauses":[
            {"source_index":0,"kind":"forall_imp",
             "if_all":["student"],"then_any":["f1","j1"]},
            {"source_index":1,"kind":"forall_imp",
             "if_all":["student","f1","wants_work"],"then_any":["cpt","opt"]},
            {"source_index":2,"kind":"fact","individual":"Mike","predicate":"student"},
            {"source_index":3,"kind":"person_imp","individual":"Mike",
             "if_all":["wants_work"],"then_any":["cpt"]}
        ],
        "check":{"individual":"Mike","predicate":"f1","negative":False}
    }

def case64():
    # Existence of one cow-pet does not imply that every pet is a cow.
    return {
        "row":64,
        "candidate_id":"990b22ec140acf9999e816f1cadd7ef4",
        "claim":"not Pet(Ted)",
        "claim_must_be":False,
        "claim_actual":False,
        "witness":{
            "Ted":{"alligator":True,"pet":True,"cow":False,
                   "bovine":False,"domesticated":False},
            "Another":{"alligator":False,"pet":True,"cow":True,
                       "bovine":True,"domesticated":True}
        },
        "clauses":[
            {"source_index":0,"kind":"forall_imp",
             "if_all":["cow"],"then_any":["bovine"]},
            {"source_index":1,"kind":"exists_and","predicates":["pet","cow"]},
            {"source_index":2,"kind":"forall_imp",
             "if_all":["bovine"],"then_any":["domesticated"]},
            {"source_index":3,"kind":"forall_disjoint",
             "left":"domesticated","right":"alligator"},
            {"source_index":4,"kind":"fact","individual":"Ted","predicate":"alligator"}
        ],
        "check":{"individual":"Ted","predicate":"pet","negative":True}
    }

def audit_case(spec,source_rows):
    source=source_rows[spec["row"]-61]
    premises=source["premises"]
    if len(premises)!=len(spec["clauses"]):
        raise ValueError("source/interpretation premise count disagrees")
    for i,clause in enumerate(spec["clauses"]):
        if clause.get("source_index")!=i:
            raise ValueError("source clause index must be exact")
    valid=[satisfies(spec["witness"],c) for c in spec["clauses"]]
    if not all(valid):
        raise ValueError("proposed countermodel violates at least one premise")
    target=spec["check"]
    truth=pred(spec["witness"],target["individual"],target["predicate"])
    candidate_truth=not truth if target["negative"] else truth
    if candidate_truth:
        raise ValueError("witness does not refute the model candidate")
    return {
        "external_row":spec["row"],
        "candidate_id":spec["candidate_id"],
        "candidate_claim":spec["claim"],
        "premises_count":len(premises),
        "all_manually_encoded_premises_satisfied":True,
        "each_clause_satisfied":valid,
        "candidate_claim_false_in_model":True,
        "finite_countermodel":spec["witness"],
        "reproduced_under":"MANUAL_TRANSLATION_NOT_SEMANTICALLY_CERTIFIED",
        "statistical_holdout":False,
        "posthoc":True,
        "source_texts_sha256":proposer.ledger.sha(premises),
        "independent_numeric_oracle":"FINITE_PREDICATE_MODEL_EVALUATOR",
        "scientific_status":"COUNTERMODEL_RELATIVE_TO_MANUAL_ENCODING"
    }

def run():
    source_rows=proposer.frozen_cases()
    return {
        "experiment":"OMEGA-11-POSTHOC-COUNTERMODEL",
        "original_generation_run":"https://github.com/Abrasax63/Omega-pub/actions/runs/44157203400",
        "original_generation_sha256":"c888847cc11661252bc93fad25d0c47f92860a3396813963bd5b16d21d7d965a",
        "status":"TWO_MODEL_PROPOSALS_REFUTED_UNDER_MANUAL_TRANSLATION",
        "semantic_tests_executed":2,
        "new_proven_scientific_theorems":0,
        "cases":[audit_case(s,source_rows) for s in (case62(),case64())]
    }

if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False,indent=2))
