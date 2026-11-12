"""P5-REAL-03: new dual-Qwen response generation; frozen typed parser; online adaptation.

The policy observes only the public task, parsed model answer, elapsed step,
and outcomes of its own purchased exact verifications. Hidden model identity,
phase, and labels for unverified answers belong to the evaluator only.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
import gc
import json
import math
from pathlib import Path

import p5_real02_multimodel as base
from p5_real03_semantic import extract,PARSER_VERSION

PROTOCOL="P5-REAL-03"
STATUS="REAL_OPEN_MODELS_PUBLIC_AUTHOR_DATA_NOT_EXTERNAL_VALIDATION"
SEED=20261112
KINDS=("MUL","CRT","RATE","INJ")
MODELS={
    "small":("Qwen/Qwen2.5-0.5B-Instruct",
             "7ae557604adf67be50417f59c2c2f167def9a775"),
    "large":("Qwen/Qwen2.5-1.5B-Instruct",
             "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"),
}
BUDGET=24
HORIZON=64
COST={"MUL":.20,"CRT":.45,"RATE":.30,"INJ":.15}
MAX_NEW_TOKENS=56
GAMMA=.70
WINDOW=6
ALARM_ON=.30
ALARM_OFF=.15
POLICIES=("direct","abstain","periodic","static_kind","online_beta",
          "discount_beta","window_beta","omega_candidate","omega_no_alarm")

def hash_num(*parts):
    return int.from_bytes(sha256(
        ("P5REAL03|"+"|".join(map(str,parts))).encode("utf-8")
    ).digest()[:8],"big")

def make_case(kind,index):
    if kind not in KINDS or type(index) is not int or not 0<=index<20:
        raise ValueError("case outside preregistered space")
    if kind=="MUL":
        a=19+hash_num(kind,index,"a")%83
        b=(3+hash_num(kind,index,"b")%8) if index%3==0 else (
            11+hash_num(kind,index,"b")%43)
        params=(a,b)
        question=f"Combien vaut exactement {a} multiplié par {b} ?"
    elif kind=="CRT":
        m=(5,7,9,11,13)[hash_num(kind,index,"m")%5]
        n=(8,16,17,19)[hash_num(kind,index,"n")%4]
        a=hash_num(kind,index,"a")%m
        b=hash_num(kind,index,"b")%n
        params=(m,a,n,b)
        question=(f"Donne le plus petit x entier supérieur ou égal à zéro "
                  f"pour lequel x modulo {m} = {a} et x modulo {n} = {b}.")
    elif kind=="RATE":
        denoms=[11+hash_num(kind,index,"d",j)%75 for j in range(4)]
        succ=[1+hash_num(kind,index,"s",j)%(d-1)
              for j,d in enumerate(denoms)]
        a,b,c,d=denoms
        x,y,z,w=succ
        if (x+y)*(c+d)==(z+w)*(a+b):
            y=y-1 if y>1 else y+1
        params=(x,a,y,b,z,c,w,d)
        question=(f"Dans deux groupes A et B, les succès sont respectivement "
                  f"pour A : {x} sur {a}, puis {y} sur {b} ; "
                  f"pour B : {z} sur {c}, puis {w} sur {d}. "
                  "Quel groupe a le meilleur taux global de succès ?")
    else:
        n=6
        images=sorted(range(n),key=lambda j:(
            hash_num(kind,index,"permutation",j),j))
        if index%2:
            pos=1+hash_num(kind,index,"duplicate")%(n-1)
            images[pos]=images[0]
        params=tuple(images)
        question=(f"Sur X = {{0, 1, ..., {n-1}}}, "
                  f"f est définie par [f(0), ..., f({n-1})] = "
                  f"{images}. La fonction f est-elle injective ?")
    return {
        "id":f"REAL03-{kind}-{index:02d}",
        "kind":kind,"index":index,"parameters":params,
        "question":question,
        "split":"calibration" if index<4 else "evaluation",
    }

def universe():
    rows=[make_case(kind,i) for kind in KINDS for i in range(20)]
    assert len(rows)==80
    assert len({r["id"] for r in rows})==80
    assert len({r["question"] for r in rows})==80, "duplicate public question"
    assert len({(r["kind"],tuple(r["parameters"])) for r in rows})==80
    for r in rows:
        assert reference(r)==verify_exact(r),f"dual oracle disagreement: {r['id']}"
    return rows

def reference(row):
    # A separate oracle from the running tool; never called by a policy.
    kind,p=row["kind"],row["parameters"]
    if kind=="MUL":return str(p[0]*p[1])
    if kind=="CRT":
        m,a,n,b=p
        assert math.gcd(m,n)==1
        return str((a+m*(((b-a)*pow(m,-1,n))%n))%(m*n))
    if kind=="RATE":
        x,a,y,b,z,c,w,d=p
        u=Fraction(x+y,a+b)
        v=Fraction(z+w,c+d)
        assert u!=v
        return "A" if u>v else "B"
    if kind=="INJ":
        return "OUI" if len(p)==len(set(p)) else "NON"
    raise AssertionError("invalid question")

def verify_exact(row):
    # Independent, implementationally distinct exact tool.
    kind,p=row["kind"],row["parameters"]
    if kind=="MUL":
        x,y=p
        s=0
        for _ in range(y):s+=x
        return str(s)
    if kind=="CRT":
        m,a,n,b=p
        return str(next(x for x in range(m*n) if x%m==a and x%n==b))
    if kind=="RATE":
        x,a,y,b,z,c,w,d=p
        q=(x+y)*(c+d)-(z+w)*(a+b)
        assert q!=0
        return "A" if q>0 else "B"
    if kind=="INJ":
        for i in range(len(p)):
            for j in range(i+1,len(p)):
                if p[i]==p[j]:return "NON"
        return "OUI"
    raise AssertionError("invalid question")

def generation_plan():
    calibration=[(model,make_case(kind,i)) for model in ("small","large")
                 for kind in KINDS for i in range(4)]
    evaluation=[]
    for phase,model in enumerate(("large","small","large","small")):
        offset=(4,12,8,16)[phase]
        for k in range(4):
            for kind in KINDS:
                evaluation.append((model,make_case(kind,offset+k)))
    assert len(calibration)==32 and len(evaluation)==64
    assert len({row["id"] for _,row in evaluation})==64
    assert not {row["id"] for _,row in calibration}&{
        row["id"] for _,row in evaluation}
    return calibration,evaluation

def prompt(row):
    return [
        {"role":"system","content":"Réponds de façon concise, en français."},
        {"role":"user","content":row["question"]+
         "\nDonne la réponse finale sur une seule ligne, sans calcul ni exemple."},
    ]

def public_view(row,output):
    return {
        "kind":row["kind"],
        "question":row["question"],
        "model_output":output["text"],
        "parsed":output["parsed"],
        "parse_reason":output["parse_reason"],
        "verify_cost":COST[row["kind"]],
    }

def _calibration(calibrated):
    accum={kind:{"correct":0,"total":0} for kind in KINDS}
    for row,output in calibrated:
        stats=accum[row["kind"]]
        stats["correct"]+=int(output["parsed"]==reference(row))
        stats["total"]+=1
    assert all(v["total"]==8 for v in accum.values())
    return accum

class Selector:
    """No access to gold, tool or hidden model index in decide/observe."""
    def __init__(self,name,labeled_calibration):
        if name not in POLICIES:raise ValueError("unknown policy")
        self.name=name
        self.prior=_calibration(labeled_calibration)
        self.prior_global=sum(v["correct"] for v in self.prior.values())/32
        self.evidence=defaultdict(list)
        self.all_checks=[]
        self.used=0
        self.active=False
        self.alarm_events=[]
        self.audit=[]
        self.plan_version=None
        if name.startswith("omega_"):
            from planner import plan_mission
            p=plan_mission({
                "question":"Vérifier les réponses et adapter la politique "
                           "lorsqu'un changement de fiabilité est observable.",
                "mission_type":"general",
                "decision_context":{
                    "blocking_uncertainty":"Fiabilité du modèle non établie",
                    "verification":"Exécuter un calcul exact choisi sous budget",
                    "verification_effect":"Corriger la réponse et mettre à jour les estimations",
                },
            })
            if p["next_action"]["action"]!="verify":
                raise AssertionError("P1 did not recommend verification")
            self.plan_version=p["planner_version"]

    def _p(self,kind):
        count=self.prior[kind]["total"]
        good=self.prior[kind]["correct"]
        history=self.evidence[kind]
        if self.name in ("online_beta","omega_candidate","omega_no_alarm"):
            count+=len(history)
            good+=sum(history)
        elif self.name=="discount_beta":
            w=1.0
            for correct in reversed(history):
                count+=w
                good+=w*correct
                w*=GAMMA
        elif self.name=="window_beta":
            window=history[-WINDOW:]
            count+=len(window)
            good+=sum(window)
        p=(good+1)/(count+2)
        if self.name=="omega_candidate" and self.active and len(self.all_checks)>=WINDOW:
            local=sum(x["correct"] for x in self.all_checks[-WINDOW:])/WINDOW
            p=.5*p+.5*local
        return p

    def decide(self,t,view):
        if type(t) is not int or not 0<=t<HORIZON:
            raise ValueError("invalid time index")
        required={"kind","question","model_output","parsed",
                  "parse_reason","verify_cost"}
        if not isinstance(view,dict) or set(view)!=required or view["kind"] not in KINDS:
            raise ValueError("hidden or malformed public view")
        if self.name=="direct":return "DIRECT"
        if self.name=="abstain":return "ABSTAIN"
        allowed=self.used<((t+1)*BUDGET)//HORIZON
        if self.name=="periodic":return "VERIFY" if allowed else "DIRECT"
        p=self._p(view["kind"])
        u={"ABSTAIN":.05,
           "DIRECT":.05 if view["parsed"] is None else 3*p-2,
           "VERIFY":1-view["verify_cost"] if allowed else -100.0}
        order=("ABSTAIN","DIRECT","VERIFY")
        return max(order,key=lambda x:(u[x],-order.index(x)))

    def observe(self,t,view,correct):
        if type(correct) is not bool:
            raise ValueError("feedback must be a verified Boolean")
        if self.used>=((t+1)*BUDGET)//HORIZON:
            raise AssertionError("attempted overdraw of paced credit")
        self.evidence[view["kind"]].append(int(correct))
        self.all_checks.append({
            "t":t,"kind":view["kind"],"correct":int(correct)})
        self.used+=1
        event=None
        if self.name=="omega_candidate" and len(self.all_checks)>=WINDOW:
            recent=sum(r["correct"] for r in self.all_checks[-WINDOW:])/WINDOW
            gap=abs(recent-self.prior_global)
            if not self.active and gap>=ALARM_ON:
                self.active=True
                event="alarm_on"
            elif self.active and gap<=ALARM_OFF:
                self.active=False
                event="alarm_off"
            if event:
                self.alarm_events.append({"t":t,"event":event,
                                          "gap":round(gap,6)})
        self.audit.append({
            "t":t,"kind":view["kind"],"verified_correct":bool(correct),
            "evidence_count":len(self.all_checks),"alarm_event":event,
            "alarm_active":self.active,
        })

def evaluate(calibration,evaluation,outputs):
    expected={(m,r["id"]) for m,r in calibration+evaluation}
    if len(outputs)!=96 or set(outputs)!=expected:
        raise ValueError("incomplete or duplicated real model outputs")
    labeled=[(row,outputs[(model,row["id"])]) for model,row in calibration]
    results={}
    for policy in POLICIES:
        s=Selector(policy,labeled)
        moves=[]
        for t,(model,row) in enumerate(evaluation):
            out=outputs[(model,row["id"])]
            view=public_view(row,out)
            action=s.decide(t,view)
            if action=="VERIFY":
                checked=verify_exact(row)
                s.observe(t,view,out["parsed"]==checked)
                final=checked
                utility=1-COST[row["kind"]]
            elif action=="DIRECT":
                final=out["parsed"]
                utility=(1 if final==reference(row) else -2) if final is not None else .05
            else:
                final=None
                utility=.05
            # Evaluator owns reference and model metadata; this record is
            # written only AFTER decide + observe.
            truth=reference(row)
            moves.append({
                "t":t,"phase_evaluator_only":t//16,
                "model_evaluator_only":model,"question_evaluator_only":row["id"],
                "kind":row["kind"],"model_correct_evaluator_only":
                out["parsed"]==truth,"answer_evaluator_only":truth,
                "action":action,"final":final,"utility":round(utility,5),
                "parsed":out["parsed"],"parse_reason":out["parse_reason"],
            })
        results[policy]={
            "utility":round(sum(m["utility"] for m in moves),5),
            "verified":s.used,
            "correct_published":sum(m["final"]==m["answer_evaluator_only"] and
                                     m["final"] is not None for m in moves),
            "wrong_published":sum(m["final"]!=m["answer_evaluator_only"] and
                                   m["final"] is not None for m in moves),
            "abstained":sum(m["final"] is None for m in moves),
            "verifier_cost":round(sum(COST[m["kind"]] for m in moves
                                      if m["action"]=="VERIFY"),5),
            "alarm_events":s.alarm_events,
            "logged_verification_feedback":s.audit,
            "planner_version":s.plan_version,
            "trajectory":moves,
        }
        assert results[policy]["verified"]<=BUDGET
    assert results["online_beta"]["trajectory"]==results["omega_no_alarm"]["trajectory"]
    return results

def preflight():
    rows=universe()
    cal,ev=generation_plan()
    pub=[{"model":model,"id":row["id"],"question":row["question"],
          "kind":row["kind"],"split":row["split"]}
         for model,row in cal+ev]
    return {
        "protocol":PROTOCOL,"status":"FROZEN_PREFLIGHT",
        "parser":PARSER_VERSION,"questions":len(rows),
        "actual_generations_planned":96,"calibration":32,"test":64,
        "cases_sha256":sha256(json.dumps(pub,sort_keys=True,
              ensure_ascii=False).encode("utf-8")).hexdigest(),
        "paid_api_calls":0,"private_data_access":False,
    }

def generate(output):
    frozen=preflight()
    cal,ev=generation_plan()
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    actual={}
    revisions={}
    for model_key in ("large","small"):
        ident,rev=MODELS[model_key]
        tokenizer=AutoTokenizer.from_pretrained(ident,revision=rev)
        model=AutoModelForCausalLM.from_pretrained(
            ident,revision=rev,torch_dtype=torch.float32).eval()
        revisions[model_key]=getattr(model.config,"_commit_hash",None)
        tasks=[row for mdl,row in cal+ev if mdl==model_key]
        assert len(tasks)==48
        for row in tasks:
            msg=prompt(row)
            query=tokenizer.apply_chat_template(
                msg,tokenize=False,add_generation_prompt=True)
            inp=tokenizer([query],return_tensors="pt")
            with torch.inference_mode():
                response=model.generate(**inp,do_sample=False,
                   max_new_tokens=MAX_NEW_TOKENS,
                   pad_token_id=tokenizer.eos_token_id)
            prefix=inp["input_ids"].shape[1]
            continuation=response[0][prefix:]
            raw=tokenizer.decode(continuation,skip_special_tokens=True)
            parsed,reason=extract(raw,row["kind"])
            actual[(model_key,row["id"])]={
                "text":raw,"parsed":parsed,"parse_reason":reason,
                "input_tokens":int(prefix),
                "output_tokens":int(continuation.shape[0]),
            }
            print("REAL03_GENERATION",model_key,row["id"],
                  "parsed="+str(parsed),"reason="+reason,flush=True)
        del model,tokenizer
        gc.collect()
    result=evaluate(cal,ev,actual)
    delta=result["omega_candidate"]["utility"]-result["discount_beta"]["utility"]
    diffs=sum(a["action"]!=b["action"]
              for a,b in zip(result["omega_candidate"]["trajectory"],
                             result["omega_no_alarm"]["trajectory"]))
    test=[{"model":mdl,"id":row["id"],"kind":row["kind"],
           "correct":actual[(mdl,row["id"])]["parsed"]==reference(row),
           "parsed":actual[(mdl,row["id"])]["parsed"]}
          for mdl,row in ev]
    raw=[{"model":mdl,"id":row["id"],"question":row["question"],
          "kind":row["kind"],"split":row["split"],
          "reference_evaluator_only":reference(row),
          **actual[(mdl,row["id"])]} for mdl,row in cal+ev]
    phases={str(k):{
        "model":("large","small","large","small")[k],
        "correct":sum(r["correct"] for r in test[16*k:16*(k+1)]),
        "unparsed":sum(r["parsed"] is None for r in test[16*k:16*(k+1)]),
    } for k in range(4)}
    report={
        "protocol":PROTOCOL,"status":STATUS,
        "frozen_preflight":frozen,
        "revisions":revisions,"actual_generations":len(actual),
        "test_decisions":HORIZON,"paid_api_calls":0,"private_data_used":False,
        "model_evaluation":{
            "correct":sum(r["correct"] for r in test),
            "unparsed":sum(r["parsed"] is None for r in test),
            "by_phase":phases,
            "by_kind":{kind:{
                "correct":sum(r["correct"] for r in test if r["kind"]==kind),
                "unparsed":sum(r["parsed"] is None for r in test if r["kind"]==kind),
                "count":sum(r["kind"]==kind for r in test)}
                for kind in KINDS},
        },
        "primary_omega_minus_discount":round(delta,5),
        "different_actions_vs_no_alarm":diffs,
        "policy_results":result,
        "raw_model_outputs":raw,
        "limitations":[
            "Public author-designed tasks, not independently sourced or blinded",
            "Model switching experimentally staged, not natural environment change",
            "Exact narrow-domain verifiers, no unreliable external sources",
            "Calibration 32 model outputs; evaluation just one 64-step sequence",
            "P1 plans but does not independently implement the adaptive controller",
            "Parser adapted to old experiment forms, locked for this new experiment",
        ],
    }
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,sort_keys=True,ensure_ascii=False,
                indent=2)+"\n",encoding="utf-8")
    print("P5_REAL03_SUMMARY "+json.dumps({
        "status":STATUS,"real_generations":len(actual),
        "model_evaluation":report["model_evaluation"],
        "primary_omega_minus_discount":report["primary_omega_minus_discount"],
        "different_actions_vs_no_alarm":diffs,
        "policies":{k:{field:v[field] for field in (
            "utility","verified","correct_published",
            "wrong_published","abstained")}
                    |{"alarm_count":len(v["alarm_events"])}
                    for k,v in result.items()},
        "revisions":revisions,
    },sort_keys=True,ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--output",default="p5_real03_results.json")
    args=ap.parse_args()
    if args.preflight:
        print(json.dumps(preflight(),sort_keys=True,ensure_ascii=False))
    else:generate(args.output)

if __name__=="__main__":
    main()
