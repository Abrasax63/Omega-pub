"""P5-FALSIFY-04: exact finite synthetic imperfect-verifier test.
This is a candidate policy, not the Omega P1/P2/P3 implementation.
Pre-registration: commit 4f1feef5372d61e27c1835fef8d3aaec8e8faea8.
"""
from __future__ import annotations
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
import json

STATES=tuple(product((0,1),repeat=2))
TOOLS=("A","B","C")
COST={"A":F(3,50),"B":F(3,50),"C":F(13,100)}
ACCURACY={"A":(F(9,10),F(11,20)),"B":(F(11,20),F(9,10)),"C":(F(4,5),F(4,5))}
ABSTAIN=F(1,20)
MAX_CALLS=2

def initial_belief(m,h):
    weights=tuple(F(1,4)*(F(2,3) if m==y else F(1,3))*
                  (F(3,4) if h==r else F(1,4)) for y,r in STATES)
    total=sum(weights)
    assert total==F(1,4)
    return tuple(w/total for w in weights)

def observation_probability(tool,z,y,r):
    accuracy=ACCURACY[tool][r]
    return accuracy if z==y else 1-accuracy

def observe(b,tool,z):
    weights=tuple(p*observation_probability(tool,z,*s) for p,s in zip(b,STATES))
    mass=sum(weights)
    assert mass>0
    return mass,tuple(w/mass for w in weights)

def terminal(b):
    p1=sum(p for p,(y,r) in zip(b,STATES) if y==1)
    choices={"predict_0":F(1)-F(3)*p1,"predict_1":F(3)*p1-F(2),"abstain":ABSTAIN}
    return max(choices.items(),key=lambda item:(item[1],
        {"abstain":3,"predict_0":2,"predict_1":1}[item[0]]))[::-1]

@lru_cache(None)
def optimal(b,unused=TOOLS,calls=MAX_CALLS):
    best=terminal(b)
    if calls>0:
        for t in unused:
            candidate=-COST[t]
            for z in (0,1):
                mass,post=observe(b,t,z)
                candidate+=mass*optimal(post,tuple(x for x in unused if x!=t),calls-1)[0]
            if candidate>best[0]:
                best=(candidate,t)
    return best

def heuristic_action(b,m,h,previous=None,observed=None):
    if previous is None:
        return "A" if h==0 else "B"
    if previous=="C":
        return terminal(b)[1]
    if observed!=m:
        return "C"
    return terminal(b)[1]

def policy_tree(policy,m,h):
    start=initial_belief(m,h)
    result={k:F(0) for k in ("utility","cost","calls","correct","wrong","abstain")}
    def visit(b,p,unused,calls,previous=None,signal=None,spent=F(0)):
        if policy=="bellman":
            action=optimal(b,unused,calls)[1]
        elif policy=="omega_like":
            action=heuristic_action(b,m,h,previous,signal)
        elif policy=="fixed_A_C":
            action="A" if previous is None else "C" if previous=="A" else terminal(b)[1]
        elif policy=="no_tool":
            action=terminal(b)[1]
        else:
            raise ValueError(policy)
        if action in TOOLS and calls>0 and action in unused:
            for z in (0,1):
                probability,post=observe(b,action,z)
                visit(post,p*probability,tuple(t for t in unused if t!=action),
                    calls-1,action,z,spent+COST[action])
            return
        if action in TOOLS:
            raise ValueError("inadmissible action")
        if action=="abstain":
            utility=ABSTAIN
            result["abstain"]+=p
        else:
            guess=int(action[-1])
            pcorrect=sum(q for q,(y,r) in zip(b,STATES) if y==guess)
            utility=F(3)*pcorrect-F(2)
            result["correct"]+=p*pcorrect
            result["wrong"]+=p*(1-pcorrect)
        result["utility"]+=p*(utility-spent)
        result["cost"]+=p*spent
        result["calls"]+=p*(len(TOOLS)-len(unused))
    visit(start,F(1),TOOLS,MAX_CALLS)
    assert sum(result[k] for k in ("correct","wrong","abstain"))==1
    return result

def main():
    means={p:{k:F(0) for k in ("utility","cost","calls","correct","wrong","abstain")}
           for p in ("no_tool","fixed_A_C","omega_like","bellman")}
    rows=[]
    for m,h in product((0,1),repeat=2):
        b=initial_belief(m,h)
        row={"context":{"m":m,"h":h},"bellman_first_action":optimal(b)[1]}
        for policy in means:
            detail=policy_tree(policy,m,h)
            row[policy]={k:float(v) for k,v in detail.items()}
            for key,value in detail.items():
                means[policy][key]+=value/F(4)
            if policy=="bellman":
                assert detail["utility"]==optimal(b)[0]
        rows.append(row)
    for name in means:
        assert means["bellman"]["utility"]>=means[name]["utility"]
    report={
        "protocol":"P5-FALSIFY-04",
        "pre_registration_commit":"4f1feef5372d61e27c1835fef8d3aaec8e8faea8",
        "status":"SYNTHETIC_EXACT_UTILITY_NO_OMEGA_UNIQUE_ADVANTAGE",
        "worlds":4,"hidden_states":4,"candidate_tools":3,"maximum_purchases":2,
        "models_executed":0,"api_cost_usd":0,
        "aggregate":{"policies":{name:{k:{"numerator":v.numerator,
            "denominator":v.denominator,"decimal":round(float(v),8)}
            for k,v in fields.items()} for name,fields in means.items()}},
        "conditional_results":rows,
        "limitations":[
            "Synthetic model probabilities, not empirical reliability measures",
            "Omega-like heuristic, not real P1/P2/P3",
            "Same information to all policies; classical Bellman exact is an upper bound",
            "No new model run; no scientifically independent test corpus"] }
    print(json.dumps(report,sort_keys=True,indent=2))
    return report

if __name__=="__main__":
    main()
