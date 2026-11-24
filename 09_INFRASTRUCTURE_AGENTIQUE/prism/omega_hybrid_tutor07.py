"""OMEGA-TUTOR-07: verified atomic proof tutoring versus neutral feedback.

A model first tries two *training-only* relations. Feedback is independently
computed: raw premise membership on a negative example and a complete
partition on a positive example. It then writes its own transfer note and
answers a NEW six-vertex holdout. Weights remain frozen: a positive result
would show only in-context procedural transfer, not parametric learning.

No holdout solution, witness, label or oracle data is included in a prompt.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

from concept_abstraction_lab import check_axioms
from incremental_math_library import canonical
from omega_memory_real02 import prompt_budget
from real_abstraction_trial import RealClient

PROTOCOL="OMEGA-ATOMIC-TUTOR-07-2026-11-23"
SEED="omega-tutor07-sealed-six-node-v1"
MODEL_SHA="9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"
NODES=tuple("u"+str(i) for i in range(6))
TRAIN_NODES=("a","b","c","d")
AXIOMS=("reflexive","symmetric","transitive")
ARMS=("D","G","T")
MAX_TOKENS=400
SYSTEM=("You inspect directed finite relations. Never invent edges in the "
        "given relation. Reply with exactly one JSON object and nothing else.")


def graph(nodes,undirected):
    e={(x,x) for x in nodes}
    for x,y in undirected:
        if x not in nodes or y not in nodes or x==y:
            raise ValueError("INVALID_UNDIRECTED_EDGE")
        e.update(((x,y),(y,x)))
    return frozenset(e)


def make_training():
    """Training graphs are four-node, disjoint from six-node hidden evaluation."""
    positive=graph(TRAIN_NODES,(("a","b"),("c","d")))
    negative=graph(TRAIN_NODES,(("a","b"),("b","c")))
    return [
      {"id":"TRAIN_NEG","nodes":list(TRAIN_NODES),
       "edges":[list(x) for x in sorted(negative)]},
      {"id":"TRAIN_POS","nodes":list(TRAIN_NODES),
       "edges":[list(x) for x in sorted(positive)]}
    ]


def relabel(nodes,edges,tag):
    order=sorted(nodes,key=lambda x:sha256((SEED+":relabel:"+tag+":"+x).encode()).digest())
    mapping=dict(zip(nodes,order))
    return frozenset((mapping[x],mapping[y]) for x,y in edges)


def iso_key(nodes,edges):
    return min(
        tuple(sorted((d[a],d[b]) for a,b in edges))
        for perm in permutations(nodes)
        for d in (dict(zip(nodes,perm)),)
    )


def make_holdout():
    """Four distinct partition types; four distinct nonclique graph types."""
    u=NODES
    pos = [
        [(u[0],u[1])],
        [(u[0],u[1]),(u[2],u[3])],
        [(u[0],u[1]),(u[0],u[2]),(u[1],u[2])],
        [(u[0],u[1]),(u[0],u[2]),(u[1],u[2]),(u[3],u[4])],
    ]
    neg = [
        [(u[0],u[1]),(u[1],u[2])], # P3 + 3 isolated
        [(u[0],u[1]),(u[1],u[2]),(u[2],u[3])], # P4 + 2
        [(u[0],u[1]),(u[0],u[2]),(u[0],u[3])], # claw + 2
        [(u[0],u[1]),(u[1],u[2]),(u[2],u[3]),(u[3],u[0])], # C4 + 2
    ]
    candidates=[]
    for i,undirected in enumerate(pos+neg):
        edges=relabel(u,graph(u,undirected),str(i))
        ident=sha256((SEED+":id:"+str(i)).encode()).hexdigest()[:18]
        candidates.append((ident,edges))
    candidates.sort(key=lambda z:sha256((SEED+":shuffle:"+z[0]).encode()).digest())
    questions=[];answers=[];orbits=set()
    for ident,edges in candidates:
        key=iso_key(u,edges)
        if key in orbits:
            raise AssertionError("HOLDOUT_ISOMORPHISM_DUPLICATED")
        orbits.add(key)
        truth=truth_oracle(u,edges)
        if independent_oracle(u,edges)!=truth["holds"]:
            raise AssertionError("INDEPENDENT_ORACLE_DISAGREEMENT")
        questions.append({"id":ident,"nodes":list(u),
                          "edges":[list(x) for x in sorted(edges)]})
        answers.append({"id":ident,**truth})
    if len(questions)!=8 or sum(x["holds"] for x in answers)!=4:
        raise AssertionError("HOLDOUT_NOT_BALANCED")
    return ({"protocol":PROTOCOL,"seed":SEED,"questions":questions,
             "has_labels":False},
            {"protocol":PROTOCOL,"seed":SEED,"answers":answers})


def truth_oracle(nodes,edges):
    checks=check_axioms(tuple(nodes),frozenset(edges))
    failed=[a for a in AXIOMS if not checks[a]["holds"]]
    return {"holds":not failed,"failed_axioms":failed}


def independent_oracle(nodes,edges):
    """Equivalence iff reflexive symmetric component-cliques, no check_axioms."""
    s=set(edges)
    if any((x,x) not in s for x in nodes):
        return False
    if any((b,a) not in s for a,b in s):
        return False
    pending=set(nodes)
    while pending:
        first=min(pending);pending.remove(first)
        comp={first};todo=[first]
        while todo:
            cur=todo.pop()
            for nxt in nodes:
                if (cur,nxt) in s and nxt not in comp:
                    comp.add(nxt);todo.append(nxt);pending.discard(nxt)
        if any((a,b) not in s for a in comp for b in comp):
            return False
    return True


def exact_partition(nodes,edges):
    s=set(edges);pending=set(nodes);blocks=[]
    while pending:
        first=min(pending);seen={first};pending.remove(first);todo=[first]
        while todo:
            x=todo.pop()
            for y in nodes:
                if (x,y) in s and y not in seen:
                    seen.add(y);pending.discard(y);todo.append(y)
        blocks.append(sorted(seen))
    if {(a,b) for block in blocks for a in block for b in block}!=s:
        return None
    return blocks


def atomic_membership(nodes,edges,triple):
    if not isinstance(triple,list) or len(triple)!=3 or any(
        type(x) is not str or x not in nodes for x in triple
    ):
        return None
    a,b,c=triple;s=set(edges)
    return {"xy":(a,b) in s,"yz":(b,c) in s,"xz":(a,c) in s}


def exact_counterexample(nodes,edges):
    s=set(edges)
    for a in nodes:
        for b in nodes:
            for c in nodes:
                if (a,b) in s and (b,c) in s and (a,c) not in s:
                    return [a,b,c]
    return None


def check_certificate(nodes,edges,claimed_holds,cert):
    if not isinstance(cert,dict):
        return False,False
    if claimed_holds:
        if set(cert)!={"kind","blocks"} or cert.get("kind")!="partition":
            return False,False
        blocks=cert["blocks"]
        if not isinstance(blocks,list) or not blocks:
            return False,False
        seen=set()
        for block in blocks:
            if not isinstance(block,list) or not block or any(
                type(x) is not str or x not in nodes for x in block
            ) or len(set(block))!=len(block) or any(x in seen for x in block):
                return False,False
            seen.update(block)
        if seen!=set(nodes):
            return False,False
        edges_from_blocks={(a,b) for block in blocks for a in block for b in block}
        correct=edges_from_blocks==set(edges)
        return correct,correct
    if set(cert)!={"kind","triple","premises"} or cert.get("kind")!="missing_transitive_edge":
        return False,False
    actual=atomic_membership(nodes,edges,cert["triple"])
    reported=cert["premises"]
    if actual is None or not isinstance(reported,dict) or set(reported)!={"xy","yz","xz"}:
        return False,False
    if any(type(reported[k]) is not bool for k in ("xy","yz","xz")):
        return False,False
    bitwise=all(reported[k] == actual[k] for k in ("xy","yz","xz"))
    return bitwise and actual=={"xy":True,"yz":True,"xz":False},bitwise


def score_raw(raw,nodes,edges):
    truth=truth_oracle(nodes,edges)
    bad={"status":"INVALID","boolean_correct":False,"axioms_correct":False,
         "certificate_correct":False,"atomic_bits_correct":False,
         "fully_certified":False}
    if not isinstance(raw,str):
        return bad
    try:
        r=json.loads(raw.strip())
    except ValueError:
        return bad
    if r=={"abstain":True}:
        return {**bad,"status":"ABSTAIN"}
    if not isinstance(r,dict) or set(r)!={"holds","failed_axioms","certificate"} or type(r["holds"]) is not bool:
        return bad
    failed=r["failed_axioms"]
    if (not isinstance(failed,list) or
        any(type(x) is not str or x not in AXIOMS for x in failed) or
        len(failed)!=len(set(failed)) or r["holds"] != (len(failed)==0)):
        return bad
    valid,bitwise=check_certificate(nodes,edges,r["holds"],r["certificate"])
    b=r["holds"]==truth["holds"]
    a=b and set(failed)==set(truth["failed_axioms"])
    return {"status":"ANSWER","boolean_correct":b,"axioms_correct":a,
            "certificate_correct":valid,"atomic_bits_correct":bitwise,
            "fully_certified":a and valid}


def question_text(task,lesson=None):
    note=("No previous practice note is available." if lesson is None else
          "A note you composed after practice was: "+lesson)
    return (note+"\nUniverse: "+canonical(task["nodes"])+
       ". Directed edge list: "+canonical(task["edges"])+
       ". Verify whether the given relation is reflexive, symmetric and transitive. "
       "Return exactly JSON with keys holds (boolean), failed_axioms "
       "(array of axioms reflexive/symmetric/transitive), certificate (object). "
       "If it holds, supply certificate with kind partition and blocks covering "
       "all vertices and exactly all edges. If it fails, supply certificate "
       "with kind missing_transitive_edge, triple [x,y,z], and premises with "
       "xy,yz,xz as exact booleans indicating whether each corresponding "
       "directed edge EXISTS. Check all three atomic bits against the graph. "
       "No proof text. You may return {\"abstain\":true}.")


def teacher_feedback(task,raw,arm):
    nodes=tuple(task["nodes"]);edges=frozenset(map(tuple,task["edges"]))
    score=score_raw(raw,nodes,edges)
    if arm=="G":
        return "The submitted attempt was recorded; detailed verifier feedback is withheld."
    if arm!="T":
        raise ValueError("FEEDBACK_ARM_UNKNOWN")
    truth=truth_oracle(nodes,edges)
    response={"kind":"EXACT_ATOMIC_TUTOR_FEEDBACK","model_submission_status":score["status"],
              "submitted_proof_valid":score["fully_certified"],
              "ground_truth_holds":truth["holds"],
              "ground_truth_failed_axioms":truth["failed_axioms"]}
    if truth["holds"]:
        response["positive_certificate"]={"kind":"partition",
             "blocks":exact_partition(nodes,edges)}
        response["teaching_point"]="To prove the positive case, check every pair in each block and all cross-block absences."
    else:
        triple=exact_counterexample(nodes,edges)
        response["negative_certificate"]={"kind":"missing_transitive_edge",
            "triple":triple,"premises":atomic_membership(nodes,edges,triple)}
        response["teaching_point"]="An alleged transitivity failure requires xy=true, yz=true, xz=false; inspect all three memberships."
    return canonical(response)


def lesson_prompt(transcript):
    return ("Review ONLY your two previous training attempts and the external "
            "feedback below. Infer a general procedure for verifying a finite "
            "relation on NEW vertex labels, based on what you actually learned. "
            "Do not assume either attempted answer was correct. Do not invent "
            "feedback, tests or source truths. "
            "Produce JSON with exactly a 'rule' string of at most 500 characters, "
            "or {\"abstain\":true}. Do not use training vertex names.\n"+
            canonical(transcript))


def parse_note(raw):
    try:
        o=json.loads(raw.strip())
    except (ValueError,AttributeError):
        return None,"INVALID_NOTE"
    if o=={"abstain":True}:
        return None,"ABSTAIN"
    if (not isinstance(o,dict) or set(o)!={"rule"} or
        not isinstance(o["rule"],str) or not 10<=len(o["rule"])<=500):
        return None,"INVALID_NOTE"
    return o["rule"],"NOTE_VALID"


def equalize(endpoint,prompts,token_counter=None):
    count=token_counter or (lambda s:prompt_budget(endpoint,s))
    output=dict(prompts)
    sizes={a:count(SYSTEM+"\n"+t) for a,t in output.items()}
    target=max(sizes.values())
    for arm in ARMS:
        for _ in range(250):
            if sizes[arm]>=target:break
            output[arm]+="\nNeutral administrative identifier."
            sizes[arm]=count(SYSTEM+"\n"+output[arm])
    final={a:count(SYSTEM+"\n"+t) for a,t in output.items()}
    balanced=(min(final.values())>0 and
        (max(final.values())-min(final.values()))/max(final.values())<=.05)
    return output,final,balanced


def model_call(client,prompt):
    messages=[{"role":"system","content":SYSTEM},{"role":"user","content":prompt}]
    completion=client(messages,MAX_TOKENS)
    raw=completion["text"]
    return {"raw":raw,"raw_sha256":sha256(raw.encode()).hexdigest(),
            "prompt_sha256":sha256(canonical(messages).encode()).hexdigest(),
            "usage":completion["usage"],"time_s":completion["time_s"]}


def save(root,name,data):
    p=Path(root)/name;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def run(root,endpoint,client=None,token_counter=None):
    inputs,oracle=make_holdout()
    llm=client if client is not None else RealClient(endpoint)
    report={"protocol":PROTOCOL,"status":"STARTED",
            "input_manifest_sha256":sha256(canonical(inputs).encode()).hexdigest(),
            "oracle_manifest_sha256":sha256(canonical(oracle).encode()).hexdigest(),
            "model_weights_sha256_expected":MODEL_SHA,"model_weights_updated":False,
            "paid_model_calls":0,"new_competences_certified":0,
            "train_calls":0,"note_calls":0,"evaluation_calls":0,
            "training":{},"evaluation":[]}
    save(root,"model_inputs.json",inputs)
    save(root,"oracle_only.json",oracle)
    save(root,"report.json",report)
    training=make_training()
    save(root,"training_inputs.json",{"cases":training})
    try:
        notes={"D":None}
        for arm in ("G","T"):
            history=[];report["training"][arm]={"traces":[],"note":None}
            for task in training:
                result=model_call(llm,question_text(task))
                feedback=teacher_feedback(task,result["raw"],arm)
                report["training"][arm]["traces"].append({
                    "training_id":task["id"],"output":result,
                    "feedback":feedback,
                    "training_grade":score_raw(result["raw"],tuple(task["nodes"]),
                          frozenset(map(tuple,task["edges"])))})
                # Do not reveal truth-labeled IDs TRAIN_POS/TRAIN_NEG to the
                # rule generator in either arm; preserve IDs only in the audit.
                visible={"nodes":task["nodes"],"edges":task["edges"]}
                history.append({"question":visible,"attempt":result["raw"],
                                "feedback":feedback})
                report["train_calls"]+=1
                save(root,"report.json",report)
            conclusion=model_call(llm,lesson_prompt(history))
            lesson,status=parse_note(conclusion["raw"])
            report["training"][arm]["note"]={"output":conclusion,"status":status,"rule":lesson}
            notes[arm]=lesson
            report["note_calls"]+=1
            save(root,"report.json",report)
        idx={x["id"]:x for x in oracle["answers"]}
        orders=(("D","G","T"),("G","T","D"),("T","D","G"),
                ("D","T","G"),("G","D","T"),("T","G","D"))
        balanced=True
        for i,task in enumerate(inputs["questions"]):
            prompts={a:question_text(task,notes[a]) for a in ARMS}
            prompts,estimated,matched=equalize(endpoint,prompts,token_counter)
            balanced &= matched
            row={"id":task["id"],"order":list(orders[i%len(orders)]),
                 "tokenization_prompt_estimates":estimated,
                 "precall_balanced":matched,"arms":{}}
            report["evaluation"].append(row)
            save(root,"report.json",report)
            for arm in row["order"]:
                raw=model_call(llm,prompts[arm])
                # Oracle is accessed only AFTER generating model output.
                raw["score"]=score_raw(raw["raw"],tuple(task["nodes"]),
                      frozenset(map(tuple,task["edges"])))
                row["arms"][arm]=raw
                report["evaluation_calls"]+=1
                save(root,"report.json",report)
        metrics={}
        for arm in ARMS:
            results=[row["arms"][arm] for row in report["evaluation"]]
            metrics[arm]={"n":len(results),
                "boolean_correct":sum(x["score"]["boolean_correct"] for x in results),
                "axioms_correct":sum(x["score"]["axioms_correct"] for x in results),
                "certificate_correct":sum(x["score"]["certificate_correct"] for x in results),
                "fully_certified":sum(x["score"]["fully_certified"] for x in results),
                "invalid":sum(x["score"]["status"]=="INVALID" for x in results),
                "abstain":sum(x["score"]["status"]=="ABSTAIN" for x in results),
                "prompt_tokens":sum(int(x["usage"].get("prompt_tokens",0)) for x in results),
                "completion_tokens":sum(int(x["usage"].get("completion_tokens",0)) for x in results),
                "model_seconds":round(sum(x["time_s"] for x in results),3)}
        for row in report["evaluation"]:
            tokens=[row["arms"][arm]["usage"].get("prompt_tokens",0) for arm in ARMS]
            if any(type(x) is not int or x<=0 for x in tokens) or (
                max(tokens)-min(tokens))/max(tokens)>.05:
                balanced=False
        full_training_cost={}
        for arm in ("G","T"):
            entries=[x["output"] for x in report["training"][arm]["traces"]]
            entries.append(report["training"][arm]["note"]["output"])
            full_training_cost[arm]={
                "calls":len(entries),
                "prompt_tokens":sum(x["usage"].get("prompt_tokens",0) for x in entries),
                "completion_tokens":sum(x["usage"].get("completion_tokens",0) for x in entries)}
        full_training_cost["D"]={"calls":0,"prompt_tokens":0,"completion_tokens":0}
        total_cost={arm:{"calls":8+full_training_cost[arm]["calls"],
            "prompt_tokens":metrics[arm]["prompt_tokens"]+full_training_cost[arm]["prompt_tokens"],
            "completion_tokens":metrics[arm]["completion_tokens"]+full_training_cost[arm]["completion_tokens"]}
            for arm in ARMS}
        successes={arm:{row["id"] for row in report["evaluation"]
           if row["arms"][arm]["score"]["fully_certified"]} for arm in ARMS}
        positive={x["id"] for x in oracle["answers"] if x["holds"]}
        t=metrics["T"]["fully_certified"]
        gain=bool(balanced and t>=6 and len(successes["T"]&positive)>=3
             and len(successes["T"]-positive)>=3 and
             t-metrics["G"]["fully_certified"]>=2 and
             t-metrics["D"]["fully_certified"]>=2 and
             metrics["T"]["invalid"]==0)
        report["metrics"]=metrics
        report["total_cost_training_included"]=total_cost
        report["actual_eval_prompts_balanced"]=balanced
        report["registered_gain"]=gain
        report["status"]="POINTWISE_CONTEXT_TRANSFER_OBSERVED" if gain else (
           "INDETERMINATE_BUDGET" if not balanced else
           "REGISTERED_CONTEXT_GAIN_NOT_OBSERVED")
        report["durable_skill_proven"]=False
        report["weight_training_performed"]=False
        report["statistical_gain_proven"]=False
    except Exception as exc:
        report["status"]="TECHNICAL_FAILURE"
        report["failure_class"]=type(exc).__name__
        raise
    finally:
        save(root,"report.json",report)
    return report


def main():
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    args=p.parse_args()
    report=run(args.output,args.server)
    print(json.dumps({"status":report["status"],"train_calls":report["train_calls"],
        "note_calls":report["note_calls"],"eval_calls":report["evaluation_calls"],
        "metrics":report["metrics"],"new_competences_certified":0},
        ensure_ascii=False))

if __name__=="__main__":
    main()
