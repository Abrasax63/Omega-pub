"""OMEGA-REPAIR-BENCH-04: compare negative, single witness and global obligations.

Preregistered six-task exploratory CPU experiment. No paid model API or new
certification; all correct decisions made by the pre-existing finite oracle.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

from concept_abstraction_lab import check_axioms
from incremental_math_library import canonical
from real_abstraction_trial import RealClient

PROTOCOL="OMEGA-REPAIR-BENCH-04-2026-11-23"
TASKS=(
 ("R1","equivalence",("a1","a2","a3","a4"),
  ("reflexive","symmetric","transitive")),
 ("R2","partial_order",("b1","b2","b3","b4"),
  ("reflexive","antisymmetric","transitive")),
 ("R3","preorder",("c1","c2","c3","c4"),
  ("reflexive","transitive")),
 ("R4","symmetric",("h1","h2","h3","h4"),("symmetric",)),
 ("R5","transitive",("j1","j2","j3","j4"),("transitive",)),
 ("R6","antisymmetric",("t1","t2","t3","t4"),("antisymmetric",)),
)
DEFINITIONS={
 "reflexive":"each x must relate to itself",
 "symmetric":"for every xRy, yRx must also hold",
 "antisymmetric":"if xRy and yRx then x=y",
 "transitive":"if xRy and yRz then xRz",
}
AXIOM_ORDER=("reflexive","symmetric","antisymmetric","transitive")
ARMS=("G","S","A")
ORDERS=(
 ("G","S","A"),("S","A","G"),("A","G","S"),
 ("G","A","S"),("S","G","A"),("A","S","G"))
SYSTEM=("You construct finite mathematical relations. Only return valid JSON. "
        "Avoid extra prose and invent the relation yourself; abstain if needed.")
OUTPUT_RULE=('Return JSON object with only one key "edges": a list of distinct '
             'ordered pairs. At least TWO pairs must have different endpoints; '
             'the empty/diagonal-only solution is not permitted.')
TOKEN_FILL=" Neutral administrative check marker."
MAX_OUTPUT_TOKENS=260
SOURCE_COMMIT="1a2005c6797bec10289f09e706f81c6c4b809a52"
SOURCE_BLOB="75bebda318694bb4712d60380b0e183e77f1e757"
MODEL_SHA="9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"

def task_description(task):
    _,name,nodes,axioms=task
    return ("Concept "+name+" on EXACT universe "+canonical(list(nodes))
            +"; required properties: "+ "; ".join(
                a+": "+DEFINITIONS[a] for a in axioms) +".")

def first_prompt(task):
    return ("Generate one NEW positive example for the following concept. "
            +task_description(task)+" "+OUTPUT_RULE)

def parse_edges(raw,nodes):
    try:
        data=json.loads(raw.strip())
        if not isinstance(data,dict) or data.get("abstain") is True:
            return None,"INVALID_JSON_OR_ABSTENTION"
        if set(data)!={"edges"} or not isinstance(data["edges"],list):
            return None,"INVALID_SCHEMA"
        edges=[]
        for edge in data["edges"]:
            if (not isinstance(edge,list) or len(edge)!=2
                    or any(not isinstance(v,str) or v not in nodes
                           for v in edge)):
                return None,"INVALID_VERTEX_OR_EDGE"
            edges.append(tuple(edge))
        if len(edges)>len(nodes)**2 or len(edges)!=len(set(edges)):
            return None,"DUPLICATE_OR_OVERSIZE"
        if sum(a!=b for a,b in edges)<2:
            return None,"DEGENERATE_FEWER_THAN_TWO_OFF_DIAGONAL"
        return frozenset(edges),"VALID"
    except (ValueError,TypeError):
        return None,"INVALID_JSON"

def all_obligations(nodes,edges,axioms):
    """All distinct exact failures for requested axioms (n<=4), sorted."""
    s=set(edges)
    problems=[]
    for a in axioms:
        if a=="reflexive":
            for x in nodes:
                if (x,x) not in s:
                    problems.append({"axiom":a,"witness":[x,x]})
        elif a=="symmetric":
            for x in nodes:
                for y in nodes:
                    if (x,y) in s and (y,x) not in s:
                        problems.append({"axiom":a,"witness":[x,y]})
        elif a=="antisymmetric":
            for i,x in enumerate(nodes):
                for y in nodes[i+1:]:
                    if (x,y) in s and (y,x) in s:
                        problems.append({"axiom":a,"witness":[x,y]})
        elif a=="transitive":
            for x in nodes:
                for y in nodes:
                    if (x,y) in s:
                        for z in nodes:
                            if (y,z) in s and (x,z) not in s:
                                problems.append({"axiom":a,
                                                 "witness":[x,y,z]})
        else:
            raise ValueError("UNKNOWN_REQUIRED_AXIOM")
    return problems

def audit(raw,task):
    tid,name,nodes,axioms=task
    edges,status=parse_edges(raw,nodes)
    if edges is None:
        return {"format_ok":False,"status":status,"correct":None,
                "violations":[],"violations_count":None,
                "edges":None,"fail_names":[]}
    oracle=check_axioms(nodes,edges)
    problems=all_obligations(nodes,edges,axioms)
    wrong=[a for a in axioms if not oracle[a]["holds"]]
    if set(wrong)!={v["axiom"] for v in problems}:
        raise AssertionError("EXACT_ORACLE_DISAGREES_WITH_WITNESS_ENUMERATOR")
    return {"format_ok":True,"status":status,"correct":not wrong,
            "violations":problems,"violations_count":len(problems),
            "edges":[list(e) for e in sorted(edges)],
            "fail_names":wrong}

def repaired_from(initial,candidate):
    if initial["edges"] is None or candidate["edges"] is None:
        return {"changed":None,"edits":None}
    a={tuple(x) for x in initial["edges"]}
    b={tuple(x) for x in candidate["edges"]}
    return {"changed":a!=b,"edits":len(a.symmetric_difference(b))}

def minimal_exact_repair(initial,task):
    """Exhaustive 2^16 search in Hamming-distance order; domain n=4 only."""
    if not initial["format_ok"]:return None
    _,_,nodes,axioms=task
    pairs=[(x,y) for x in nodes for y in nodes]
    assert len(pairs)==16
    old={tuple(x) for x in initial["edges"]}
    mask=sum((1<<i) for i,p in enumerate(pairs) if p in old)
    start=time.monotonic()
    inspected=0
    for edits in range(17):
        for comb in combinations(range(16),edits):
            inspected+=1
            candidate_mask=mask
            for i in comb:
                candidate_mask ^= (1<<i)
            edges=frozenset(p for i,p in enumerate(pairs)
                            if (candidate_mask>>i)&1)
            if sum(x!=y for x,y in edges)<2:
                continue
            facts=check_axioms(nodes,edges)
            if all(facts[a]["holds"] for a in axioms):
                chosen=[list(p) for p in sorted(edges)]
                verified=audit(canonical({"edges":chosen}),task)
                if not verified["correct"]:
                    raise AssertionError("SYMBOLIC_RESULT_FAILED_INDEPENDENT_ORACLE")
                return {"method":"EXACT_MINIMUM_HAMMING_DISTANCE",
                        "edits":edits,"relations_inspected":inspected,
                        "seconds":round(time.monotonic()-start,4),
                        "result_edges":chosen,"verified":True}
    raise AssertionError("NO_FINITE_SOLUTION")

def feedback(arm,previous,prior):
    assert previous["format_ok"] and not previous["correct"]
    if arm=="G":
        msg="External checker rejected the current candidate; reason hidden."
    elif arm=="S":
        one=previous["violations"][0]
        old=[p["single"] for p in prior if p.get("single") is not None]
        msg=("First exact counterexample: "+canonical(one)+
             ". Earlier exact counterexamples: "+canonical(old)+".")
    elif arm=="A":
        all_now=previous["violations"]
        old=[p["all"] for p in prior if p.get("all") is not None]
        if len(all_now)>64: raise ValueError("TOO_MANY_EXACT_WITNESSES")
        msg=("All current exact counterexamples: "+canonical(all_now)+
             ". Earlier full feedback: "+canonical(old)+".")
    else:
        raise ValueError("UNKNOWN_ARM")
    return msg

def prompt_repair(task,previous,arm,history):
    return ("Repair this same candidate. "+task_description(task)
       +" Current edges: "+canonical(previous["edges"])
       +". Feedback: "+feedback(arm,previous,history)
       +" Check ALL required properties on the final relation. "
       +OUTPUT_RULE+" Return your corrected relation now.")

def count_tokens(endpoint,s):
    req=Request(endpoint.rstrip("/")+"/tokenize",
                data=json.dumps({"content":s}).encode(),
                headers={"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=35) as resp:return len(json.load(resp)["tokens"])

def equalize(endpoint,prompts):
    out=dict(prompts)
    wanted=max(count_tokens(endpoint,p) for p in out.values())
    for arm in out:
        for _ in range(280):
            if count_tokens(endpoint,out[arm]) >= wanted:break
            out[arm]=out[arm].replace(" Return your corrected relation now.",
                        TOKEN_FILL+" Return your corrected relation now.",1)
    counts={arm:count_tokens(endpoint,p) for arm,p in out.items()}
    good=(min(counts.values())>0
          and (max(counts.values())-min(counts.values()))
               /min(counts.values())<=.05)
    return out,counts,good

def model_call(client,prompt):
    messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}]
    out=client(messages,MAX_OUTPUT_TOKENS)
    return {"messages":messages,
            "prompt_sha256":sha256(canonical(messages).encode()).hexdigest(),
            "text":out["text"],
            "text_sha256":sha256(out["text"].encode()).hexdigest(),
            "usage":out["usage"],"time_s":out["time_s"]}

def write_report(out,report):
    out.mkdir(parents=True,exist_ok=True)
    (out/"report.json").write_text(
        json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

def run(output,endpoint):
    out=Path(output)
    report={"protocol":PROTOCOL,"stage":"STARTED",
        "model_weights_updated":False,"api_paid_calls":0,
        "certified_theorems":0,
        "source_commit":SOURCE_COMMIT,"source_blob":SOURCE_BLOB,
        "model_weights_sha256":MODEL_SHA,
        "model_calls":0,"tasks":[]}
    write_report(out,report)
    client=RealClient(endpoint)
    try:
        for i,task in enumerate(TASKS):
            tid,name,nodes,axioms=task
            task_row={"id":tid,"concept":name,"nodes":list(nodes),
                      "required_axioms":list(axioms)}
            report["tasks"].append(task_row)
            first=model_call(client,first_prompt(task))
            first["oracle"]=audit(first["text"],task)
            task_row["initial"]=first
            write_report(out,report)
            if not first["oracle"]["format_ok"]:
                task_row["eligible"]=False
                task_row["reason"]="INITIAL_INVALID"
                continue
            task_row["symbolic_minimal"]=minimal_exact_repair(
                                  first["oracle"],task)
            if first["oracle"]["correct"]:
                task_row["eligible"]=False
                task_row["reason"]="INITIAL_CORRECT"
                continue
            task_row["eligible"]=True
            states={arm:dict(previous=first["oracle"],history=[],
                             attempts=[],stopped=False) for arm in ARMS}
            task_row["arms"]={arm:states[arm]["attempts"] for arm in ARMS}
            task_row["orders"]=[]
            task_row["token_budget_checks"]=[]
            # Same original specimen for each arm; independent subsequent states.
            for k in range(2):
                active=[arm for arm in ORDERS[i] if not states[arm]["stopped"]]
                if not active: break
                inputs={a:prompt_repair(task,states[a]["previous"],a,
                                        states[a]["history"]) for a in active}
                inputs,budgets,comparable=equalize(endpoint,inputs)
                task_row["orders"].append(active)
                task_row["token_budget_checks"].append(
                    {"round":k+1,"tokens":budgets,"within_five_percent":comparable})
                for arm in active:
                    state=states[arm]
                    prev=state["previous"]
                    # Preserve feedback of an earlier round, never another arm.
                    reply=model_call(client,inputs[arm])
                    reply["oracle"]=audit(reply["text"],task)
                    reply["change_from_initial"]=repaired_from(first["oracle"],
                                                               reply["oracle"])
                    reply["success"]=bool(
                        reply["oracle"]["correct"] is True
                        and reply["change_from_initial"]["changed"] is True)
                    reply["round"]=k+1
                    state["attempts"].append(reply)
                    if arm=="S":
                        state["history"].append(
                          {"single":prev["violations"][0]})
                    elif arm=="A":
                        state["history"].append({"all":prev["violations"]})
                    else:
                        state["history"].append({"generic":"rejected"})
                    state["previous"]=reply["oracle"]
                    if reply["success"] or not reply["oracle"]["format_ok"]:
                        state["stopped"]=True
                    write_report(out,report)
        valid=[t for t in report["tasks"]
               if t.get("initial",{}).get("oracle",{}).get("format_ok")]
        eligible=[t for t in report["tasks"] if t.get("eligible")]
        metrics={"total":len(TASKS),
                 "initial_valid":len(valid),
                 "initial_correct":sum(t["initial"]["oracle"]["correct"] is True
                                       for t in valid),
                 "initial_invalid":len(TASKS)-len(valid),
                 "eligible_errors":len(eligible)}
        for arm in ARMS:
            attempts=[a for t in eligible for a in t["arms"][arm]]
            wins=sum(any(a["success"] for a in t["arms"][arm]) for t in eligible)
            early=sum(bool(t["arms"][arm] and t["arms"][arm][0]["success"])
                      for t in eligible)
            metrics[arm]={"success_1":early,"success_by_2":wins,
                           "invalid_replies":sum(
                             not a["oracle"]["format_ok"] for a in attempts),
                           "calls":len(attempts),
                           "prompt_tokens":sum(
                             int(a["usage"].get("prompt_tokens",0)) for a in attempts),
                           "completion_tokens":sum(
                             int(a["usage"].get("completion_tokens",0))
                             for a in attempts),
                           "seconds":round(sum(a["time_s"] for a in attempts),3)}
        all_budget_good=all(
           b["within_five_percent"] for t in eligible
             for b in t["token_budget_checks"] if len(b["tokens"])>1)
        report["metrics"]=metrics
        report["all_pairs_token_comparable"]=all_budget_good
        report["registered_gain"]=bool(
            len(eligible)>=3 and all_budget_good
            and metrics["A"]["success_by_2"]>=2
            and metrics["A"]["success_by_2"]-metrics["G"]["success_by_2"]>=2
            and metrics["A"]["success_by_2"]-metrics["S"]["success_by_2"]>=1)
        if len(eligible)<3 or not all_budget_good:
            report["stage"]="INDETERMINATE"
        elif report["registered_gain"]:
            report["stage"]="POINTWISE_GLOBAL_FEEDBACK_GAIN"
        else:
            report["stage"]="REGISTERED_GAIN_NOT_OBSERVED"
    except Exception as e:
        report["stage"]="TECHNICAL_FAILURE"
        report["error_type"]=type(e).__name__
        raise
    finally:
        report["model_calls"]=len(client.calls)
        report["model_metrics"]=client.calls
        write_report(out,report)
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    a=p.parse_args()
    r=run(a.output,a.server)
    print(json.dumps({"stage":r["stage"],"calls":r["model_calls"],
                      "metrics":r.get("metrics")},ensure_ascii=False))
if __name__=="__main__":main()
