"""FALSIFY-05: REAL, previously published ClaimDB outputs from 3 model vendors.

A calibration-only empirical JOINT distribution of truth and potential tool
outcomes permits exact finite-horizon Bellman decisions. Held-out labels NEVER
enter policies; this is a GROUP-HELD-OUT retrospective replay, not blind truth.
All tool-call prices are PREDECLARED UTILITY PROXIES, not measured money.
'omega_like' is deliberately NOT the real Omega P1/P2/P3 orchestrator.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from functools import lru_cache
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import json
import math
import re
import statistics

PROTOCOL="P5-FALSIFY-05"
STATUS="REAL_MULTIVENDOR_MODEL_ERRORS_RETROSPECTIVE_NOT_OMEGA_PROVEN"
COMMIT="e06c3a22cc14a8ef6858bb5d40bca7925241b98d"
LABELS=("ENTAILED","CONTRADICTED","NOT ENOUGH INFO")
TOOLS=("nano","gemini","claude")
COST=(8,12,16)  # hundredths of hypothetical utility
MAX_COST=24
MAX_CALLS=2
ALPHA=.10
ABSTAIN=.05
NO_SQL="NO_SQL_OUTPUT"
NO_LABEL="NO_VERIFIER_LABEL"
SOURCES={
    "gold":("final-benchmark/test-public.jsonl",
      "b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810"),
    "base":("experiments/public/no_tools/gpt-5-mini.jsonl",
      "552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6"),
    "nano":("experiments/public/gpt-5-nano.jsonl",
      "c41127fc6a5d1105f582ec876dccec2c685ecd3a01a651ac4033d9c6058816c0"),
    "gemini":("experiments/public/gemini-2.5-flash.jsonl",
      "8c2107a3f9cea8bfd37a8305441541c3566627640f47f7d63d3bdd93a3fc5b4c"),
    "claude":("experiments/public/claude-haiku-4-5.jsonl",
      "2bf7a999dd853a16e5aa40e6fbf65879952d076fbdfa02968c3e80e4f3fa2130"),
}
DEPLOYABLE=("no_tool","fixed_cheapest_two","bayes_global_exact",
  "bayes_context_exact","bayes_raw_exact","omega_like_no_memory",
  "omega_like_no_observability","omega_like_full")
POLICIES=DEPLOYABLE+("hindsight_oracle",)


def hash_str(s):
    return sha256(s.encode("utf-8")).hexdigest()


def _read(path,expected):
    raw=Path(path).read_bytes()
    if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("LFS_POINTER_INSTEAD_OF_REAL_MODEL_OUTPUTS")
    dig=sha256(raw).hexdigest()
    if dig!=expected:
        raise ValueError(f"ORIGINAL_SOURCE_SHA256_MISMATCH:{path}:{dig}")
    rows=[json.loads(line) for line in raw.splitlines() if line.strip()]
    if len(rows)!=1000 or len({r["claim_id"] for r in rows})!=1000:
        raise ValueError("source not 1000 unique ClaimDB records")
    return {r["claim_id"]:r for r in rows},{"sha256":dig,"bytes":len(raw),"cases":len(rows)}


def trace_receipt(row):
    actions=row.get("to_input_list")
    if not isinstance(actions,list):
        return {"trace_available":False,"outputs":0,"calls":0}
    items=[x.get("type") for x in actions if isinstance(x,dict)]
    return {"trace_available":True,
            "outputs":sum(t in ("function_call_output","tool_result") for t in items),
            "calls":sum(t in ("function_call","tool_call") for t in items)}


def context(text):
    text=text.lower()
    return ("numeric" if re.search(r"\d",text) or any(s in text for s in
        ("exactly","at least","more than","average","percentage","how many",
         "number of")) else "other")


def ingest(root):
    raw={}; manifests={}
    for name,(relative,digest) in SOURCES.items():
        raw[name],manifests[name]=_read(Path(root)/relative,digest)
    ids=set(raw["gold"])
    if any(set(raw[name])!=ids for name in raw):
        raise ValueError("UNALIGNED_CLAIM_IDS")
    all_rows=[]
    for key in sorted(ids):
        g=raw["gold"][key]
        if g.get("label") not in LABELS or not g.get("db_name"):
            raise ValueError("invalid gold/DB annotation")
        base=raw["base"][key]["verdict"]
        if base not in LABELS:
            raise ValueError("invalid base model response")
        reports=[]
        for tool in TOOLS:
            pred=raw[tool][key].get("verdict")
            # Real unparsed/absent output is a paid verifier failure, not
            # missing ground truth or a reason to drop an inconvenient claim.
            if pred not in LABELS:
                pred=NO_LABEL
            receipt=trace_receipt(raw[tool][key])
            reports.append({"verdict":pred,"trace":receipt})
        all_rows.append({
            "id":key,"db_name":g["db_name"],"claim":g["claim"],
            "extra_info":g.get("extra_info") or "",
            "context":context(g["claim"]),
            "base":base,
            "truth_evaluator_only":g["label"],
            "reports_evaluator_only":reports,
        })
    databases=sorted({r["db_name"] for r in all_rows},
                     key=lambda s:(hash_str("P5-FALSIFY05-DB-GROUP|"+s),s))
    cutoff=round(.60*len(databases))
    train_dbs=set(databases[:cutoff])
    cal=[r for r in all_rows if r["db_name"] in train_dbs]
    test=[r for r in all_rows if r["db_name"] not in train_dbs]
    if min(len(cal),len(test))<100 or {r["db_name"] for r in cal}&{
        r["db_name"] for r in test}:
        raise ValueError("INVALID_GROUP_SPLIT")
    return cal,test,{
        "sources":manifests,
        "number_of_databases":len(databases),
        "calibration_databases":len(train_dbs),
        "evaluation_databases":len(databases)-len(train_dbs),
        "calibration_count":len(cal),"evaluation_count":len(test),
        "sample_digest":hash_str(json.dumps([(x["id"],"cal" if x in cal else "test")
                       for x in all_rows],separators=(",",":"))),
    }


def symbol(row,tool_index,gated):
    report=row["reports_evaluator_only"][tool_index]
    if report["verdict"]==NO_LABEL:
        return NO_LABEL
    if gated and report["trace"]["outputs"]==0:
        return NO_SQL
    return report["verdict"]


class Joint:
    """Dirichlet-smoothed empirical joint over Y and ALL potential tool outputs.

    No naive conditional-independence assumption across verifiers.
    """
    def __init__(self,records,gated,contextual):
        self.gated=gated
        self.contextual=contextual
        self.symbols=LABELS+(NO_SQL,NO_LABEL) if gated else LABELS+(NO_LABEL,)
        self.universe=tuple(product(LABELS,self.symbols,self.symbols,self.symbols))
        self.cal=records
        self.ctx_counts=Counter(r["context"] for r in records)
        self.groups=defaultdict(Counter)
        for r in records:
            key=("all" if not contextual or self.ctx_counts[r["context"]]<80
                 else r["context"],r["base"])
            observation=tuple(symbol(r,i,gated) for i in range(3))
            self.groups[key][(r["truth_evaluator_only"],)+observation]+=1
            # All-category global fallback requires a full separate tally.
            self.groups[("all",r["base"])][
                (r["truth_evaluator_only"],)+observation]+=(
                    0 if key[0]=="all" else 1)
        self._cache={}

    def category(self,view):
        ctx=view["context"]
        return (ctx if self.contextual and self.ctx_counts[ctx]>=80
                else "all")

    def cells(self,view):
        group=(self.category(view),view["base"])
        if group not in self._cache:
            c=self.groups[group]
            self._cache[group]=tuple((cell,c.get(cell,0)+ALPHA)
                                     for cell in self.universe)
        return self._cache[group]

    def posterior(self,view,observed):
        cells=[(c,n) for c,n in self.cells(view)
               if all(o is None or c[i+1]==o for i,o in enumerate(observed))]
        total=sum(w for _,w in cells)
        if total<=0:
            raise ValueError("zero posterior mass after smoothing")
        p={y:0. for y in LABELS}
        future=[{s:0. for s in self.symbols} for _ in TOOLS]
        for values,weight in cells:
            p[values[0]]+=weight/total
            for i in range(3):
                future[i][values[i+1]]+=weight/total
        return p,future

    def stop(self,view,observed):
        p,_=self.posterior(view,observed)
        scores={lab:3*p[lab]-2 for lab in LABELS}
        answer=max(scores,key=lambda z:scores[z])
        return (scores[answer],answer) if scores[answer]>ABSTAIN+1e-12 else (ABSTAIN,"ABSTAIN")

    def expected_one(self,view,observed,i):
        _,future=self.posterior(view,observed)
        expected=-COST[i]/100
        for z,p in future[i].items():
            if p<=0:continue
            next_obs=list(observed);next_obs[i]=z
            expected+=p*self.stop(view,tuple(next_obs))[0]
        return expected


class Agent:
    def __init__(self,name,cal):
        if name not in DEPLOYABLE:
            raise ValueError("invalid deployable agent")
        self.name=name
        gated=name not in ("bayes_raw_exact","omega_like_no_observability")
        contextual=name in ("bayes_context_exact","omega_like_no_observability",
                            "omega_like_full")
        self.joint=Joint(cal,gated=gated,contextual=contextual)
        self.call_count=0

    def _dp(self,view,observed,cash_left,buy_left):
        """Exact Bellman optimal action under the calibrated joint model."""
        memo={}
        def recurse(obs,cash,remaining):
            key=(obs,cash,remaining)
            if key in memo:return memo[key]
            val,stop_action=self.joint.stop(view,obs)
            best=(val,stop_action)
            if remaining>0:
                _,next_probs=self.joint.posterior(view,obs)
                for i in range(3):
                    if obs[i] is not None or cash<COST[i]:continue
                    expected=-COST[i]/100
                    for outcome,p in next_probs[i].items():
                        if p<=0:continue
                        nxt=list(obs);nxt[i]=outcome
                        expected+=p*recurse(tuple(nxt),cash-COST[i],remaining-1)[0]
                    if expected>best[0]+1e-10:
                        best=(expected,i)
            memo[key]=best
            return best
        return recurse(observed,cash_left,buy_left)

    def action(self,view,observed,cash_left,buy_left):
        self.call_count+=1
        if self.name=="no_tool":
            return self.joint.stop(view,observed)[1]
        if self.name=="fixed_cheapest_two":
            for i in (0,1):
                if observed[i] is None and cash_left>=COST[i] and buy_left>0:
                    return i
            return self.joint.stop(view,observed)[1]
        if self.name in ("bayes_global_exact","bayes_context_exact",
                         "bayes_raw_exact"):
            return self._dp(view,observed,cash_left,buy_left)[1]
        if self.name=="omega_like_no_memory":
            if observed[0] is None and cash_left>=COST[0] and buy_left>0:
                return 0
            if (observed[1] is None and buy_left>0 and cash_left>=COST[1]
                    and observed[0]!=view["base"]):
                return 1
            seen=[x for x in observed if x not in (None,NO_SQL)]
            if len(seen)>=2 and seen[0]==seen[1]:
                return seen[0]
            return "ABSTAIN"
        # Experimentally defined myopic VOI heuristic, NOT Omega P1.
        terminal,stop=self.joint.stop(view,observed)
        best_gain=0.
        chosen=stop
        if buy_left>0:
            for i in range(3):
                if observed[i] is not None or cash_left<COST[i]:continue
                expected=self.joint.expected_one(view,observed,i)
                gain=expected-terminal
                if gain>best_gain+1e-10:
                    best_gain=gain;chosen=i
        return chosen


def view_of(row):
    """A selection algorithm may see ONLY these four public input fields."""
    return {"id":row["id"],"db_name":row["db_name"],
            "base":row["base"],"context":context(row["claim"])}


def read_tool(row,i,gated):
    """Historical output revealed only after a paid action."""
    x=row["reports_evaluator_only"][i]
    return {"symbol":symbol(row,i,gated),
            "trace_available":x["trace"]["trace_available"],
            "tool_output_count":x["trace"]["outputs"],
            "same_source_gold_provider":"claimdb/claimdb",
            "independent_sql_reexecution":False}


def payoff(decision,truth):
    return ABSTAIN if decision=="ABSTAIN" else (1 if decision==truth else -2)


def execute_agent(agent,rows):
    events=[]
    for row in rows:
        view=view_of(row)
        observed=[None,None,None]
        purchased=[]
        paid_cost=0
        visited=[]
        for turn in range(MAX_CALLS+1):
            action=agent.action(view,tuple(observed),MAX_COST-paid_cost,
                                MAX_CALLS-len(purchased))
            if isinstance(action,int):
                if not 0<=action<3 or action in purchased:
                    raise AssertionError("duplicate/invalid paid tool")
                if len(purchased)>=MAX_CALLS or paid_cost+COST[action]>MAX_COST:
                    raise AssertionError("budget exceeded")
                receipt=read_tool(row,action,agent.joint.gated)
                observed[action]=receipt["symbol"]
                purchased.append(action)
                paid_cost+=COST[action]
                visited.append({"tool":TOOLS[action],"outcome":receipt["symbol"],
                     "trace_available":receipt["trace_available"],
                     "tool_output_count":receipt["tool_output_count"],
                     "independent_sql_reexecution":False})
            else:
                decision=action
                break
        else:
            raise AssertionError("policy did not terminate")
        if decision not in LABELS+("ABSTAIN",):
            raise ValueError("invalid selected final answer")
        utility=payoff(decision,row["truth_evaluator_only"])-paid_cost/100
        events.append({
            "id":row["id"],"database":row["db_name"],
            "decision":decision,"bought":list(TOOLS[i] for i in purchased),
            "cost_proxy":round(paid_cost/100,5),
            "total_acquisitions":len(purchased),
            "utility":round(utility,5),
            "correct":decision==row["truth_evaluator_only"],
            "wrong":decision!="ABSTAIN" and decision!=row["truth_evaluator_only"],
            "abstained":decision=="ABSTAIN",
            "gold_evaluator_only":row["truth_evaluator_only"],
            "observed_trace":visited,
        })
    return events


def summarize(events):
    return {
        "N":len(events),
        "mean_utility":round(statistics.mean(e["utility"] for e in events),6),
        "total_utility":round(sum(e["utility"] for e in events),4),
        "purchased_tools":sum(e["total_acquisitions"] for e in events),
        "mean_cost_proxy":round(statistics.mean(e["cost_proxy"] for e in events),6),
        "correct":sum(e["correct"] for e in events),
        "wrong":sum(e["wrong"] for e in events),
        "abstained":sum(e["abstained"] for e in events),
        "evidence_missing_purchased":sum(
          z["outcome"]==NO_SQL for e in events for z in e["observed_trace"]),
    }


def bootstrap_by_database(a,b,n=2000,seed=20261112):
    by_a={x["id"]:x for x in a}
    by_b={x["id"]:x for x in b}
    if set(by_a)!=set(by_b):
        raise ValueError("not paired cases")
    diffs=defaultdict(list)
    for key in by_a:
        x,y=by_a[key],by_b[key]
        if x["database"]!=y["database"]:
            raise ValueError("database grouping mismatch")
        diffs[x["database"]].append(x["utility"]-y["utility"])
    groups=list(sorted(diffs))
    rng=Random(seed)
    stats=[]
    for _ in range(n):
        picked=[groups[rng.randrange(len(groups))] for _ in groups]
        flat=[val for g in picked for val in diffs[g]]
        stats.append(sum(flat)/len(flat))
    stats.sort()
    return {"groups":len(groups),"bootstrap_rounds":n,
            "lower_95":round(stats[int(.025*n)],6),
            "upper_95":round(stats[min(n-1,int(.975*n))],6),
            "mean_difference":round(statistics.mean(
               [d for g in groups for d in diffs[g]]),6)}


def run(root):
    cal,test,manifest=ingest(root)
    simulations={}
    detail={}
    for name in DEPLOYABLE:
        agent=Agent(name,cal)
        ev=execute_agent(agent,test)
        simulations[name]=summarize(ev)
        detail[name]=ev
    # Oracle is NONDEPLOYABLE: sees the true label at no verification cost.
    simulations["hindsight_oracle"]={
        "N":len(test),"mean_utility":1.,"total_utility":float(len(test)),
        "purchased_tools":0,"correct":len(test),
        "wrong":0,"abstained":0,
        "not_deployable":True,"truth_leaked_to_oracle_by_design":True,
    }
    diffs=bootstrap_by_database(detail["omega_like_full"],
                                detail["bayes_context_exact"])
    actions_diff=sum(
        (a["bought"],a["decision"])!=(b["bought"],b["decision"])
        for a,b in zip(detail["omega_like_full"],
                       detail["bayes_context_exact"]))
    receipts={
        tool:{"trace_available_calibration":sum(
                  r["reports_evaluator_only"][i]["trace"]["trace_available"] for r in cal),
              "sql_output_positive_calibration":sum(
                  r["reports_evaluator_only"][i]["trace"]["outputs"]>0 for r in cal),
              "sql_output_positive_test_descriptive":sum(
                  r["reports_evaluator_only"][i]["trace"]["outputs"]>0 for r in test),
              "report_verdict_correct_test_evaluator_only":sum(
                  r["reports_evaluator_only"][i]["verdict"]==r["truth_evaluator_only"]
                  for r in test),
              "no_verdict_calibration":sum(
                  r["reports_evaluator_only"][i]["verdict"]==NO_LABEL for r in cal),
              "no_verdict_test":sum(
                  r["reports_evaluator_only"][i]["verdict"]==NO_LABEL for r in test),
             } for i,tool in enumerate(TOOLS)
    }
    if any(v["trace_available_calibration"]==0 for v in receipts.values()):
        status="REAL_MODEL_RESPONSES_BUT_PROVENANCE_TRACE_UNAVAILABLE"
    else:
        status=STATUS
    return {
        "protocol":PROTOCOL,"status":status,"source_commit":COMMIT,
        "model_calls_now":0,"external_api_cost_usd_now":0,
        "same_gold_benchmark_provider":True,
        "actual_real_historical_model_outputs":True,
        "actual_sql_executed_by_omega":0,
        "models_three_distinct_organisations_not_independent_gold":True,
        "source_manifest":manifest,
        "policy_names":list(POLICIES),
        "policy_summary":simulations,
        "per_case_trajectories":detail,
        "verifier_trace_metadata":receipts,
        "primary_paired_effect_omega_minus_bayes_context":diffs,
        "different_policy_actions_from_bayes_context":actions_diff,
        "omega_like_is_actual_P1_P2_P3":False,
        "source_model_requires_independence":False,
        "limitations":[
          "Source is already-published ClaimDB public 1000 cases, NOT blind unseen gold",
          "Each purchased result is an actual previously observed model prediction, NOT a certified SQL fact",
          "Model organisations differ; all truth labels and tool transcripts hosted by one ClaimDB dataset",
          "Group split by database name avoids same-DB contamination, not common model training contamination",
          "Prices 0.08,0.12,0.16 are preregistered pseudo-costs, NOT measured real API prices",
          "Bellman is EXACT only with respect to learned smoothed JOINT calibration distribution",
          "Omega-like heuristics here are not the deployed P1/P2/P3 orchestrator",
          "Actual judge accuracy uses ClaimDB annotations, not independent SQL re-execution",
          "No human semantic review of the model-reported SQL outputs",
          "A larger score on this one dataset would NOT establish general Omega superiority",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",required=True,type=Path)
    p.add_argument("--output",type=Path)
    o=p.parse_args()
    result=run(o.source_root)
    if o.output:
        o.output.parent.mkdir(parents=True,exist_ok=True)
        o.output.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,
                        indent=2)+"\n",encoding="utf-8")
    print("FALSIFY05_REAL_VERIFIER_SUMMARY",json.dumps({
        "status":result["status"],
        "split":{k:v for k,v in result["source_manifest"].items() if k!="sources"},
        "scores":result["policy_summary"],
        "primary_delta":result["primary_paired_effect_omega_minus_bayes_context"],
        "policy_action_differences":result["different_policy_actions_from_bayes_context"],
        "receipts":result["verifier_trace_metadata"],
    },ensure_ascii=False,sort_keys=True),flush=True)

if __name__=="__main__":
    main()
