"""CONG-001: revision of modular proofs with an independent finite ATMS.

All claims x ≡ r (mod m), m | 60. Inconsistency is explicitly reported,
not interpreted as entailing every proposition. One set of justifications is
derived using generalized CRT; another from finite solution sets on 0..59.
This is a constructed experiment, not the general Omega planner or a Lean proof.
"""
from collections import defaultdict
from itertools import combinations
from math import gcd
from pathlib import Path
import json

PATH=Path(__file__).with_name("congruence_revision_cases_v01.json")
U=60

def check(c):
    if type(c) is not dict or set(c)!={"r","m"}:
        raise ValueError("invalid congruence")
    r,m=c["r"],c["m"]
    if type(r) is not int or type(m) is not int or m<=0 or U%m or not 0<=r<m:
        raise ValueError("invalid residue or modulus")
    return r,m

def crt(items):
    """Generalized CRT; return canonical (a,lcm) or None if inconsistent."""
    a,L=0,1
    for c in items:
        b,m=check(c)
        g=gcd(L,m)
        if (b-a)%g:return None
        n=m//g
        t=0 if n==1 else (((b-a)//g)*pow(L//g,-1,n))%n
        a=(a+L*t)%(L*n)
        L*=n
    return a,L

def symbolic_kind(items,q):
    result=crt(items)
    if result is None:return "inconsistent_environment"
    a,L=result
    r,m=check(q)
    if (a-r)%gcd(L,m):return "refuted"
    if L%m==0 and a%m==r:return "entailed"
    return "undetermined"

def models(items):
    return frozenset(x for x in range(U)
                     if all(x%c["m"]==c["r"] for c in items))

def finite_kind(items,q):
    feasible=models(items)
    if not feasible:return "inconsistent_environment"
    r,m=check(q)
    if all(x%m==r for x in feasible):return "entailed"
    if all(x%m!=r for x in feasible):return "refuted"
    return "undetermined"

def _supports(premises,query,kind,method):
    selected=[]
    for size in range(1,min(3,len(premises))+1):
        for sub in combinations(sorted(premises),size):
            if any(set(earlier).issubset(sub) for earlier in selected):continue
            rows=[premises[a] for a in sub]
            result=(symbolic_kind(rows,query) if method=="symbolic"
                    else finite_kind(rows,query))
            if result==kind:selected.append(sub)
    return tuple(selected)

def _conflicts(premises,active,method):
    return tuple((a,b) for a,b in combinations(sorted(active),2)
                 if (symbolic_kind([premises[a],premises[b]],{"r":0,"m":1})
                     if method=="symbolic" else
                     finite_kind([premises[a],premises[b]],{"r":0,"m":1}))
                    =="inconsistent_environment")

class ProofLabels:
    def __init__(self,premises,queries,method):
        if method not in ("symbolic","finite"):raise ValueError("bad method")
        self.premises=premises; self.queries=queries; self.method=method
        for v in list(premises.values())+list(queries.values()):check(v)
        self.labels={q:{kind:_supports(premises,claim,kind,method)
                        for kind in ("entailed","refuted")}
                     for q,claim in sorted(queries.items())}
        self.history=[]

    def evaluate(self,version,active):
        if set(active)-set(self.premises):raise ValueError("unknown premise")
        conflicts=_conflicts(self.premises,active,self.method)
        result={}
        for q in sorted(self.queries):
            if conflicts:
                result[q]={"status":"inconsistent_environment",
                           "proofs":[],"conflicts":[list(x) for x in conflicts]}
                continue
            p={kind:[list(s) for s in self.labels[q][kind]
                     if set(s).issubset(active)] for kind in ("entailed","refuted")}
            if p["entailed"] and p["refuted"]:
                raise AssertionError("both proofs in consistent environment")
            status=("entailed" if p["entailed"] else "refuted"
                    if p["refuted"] else "undetermined")
            result[q]={"status":status,"proofs":p.get(status,[]),"conflicts":[]}
        self.history.append({"version":version,"active":sorted(active),
                             "results":result})
        return result

def independently_verify_proof(premises,query,active,kind,support):
    """Auditor never calls CRT or examines model-derived predictions."""
    if kind not in ("entailed","refuted") or not support:return False
    if len(support)!=len(set(support)) or not set(support).issubset(active):
        return False
    if set(active)-set(premises):return False
    if not models([premises[k] for k in active]):return False
    return finite_kind([premises[k] for k in support],query)==kind

def validate_scenario(s):
    if set(s)!={"id","split","premises","queries","initial","events"}:
        raise ValueError("bad schema")
    if s["split"] not in ("calibration","test"):raise ValueError("bad split")
    for c in list(s["premises"].values())+list(s["queries"].values()):check(c)
    active=set(s["initial"])
    if active-set(s["premises"]):raise ValueError("invalid initial")
    for event in s["events"]:
        if set(event)!={"op","id"} or event["id"] not in s["premises"]:
            raise ValueError("bad event")
        if event["op"]=="activate" and event["id"] not in active:
            active.add(event["id"])
        elif event["op"]=="retract" and event["id"] in active:
            active.remove(event["id"])
        else:raise ValueError("invalid transition")

def replay(data=None):
    if data is None:data=json.loads(PATH.read_text(encoding="utf-8"))
    if data["universe"]["modulus"]!=60:raise ValueError("wrong universe")
    summary=defaultdict(lambda:defaultdict(int))
    timeline=[]; histories=[]
    for s in data["scenarios"]:
        validate_scenario(s)
        indexed=ProofLabels(s["premises"],s["queries"],"finite")
        omega=ProofLabels(s["premises"],s["queries"],"symbolic")
        for q in s["queries"]:
            if indexed.labels[q]!=omega.labels[q]:
                raise AssertionError(("precomputed supports differ",s["id"],q))
            for kind in ("entailed","refuted"):
                for support in omega.labels[q][kind]:
                    if finite_kind([s["premises"][a] for a in support],
                                   s["queries"][q])!=kind:
                        raise AssertionError("invalid symbolic CRT certificate")
        active=set(s["initial"])
        for step,event in enumerate([None]+s["events"]):
            if event:
                if event["op"]=="activate":active.add(event["id"])
                else:active.remove(event["id"])
            atms=indexed.evaluate(step,active)
            outputs=omega.evaluate(step,active)
            actual={q:finite_kind([s["premises"][a] for a in sorted(active)],claim)
                    for q,claim in s["queries"].items()}
            if outputs!=atms:
                raise AssertionError(("symbolic/finite policy disagreement",s["id"],step))
            for q,truth in actual.items():
                got=outputs[q]
                if got["status"]!=truth:raise AssertionError(("wrong verdict",s["id"],step,q))
                for support in got["proofs"]:
                    if not independently_verify_proof(s["premises"],s["queries"][q],
                                                     active,truth,support):
                        raise AssertionError("forged, stale or explosive certificate")
                summary[s["split"]][truth]+=1
                summary[s["split"]]["judgments"]+=1
                summary[s["split"]]["active_certificate_paths"]+=len(got["proofs"])
                summary[s["split"]]["queries_with_certificate"]+=bool(got["proofs"])
                summary[s["split"]]["queries_with_two_or_more_paths"]+=(len(got["proofs"])>=2)
            if not models([s["premises"][a] for a in active]):
                if len(active)>1 and not _conflicts(s["premises"],active,"symbolic"):
                    raise AssertionError("missing minimal conflicting pair")
            timeline.append({"scenario":s["id"],"split":s["split"],
                             "revision":step,"event":event,
                             "active_premises":sorted(active),"truth":actual,
                             "omega":outputs,"baseline":atms})
        histories.append({"scenario":s["id"],"split":s["split"],
                          "archive":omega.history})
    return {"status":"PUBLIC_CONSTRUCTED_MODULAR_PROOF_MAINTENANCE",
            "data_commit":"7d6185185f3deddef95553d7af1dead31ef3c88b",
            "scenario_count":len(data["scenarios"]),"states":len(timeline),
            "summaries":{k:dict(v) for k,v in summary.items()},
            "results":timeline,"certificates_archive":histories,
            "ATMS_symbolic_omega_paired_identical":True,
            "independent_60_residue_oracle_validated":True,
            "model_calls":0,"generalization_demonstrated":False}

if __name__=="__main__":
    result=replay()
    print("OMEGA_CONGRUENCE_REVISION "+json.dumps(
        {k:v for k,v in result.items() if k not in ("results","certificates_archive")},
        sort_keys=True,ensure_ascii=False))
