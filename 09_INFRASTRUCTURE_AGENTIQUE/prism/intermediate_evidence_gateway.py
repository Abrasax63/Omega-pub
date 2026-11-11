"""Executable observation gateway for STRAT-004 opaque evidence envelopes.

The policy sees only action receipts, NEVER payload/schema/outage data.
Routes are derived from the actual stored payload shape by a paid probe.
Every terminal certificate comes from a computation, not a label fixture.
"""
import json
from fractions import Fraction
from pathlib import Path
from strategic_methods_executable import _euler_dfs, _euler_theorem

ROOT=Path(__file__).parent
FROZEN=ROOT/"intermediate_evidence_cases_v01.json"
ACTIONS=("probe","formal","graph","fraction","source")
SPECIALISTS=("formal","graph","fraction","source")
ROUTE_TO_SPECIALIST={
    "route:algebra":"formal",
    "route:graph":"graph",
    "route:rates":"fraction",
    "route:http":"source",
}
RFC_RULE={301:True,302:True,307:False,308:False}
RFC_REF={
    301:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.2",
    302:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.3",
    307:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.8",
    308:"https://www.rfc-editor.org/rfc/rfc9110#section-15.4.9",
}

def cases():
    values=json.loads(FROZEN.read_text(encoding="utf-8"))
    rows=values["cases"]
    if len(rows)!=64 or len({x["id"] for x in rows})!=64:
        raise ValueError("corrupted frozen task list")
    return rows

def _route_from_payload(payload):
    if not isinstance(payload,dict) or len(payload)!=1:
        raise ValueError("unknown evidence schema")
    key=next(iter(payload))
    labels={"coefficients":"algebra","graph":"graph","rates":"rates",
            "http_status":"http"}
    if key not in labels:
        raise ValueError("unsupported schema")
    return "route:"+labels[key]

def _actual_truth(task):
    route=_route_from_payload(task["payload"])
    p=next(iter(task["payload"].values()))
    if route=="route:algebra":
        return p["a"]%p["m"]==0 and p["b"]%p["m"]==0
    if route=="route:graph":
        return _euler_dfs(p["edges"])
    if route=="route:rates":
        return Fraction(*p["a"])>Fraction(*p["b"])
    if route=="route:http":
        return RFC_RULE[p["status"]]
    raise AssertionError("unknown route")

def run_check(task,action):
    """Only simulator receives a task. An actual selector receives receipts."""
    if action not in ACTIONS:
        raise ValueError("unknown action")
    route=_route_from_payload(task["payload"])
    p=next(iter(task["payload"].values()))
    if action=="probe":
        return {"outcome":route,"certificate":None,
                "kind":"intermediate_nonterminal"}
    if ROUTE_TO_SPECIALIST[route]!=action:
        return {"outcome":"unknown:unsupported","certificate":None,
                "kind":"no_certificate"}
    if task["simulated_outage"]:
        return {"outcome":"unknown:outage","certificate":None,
                "kind":"synthetic_outage"}
    if action=="formal":
        decision=p["a"]%p["m"]==0 and p["b"]%p["m"]==0
        witness=(0 if p["b"]%p["m"] else 1) if not decision else None
        certificate={"kind":"linear_congruence","a":p["a"],"b":p["b"],
                     "m":p["m"],"witness_k":witness}
    elif action=="graph":
        decision=_euler_theorem(p["edges"])
        degree=[sum(v in edge for edge in p["edges"])
                for v in range(p["n"])]
        certificate={"kind":"euler_degree_connectivity","n":p["n"],
                     "edge_count":len(p["edges"]),"degrees":degree}
    elif action=="fraction":
        a,b=p["a"],p["b"]
        decision=a[0]*b[1]>b[0]*a[1]
        certificate={"kind":"ratio_cross_product","left":a[0]*b[1],
                     "right":b[0]*a[1]}
    elif action=="source":
        decision=RFC_RULE[p["status"]]
        certificate={"kind":"normative_rfc9110","status":p["status"],
                     "source_url":RFC_REF[p["status"]],"scope":"POST -> GET"}
    else:raise AssertionError(action)
    return {"outcome":"yes" if decision else "no",
            "certificate":certificate,"kind":"certified"}

def independent_verify(task,receipt):
    """Second computation of truth and elementary certificate provenance."""
    outcome=receipt["outcome"]
    if outcome.startswith("route:"):
        return (outcome == _route_from_payload(task["payload"]) and
                receipt["certificate"] is None)
    if outcome not in ("yes","no"):
        return (outcome in ("unknown:unsupported","unknown:outage") and
                receipt["certificate"] is None)
    c=receipt["certificate"]
    if not isinstance(c,dict):
        return False
    actual=_actual_truth(task)
    if (outcome=="yes")!=actual:return False
    route=_route_from_payload(task["payload"])
    p=next(iter(task["payload"].values()))
    if route=="route:algebra":
        if c.get("kind")!="linear_congruence":return False
        if (c.get("a"),c.get("b"),c.get("m")) != (p["a"],p["b"],p["m"]):
            return False
        if not actual:
            k=c.get("witness_k")
            return type(k) is int and (p["a"]*k+p["b"])%p["m"]!=0
        return p["b"]%p["m"]==0 and (p["a"]+p["b"])%p["m"]==0
    if route=="route:graph":
        if c.get("kind")!="euler_degree_connectivity":return False
        degrees=[sum(v in e for e in p["edges"]) for v in range(p["n"])]
        return (c.get("degrees")==degrees and
                c.get("edge_count")==len(p["edges"]) and
                _euler_dfs(p["edges"])==_euler_theorem(p["edges"]))
    if route=="route:rates":
        return (c.get("kind")=="ratio_cross_product" and
                c.get("left")==p["a"][0]*p["b"][1] and
                c.get("right")==p["b"][0]*p["a"][1])
    if route=="route:http":
        return (c.get("kind")=="normative_rfc9110" and
                c.get("status")==p["status"] and
                c.get("source_url")==RFC_REF[p["status"]])
    return False

def frozen_audit():
    rows=cases()
    facts={"train":{"count":0,"yes":0,"no":0,"routes":{}},
           "test":{"count":0,"yes":0,"no":0,"routes":{}}}
    for t in rows:
        partition=t["partition"]
        if partition not in facts:raise AssertionError("unknown split")
        route=run_check(t,"probe")["outcome"]
        f=facts[partition]
        f["count"]+=1
        f["yes" if _actual_truth(t) else "no"]+=1
        g=f["routes"].setdefault(route,{"yes":0,"no":0,"outages":0})
        g["yes" if _actual_truth(t) else "no"]+=1
        if t["simulated_outage"]:g["outages"]+=1
        for a in ACTIONS:
            if not independent_verify(t,run_check(t,a)):
                raise AssertionError((t["id"],a,"invalid certificate"))
    for partition in facts:
        f=facts[partition]
        if (f["count"],f["yes"],f["no"])!=(32,16,16):
            raise AssertionError("imbalanced truth")
        if len(f["routes"])!=4:raise AssertionError("missing route")
        if any((x["yes"],x["no"],x["outages"])!=(4,4,1)
               for x in f["routes"].values()):
            raise AssertionError("conditional route leaks final decision")
    return facts
