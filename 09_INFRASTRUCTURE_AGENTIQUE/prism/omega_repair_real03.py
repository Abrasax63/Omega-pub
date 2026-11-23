"""REAL-03: an independently scored, paired exact-witness repair experiment.

Not a semantic proof, no model-weight updates, no writes to scientific memory.
Requires the CPU llama.cpp local server from the REAL-02 workflow.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

from concept_abstraction_lab import check_axioms
from incremental_math_library import canonical
from real_abstraction_trial import RealClient

PROTOCOL = "OMEGA-REPAIR-REAL-03-2026-11-23"
MODEL_SHA = "9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"
NODES_TO_TASKS = (
    ("T1", "partial_order", ("p", "q", "r", "s"),
     ("A partial order is a relation on the displayed set that is reflexive "
      "(every element relates to itself), antisymmetric (if xRy and yRx then "
      "x=y), and transitive (if xRy and yRz then xRz).")),
    ("T2", "symmetric", ("u", "v", "w", "x"),
     ("A relation is symmetric when xRy implies yRx for every x and y.")),
    ("T3", "transitive", ("k", "l", "m", "n"),
     ("A relation is transitive when xRy and yRz imply xRz for all x,y,z.")),
    ("T4", "antisymmetric", ("d", "e", "f", "g"),
     ("A relation is antisymmetric when xRy and yRx imply x=y for all x,y.")),
)
AXIOM_MAP = {
    "partial_order": ("reflexive", "antisymmetric", "transitive"),
    "symmetric": ("symmetric",),
    "transitive": ("transitive",),
    "antisymmetric": ("antisymmetric",),
}
PRIORITY = ("reflexive", "symmetric", "antisymmetric", "transitive")
SYSTEM = (
    "You investigate finite relations, and may abstain if uncertain. "
    "Do not claim a proof beyond the supplied finite structures. "
    "Respond with exactly one JSON object. Never copy a proposed solution "
    "from background text; construct your own relation."
)
OUTPUT_SCHEMA = (
    'Output JSON with exactly one key "edges", an array of ordered pairs, '
    'such as [["label1","label2"], ...]. The universe is fixed and is '
    'not a field in the answer. Do not provide any explanations.'
)
NONTRIVIAL = (
    "The proposed relation must have at least TWO distinct off-diagonal "
    "ordered pairs, to prevent a vacuous empty/diagonal-only answer."
)
FILLER = " Unrelated archival bookkeeping marker."
MAX_REPAIR_PAD = 100
MAX_OUTPUT = 260

def initial_prompt(task):
    tid, target, nodes, description = task
    return (
        "Construct ONE new positive example of " + target + " on EXACTLY the "
        "following four distinct labels: " + canonical(list(nodes)) + ". "
        "Definition: " + description + " "
        + NONTRIVIAL + " " + OUTPUT_SCHEMA
    )

def parse_relation(raw, nodes):
    try:
        data = json.loads(raw.strip())
        if not isinstance(data, dict) or data.get("abstain") is True:
            return None, "ABSTENTION_OR_INVALID_JSON"
        edges = data.get("edges")
        if not isinstance(edges, list) or len(edges) > len(nodes) ** 2:
            return None, "INVALID_EDGE_LIST"
        pairs = []
        for e in edges:
            if (not isinstance(e, list) or len(e) != 2
                    or any(not isinstance(x, str) or x not in nodes for x in e)):
                return None, "INVALID_VERTEX_OR_PAIR"
            pairs.append(tuple(e))
        if len(set(pairs)) != len(pairs):
            return None, "DUPLICATE_PAIR"
        if sum(a != b for a, b in pairs) < 2:
            return None, "DEGENERATE_FEWER_THAN_TWO_OFFDIAGONAL_EDGES"
        return frozenset(pairs), "VALID_FORMAT_AND_NONTRIVIAL"
    except (ValueError, TypeError):
        return None, "INVALID_JSON"

def evaluate(raw, nodes, axioms):
    pairs, status = parse_relation(raw, nodes)
    if pairs is None:
        return {"parsed_status": status, "format_ok": False,
                "math_correct": None, "failed_axioms": [],
                "first_witness": None, "edges": None}
    facts = check_axioms(nodes, pairs)
    wrong = [a for a in PRIORITY if a in axioms and not facts[a]["holds"]]
    return {"parsed_status": status, "format_ok": True,
            "math_correct": not wrong, "failed_axioms": wrong,
            "first_witness": ({"axiom":wrong[0],
                               "witness":facts[wrong[0]]["counterexample"]}
                              if wrong else None),
            "edges": [list(x) for x in sorted(pairs)]}

def same_or_changed(original, new):
    if not (original["edges"] is not None and new["edges"] is not None):
        return {"changed": None, "edit_distance": None}
    initial = {tuple(p) for p in original["edges"]}
    later = {tuple(p) for p in new["edges"]}
    return {"changed": initial != later,
            "edit_distance": len(initial.symmetric_difference(later))}

def feedback(task, original, arm):
    tid, target, nodes, description = task
    assert original["format_ok"] and not original["math_correct"]
    context = (
        "Previously you produced this relation over " + canonical(list(nodes))
        + ": " + canonical(original["edges"]) + ". "
        "Target: " + target + ". Definition: " + description + " "
    )
    if arm == "W":
        w = original["first_witness"]
        detail = ("Independent exact checker found a violation of axiom "
                  + w["axiom"] + "; counterexample witness = "
                  + canonical(w["witness"]) + ".")
    else:
        detail = ("Independent exact checker found a violation of at least "
                  "one required axiom; the axiom name and witness are withheld.")
    return (context + detail + " Repair your own relation once. "
            "No corrected edge set is supplied. " + NONTRIVIAL + " " + OUTPUT_SCHEMA)

def count_tokens(endpoint, s):
    request = Request(
        endpoint.rstrip("/") + "/tokenize",
        data=json.dumps({"content": s}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST")
    with urlopen(request, timeout=35) as answer:
        return len(json.load(answer)["tokens"])

def equalize(endpoint, prompts):
    # Pad the shorter repair prompt with *nonscientific* material only.
    counts = {k:count_tokens(endpoint, v) for k,v in prompts.items()}
    wanted = max(counts.values())
    out = dict(prompts)
    for arm in out:
        for _ in range(MAX_REPAIR_PAD):
            if count_tokens(endpoint, out[arm]) >= wanted:
                break
            out[arm] = out[arm].replace(" Repair your own relation once.",
                         FILLER + " Repair your own relation once.", 1)
    counts = {k:count_tokens(endpoint,v) for k,v in out.items()}
    comparable = (min(counts.values()) > 0
                  and (max(counts.values())-min(counts.values()))
                        /min(counts.values()) <= 0.05)
    return out, counts, comparable

def saved(root, report):
    root.mkdir(parents=True,exist_ok=True)
    (root/"report.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def call(client, system, prompt):
    messages=[{"role":"system","content":system},
              {"role":"user","content":prompt}]
    out=client(messages, MAX_OUTPUT)
    return {"prompt_sha256":sha256(canonical(messages).encode()).hexdigest(),
            "messages":messages, "raw":out["text"], "usage":out["usage"],
            "seconds":out["time_s"]}

def run(output, endpoint):
    root=Path(output)
    report={"protocol": PROTOCOL, "experiment_status": "IN_PROGRESS",
            "source": {"book":"Oscar Levin, DMOI4",
              "upstream_commit":"1a2005c6797bec10289f09e706f81c6c4b809a52",
              "upstream_blob":"75bebda318694bb4712d60380b0e183e77f1e757"},
            "model_sha256_expected": MODEL_SHA,
            "model_weights_updated": False,
            "theorems_certified": 0,
            "api_paid_calls": 0,
            "tasks": [], "model_calls": 0}
    saved(root, report)
    client=RealClient(endpoint)
    try:
        for index, task in enumerate(NODES_TO_TASKS):
            tid,target,nodes,description=task
            axioms=AXIOM_MAP[target]
            task_report={"id":tid,"target":target,"nodes":list(nodes),
                         "axioms":list(axioms),"repair_eligible":False}
            report["tasks"].append(task_report)
            prompt=initial_prompt(task)
            initial=call(client,SYSTEM,prompt)
            initial["oracle"]=evaluate(initial["raw"],nodes,axioms)
            task_report["initial"]=initial
            saved(root,report)
            if (not initial["oracle"]["format_ok"]
                    or initial["oracle"]["math_correct"]):
                task_report["skip_reason"]=(
                    "INITIAL_INVALID_FORMAT" if not initial["oracle"]["format_ok"]
                    else "ALREADY_CORRECT_NO_REPAIR")
                continue
            task_report["repair_eligible"]=True
            arms=("W","G") if index%2==0 else ("G","W")
            before={arm:feedback(task,initial["oracle"],arm) for arm in ("W","G")}
            prepared,counts,comparable=equalize(endpoint,before)
            task_report["repair_order"]=list(arms)
            task_report["repair_prompt_tokens"]=counts
            task_report["comparable_prompt_lengths"]=comparable
            task_report["repairs"]={}
            saved(root,report)
            for arm in arms:
                output_record=call(client,SYSTEM,prepared[arm])
                output_record["oracle"]=evaluate(output_record["raw"],nodes,axioms)
                output_record["edits"]=same_or_changed(initial["oracle"],
                                                      output_record["oracle"])
                output_record["success"]=bool(
                    output_record["oracle"]["math_correct"] is True
                    and output_record["edits"]["changed"] is True)
                task_report["repairs"][arm]=output_record
                saved(root,report)
        eligible=[t for t in report["tasks"] if t["repair_eligible"]]
        report["counts"]={
            "tasks_total":len(report["tasks"]),
            "initial_correct":sum(t["initial"]["oracle"]["math_correct"] is True
                                  for t in report["tasks"]),
            "initial_invalid_format":sum(not t["initial"]["oracle"]["format_ok"]
                                         for t in report["tasks"]),
            "repair_opportunities":len(eligible),
            "W_success":sum(t["repairs"]["W"]["success"] for t in eligible),
            "G_success":sum(t["repairs"]["G"]["success"] for t in eligible),
            "W_invalid":sum(not t["repairs"]["W"]["oracle"]["format_ok"]
                             for t in eligible),
            "G_invalid":sum(not t["repairs"]["G"]["oracle"]["format_ok"]
                             for t in eligible)}
        delta=report["counts"]["W_success"]-report["counts"]["G_success"]
        compare=all(t["comparable_prompt_lengths"] for t in eligible)
        report["prompt_lengths_comparable"]=compare
        report["criterion_met"]=bool(
            len(eligible)>=2 and compare
            and report["counts"]["W_success"]>=2
            and delta>=2 and report["counts"]["W_invalid"]==0)
        if len(eligible)<2 or not compare:
            report["experiment_status"]="INDETERMINATE_INSUFFICIENT_COMPARABLE_ERRORS"
        elif report["criterion_met"]:
            report["experiment_status"]="POINTWISE_WITNESS_GAIN"
        else:
            report["experiment_status"]="PRE_REGISTERED_GAIN_NOT_OBSERVED"
        return report
    except Exception as exc:
        report["experiment_status"]="TECHNICAL_FAILURE"
        report["error_type"]=type(exc).__name__
        raise
    finally:
        report["model_calls"]=len(client.calls)
        report["model_metrics"]=client.calls
        saved(root,report)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    args=p.parse_args()
    result=run(args.output,args.server)
    print(json.dumps({
        "status":result["experiment_status"],
        "calls":result["model_calls"],
        "counts":result.get("counts")},ensure_ascii=False))

if __name__=="__main__":
    main()
