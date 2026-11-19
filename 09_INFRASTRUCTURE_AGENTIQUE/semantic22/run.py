#!/usr/bin/env python3
"""SEM22 realistic integration: model proposes; exact checker rejects false claims.

Frozen holdout gold is imported only here, NOT by checker.py.
Source text and Git hash are the only inputs to the verifier.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"reader_benchmark21"))
sys.path.insert(0,str(HERE.parent/"reader_benchmark19"))
sys.path.insert(0,str(HERE.parent/"reader_bridge14"))
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
from checker import verify_source, select_verified
from benchmark import source_gate, metric, aggregate
from experiment import call_model
from read import safe_read, packetize, verify_packets
from selector import parse_selection

SPEC=HERE/"CASE_SPEC.json"
FROZEN=HERE/"FROZEN_ORACLE.json"
MODEL_SHA={
    "0p5b":"74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    "3b":"626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}
LLAMA_SHA="5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
N=24
FIRST_LINE=9
LAST_LINE=15
MAX_SELECT=3
CANDIDATE_LABELS=tuple(range(1,8))


def candidate_map()->dict[int,int]:
    return {idx:idx+8 for idx in CANDIDATE_LABELS}


def source_tasks()->list[dict]:
    metadata=json.loads(FROZEN.read_text(encoding="utf8"))
    cases=json.loads(SPEC.read_text(encoding="utf8"))["cases"]
    if metadata["status"]!="FROZEN_BEFORE_ANY_LLM_INFERENCE" or len(metadata["docs"])!=N or len(cases)!=N:
        raise ValueError("HOLDOUT_MANIFEST_NOT_FROZEN")
    byid={c["id"]:c for c in cases}
    if len(byid)!=N or len({d["id"] for d in metadata["docs"]})!=N:
        raise ValueError("DUPLICATE_EXPERIMENT_ID")
    result=[]
    for ref in metadata["docs"]:
        spec=byid[ref["id"]]
        source=ROOT/ref["path"]
        if source.resolve()!=(HERE/"cases"/(ref["id"]+".md")).resolve():
            raise ValueError("SOURCE_PATH_DRIFT")
        raw=safe_read(source,ref["blob"])
        checked=verify_source(raw,expected_blob=ref["blob"],source_path=ref["path"])
        if checked["status"]!="EVALUATED_FINITE_SCOPE" or not checked["all_claims_checked"]:
            raise ValueError("UNSUPPORTED_SYNTAX_IN_FROZEN_HOLDOUT")
        if len(checked["results"])!=7 or [x["line"] for x in checked["results"]]!=list(range(9,16)):
            raise ValueError("SEMANTIC_CANDIDATE_COVERAGE_FAILURE")
        # This agreement is an AUDIT only. No labels are fed to checker.
        checked_true=[x["line"] for x in checked["results"] if x["verdict"]=="TRUE"]
        if checked_true!=ref["oracle_true_lines"]:
            raise ValueError("INDEPENDENT_CHECKER_DISAGREES_WITH_PRIOR_GOLD")
        lines=raw.decode("utf8").splitlines()
        inv=packetize(raw,str(source))
        if verify_packets(raw,inv):
            raise ValueError("SOURCE_PACKET_VERIFICATION_FAILED")
        lookup={line:p for p in inv["packets"]
                for line in range(p["start_line"],p["end_line"]+1)}
        candidates=[]
        for n in range(FIRST_LINE,LAST_LINE+1):
            p=lookup.get(n)
            if p is None or p["section_path"][-1]!="Énoncé":
                raise ValueError("MISSING_CLAIM_PACKET")
            candidates.append({"line":n,"source_text":lines[n-1],
                               "packet_id":p["packet_id"],"section":p["section_path"]})
        task={"ref":ref,"case":spec,"raw":raw,"source":source,
              "candidates":candidates,"definition":lines[4],
              "checked":checked}
        for line in range(FIRST_LINE,LAST_LINE+1):
            source_gate(task,[line],"semantic22-input-source-check")
        result.append(task)
    return result


def prompt(t:dict)->list[dict]:
    options=[{"id":i,"proposition":c["source_text"]}
             for i,c in enumerate(t["candidates"],start=1)]
    return [
        {"role":"system","content":"Évalue des propositions mathématiques sur une fonction finie. Réponds uniquement avec des identifiants proposés ou NONE."},
        {"role":"user","content":(
            "Détermine jusqu'à trois propositions mathématiquement VRAIES "
            "pour la fonction donnée. Choisis uniquement parmi les IDENTIFIANTS "
            "1,2,3,4,5,6,7. Les identifiants sont des étiquettes et non des valeurs. "
            "Si tu ne sélectionnes aucune proposition, réponds NONE. "
            "Réponds seulement avec les numéros distincts, séparés de virgules ; "
            "pas de phrase, JSON ni Markdown.\n"
            "DÉFINITION :\n"+t["definition"]+"\nPROPOSITIONS :\n"+
            json.dumps(options,ensure_ascii=False)
        )},
    ]


def model_row(t:dict,label:str,caller=call_model)->dict:
    dialog=prompt(t)
    response=caller(dialog)
    if response.get("finish_reason")=="length":
        raise ValueError("TRUNCATED_MODEL_REPLY")
    raw_reply=response["raw_reply"]
    ids,reason=parse_selection(raw_reply,set(CANDIDATE_LABELS))
    selected=[candidate_map()[x] for x in ids] if reason is None else []
    if len(selected)>MAX_SELECT or len(selected)!=len(set(selected)):
        raise ValueError("UNEXPECTED_MODEL_SELECTION")
    if reason is None:
        source_gate(t,selected,"semantic22-model-"+label)
    filtering=select_verified(t["checked"],selected)
    if filtering["selected_true_lines"]:
        source_gate(t,filtering["selected_true_lines"],"semantic22-verified-filter")
    gold=t["ref"]["oracle_true_lines"]
    return {
        "id":t["ref"]["id"], "family":t["case"]["kind"],
        "source_blob":t["ref"]["blob"],
        "source_path":t["ref"]["path"],
        "raw_reply":raw_reply,
        "selection_status":"VALID" if reason is None else "REJECTED",
        "parse_error":reason,
        "abstention":reason is None and not selected,
        "chosen_ordinal_ids":ids,
        "raw_selected_source_lines":selected,
        "filtered_true_source_lines":filtering["selected_true_lines"],
        "rejected_by_checker":filtering["suppressed"],
        "frozen_gold_lines_for_posthoc_scoring_only":gold,
        "model_only_metrics":metric(selected,gold),
        "model_plus_verifier_metrics":metric(filtering["selected_true_lines"],gold),
        "independent_checker_status":t["checked"]["status"],
        "messages":dialog,
        "inference":response,
        "automatic_certifications":0,"horn_rules":[],
    }


def reference_run(tasks:list[dict])->dict:
    records=[];mechanical=[]
    for t in tasks:
        checked=t["checked"]
        all_true=[x["line"] for x in checked["results"] if x["verdict"]=="TRUE"]
        for start in range(0,len(all_true),3):
            source_gate(t,all_true[start:start+3],"semantic22-exact-full-scan")
        gold=t["ref"]["oracle_true_lines"]
        records.append({
            "id":t["ref"]["id"],"family":t["case"]["kind"],
            "source_blob":t["ref"]["blob"],
            "n_checked":len(checked["results"]),
            "n_true":len(all_true),
            "n_false":sum(x["verdict"]=="FALSE" for x in checked["results"]),
            "n_indeterminate":sum(x["verdict"]=="INDETERMINATE" for x in checked["results"]),
            "checked_results":checked["results"],
            "exact_full_scan_metrics":metric(all_true,gold),
            "reference_truth_source":"GOLD_FROZEN_BEFORE_INDEPENDENT_VERIFIER",
            "reference_gold_lines":gold,
        })
        mech=[9,10,11]
        source_gate(t,mech,"semantic22-mechanical-first3")
        mechanical.append({
            "id":t["ref"]["id"],
            "metrics":metric(mech,gold),
        })
    return {
        "status":"EXACT_FULL_SCAN_AUDITED",
        "source_type":"SYNTHETIC_AUTHOR_GENERATED_NOT_HUMAN_ANNOTATED",
        "n_cases":len(records),
        "n_claims":sum(r["n_checked"] for r in records),
        "n_indeterminate":sum(r["n_indeterminate"] for r in records),
        "n_true":sum(r["n_true"] for r in records),
        "verified_complete_micro":aggregate([{"metrics":r["exact_full_scan_metrics"]} for r in records]),
        "first3_control_micro":aggregate(mechanical),
        "records":records,
        "automatic_certifications":0,"horn_rules":[],
    }


def totals(rows:list[dict],key:str)->dict:
    vals=[{"metrics":r[key]} for r in rows]
    return aggregate(vals)


def real_run(model:str)->dict:
    if model not in MODEL_SHA:
        raise ValueError("MODEL_NOT_AUTHORIZED")
    tasks=source_tasks()
    start=time.perf_counter()
    rows=[]
    for t in tasks:
        row=model_row(t,model)
        rows.append(row)
        print("SEM22",model,row["id"],row["selection_status"],
              repr(row["raw_reply"]),row["raw_selected_source_lines"],
              row["filtered_true_source_lines"],flush=True)
    return {
        "status":"REAL_MODEL_COMPLETED",
        "model":model,"model_sha256":MODEL_SHA[model],
        "llama_cpp_sha":LLAMA_SHA,
        "n_cases":len(rows),"rows":rows,
        "model_only_micro":totals(rows,"model_only_metrics"),
        "with_exact_filter_micro":totals(rows,"model_plus_verifier_metrics"),
        "by_family":{
            family:{
                "model_only":totals([r for r in rows if r["family"]==family],"model_only_metrics"),
                "filtered":totals([r for r in rows if r["family"]==family],"model_plus_verifier_metrics"),
            } for family in ("affine","quadratic")},
        "model_rejections":sum(r["selection_status"]=="REJECTED" for r in rows),
        "model_abstentions":sum(r["abstention"] for r in rows),
        "independently_filtered_false":sum(len(r["rejected_by_checker"]) for r in rows),
        "time_model_inference_only":round(sum(r["inference"]["seconds"] for r in rows),3),
        "time_full_run":round(time.perf_counter()-start,3),
        "automated_theorems":0,"promotions":0,"horn_rules":[],
    }


def compare(reference:Path,small:Path,large:Path)->dict:
    a=json.loads(reference.read_text(encoding="utf8"))
    b=json.loads(small.read_text(encoding="utf8"))
    c=json.loads(large.read_text(encoding="utf8"))
    if (a["status"]!="EXACT_FULL_SCAN_AUDITED" or a["n_cases"]!=24 or a["n_claims"]!=168
        or any(x["status"]!="REAL_MODEL_COMPLETED" or x["n_cases"]!=24 for x in (b,c))
        or [x["id"] for x in b["rows"]] != [x["id"] for x in c["rows"]]):
        raise ValueError("SEM22_INCOMPLETE_BENCHMARK")
    if (b["model"]!="0p5b" or c["model"]!="3b"
        or b["model_sha256"]!=MODEL_SHA["0p5b"] or c["model_sha256"]!=MODEL_SHA["3b"]):
        raise ValueError("MODEL_OR_MODEL_HASH_MISMATCH")
    if ([x["source_blob"] for x in b["rows"]] !=
        [x["source_blob"] for x in c["rows"]]):
        raise ValueError("MODEL_CORPORA_DIFFER")
    return {
        "status":"SEM22_COMPLETE_COMPARISON",
        "cases":24, "claims":168,
        "model_calls":48,
        "exact_full_scan":a["verified_complete_micro"],
        "mechanical_first3":a["first3_control_micro"],
        "models":{
            x["model"]:{
                "alone":x["model_only_micro"],
                "filtered":x["with_exact_filter_micro"],
                "fp_suppressed":x["independently_filtered_false"],
                "rejections":x["model_rejections"],
                "abstentions":x["model_abstentions"],
                "inference_seconds":x["time_model_inference_only"],
            } for x in (b,c)
        },
        "pre_registered_local_success":(
            a["n_indeterminate"]==0
            and a["verified_complete_micro"]["fp"]==0
            and a["verified_complete_micro"]["fn"]==0
            and any(x["independently_filtered_false"]>0 for x in (b,c))
        ),
        "semantic_scope":"ONLY_SYNTHETIC_FINITE_MODULAR_FUNCTION_LANGUAGE",
        "real_papers_or_general_intelligence":"NOT_TESTED",
        "model_weights_changed":False,
        "formal_certifications":0,"horn_rules":[],
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",required=True,choices=("control","model","compare"))
    parser.add_argument("--model",choices=("0p5b","3b"))
    parser.add_argument("--reference",type=Path)
    parser.add_argument("--small",type=Path)
    parser.add_argument("--large",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    failed=False
    try:
        if args.mode=="control":
            result=reference_run(source_tasks())
        elif args.mode=="model":
            result=real_run(args.model)
        else:
            if not (args.reference and args.small and args.large):
                raise ValueError("REQUIRED_COMPARISON_FILES_MISSING")
            result=compare(args.reference,args.small,args.large)
    except Exception:
        result={"status":"FAILURE_NOT_SCIENTIFIC_RESULT",
                "exception":traceback.format_exc()}
        failed=True
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("SEM22",args.mode,result["status"],flush=True)
    if failed:
        sys.exit(1)


if __name__=="__main__":
    main()
