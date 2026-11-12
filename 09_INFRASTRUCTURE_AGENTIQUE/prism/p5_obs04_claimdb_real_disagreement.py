"""P5-OBS-04: externally logged actual GPT-5-mini with/without SQL on ClaimDB.

Public secondary analysis. The gold labels are from one benchmark provider.
Two model configurations are NOT independent providers or observed proof
chains. Never substitute synthetic model predictions for missing real logs.

Exact paired join by ClaimDB claim_id; abstention is distinct from NEI.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import json
import math

PROTOCOL="P5-OBS-04"
STATUS="REAL_PAIRED_LLM_METHOD_DISAGREEMENT_SINGLE_BENCHMARK_PROVIDER"
SOURCE_COMMIT="e06c3a22cc14a8ef6858bb5d40bca7925241b98d"
FILES={
    "gold":("final-benchmark/test-public.jsonl",
            "b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810"),
    "sql":("experiments/public/gpt-5-mini.jsonl",
           "e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100"),
    "no_tools":("experiments/public/no_tools/gpt-5-mini.jsonl",
                "552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6"),
}
LABELS=("ENTAILED","CONTRADICTED","NOT ENOUGH INFO")
ABSTAIN="ABSTAIN"
POLICIES=("no_tools","sql_tools","agree_or_abstain",
          "prefer_sql_when_disagree","sql_trace_gate",
          "oracle_after_disagreement","reject_all")

def read_rows(path,mode,verify_sha=True):
    if mode not in FILES:raise ValueError("unknown source")
    p=Path(path)
    raw=p.read_bytes()
    if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("UNAVAILABLE_SOURCE_LFS_POINTER")
    digest=sha256(raw).hexdigest()
    if verify_sha and digest!=FILES[mode][1]:
        raise ValueError("DATA_SOURCE_SHA256_MISMATCH_"+mode)
    rows=[]
    for line_num,line in enumerate(raw.decode("utf-8").splitlines(),1):
        if not line.strip():continue
        x=json.loads(line)
        if not isinstance(x,dict) or type(x.get("claim_id")) is not int:
            raise ValueError(f"unjoinable claim id {mode} line {line_num}")
        rows.append(x)
    ids=[r["claim_id"] for r in rows]
    if len(ids)!=len(set(ids)):
        raise ValueError("DUPLICATE_CLAIM_ID_"+mode)
    return rows,{"path":FILES[mode][0],"sha256":digest,"bytes":len(raw),"count":len(rows)}

def label_strict(x):
    return x if type(x) is str and x in LABELS else None

def tool_events(row):
    """Count visibly recorded function calls; never claim result is valid proof."""
    events=row.get("to_input_list")
    if not isinstance(events,list):
        return {"logged_calls":0,"logged_outputs":0,"trace_available":False}
    def types_of(x):
        if not isinstance(x,dict):return set()
        return {x.get("type")} if type(x.get("type")) is str else set()
    types=[t for x in events for t in types_of(x)]
    return {"logged_calls":sum(t in ("function_call","tool_call") for t in types),
            "logged_outputs":sum(t in ("function_call_output","tool_result") for t in types),
            "trace_available":True}

def gain(verdict,gold):
    if verdict==ABSTAIN:return .05
    return 1 if verdict==gold else -2

def evaluate(gold,sql,no_tools):
    g={x["claim_id"]:x for x in gold}
    s={x["claim_id"]:x for x in sql}
    n={x["claim_id"]:x for x in no_tools}
    if len(g)!=1000 or len(s)==0 or len(n)==0:
        raise ValueError("INCOMPLETE_REAL_SOURCE_ROWS")
    joined=sorted(set(g)&set(s)&set(n))
    if not joined:raise ValueError("INCOMPLETE_UNJOINABLE_MODEL_TRACES")
    missing={
        "gold_without_sql":len(set(g)-set(s)),
        "gold_without_no_tools":len(set(g)-set(n)),
        "sql_outside_gold":len(set(s)-set(g)),
        "no_tools_outside_gold":len(set(n)-set(g)),
    }
    scores={k:[] for k in POLICIES}
    details=[]
    errors=Counter()
    by_gold=defaultdict(lambda: Counter())
    by_db=defaultdict(lambda: Counter())
    for key in joined:
        row=g[key]
        truth=label_strict(row.get("label"))
        a=label_strict(n[key].get("verdict"))
        b=label_strict(s[key].get("verdict"))
        if truth is None:raise ValueError("INVALID_BENCHMARK_LABEL")
        if a is None or b is None:
            errors["invalid_or_missing_verdict"]+=1
            continue
        evidence=tool_events(s[key])
        no_trace=tool_events(n[key])
        if (no_trace["logged_calls"]>0 or no_trace["logged_outputs"]>0):
            errors["no_tools_trace_contains_tool_event"]+=1
        if evidence["logged_outputs"]>evidence["logged_calls"]:
            errors["sql_trace_has_more_outputs_than_calls"]+=1
        same=a==b
        decisions={
            "no_tools":a,
            "sql_tools":b,
            "agree_or_abstain":b if same else ABSTAIN,
            "prefer_sql_when_disagree":b,
            "sql_trace_gate":b if evidence["logged_outputs"]>0 else ABSTAIN,
            "oracle_after_disagreement":b if same else (
                a if a==truth else b if b==truth else ABSTAIN),
            "reject_all":ABSTAIN,
        }
        for name,decision in decisions.items():
            scores[name].append({
                "decision":decision,"correct":decision==truth,
                "published":decision!=ABSTAIN,
                "wrong":decision!=ABSTAIN and decision!=truth,
                "utility":gain(decision,truth),
            })
        by_gold[truth]["total"]+=1
        by_gold[truth]["disagree"]+=int(not same)
        by_db[row.get("db_name") or "UNKNOWN"]["total"]+=1
        by_db[row.get("db_name") or "UNKNOWN"]["disagree"]+=int(not same)
        errors["disagreements"]+=int(not same)
        errors["both_right"]+=int(same and b==truth)
        errors["both_wrong_same"]+=int(same and b!=truth)
        errors["sql_right_no_tools_wrong"]+=int(b==truth and a!=truth)
        errors["no_tools_right_sql_wrong"]+=int(a==truth and b!=truth)
        errors["both_wrong_different"]+=int(b!=truth and a!=truth and not same)
        errors["sql_logged_calls"]+=evidence["logged_calls"]
        errors["sql_logged_outputs"]+=evidence["logged_outputs"]
        errors["sql_no_output_event"]+=int(evidence["logged_outputs"]==0)
        details.append({
            "claim_id":key,
            "db_name":row.get("db_name"),
            "gold":truth,
            "no_tools":a,
            "sql_tools":b,
            "disagrees":not same,
            "logged_sql_tool_calls":evidence["logged_calls"],
            "logged_sql_tool_outputs":evidence["logged_outputs"],
            "trace_available":evidence["trace_available"],
            "source_provenance_group":"claimdb/claimdb",
        })
    valid=len(details)
    if not valid:raise ValueError("INCOMPLETE_NO_VALID_PAIRED_VERDICTS")
    result={}
    for name,records in scores.items():
        published=sum(x["published"] for x in records)
        correct=sum(x["correct"] for x in records if x["published"])
        wrong=sum(x["wrong"] for x in records)
        abstained=len(records)-published
        result[name]={
            "n":len(records),
            "published":published,
            "abstained":abstained,
            "coverage":round(published/len(records),6),
            "correct_published":correct,
            "wrong_published":wrong,
            "risk_on_published":round(wrong/published,6) if published else None,
            "overall_correct_on_all":round(correct/len(records),6),
            "total_utility":round(sum(x["utility"] for x in records),6),
        }
    assert result["prefer_sql_when_disagree"]==result["sql_tools"]
    assert result["reject_all"]["published"]==0
    assert result["agree_or_abstain"]["published"]==valid-errors["disagreements"]
    if missing["gold_without_sql"] or missing["gold_without_no_tools"]:
        status="INCOMPLETE_PAIRED_COVERAGE_PARTIAL"
    else:
        status=STATUS
    return {
        "protocol":PROTOCOL,"status":status,
        "source_commit":SOURCE_COMMIT,
        "gold_record_count":len(g),"sql_record_count":len(s),
        "no_tools_record_count":len(n),
        "paired_ids":len(joined),"valid_paired_verdicts":valid,
        "missing_or_extra_ids":missing,
        "label_distribution":dict(Counter(g[k]["label"] for k in g)),
        "outcome_counts":dict(errors),
        "by_truth_label":{k:dict(v) for k,v in sorted(by_gold.items())},
        "by_database":{k:dict(v) for k,v in sorted(by_db.items())},
        "model_policies":result,
        "case_audit":details,
        "claims_text_redistributed":False,
        "sql_tool_event_is_not_verified_sql_correctness":True,
        "same_model_family_not_independent_provider":True,
        "gold_database_not_recomputed":True,
        "new_model_inferences":0,
        "limitations":[
            "Two genuine historical GPT-5-mini experimental modes, not two independent providers",
            "One benchmark label source; database evidence and SQL query semantics not re-executed",
            "Logs are public and nonblind; source experiment prompts/settings may differ",
            "Agree-or-abstain is a classical filter, not a novel Omega adaptive policy",
            "Tool-output event does not certify correct SQL computation or relevant evidence",
            "Gold is used only after decisions to compute scores; oracle is nondeployable",
            "No SQL runtime cost or end-to-end latency comparison is justified",
            "ClaimDB public test cases are clustered by underlying databases",
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",type=Path,required=True)
    ap.add_argument("--output",type=Path)
    opts=ap.parse_args()
    root=opts.source_root
    data={}
    metadata={}
    for mode,(rel,digest) in FILES.items():
        data[mode],metadata[mode]=read_rows(root/rel,mode)
    report=evaluate(data["gold"],data["sql"],data["no_tools"])
    report["sources"]=metadata
    if opts.output:
        opts.output.parent.mkdir(parents=True,exist_ok=True)
        opts.output.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,
                          indent=2)+"\n",encoding="utf-8")
    print("P5_OBS04_REAL_METHOD_DISAGREEMENTS",json.dumps({
        "status":report["status"],
        "valid_paired_verdicts":report["valid_paired_verdicts"],
        "missing_or_extra_ids":report["missing_or_extra_ids"],
        "outcome_counts":report["outcome_counts"],
        "policies":report["model_policies"],
        "sources":report["sources"],
    },sort_keys=True,ensure_ascii=False))

if __name__=="__main__":
    main()
