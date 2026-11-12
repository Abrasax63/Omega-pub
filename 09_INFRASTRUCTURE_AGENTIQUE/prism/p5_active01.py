"""P5 ACTIVE-01: costly chosen feedback, four competing candidate claims per round.

Narrow PUBLIC experiment. Real Qwen next-token class logits, not free text
generation. Exact verifier invoked only after the controller selects one claim.
Reference answers and source model/phase never enter Policy.choose().
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from fractions import Fraction
from hashlib import sha256
from math import exp,gcd
from pathlib import Path
import gc
import json

from planner import plan_mission

PROTOCOL="P5-ACTIVE-01"
STATUS="PUBLIC_OPEN_MODEL_ACTIVE_INFORMATION_EXPLORATORY"
KINDS=("MUL","CRT","RATE","INJ")
MODELS={
    "small":("Qwen/Qwen2.5-0.5B-Instruct","7ae557604adf67be50417f59c2c2f167def9a775"),
    "large":("Qwen/Qwen2.5-1.5B-Instruct","989aa7980e4cf806f80c7fef2b1adb7bc71aa306"),
}
COST={"MUL":.25,"CRT":.40,"RATE":.30,"INJ":.20}
ROUNDS=16
CANDIDATES=4
MAX_VERIFICATIONS=16
POLICIES=("none","fixed_first","round_robin","voi_static","voi_online",
          "voi_discount","voi_margin","omega_candidate","omega_no_change",
          "hindsight_oracle")
DEPLOYABLE=tuple(p for p in POLICIES if p!="hindsight_oracle")
GAMMA=.75
MARGIN_BOUND=.75
ALARM_ON=.35
ALARM_OFF=.15
ONE_VERIFY_PER_ROUND=True

def _rand(*parts):
    return int.from_bytes(sha256(
        ("P5ACTIVE01|"+"|".join(map(str,parts))).encode("utf-8")
    ).digest()[:8],"big")

def make_case(kind,i):
    if kind not in KINDS or type(i) is not int or not 0<=i<20:
        raise ValueError("unregistered kind/index")
    if kind=="MUL":
        a=13+_rand(kind,i,"a")%90
        b=2+_rand(kind,i,"b")%65
        stated=a*b if i%2==0 else a*b+1+_rand(kind,i,"offset")%7
        p=(a,b,stated)
        question=f"Proposition : {a} multiplié par {b} est exactement égal à {stated}."
    elif kind=="CRT":
        m=(5,7,9,11,13)[_rand(kind,i,"m")%5]
        n=(8,16,17,19)[_rand(kind,i,"n")%4]
        x=_rand(kind,i,"x")%(m*n)
        a=x%m
        b=x%n
        proposed=x if i%2==0 else (x+1)%(m*n)
        p=(m,a,n,b,proposed)
        question=(f"Proposition : le nombre {proposed} satisfait en même temps "
                  f"x modulo {m} = {a} et x modulo {n} = {b}.")
    elif kind=="RATE":
        totals=[11+_rand(kind,i,"den",j)%67 for j in range(4)]
        hits=[1+_rand(kind,i,"hit",j)%(v-1) for j,v in enumerate(totals)]
        a,b,c,d=totals
        x,y,z,w=hits
        if (x+y)*(c+d)==(z+w)*(a+b):
            y=y+1 if y+1<b else y-1
        raw=(x,a,y,b,z,c,w,d)
        # swap groups where needed to enforce truth on even i.
        true=((x+y)*(c+d)>(z+w)*(a+b))
        if true != (i%2==0):
            raw=(z,c,w,d,x,a,y,b)
        p=raw
        x,a,y,b,z,c,w,d=p
        question=(f"Proposition : A, avec {x} succès/{a} puis {y}/{b}, "
                  f"a un taux global STRICTEMENT plus élevé que B, "
                  f"avec {z}/{c} puis {w}/{d}.")
    else:
        n=7
        vals=sorted(range(n),key=lambda j:(_rand(kind,i,"perm",j),j))
        if i%2:
            t=1+_rand(kind,i,"duplicate")%(n-1)
            vals[t]=vals[0]
        p=tuple(vals)
        question=(f"Proposition : sur X = {{0, ..., {n-1}}}, "
                  f"la fonction définie par les images f(0),...,f({n-1}) = "
                  f"{vals} est injective.")
    row={"id":f"ACTIVE-{kind}-{i:02d}","kind":kind,"index":i,
         "question":question,"parameters":p,
         "split":"calibration" if i<4 else "test"}
    return row

def gold(r):
    p=r["parameters"]
    if r["kind"]=="MUL":return "A" if p[0]*p[1]==p[2] else "B"
    if r["kind"]=="CRT":
        m,a,n,b,x=p
        return "A" if x%m==a and x%n==b else "B"
    if r["kind"]=="RATE":
        x,a,y,b,z,c,w,d=p
        return "A" if Fraction(x+y,a+b)>Fraction(z+w,c+d) else "B"
    if r["kind"]=="INJ":return "A" if len(set(p))==len(p) else "B"
    raise AssertionError("invalid kind")

def verify_exact(r):
    # Independently implemented actual verifier, not a simulated fault.
    p=r["parameters"]
    if r["kind"]=="MUL":
        x,y,claimed=p
        total=0
        for _ in range(y):total+=x
        return "A" if total==claimed else "B"
    if r["kind"]=="CRT":
        m,a,n,b,claimed=p
        assert gcd(m,n)==1
        solution=next(k for k in range(m*n) if k%m==a and k%n==b)
        return "A" if solution==claimed else "B"
    if r["kind"]=="RATE":
        x,a,y,b,z,c,w,d=p
        delta=(x+y)*(c+d)-(z+w)*(a+b)
        assert delta!=0
        return "A" if delta>0 else "B"
    if r["kind"]=="INJ":
        for j in range(len(p)):
            for k in range(j+1,len(p)):
                if p[j]==p[k]:return "B"
        return "A"
    raise AssertionError("invalid kind")

def universe():
    rows=[make_case(kind,i) for kind in KINDS for i in range(20)]
    assert len(rows)==80 and len({r["id"] for r in rows})==80
    assert len({r["question"] for r in rows})==80
    assert len({(r["kind"],tuple(r["parameters"])) for r in rows})==80
    for r in rows:
        assert gold(r)==verify_exact(r),r["id"]
        assert gold(r)==("A" if r["index"]%2==0 else "B"),r["id"]
    return rows

def plan():
    calibration=[(model,make_case(k,i)) for model in ("small","large")
                 for k in KINDS for i in range(4)]
    batches=[]
    for t in range(ROUNDS):
        phase=t//4
        model=("large","small","large","small")[phase]
        offset=(4,12,8,16)[phase]
        i=offset+(t%4)
        candidates=[make_case(k,i) for k in KINDS]
        ordered=sorted(candidates,key=lambda r:(
            _rand("round",t,"position",r["kind"]),r["kind"]))
        batches.append([(model,r) for r in ordered])
    all_eval=[(m,r) for batch in batches for m,r in batch]
    assert len(calibration)==32 and len(all_eval)==64
    assert len({r["id"] for _,r in all_eval})==64
    assert not {r["id"] for _,r in calibration}&{r["id"] for _,r in all_eval}
    assert all({r["kind"] for _,r in batch}==set(KINDS) for batch in batches)
    return calibration,batches

def model_prompt(r):
    # Labels A/B are guaranteed as *allowed* token candidates, not parsed
    # from unconstrained explanation or computed using gold.
    return [
        {"role":"system","content":"Réponds aux propositions en français."},
        {"role":"user","content":r["question"]+
         "\nChoix : A = Vrai. B = Faux. Donne uniquement A ou B."},
    ]

def public(r,out):
    """No model identity, phase, item index, answer key or label."""
    return {
        "kind":r["kind"],"question":r["question"],
        "answer":out["answer"],"confidence":out["confidence"],
        "margin":out["margin"],"cost":COST[r["kind"]],
    }

def baseline_stats(calibration):
    stats={k:{"total":0,"correct":0} for k in KINDS}
    by_margin={k:{"low":[0,0],"high":[0,0]} for k in KINDS}
    for r,out in calibration:
        s=stats[r["kind"]]
        is_correct=int(out["answer"]==gold(r))
        s["correct"]+=is_correct
        s["total"]+=1
        key="high" if out["confidence"]>=MARGIN_BOUND else "low"
        by_margin[r["kind"]][key][0]+=is_correct
        by_margin[r["kind"]][key][1]+=1
    assert all(v["total"]==8 for v in stats.values())
    return stats,by_margin

def laplace(right,total):
    return (right+1)/(total+2)

class Policy:
    """One paid feedback message per chosen verifier; append-only scientific log."""
    def __init__(self,name,calibration):
        if name not in DEPLOYABLE:raise ValueError("not a deployable policy")
        self.name=name
        self.prior,self.margin_prior=baseline_stats(calibration)
        self.global_prior=(sum(s["correct"] for s in self.prior.values())/
                           sum(s["total"] for s in self.prior.values()))
        self.feedback=defaultdict(list)
        self.feedback_bins=defaultdict(list)
        self.seen=[]
        self.alarms=[]
        self.alarm_active=False
        self.used=0
        self.version=None
        if name.startswith("omega_"):
            p=plan_mission({
                "question":"Choisir une seule preuve parmi quatre réponses "
                           "concurrentes, sous coût, sans voir les vérités cachées.",
                "mission_type":"general",
                "decision_context":{
                    "blocking_uncertainty":"Fiabilité relative des réponses inconnue",
                    "verification":"Contrôle mathématique exact d'une seule candidate",
                    "verification_effect":"Écarter une erreur et actualiser la mémoire",
                },
            })
            assert p["next_action"]["action"]=="verify"
            self.version=p["planner_version"]

    def estimate(self,view):
        kind=view["kind"]
        c=self.prior[kind]
        history=self.feedback[kind]
        right,total=c["correct"],c["total"]
        if self.name in ("voi_online","voi_margin",
                         "omega_candidate","omega_no_change"):
            right+=sum(history)
            total+=len(history)
        elif self.name=="voi_discount":
            w=1.0
            for b in reversed(history):
                right+=w*b
                total+=w
                w*=GAMMA
        p=laplace(right,total)
        if self.name=="voi_margin":
            bin_name="high" if view["confidence"]>=MARGIN_BOUND else "low"
            b=self.margin_prior[kind][bin_name]
            if b[1]!=0:
                observations=self.feedback_bins[(kind,bin_name)]
                p=laplace(b[0]+sum(observations),b[1]+len(observations))
        if self.name=="omega_candidate" and self.alarm_active:
            recent=[x["correct"] for x in self.seen[-4:]]
            if recent:
                p=.5*p+.5*laplace(sum(recent),len(recent))
        return p

    def choose(self,t,views):
        if type(t) is not int or not 0<=t<ROUNDS:
            raise ValueError("bad round index")
        if not isinstance(views,list) or len(views)!=4:
            raise ValueError("exactly four candidate contexts required")
        expected_keys={"kind","question","answer","confidence","margin","cost"}
        if {v["kind"] for v in views}!=set(KINDS):
            raise ValueError("no duplicates, four known domains")
        if any(set(v)!=expected_keys for v in views):
            raise ValueError("hidden or extra field in policy input")
        probs=[self.estimate(v) for v in views]
        baselines=[max(3*p-2,.05) for p in probs]
        benefits=[(1-v["cost"])-base for v,base in zip(views,baselines)]
        if self.name=="none":
            chosen=None
        elif self.name=="fixed_first":
            chosen=0
        elif self.name=="round_robin":
            chosen=next(i for i,v in enumerate(views)
                        if v["kind"]==KINDS[t%len(KINDS)])
        else:
            chosen=min(range(4),key=lambda i:(
                -benefits[i],KINDS.index(views[i]["kind"])))
            if benefits[chosen]<=0:
                chosen=None
        actions=["DIRECT" if 3*p-2>.05 else "ABSTAIN" for p in probs]
        if chosen is not None:actions[chosen]="VERIFY"
        return {"chosen":chosen,"actions":actions,
                "estimated_benefits":[round(x,6) for x in benefits]}

    def observe(self,t,view,is_correct):
        if type(is_correct) is not bool:
            raise ValueError("paid feedback must be boolean")
        if self.seen and t<=self.seen[-1]["round"]:
            raise ValueError("at most one paid observation per round")
        event={"round":t,"kind":view["kind"],"correct":int(is_correct),
               "confidence":view["confidence"]}
        self.seen.append(event)
        self.feedback[view["kind"]].append(int(is_correct))
        bin_name="high" if view["confidence"]>=MARGIN_BOUND else "low"
        self.feedback_bins[(view["kind"],bin_name)].append(int(is_correct))
        self.used+=1
        if self.used>ROUNDS:
            raise AssertionError("verification budget overflow")
        if self.name=="omega_candidate" and len(self.seen)>=4:
            recent=sum(x["correct"] for x in self.seen[-4:])/4
            gap=abs(recent-self.global_prior)
            if not self.alarm_active and gap>=ALARM_ON:
                self.alarm_active=True
                self.alarms.append({"round":t,"event":"alarm_on","gap":round(gap,5)})
            elif self.alarm_active and gap<=ALARM_OFF:
                self.alarm_active=False
                self.alarms.append({"round":t,"event":"alarm_off","gap":round(gap,5)})

def _score_one(row,out,act):
    truth=gold(row) # evaluator-only
    if act=="VERIFY":
        verified=verify_exact(row)
        return verified,round(1-COST[row["kind"]],5)
    if act=="DIRECT":
        return out["answer"],(1 if out["answer"]==truth else -2)
    if act=="ABSTAIN":
        return None,.05
    raise AssertionError("unknown action")

def evaluate(cal_plan,batches,outputs):
    all_pairs=cal_plan+[p for batch in batches for p in batch]
    if len(outputs)!=96 or set(outputs)!={(m,r["id"]) for m,r in all_pairs}:
        raise ValueError("all genuine outputs required")
    calibration=[(r,outputs[(m,r["id"])]) for m,r in cal_plan]
    results={}
    for name in DEPLOYABLE:
        controller=Policy(name,calibration)
        events=[]
        for t,batch in enumerate(batches):
            views=[public(r,outputs[(m,r["id"])]) for m,r in batch]
            decision=controller.choose(t,views)
            assert decision["actions"].count("VERIFY")<=1
            chosen=decision["chosen"]
            for i,(model,row) in enumerate(batch):
                out=outputs[(model,row["id"])]
                action=decision["actions"][i]
                final,reward=_score_one(row,out,action)
                events.append({
                    "round":t,"position":i,"kind":row["kind"],
                    "action":action,"reward":reward,
                    "model_evaluator_only":model,
                    "case_evaluator_only":row["id"],
                    "gold_evaluator_only":gold(row),
                    "model_answer":out["answer"],"model_correct_evaluator_only":
                        out["answer"]==gold(row),"final":final,
                    "estimated_verification_gain":decision["estimated_benefits"][i],
                })
                if chosen==i:
                    # Only observed chosen verifications are shown to the policy.
                    controller.observe(t,views[i],out["answer"]==verify_exact(row))
        results[name]={
            "utility":round(sum(e["reward"] for e in events),5),
            "verified":controller.used,
            "correct_published":sum(e["final"] is not None and
                                   e["final"]==e["gold_evaluator_only"] for e in events),
            "wrong_published":sum(e["final"] is not None and
                                   e["final"]!=e["gold_evaluator_only"] for e in events),
            "abstained":sum(e["final"] is None for e in events),
            "cost":round(sum(COST[e["kind"]] for e in events
                       if e["action"]=="VERIFY"),5),
            "alarm_events":controller.alarms,
            "observed_feedback":controller.seen,
            "planner_version":controller.version,
            "trajectory":events,
        }
        assert controller.used<=ROUNDS
    assert results["voi_online"]["trajectory"]==results["omega_no_change"]["trajectory"]
    # Counterfactual hindsight oracle: NOT a deployable policy.
    oracle=[]
    for t,batch in enumerate(batches):
        vals=[]
        for model,row in batch:
            out=outputs[(model,row["id"])]
            correct=out["answer"]==gold(row)
            base=max(1 if correct else -2,.05)
            uplift=1-COST[row["kind"]]-base
            vals.append((uplift,row["kind"]))
        chosen=max(range(4),key=lambda j:(
            vals[j][0],-KINDS.index(batch[j][1]["kind"])))
        if vals[chosen][0]<=0:chosen=None
        for j,(model,row) in enumerate(batch):
            answer=outputs[(model,row["id"])]["answer"]
            act="VERIFY" if j==chosen else (
                "DIRECT" if answer==gold(row) else "ABSTAIN")
            final,reward=_score_one(row,outputs[(model,row["id"])],act)
            oracle.append({"round":t,"action":act,"reward":reward,
                           "kind":row["kind"],"final":final})
    results["hindsight_oracle"]={
        "utility":round(sum(e["reward"] for e in oracle),5),
        "verified":sum(e["action"]=="VERIFY" for e in oracle),
        "trajectory":oracle,
        "nondeployable":True,
    }
    return results

def preflight():
    rows=universe()
    ca,ba=plan()
    public_rows=[{"model":m,"id":r["id"],"question":r["question"]}
        for m,r in ca+[x for batch in ba for x in batch]]
    return {
        "protocol":PROTOCOL,"status":"FROZEN_BEFORE_INFERENCE",
        "public_question_count":len(rows),
        "calibration_outputs":32,"test_outputs":64,"real_model_forwards":96,
        "batches":ROUNDS,"candidates_per_batch":4,
        "public_digest":sha256(json.dumps(public_rows,sort_keys=True,
            ensure_ascii=False).encode()).hexdigest(),
        "private_data_used":False,"paid_api_calls":0,
    }

def _one_model_score(model,tokenizer,row):
    import torch
    # Score allowed ONE TOKEN completions, no parsing, no generation.
    tokens={label:tokenizer.encode(label,add_special_tokens=False)
            for label in ("A","B")}
    if any(len(ids)!=1 for ids in tokens.values()):
        raise AssertionError(f"A/B are not single tokens: {tokens}")
    if tokens["A"][0]==tokens["B"][0]:
        raise AssertionError("A/B token IDs collide")
    chat=tokenizer.apply_chat_template(model_prompt(row),
                tokenize=False,add_generation_prompt=True)
    enc=tokenizer([chat],return_tensors="pt")
    with torch.inference_mode():
        logits=model(**enc).logits[0,-1]
    l_a=float(logits[tokens["A"][0]].item())
    l_b=float(logits[tokens["B"][0]].item())
    z=abs(l_a-l_b)
    chosen="A" if l_a>=l_b else "B"
    confidence=1/(1+exp(-z))
    return {
        "answer":chosen,"confidence":round(confidence,9),
        "margin":round(z,9),
        "logit_a":round(l_a,9),"logit_b":round(l_b,9),
        "input_tokens":int(enc["input_ids"].shape[1]),
        "method":"CONSTRAINED_NEXT_TOKEN_SCORE",
        "token_id_a":tokens["A"][0],"token_id_b":tokens["B"][0],
    }

def run(output):
    frozen=preflight()
    cal,batches=plan()
    tasks=cal+[p for batch in batches for p in batch]
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    torch.set_num_threads(2)
    torch.manual_seed(20261112)
    answers={}
    revisions={}
    for key in ("large","small"):
        model_id,rev=MODELS[key]
        tokenizer=AutoTokenizer.from_pretrained(model_id,revision=rev)
        model=AutoModelForCausalLM.from_pretrained(
            model_id,revision=rev,torch_dtype=torch.float32).eval()
        revisions[key]=getattr(model.config,"_commit_hash",None)
        pair=[r for m,r in tasks if m==key]
        assert len(pair)==48
        for row in pair:
            answers[(key,row["id"])]=_one_model_score(model,tokenizer,row)
            print("P5_ACTIVE01_MODEL",key,row["id"],
                  answers[(key,row["id"])]["answer"],
                  answers[(key,row["id"])]["confidence"],flush=True)
        del tokenizer,model
        gc.collect()
    scores=evaluate(cal,batches,answers)
    differences=sum(
        a["action"]!=b["action"] for a,b in zip(
            scores["omega_candidate"]["trajectory"],
            scores["omega_no_change"]["trajectory"]))
    margin_differences=sum(
        a["action"]!=b["action"] for a,b in zip(
            scores["voi_online"]["trajectory"],
            scores["voi_margin"]["trajectory"]))
    all_choice_patterns=set()
    for t in range(ROUNDS):
        pattern=tuple(next((e["kind"] for e in scores[p]["trajectory"]
                if e["round"]==t and e["action"]=="VERIFY"),"NONE")
                for p in DEPLOYABLE)
        all_choice_patterns.add(pattern)
    task_rows=[{"model":key,"question_id":r["id"],
                "kind":r["kind"],"split":r["split"],
                "question":r["question"],"gold_posthoc_only":gold(r),
                **answers[(key,r["id"])]} for key,r in tasks]
    evaluation=[e for e in task_rows if e["split"]=="test"]
    report={
        "protocol":PROTOCOL,"status":STATUS,
        "preflight":frozen,"model_revisions":revisions,
        "actual_model_forwards":len(answers),"paid_api_calls":0,
        "private_data_used":False,
        "model_test":{
            "correct":sum(x["answer"]==x["gold_posthoc_only"] for x in evaluation),
            "count":len(evaluation),
            "by_kind":{k:{
                "correct":sum(x["answer"]==x["gold_posthoc_only"]
                              for x in evaluation if x["kind"]==k),
                "count":sum(x["kind"]==k for x in evaluation)}
                for k in KINDS},
        },
        "policies":scores,
        "omega_minus_discount":round(
            scores["omega_candidate"]["utility"]-
            scores["voi_discount"]["utility"],5),
        "omega_minus_margin":round(
            scores["omega_candidate"]["utility"]-
            scores["voi_margin"]["utility"],5),
        "omega_vs_no_change_action_differences":differences,
        "online_vs_margin_action_differences":margin_differences,
        "unique_batch_policy_choice_patterns":len(all_choice_patterns),
        "raw_model_scores":task_rows,
        "limitations":[
            "Real model forward passes (next-token binary choices), not free-text generations",
            "Artificial author-designed questions and exact tools",
            "Hidden source model switches, not natural distribution drift",
            "Class A/B token bias and next-token scores may be poorly calibrated",
            "Only one 16-round rollout, no statistical significance for generalization",
            "Different policies get chosen-action feedback, not identical revealed truths",
            "Omega experimental controller is not the existing P1 learning system",
            "No real-world imperfect verifiers, external holdout or scientific memory use",
        ],
    }
    path=Path(output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2,sort_keys=True,
                              ensure_ascii=False)+"\n",encoding="utf-8")
    print("P5_ACTIVE01_SUMMARY "+json.dumps({
        "status":STATUS,"real_model_forwards":len(answers),
        "model_test":report["model_test"],
        "omega_minus_discount":report["omega_minus_discount"],
        "omega_minus_margin":report["omega_minus_margin"],
        "omega_vs_no_change_action_differences":differences,
        "online_vs_margin_action_differences":margin_differences,
        "unique_batch_policy_choice_patterns":len(all_choice_patterns),
        "policies":{k:{"utility":v["utility"],"verified":v["verified"],
                         "correct_published":v.get("correct_published"),
                         "wrong_published":v.get("wrong_published"),
                         "abstained":v.get("abstained"),
                         "alarms":len(v.get("alarm_events",[]))}
                    for k,v in scores.items()},
        "model_revisions":revisions,
    },ensure_ascii=False,sort_keys=True),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--output",default="p5_active01_results.json")
    args=ap.parse_args()
    if args.preflight:
        print(json.dumps(preflight(),sort_keys=True))
    else:run(args.output)

if __name__=="__main__":
    main()
