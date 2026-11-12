"""P5-REAL-01: real open-weight model outputs and budgeted online feedback.

Public author-designed questions; no paid API; no private holdout.
This is a public pilot of a candidate policy, NOT the existing P1 learning.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re

from planner import plan_mission

EXPERIMENT="P5-REAL-01"
STATUS="REAL_MODEL_PUBLIC_PILOT_NOT_INDEPENDENT_HOLDOUT"
MODEL="Qwen/Qwen2.5-0.5B-Instruct"
REVISION="7ae557604adf67be50417f59c2c2f167def9a775"
STRATA=("DATA_SMALL","CRT_LARGE","DATA_LARGE","CRT_SMALL")
KINDS=("CRT","DATA")
BUDGET=16
MAX_NEW_TOKENS=48
POLICIES=("direct","verify_budget","abstain","kind_rule","stratum_rule",
          "online_beta","omega_candidate","omega_no_alarm")
RESULT_RE=re.compile(r"(?i)^\s*(?:R[ÉE]PONSE(?:\s+FINALE)?\s*[:=]\s*)?([0-9]+|A|B)\s*[.]?\s*$")
FALLBACK_RE=re.compile(
    r"(?i)^\s*(?:LA\s+)?R[ÉE]PONSE(?:\s+FINALE)?\s+EST\s+([0-9]+|A|B)\s*[.]?\s*$")

def _rand(*parts):
    return int.from_bytes(sha256(
        ("P5REAL01|"+"|".join(map(str,parts))).encode("utf-8")
    ).digest()[:8],"big")

def make_case(stratum,j):
    if stratum not in STRATA or type(j) is not int or not 0<=j<12:
        raise ValueError("unsupported case")
    cid=f"REAL-{stratum}-{j:02d}"
    if stratum.startswith("CRT"):
        small=stratum.endswith("SMALL")
        ms=(5,7,9,11) if small else (17,19,23,29)
        ns=(8,13,17,19) if small else (31,37,41,43)
        m=ms[_rand(stratum,j,"m")%len(ms)]
        n=ns[_rand(stratum,j,"n")%len(ns)]
        r=_rand(stratum,j,"r")%m
        s=_rand(stratum,j,"s")%n
        params=(m,r,n,s)
        question=(f"Trouve le plus petit entier x >= 0 tel que "
                  f"x modulo {m} = {r} et x modulo {n} = {s}.")
        kind="CRT"
    else:
        small=stratum.endswith("SMALL")
        totals=[8+_rand(stratum,j,k)%12 for k in range(4)] if small else [
            32+_rand(stratum,j,k)%37 for k in range(4)]
        # Moderate diversity; avoid absolute extrema and exact ties.
        successes=[1+_rand(stratum,j,"s",k)%(v-1) for k,v in enumerate(totals)]
        a,b,c,d=totals
        x,y,z,w=successes
        if (x+y)*(c+d)==(z+w)*(a+b):
            y=y-1 if y>1 else y+1
        params=(x,a,y,b,z,c,w,d)
        question=(f"Groupe A : {x} succès sur {a} en strate 1 et "
                  f"{y} sur {b} en strate 2. Groupe B : {z} succès sur "
                  f"{c} en strate 1 et {w} sur {d} en strate 2. "
                  "Quel groupe a le meilleur taux global de succès, A ou B ?")
        kind="DATA"
    return {
        "id":cid,"stratum":stratum,"kind":kind,
        "question":question,"parameters":params,
        "split":"calibration" if j<4 else "evaluation",
    }

def cases():
    rows={s:[make_case(s,j) for j in range(12)] for s in STRATA}
    ordered=[item for s in STRATA for item in rows[s]]
    assert len(ordered)==48 and len({x["id"] for x in ordered})==48
    assert len({(x["stratum"],tuple(x["parameters"])) for x in ordered})==48
    for r in ordered:
        if limited_verifier(r) is not None:
            assert limited_verifier(r)==gold(r)
    return ordered

def gold(row):
    """Exact evaluator, mathematically different from bounded verifier."""
    if row["kind"]=="CRT":
        m,r,n,s=row["parameters"]
        return str((r+m*(((s-r)*pow(m,-1,n))%n))%(m*n))
    x,a,y,b,z,c,w,d=row["parameters"]
    lhs=Fraction(x+y,a+b)
    rhs=Fraction(z+w,c+d)
    assert lhs!=rhs
    return "A" if lhs>rhs else "B"

def limited_verifier(row):
    """Actual resource-limited algorithm: correct or UNRESOLVED, never fake."""
    if row["kind"]=="CRT":
        m,r,n,s=row["parameters"]
        for k in range(50):
            if k%m==r and k%n==s:return str(k)
        return None
    x,a,y,b,z,c,w,d=row["parameters"]
    if a+b+c+d>100:return None
    left=(x+y)*(c+d)
    right=(z+w)*(a+b)
    assert left!=right
    return "A" if left>right else "B"

def parse(text):
    """Frozen before real generation. Reject ambiguous/absent answers."""
    if not isinstance(text,str):return None
    lines=[line.strip() for line in text.splitlines() if line.strip()]
    if not lines:return None
    for line in lines[:2]:
        match=RESULT_RE.fullmatch(line) or FALLBACK_RE.fullmatch(line)
        if match:return match.group(1).upper()
    return None

def prompt(row):
    return [
        {"role":"system","content":"Réponds en français. Donne uniquement la réponse demandée."},
        {"role":"user","content":row["question"]+"\n"
         "Réponds sur une seule ligne : REPONSE=nombre ou REPONSE=A ou REPONSE=B. "
         "Ne recopie pas les mots nombre, A ou B comme exemples."},
    ]

def public_view(row,generated):
    return {
        "id":row["id"],"kind":row["kind"],"stratum":row["stratum"],
        "question":row["question"],"model_output":generated["text"],
        "parsed":generated["parsed"],
        "verify_cost":.35 if row["kind"]=="CRT" else .20,
    }

def laplace(success,total):
    return (success+1)/(total+2)

def _stats(calibration,key_fn):
    results=defaultdict(lambda:{"right":0,"total":0,"resolved":0})
    for row,gen in calibration:
        key=key_fn(row)
        z=results[key]
        z["total"]+=1
        z["right"]+=int(gen["parsed"]==gold(row))
        z["resolved"]+=int(limited_verifier(row) is not None)
    return dict(results)

class DecisionPolicy:
    """Only .choose(public) and .observe(verified observation) are visible."""
    def __init__(self,name,calibration):
        if name not in POLICIES:raise ValueError("policy")
        self.name=name
        self.by_stratum=_stats(calibration,lambda r:r["stratum"])
        self.by_kind=_stats(calibration,lambda r:r["kind"])
        self.feedback=defaultdict(list)
        self.logs=[]
        self.budget_left=BUDGET
        self.alarms=0
        self.last_alarm_bucket=set()
        self.plan=None
        if name.startswith("omega_"):
            plan=plan_mission({
                "question":"Quelle réponse vérifier avant de la publier et "
                           "quand réviser la stratégie à partir de retours vérifiés ?",
                "mission_type":"general",
                "decision_context":{
                    "blocking_uncertainty":"Fiabilité de la réponse inconnue",
                    "verification":"Comparer une réponse à un calcul exact borné",
                    "verification_effect":"Confirmer la réponse ou corriger et réviser l'estimation",
                },
            })
            assert plan["next_action"]["action"]=="verify"
            self.plan=plan["planner_version"]

    def _estimates(self,view):
        key=view["kind"] if self.name=="kind_rule" else view["stratum"]
        source=self.by_kind if self.name=="kind_rule" else self.by_stratum
        c=source[key]
        correct=c["right"]
        total=c["total"]
        resolved=c["resolved"]
        # Only a check that actually RESOLVES reveals correctness online.
        if self.name in ("online_beta","omega_candidate","omega_no_alarm"):
            reports=self.feedback[view["stratum"]]
            good=[x["model_correct"] for x in reports if x["resolved"]]
            correct+=sum(good)
            total+=len(good)
            resolved+=sum(x["resolved"] for x in reports)
            # Coverage is learned from actual performed checks, including failures.
            coverage_total=c["total"]+len(reports)
        else:coverage_total=c["total"]
        p=laplace(correct,total)
        coverage=laplace(resolved,coverage_total)
        if self.name=="omega_candidate":
            checked=[x["model_correct"] for x in self.feedback[view["stratum"]]
                     if x["resolved"]]
            if len(checked)>=3:
                last=checked[-3:]
                prior=laplace(c["right"],c["total"])
                dev=abs(sum(last)/3-prior)
                if dev>=.40:
                    self.last_alarm_bucket.add(view["stratum"])
                    # Use only the recent observed verification outcomes.
                    p=laplace(sum(last),len(last))
                else:self.last_alarm_bucket.discard(view["stratum"])
        return p,coverage

    def choose(self,view):
        if self.name=="direct":return "DIRECT"
        if self.name=="abstain":return "ABSTAIN"
        if self.name=="verify_budget":
            return "VERIFY" if self.budget_left else "DIRECT"
        p,coverage=self._estimates(view)
        direct=.05 if view["parsed"] is None else (3*p-2)
        verify=coverage*1+(1-coverage)*.05-view["verify_cost"]
        scores={"ABSTAIN":.05,"DIRECT":direct,
                "VERIFY":verify if self.budget_left else -1e6}
        # on tie abstain > direct > verify (fixed before generation).
        return max(("ABSTAIN","DIRECT","VERIFY"),
                   key=lambda a:(scores[a],-("ABSTAIN","DIRECT","VERIFY").index(a)))

    def observe(self,view,verification):
        if self.budget_left<=0:raise AssertionError("budget overspend")
        if not isinstance(verification,dict) or set(verification)!={"resolved","model_correct"}:
            raise ValueError("invalid verifier feedback keys")
        if type(verification["resolved"]) is not bool:
            raise ValueError("resolved must be boolean")
        if verification["resolved"] and type(verification["model_correct"]) is not bool:
            raise ValueError("a resolved verification must report model correctness")
        if not verification["resolved"] and verification["model_correct"] is not None:
            raise ValueError("oracle leaked on unresolved verification")
        self.budget_left-=1
        self.feedback[view["stratum"]].append(dict(verification))
        before=set(self.last_alarm_bucket)
        if self.name=="omega_candidate":
            self._estimates(view)
            newly_active=set(self.last_alarm_bucket)-before
            self.alarms+=len(newly_active)
        else:newly_active=set()
        self.logs.append({
            "id":view["id"],"resolved":verification["resolved"],
            "model_correct":verification["model_correct"],
            "budget_remaining":self.budget_left,
            "alarms_total":self.alarms,
            "alarm_new":bool(newly_active),
        })

def _evaluation_sequence(all_rows):
    # Frozen four-block sequence; kind/size are visible in every question.
    return [row for stratum in STRATA for row in all_rows
            if row["stratum"]==stratum and row["split"]=="evaluation"]

def evaluate_policies(all_rows,outputs):
    if len(outputs)!=48 or set(outputs)!={r["id"] for r in all_rows}:
        raise ValueError("all 48 REAL model responses required")
    calibration=[(r,outputs[r["id"]]) for r in all_rows
                 if r["split"]=="calibration"]
    stream=_evaluation_sequence(all_rows)
    records={}
    for name in POLICIES:
        policy=DecisionPolicy(name,calibration)
        trajectory=[]
        for row in stream:
            gen=outputs[row["id"]]
            view=public_view(row,gen)
            action=policy.choose(view)
            original_correct=(gen["parsed"]==gold(row))
            true=gold(row) # EVALUATOR only; never passed to choose
            checked=None
            if action=="VERIFY":
                checked=limited_verifier(row)
                success=checked is not None
                gain=(1.0 if success else .05)-view["verify_cost"]
                policy.observe(view,{
                    "resolved":success,
                    "model_correct":(gen["parsed"]==checked) if success else None,
                })
                final=checked if success else None
            elif action=="DIRECT":
                final=gen["parsed"]
                gain=(1.0 if original_correct else -2.0) if final is not None else .05
            else:
                final=None
                gain=.05
            trajectory.append({
                "id":row["id"],"kind":row["kind"],"stratum":row["stratum"],
                "action":action,"final":final,
                "expected":true,  # only public POST-HOC archive, not controller!
                "model_parsed":gen["parsed"],"model_correct":original_correct,
                "verified_outcome":checked,
                "gain":round(gain,5),
            })
        records[name]={
            "utility":round(sum(x["gain"] for x in trajectory),5),
            "verified":sum(x["action"]=="VERIFY" for x in trajectory),
            "wrong_published":sum(x["final"] is not None and x["final"]!=x["expected"]
                                  for x in trajectory),
            "correct_published":sum(x["final"] is not None and x["final"]==x["expected"]
                                    for x in trajectory),
            "abstained":sum(x["final"] is None for x in trajectory),
            "verification_cost":round(sum(
                (.35 if x["kind"]=="CRT" else .20) for x in trajectory
                if x["action"]=="VERIFY"),5),
            "alarm_count":policy.alarms,
            "alarm_log":policy.logs,
            "trajectory":trajectory,
        }
        assert records[name]["verified"]<=BUDGET
    return records

def preflight():
    rows=cases()
    assert len([x for x in rows if x["split"]=="calibration"])==16
    assert len([x for x in rows if x["split"]=="evaluation"])==32
    digest=sha256(json.dumps(rows,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    return {
        "protocol":EXPERIMENT,
        "status":"PREFLIGHT_NO_MODEL_CALL",
        "model_generations":0,"planned_model_generations":48,
        "public_cases_sha256":digest,
        "private_holdout_read":False,"paid_api_calls":0,
        "calibration_case_count":16,"evaluation_case_count":32,
        "budget":BUDGET,"model_revision":REVISION,
    }

def real_run(output):
    frozen=preflight()
    rows=cases()
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(2)
    torch.manual_seed(20261112)
    tokenizer=AutoTokenizer.from_pretrained(MODEL,revision=REVISION)
    model=AutoModelForCausalLM.from_pretrained(
        MODEL,revision=REVISION,torch_dtype=torch.float32).eval()
    outputs={}
    for row in rows:
        msgs=prompt(row)
        rendered=tokenizer.apply_chat_template(
            msgs,tokenize=False,add_generation_prompt=True)
        tokens=tokenizer([rendered],return_tensors="pt")
        with torch.inference_mode():
            sampled=model.generate(
                **tokens,do_sample=False,
                max_new_tokens=MAX_NEW_TOKENS,
                pad_token_id=tokenizer.eos_token_id)
        left=tokens["input_ids"].shape[1]
        new=sampled[0][left:]
        text=tokenizer.decode(new,skip_special_tokens=True)
        outputs[row["id"]]={
            "text":text,"parsed":parse(text),
            "input_tokens":int(left),
            "output_tokens":int(new.shape[0]),
        }
        print("REAL_MODEL_CASE",row["id"],row["split"],
              "parsed="+str(outputs[row["id"]]["parsed"]),flush=True)
    policies=evaluate_policies(rows,outputs)
    test_cases=[r for r in rows if r["split"]=="evaluation"]
    report={
        "status":STATUS,"protocol":EXPERIMENT,
        "model":MODEL,"model_revision":getattr(model.config,"_commit_hash",None),
        "generated_responses":len(outputs),"calibration_cases":16,"test_cases":32,
        "openai_api_calls":0,"private_data_used":False,
        "frozen_public_cases_sha256":frozen["public_cases_sha256"],
        "budget":BUDGET,
        "model_on_test":{
            "correct_extracted":sum(outputs[r["id"]]["parsed"]==gold(r) for r in test_cases),
            "unparsed":sum(outputs[r["id"]]["parsed"] is None for r in test_cases),
            "verifier_resolved":sum(limited_verifier(r) is not None for r in test_cases),
            "by_stratum":{s:{
                "correct":sum(outputs[r["id"]]["parsed"]==gold(r)
                            for r in test_cases if r["stratum"]==s),
                "verifier_resolved":sum(limited_verifier(r) is not None
                            for r in test_cases if r["stratum"]==s)}
                for s in STRATA},
        },
        "policies":policies,
        "public_questions":[{**r,"gold":gold(r),
             "limited_verifier_answer":limited_verifier(r)} for r in rows],
        "model_outputs":outputs,
        "limitations":[
            "48 public author-generated tasks, no external independent holdout",
            "One small open-weight model, greedy, one generation per question",
            "Resource-bounded verifiers deliberately fail closed on large cases",
            "No direct-action feedback revealed to online controllers",
            "Real outputs not independent external scientific research tasks",
            "Omega candidate is experimental wrapper, not deployed P1 learning",
            "Small evaluation size and visible size/type distribution changes",
        ],
    }
    dest=Path(output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(report,ensure_ascii=False,indent=2,
                               sort_keys=True)+"\n",encoding="utf-8")
    print("P5_REAL01_RESULT "+json.dumps({
        "status":STATUS,
        "model_generations":len(outputs),
        "calibration_cases":16,"evaluation_cases":32,
        "test_model":report["model_on_test"],
        "policies":{k:{j:v[j] for j in (
            "utility","verified","wrong_published","correct_published",
            "abstained","alarm_count")} for k,v in policies.items()},
    },sort_keys=True,ensure_ascii=False),flush=True)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preflight",action="store_true")
    ap.add_argument("--output",default="p5_real01_results.json")
    opt=ap.parse_args()
    if opt.preflight:print(json.dumps(preflight(),sort_keys=True))
    else:real_run(opt.output)

if __name__=="__main__":main()
