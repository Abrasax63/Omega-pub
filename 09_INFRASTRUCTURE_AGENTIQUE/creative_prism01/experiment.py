#!/usr/bin/env python3
"""Omega creative prism 01: audited representation changes on finite tasks.

The candidate transforms are a FIXED library of classical algorithms.
This is an executable test of representation switching, NOT a demonstration
of autonomous scientific creativity, novelty, or learning.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import random
import time
from pathlib import Path

SEED = 20261119
BUDGET = 500
ARMS = ("A_direct", "B_diversify", "C_change_representation", "D_strong_baseline")


class Unsupported(ValueError):
    pass


class BudgetExhausted(RuntimeError):
    pass


class Counter:
    def __init__(self, budget=BUDGET):
        self.budget=budget
        self.count=0
    def tick(self, n=1, cap=None):
        if self.count+n > (self.budget if cap is None else min(self.budget,cap)):
            raise BudgetExhausted()
        self.count+=n


def corpus(seed=SEED):
    """Recipe frozen in PREREG.md before code; no filtering on solver scores."""
    rng=random.Random(seed)
    output=[]
    for index in range(24):
        n=rng.randint(10,15)
        colors=[rng.randrange(2) for _ in range(n)]
        order=list(range(n))
        rng.shuffle(order)
        edges=[]
        used=set()
        for pos in range(1,n):
            u=order[pos]
            v=order[rng.randrange(pos)]
            key=tuple(sorted((u,v)))
            used.add(key)
            edges.append((u,v,colors[u]^colors[v]))
        extra=rng.randint(1,4)
        for k in range(extra):
            choices=[(u,v) for u in range(n) for v in range(u+1,n)
                     if (u,v) not in used]
            if not choices:
                raise AssertionError("CORPUS_CHORD_UNAVAILABLE")
            u,v=rng.choice(choices)
            used.add((u,v))
            bit=colors[u]^colors[v]
            if index%2==1 and k==0:
                bit^=1
            edges.append((u,v,bit))
        output.append({"id":f"G{index+1:02d}","kind":"xor",
                       "n":n,"edges":[list(e) for e in edges]})
    for index in range(24):
        n=rng.randint(9,15)
        order=list(range(n))
        rng.shuffle(order)
        transition=[0]*n
        for i,x in enumerate(order):
            transition[x]=order[(i+1)%n]
        colors=[rng.randrange(2) for _ in range(n)] if index%2==0 else [0]*n
        output.append({"id":f"O{index+1:02d}","kind":"observability",
                       "transition":transition,"pi":colors,"h":n})
    output.extend([
        {"id":"X01","kind":"xor","n":3,"edges":[[0,1,2]]},
        {"id":"X02","kind":"xor","n":3,"domain":3,"edges":[[0,1,1]]},
        {"id":"X03","kind":"observability","transition":[1,None],
         "pi":[0,1],"h":2},
        {"id":"X04","kind":"observability","transition":[1,0],
         "pi":[0,1],"h":-1},
    ])
    return output


def valid(task):
    if not isinstance(task,dict):
        raise Unsupported("NOT_A_TASK")
    if task.get("kind")=="xor":
        if set(task)!={"id","kind","n","edges"}:
            raise Unsupported("XOR_EXTRA_FIELDS_OR_MISSING_DOMAIN")
        n=task["n"]
        edges=task["edges"]
        if (type(n)!=int or not 2<=n<=20 or not isinstance(edges,list)
            or len(edges)>120):
            raise Unsupported("XOR_INVALID_SIZE")
        used=set()
        for edge in edges:
            if (not isinstance(edge,(list,tuple)) or len(edge)!=3 or
                any(type(x)!=int for x in edge)):
                raise Unsupported("XOR_EDGE_NOT_INTEGER")
            u,v,bit=edge
            if not(0<=u<n and 0<=v<n and u!=v and bit in (0,1)):
                raise Unsupported("XOR_EDGE_OUT_OF_SCOPE")
            key=tuple(sorted((u,v)))
            if key in used:
                raise Unsupported("XOR_DUPLICATE_EDGE")
            used.add(key)
        return
    if task.get("kind")=="observability":
        if set(task)!={"id","kind","transition","pi","h"}:
            raise Unsupported("OBS_EXTRA_FIELDS")
        t=task["transition"];pi=task["pi"];h=task["h"]
        if not isinstance(t,list) or not isinstance(pi,list):
            raise Unsupported("OBS_WRONG_ARRAY_TYPE")
        n=len(t)
        if (not 2<=n<=20 or len(pi)!=n or type(h)!=int or not 1<=h<=n
            or any(type(v)!=int or not 0<=v<n for v in t)
            or any(type(v)!=int or v not in (0,1) for v in pi)):
            raise Unsupported("OBS_INVALID_TOTAL_MAP_OR_HORIZON")
        return
    raise Unsupported("UNKNOWN_TASK_KIND")


def word(t,pi,h,x):
    out=[]
    for _ in range(h):
        out.append(pi[x])
        x=t[x]
    return tuple(out)


def exact_reference(task):
    """Unbounded independent ground truth, called ONLY after all arm outputs."""
    if task["kind"]=="xor":
        n=task["n"]
        for bits in range(1<<n):
            if all(((bits>>u)&1)^((bits>>v)&1)==b for u,v,b in task["edges"]):
                return True
        return False
    t=task["transition"];pi=task["pi"];h=task["h"]
    words=[word(t,pi,h,x) for x in range(len(t))]
    return len(set(words))==len(t)


def graph_bfs(task,c):
    n=task["n"]
    adj=[[] for _ in range(n)]
    for u,v,b in task["edges"]:
        c.tick()
        adj[u].append((v,b))
        adj[v].append((u,b))
    bits=[None]*n
    for root in range(n):
        c.tick()
        if bits[root] is not None:
            continue
        bits[root]=0
        queue=[root]
        for u in queue:
            for v,b in adj[u]:
                c.tick()
                if bits[v] is None:
                    bits[v]=bits[u]^b
                    queue.append(v)
                elif bits[v]!=(bits[u]^b):
                    return False, None
    return True,bits


def brute_graph(task,c,*,cap=BUDGET,reverse=False,complement=False):
    n=task["n"]
    tests=range((1<<n)-1,-1,-1) if reverse else range(1<<n)
    for mask in tests:
        if complement:
            mask^=(1<<n)-1
        ok=True
        for u,v,b in task["edges"]:
            c.tick(cap=cap)
            if (((mask>>u)&1)^((mask>>v)&1))!=b:
                ok=False
                break
        if ok:
            return True
    return False


def pair_scan(task,c,*,cap=BUDGET,reverse=False):
    t=task["transition"];pi=task["pi"];h=task["h"]
    n=len(t)
    pairs=[(x,y) for x in range(n) for y in range(x+1,n)]
    if reverse:
        pairs.reverse()
    for x,y in pairs:
        p,q=x,y
        same=True
        for _ in range(h):
            c.tick(cap=cap)
            if pi[p]!=pi[q]:
                same=False
                break
            p=t[p];q=t[q]
        if same:
            return False
    return True


def diversify(task,c):
    first=None
    try:
        if task["kind"]=="xor":
            first=brute_graph(task,c,cap=250)
        else:
            first=pair_scan(task,c,cap=250)
        return first
    except BudgetExhausted:
        pass
    # Second view is a reordering of the SAME search space; not an
    # independent mathematical perspective.
    try:
        if task["kind"]=="xor":
            return brute_graph(task,c,cap=500,reverse=True,complement=True)
        return pair_scan(task,c,cap=500,reverse=True)
    except BudgetExhausted:
        return None


def find_uf(x,parent,parity,c):
    c.tick()
    if parent[x]==x:
        return x,0
    root,p=find_uf(parent[x],parent,parity,c)
    parity[x]^=p
    parent[x]=root
    return root,parity[x]


def parity_transform(task,c):
    n=task["n"]
    parent=list(range(n));rank=[0]*n;parity=[0]*n
    for u,v,b in task["edges"]:
        c.tick()
        ru,pu=find_uf(u,parent,parity,c)
        rv,pv=find_uf(v,parent,parity,c)
        if ru==rv:
            if (pu^pv)!=b:
                return False,{"contradiction_edge":[u,v,b]}
        else:
            if rank[ru]<rank[rv]:
                ru,rv=rv,ru
                pu,pv=pv,pu
            parent[rv]=ru
            parity[rv]=pu^pv^b
            if rank[ru]==rank[rv]:
                rank[ru]+=1
    bits=[find_uf(x,parent,parity,c)[1] for x in range(n)]
    # Backtranslate to ORIGINAL edges; if inconsistent, fail closed.
    if not all((bits[u]^bits[v])==b for u,v,b in task["edges"]):
        raise AssertionError("PARITY_BACKTRANSLATION_FAILURE")
    return True,{"witness_bits":bits}


def partitions_transform(task,c):
    t=task["transition"];pi=task["pi"];h=task["h"]
    n=len(t)
    labels=list(pi)
    c.tick(n)
    counts=[len(set(labels))]
    for _ in range(2,h+1):
        signature_to_id={}
        next_labels=[]
        for x in range(n):
            c.tick()
            sig=(pi[x],labels[t[x]])
            if sig not in signature_to_id:
                signature_to_id[sig]=len(signature_to_id)
            next_labels.append(signature_to_id[sig])
        labels=next_labels
        counts.append(len(set(labels)))
    if any(b<a for a,b in zip(counts,counts[1:])):
        raise AssertionError("MONOTONIC_REFINEMENT_FAILURE")
    # Independent semantic check with actual output words, not labels.
    words=[word(t,pi,h,x) for x in range(n)]
    for x in range(n):
        for y in range(x+1,n):
            if (labels[x]==labels[y])!=(words[x]==words[y]):
                raise AssertionError("REFINEMENT_NOT_EQUIVALENT_TO_SOURCE")
    truth=len(set(labels))==n
    duplicate=next(([x,y] for x in range(n) for y in range(x+1,n)
                    if labels[x]==labels[y]),None)
    return truth,{"classes_each_horizon":counts,
                  "monotonicity":"KNOWN_INVARIANT",
                  "indistinguishable_pair":duplicate}


def strong_obs(task,c):
    t=task["transition"];pi=task["pi"];h=task["h"]
    words=[]
    for x in range(len(t)):
        s=[];at=x
        for _ in range(h):
            c.tick()
            s.append(pi[at])
            at=t[at]
        words.append(tuple(s))
    return len(set(words))==len(t)


def propose(task):
    """Select by task structure, not by manually supplied solver name."""
    if task["kind"]=="xor":
        return {"candidate":"graph_parity_union_find",
                "rejected_candidate":"erase_edge_parity",
                "invariant":"parity of each original edge"}
    return {"candidate":"temporal_equivalence_refinement",
            "rejected_candidate":"sort_temporal_symbols",
            "invariant":"same length-h output word equivalence"}


def run_arm(task,name):
    c=Counter()
    start=time.perf_counter()
    chosen=None
    try:
        if name=="A_direct":
            value=brute_graph(task,c) if task["kind"]=="xor" else pair_scan(task,c)
        elif name=="B_diversify":
            value=diversify(task,c)
        elif name=="C_change_representation":
            if task["kind"]=="xor":
                value,chosen=parity_transform(task,c)
            else:
                value,chosen=partitions_transform(task,c)
        elif name=="D_strong_baseline":
            if task["kind"]=="xor":
                value,chosen=graph_bfs(task,c)
            else:
                value=strong_obs(task,c)
        else:
            raise ValueError("UNKNOWN_ARM")
    except BudgetExhausted:
        value=None
    duration=round((time.perf_counter()-start)*1000,5)
    return {"status":("ABSTAIN_BUDGET" if value is None else
                      "VERIFIED_TRUE" if value else "VERIFIED_FALSE"),
            "claim":value,"operations":c.count,"budget":BUDGET,
            "elapsed_ms":duration,"certificate":chosen}


def test_wrong_representation_controls():
    bad_graph={"kind":"xor","n":3,
               "edges":[[0,1,1],[1,2,1],[0,2,1]]}
    truth=exact_reference(bad_graph)
    erased={"kind":"xor","n":3,
            "edges":[[u,v,0] for u,v,_ in bad_graph["edges"]]}
    wrong=exact_reference(erased)
    bad_obs={"kind":"observability","transition":[1,0],"pi":[0,1],"h":2}
    actual=exact_reference(bad_obs)
    wrong_uniq=len({tuple(sorted(word(bad_obs["transition"],bad_obs["pi"],2,x)))
                   for x in range(2)})==2
    result=[
      {"name":"erase_edge_parity","original_truth":truth,
       "wrong_transform_truth":wrong,"falsified":truth!=wrong,
       "witness":bad_graph},
      {"name":"sort_temporal_symbols","original_truth":actual,
       "wrong_transform_truth":wrong_uniq,"falsified":actual!=wrong_uniq,
       "witness":bad_obs},
    ]
    if any(not row["falsified"] for row in result):
        raise AssertionError("WRONG_TRANSFORM_WITNESS_FAILED")
    return result


def experiment():
    tasks=corpus()
    rows=[]
    for task in tasks:
        try:
            valid(task)
        except Unsupported as error:
            rows.append({"task_id":task["id"],"task":task,
                         "status":"ABSTAIN_UNSUPPORTED","reason":str(error),
                         "arms":None,"ground_truth":None})
            continue
        # All four arms are evaluated before the unbounded ground truth.
        arms={name:run_arm(task,name) for name in ARMS}
        truth=exact_reference(task)
        for name,row in arms.items():
            if row["claim"] is not None and row["claim"]!=truth:
                raise AssertionError(f"SILENT_ERROR_{task['id']}_{name}")
        rows.append({"task_id":task["id"],"task":task,"status":"EVALUATED",
                     "representation_proposals":propose(task),
                     "ground_truth":truth,"arms":arms})
    positive=[r for r in rows if r["status"]=="EVALUATED"]
    invalid=[r for r in rows if r["status"]=="ABSTAIN_UNSUPPORTED"]
    stats={}
    for name in ARMS:
        stats[name]={
            "solved":sum(r["arms"][name]["claim"] is not None for r in positive),
            "abstained_budget":sum(r["arms"][name]["claim"] is None for r in positive),
            "correct":sum(r["arms"][name]["claim"]==r["ground_truth"]
                          for r in positive if r["arms"][name]["claim"] is not None),
            "false_verdicts":0,
            "operations_total":sum(r["arms"][name]["operations"] for r in positive),
            "elapsed_ms_total":round(sum(r["arms"][name]["elapsed_ms"] for r in positive),5),
            "by_domain":{
                domain:sum(r["arms"][name]["claim"] is not None
                           for r in positive if r["task"]["kind"]==domain)
                for domain in ("xor","observability")
            },
        }
    wrong=test_wrong_representation_controls()
    stable=[{"id":r["task_id"],"task":r["task"],
             "truth":r["ground_truth"],"status":r["status"],
             "arms":({name:{"status":v["status"],"claim":v["claim"],
                            "operations":v["operations"],
                            "certificate":v["certificate"]}
                      for name,v in r["arms"].items()}
                     if r["arms"] else None)}
            for r in rows]
    digest=hashlib.sha256(json.dumps(stable,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    c=stats["C_change_representation"]["solved"]
    return {
      "experiment":"OMEGA_CREATIVE_PRISM01_STRUCTURAL_REPRESENTATION",
      "seed":SEED,"instrumented_budget_per_arm":BUDGET,
      "operations_interchangeable_as_cpu_cost":False,
      "candidate_source":"FIXED_LIBRARY_OF_CLASSICAL_TRANSFORMATIONS",
      "autonomous_creativity_proven":False,
      "novel_mathematical_theorems":0,
      "formal_proof_lean":False,
      "model_weight_updates":0,
      "new_knowledge_promoted":0,
      "corpus_count":len(tasks),"valid_cases":len(positive),
      "rejected_out_of_scope":len(invalid),
      "falsified_bad_transformations":len(wrong),
      "silent_errors":0,"wrong_transform_counterexamples":wrong,
      "metrics":stats,
      "representation_minus_direct":c-stats["A_direct"]["solved"],
      "representation_minus_diversification":c-stats["B_diversify"]["solved"],
      "representation_minus_strong_baseline":c-stats["D_strong_baseline"]["solved"],
      "decisions_sha256_excluding_wall_clock":digest,
      "cases":rows
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args()
    report=experiment()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("CREATIVE_PRISM01",json.dumps({
        "cases":report["corpus_count"],"valid":report["valid_cases"],
        "invalid_rejected":report["rejected_out_of_scope"],
        "wrong_representation_counterexamples":report["falsified_bad_transformations"],
        "metrics":report["metrics"],"vs_strong":report["representation_minus_strong_baseline"],
        "decisions_sha":report["decisions_sha256_excluding_wall_clock"]
    },ensure_ascii=False),flush=True)

if __name__=="__main__":
    main()
