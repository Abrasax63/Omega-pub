"""P5-EVID-06: budgeted routing on REAL paired ClaimDB/GPT-5-mini public logs.

No new model calls. SQL-mode is a historically observed *model response*,
NOT an exact verified answer. Both modes share a model family and ClaimDB.
Gold labels NEVER enter policy decisions. Only 24 calibration labels are known.

Experimental Omega candidate = classical contextual VOI with an explicit
same-provider evidence receipt; expected to tie strong classical trace gate.
"""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import json
import re

PROTOCOL="P5-EVID-06"
STATUS="REAL_PAIRED_MODEL_BUDGET_ROUTING_AND_BIRD_SQL_SECONDARY_AUDIT"
SRC_COMMIT="e06c3a22cc14a8ef6858bb5d40bca7925241b98d"
FILES={
  "gold":("final-benchmark/test-public.jsonl",
          "b87d7062307cfcf5ae862bf03bd7e82f7123ff39cf0b69d3dc5cc25caaaea810"),
  "sql":("experiments/public/gpt-5-mini.jsonl",
         "e31443bd85f46c4edc4a146243bb709634c6330c2914c726630c3f3349edb100"),
  "plain":("experiments/public/no_tools/gpt-5-mini.jsonl",
           "552531cba335298816a998f7a2b6fb548d9cd0eb7f9b47e5d1272809620a9aa6"),
}
SENTINELS=(4267,4179,4324,3930,4419,15601,3730,3971)
LABELS=("ENTAILED","CONTRADICTED","NOT ENOUGH INFO")
POLICIES=("no_purchase","position_first_two","hash_random_two","global_voi",
          "context_voi","context_trace_gate","omega_observability_candidate",
          "hindsight_oracle")
DEPLOYABLE=tuple(p for p in POLICIES if p!="hindsight_oracle")
CAL=24
EVAL=64
BATCH=8
PURCHASES=2
COST=.20
ABSTAIN=.05


def _read(filepath,expected_sha):
    raw=Path(filepath).read_bytes()
    if raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
        raise ValueError("UNRESOLVED_GIT_LFS_POINTER")
    digest=sha256(raw).hexdigest()
    if digest!=expected_sha:
        raise ValueError(f"PINNED_SOURCE_SHA256_MISMATCH {filepath}: {digest}")
    rows=[json.loads(x) for x in raw.decode("utf-8").splitlines() if x.strip()]
    if len(rows)!=1000 or len({r["claim_id"] for r in rows})!=1000:
        raise ValueError("original source count/identity mismatch")
    return {r["claim_id"]:r for r in rows},{"sha256":digest,"size":len(raw),"rows":len(rows)}


def load_real_source(root):
    maps={}
    sources={}
    for key,(rel,digest) in FILES.items():
        maps[key],sources[key]=_read(Path(root)/rel,digest)
    if not(set(maps["gold"])==set(maps["sql"])==set(maps["plain"])):
        raise ValueError("different claim_id sets across actual model modes")
    for r in maps["gold"].values():
        if r.get("label") not in LABELS:
            raise ValueError("missing external gold label")
    for key in ("sql","plain"):
        for r in maps[key].values():
            if r.get("verdict") not in LABELS:
                raise ValueError("unparsed real model verdict")
    return maps,sources


def _rank(claim_id):
    return sha256(f"EVID06|2026-11-12|{claim_id}".encode()).hexdigest()


def _context(text):
    text=text.lower()
    if ("hypothetical" in text or "counterfactual" in text or
        re.search(r"\bif\b.{0,180}\b(would|were|could)\b",text)):
        return "hypothetical"
    if any(x in text for x in ("most appealing","more impressive",
            "widely regarded","ideal","preferable","better than",
            "compelling","popular among")):
        return "subjective"
    if re.search(r"\d",text) or any(x in text for x in (
        "exactly","number of","count of","how many","average",
        "percentage","total")):
        return "numeric"
    return "other"


def actual_tool_events(row):
    entries=row.get("to_input_list")
    if not isinstance(entries,list):
        return {"calls":0,"outputs":0,"trace_available":False}
    types=[r.get("type") for r in entries if isinstance(r,dict)]
    return {
        "calls":sum(x in ("function_call","tool_call") for x in types),
        "outputs":sum(x in ("function_call_output","tool_result") for x in types),
        "trace_available":True,
    }


def prepare(maps):
    """Source annotations are not used to select calibrations or test records."""
    candidates=[r for r in maps["gold"].values()
                if r["db_name"]=="superhero" and r["claim_id"] not in SENTINELS]
    if len(candidates)!=112:
        raise ValueError(f"unexpected superhero cohort: {len(candidates)} !=112")
    candidates.sort(key=lambda r:(_rank(r["claim_id"]),r["claim_id"]))
    calibration=candidates[:CAL]
    evaluation=candidates[CAL:CAL+EVAL]
    assert len(calibration)==24 and len(evaluation)==64
    assert not {r["claim_id"] for r in calibration}&{
        r["claim_id"] for r in evaluation}
    table={}
    for r in calibration+evaluation:
        key=r["claim_id"]
        table[key]={
            "claim_id":key,"claim":r["claim"],
            "extra_info":r.get("extra_info") or "",
            "db_name":r["db_name"],
            "context":_context(r["claim"]),
            "no_tools":maps["plain"][key]["verdict"],
            "with_sql":maps["sql"][key]["verdict"],
            "evaluator_only_label":r["label"],
            "evaluator_only_tool_trace":actual_tool_events(maps["sql"][key]),
        }
    digest=sha256(json.dumps(
        [{"id":r["claim_id"],"claim":r["claim"]}
         for r in calibration+evaluation],
        ensure_ascii=False,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return [table[r["claim_id"]] for r in calibration],[
        table[r["claim_id"]] for r in evaluation],digest


def _prob(correct,total):
    return (1+correct)/(2+total)


def calibration_model(rows):
    prior={}
    for category in ("overall","numeric","other","hypothetical","subjective"):
        subset=rows if category=="overall" else [
            r for r in rows if r["context"]==category]
        prior[category]={
            "n":len(subset),
            "plain":_prob(sum(r["no_tools"]==r["evaluator_only_label"]
                              for r in subset),len(subset)),
            "sql":_prob(sum(r["with_sql"]==r["evaluator_only_label"]
                            for r in subset),len(subset)),
        }
    assert prior["overall"]["n"]==24
    return prior


def decision_utility(prob):
    return max(ABSTAIN,3*prob-2)


def route_gain(p_plain,p_sql):
    return decision_utility(p_sql)-COST-decision_utility(p_plain)


def public(row):
    return {
        "claim_id":row["claim_id"],
        "claim":row["claim"],
        "extra_info":row["extra_info"],
        "db_name":row["db_name"],
        "no_tools":row["no_tools"],
        "context":_context(row["claim"]),
        "cost":COST,
    }


def paid_result(row):
    """Reveal historical SQL-mode model answer and log ONLY after routing."""
    return {
        "with_sql":row["with_sql"],
        "trace":row["evaluator_only_tool_trace"],
        "provider":"claimdb/claimdb",
        "provenance":"one same-model-family SQL-assisted run",
    }


class Policy:
    def __init__(self,name,priors):
        if name not in DEPLOYABLE:
            raise ValueError("not a deployable policy")
        self.name=name
        self.priors=priors
        self.audit=[]

    def _prior(self,view):
        if self.name in ("context_voi","context_trace_gate",
                         "omega_observability_candidate"):
            contextual=self.priors[view["context"]]
            if contextual["n"]>=3:
                return contextual
        return self.priors["overall"]

    def choose(self,t,views):
        """Observe only claim text + no-tools verdict. Never see SQL or label."""
        if not isinstance(views,list) or len(views)!=BATCH:
            raise ValueError("eight candidate input views per batch")
        expected={"claim_id","claim","extra_info","db_name","no_tools","context","cost"}
        if any(set(v)!=expected for v in views):
            raise ValueError("evaluator labels, hidden tools or extra fields leaked")
        if len({v["claim_id"] for v in views})!=BATCH:
            raise ValueError("duplicate candidates")
        gains=[route_gain(self._prior(v)["plain"],self._prior(v)["sql"])
               for v in views]
        if self.name=="no_purchase":
            return []
        if self.name=="position_first_two":
            return [0,1]
        if self.name=="hash_random_two":
            return sorted(range(BATCH),key=lambda i:(
                _rank(views[i]["claim_id"]+"100000"),i))[:PURCHASES]
        choices=sorted(range(BATCH),
            key=lambda i:(-gains[i],_rank(views[i]["claim_id"]),i))
        return [i for i in choices if gains[i]>0][:PURCHASES]

    def finish(self,view,paid=None):
        pri=self._prior(view)
        if paid is None:
            return view["no_tools"] if 3*pri["plain"]-2>ABSTAIN else "ABSTAIN"
        if set(paid)!={"with_sql","trace","provider","provenance"}:
            raise ValueError("invalid paid interface")
        if paid["provider"]!="claimdb/claimdb":
            raise ValueError("unrecognized receipt source")
        if self.name in ("context_trace_gate","omega_observability_candidate"):
            if paid["trace"]["outputs"]==0:
                self.audit.append({
                    "id":view["claim_id"],"source":"claimdb/claimdb",
                    "status":"NO_LOGGED_SQL_OUTPUT_NOT_PROOF","independent_providers":0,
                })
                return "ABSTAIN"
        if self.name=="omega_observability_candidate":
            self.audit.append({
                "id":view["claim_id"],"source":"claimdb/claimdb",
                "status":"MODEL_SQL_TOOL_OUTPUT_LOGGED_NOT_INDEPENDENTLY_REPRODUCED",
                "independent_providers":0,
                "logged_outputs":paid["trace"]["outputs"],
            })
        return paid["with_sql"] if 3*pri["sql"]-2>ABSTAIN else "ABSTAIN"


def gain(decision,truth):
    return ABSTAIN if decision=="ABSTAIN" else (1 if decision==truth else -2)


def _hindsight(batches):
    """Nondeployable upper bound; reads truth and both outputs only OFFLINE."""
    events=[]
    for t,batch in enumerate(batches):
        candidates=[]
        for i,r in enumerate(batch):
            truth=r["evaluator_only_label"]
            base=max(gain(r["no_tools"],truth),ABSTAIN)
            routed=max(gain(r["with_sql"],truth),ABSTAIN)-COST
            candidates.append((routed-base,i))
        chosen=set(i for uplift,i in sorted(candidates,reverse=True)[:PURCHASES]
                   if uplift>0)
        for i,r in enumerate(batch):
            truth=r["evaluator_only_label"]
            if i in chosen:
                choice=r["with_sql"] if r["with_sql"]==truth else "ABSTAIN"
                reward=gain(choice,truth)-COST
            else:
                choice=r["no_tools"] if r["no_tools"]==truth else "ABSTAIN"
                reward=gain(choice,truth)
            events.append({
                "round":t,"claim_id":r["claim_id"],"route":i in chosen,
                "decision":choice,"reward":round(reward,6),
                "model_truth_evaluator_only":truth,
            })
    return _summarize(events,[])


def _summarize(events,receipt):
    return {
        "utility":round(sum(e["reward"] for e in events),6),
        "routed":sum(e["route"] for e in events),
        "correct_published":sum(e["decision"]==e["model_truth_evaluator_only"]
                                for e in events),
        "wrong_published":sum(e["decision"]!="ABSTAIN" and
                              e["decision"]!=e["model_truth_evaluator_only"]
                              for e in events),
        "abstentions":sum(e["decision"]=="ABSTAIN" for e in events),
        "events":events,
        "provenance_certificates":receipt,
    }


def evaluate(calibration,testing):
    if len(calibration)!=CAL or len(testing)!=EVAL:
        raise ValueError("incomplete splits")
    pri=calibration_model(calibration)
    batches=[testing[i:i+BATCH] for i in range(0,EVAL,BATCH)]
    results={}
    for name in DEPLOYABLE:
        policy=Policy(name,pri)
        events=[]
        for t,batch in enumerate(batches):
            views=[public(r) for r in batch]
            selected=policy.choose(t,views)
            if (len(selected)>PURCHASES or len(set(selected))!=len(selected)
                or any(type(i) is not int or not 0<=i<BATCH for i in selected)):
                raise AssertionError("overbudget/invalid routing")
            for i,(row,view) in enumerate(zip(batch,views)):
                routed=i in selected
                paid=paid_result(row) if routed else None
                decision=policy.finish(view,paid)
                reward=gain(decision,row["evaluator_only_label"])-(COST if routed else 0)
                events.append({
                    "round":t,"claim_id":row["claim_id"],"context":row["context"],
                    "route":routed,"decision":decision,
                    "reward":round(reward,6),
                    "no_tools_verdict":row["no_tools"],
                    "sql_verdict_evaluator_only":row["with_sql"],
                    "model_truth_evaluator_only":row["evaluator_only_label"],
                    "tool_outputs_if_purchased":
                        paid["trace"]["outputs"] if paid else None,
                })
        results[name]=_summarize(events,policy.audit)
        assert results[name]["routed"]<=16
        assert results[name]["correct_published"]+results[name]["wrong_published"]+results[name]["abstentions"]==64
    results["hindsight_oracle"]=_hindsight(batches)
    if results["context_trace_gate"]["events"]!=results["omega_observability_candidate"]["events"]:
        raise AssertionError("Omega protocol is not equivalent to classical trace gate")
    strong=("global_voi","context_voi","context_trace_gate","omega_observability_candidate")
    patterns={
      name:tuple(e["claim_id"] for e in results[name]["events"] if e["route"])
      for name in strong
    }
    same_all=len(set(patterns.values()))==1
    return pri,results,{
        "strong_routes_identical":same_all,
        "strong_unique_routing_patterns":len(set(patterns.values())),
        "design_gate":"BENCHMARK_NON_DISCRIMINATING" if same_all else "PASS_DIFFERENT_ROUTES",
        "omega_minus_classical_trace_gate":round(
            results["omega_observability_candidate"]["utility"]-
            results["context_trace_gate"]["utility"],6),
        "omega_vs_classical_action_differences":sum(
            a["route"]!=b["route"] or a["decision"]!=b["decision"]
            for a,b in zip(results["omega_observability_candidate"]["events"],
                            results["context_trace_gate"]["events"])),
    }


def run(root):
    maps,sources=load_real_source(root)
    calibration,testing,selection_digest=prepare(maps)
    pri,results,diagnostics=evaluate(calibration,testing)
    assert len(testing)==64 and len(calibration)==24
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "sources":sources,
        "claimdb_commit":SRC_COMMIT,
        "sample_selection_sha256":selection_digest,
        "calibration_size":len(calibration),
        "testing_size":len(testing),
        "source_provider_count":1,
        "new_inferences":0,"paid_api_calls":0,
        "paid_tool_is_exact_verifier":False,
        "calibration":{k:{"id":x["claim_id"],"context":x["context"]}
                       for k,x in enumerate(calibration)},
        "priors":pri,
        "policies":results,
        "diagnostics":diagnostics,
        "limitations":[
          "Historic publicly-known ClaimDB public test, not a blind holdout",
          "SQL-tool mode is an existing GPT-5-mini response, NOT exact database truth",
          "The two modes share a model family and a single ClaimDB benchmark provider",
          "No test label is revealed to any policy; no online supervised learning",
          "Context regex authored by the same operator, not third-party reviewed",
          "Fixed 0.20 utility cost does not measure original inference time or API spend",
          "Budgeted routing is an offline potential-outcome replay, not live tool routing",
          "Omega candidate is a classical VOI trace gate plus provenance log, not P1 adaptation",
        ],
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",type=Path,required=True)
    p.add_argument("--output",type=Path)
    opt=p.parse_args()
    x=run(opt.source_root)
    if opt.output:
        opt.output.parent.mkdir(parents=True,exist_ok=True)
        opt.output.write_text(json.dumps(x,ensure_ascii=False,sort_keys=True,
                                      indent=2)+"\n",encoding="utf-8")
    print("EVID06_ROUTING_SUMMARY",json.dumps({
      "calibration":x["calibration_size"],
      "test":x["testing_size"],
      "priors":x["priors"],
      "diagnostics":x["diagnostics"],
      "scores":{n:{k:r[k] for k in ("utility","routed","correct_published",
                "wrong_published","abstentions")} for n,r in x["policies"].items()},
      "sources":x["sources"],
    },ensure_ascii=False,sort_keys=True),flush=True)


if __name__=="__main__":
    main()
