#!/usr/bin/env python3
"""Exhaustive metamorphic locality audit over all 861 unordered U42 pairs."""
import csv, json, sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research" / "data" / "v19_c5"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_metamorphic_v19_c5_l3 import shadow_dsu, CYCLE, L, trajectory_prefix

def canonical(shadow):
    def transform(mask, k):
        return sum(1 << ((i+k)%5) for i in range(5) if (mask >> i)&1)
    return min(tuple(sorted(transform(m,k) for m in shadow)) for k in range(5))

def parse_equations(s):
    eqs=[]
    for term in s.split(";"):
        lhs,rhs=term.strip().split("="); a,b=lhs.strip().split("+")
        eqs.append((int(a.strip()[1:]),int(b.strip()[1:]),int(rhs.strip())))
    return frozenset(m for m in range(32) if all((((m>>i)&1)^((m>>j)&1))==r for i,j,r in eqs))

def forced_edges(F):
    return [(u,v,1) for u,v in combinations(range(len(F)),2)
            if F[u]==F[v] or {F[u],F[v]}=={u,v}]

def event_edges(F,pair):
    a,b=pair; out=[]
    for _ in range(L):
        if a!=b: out.append((a,b,0))
        a,b=F[a],F[b]
    return out

def shadow_graph(F,pair,allowed=None):
    allowed=set(range(len(F))) if allowed is None else set(allowed)
    adj={u:[] for u in allowed}
    for u,v,d in forced_edges(F):
        if u in allowed and v in allowed: adj[u].append((v,d)); adj[v].append((u,d))
    for u,v,d in event_edges(F,pair):
        if u not in allowed or v not in allowed: raise AssertionError("prefix omitted event endpoint")
        adj[u].append((v,d)); adj[v].append((u,d))
    result=set()
    for mask in range(32):
        colors={i:(mask>>i)&1 for i in range(5)}; stack=list(CYCLE); ok=True
        while True:
            while stack and ok:
                u=stack.pop()
                for v,d in adj[u]:
                    want=colors[u]^d
                    if v in colors:
                        if colors[v]!=want: ok=False; break
                    else: colors[v]=want; stack.append(v)
            if not ok: break
            free=next((u for u in allowed if u not in colors),None)
            if free is None: break
            colors[free]=0; stack=[free]
        if ok: result.add(mask)
    return frozenset(result)

def main():
    source=json.loads((DATA/"V19_UNIVERSAL10_U42_2026-10-15.json").read_text())
    F=tuple(source["T"]); assert len(F)==42 and tuple(F[i] for i in CYCLE)==(1,2,3,4,0)
    rows=list(csv.DictReader((DATA/"V19_ORIENTED14_CLASSES_2026-10-15.csv").open()))
    class_ids={canonical(parse_equations(r["canonical_equations"])):r["c5_class_id"] for r in rows}
    assert len(class_ids)==14
    sizes=Counter(); classes=Counter(); proper=0
    for pair in combinations(range(42),2):
        visible=trajectory_prefix(F,pair,L,CYCLE)
        gd=shadow_dsu(F,pair,CYCLE,L); ld=shadow_dsu(F,pair,CYCLE,L,visible)
        gg=shadow_graph(F,pair); lg=shadow_graph(F,pair,visible)
        assert gd==ld,("DSU global/local",pair)
        assert gg==lg,("graph global/local",pair)
        assert gd==gg,("solver disagreement",pair)
        sizes[len(gd)]+=1
        if 0<len(gd)<32: proper+=1; classes[class_ids[canonical(gd)]]+=1
    expected={f"C5O-{i:02d}":source["oriented_class_counts"][f"C5O-{i:02d}"] for i in range(14)}
    assert sum(sizes.values())==861 and proper==680 and dict(classes)==expected
    assert sizes==Counter({16:500,8:140,4:40,32:40,0:141}) and min(classes.values())==10
    print("U42_PAIR_DOMAIN: PASS (861 unordered pairs)")
    print("GLOBAL_LOCAL_DSU: PASS (861/861)")
    print("GLOBAL_LOCAL_GRAPH: PASS (861/861)")
    print("DUAL_SOLVER: PASS (861/861)")
    print("SHADOW_SIZE_DISTRIBUTION: PASS "+json.dumps(dict(sorted(sizes.items()))))
    print("ORIENTED_CLASS_COVERAGE: PASS (14/14; 680 proper shadows)")
    print("CLASS_COUNTS: "+json.dumps(dict(sorted(classes.items())),sort_keys=True))
    print("METAMORPHIC_C5_L3_U42_ALL_PAIRS: ALL CHECKS PASSED")
    print("Scope: finite U42 witness only; no universal L+2 proof.")
if __name__=="__main__": main()
