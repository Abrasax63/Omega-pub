"""OMEGA-ATOM-08: fail-closed test of edge reading and local implication.

Diagnostic, NOT training: 12 novel labelled directed graphs and all 8
Boolean triples. The same frozen model reads list/matrix representations and
evaluates the 3-bit transitivity implication independently. No verdict
or oracle is ever sent to the model during graph-reading trials.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path
import random

PROTOCOL = "OMEGA-ATOM-08-2026-11-24"
SEED = "omega-atom08-atomic-reading-logic-before-training-v1"
NODES = ("p0", "p1", "p2", "p3")
ARMS = ("LIST", "MATRIX")
FIELDS = ("xy", "yz", "xz")
PATTERNS = (0, 1, 2, 3, 4, 5, 6, 7, 6, 6, 3, 5)
SYSTEM = "Read the exact supplied data. Return only the requested JSON object. Do not infer missing edges."
MODEL_SHA = "9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"
MAX_TOKENS = 100


def canonical(item):
    return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def h(text):
    return sha256(text.encode("utf-8")).hexdigest()


def bits(mask):
    if type(mask) is not int or not 0 <= mask <= 7:
        raise ValueError("INVALID_MASK")
    return {"xy": bool(mask & 4), "yz": bool(mask & 2), "xz": bool(mask & 1)}


def violates(triple_bits):
    return triple_bits["xy"] and triple_bits["yz"] and not triple_bits["xz"]


def make_manifest():
    questions, answers = [], []
    for i,mask in enumerate(PATTERNS):
        ordered = list(NODES)
        random.Random(int(h(SEED + ":order:" + str(i))[:16], 16)).shuffle(ordered)
        a,b,c,d = ordered
        targets = ((a,b),(b,c),(a,c))
        required = bits(mask)
        e = {edge for field,edge in zip(FIELDS,targets) if required[field]}
        # Deterministic nuisance edges: reading must not assume symmetry,
        # reflexivity, equivalence, or transitive closure.
        extras = [pair for pair in ((x,y) for x in NODES for y in NODES)
                  if pair not in targets]
        extras.sort(key=lambda p:h(SEED + ":extra:" + str(i) + ":" + canonical(p)))
        e.update(extras[:4 + (i % 3)])
        # No nuisance edge can accidentally overwrite an absent queried edge.
        assert {field:edge in e for field,edge in zip(FIELDS,targets)} == required
        label = h(SEED + ":case:" + str(i))[:16]
        questions.append({"id":label, "nodes":list(NODES),
                          "triple":[a,b,c],"edges":[list(p) for p in sorted(e)]})
        answers.append({"id":label, "bits":required, "violates":violates(required)})
    ordered_truth = list(range(8))
    ordered_truth.sort(key=lambda k:h(SEED + ":truth:" + str(k)))
    logic_questions = [{"id":h(SEED + ":logic:" + str(i))[:16],
                        "bits":bits(i)} for i in ordered_truth]
    logic_answers = [{"id":item["id"],"violates":violates(item["bits"])}
                     for item in logic_questions]
    return ({"protocol":PROTOCOL,"seed":SEED,"graphs":questions,
             "truth_table_queries":logic_questions,"answers_included":False},
            {"protocol":PROTOCOL,"seed":SEED,"graph_answers":answers,
             "truth_table_answers":logic_answers})


def matrix_of(graph):
    e={tuple(pair) for pair in graph["edges"]}
    ns=graph["nodes"]
    return [[1 if (x,y) in e else 0 for y in ns] for x in ns]


def prompt_for_graph(graph,arm):
    ns=canonical(graph["nodes"]); triple=canonical(graph["triple"])
    start=("Universe "+ns+". For ordered triple [x,y,z]="+triple+
           ", read whether the three DIRECTED edges x->y, y->z and x->z "
           "occur. Do not guess by transitivity. ")
    if arm=="LIST":
        repr_text="The exhaustive directed edge LIST is "+canonical(graph["edges"])+". "
    elif arm=="MATRIX":
        repr_text=("The adjacency MATRIX rows and columns are indexed in the exact order "+
                   ns+". A row i, column j value 1 means the directed edge exists. "+
                   "The complete matrix is "+canonical(matrix_of(graph))+". ")
    else:
        raise ValueError("INVALID_REPRESENTATION")
    return (start+repr_text+"Return JSON with exactly three Boolean keys "+
            "xy,yz,xz. Example of field names only: xy, yz, xz.")


def prompt_for_logic(question):
    return ("Given ONLY these three verified membership bits for a directed "
            "relation's edges x->y, y->z, x->z: "+canonical(question["bits"])+
            ". A transitivity counterexample exists for this triple exactly "
            "when xy AND yz AND NOT xz. Return JSON containing exactly one "
            "Boolean key violates, true only for a counterexample.")


def score_bits(raw):
    try:
        parsed=json.loads(raw.strip())
    except (AttributeError,TypeError,ValueError):
        return None
    if not isinstance(parsed,dict) or set(parsed)!=set(FIELDS) or any(
        type(parsed[k]) is not bool for k in FIELDS
    ):
        return None
    return parsed


def score_logic(raw):
    try:
        parsed=json.loads(raw.strip())
    except (AttributeError,TypeError,ValueError):
        return None
    if not isinstance(parsed,dict) or set(parsed)!={"violates"} or type(parsed["violates"]) is not bool:
        return None
    return parsed["violates"]


def issue(client,text):
    messages=[{"role":"system","content":SYSTEM},
              {"role":"user","content":text}]
    response=client(messages,MAX_TOKENS)
    if not isinstance(response,dict) or not isinstance(response.get("text"),str):
        raise ValueError("NO_RAW_MODEL_RESPONSE")
    raw=response["text"]
    return {"raw":raw,"raw_sha256":h(raw),"prompt_sha256":h(canonical(messages)),
            "usage":response.get("usage"),"time_s":response.get("time_s"),
            "max_tokens":MAX_TOKENS}


def persist(folder,filename,obj):
    p=Path(folder)/filename
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def run(folder,endpoint,client=None):
    q,a=make_manifest()
    persist(folder,"model_inputs.json",q)
    persist(folder,"oracle_only.json",a)
    report={"protocol":PROTOCOL,"status":"STARTED",
            "input_manifest_sha256":h(canonical(q)),
            "oracle_manifest_sha256":h(canonical(a)),
            "model_sha256_expected":MODEL_SHA,
            "model_weights_updated":False,"paid_model_calls":0,
            "new_competences_certified":0,"calls":0,
            "graph_trials":[],"logic_trials":[]}
    persist(folder,"report.json",report)
    if client is None:
        from real_abstraction_trial import RealClient
        client=RealClient(endpoint)
    oracle_graph={x["id"]:x for x in a["graph_answers"]}
    oracle_logic={x["id"]:x for x in a["truth_table_answers"]}
    try:
        for i,graph in enumerate(q["graphs"]):
            row={"id":graph["id"],"order":list(ARMS if i%2==0 else ARMS[::-1]),
                 "arms":{}}
            report["graph_trials"].append(row)
            persist(folder,"report.json",report)
            for arm in row["order"]:
                result=issue(client,prompt_for_graph(graph,arm))
                pred=score_bits(result["raw"])
                truth=oracle_graph[graph["id"]]["bits"]
                result["score"]={"valid_format":pred is not None,
                    "all_three":pred==truth if pred is not None else False,
                    "individual_bits":sum(pred[k]==truth[k] for k in FIELDS) if pred else 0}
                row["arms"][arm]=result
                report["calls"]+=1
                persist(folder,"report.json",report)
        for case in q["truth_table_queries"]:
            result=issue(client,prompt_for_logic(case))
            pred=score_logic(result["raw"])
            result["score"]={"valid_format":pred is not None,
                "correct":pred==oracle_logic[case["id"]]["violates"]
                            if pred is not None else False}
            report["logic_trials"].append({"id":case["id"],"output":result})
            report["calls"]+=1
            persist(folder,"report.json",report)
        metrics={}
        for arm in ARMS:
            out=[row["arms"][arm] for row in report["graph_trials"]]
            metrics[arm]={"n":len(out),
                "all_three_correct":sum(x["score"]["all_three"] for x in out),
                "individual_bits_correct":sum(x["score"]["individual_bits"] for x in out),
                "invalid":sum(not x["score"]["valid_format"] for x in out),
                "prompt_tokens":sum(x["usage"]["prompt_tokens"] for x in out),
                "completion_tokens":sum(x["usage"]["completion_tokens"] for x in out),
                "seconds":round(sum(x["time_s"] for x in out),3)}
        logic=[r["output"] for r in report["logic_trials"]]
        pos={item["id"] for item in a["truth_table_answers"] if item["violates"]}
        logic_correct={r["id"] for r in report["logic_trials"] if r["output"]["score"]["correct"]}
        metrics["LOGIC"]={"n":8,"correct":len(logic_correct),
             "positive_case_correct":pos.issubset(logic_correct),
             "invalid":sum(not r["score"]["valid_format"] for r in logic),
             "prompt_tokens":sum(r["usage"]["prompt_tokens"] for r in logic),
             "completion_tokens":sum(r["usage"]["completion_tokens"] for r in logic),
             "seconds":round(sum(r["time_s"] for r in logic),3)}
        reading_gate=all(metrics[arm]["all_three_correct"]>=10
                 and metrics[arm]["invalid"]==0 for arm in ARMS)
        logic_gate=metrics["LOGIC"]["correct"]==8 and metrics["LOGIC"]["invalid"]==0
        report["metrics"]=metrics
        report["reading_gate"]=reading_gate
        report["logic_gate"]=logic_gate
        report["status"]="FOUNDATIONAL_GATES_PASS_DESCRIPTIVE_ONLY" if (
             reading_gate and logic_gate) else "FOUNDATIONAL_GATE_NOT_PASSED"
        report["statistical_gain_proven"]=False
        report["new_skill_learned"]=False
    except Exception as exc:
        report["status"]="TECHNICAL_FAILURE"
        report["error_class"]=type(exc).__name__
        raise
    finally:
        persist(folder,"report.json",report)
    return report


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    args=p.parse_args()
    result=run(args.output,args.server)
    print(json.dumps({"status":result["status"],"calls":result["calls"],
                      "metrics":result.get("metrics"),"new_competences_certified":0}))

if __name__=="__main__":
    main()
