"""Independent post-run audit of OMEGA-ATOM-08: no model inference.

Reconstructs edge membership from raw graph edges and the complete 3-bit
truth table without calling the experiment's scorer. All manifests and
raw-response digests are checked; all 32 calls remain in the denominator.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from omega_hybrid_atom08 import (
    ARMS, FIELDS, MODEL_SHA, PROTOCOL, SYSTEM, make_manifest,
    prompt_for_graph, prompt_for_logic,
)

def canonical(x):
    return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)

def digest(x):
    return sha256(x.encode()).hexdigest()


def read_bits(raw):
    try:o=json.loads(raw.strip())
    except (AttributeError,TypeError,ValueError):return None
    return o if isinstance(o,dict) and set(o)==set(FIELDS) and all(
        type(o[k]) is bool for k in FIELDS) else None

def read_implication(raw):
    try:o=json.loads(raw.strip())
    except (AttributeError,TypeError,ValueError):return None
    return o["violates"] if isinstance(o,dict) and set(o)=={"violates"} and (
        type(o["violates"]) is bool) else None

def audit(report,question_manifest,oracle_manifest):
    def fail(reason):
        return {"status":"BLOCKED","reason":reason,"new_skills_certified":0}
    q,a=make_manifest()
    if question_manifest!=q or oracle_manifest!=a:
        return fail("MANIFEST_CHANGED")
    if not isinstance(report,dict) or report.get("protocol")!=PROTOCOL:
        return fail("PROTOCOL_MISMATCH")
    if report.get("input_manifest_sha256")!=digest(canonical(q)) or (
        report.get("oracle_manifest_sha256")!=digest(canonical(a))):
        return fail("MANIFEST_HASH_MISMATCH")
    if report.get("model_sha256_expected")!=MODEL_SHA or report.get("model_weights_updated") is not False:
        return fail("MODEL_VERSION_OR_WEIGHTS_MISMATCH")
    if report.get("status") not in (
        "FOUNDATIONAL_GATES_PASS_DESCRIPTIVE_ONLY","FOUNDATIONAL_GATE_NOT_PASSED") or (
        report.get("calls")!=32 or len(report.get("graph_trials",[]))!=12 or
        len(report.get("logic_trials",[]))!=8):
        return fail("MODEL_RUN_INCOMPLETE")
    recomputed={arm:{"n":12,"all_three_correct":0,"individual_bits_correct":0,
        "invalid":0,"prompt_tokens":0,"completion_tokens":0} for arm in ARMS}
    recomputed["LOGIC"]={"n":8,"correct":0,"positive_case_correct":False,
        "invalid":0,"prompt_tokens":0,"completion_tokens":0}
    positive_seen=False
    for graph,row,truth in zip(q["graphs"],report["graph_trials"],a["graph_answers"]):
        if graph["id"]!=row.get("id") or graph["id"]!=truth["id"] or set(row.get("arms",{}))!=set(ARMS):
            return fail("GRAPH_IDS_OR_ARMS_TAMPERED")
        x,y,z=graph["triple"]
        edges={tuple(e) for e in graph["edges"]}
        actual={"xy":(x,y) in edges,"yz":(y,z) in edges,"xz":(x,z) in edges}
        if actual!=truth["bits"]:
            return fail("ATOM_ORACLE_INCONSISTENCY")
        for arm in ARMS:
            o=row["arms"][arm]
            raw=o.get("raw")
            if not isinstance(raw,str) or digest(raw)!=o.get("raw_sha256"):
                return fail("RAW_REPLY_MODIFIED")
            prompt=[{"role":"system","content":SYSTEM},
                    {"role":"user","content":prompt_for_graph(graph,arm)}]
            if digest(canonical(prompt))!=o.get("prompt_sha256"):
                return fail("MODEL_PROMPT_MODIFIED")
            usage=o.get("usage",{})
            p=usage.get("prompt_tokens");c=usage.get("completion_tokens")
            if type(p) is not int or p<=0 or type(c) is not int or c<0:
                return fail("MISSING_TOKEN_USAGE")
            observed=read_bits(raw)
            score={"valid_format":observed is not None,
                "all_three":observed==actual if observed is not None else False,
                "individual_bits":sum(observed[k]==actual[k] for k in FIELDS)
                    if observed is not None else 0}
            if score!=o.get("score"):
                return fail("GRAPH_SCORE_ALTERED")
            m=recomputed[arm]
            m["all_three_correct"]+=int(score["all_three"])
            m["individual_bits_correct"]+=score["individual_bits"]
            m["invalid"]+=int(not score["valid_format"])
            m["prompt_tokens"]+=p;m["completion_tokens"]+=c
    for case,row,answer in zip(q["truth_table_queries"],report["logic_trials"],a["truth_table_answers"]):
        if case["id"]!=row.get("id") or case["id"]!=answer["id"]:
            return fail("LOGIC_CASE_ORDER_CHANGED")
        actual=case["bits"]["xy"] and case["bits"]["yz"] and not case["bits"]["xz"]
        if actual!=answer["violates"]:
            return fail("LOGIC_ORACLE_INCONSISTENCY")
        o=row.get("output",{})
        raw=o.get("raw")
        if not isinstance(raw,str) or digest(raw)!=o.get("raw_sha256"):
            return fail("LOGIC_RAW_ALTERED")
        prompt=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt_for_logic(case)}]
        if digest(canonical(prompt))!=o.get("prompt_sha256"):
            return fail("LOGIC_PROMPT_ALTERED")
        usage=o.get("usage",{})
        p=usage.get("prompt_tokens");c=usage.get("completion_tokens")
        if type(p) is not int or p<=0 or type(c) is not int or c<0:
            return fail("LOGIC_COST_MISSING")
        pred=read_implication(raw)
        score={"valid_format":pred is not None,
               "correct":pred==actual if pred is not None else False}
        if score!=o.get("score"):
            return fail("LOGIC_SCORE_TAMPERED")
        m=recomputed["LOGIC"]
        m["correct"]+=int(score["correct"])
        m["invalid"]+=int(not score["valid_format"])
        m["prompt_tokens"]+=p;m["completion_tokens"]+=c
        if actual:
            positive_seen=True
            m["positive_case_correct"]=bool(score["correct"])
    if not positive_seen:
        return fail("NO_POSITIVE_TRUTH_TABLE_TEST")
    recorded=report.get("metrics",{})
    for arm in (*ARMS,"LOGIC"):
        for key,val in recomputed[arm].items():
            if recorded.get(arm,{}).get(key)!=val:
                return fail("AGGREGATE_CORRUPTED_"+arm+"_"+key)
    reading=all(recomputed[arm]["all_three_correct"]>=10
            and recomputed[arm]["invalid"]==0 for arm in ARMS)
    logic=recomputed["LOGIC"]["correct"]==8 and recomputed["LOGIC"]["invalid"]==0
    if report.get("reading_gate")!=reading or report.get("logic_gate")!=logic:
        return fail("GATE_STATUS_FALSIFIED")
    desired="FOUNDATIONAL_GATES_PASS_DESCRIPTIVE_ONLY" if (
        reading and logic) else "FOUNDATIONAL_GATE_NOT_PASSED"
    if report["status"]!=desired:
        return fail("EPISTEMIC_STATUS_FALSIFIED")
    return {"status":"EXTERNAL_ATOM08_AUDIT_PASSED",
            "metrics":recomputed,
            "reading_gate":reading,"logic_gate":logic,
            "prompt_representation_has_uncontrolled_length":True,
            "reported_new_model_skills":0,"weights_trained":False}


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--folder",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    get=lambda name:json.loads((args.folder/name).read_text(encoding="utf-8"))
    result=audit(get("report.json"),get("model_inputs.json"),get("oracle_only.json"))
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":result["status"],"reason":result.get("reason")}))
    if result["status"]!="EXTERNAL_ATOM08_AUDIT_PASSED":
        raise SystemExit("EVIDENCE_INCOMPLETE_OR_TAMPERED")
if __name__=="__main__": main()
