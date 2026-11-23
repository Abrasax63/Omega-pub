"""OMEGA-TRANSFER-05: a blind four-node, witness-vs-generic transfer pilot.

Question: does a model-generated lesson from an exact three-node transitivity
counterexample outperform generic feedback on eight four-node relation
classifications? This measures in-context feedback use, NOT weight learning.
No paid API, no scientific certification, no main changes.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import random

from concept_abstraction_lab import check_axioms
from incremental_math_library import canonical
from real_abstraction_trial import RealClient
from omega_memory_real02 import prompt_budget

PROTOCOL = "OMEGA-HYBRID-TRANSFER-05-2026-11-23"
NODES = ("m0", "m1", "m2", "m3")
TRAIN_NODES = ("a", "b", "c")
AXIOMS = ("reflexive", "symmetric", "transitive")
ARMS = ("D", "G", "W")
SEED = "omega-transfer05-predeclared-finite-relations-v1"
MODEL_SHA = "9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94"
SOURCE_RUN = 45274034725
MAX_COMPLETION = 260
COMMON_SYSTEM = ("You classify finite relations exactly. "
                 "Return one JSON object only, without explanation.")
# Previously exposed *actual* Qwen failure: not an unseen test.
ERROR_EDGES = [["a", "a"], ["b", "b"], ["c", "c"],
               ["a", "b"], ["b", "a"], ["b", "c"], ["c", "b"]]
WITNESS = ("transitive", ["a", "b", "c"])

PAIRS = list(combinations(NODES, 2))


def relation(mask):
    edges = {(x, x) for x in NODES}
    for k, (x,y) in enumerate(PAIRS):
        if (mask >> k) & 1:
            edges.update(((x,y),(y,x)))
    return frozenset(edges)


def orbit(edges):
    """Canonical orbit under the full permutation group S4."""
    return min(tuple(sorted((rename[a],rename[b]) for a,b in edges))
               for order in permutations(NODES)
               for rename in (dict(zip(NODES, order)),))


def oracle(edges):
    facts = check_axioms(NODES, frozenset(edges))
    failed = tuple(a for a in AXIOMS if not facts[a]["holds"])
    return {"holds": not failed, "failed_axioms": list(failed),
            "witnesses": {a:facts[a]["counterexample"] for a in failed}}


def make_manifest():
    """4 nontrivial equivalences + 4 distinct reflexive symmetric nontransitive cases.

    All cases have four nodes. Labels and graph isomorphisms are deduped
    across both classes; the exact 3-node teaching case cannot be present.
    """
    classes, seen = {"positive":[], "negative":[]}, set()
    for mask in sorted(range(64),
            key=lambda m: sha256((SEED + ":select:" + str(m)).encode()).digest()):
        edges = relation(mask)
        key = orbit(edges)
        if key in seen:
            continue
        result = oracle(edges)
        if result["holds"] and mask == 0:
            continue  # forbid the trivial diagonal-only positive example
        name = "positive" if result["holds"] else "negative"
        seen.add(key)
        classes[name].append((mask, edges, result))
    if len(classes["positive"]) < 4 or len(classes["negative"]) < 4:
        raise ValueError("INSUFFICIENT_NONISOMORPHIC_CASES")
    selected = classes["positive"][:4] + classes["negative"][:4]
    selected.sort(key=lambda v: sha256(
        (SEED + ":display:" + str(v[0])).encode()).digest())
    model, truth = [], []
    for mask, edges, reference in selected:
        ident=sha256((SEED + ":case:" + str(mask)).encode()).hexdigest()[:16]
        model.append({"id":ident, "nodes":list(NODES),
                      "edges":[list(e) for e in sorted(edges)]})
        truth.append({"id":ident, "mask":mask, **reference})
    if len({orbit(frozenset(map(tuple,x["edges"]))) for x in model}) != 8:
        raise AssertionError("CASE_ISOMORPH_COLLISION")
    input_manifest = {"protocol":PROTOCOL, "seed":SEED,
                      "cases":model, "answers_excluded":True}
    answer_manifest = {"protocol":PROTOCOL, "seed":SEED,
                       "answers":truth}
    return input_manifest, answer_manifest


def training_prompt(arm):
    if arm not in ("G","W"):
        raise ValueError("ONLY_FEEDBACK_ARMS_TRAIN")
    feedback = ("An external checker rejects your example. No reason supplied."
        if arm == "G" else
        "An exact checker rejects it: the transitivity implication "
        "aRb AND bRc IMPLIES aRc fails on (a,b,c); edges a->b and b->c "
        "are present, edge a->c is missing.")
    return ("Previously, you attempted to construct a positive example of "
            "an equivalence relation on a,b,c. Your exact candidate edges: "
            +canonical(ERROR_EDGES)+". External feedback: "+feedback+
            " Formulate one transferable, general verification rule for "
            "checking unfamiliar finite relations. "
            "Return JSON containing only a string field named rule, or one "
            "boolean field named abstain if uncertain. "
            "Do not give any new candidate graph; do not use any future test.")


def parse_lesson(raw):
    try:
        obj=json.loads(raw.strip())
        if obj == {"abstain":True}:
            return None, "ABSTAIN"
        if not isinstance(obj,dict) or set(obj) != {"rule"} or \
                not isinstance(obj["rule"],str) or not 5 <= len(obj["rule"]) <= 550:
            return None,"INVALID_LESSON"
        return obj["rule"],"VALID_LESSON"
    except (AttributeError,ValueError,TypeError):
        return None,"INVALID_LESSON"


def task_prompt(task, lesson):
    prefix=("Neutral context note. No specific lesson has been provided."
            if lesson is None else "Previous self-generated study note: "+lesson)
    return (prefix+"\nClassify ONLY this given finite relation as an "
            "equivalence relation. Universe: "+canonical(task["nodes"])+
            "; edges: "+canonical(task["edges"])+
            ". Check reflexivity, symmetry and transitivity over ALL four "
            "vertices. Return one JSON object with boolean holds and array "
            "failed_axioms listing all violated properties, or with boolean "
            "abstain true. "
            "No explanations, no other fields.")


def parse_answer(raw, correct):
    try:
        d=json.loads(raw.strip())
    except (AttributeError,ValueError,TypeError):
        return {"status":"INVALID_FORMAT","boolean_correct":False,
                "full_axioms_correct":False}
    if d=={"abstain":True}:
        return {"status":"ABSTAIN","boolean_correct":False,
                "full_axioms_correct":False}
    if not isinstance(d,dict) or set(d)!={"holds","failed_axioms"} or \
            type(d["holds"]) is not bool or not isinstance(d["failed_axioms"],list) or \
            any(type(a) is not str or a not in AXIOMS for a in d["failed_axioms"]) or \
            len(set(d["failed_axioms"]))!=len(d["failed_axioms"]) or \
            d["holds"] != (len(d["failed_axioms"]) == 0):
        return {"status":"INVALID_FORMAT","boolean_correct":False,
                "full_axioms_correct":False}
    bool_ok=d["holds"]==correct["holds"]
    full_ok=bool_ok and set(d["failed_axioms"])==set(correct["failed_axioms"])
    return {"status":"ANSWER","boolean_correct":bool_ok,
            "full_axioms_correct":full_ok,"model_answer":d}


def equalize(endpoint, prompts, token_counter=None):
    counter = token_counter or (lambda text: prompt_budget(endpoint,text))
    """Equal-token measured *complete* task prompts, before the LLM call."""
    count = {a:counter(COMMON_SYSTEM+"\n"+p)
             for a,p in prompts.items()}
    target=max(count.values())
    result=dict(prompts)
    for arm in ARMS:
        for _ in range(130):
            if count[arm]>=target:
                break
            result[arm]+="\nNeutral administrative placeholder."
            count[arm]=counter(COMMON_SYSTEM+"\n"+result[arm])
    final={a:counter(COMMON_SYSTEM+"\n"+p)
           for a,p in result.items()}
    comparable=min(final.values())>0 and \
               (max(final.values())-min(final.values()))/min(final.values())<=.05
    return result,final,comparable


def model_call(client,user_prompt):
    messages=[{"role":"system","content":COMMON_SYSTEM},
              {"role":"user","content":user_prompt}]
    response=client(messages,MAX_COMPLETION)
    return {"raw":response["text"],"usage":response["usage"],
            "time_s":response["time_s"],
            "response_sha256":sha256(response["text"].encode()).hexdigest(),
            "prompt_sha256":sha256(canonical(messages).encode()).hexdigest(),
            "max_tokens":MAX_COMPLETION}


def save(root, name, payload):
    path=Path(root)/name
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",
                    encoding="utf-8")


def run(root, endpoint, injected_client=None, token_counter=None):
    """One frozen A/B/C comparison. No training checkpoints, no Web search."""
    model_inputs, oracle_only=make_manifest()
    client = injected_client if injected_client is not None else RealClient(endpoint)
    report={"protocol":PROTOCOL, "stage":"PREREGISTERED_START",
            "source_run_exposed":SOURCE_RUN,"seed":SEED,
            "model_weights_sha256_expected":MODEL_SHA,
            "model_weights_modified":False,"paid_api_calls":0,
            "certified_new_competences":0,"train_calls":0,
            "eval_calls":0,"tasks":[]}
    save(root,"model_inputs.json",model_inputs)
    save(root,"oracle_only.json",oracle_only)
    report["manifest_sha256"]=sha256(canonical(model_inputs).encode()).hexdigest()
    report["oracle_sha256"]=sha256(canonical(oracle_only).encode()).hexdigest()
    save(root,"report.json",report)
    if injected_client is None:
        # runtime model identity is checked by workflow's pinned sha256sum
        pass
    try:
        lessons={"D":None}
        report["training"]={}
        for arm in ("G","W"):
            response=model_call(client,training_prompt(arm))
            rule,status=parse_lesson(response["raw"])
            lessons[arm]=rule
            report["training"][arm]={**response,"lesson_status":status,
                                      "lesson":rule}
            report["train_calls"]+=1
            save(root,"report.json",report)
        tasks=model_inputs["cases"]
        key={x["id"]:x for x in oracle_only["answers"]}
        orders=[("D","G","W"),("G","W","D"),("W","D","G"),
                ("D","W","G"),("G","D","W"),("W","G","D")]
        all_comp=True
        for i,task in enumerate(tasks):
            prompts={a:task_prompt(task,lessons[a]) for a in ARMS}
            prompts,approx_tokens,balanced=equalize(endpoint,prompts,token_counter)
            all_comp=all_comp and balanced
            t={"id":task["id"],"question_sha256":sha256(canonical(task).encode()).hexdigest(),
               "order":list(orders[i%len(orders)]),
               "prompt_tokens_estimated":approx_tokens,
               "prompt_within_five_percent":balanced,"arms":{}}
            report["tasks"].append(t)
            save(root,"report.json",report)
            for arm in t["order"]:
                response=model_call(client,prompts[arm])
                score=parse_answer(response["raw"],key[task["id"]])
                t["arms"][arm]={**response,"scoring":score}
                report["eval_calls"]+=1
                save(root,"report.json",report)
        actual_comparable=True
        for t in report["tasks"]:
            tokens=[t["arms"][a]["usage"].get("prompt_tokens",0) for a in ARMS]
            if any(type(k) is not int or k<=0 for k in tokens) or \
                    (max(tokens)-min(tokens))/max(tokens)>.05:
                actual_comparable=False
        stats={}
        for arm in ARMS:
            replies=[t["arms"][arm] for t in report["tasks"]]
            stats[arm]={
                "n":len(replies),
                "boolean_correct":sum(x["scoring"]["boolean_correct"] for x in replies),
                "full_axioms_correct":sum(x["scoring"]["full_axioms_correct"] for x in replies),
                "invalid":sum(x["scoring"]["status"]=="INVALID_FORMAT" for x in replies),
                "abstain":sum(x["scoring"]["status"]=="ABSTAIN" for x in replies),
                "prompt_tokens":sum(x["usage"].get("prompt_tokens",0) for x in replies),
                "completion_tokens":sum(x["usage"].get("completion_tokens",0) for x in replies),
                "seconds":round(sum(x["time_s"] for x in replies),3)}
        report["results"]={"stats":stats,
            "actual_prompts_balanced":actual_comparable,
            "approximate_prompts_balanced":all_comp,
            "W_minus_G_full":stats["W"]["full_axioms_correct"]-stats["G"]["full_axioms_correct"],
            "W_minus_D_full":stats["W"]["full_axioms_correct"]-stats["D"]["full_axioms_correct"],
            "registered_gain_observed":bool(
                actual_comparable and all_comp and
                stats["W"]["full_axioms_correct"]>=6 and
                stats["W"]["full_axioms_correct"]-stats["G"]["full_axioms_correct"]>=2 and
                stats["W"]["full_axioms_correct"]-stats["D"]["full_axioms_correct"]>=2 and
                stats["W"]["invalid"]==0),
            "statistical_significance_claimed":False,
            "durable_learning_claimed":False}
        report["stage"]="POINTWISE_GAIN_OBSERVED" if report["results"]["registered_gain_observed"] \
           else ("INDETERMINATE_BUDGETS" if not actual_comparable or not all_comp
                 else "PRE_REGISTERED_GAIN_NOT_OBSERVED")
    except Exception as exc:
        report["stage"]="TECHNICAL_FAILURE"
        report["error_type"]=type(exc).__name__
        raise
    finally:
        report["calls"]=len(client.calls) if hasattr(client,"calls") else None
        save(root,"report.json",report)
    return report


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    args=p.parse_args()
    r=run(args.output,args.server)
    print(json.dumps({"stage":r["stage"],"calls":r["calls"],
                      "results":r.get("results",{}).get("stats"),
                      "new_competences_certified":0},ensure_ascii=False))


if __name__=="__main__":
    main()
