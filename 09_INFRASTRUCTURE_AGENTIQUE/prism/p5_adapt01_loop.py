"""P5-ADAPT-01: public synthetic online adaptation against strong controls.

WARNING: not a language-model experiment. P1 plans; it is not trained here.
The Omega candidate is a *new experimental* controller with observations,
mode switches, snapshots, weak memory priors and rollback. All controls see
only the chosen action's outcome. World probabilities are evaluation-only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import math
from pathlib import Path

from planner import plan_mission

EXPERIMENT="P5-ADAPT-01"
STATUS="SYNTHETIC_ONLINE_ADAPTATION_NOT_REAL_MODEL_VALIDATION"
ACTIONS=("DIRECT","VERIFY","ABSTAIN")
REGIMES=("stationary","abrupt","recurrent","gradual")
EPISODES=32
HORIZON=180
PENALTY_VERIFY=0.20
REWARD_ABSTAIN=0.08
BONUS=0.65
PROFILES={
    "direct_good":(.92,.94),
    "direct_bad":(.32,.91),
    "verify_bad":(.76,.42),
    "both_bad":(.38,.40),
}
BASELINES=("fixed_direct","fixed_verify","fixed_abstain",
           "ucb_stationary","sw_ucb","discount_ucb","restart_ucb")
ADAPTIVE=("omega_candidate","omega_no_memory","omega_no_rollback")
POLICIES=BASELINES+ADAPTIVE

def _hash_number(*parts):
    return int.from_bytes(sha256(
        ("P5ADAPT01|"+"|".join(map(str,parts))).encode("utf-8")
    ).digest()[:8],"big")

def _world_probabilities(regime,seed,t):
    """Private environment representation; not passed into any controller."""
    if regime=="stationary":
        return PROFILES["both_bad"] if seed%4==0 else (
            PROFILES["direct_bad"] if seed%2 else PROFILES["direct_good"])
    if regime=="abrupt":
        return PROFILES["direct_good"] if t<60 or t>=120 else PROFILES["direct_bad"]
    if regime=="recurrent":
        key=("direct_good" if t<45 else "direct_bad" if t<90
             else "verify_bad" if t<135 else "direct_bad")
        return PROFILES[key]
    if regime=="gradual":
        a=(t/(HORIZON-1))
        x=PROFILES["direct_good"]
        y=PROFILES["direct_bad"]
        return tuple(x[i]*(1-a)+y[i]*a for i in (0,1))
    raise ValueError("unknown regime")

def _expected_rewards(regime,seed,t):
    pd,pv=_world_probabilities(regime,seed,t)
    return {"DIRECT":3*pd-2,"VERIFY":3*pv-2-PENALTY_VERIFY,
            "ABSTAIN":REWARD_ABSTAIN}

def _reward(regime,seed,t,action):
    if action=="ABSTAIN":return REWARD_ABSTAIN
    assert action in ACTIONS
    probabilities=_world_probabilities(regime,seed,t)
    probability=probabilities[ACTIONS.index(action)]
    u=_hash_number(regime,seed,t,action,"outcome")/2**64
    correct=u<probability
    return (1.0 if correct else -2.0) - (
        PENALTY_VERIFY if action=="VERIFY" else 0)

def _normal(reward):
    return (reward+2.2)/3.2

def _argmax(values):
    return max(ACTIONS,key=lambda a:(values[a],-ACTIONS.index(a)))

def _ucb_from_history(history,t,window,prior=None):
    relevant=history if window is None else history[-window:]
    counts=Counter(a for _,a,_ in relevant)
    # All new strategies, including Omega, have the same cold-start rule.
    for a in ACTIONS:
        if counts[a]==0:return a
    total=max(2,len(relevant)+1)
    scores={}
    for a in ACTIONS:
        rows=[r for _,name,r in relevant if name==a]
        n=float(len(rows))
        sum_rewards=sum(_normal(r) for r in rows)
        if prior and a in prior:
            # An archived mean contributes half an observation, *after*
            # the action has been explored in the CURRENT environment.
            sum_rewards+=0.5*prior[a]
            n+=0.5
        scores[a]=sum_rewards/n + BONUS*math.sqrt(math.log(t+2)/n)
    return _argmax(scores)

class Policy:
    def __init__(self,name):
        if name not in POLICIES:raise ValueError("unknown policy")
        self.name=name
        self.history=[]
        self.all_observed=[]
        self.alarms=0
        self.rollbacks=0
        self.mode_switches=0
        self.mode="stable"
        self.last_alarm=-1000
        self.fast_left=0
        self.fast_rewards=[]
        self.pre_fast_average=0.0
        self.snapshot=[]
        self.memory=[]
        self.last_event=None
        self.plan_version=None
        if name.startswith("omega_"):
            plan=plan_mission({
                "question":(
                    "Comment réviser le choix entre répondre, vérifier "
                    "ou s'abstenir lorsque les retours observés changent ?"),
                "mission_type":"general",
                "decision_context":{
                    "blocking_uncertainty":"Fiabilité des retours encore inconnue",
                    "verification":"Observer l'issue de la décision choisie",
                    "verification_effect":"Réviser la politique si les retours la contredisent",
                },
            })
            if plan["next_action"]["action"]!="verify":
                raise AssertionError("P1 did not plan verification")
            self.plan_version=plan["planner_version"]

    def choose(self,t):
        if self.name=="fixed_direct":return "DIRECT"
        if self.name=="fixed_verify":return "VERIFY"
        if self.name=="fixed_abstain":return "ABSTAIN"
        if self.name=="ucb_stationary":
            return _ucb_from_history(self.history,t,None)
        if self.name=="sw_ucb":
            return _ucb_from_history(self.history,t,36)
        if self.name=="discount_ucb":
            # Simplified discount-UCB with the same reward normalization.
            effective={}
            total=0.0
            for a in ACTIONS:
                weighted=[(.97**(t-1-s),r) for s,k,r in self.history if k==a]
                n=sum(w for w,_ in weighted)
                mean=sum(w*_normal(r) for w,r in weighted)/n if n else 0.0
                effective[a]=(n,mean)
                total+=n
            for a in ACTIONS:
                if effective[a][0]<0.6:return a
            return _argmax({a:effective[a][1]+
                  BONUS*math.sqrt(math.log(t+2)/effective[a][0]) for a in ACTIONS})
        if self.name=="restart_ucb":
            return _ucb_from_history(self.history,t,48)
        if self.name.startswith("omega_"):
            prior=self._memory_prior() if self.name!="omega_no_memory" else None
            return _ucb_from_history(self.history,t,
                  12 if self.mode=="fast" else 48,prior=prior)
        raise AssertionError("unhandled policy")

    def _memory_prior(self):
        if self.mode!="fast" or not self.memory:return None
        previous=self.memory[-1]
        priors={}
        for a in ACTIONS:
            rows=[_normal(r) for _,k,r in previous if k==a]
            if rows:priors[a]=sum(rows)/len(rows)
        return priors

    def _alarm_detected(self,t):
        if t-self.last_alarm<12:return False
        # Two blocks of *observed feedback* on the same selected action,
        # never a peek into unchosen counterfactual outcomes.
        for a in ACTIONS[:2]:
            rows=[r for _,k,r in self.history if k==a]
            if len(rows)>=12:
                old=sum(rows[-12:-6])/6
                recent=sum(rows[-6:])/6
                if abs(old-recent)>0.8:return True
        return False

    def observe(self,t,action,reward):
        if action not in ACTIONS or type(t) is not int:
            raise ValueError("invalid observed result")
        if not isinstance(reward,(int,float)) or not math.isfinite(reward):
            raise ValueError("invalid measured reward")
        record=(t,action,float(reward))
        self.history.append(record)
        self.all_observed.append(record)
        self.last_event=None
        if self.name=="restart_ucb":
            if self._alarm_detected(t):
                self.alarms+=1
                self.last_alarm=t
                self.history=[]
                self.last_event="reset_after_alarm"
            return
        if not self.name.startswith("omega_"):return
        if self.mode=="fast":
            self.fast_rewards.append(reward)
            self.fast_left-=1
            if self.fast_left==0:
                avg=sum(self.fast_rewards)/len(self.fast_rewards)
                allow_rollback=self.name!="omega_no_rollback"
                if allow_rollback and avg<self.pre_fast_average-0.25:
                    # Deliberately conservative checkpoint recovery,
                    # may be counterproductive under a real concept shift.
                    self.history=list(self.snapshot)
                    self.rollbacks+=1
                    self.last_event="rollback_to_prechange_checkpoint"
                else:
                    self.last_event="keep_new_strategy"
                self.mode="stable"
                self.mode_switches+=1
            return
        if self._alarm_detected(t):
            self.alarms+=1
            self.last_alarm=t
            self.snapshot=list(self.history[-48:])
            self.memory.append(list(self.snapshot))
            self.memory=self.memory[-3:]
            self.pre_fast_average=sum(x[2] for x in self.history[-18:])/(
                len(self.history[-18:]) or 1)
            self.history=[]
            self.mode="fast"
            self.fast_left=18
            self.fast_rewards=[]
            self.mode_switches+=1
            self.last_event="change_alarm_start_fast"

def evaluate(regime,seed,policy_name,keep_trace=False):
    policy=Policy(policy_name)
    trace=[]
    total=0.0
    expected=0.0
    oracle=0.0
    mistakes=0
    checks=0
    abstentions=0
    switches=0
    previous=None
    digest=sha256()
    for t in range(HORIZON):
        action=policy.choose(t)
        if action not in ACTIONS:raise AssertionError("invalid action")
        gain=_reward(regime,seed,t,action)
        means=_expected_rewards(regime,seed,t)
        total+=gain
        expected+=means[action]
        oracle+=max(means.values())
        if action=="VERIFY":checks+=1
        if action=="ABSTAIN":abstentions+=1
        if gain<=-2.0:mistakes+=1
        if previous is not None and previous!=action:switches+=1
        previous=action
        policy.observe(t,action,gain)
        public_event={
            "t":t,"action":action,"reward":round(gain,4),
            "mode":policy.mode,"event":policy.last_event,
        }
        # Hash only the action's observed feedback, NEVER the hidden state.
        digest.update(json.dumps(public_event,sort_keys=True,
                                 separators=(",",":")).encode("utf-8")+b"\n")
        if keep_trace:trace.append(public_event)
    pseudo_regret=max(0.0,oracle-expected)
    return {
        "policy":policy_name,
        "seed":seed,"regime":regime, # evaluator metadata, not controller input
        "realized_utility":round(total,6),
        "expected_utility":round(expected,6),
        "dynamic_oracle_expected_utility":round(oracle,6),
        "pseudo_regret":round(pseudo_regret,6),
        "mistakes":mistakes,"verifications":checks,
        "verification_cost":round(PENALTY_VERIFY*checks,6),
        "abstentions":abstentions,"action_switches":switches,
        "alarms":policy.alarms,"rollbacks":policy.rollbacks,
        "mode_switches":policy.mode_switches,
        "planner_version":policy.plan_version,
        "observed_trace_sha256":digest.hexdigest(),
        **({"trace_observed_only":trace} if keep_trace else {}),
    }

def run():
    all_results=[]
    for regime in REGIMES:
        for seed in range(EPISODES):
            for name in POLICIES:
                all_results.append(evaluate(
                    regime,seed,name,keep_trace=seed==0 and
                    name in ("sw_ucb","restart_ucb","omega_candidate")
                ))
    aggregate={}
    by_key={(x["regime"],x["seed"],x["policy"]):x for x in all_results}
    for regime in REGIMES:
        sums={}
        for name in POLICIES:
            subset=[by_key[regime,s,name] for s in range(EPISODES)]
            sums[name]={
                "episodes":len(subset),
                "mean_pseudo_regret":round(sum(
                    x["pseudo_regret"] for x in subset)/EPISODES,6),
                "mean_realized_utility":round(sum(
                    x["realized_utility"] for x in subset)/EPISODES,6),
                "total_mistakes":sum(x["mistakes"] for x in subset),
                "total_verifications":sum(x["verifications"] for x in subset),
                "total_abstentions":sum(x["abstentions"] for x in subset),
                "total_alarms":sum(x["alarms"] for x in subset),
                "total_rollbacks":sum(x["rollbacks"] for x in subset),
                "total_mode_switches":sum(x["mode_switches"] for x in subset),
            }
        # Choose a strong comparator after results ONLY for transparent,
        # conservative descriptive comparison; not a deployable oracle.
        best=min(BASELINES,key=lambda n:sums[n]["mean_pseudo_regret"])
        comparison={"wins":0,"ties":0,"losses":0}
        deltas=[]
        for seed in range(EPISODES):
            ours=by_key[regime,seed,"omega_candidate"]["pseudo_regret"]
            theirs=by_key[regime,seed,best]["pseudo_regret"]
            deltas.append(round(ours-theirs,6))
            key="wins" if ours<theirs-1e-8 else (
                "losses" if ours>theirs+1e-8 else "ties")
            comparison[key]+=1
        aggregate[regime]={
            "policy_summary":sums,
            "best_classical_posthoc":best,
            "omega_minus_best_classical_mean_regret":round(
                sum(deltas)/EPISODES,6),
            "paired_outcomes_omega_vs_best":comparison,
            "paired_regret_differences":deltas,
        }
    result={
        "protocol":EXPERIMENT,"status":STATUS,
        "synthetic_author_designed":True,
        "model_generations":0,"paid_api_calls":0,
        "private_data_read":False,
        "episodes_per_regime":EPISODES,
        "horizon":HORIZON,"actions":ACTIONS,
        "regimes":REGIMES,
        "comparators":POLICIES,
        "world_version_sha256":sha256(json.dumps(
            {"profiles":PROFILES,"regimes":REGIMES,
             "horizon":HORIZON,"episodes":EPISODES},sort_keys=True
        ).encode("utf-8")).hexdigest(),
        "aggregate":aggregate,
        "individual_results":all_results,
        "limitations":[
            "Synthetic rewards not actual language-model correctness",
            "Controller sees only realized reward but oracle knows hidden expected values",
            "Author-designed simulation not independent or blinded",
            "Simplified UCB variants, not certified reference implementations",
            "P1 planner does not learn; Omega candidate is new experimental wrapper",
            "Ex post best baseline per regime is not deployable",
            "No measured real tool error rates or costs",
        ],
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    report=run()
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,ensure_ascii=False,
                       indent=2,sort_keys=True)+"\n",encoding="utf-8")
    concise={r:{
        "best_classical":v["best_classical_posthoc"],
        "omega_mean_regret":v["policy_summary"]["omega_candidate"]["mean_pseudo_regret"],
        "best_mean_regret":v["policy_summary"][v["best_classical_posthoc"]]["mean_pseudo_regret"],
        "omega_minus_best":v["omega_minus_best_classical_mean_regret"],
        "omega_alarms":v["policy_summary"]["omega_candidate"]["total_alarms"],
        "omega_rollbacks":v["policy_summary"]["omega_candidate"]["total_rollbacks"],
    } for r,v in report["aggregate"].items()}
    print("P5_ADAPT01_RESULT "+json.dumps({
        "status":STATUS,"episodes":len(REGIMES)*EPISODES,
        "model_generations":0,"summary":concise,
        "world_version_sha256":report["world_version_sha256"],
    },sort_keys=True))

if __name__=="__main__":main()
