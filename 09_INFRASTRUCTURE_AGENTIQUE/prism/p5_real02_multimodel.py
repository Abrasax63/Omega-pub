"""P5-REAL-02. Two genuine open-weight models; hidden changes; budgeted feedback.

Public author-generated pilot, not an external holdout; the experimental
Omega decision layer is NOT the existing P1 planner learning by itself.
The verifier is real exact code, and ONLY paid verifications reveal labels.
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
import re

from planner import plan_mission

PROTOCOL="P5-REAL-02"
STATUS="PUBLIC_REAL_MULTIMODEL_EXPLORATORY_NOT_INDEPENDENT"
MODELS={
    "small":("Qwen/Qwen2.5-0.5B-Instruct","7ae557604adf67be50417f59c2c2f167def9a775"),
    "large":("Qwen/Qwen2.5-1.5B-Instruct",None),
}
KINDS=("MUL","CRT","RATE","INJ")
HORIZON=64
BUDGET=24
MAX_NEW_TOKENS=56
COST={"MUL":.20,"CRT":.45,"RATE":.30,"INJ":.15}
POLICIES=("direct","abstain","periodic","static_kind","online_beta",
          "discount_beta","omega_candidate","omega_no_alarm")
OUTPUT_RE=re.compile(
    r"(?i)^\s*(?:(?:réponse(?:\s+finale)?|resultat|résultat)\s*[:=]\s*)?"
    r"(OUI|NON|A|B|[0-9]+)\b\s*(?:[.!]?|[:;,-].*)?$"
)

def _rand(*parts):
    return int.from_bytes(sha256(
        ("P5REAL02|"+"|".join(map(str,parts))).encode("utf-8")
    ).digest()[:8],"big")

def case(kind,index):
    if kind not in KINDS or type(index) is not int or not 0<=index<20:
        raise ValueError("unregistered case")
    if kind=="MUL":
        a=13+_rand(kind,index,"a")%86
        b=(2+_rand(kind,index,"b")%8) if index%3==0 else (
            12+_rand(kind,index,"b")%48)
        parameters=(a,b)
        question=f"Quel est le produit exact de {a} et de {b} ?"
    elif kind=="CRT":
        m=(5,7,9,11,13)[_rand(kind,index,"m")%5]
        n=(8,16,17,19)[_rand(kind,index,"n")%4]
        a=_rand(kind,index,"a")%m
        b=_rand(kind,index,"b")%n
        parameters=(m,a,n,b)
        question=(f"Quel est le plus petit entier x positif ou nul tel que "
                  f"x modulo {m} vaut {a} et x modulo {n} vaut {b} ?")
    elif kind=="RATE":
        totals=[12+_rand(kind,index,"total",j)%85 for j in range(4)]
        succ=[1+_rand(kind,index,"succ",j)%(n-1)
              for j,n in enumerate(totals)]
        a,b,c,d=totals
        x,y,z,w=succ
        if (x+y)*(c+d)==(z+w)*(a+b):
            y=y+1 if y+1<b else y-1
        parameters=(x,a,y,b,z,c,w,d)
        question=(f"Equipe A : {x}/{a} puis {y}/{b} succès ; "
                  f"équipe B : {z}/{c} puis {w}/{d} succès. "
                  "Quelle équipe a le taux global de succès le plus élevé ?")
    else:
        n=5+_rand(kind,index,"n")%2
        shift=_rand(kind,index,"shift")%n
        values=[(j+shift)%n for j in range(n)]
        if index%2:
            pos=1+_rand(kind,index,"dup")%(n-1)
            values[pos]=values[0]
        parameters=tuple(values)
        question=(f"Sur X = {{0, ..., {n-1}}}, la fonction f est définie "
                  f"par la liste des images [f(0),...,f({n-1})] = "
                  f"{values}. Est-elle injective ?")
    return {
        "id":f"P5REAL02-{kind}-{index:02d}",
        "kind":kind,"index":index,"question":question,"parameters":parameters,
        "split":"calibration" if index<4 else "evaluation",
    }

def all_cases():
    rows=[case(k,j) for k in KINDS for j in range(20)]
    assert len({r["id"] for r in rows})==80
    for r in rows:
        assert reference(r)==verify_exact(r)
    return rows

def reference(row):
    p=row["parameters"]
    if row["kind"]=="MUL":
        a,b=p
        return str(a*b)
    if row["kind"]=="CRT":
        m,a,n,b=p
        assert math.gcd(m,n)==1
        return str((a+m*(((b-a)*pow(m,-1,n))%n))%(m*n))
    if row["kind"]=="RATE":
        x,a,y,b,z,c,w,d=p
        u=Fraction(x+y,a+b)
        v=Fraction(z+w,c+d)
        if u==v:raise AssertionError("rate tie")
        return "A" if u>v else "B"
    if row["kind"]=="INJ":
        return "OUI" if len(set(p))==len(p) else "NON"
    raise ValueError("unsupported kind")

def verify_exact(row):
    """Independent exact algorithm; invoked for test ONLY when paid."""
    p=row["parameters"]
    if row["kind"]=="MUL":
        a,b=p
        result=0
        for _ in range(b):result+=a
        return str(result)
    if row["kind"]=="CRT":
        m,a,n,b=p
        for x in range(m*n):
            if x%m==a and x%n==b:return str(x)
        raise AssertionError("CRT must have a solution")
    if row["kind"]=="RATE":
        x,a,y,b,z,c,w,d=p
        lhs=(x+y)*(c+d)
        rhs=(z+w)*(a+b)
        if lhs==rhs:raise AssertionError("rate tie")
        return "A" if lhs>rhs else "B"
    if row["kind"]=="INJ":
        for i in range(len(p)):
            for j in range(i+1,len(p)):
                if p[i]==p[j]:return "NON"
        return "OUI"
    raise ValueError("unsupported kind")

def parse(text,kind):
    if kind not in KINDS or not isinstance(text,str):return None
    lines=[s.strip().strip("\u200b") for s in text.splitlines() if s.strip()]
    if not lines:return None
    match=OUTPUT_RE.fullmatch(lines[0])
    if not match:return None
    value=match.group(1).upper()
    if kind in ("MUL","CRT"):
        return value if value.isdecimal() else None
    if kind=="RATE":
        return value if value in ("A","B") else None
    return value if value in ("OUI","NON") else None

def prompt(row):
    # No A/B sample in numeric prompts; prevent contamination from examples.
    question=row["question"]
    return [
        {"role":"system","content":"Réponds de manière concise en français."},
        {"role":"user","content":question+"\n"
            "Donne uniquement le résultat final sur une ligne, "
            "sans justification ni exemple."},
    ]

def generation_plan():
    """96 distinct (model, question) pairs, 80 question IDs in total."""
    calibrate=[(model,case(kind,j)) for model in ("small","large")
               for kind in KINDS for j in range(4)]
    assert len(calibrate)==32
    eval_plan=[]
    for phase,model in enumerate(("large","small","large","small")):
        offset=(4 if phase==0 else 8 if phase==2 else
                12 if phase==1 else 16)
        for step in range(4):
            for kind in KINDS:
                eval_plan.append((model,case(kind,offset+step)))
    assert len(eval_plan)==64
    assert len({row["id"] for _,row in eval_plan})==64
    assert not {r["id"] for _,r in calibrate}&{r["id"] for _,r in eval_plan}
    assert Counter(x for x,_ in eval_plan)=={"large":32,"small":32}
    return calibrate,eval_plan

def public_input(row,out):
    """MUST NOT contain model ID, phase, case ID/index, gold, hidden state."""
    return {
        "kind":row["kind"],"question":row["question"],
        "model_output":out["text"],"parsed":out["parsed"],
        "verification_cost":COST[row["kind"]],
    }

def _calibration_totals(calibrated):
    counts=defaultdict(lambda:{"right":0,"total":0})
    for row,out in calibrated:
        c=counts[row["kind"]]
        c["total"]+=1
        c["right"]+=int(out["parsed"]==reference(row))
    return dict(counts)

class Policy:
    """No oracle/reference access after calibration, only own verified feedback."""
    def __init__(self,name,calibration):
        if name not in POLICIES:raise ValueError("unknown policy")
        self.name=name
        self.calibration=_calibration_totals(calibration)
        self.base_accuracy=(sum(x["right"] for x in self.calibration.values())/
                            sum(x["total"] for x in self.calibration.values()))
        self.feedback=defaultdict(list)
        self.all_checked=[]
        self.verified=0
        self.alarm=False
        self.alarms=[]
        self.alarm_off=[]
        self.log=[]
        self.plan_version=None
        if name.startswith("omega_"):
            plan=plan_mission({
                "question":"Quand vérifier la réponse d'un modèle et réviser "
                           "son estimation de fiabilité après contradiction ?",
                "mission_type":"general",
                "decision_context":{
                    "blocking_uncertainty":"Le taux d'erreur du modèle peut varier",
                    "verification":"Vérification arithmétique et logique exacte",
                    "verification_effect":"Actualiser le niveau de confiance",
                },
            })
            if plan["next_action"]["action"]!="verify":
                raise AssertionError("P1 plan did not request verification")
            self.plan_version=plan["planner_version"]

    def _estimate(self,kind):
        stats=self.calibration[kind]
        correct=stats["right"]
        total=stats["total"]
        seen=self.feedback[kind]
        if self.name in ("online_beta","omega_candidate","omega_no_alarm"):
            correct+=sum(seen)
            total+=len(seen)
        elif self.name=="discount_beta":
            # exponential fading with fixed gamma=0.70
            weight=1.0
            wsum=0.0
            wgood=0.0
            for v in reversed(seen):
                wsum+=weight
                wgood+=weight*v
                weight*=.70
            correct+=wgood
            total+=wsum
        p=(correct+1)/(total+2)
        if self.name=="omega_candidate" and self.alarm and len(seen)>=2:
            sample=seen[-6:]
            p=(sum(sample)+1)/(len(sample)+2)
        return p

    def decide(self,t,view):
        if type(t) is not int or not 0<=t<HORIZON:
            raise ValueError("invalid time")
        if set(view)!={"kind","question","model_output","parsed","verification_cost"}:
            raise ValueError("unexpected hidden features in decision")
        if self.name=="direct":return "DIRECT"
        if self.name=="abstain":return "ABSTAIN"
        available=min(BUDGET,((t+1)*BUDGET)//HORIZON)
        allowed=self.verified<available
        if self.name=="periodic":
            return "VERIFY" if allowed else "DIRECT"
        p=self._estimate(view["kind"])
        u={"ABSTAIN":.05,
           "DIRECT":.05 if view["parsed"] is None else 3*p-2,
           "VERIFY":1-view["verification_cost"] if allowed else -10.0}
        order=("ABSTAIN","DIRECT","VERIFY")
        return max(order,key=lambda a:(u[a],-order.index(a)))

    def observe_verification(self,t,view,correct):
        if type(correct) is not bool:
            raise ValueError("verified feedback must be a boolean")
        if self.verified>=min(BUDGET,((t+1)*BUDGET)//HORIZON):
            raise AssertionError("budget or paced-credit violation")
        self.feedback[view["kind"]].append(int(correct))
        self.all_checked.append({
            "t":t,"kind":view["kind"],"model_correct":correct})
        self.verified+=1
        event=None
        if self.name=="omega_candidate" and len(self.all_checked)>=6:
            recent=sum(x["model_correct"] for x in self.all_checked[-6:])/6
            deviation=abs(recent-self.base_accuracy)
            if not self.alarm and deviation>.35:
                self.alarm=True
                self.alarms.append(t)
                event="alarm_on"
            elif self.alarm and deviation<=.20:
                self.alarm=False
                self.alarm_off.append(t)
                event="alarm_off"
        self.log.append({"t":t,"kind":view["kind"],"correct":correct,
            "alarm_active":self.alarm,"event":event,
            "verified_so_far":self.verified})

def score_policies(calibration,eval_plan,outputs):
    expect={(model,row["id"]) for model,row in calibration+eval_plan}
    if set(outputs)!=expect or len(outputs)!=96:
        raise ValueError("incomplete REAL MODEL generations")
    calib=[(r,outputs[(model,r["id"])]) for model,r in calibration]
    results={}
    for policy_name in POLICIES:
        pol=Policy(policy_name,calib)
        trajectory=[]
        for t,(model,row) in enumerate(eval_plan):
            out=outputs[(model,row["id"])]
            view=public_input(row,out)
            action=pol.decide(t,view)
            if action=="VERIFY":
                correct_answer=verify_exact(row)
                original_correct=(out["parsed"]==correct_answer)
                pol.observe_verification(t,view,original_correct)
                final=correct_answer
                gain=1.0-COST[row["kind"]]
            elif action=="DIRECT":
                final=out["parsed"]
                gain=(1 if final==reference(row) else -2) if final is not None else .05
            else:
                final=None
                gain=.05
            trajectory.append({
                "t":t,"phase_index_evaluator_only":t//16,
                "model_id_evaluator_only":model,
                "case_id_evaluator_only":row["id"],
                "kind":row["kind"],"action":action,
                "parsed_model":out["parsed"],"final":final,
                "gold_evaluator_only":reference(row),
                "model_correct_evaluator_only":out["parsed"]==reference(row),
                "gain":round(gain,5),
            })
        if pol.verified>BUDGET:raise AssertionError("budget overspent")
        results[policy_name]={
            "total_utility":round(sum(x["gain"] for x in trajectory),5),
            "verified":pol.verified,
            "verify_cost":round(sum(COST[x["kind"]] for x in trajectory
                           if x["action"]=="VERIFY"),5),
            "correct_published":sum(x["final"]==x["gold_evaluator_only"] and
                                     x["final"] is not None for x in trajectory),
            "wrong_published":sum(x["final"]!=x["gold_evaluator_only"] and
                                   x["final"] is not None for x in trajectory),
            "abstained":sum(x["final"] is None for x in trajectory),
            "alarm_count":len(pol.alarms),
            "alarm_times":list(pol.alarms),
            "alarm_off_times":list(pol.alarm_off),
            "logged_verifications":pol.log,
            "planner_version":pol.plan_version,
            "trajectory":trajectory,
        }
    assert results["omega_no_alarm"]["trajectory"]==results["online_beta"]["trajectory"]
    return results

def preflight():
    cal,ev=generation_plan()
    rows=all_cases()
    public=[{"model":m,"id":r["id"],"question":r["question"],
             "kind":r["kind"],"split":r["split"]}
            for m,r in cal+ev]
    return {
        "protocol":PROTOCOL,"status":"PREFLIGHT_ONLY",
        "expected_generations":96,"calibration_generations":32,
        "evaluation_generations":64,
        "public_cases_sha256":sha256(json.dumps(public,sort_keys=True,
            ensure_ascii=False).encode()).hexdigest(),
        "oracles_agree_on_all":len(rows),
        "paid_api_calls":0,"private_data_read":False,"budget":BUDGET,
    }

def run(output_path):
    pre=preflight()
    cal,ev=generation_plan()
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(20261112)
    outputs={}
    revisions={}
    for model_key in ("large","small"):
        identifier,revision=MODELS[model_key]
        model_args={"revision":revision} if revision else {}
        tokenizer=AutoTokenizer.from_pretrained(identifier,**model_args)
        model=AutoModelForCausalLM.from_pretrained(
            identifier,torch_dtype=torch.float32,**model_args).eval()
        revisions[model_key]=getattr(model.config,"_commit_hash",None)
        these=[r for mk,r in cal+ev if mk==model_key]
        assert len(these)==48
        for row in these:
            msgs=prompt(row)
            rendered=tokenizer.apply_chat_template(
                msgs,tokenize=False,add_generation_prompt=True)
            inp=tokenizer([rendered],return_tensors="pt")
            with torch.inference_mode():
                generated=model.generate(**inp,do_sample=False,
                    max_new_tokens=MAX_NEW_TOKENS,
                    pad_token_id=tokenizer.eos_token_id)
            prefix=inp["input_ids"].shape[1]
            generated_tokens=generated[0][prefix:]
            answer=tokenizer.decode(generated_tokens,skip_special_tokens=True)
            outputs[(model_key,row["id"])]={
                "text":answer,"parsed":parse(answer,row["kind"]),
                "input_tokens":int(prefix),
                "output_tokens":int(generated_tokens.shape[0]),
            }
            print("REAL02_MODEL_GENERATION",model_key,row["id"],
                  "parsed="+str(outputs[(model_key,row["id"])]["parsed"]),flush=True)
        del model,tokenizer
        gc.collect()
    assert len(outputs)==96
    scores=score_policies(cal,ev,outputs)
    delta=scores["omega_candidate"]["total_utility"]-scores["discount_beta"]["total_utility"]
    action_diff=sum(
        a["action"]!=b["action"]
        for a,b in zip(scores["omega_candidate"]["trajectory"],
                       scores["omega_no_alarm"]["trajectory"])
    )
    test_rows=[
        {"model":model_key,"case_id":row["id"],"kind":row["kind"],
         "correct":outputs[(model_key,row["id"])]["parsed"]==reference(row),
         "parsed":outputs[(model_key,row["id"])]["parsed"],
         "gold":reference(row)}
        for model_key,row in ev
    ]
    by_phase={str(i):{
        "model":("large","small","large","small")[i],
        "correct":sum(x["correct"] for x in test_rows[i*16:(i+1)*16]),
        "unparsed":sum(x["parsed"] is None for x in test_rows[i*16:(i+1)*16]),
    } for i in range(4)}
    raw_outputs=[
        {"model":model_key,"case_id":row["id"],"kind":row["kind"],
         "question":row["question"],
         "split":"calibration" if row["index"]<4 else "test",
         "gold_posthoc_only":reference(row),**outputs[(model_key,row["id"])]}
        for model_key,row in cal+ev
    ]
    report={
        "status":STATUS,"protocol":PROTOCOL,
        "preflight_public_cases_sha256":pre["public_cases_sha256"],
        "revisions":revisions,
        "paid_api_calls":0,"private_data_used":False,
        "real_generations":len(outputs),"evaluation_decisions":64,
        "budgets_equal":BUDGET,
        "model_test":{
            "correct":sum(x["correct"] for x in test_rows),
            "unparsed":sum(x["parsed"] is None for x in test_rows),
            "by_phase":by_phase,
            "by_kind":{k:{
                "correct":sum(x["correct"] for x in test_rows if x["kind"]==k),
                "count":sum(x["kind"]==k for x in test_rows)}
                for k in KINDS},
        },
        "primary_difference_omega_minus_discount":round(delta,5),
        "different_actions_omega_vs_no_alarm":action_diff,
        "policy_results":scores,
        "raw_model_outputs":raw_outputs,
        "limitations":[
            "Author-designed finite problems, not independent external holdout",
            "1.5B and 0.5B are different model capacities; change not concealed in texts",
            "Evaluation intentionally makes model switch, not real nonstationarity",
            "Only correctness of paid verification is observed by controllers",
            "Exact verifiers on narrow domains; no imperfect external retrieval",
            "Candidate is an experimental layer using planner, not P1 learning",
            "One 64-decision sequence, no statistical generalization inference",
            "No API billing, no model training, no private-data use",
        ],
    }
    dest=Path(output_path)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,indent=2,sort_keys=True,
                               ensure_ascii=False)+"\n",encoding="utf-8")
    print("P5_REAL02_SUMMARY",json.dumps({
        "status":STATUS,"real_generations":len(outputs),
        "model_test":report["model_test"],
        "primary_difference_omega_minus_discount":round(delta,5),
        "different_actions_omega_vs_no_alarm":action_diff,
        "policies":{k:{f:v[f] for f in (
            "total_utility","verified","correct_published",
            "wrong_published","abstained","alarm_count")}
            for k,v in scores.items()},
        "revisions":revisions,
    },ensure_ascii=False,sort_keys=True),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--preflight",action="store_true")
    parser.add_argument("--output",default="p5_real02_output.json")
    args=parser.parse_args()
    if args.preflight:print(json.dumps(preflight(),sort_keys=True))
    else:run(args.output)

if __name__=="__main__":
    main()
