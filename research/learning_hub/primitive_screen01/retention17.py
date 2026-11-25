"""RETENTION17: optimize balanced replay under exact token constraints.
Tokenizer-only. No model weights or second training block.
"""
import argparse,json,random
from pathlib import Path
from collections import Counter
import curriculum06 as c
import trainer07 as t
import retention16 as p

def need(ok,msg):
    if not ok:raise ValueError(msg)

def solve(old,new,enc,limit=30):
    import numpy as np
    from scipy.optimize import milp,Bounds,LinearConstraint
    c.validate(old,"train")
    go,gn=p.pairs(old),p.pairs(new)
    keys=list(gn);random.Random(p.SEED).shuffle(keys)
    shared,extra=keys[:32],keys[32:]
    olds=list(go);allkeys=olds+extra
    vv={k:p.vec(enc,g,k) for g in (go,gn) for k in g}
    ref=p.add(*(vv[k] for k in keys))
    # Binary variables: add old pair, or remove new pair.
    # One integer q, number of old pairs per skill (0..8).
    n=len(allkeys)+1
    A=[];lo=[];hi=[]
    def row(coeff,l,h):
        A.append(coeff);lo.append(l);hi.append(h)
    for k in c.KINDS:
        row([int(go[z][0]["kind"]==k) for z in olds]+[0]*len(extra)+[-1],0,0)
    row([0]*len(olds)+[1]*len(extra)+[-4],0,0)
    # Exact integer equivalents of candidate/reference within 2%:
    # ceil(100*ref/102) <= candidate <= floor(102*ref/100).
    for j,b in enumerate(ref):
        coeff=[vv[z][j] for z in olds]+[-vv[z][j] for z in extra]+[0]
        row(coeff,(100*b+101)//102-b,102*b//100-b)
    obj=[0]*(n-1)+[-1]
    result=milp(c=obj,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.array([1]*(n-1)+[8])),constraints=LinearConstraint(np.array(A),lo,hi),options={"time_limit":limit,"mip_rel_gap":0.0})
    need(result.x is not None,"NO_FEASIBLE_INCUMBENT")
    z=np.rint(result.x).astype(int)
    need(float(np.max(np.abs(z-result.x)))<1e-5,"NONINTEGER")
    q=int(z[-1]);added=[k for k,a in zip(olds,z[:len(olds)]) if a];removed={k for k,a in zip(extra,z[len(olds):-1]) if a}
    need(0<=q<=8 and len(added)==len(removed)==4*q,"COUNT")
    need(Counter(go[k][0]["kind"] for k in added)==Counter({k:q for k in c.KINDS}),"BALANCE")
    # Preserve second-half positions; replace only selected new pairs.
    random.Random(p.SEED+1).shuffle(added)
    it=iter(added);chosen=shared+[next(it) if k in removed else k for k in extra]
    cand=p.add(*(vv[k] for k in chosen))
    need(len(set(chosen))==64 and all(100*a<=102*b and 100*b<=102*a for a,b in zip(cand,ref)),"EXACT_BUDGET")
    g={**go,**gn}
    plans={k:[[r["id"] for r in g[z]] for z in zz] for k,zz in (("new_only",keys),("replay",chosen))}
    need(plans["new_only"][:32]==plans["replay"][:32],"PREFIX")
    return dict(status="TOKEN_BUDGET_OPTIMIZATION",solver_status=int(result.status),optimality_proved=result.status==0,solver_message=str(result.message),replay_pairs=4*q,replay_pairs_per_skill=q,replay_fraction=4*q/64,nontrivial=q>0,new_examples={"new_only":128,"replay":128-8*q},steps_per_arm=64,reference=dict(zip(p.FIELDS,ref)),candidate=dict(zip(p.FIELDS,cand)),relative_spread=dict(zip(p.FIELDS,p.spread(cand,ref))),plans=plans,training_authorized=False,scope="fixed prefix, fixed candidate pools; only solver-certified optimum within this design")
def selftest():
    old,new=p.datasets()
    enc={z["id"]:[dict(input_ids=[0]*40,target_tokens=4),dict(input_ids=[0]*40,target_tokens=4)] for z in old+new}
    a=solve(old,new,enc)
    need(a["optimality_proved"] and a["replay_pairs"]==32,"EQUAL_BUDGET")
    for z in old:
        for v in enc[z["id"]]:v["target_tokens"]=1
    b=solve(old,new,enc)
    need(b["optimality_proved"] and b["replay_pairs"]==0,"INFEASIBLE_POSITIVE_REPLAY")
    print("RETENTION17 exact budget controls passed")
def preflight(out):
    from transformers import AutoTokenizer
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    old,new=p.datasets();enc={**p.encode(tok,p.pairs(old)),**p.encode(tok,p.pairs(new))}
    d=solve(old,new,enc);d["revision"]=c.REV
    Path(out).write_text(json.dumps(d,indent=2))
    print(json.dumps({k:v for k,v in d.items() if k!="plans"},indent=2))
if __name__=="__main__":
    a=argparse.ArgumentParser();a.add_argument("cmd",choices=["selftest","preflight"]);a.add_argument("--out");args=a.parse_args()
    if args.cmd=="selftest":selftest()
    else:preflight(args.out)
