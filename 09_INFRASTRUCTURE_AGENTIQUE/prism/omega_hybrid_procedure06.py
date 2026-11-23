"""OMEGA-PROCEDURE-06: can a small language model EXECUTE a finite definition?

Pre-registered exploratory comparison of direct classification (D), textual
transitivity reminder (R), and operational certificates (P). The same fixed
Qwen weights are used, without training or paid APIs. The P arm must produce
a verifier-checkable partition OR an explicit transitivity counterexample.

All eight test graphs are five-node, reflexive, symmetric, pairwise
nonisomorphic and unseen in previous three/four-node Omega trials. The
classification oracle is NEVER included in model-facing messages.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path

from concept_abstraction_lab import check_axioms
from incremental_math_library import canonical
from omega_memory_real02 import prompt_budget
from real_abstraction_trial import RealClient

PROTOCOL = "OMEGA-PROCEDURE-06-2026-11-23"
SEED = "omega-procedure06-five-nodes-preregistered-v1"
MODEL_SHA = "9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"
NODES = ("v0", "v1", "v2", "v3", "v4")
PAIRS = tuple(combinations(NODES, 2))
AXIOMS = ("reflexive", "symmetric", "transitive")
ARMS = ("D", "R", "P")
ORDERS = (("D","R","P"), ("R","P","D"), ("P","D","R"),
          ("D","P","R"), ("R","D","P"), ("P","R","D"))
SYSTEM = ("You analyze finite directed relations. Return exactly one JSON "
          "object as instructed. No prose outside JSON. Do not invent edges.")
MAX_TOKENS = 420


def relation(mask):
    """Every graph is reflexive and symmetric; only transitivity varies."""
    if type(mask) is not int or not 0 <= mask < (1 << len(PAIRS)):
        raise ValueError("BAD_MASK")
    edges = {(x,x) for x in NODES}
    for i,(x,y) in enumerate(PAIRS):
        if mask & (1 << i):
            edges.update(((x,y), (y,x)))
    return frozenset(edges)


def isomorphic_key(edges):
    """Canonical relabeling by S5, not merely a pretty serialization."""
    return min(
        tuple(sorted((mapping[a], mapping[b]) for a,b in edges))
        for order in permutations(NODES)
        for mapping in (dict(zip(NODES,order)),)
    )


def exact_result(edges):
    facts = check_axioms(NODES, edges)
    failed = [a for a in AXIOMS if not facts[a]["holds"]]
    return {"holds": not failed, "failed_axioms": failed,
            "oracle_witnesses": {a:facts[a]["counterexample"] for a in failed}}


def independent_clique_check(edges):
    """Second oracle, component cliques, does not call check_axioms."""
    e = set(edges)
    if any((x,x) not in e for x in NODES):
        return False
    if any((b,a) not in e for a,b in e):
        return False
    remaining = set(NODES)
    while remaining:
        root = min(remaining)
        component = {root}
        todo = [root]
        remaining.remove(root)
        while todo:
            a = todo.pop()
            for b in NODES:
                if (a,b) in e and b not in component:
                    component.add(b)
                    remaining.discard(b)
                    todo.append(b)
        if any((a,b) not in e for a in component for b in component):
            return False
    return True


def make_manifest():
    yes,no,seen = [],[],set()
    # Fresh, frozen SHA selection; never draw tasks according to model answers.
    ordered = sorted(range(1 << len(PAIRS)),
        key=lambda m: sha256((SEED+":select:"+str(m)).encode()).digest())
    for mask in ordered:
        edges = relation(mask)
        key = isomorphic_key(edges)
        if key in seen:
            continue
        seen.add(key)
        truth = exact_result(edges)
        if independent_clique_check(edges) != truth["holds"]:
            raise AssertionError("TWO_ORACLES_DISAGREE")
        if truth["holds"]:
            if mask == 0:
                continue  # no trivial identity-only positive
            yes.append((mask,edges,truth))
        else:
            no.append((mask,edges,truth))
        if len(yes) >= 4 and len(no) >= 4:
            break
    if len(yes) < 4 or len(no) < 4:
        raise ValueError("INSUFFICIENT_NONISOMORPHIC_CLASSES")
    selected = yes[:4]+no[:4]
    selected.sort(key=lambda it:sha256(
        (SEED+":display:"+str(it[0])).encode()).digest())
    questions,answers = [],[]
    for mask,edges,truth in selected:
        ident = sha256((SEED+":case:"+str(mask)).encode()).hexdigest()[:20]
        questions.append({"id":ident,"nodes":list(NODES),
                          "edges":[list(x) for x in sorted(edges)]})
        answers.append({"id":ident,"mask":mask,**truth})
    if len({isomorphic_key(frozenset(map(tuple,q["edges"])))
            for q in questions}) != 8:
        raise AssertionError("NONISOMORPHISM_FAILED")
    return ({"protocol":PROTOCOL,"seed":SEED,"questions":questions,
             "contains_oracle_answers":False},
            {"protocol":PROTOCOL,"seed":SEED,"answers":answers})


def valid_answer(raw, truth, arm, edges):
    """Exact result has two levels: semantic classification and certificate."""
    failure = {"status":"INVALID_FORMAT","holds_correct":False,
               "full_axioms_correct":False,"certificate_valid":False if arm=="P" else None}
    if not isinstance(raw,str):
        return failure
    try:
        obj = json.loads(raw.strip())
    except ValueError:
        return failure
    keys = {"holds","failed_axioms","certificate"} if arm=="P" else {"holds","failed_axioms"}
    if not isinstance(obj,dict) or set(obj) != keys or type(obj["holds"]) is not bool:
        if obj == {"abstain":True}:
            return {**failure,"status":"ABSTAIN"}
        return failure
    f = obj["failed_axioms"]
    if not isinstance(f,list) or any(type(a) is not str or a not in AXIOMS for a in f) or (
        len(f) != len(set(f))) or obj["holds"] != (len(f)==0):
        return failure
    bool_ok = obj["holds"] == truth["holds"]
    full_ok = bool_ok and set(f)==set(truth["failed_axioms"])
    if arm!="P":
        return {"status":"ANSWER","holds_correct":bool_ok,
                "full_axioms_correct":full_ok,"certificate_valid":None}
    cert_ok = check_certificate(obj["certificate"],edges,obj["holds"])
    return {"status":"CERTIFIED" if cert_ok else "CERTIFICATE_INVALID",
            "holds_correct":bool_ok, "full_axioms_correct":full_ok,
            "certificate_valid":cert_ok}


def check_certificate(certificate, edges, claimed_holds):
    """Reject plausible text and fabricated witnesses; no correction injected."""
    if not isinstance(certificate,dict):
        return False
    e = set(edges)
    if claimed_holds:
        if set(certificate)!={"kind","blocks"} or certificate["kind"]!="partition":
            return False
        blocks = certificate["blocks"]
        if not isinstance(blocks,list) or not blocks:
            return False
        seen=set()
        for block in blocks:
            if not isinstance(block,list) or not block or any(
                type(v) is not str or v not in NODES for v in block):
                return False
            if len(set(block))!=len(block) or seen.intersection(block):
                return False
            seen.update(block)
        if seen!=set(NODES):
            return False
        generated={(x,y) for block in blocks for x in block for y in block}
        return generated==e
    if set(certificate)!={"kind","triple"} or certificate["kind"]!="missing_transitive_edge":
        return False
    triple=certificate["triple"]
    if not isinstance(triple,list) or len(triple)!=3 or any(
        type(x) is not str or x not in NODES for x in triple):
        return False
    a,b,c = triple
    return (a,b) in e and (b,c) in e and (a,c) not in e


def task_prompt(item,arm):
    nodes=canonical(item["nodes"])
    edges=canonical(item["edges"])
    common=("Given the directed relation with universe "+nodes+" and edges "+edges+
            ". All self loops and reverse edges are present; classify whether "
            "this is an equivalence relation. The three required axioms are "
            "reflexive, symmetric and transitive. ")
    if arm=="D":
        ending=("Return JSON with exactly holds (boolean) and failed_axioms "
                "(array of names from reflexive,symmetric,transitive).")
    elif arm=="R":
        ending=("Recall transitivity: for every x,y,z, if xRy and yRz then "
                "xRz. Check the supplied graph yourself. Return JSON with "
                "exactly holds (boolean) and failed_axioms (array of names "
                "from reflexive,symmetric,transitive).")
    elif arm=="P":
        ending=("Apply a mechanical certificate procedure, do not just recite "
                "the axioms. If the relation IS an equivalence, partition ALL "
                "vertices into blocks such that exactly every ordered pair "
                "within each block is an edge and no other edge exists; "
                "output certificate {kind:'partition',blocks:[...]}. "
                "If it is NOT an equivalence, find actual vertices x,y,z "
                "with xRy and yRz in the edge list, but xRz absent; "
                "output certificate {kind:'missing_transitive_edge',triple:[x,y,z]}. "
                "Return JSON with exactly holds (boolean), failed_axioms "
                "(array of names from reflexive,symmetric,transitive), and "
                "certificate (object). Use JSON double quotes.")
    else:
        raise ValueError("UNKNOWN_ARM")
    return common+ending


def count_matched(endpoint,prompts,token_counter=None):
    count = token_counter or (lambda txt: prompt_budget(endpoint,txt))
    outputs=dict(prompts)
    sizes={a:count(SYSTEM+"\n"+p) for a,p in outputs.items()}
    target=max(sizes.values())
    for arm in ARMS:
        for _ in range(180):
            if sizes[arm]>=target:
                break
            outputs[arm]+="\nNeutral administrative placeholder."
            sizes[arm]=count(SYSTEM+"\n"+outputs[arm])
    final={a:count(SYSTEM+"\n"+p) for a,p in outputs.items()}
    comparable=min(final.values())>0 and (max(final.values())-min(final.values()))/max(final.values()) <= .05
    return outputs,final,comparable


def persist(root,name,data):
    p=Path(root)/name
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def run(root,endpoint,client=None,token_counter=None):
    questions,answers=make_manifest()
    report={"protocol":PROTOCOL, "status":"STARTED",
            "frozen_question_sha256":sha256(canonical(questions).encode()).hexdigest(),
            "frozen_oracle_sha256":sha256(canonical(answers).encode()).hexdigest(),
            "model_sha256_expected":MODEL_SHA,"model_weights_updated":False,
            "paid_model_calls":0,"model_calls":0,"scientific_skills_certified":0,
            "model_prompt_cost_balanced":True,"trials":[]}
    persist(root,"model_inputs.json",questions)
    persist(root,"oracle_only.json",answers)
    persist(root,"report.json",report)
    llm=client if client is not None else RealClient(endpoint)
    key={v["id"]:v for v in answers["answers"]}
    try:
        for i,item in enumerate(questions["questions"]):
            prompts={a:task_prompt(item,a) for a in ARMS}
            prompts,budget,balanced=count_matched(endpoint,prompts,token_counter)
            report["model_prompt_cost_balanced"] &= balanced
            row={"id":item["id"],"order":list(ORDERS[i%len(ORDERS)]),
                 "measured_prompt_tokens":budget,
                 "prompt_tokens_comparable":balanced,"arms":{}}
            report["trials"].append(row)
            persist(root,"report.json",report)
            for arm in row["order"]:
                messages=[{"role":"system","content":SYSTEM},
                          {"role":"user","content":prompts[arm]}]
                completion=llm(messages,MAX_TOKENS)
                raw=completion["text"]
                row["arms"][arm]={
                    "raw":raw,"raw_sha256":sha256(raw.encode()).hexdigest(),
                    "prompt_sha256":sha256(canonical(messages).encode()).hexdigest(),
                    "usage":completion["usage"],"time_s":completion["time_s"],
                    "verdict":valid_answer(raw,key[item["id"]],arm,
                            frozenset(map(tuple,item["edges"])))}
                report["model_calls"]+=1
                persist(root,"report.json",report)
        metrics={}
        comparable=report["model_prompt_cost_balanced"]
        for arm in ARMS:
            results=[row["arms"][arm] for row in report["trials"]]
            tokens=[r["usage"].get("prompt_tokens",0) for r in results]
            metrics[arm]={"total":len(results),
                "holds_correct":sum(int(r["verdict"]["holds_correct"]) for r in results),
                "full_axioms_correct":sum(int(r["verdict"]["full_axioms_correct"]) for r in results),
                "certificate_valid":sum(r["verdict"]["certificate_valid"] is True for r in results) if arm=="P" else None,
                "invalid_format":sum(r["verdict"]["status"]=="INVALID_FORMAT" for r in results),
                "invalid_certificate":sum(r["verdict"]["status"]=="CERTIFICATE_INVALID" for r in results),
                "abstain":sum(r["verdict"]["status"]=="ABSTAIN" for r in results),
                "input_tokens":sum(tokens),
                "output_tokens":sum(int(r["usage"].get("completion_tokens",0)) for r in results),
                "model_seconds":round(sum(r["time_s"] for r in results),3)}
            if any(type(t) is not int or t<=0 for t in tokens):
                comparable=False
        for trial in report["trials"]:
            usage=[trial["arms"][a]["usage"].get("prompt_tokens",0) for a in ARMS]
            if max(usage)-min(usage) > .05*max(usage):
                comparable=False
        gain=(comparable and metrics["P"]["full_axioms_correct"]>=6
              and metrics["P"]["full_axioms_correct"]-metrics["D"]["full_axioms_correct"]>=2
              and metrics["P"]["full_axioms_correct"]-metrics["R"]["full_axioms_correct"]>=2
              and metrics["P"]["certificate_valid"]>=6
              and metrics["P"]["invalid_format"]==0)
        report["metrics"]=metrics
        report["actual_input_budget_comparable"]=comparable
        report["gain_criterion_met"]=bool(gain)
        report["status"]=("POINTWISE_PROCEDURE_GAIN_OBSERVED" if gain else
                          "INDETERMINATE_BUDGET" if not comparable else
                          "PRE_REGISTERED_GAIN_NOT_OBSERVED")
        report["statistical_significance"]=False
        report["durable_training"]=False
    except Exception as err:
        report["status"]="TECHNICAL_FAILURE"
        report["error_class"]=type(err).__name__
        raise
    finally:
        persist(root,"report.json",report)
    return report


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    args=p.parse_args()
    result=run(args.output,args.server)
    print(json.dumps({"status":result["status"],"model_calls":result["model_calls"],
                      "metrics":result.get("metrics"),"certified_skills":0}))


if __name__=="__main__":
    main()
