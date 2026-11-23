"""Post-run independent audit of TRANSFER-05 (never used by the model).

For reflexive symmetric relations, transitivity is equivalent to every
connected component being a complete clique. This oracle uses a different
algorithm from concept_abstraction_lab.check_axioms. No model calls.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path

from incremental_math_library import canonical
from omega_hybrid_transfer05 import (
    ARMS, NODES, PROTOCOL, make_manifest, parse_answer,
)

def clique_oracle(raw_edges, nodes=NODES):
    """Independently check partition-clique criterion for equivalence."""
    if not isinstance(raw_edges,list):
        raise ValueError("MISSING_EDGE_LIST")
    edges=set()
    for p in raw_edges:
        if not isinstance(p,list) or len(p)!=2 or any(
                not isinstance(x,str) or x not in nodes for x in p):
            raise ValueError("INVALID_EDGE")
        tup=tuple(p)
        if tup in edges:
            raise ValueError("DUPLICATE_EDGE")
        edges.add(tup)
    if any((x,x) not in edges for x in nodes):
        return False
    if any((y,x) not in edges for x,y in edges):
        return False
    unvisited=set(nodes)
    while unvisited:
        seed=min(unvisited)
        component={seed}
        pending=[seed]
        unvisited.remove(seed)
        while pending:
            x=pending.pop()
            for y in nodes:
                if (x,y) in edges and y not in component:
                    component.add(y)
                    unvisited.discard(y)
                    pending.append(y)
        # Missing any directed edge inside a connected component means
        # that symmetric/reflexive relation is not transitive.
        if any((x,y) not in edges for x in component for y in component):
            return False
    return True


def audit(report, model_inputs, oracle_only):
    fail=lambda reason: {"status":"BLOCKED","reason":reason,
         "independently_certified_new_competence":False}
    if not isinstance(report,dict) or report.get("protocol")!=PROTOCOL:
        return fail("WRONG_PROTOCOL")
    if report.get("stage") not in ("POINTWISE_GAIN_OBSERVED",
                                  "PRE_REGISTERED_GAIN_NOT_OBSERVED",
                                  "INDETERMINATE_BUDGETS"):
        return fail("NO_COMPLETE_REAL_EXPERIMENT")
    expected_inputs,expected_answers=make_manifest()
    if model_inputs!=expected_inputs or oracle_only!=expected_answers:
        return fail("FROZEN_MANIFEST_MISMATCH")
    if sha256(canonical(model_inputs).encode()).hexdigest()!=report.get("manifest_sha256"):
        return fail("INPUT_MANIFEST_HASH_MISMATCH")
    if sha256(canonical(oracle_only).encode()).hexdigest()!=report.get("oracle_sha256"):
        return fail("ORACLE_MANIFEST_HASH_MISMATCH")
    if report.get("train_calls")!=2 or report.get("eval_calls")!=24:
        return fail("WRONG_NUMBER_OF_MODEL_CALLS")
    cases=model_inputs["cases"]
    answers=oracle_only["answers"]
    if len(cases)!=8 or len(answers)!=8 or len(report.get("tasks",[]))!=8:
        return fail("WRONG_TASK_COUNT")
    answer_map={x["id"]:x for x in answers}
    recomputed={arm:{"full":0,"boolean":0,"invalid":0,
                     "abstain":0,"prompt_tokens":0,"completion_tokens":0}
                for arm in ARMS}
    rows=[]
    for item,logged in zip(cases,report["tasks"]):
        ident=item["id"]
        if logged.get("id")!=ident or ident not in answer_map:
            return fail("ORDER_OR_ID_MISMATCH")
        truth=answer_map[ident]
        if clique_oracle(item["edges"]) != truth["holds"]:
            return fail("INDEPENDENT_CLIQUE_ORACLE_DISAGREES")
        if not isinstance(logged.get("arms"),dict) or set(logged["arms"])!=set(ARMS):
            return fail("MISSING_ARM")
        row={"id":ident,"truth":truth["holds"],"full":{}}
        for arm in ARMS:
            logged_reply=logged["arms"][arm]
            raw=logged_reply.get("raw")
            result=parse_answer(raw,truth)
            if result!=logged_reply.get("scoring"):
                return fail("SCORE_MISMATCH_"+arm)
            if not isinstance(raw,str) or sha256(raw.encode()).hexdigest()!=logged_reply.get("response_sha256"):
                return fail("RAW_REPLY_HASH_MISMATCH_"+arm)
            usage=logged_reply.get("usage",{})
            p,c=usage.get("prompt_tokens"),usage.get("completion_tokens")
            if type(p) is not int or p<=0 or type(c) is not int or c<0:
                return fail("TOKEN_METRICS_MISSING_"+arm)
            recomputed[arm]["full"]+=int(result["full_axioms_correct"])
            recomputed[arm]["boolean"]+=int(result["boolean_correct"])
            recomputed[arm]["invalid"]+=int(result["status"]=="INVALID_FORMAT")
            recomputed[arm]["abstain"]+=int(result["status"]=="ABSTAIN")
            recomputed[arm]["prompt_tokens"]+=p
            recomputed[arm]["completion_tokens"]+=c
            row["full"][arm]=bool(result["full_axioms_correct"])
        rows.append(row)
    for arm in ARMS:
        stats=report.get("results",{}).get("stats",{}).get(arm,{})
        for key,mapped in (("full_axioms_correct","full"),
                           ("boolean_correct","boolean"),
                           ("invalid","invalid"),("abstain","abstain"),
                           ("prompt_tokens","prompt_tokens"),
                           ("completion_tokens","completion_tokens")):
            if stats.get(key)!=recomputed[arm][mapped]:
                return fail("AGGREGATE_MISMATCH_"+arm+"_"+key)
    discordant={
       "W_better_than_G":sum(x["full"]["W"] and not x["full"]["G"] for x in rows),
       "G_better_than_W":sum(x["full"]["G"] and not x["full"]["W"] for x in rows),
       "W_better_than_D":sum(x["full"]["W"] and not x["full"]["D"] for x in rows),
       "D_better_than_W":sum(x["full"]["D"] and not x["full"]["W"] for x in rows),
    }
    train_cost={}
    for arm in ("G","W"):
        item=report.get("training",{}).get(arm,{})
        usage=item.get("usage",{})
        for key in ("prompt_tokens","completion_tokens"):
            if type(usage.get(key)) is not int or usage[key]<0:
                return fail("TRAINING_USAGE_NOT_VERIFIED")
        train_cost[arm]=usage
    full_cost={arm:{
       "prompt_tokens":recomputed[arm]["prompt_tokens"]+
            (train_cost[arm]["prompt_tokens"] if arm!="D" else 0),
       "completion_tokens":recomputed[arm]["completion_tokens"]+
            (train_cost[arm]["completion_tokens"] if arm!="D" else 0),
       "calls":9 if arm!="D" else 8}
       for arm in ARMS}
    return {"status":"POST_RUN_DOUBLE_ORACLE_AGREES_DESCRIPTIVE_ONLY",
            "n":8,"scores":recomputed,"discordant_pairs":discordant,
            "total_cost_including_rule_generation":full_cost,
            "note":"D uses one fewer model call: total compute is NOT arm-balanced",
            "model_weights_updated":False,
            "statistical_significance_claimed":False,
            "independently_certified_new_competence":False}


def main():
    import argparse
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--folder",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    load=lambda name:json.loads((args.folder/name).read_text(encoding="utf-8"))
    result=audit(load("report.json"),load("model_inputs.json"),load("oracle_only.json"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"reason":result.get("reason")}))
    if result["status"]!="POST_RUN_DOUBLE_ORACLE_AGREES_DESCRIPTIVE_ONLY":
        raise SystemExit("POST_RUN_AUDIT_BLOCKED")

if __name__=="__main__":
    main()
