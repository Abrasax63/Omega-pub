"""P5-ADAPT-02: frozen calibration and decision-gated changes, synthetic only.

Reuses P5-ADAPT-01's exact world without exposing its hidden probabilities to
controllers. P1 is invoked for a plan, not for learning. The adaptive controller
is an experimental *new* numerical layer, never a deployed Omega capability.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

import p5_adapt01_loop as world
from planner import plan_mission

PROTOCOL="P5-ADAPT-02"
STATUS="SYNTHETIC_ONLY_NO_INDEPENDENT_MODEL_VALIDATION"
ACTIONS=world.ACTIONS
REGIMES=world.REGIMES
HORIZON=world.HORIZON
CALIBRATION_SEEDS=tuple(range(0,32))
TEST_SEEDS=tuple(range(100,164))
THRESHOLDS=(.375,.50,.625,.75)
FALSE_ALARM_LIMIT=.50
COOLDOWN=28
BLOCK=8
PROBATION_LENGTH=20
COMMIT_LENGTH=20
PROMOTION_MARGIN=.25
BASELINES=("fixed_verify","ucb_stationary","sw_ucb",
           "discount_ucb","restart_ucb")
CANDIDATES=("omega_gated","omega_no_gate","omega_no_memory")
POLICIES=BASELINES+CANDIDATES
CHANGE_POINTS={"stationary":(),"abrupt":(60,120),
               "recurrent":(45,90,135),"gradual":()}

class GatedController:
    """Accepts only chosen-action rewards, never regime, truth or counterfactuals."""
    def __init__(self,name,threshold):
        if name not in CANDIDATES:raise ValueError("unknown candidate")
        if threshold not in THRESHOLDS:raise ValueError("threshold outside frozen grid")
        self.name=name
        self.threshold=threshold
        self.observed=[]              # append-only; never reset
        self.mode="stable"
        self.last_alarm=-10000
        self.alarms=[]
        self.promotions=0
        self.rejections=0
        self.events=[]
        self.incumbent=None
        self.challenger=None
        self.probes={"incumbent":[],"challenger":[]}
        self.phase_left=0
        self.commit_left=0
        self.committed=None
        plan=plan_mission({
            "question":"Réviser une décision après observation contradictoire, "
                       "valider toute nouvelle stratégie avant adoption.",
            "mission_type":"general",
            "decision_context":{
                "blocking_uncertainty":"La stabilité des retours est inconnue",
                "verification":"Comparer les gains observés de deux politiques candidates",
                "verification_effect":"Accepter ou annuler une révision",
            },
        })
        if plan["next_action"]["action"]!="verify":
            raise AssertionError("P1 did not plan observation verification")
        self.planner_version=plan["planner_version"]

    def choose(self,t):
        if not isinstance(t,int) or t<0:
            raise ValueError("invalid time")
        if self.mode=="probation":
            # Paired chronological interleaving, one *observed* action per t.
            return self.incumbent if self.phase_left%2==0 else self.challenger
        if self.mode=="commit":
            return self.committed
        return world._ucb_from_history(self.observed,t,36)

    def _alternative(self,incumbent):
        # Only previously observed data; unavailable action has neutral +0.08.
        span=12 if self.name=="omega_no_memory" else 48
        scores={}
        for a in ACTIONS:
            if a==incumbent:continue
            rows=[r for _,name,r in self.observed if name==a][-span:]
            scores[a]=sum(rows)/len(rows) if rows else world.REWARD_ABSTAIN
        return max(scores,key=lambda a:(scores[a],-ACTIONS.index(a)))

    def _triggered(self,action):
        if action not in ACTIONS[:2]:return False
        rewards=[r for _,a,r in self.observed if a==action]
        if len(rewards)<2*BLOCK:return False
        first=rewards[-2*BLOCK:-BLOCK]
        second=rewards[-BLOCK:]
        earlier=sum(r>0 for r in first)/BLOCK
        later=sum(r>0 for r in second)/BLOCK
        return abs(earlier-later)>=self.threshold

    def observe(self,t,action,reward):
        if action not in ACTIONS or not isinstance(t,int) or t<0:
            raise ValueError("invalid observed action/time")
        if not isinstance(reward,(int,float)) or not -2.2-1e-8<=reward<=1.0+1e-8:
            raise ValueError("invalid observed reward")
        if self.observed and t<=self.observed[-1][0]:
            raise ValueError("non-monotonic observation")
        self.observed.append((t,action,float(reward)))
        if self.mode=="probation":
            label="incumbent" if self.phase_left%2==0 else "challenger"
            expected=self.incumbent if label=="incumbent" else self.challenger
            if action!=expected:
                raise AssertionError("probe mismatch")
            self.probes[label].append(float(reward))
            self.phase_left-=1
            if self.phase_left==0:
                assert len(self.probes["incumbent"])==10
                assert len(self.probes["challenger"])==10
                old=sum(self.probes["incumbent"])/10
                new=sum(self.probes["challenger"])/10
                accepted=(new-old)>PROMOTION_MARGIN
                self.committed=self.challenger if accepted else self.incumbent
                if accepted:
                    self.promotions+=1
                    result="promote"
                else:
                    self.rejections+=1
                    result="reject_proposal_keep_history"
                self.mode="commit"
                self.commit_left=COMMIT_LENGTH
                self.events.append({"t":t,"event":result,"observed_delta":round(new-old,4)})
            return
        if self.mode=="commit":
            if action!=self.committed:
                raise AssertionError("committed action mismatch")
            self.commit_left-=1
            if self.commit_left==0:
                self.events.append({"t":t,"event":"end_commit"})
                self.mode="stable"
                self.committed=None
            return
        if t-self.last_alarm<COOLDOWN or not self._triggered(action):
            return
        self.last_alarm=t
        self.alarms.append(t)
        self.incumbent=world._ucb_from_history(self.observed,t+1,36)
        self.challenger=self._alternative(self.incumbent)
        if self.challenger==self.incumbent:
            raise AssertionError("unchanged strategy proposal")
        self.events.append({
            "t":t,"event":"alarm","action_observed":action,
            "incumbent":self.incumbent,"challenger":self.challenger,
        })
        if self.name=="omega_no_gate":
            self.committed=self.challenger
            self.mode="commit"
            self.commit_left=COMMIT_LENGTH
            self.promotions+=1
            self.events.append({"t":t,"event":"immediate_commit_no_validation"})
        else:
            self.probes={"incumbent":[],"challenger":[]}
            self.mode="probation"
            self.phase_left=PROBATION_LENGTH

def _make_policy(name,threshold):
    return GatedController(name,threshold) if name in CANDIDATES else world.Policy(name)

def simulate(regime,seed,name,threshold,trace=False):
    """The evaluator owns the hidden world; controller only sees its own reward."""
    if regime not in REGIMES:raise ValueError("unknown regime")
    if seed not in CALIBRATION_SEEDS and seed not in TEST_SEEDS:
        raise ValueError("unregistered split")
    if name not in POLICIES:raise ValueError("unknown policy")
    p=_make_policy(name,threshold)
    utility=0.0
    expected=0.0
    oracle=0.0
    errors=0
    checks=0
    abstentions=0
    digest=sha256()
    visible_trace=[]
    for t in range(HORIZON):
        a=p.choose(t)
        if a not in ACTIONS:raise AssertionError("invalid action")
        # Only the EVALUATOR can consult hidden counterfactual means.
        means=world._expected_rewards(regime,seed,t)
        gain=world._reward(regime,seed,t,a)
        p.observe(t,a,gain)
        utility+=gain
        expected+=means[a]
        oracle+=max(means.values())
        errors+=int(gain<=-2.0+1e-10)
        checks+=int(a=="VERIFY")
        abstentions+=int(a=="ABSTAIN")
        event={"t":t,"action":a,"reward":round(gain,4)}
        digest.update(json.dumps(event,sort_keys=True).encode()+b"\n")
        if trace:visible_trace.append(event)
    is_candidate=isinstance(p,GatedController)
    alarms=p.alarms if is_candidate else []
    out={
        "regime":regime,"seed":seed,"policy":name,
        "regret":round(max(0.0,oracle-expected),6),
        "realized_utility":round(utility,6),
        "errors":errors,"verifications":checks,
        "verification_cost":round(checks*world.PENALTY_VERIFY,6),
        "abstentions":abstentions,
        "alarms":len(alarms),
        "alarm_times":list(alarms),
        "promotions":p.promotions if is_candidate else None,
        "rejected_proposals":p.rejections if is_candidate else None,
        "observed_trace_sha256":digest.hexdigest(),
        "observed_count":len(p.observed) if is_candidate else len(p.all_observed),
        "planner_version":p.planner_version if is_candidate else None,
    }
    if trace:
        out["observed_trace"]=visible_trace
        out["decisions_events"]=list(p.events) if is_candidate else []
    return out

def calibrate():
    """Uses only indices 0-31, never reads evaluation seeds 100-163."""
    choices=[]
    for threshold in THRESHOLDS:
        by_regime={}
        for regime in REGIMES:
            vals=[simulate(regime,s,"omega_gated",threshold)
                  for s in CALIBRATION_SEEDS]
            by_regime[regime]={
                "mean_regret":round(sum(x["regret"] for x in vals)/len(vals),6),
                "mean_alarms":round(sum(x["alarms"] for x in vals)/len(vals),6),
            }
        regret=sum(by_regime[r]["mean_regret"]
                   for r in REGIMES if r!="stationary")/3
        qualifies=by_regime["stationary"]["mean_alarms"]<=FALSE_ALARM_LIMIT
        choices.append({
            "threshold":threshold,
            "qualifies_stationary_guardrail":qualifies,
            "calibration_mean_changing_regret":round(regret,6),
            "by_regime":by_regime,
        })
    valid=[x for x in choices if x["qualifies_stationary_guardrail"]]
    if valid:
        selected=min(valid,key=lambda x:(
            x["calibration_mean_changing_regret"],-x["threshold"]))
        status="CALIBRATED_WITH_STATIONARY_GUARDRAIL"
    else:
        selected=next(x for x in choices if x["threshold"]==max(THRESHOLDS))
        status="CALIBRATION_GUARDRAIL_FAILED_FALLBACK_MAX_THRESHOLD"
    return {
        "status":status,
        "threshold":selected["threshold"],
        "stationary_false_alarm_target":FALSE_ALARM_LIMIT,
        "calibration_episode_count":len(CALIBRATION_SEEDS)*len(REGIMES),
        "candidates":choices,
    }

def _detection(alarms,regime):
    cps=CHANGE_POINTS[regime]
    seen=[]
    for cp in cps:
        nearby=[t-cp for t in alarms if cp<=t<=cp+30]
        seen.append(min(nearby) if nearby else None)
    return seen

def evaluate():
    cal=calibrate()
    threshold=cal["threshold"]
    rows=[]
    for regime in REGIMES:
        for seed in TEST_SEEDS:
            for name in POLICIES:
                rows.append(simulate(
                    regime,seed,name,threshold,
                    trace=(seed==TEST_SEEDS[0] and
                           name in ("omega_gated","omega_no_gate","sw_ucb"))
                ))
    lookup={(x["regime"],x["seed"],x["policy"]):x for x in rows}
    summaries={}
    for regime in REGIMES:
        pol={}
        for name in POLICIES:
            sample=[lookup[regime,s,name] for s in TEST_SEEDS]
            pol[name]={
                "episodes":len(sample),
                "mean_regret":round(sum(x["regret"] for x in sample)/len(sample),6),
                "mean_utility":round(sum(x["realized_utility"] for x in sample)/len(sample),6),
                "total_errors":sum(x["errors"] for x in sample),
                "total_checks":sum(x["verifications"] for x in sample),
                "total_abstentions":sum(x["abstentions"] for x in sample),
                "total_alarms":sum(x["alarms"] for x in sample),
                "total_promotions":sum(x["promotions"] or 0 for x in sample),
                "total_rejections":sum(x["rejected_proposals"] or 0 for x in sample),
            }
        best=min(BASELINES,key=lambda k:pol[k]["mean_regret"])
        diff=[]
        counts={"wins":0,"ties":0,"losses":0}
        for seed in TEST_SEEDS:
            d=(lookup[regime,seed,"omega_gated"]["regret"]-
               lookup[regime,seed,"sw_ucb"]["regret"])
            diff.append(round(d,6))
            counts["wins" if d<-1e-8 else "losses" if d>1e-8 else "ties"]+=1
        possible=len(CHANGE_POINTS[regime])*len(TEST_SEEDS)
        detected=[]
        for seed in TEST_SEEDS:
            a=lookup[regime,seed,"omega_gated"]["alarm_times"]
            detected.extend(_detection(a,regime))
        seen=[x for x in detected if x is not None]
        summaries[regime]={
            "by_policy":pol,
            "best_baseline_posthoc":best,
            "omega_minus_sw_ucb_mean_regret":round(sum(diff)/len(diff),6),
            "omega_minus_best_posthoc":round(
                pol["omega_gated"]["mean_regret"]-pol[best]["mean_regret"],6),
            "paired_omega_vs_sw_ucb":counts,
            "paired_differences":diff,
            "change_detection":{
                "known_change_points_evaluator_only":list(CHANGE_POINTS[regime]),
                "total_true_change_events":possible,
                "detected_within_30_decisions":len(seen),
                "mean_delay_detected":round(sum(seen)/len(seen),6) if seen else None,
            },
        }
    return {
        "protocol":PROTOCOL,"status":STATUS,
        "calibration":cal,
        "calibration_seeds":list(CALIBRATION_SEEDS),
        "evaluation_seeds":list(TEST_SEEDS),
        "total_evaluation_episodes":len(REGIMES)*len(TEST_SEEDS),
        "policy_rollouts":len(rows),
        "world_version_sha256":sha256(json.dumps(
            {"profiles":world.PROFILES,"horizon":HORIZON,"regimes":REGIMES},
            sort_keys=True).encode()).hexdigest(),
        "paid_api_calls":0,"model_generations":0,"private_data_read":False,
        "results":summaries,
        "rollouts":rows,
        "limitations":[
            "Author-designed known synthetic bandit generator, no real LLM errors",
            "Calibration seed split is not a third-party holdout",
            "Candidate controller new experimental layer, not existing Omega P1",
            "Probation compares actions at different times, never counterfactual pairs",
            "False alarms calibrated empirically only; no statistical guarantee",
            "Best per-regime baseline selected after evaluation is nondeployable",
        ],
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    opt=ap.parse_args()
    result=evaluate()
    if opt.output:
        dest=Path(opt.output)
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,
                      indent=2)+"\n",encoding="utf-8")
    print("ADAPT02_SUMMARY "+json.dumps({
        "status":result["status"],"calibration":result["calibration"],
        "evaluation_episodes":result["total_evaluation_episodes"],
        "rollouts":result["policy_rollouts"],
        "summary":{regime:{
            "omega":x["by_policy"]["omega_gated"]["mean_regret"],
            "sw_ucb":x["by_policy"]["sw_ucb"]["mean_regret"],
            "no_gate":x["by_policy"]["omega_no_gate"]["mean_regret"],
            "no_memory":x["by_policy"]["omega_no_memory"]["mean_regret"],
            "best_baseline":x["best_baseline_posthoc"],
            "omega_alarms":x["by_policy"]["omega_gated"]["total_alarms"],
            "omega_rejections":x["by_policy"]["omega_gated"]["total_rejections"],
            "omega_promotions":x["by_policy"]["omega_gated"]["total_promotions"],
            "change_detection":x["change_detection"],
        } for regime,x in result["results"].items()}
    },ensure_ascii=False,sort_keys=True))

if __name__=="__main__":main()
