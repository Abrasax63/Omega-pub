#!/usr/bin/env python3
"""BENCH20: prospectively paired SOURCE (Git line IDs) vs ORDINAL (1..5) interface.

Author-generated finite arithmetic truth; no independent human annotation.
Never repair a model reply. Convert IDs to verified source lines only when
the output parses strictly in its own offered ID space, then quarantine.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / "reader_benchmark19"))
sys.path.insert(0, str(HERE.parent / "reader_bridge14"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from benchmark import render, metric, aggregate, call_model, source_gate
from selector import parse_selection
from read import safe_read, packetize, verify_packets

SPEC = HERE / "CASE_SPEC.json"
FROZEN = HERE / "FROZEN_CASES.json"
INTERFACES = ("source", "ordinal")
MODEL_HASHES = {
    "0p5b": "74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db",
    "3b": "626b4a6678b86442240e33df819e00132d3ba7dddfe1cdc4fbb18e0a9615c62d",
}
LLAMA_SHA = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
KEYS = {"INJ", "FIX", "EVAL1", "EVAL2", "INV"}
N = 20
SOURCE_IDS = (9,10,11,12,13)
ORDINAL_IDS = (1,2,3,4,5)
MAX_SELECTED = 3
MAX_TOKENS = 64


def verify_exact_oracle(case: dict) -> dict:
    m, a, b = case["modulus"], case["a"], case["b"]
    if (case["kind"] not in ("affine", "quadratic")
        or any(type(x) is not int for x in (m,a,b,case["c"],case["d"]))
        or not 5 <= m <= 25 or min(a,b) < 0
        or not (0 <= case["c"] < m and 0 <= case["d"] < m)):
        raise ValueError("INVALID_EXACT_FINITE_CASE")
    def f(x):
        return (a * (x if case["kind"] == "affine" else x*x) + b) % m
    vals = [f(x) for x in range(m)]
    return {
        "INJ": len(set(vals)) == m,
        "FIX": any(v == x for x,v in enumerate(vals)),
        "EVAL1": f(1) == case["d"],
        "EVAL2": f(f(0)) == case["c"],
        "INV": all(f(f(x)) == x for x in range(m)),
    }


def prepare() -> list[dict]:
    spec = json.loads(SPEC.read_text(encoding="utf8"))
    freeze = json.loads(FROZEN.read_text(encoding="utf8"))
    if (spec["status"] != "FROZEN_BEFORE_MODEL_RUN"
        or freeze["status"] != "FROZEN_BEFORE_MODEL_INFERENCE"
        or len(spec["cases"]) != N or len(freeze["documents"]) != N):
        raise ValueError("CASE_COUNT_OR_FREEZE_FAILURE")
    by_id = {c["id"]: c for c in spec["cases"]}
    if len(by_id) != N or len({r["id"] for r in freeze["documents"]}) != N:
        raise ValueError("DUPLICATE_OR_MISSING_CASES")
    tasks = []
    for ref in freeze["documents"]:
        case = by_id[ref["id"]]
        if set(case["order"]) != KEYS or len(case["order"]) != 5:
            raise ValueError("INVALID_PROPOSITION_ORDER")
        expected = HERE / "cases" / (ref["id"] + ".md")
        source = ROOT / ref["path"]
        if source.resolve() != expected.resolve():
            raise ValueError("UNEXPECTED_SOURCE_PATH")
        raw = safe_read(source, ref["blob"])
        if raw != render(case):
            raise ValueError("FROZEN_SOURCE_RENDER_MISMATCH")
        lines = raw.decode("utf8").splitlines()
        if len(lines) != 13 or tuple(ref["candidate_lines"]) != SOURCE_IDS:
            raise ValueError("SOURCE_LINE_LAYOUT_CHANGED")
        truth = verify_exact_oracle(case)
        gold = [9+i for i,k in enumerate(case["order"]) if truth[k]]
        if truth != ref["truth_by_predicate"] or gold != ref["oracle_true_lines"]:
            raise ValueError("ORACLE_MISMATCH")
        inv = packetize(raw, str(source))
        if verify_packets(raw, inv):
            raise ValueError("PACKET_PROVENANCE_FAILURE")
        packet_by_line = {n:p for p in inv["packets"]
                          for n in range(p["start_line"],p["end_line"]+1)}
        candidates = []
        for n in SOURCE_IDS:
            p = packet_by_line.get(n)
            if p is None or p["section_path"][-1] != "Énoncé":
                raise ValueError("CANDIDATE_NOT_IN_STATEMENT_SECTION")
            if not lines[n-1].startswith("Proposition : "):
                raise ValueError("LEXICAL_FORM_DRIFT")
            candidates.append({"line":n, "source_text":lines[n-1].strip(),
                               "section":p["section_path"],
                               "packet_id":p["packet_id"]})
        task = {"ref":ref,"case":case,"source":source,
                "raw":raw,"candidates":candidates,"definition":lines[4]}
        for n in SOURCE_IDS:
            source_gate(task,[n],"bench20-source-precheck")
        tasks.append(task)
    return tasks


def id_to_source(interface: str) -> dict[int,int]:
    if interface == "source":
        return dict(zip(SOURCE_IDS, SOURCE_IDS))
    if interface == "ordinal":
        return dict(zip(ORDINAL_IDS, SOURCE_IDS))
    raise ValueError("UNKNOWN_INTERFACE")


def messages(task:dict, interface:str) -> list[dict]:
    ids = id_to_source(interface)
    inverted = {line: ident for ident,line in ids.items()}
    choices = [{"id":inverted[c["line"]], "proposition":c["source_text"]}
               for c in task["candidates"]]
    # Both arms have byte-identical task data except ID values.
    instruction = (
        "Pour la fonction finie définie ci-dessous, choisis jusqu'à TROIS "
        "IDENTIFIANTS des propositions mathématiquement vraies. "
        "Chaque identifiant est une étiquette de choix, pas une valeur "
        "mathématique. Si aucune proposition n'est vraie, réponds NONE. "
        "Réponds seulement avec les IDENTIFIANTS autorisés, distincts, "
        "séparés par des virgules. Pas de prose, JSON, Markdown, explication, "
        "autre nombre ou numérotation inventée. "
        "Ne déduis jamais un identifiant d'un numéro de ligne non affiché."
    )
    return [
        {"role":"system","content":"Vérifie des propositions sur une fonction finie. Réponds uniquement par des identifiants offerts ou NONE."},
        {"role":"user","content":instruction+
         "\nDÉFINITION DE LA FONCTION :\n"+task["definition"]+
         "\nCANDIDATS (étiquette ID et proposition) :\n"+
         json.dumps(choices,ensure_ascii=False)+
         "\nIDENTIFIANTS AUTORISÉS : "+",".join(str(x) for x in ids)}
    ]


def parse_and_map(raw_reply:str,interface:str) -> tuple[list[int],list[int],str|None]:
    ident_to_source = id_to_source(interface)
    selected, reject = parse_selection(raw_reply, set(ident_to_source))
    if reject is not None:
        return [], [], reject
    if len(selected)>MAX_SELECTED or len(selected)!=len(set(selected)):
        return [], [], "TOO_MANY_OR_DUPLICATED_CHOICES"
    translated=[ident_to_source[x] for x in selected]
    if len(translated)!=len(set(translated)) or any(x not in SOURCE_IDS for x in translated):
        raise ValueError("INTERNAL_MAPPING_DRIFT")
    return selected, translated, None


def one(task:dict,interface:str,model_label:str,call=call_model)->dict:
    chats=messages(task,interface)
    output=call(chats)
    selected_ids,selected_source,rejection=parse_and_map(output["raw_reply"],interface)
    accepted=source_gate(task,selected_source,"bench20-"+model_label+"-"+interface) if rejection is None else 0
    return {
        "case":task["ref"]["id"],"family":task["case"]["kind"],
        "interface":interface,"model_label":model_label,
        "source_blob":task["ref"]["blob"],
        "candidate_source_lines":list(SOURCE_IDS),
        "offered_choice_ids":list(id_to_source(interface)),
        "raw_output":output["raw_reply"],
        "selected_model_ids":selected_ids,
        "selected_verified_source_lines":selected_source,
        "gold_lines":task["ref"]["oracle_true_lines"],
        "status":"REJECTED" if rejection else "VALID",
        "reject_reason":rejection,
        "abstained":rejection is None and not selected_ids,
        "source_gate_accepted":accepted,
        "metrics":metric(selected_source,task["ref"]["oracle_true_lines"]),
        "messages":chats,
        "inference":output,
        "horn_rules":0,"automatic_certifications":0,
    }


def controls(tasks:list[dict])->dict:
    methods={
        "first3":lambda t:list(SOURCE_IDS[:3]),
        "none":lambda t:[],
        "all5_coverage_only":lambda t:list(SOURCE_IDS),
    }
    result={}
    for name,fn in methods.items():
        rows=[]
        for t in tasks:
            selected=fn(t)
            if name!="all5_coverage_only":
                source_gate(t,selected,"bench20-control-"+name)
            rows.append({"case":t["ref"]["id"],"family":t["case"]["kind"],
                         "selected":selected,
                         "metrics":metric(selected,t["ref"]["oracle_true_lines"])})
        result[name]={"rows":rows,"aggregate":aggregate(rows)}
    return result


def run_model(label:str)->dict:
    tasks=prepare()
    ret={"status":"STARTED","experiment":"OMEGA_BENCH20_PAIRED_INTERFACE_ABLATION",
         "n_cases":N,"n_arms":2,"model_label":label,
         "models":MODEL_HASHES,"llama_cpp_sha":LLAMA_SHA,
         "gold_type":"SYNTHETIC_EXACT_EXHAUSTIVE_FINITE_ORACLE",
         "human_independent_labels":False,
         "no_api_paid":True,"auto_promotions":0,
         "controls":controls(tasks),"rows":[]}
    if label not in MODEL_HASHES:
        raise ValueError("MODEL_UNREGISTERED")
    # Paired on the same sources, two prompts differing only by identifiers.
    for t in tasks:
        for interface in INTERFACES:
            r=one(t,interface,label)
            ret["rows"].append(r)
            print(t["ref"]["id"],label,interface,r["status"],
                  repr(r["raw_output"]),r["selected_verified_source_lines"],flush=True)
    ret["scores"]={}
    for arm in INTERFACES:
        rows=[r for r in ret["rows"] if r["interface"]==arm]
        ret["scores"][arm]={
            "aggregate":aggregate(rows),
            "by_family":{
                family:aggregate([r for r in rows if r["family"]==family])
                for family in ("affine","quadratic")},
            "rejections":sum(r["status"]=="REJECTED" for r in rows),
            "abstentions":sum(r["abstained"] for r in rows),
            "seconds_inference_only":round(sum(r["inference"]["seconds"] for r in rows),3),
        }
    ret["status"]="FINISHED_REAL_PAIRED_INFERENCE"
    return ret


def compare(control_path:Path,small_path:Path,large_path:Path)->dict:
    control=json.loads(control_path.read_text(encoding="utf8"))
    m0=json.loads(small_path.read_text(encoding="utf8"))
    m3=json.loads(large_path.read_text(encoding="utf8"))
    if (control["status"]!="VERIFIED_FROZEN_CONTROLS" or
        any(z["status"]!="FINISHED_REAL_PAIRED_INFERENCE" for z in (m0,m3))):
        raise ValueError("INCOMPLETE_COMPARISON")
    for z in (m0,m3):
        if (z["n_cases"]!=N or len(z["rows"])!=N*2 or
            z["models"]!=MODEL_HASHES or
            [r["case"] for r in z["rows"] if r["interface"]=="source"]!=
            [r["case"] for r in z["rows"] if r["interface"]=="ordinal"]):
            raise ValueError("UNPAIRED_OR_WRONG_MODEL")
    if ([r["case"] for r in m0["rows"]]!=[r["case"] for r in m3["rows"]] or
        [r["source_blob"] for r in m0["rows"]]!=[r["source_blob"] for r in m3["rows"]]):
        raise ValueError("MODEL_ARMS_NOT_PAIRED")
    baseline=control["controls"]["first3"]["aggregate"]
    comparison={}
    for x in (m0,m3):
        name=x["model_label"]
        src=x["scores"]["source"]
        ord_=x["scores"]["ordinal"]
        comparison[name]={
            "source":src,"ordinal":ord_,
            "interface_gain_criterion": (
                ord_["rejections"] < src["rejections"] and
                ord_["aggregate"]["micro_f1"] > src["aggregate"]["micro_f1"]
            )
        }
    return {
        "status":"COMPLETE_COMPARISON",
        "n_unique_new_cases":N,
        "n_real_generations":4*N,
        "first3_baseline":baseline,
        "pairs":comparison,
        "secondary_3b_better_than_0p5b_and_first3":(
            comparison["3b"]["ordinal"]["aggregate"]["micro_f1"] >
            comparison["0p5b"]["ordinal"]["aggregate"]["micro_f1"] and
            comparison["3b"]["ordinal"]["aggregate"]["micro_f1"] >
            baseline["micro_f1"]
        ),
        "external_scientific_generalization":"NOT_ESTABLISHED",
        "mathematical_certifications":0,
        "note":"Only response protocol interface changes; oracle is synthetic/exhaustive not independent human gold.",
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mode",choices=("control","model","compare"),required=True)
    p.add_argument("--model-label",choices=("0p5b","3b"))
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--control",type=Path)
    p.add_argument("--small",type=Path)
    p.add_argument("--large",type=Path)
    args=p.parse_args()
    args.out.parent.mkdir(parents=True,exist_ok=True)
    failed=False
    try:
        if args.mode=="model":
            result=run_model(args.model_label)
        elif args.mode=="control":
            tasks=prepare()
            result={"status":"VERIFIED_FROZEN_CONTROLS","n_cases":N,
                    "controls":controls(tasks)}
        else:
            if not all((args.control,args.small,args.large)):
                raise ValueError("MISSING_REPORTS")
            result=compare(args.control,args.small,args.large)
    except Exception:
        failed=True
        result={"status":"INFRA_OR_ORACLE_FAILURE_NOT_A_SCIENTIFIC_RESULT",
                "exception":traceback.format_exc()}
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BENCH20",args.mode,result["status"],flush=True)
    if failed:
        sys.exit(1)


if __name__=="__main__":
    main()
