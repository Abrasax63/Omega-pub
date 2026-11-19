#!/usr/bin/env python3
"""BENCH21: source-pinned paired free vs llama.cpp GBNF decoding experiment.

The grammar only constrains response shape. The mathematical oracle enumerates
a finite modular function independently of the language models.
No claim is ever promoted, certified or turned into a Horn rule.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import sys
import time
import traceback
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "reader_benchmark20"))
sys.path.insert(0, str(HERE.parent / "reader_benchmark19"))
sys.path.insert(0, str(HERE.parent / "reader_bridge14"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))

from paired import messages as ordinal_messages, one as source_checked_case, verify_exact_oracle
from benchmark import render, aggregate, metric, source_gate
from read import safe_read, packetize, verify_packets

FROZEN = HERE / "FROZEN_BENCHMARK.json"
SPEC = HERE / "CASE_SPEC.json"
MODEL_SHA = {
    "0p5b": "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    "3b": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}
LLAMA_SHA = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
ENDPOINT = "http://127.0.0.1:8091/v1/chat/completions"
INTERFACES = ("free", "gbnf")
NUM_CASES = 20
MAX_NEW_TOKENS = 64


def allowed_responses() -> tuple[str, ...]:
    """86 exact distinct strings, all 1-3 ordered non-repeating IDs, or NONE."""
    labels = ("1", "2", "3", "4", "5")
    choices = ("NONE",) + tuple(
        ",".join(items)
        for size in (1, 2, 3)
        for items in itertools.permutations(labels, size)
    )
    if len(choices) != 86 or len(set(choices)) != 86:
        raise AssertionError("INVALID_ENUMERATED_RESPONSE_LANGUAGE")
    return choices


def grammar_for_options(options: tuple[str, ...] | None = None) -> str:
    """Quote each complete phrase literally; no spaces, prose, repeats, unknown IDs."""
    opts = allowed_responses() if options is None else options
    if not opts or any(
        not isinstance(s, str) or not s or '"' in s or '\\' in s
        for s in opts
    ):
        raise ValueError("INVALID_GRAMMAR_TERMINAL")
    return "root ::= " + " | ".join(json.dumps(s) for s in opts) + "\n"


GRAMMAR = grammar_for_options()


def prepare() -> list[dict]:
    data = json.loads(SPEC.read_text(encoding="utf-8"))
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    if (data.get("status") != "FROZEN_BEFORE_MODEL_INFERENCE"
        or frozen.get("status") != "FROZEN_BEFORE_MODEL_INFERENCE"):
        raise ValueError("SOURCES_NOT_FROZEN_BEFORE_INFERENCE")
    cases, docs = data["cases"], frozen["docs"]
    if len(cases) != NUM_CASES or len(docs) != NUM_CASES:
        raise ValueError("EXPECTED_20_NEW_CASES")
    cases_by_id = {c["id"]: c for c in cases}
    if len(cases_by_id) != NUM_CASES or len({d["id"] for d in docs}) != NUM_CASES:
        raise ValueError("DUPLICATE_SOURCE_OR_CASE_ID")
    tasks = []
    for ref in docs:
        case = cases_by_id[ref["id"]]
        path = ROOT / ref["path"]
        expected_path = HERE / "cases" / (ref["id"] + ".md")
        if path.resolve() != expected_path.resolve():
            raise ValueError("SOURCE_OUTSIDE_FROZEN_COHORT")
        raw = safe_read(path, ref["blob"])
        if raw != render(case):
            raise ValueError("SOURCE_OR_PARAMETERS_TAMPERED")
        lines = raw.decode("utf-8").splitlines()
        if len(lines) != 13 or ref["candidate_lines"] != [9,10,11,12,13]:
            raise ValueError("SOURCE_LINE_LAYOUT_DRIFT")
        oracle = verify_exact_oracle(case)
        gold = [9+i for i,k in enumerate(case["order"]) if oracle[k]]
        if oracle != ref["truth_by_predicate"] or gold != ref["oracle_true_lines"]:
            raise ValueError("FROZEN_EXHAUSTIVE_ORACLE_DISAGREES")
        inv = packetize(raw, str(path))
        if verify_packets(raw, inv):
            raise ValueError("PACKET_PROVENANCE_FAILED")
        packet_at = {
            n:p for p in inv["packets"]
            for n in range(p["start_line"], p["end_line"] + 1)
        }
        candidates = []
        for n in ref["candidate_lines"]:
            p = packet_at.get(n)
            if not p or p["section_path"][-1] != "Énoncé":
                raise ValueError("CANDIDATE_NOT_IN_SOURCE_SECTION")
            phrase = lines[n-1].strip()
            if not phrase.startswith("Proposition : "):
                raise ValueError("CANDIDATE_STYLE_CHANGED")
            candidates.append({
                "line": n, "source_text": phrase,
                "packet_id": p["packet_id"], "section": p["section_path"]
            })
        task = {
            "ref": ref, "case": case, "raw": raw, "source": path,
            "candidates": candidates, "definition": lines[4],
        }
        for n in ref["candidate_lines"]:
            source_gate(task, [n], "bench21-provenance-precheck")
        tasks.append(task)
    return tasks


def call_model(dialogue: list[dict], *, grammar: str | None = None) -> dict:
    request_body = {
        "messages": dialogue, "max_tokens": MAX_NEW_TOKENS,
        "temperature": 0, "stream": False,
    }
    if grammar is not None:
        request_body["grammar"] = grammar
    request = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(request_body, ensure_ascii=False).encode("utf8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request, timeout=300) as response:
        body = json.loads(response.read(160000))
    duration = round(time.perf_counter() - start, 3)
    completion = body["choices"][0]
    reply = completion["message"]["content"]
    if not isinstance(reply, str):
        raise ValueError("NON_TEXT_MODEL_OUTPUT")
    return {
        "raw_reply": reply, "seconds": duration,
        "usage": body.get("usage"),
        "finish_reason": completion.get("finish_reason"),
        "server_model": body.get("model"),
        "grammar_field_in_request": grammar is not None,
    }


def probe_grammar() -> dict:
    """Fail-closed, real local model probe: only the word NONE can be generated."""
    forced = grammar_for_options(("NONE",))
    result = call_model(
        [
            {"role": "system", "content": "Return one valid option."},
            {"role": "user", "content": "Choose the digit 5. Answer 5."},
        ],
        grammar=forced
    )
    if result["raw_reply"] != "NONE":
        raise ValueError("REAL_GBNF_ENFORCEMENT_PROBE_FAILED")
    return result


def run_one(task: dict, label: str, mode: str, call=call_model) -> dict:
    if mode not in INTERFACES:
        raise ValueError("UNKNOWN_GENERATION_MODE")
    chats = ordinal_messages(task, "ordinal")
    request_grammar = GRAMMAR if mode == "gbnf" else None

    def invoke(ignored_messages):
        # Always use the very same dialogue for both arms, never a rewritten prompt.
        if ignored_messages != chats:
            raise ValueError("PROMPT_MISMATCH")
        return call(chats, grammar=request_grammar)

    result = source_checked_case(task, "ordinal", label + "-" + mode, call=invoke)
    # A run that returns without a complete generation is an execution failure,
    # not a successful low-scoring model. Keep all raw data in the report.
    if result["inference"]["finish_reason"] == "length":
        raise ValueError("MODEL_RESPONSE_TRUNCATED_BEFORE_STOP")
    result["decoding_mode"] = mode
    result["model_label"] = label
    result["grammar_sha256"] = __import__("hashlib").sha256(GRAMMAR.encode()).hexdigest() if mode == "gbnf" else None
    if mode == "gbnf" and (
        result["raw_output"] not in allowed_responses()
        or result["status"] != "VALID"
    ):
        raise ValueError("MODEL_OUTPUT_ESCAPED_GBNF_OR_GATE")
    return result


def source_controls(tasks: list[dict]) -> dict:
    variants = {
        "first3": lambda t: [9,10,11],
        "none": lambda t: [],
        "all5_coverage_only": lambda t: [9,10,11,12,13],
    }
    out={}
    for name, func in variants.items():
        rows=[]
        for task in tasks:
            chosen=func(task)
            if name != "all5_coverage_only":
                source_gate(task, chosen, "bench21-control-"+name)
            rows.append({
                "case": task["ref"]["id"],
                "family": task["case"]["kind"],
                "chosen": chosen,
                "metrics": metric(chosen, task["ref"]["oracle_true_lines"]),
            })
        out[name]={"rows":rows,"aggregate":aggregate(rows)}
    return out


def run_model(model: str) -> dict:
    tasks=prepare()
    if model not in MODEL_SHA:
        raise ValueError("UNKNOWN_MODEL_LABEL")
    result={
        "experiment":"OMEGA_BENCH21_GBNF_LOCAL_DECODING_PAIRED",
        "status":"STARTED", "model":model,
        "models_sha256":MODEL_SHA, "llama_cpp_sha":LLAMA_SHA,
        "n_cases":NUM_CASES,
        "reference_kind":"EXACT_SYNTHETIC_FINITE_FUNCTIONS_NOT_HUMAN_ANNOTATED",
        "third_party_paid_api_calls":0,
        "automatic_certifications":0, "horn_rules":0,
        "grammar_text":GRAMMAR, "grammar_allowed_responses":len(allowed_responses()),
        "grammar_probe":None,"controls":source_controls(tasks),
        "rows":[],
    }
    result["grammar_probe"]=probe_grammar()
    print("GBNF_PROBE",model,"OK",flush=True)
    for task in tasks:
        for mode in INTERFACES:
            row=run_one(task,model,mode)
            result["rows"].append(row)
            print(task["ref"]["id"],model,mode,row["status"],
                  repr(row["raw_output"]),row["selected_verified_source_lines"],flush=True)
    result["arms"]={}
    for mode in INTERFACES:
        rows=[x for x in result["rows"] if x["decoding_mode"]==mode]
        result["arms"][mode]={
            "aggregate":aggregate(rows),
            "by_family":{
                fam:aggregate([x for x in rows if x["family"]==fam])
                for fam in ("affine","quadratic")},
            "rejections":sum(x["status"]=="REJECTED" for x in rows),
            "abstentions":sum(x["abstained"] for x in rows),
            "inference_seconds_only":round(sum(x["inference"]["seconds"] for x in rows),3),
        }
    result["status"]="FINISHED_REAL_PAIRED_INFERENCE"
    return result


def compare(ctrl_file: Path, small_file: Path, large_file: Path) -> dict:
    ctrl=json.loads(ctrl_file.read_text(encoding="utf8"))
    sm=json.loads(small_file.read_text(encoding="utf8"))
    lg=json.loads(large_file.read_text(encoding="utf8"))
    if (ctrl["status"]!="FROZEN_OFFLINE_CONTROLS_OK" or
        sm["status"]!="FINISHED_REAL_PAIRED_INFERENCE" or
        lg["status"]!="FINISHED_REAL_PAIRED_INFERENCE"):
        raise ValueError("INCOMPLETE_REAL_MODEL_RUN")
    for report in (sm,lg):
        if (report["n_cases"]!=NUM_CASES or len(report["rows"])!=NUM_CASES*2
            or report["models_sha256"]!=MODEL_SHA
            or report["grammar_probe"]["raw_reply"]!="NONE"):
            raise ValueError("MISSING_PAIRED_CASE_OR_AUTHENTICATED_GBNF_PROBE")
        if ([x["case"] for x in report["rows"] if x["decoding_mode"]=="free"] !=
            [x["case"] for x in report["rows"] if x["decoding_mode"]=="gbnf"]):
            raise ValueError("NON_MATCHED_INTRA_MODEL_CASES")
    if ([x["case"] for x in sm["rows"]]!=[x["case"] for x in lg["rows"]]
        or [x["source_blob"] for x in sm["rows"]]!=[x["source_blob"] for x in lg["rows"]]):
        raise ValueError("DIFFERENT_SOURCES_BETWEEN_MODELS")
    outcomes={}
    for record in (sm,lg):
        free,gbnf=record["arms"]["free"],record["arms"]["gbnf"]
        outcomes[record["model"]]={
            "free":free, "gbnf":gbnf,
            "format_improved":gbnf["rejections"]<free["rejections"],
            "math_f1_improved":gbnf["aggregate"]["micro_f1"]>free["aggregate"]["micro_f1"],
            "format_complete_under_grammar":gbnf["rejections"]==0,
        }
    return {
        "status":"COMPLETED_SCIENTIFIC_COMPARISON",
        "n_new_cases":NUM_CASES,
        "n_experimental_model_generations":NUM_CASES*2*2,
        "n_probes":2, "n_responses_allowed_by_gbnf":86,
        "baseline_first3":ctrl["controls"]["first3"]["aggregate"],
        "scores":outcomes,
        "external_generalization":"NOT_ESTABLISHED",
        "scientific_certifications":0,
        "interpretation":"Grammar enforces syntax only; no gain in mathematical correctness is guaranteed.",
    }


def main()->None:
    arg=argparse.ArgumentParser()
    arg.add_argument("--mode", choices=("control","model","compare"),required=True)
    arg.add_argument("--model-label",choices=("0p5b","3b"))
    arg.add_argument("--output",type=Path,required=True)
    arg.add_argument("--controls",type=Path)
    arg.add_argument("--small",type=Path)
    arg.add_argument("--large",type=Path)
    args=arg.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    failure=False
    try:
        if args.mode=="model":
            result=run_model(args.model_label)
        elif args.mode=="control":
            ts=prepare()
            result={
                "status":"FROZEN_OFFLINE_CONTROLS_OK",
                "n_new_cases":len(ts),
                "gold_count":sum(len(t["ref"]["oracle_true_lines"]) for t in ts),
                "controls":source_controls(ts),
                "grammar_text":GRAMMAR, "grammar_legal_count":len(allowed_responses()),
            }
        else:
            if not (args.controls and args.small and args.large):
                raise ValueError("MISSING_COMPARISON_REPORT")
            result=compare(args.controls,args.small,args.large)
    except Exception:
        failure=True
        result={"status":"INFRA_FAILURE_NOT_SCIENTIFIC_RESULT",
                "exception":traceback.format_exc()}
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BENCH21",args.mode,result["status"],flush=True)
    if failure:
        sys.exit(1)


if __name__=="__main__":
    main()
