"""OMEGA-PROBE-001. Deterministic adaptive modular verification experiment.

The hidden x is uniformly sampled from range(60). Every arm gets the same
public modular probe/query model, probe prices and prior, never the true x
before choosing each action. The score is logical work units, NOT seconds.
All arithmetic uses exact integer totals over finite belief states.

The "Omega" arm is a newly constructed receding-horizon-2 selector, not the
original Omega planner or a claim of algorithmic novelty. A full adaptive
DP and exhaustive best fixed ordering are stronger controls.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
from hashlib import sha256
from itertools import permutations
import json
from pathlib import Path

CASE_FILE=Path(__file__).with_name("probe_strategy_cases_2026-11-11.json")
WORLD_COUNT=60
FULL_MASK=(1<<WORLD_COUNT)-1
ARMS=("ZERO","GREEDY1","OMEGA_LOOKAHEAD2","FIXED_BEST","ADAPTIVE_DP_EXACT")


def check_case(s):
    if set(s)!={"id","split","queries","probes"}:
        raise ValueError("malformed scenario")
    if s["split"] not in ("calibration","test"):
        raise ValueError("bad scenario split")
    if not (3<=len(s["probes"])<=8 and len(s["queries"])==5):
        raise ValueError("unexpected number of probes/queries")
    if len({x["id"] for x in s["probes"]})!=len(s["probes"]):
        raise ValueError("duplicate probe")
    for p in s["probes"]:
        if set(p)!={"id","r","m","cost"} or not p["id"].startswith("p"):
            raise ValueError("invalid probe schema")
        if type(p["cost"]) is not int or p["cost"]<=0:
            raise ValueError("cost must be positive integer")
    for p in s["probes"]+s["queries"]:
        if type(p["r"]) is not int or type(p["m"]) is not int:
            raise ValueError("bad modulus/residue type")
        if p["m"]<=0 or WORLD_COUNT%p["m"] or not (0<=p["r"]<p["m"]):
            raise ValueError("bad congruence")
    return s


def mask_for(item):
    return sum(1<<x for x in range(WORLD_COUNT)
               if x%item["m"]==item["r"])


class Scenario:
    def __init__(self,s,penalty=5):
        check_case(s)
        self.case=s
        self.name=s["id"]
        self.split_name=s["split"]
        self.probes=s["probes"]
        self.costs=tuple(p["cost"] for p in self.probes)
        self.pmasks=tuple(mask_for(p) for p in self.probes)
        self.qmasks=tuple(mask_for(q) for q in s["queries"])
        self.n=len(self.probes)
        self.full=(1<<self.n)-1
        self.penalty=penalty
        self._dp_calls=0

    @lru_cache(None)
    def unresolved(self,belief):
        return sum(0< (belief&mask).bit_count() < belief.bit_count()
                   for mask in self.qmasks)

    def stop_loss(self,belief):
        """Sum over all equally likely hidden worlds in belief."""
        return self.penalty*self.unresolved(belief)*belief.bit_count()

    def split(self,belief,i):
        positive=belief & self.pmasks[i]
        negative=belief ^ positive
        return positive,negative

    @lru_cache(None)
    def optimal(self,belief,remaining,horizon):
        """(total loss over this belief, action index or None).

        Horizon == -1 means full remaining lookahead. Every branch carries
        exact integer sums of loss, with no floating-point approximation.
        Stopping wins ties. Probe index breaks action ties.
        """
        best=self.stop_loss(belief)
        chosen=None
        if not remaining or horizon==0 or self.unresolved(belief)==0:
            return best,chosen
        hnext=horizon-1 if horizon>0 else -1
        for i in range(self.n):
            if not (remaining>>i)&1:
                continue
            yes,no=self.split(belief,i)
            if not yes or not no:
                continue
            rem=remaining & ~(1<<i)
            objective=self.costs[i]*belief.bit_count()
            objective+=self.optimal(yes,rem,hnext)[0]
            objective+=self.optimal(no,rem,hnext)[0]
            if objective<best:
                best=objective
                chosen=i
        return best,chosen

    @lru_cache(None)
    def static_value(self,belief,ordered,pos):
        """Bayes-optimal STOP for a given globally fixed probe ordering.

        No contingent *choice of next probe*, but may stop based on earlier
        answers and skip a probe that cannot partition the current belief.
        """
        best=self.stop_loss(belief)
        if pos==len(ordered) or self.unresolved(belief)==0:
            return best
        i=ordered[pos]
        yes,no=self.split(belief,i)
        if not yes or not no:
            return self.static_value(belief,ordered,pos+1)
        objective=(self.costs[i]*belief.bit_count()
                   +self.static_value(yes,ordered,pos+1)
                   +self.static_value(no,ordered,pos+1))
        return min(best,objective)

    def choose_fixed_order(self):
        best=self.stop_loss(FULL_MASK)
        selected=()
        for order in permutations(range(self.n)):
            loss=self.static_value(FULL_MASK,order,0)
            if loss<best:
                best,selected=loss,order
        return best,selected

    def fixed_decision(self,belief,order,pos):
        while pos<len(order):
            if self.unresolved(belief)==0:
                return None,pos
            i=order[pos]
            yes,no=self.split(belief,i)
            if not yes or not no:
                pos+=1
                continue
            cont=(self.costs[i]*belief.bit_count()
                  +self.static_value(yes,order,pos+1)
                  +self.static_value(no,order,pos+1))
            return (i if cont<self.stop_loss(belief) else None),pos
        return None,pos

    def trace(self,world,arm,order):
        if type(world) is not int or not 0<=world<WORLD_COUNT:
            raise ValueError("hidden world must be 0..59")
        if arm not in ARMS:
            raise ValueError("unknown arm")
        belief=FULL_MASK
        rem=self.full
        total_cost=0
        queries=0
        steps=[]
        pos=0
        while rem:
            if arm=="ZERO":
                chosen=None
            elif arm=="GREEDY1":
                chosen=self.optimal(belief,rem,1)[1]
            elif arm=="OMEGA_LOOKAHEAD2":
                chosen=self.optimal(belief,rem,2)[1]
            elif arm=="ADAPTIVE_DP_EXACT":
                chosen=self.optimal(belief,rem,-1)[1]
            else:
                chosen,pos=self.fixed_decision(belief,order,pos)
            if chosen is None:
                break
            if not (rem>>chosen)&1:
                raise AssertionError("repeated probe")
            old_belief=belief
            yes,no=self.split(belief,chosen)
            outcome=bool((1<<world)&self.pmasks[chosen])
            belief=yes if outcome else no
            if not belief:
                raise AssertionError("policy was given hidden world before probing")
            rem &= ~(1<<chosen)
            queries+=1
            total_cost+=self.costs[chosen]
            steps.append({
                "probe":self.probes[chosen]["id"],
                "index":chosen,
                "answer":outcome,
                "belief_size_before":old_belief.bit_count(),
                "belief_size_after":belief.bit_count(),
                "cost":self.costs[chosen],
            })
            if arm=="FIXED_BEST":
                pos+=1
        truth=[]
        for qmask in self.qmasks:
            positives=(belief&qmask).bit_count()
            if positives==belief.bit_count():
                status="entailed"
                if not (1<<world)&qmask:raise AssertionError("false entailment")
            elif positives==0:
                status="refuted"
                if (1<<world)&qmask:raise AssertionError("false refutation")
            else:
                status="undetermined"
            truth.append(status)
        unresolved=sum(v=="undetermined" for v in truth)
        loss=total_cost+self.penalty*unresolved
        return {
            "world":world,"arm":arm,
            "cost":total_cost,"probe_calls":queries,
            "undetermined_queries":unresolved,
            "resolved_queries":len(truth)-unresolved,
            "total_loss":loss,
            "truth_statuses":truth,
            "trace":steps,
            "final_belief_size":belief.bit_count(),
        }


def evaluate(data):
    if (data["id"]!="OMEGA-PROBE-001" or data["worlds"]!=WORLD_COUNT
        or data["prior"]!="uniform"
        or data["unresolved_query_penalty_units"]!=5
        or len(data["scenario_list"])!=4):
        raise ValueError("preregistered experiment contract changed")
    scored={}
    all_traces=[]
    for raw in data["scenario_list"]:
        s=Scenario(raw,5)
        fixed_loss,order=s.choose_fixed_order()
        expected_exact=s.optimal(FULL_MASK,s.full,-1)[0]
        horizon1=s.optimal(FULL_MASK,s.full,1)[0]
        horizon2=s.optimal(FULL_MASK,s.full,2)[0]
        if horizon2>horizon1 or expected_exact>horizon2 or expected_exact>fixed_loss:
            raise AssertionError("invalid exact Bellman bounds")
        traces={arm:[s.trace(world,arm,order)
                     for world in range(WORLD_COUNT)] for arm in ARMS}
        stats={}
        for arm,items in traces.items():
            sum_loss=sum(x["total_loss"] for x in items)
            sum_calls=sum(x["probe_calls"] for x in items)
            stat={
                "sum_total_loss_exact":sum_loss,
                "mean_loss":round(sum_loss/WORLD_COUNT,6),
                "mean_probe_calls":round(sum_calls/WORLD_COUNT,6),
                "mean_verification_cost":round(
                    sum(x["cost"] for x in items)/WORLD_COUNT,6),
                "mean_resolved_queries":round(
                    sum(x["resolved_queries"] for x in items)/WORLD_COUNT,6),
                "worst_case_total_loss":max(x["total_loss"] for x in items),
                "false_certificates":0,
            }
            stats[arm]=stat
        if stats["ADAPTIVE_DP_EXACT"]["sum_total_loss_exact"]!=expected_exact:
            raise AssertionError("DP policy did not achieve exact Bellman value")
        if stats["FIXED_BEST"]["sum_total_loss_exact"]!=fixed_loss:
            raise AssertionError("fixed ordering mismatched exhaustive expected loss")
        if any(stats["ADAPTIVE_DP_EXACT"]["sum_total_loss_exact"]>
               stats[arm]["sum_total_loss_exact"] for arm in ARMS):
            raise AssertionError("optimal adaptive was worse than an admissible arm")
        all_traces.extend({"scenario":s.name,"split":s.split_name,**trace}
                          for items in traces.values() for trace in items)
        scored[s.name]={
            "split":s.split,
            "n_probes":s.n,
            "n_queries":len(s.qmasks),
            "best_fixed_probe_order":[s.probes[i]["id"] for i in order],
            "truncated_horizon1_initial_loss_sum":horizon1,
            "truncated_horizon2_initial_loss_sum":horizon2,
            "full_adaptive_exact_loss_sum":expected_exact,
            "fixed_schedule_optimum_loss_sum":fixed_loss,
            "arm_metrics":stats,
        }
    return {
        "status":"SYNTHETIC_EXACT_ADAPTIVE_VERIFICATION_NOT_EXTERNAL",
        "source_cases_commit":"883cbe181bac982b8f30d5128f8f16a0381f79f9",
        "prereg_commit":"a539c2df214f2dd9fa4f410461f82e8dae38f341",
        "scenario_count":4,
        "worlds_per_scenario":WORLD_COUNT,
        "main_comparison":"adaptive_lookahead2_vs_strong_fixed_and_full_dp",
        "cost_unit":"abstract verification units",
        "model_type":"finite Bayesian cost-sensitive policy, not original Omega",
        "source_authenticity_checked":False,
        "external_problems_solved":0,
        "lean_4_formal_checks_executed":0,
        "scenarios":scored,
        "ledger":all_traces,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json-output")
    args=ap.parse_args()
    result=evaluate(json.loads(CASE_FILE.read_text(encoding="utf-8")))
    if args.json_output:
        Path(args.json_output).write_text(
            json.dumps(result,sort_keys=True,indent=2,ensure_ascii=False),
            encoding="utf-8")
    print("OMEGA_PROBE_STRATEGY_RESULT "+json.dumps({
        "status":result["status"],
        "model_type":result["model_type"],
        "scenarios":result["scenarios"],
        "worlds_per_scenario":result["worlds_per_scenario"],
    },sort_keys=True,ensure_ascii=False))


if __name__=="__main__":
    main()
