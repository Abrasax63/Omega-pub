from collections import deque, defaultdict
from itertools import combinations
import json, hashlib
from pathlib import Path

OUT=Path('/mnt/data/ravi13_discovery2/MEALY_HELLY_RESULTS_2026-10-16.json')

def build_C(q,k):
    assert q>=3 and 2<=k<=q-1
    states=[]
    for i in range(k):
        states += [(i,0),(i,1)]
    sink=('s',)
    states.append(sink)
    inputs=['a']+[f't{j}' for j in range(k)]
    def step(s,a):
        if s==sink:
            return k,sink
        i,b=s
        if a=='a':
            return i,s
        j=int(a[1:])
        if i==j:
            return 0,sink
        return b,sink
    return states,inputs,step

def child(K,a,step):
    by=defaultdict(set)
    for init,cur in K:
        y,nxt=step(cur,a)
        by[y].add((init,nxt))
    return dict(by)

def canon_blocks(blocks):
    # blocks: iterable of frozensets((init,current)); block identity irrelevant but preserved by membership
    return tuple(sorted((tuple(sorted(b,key=repr)) for b in blocks), key=repr))

def advance_blocks(blocks,a,step):
    new=[]
    for b in blocks:
        parts=defaultdict(set)
        for init,cur in b:
            y,nxt=step(cur,a)
            parts[y].add((init,nxt))
        new.extend(frozenset(v) for v in parts.values())
    return tuple(new)

def all_singletons(blocks):
    return all(len(b)<=1 for b in blocks)

def has_common_resolver(branches, inputs, step):
    # branches is list of K sets; same future input word must resolve each branch internally
    blocks=tuple(frozenset(b) for b in branches if len(b)>1)
    if not blocks: return True
    start=canon_blocks(blocks)
    dq=deque([blocks]); seen={start}
    while dq:
        cur=dq.popleft()
        for a in inputs:
            nxt=advance_blocks(cur,a,step)
            if all_singletons(nxt): return True
            key=canon_blocks(nxt)
            if key not in seen:
                seen.add(key); dq.append(nxt)
    return False

def reachable_knowledge(states,inputs,step):
    K0=frozenset((s,s) for s in states)
    dq=deque([K0]); seen={K0}
    while dq:
        K=dq.popleft()
        for a in inputs:
            for C in child(K,a,step).values():
                F=frozenset(C)
                if F and F not in seen:
                    seen.add(F); dq.append(F)
    return seen

def minimal_nonfaces(branches,inputs,step):
    # only individually resolvable branches are passed
    n=len(branches); mins=[]
    # cache compatibility masks
    compat={0:True}
    for r in range(1,n+1):
        for inds in combinations(range(n),r):
            mask=sum(1<<i for i in inds)
            ok=has_common_resolver([branches[i] for i in inds],inputs,step)
            compat[mask]=ok
            if not ok:
                minimal=True
                for i in inds:
                    if not compat.get(mask & ~(1<<i), False):
                        minimal=False; break
                if minimal: mins.append(tuple(inds))
    return mins

def run(qmax=8):
    cases=[]; total_K=0; total_nodes=0; max_core=0
    sharp=[]
    for q in range(3,qmax+1):
        for k in range(2,q):
            states,inputs,step=build_C(q,k)
            Ks=reachable_knowledge(states,inputs,step)
            total_K += len(Ks)
            violations=[]; local_max=0; root_core_sizes=[]
            K0=frozenset((s,s) for s in states)
            for K in Ks:
                for a in inputs:
                    ch=child(K,a,step)
                    labels=[]; branches=[]
                    for y,B in sorted(ch.items(),key=lambda x:x[0]):
                        if has_common_resolver([B],inputs,step):
                            labels.append(y); branches.append(frozenset(B))
                    if not branches: continue
                    mns=minimal_nonfaces(branches,inputs,step)
                    total_nodes += 1
                    for inds in mns:
                        sz=len(inds); local_max=max(local_max,sz); max_core=max(max_core,sz)
                        if sz>q-1:
                            violations.append({'K':repr(K),'input':a,'size':sz})
                        if K==K0 and a=='a':
                            root_core_sizes.append(sz)
            expected=k
            if expected not in root_core_sizes:
                raise AssertionError((q,k,'missing sharp root core',root_core_sizes))
            if violations:
                raise AssertionError((q,k,violations[:3]))
            cases.append({'q':q,'k':k,'states':len(states),'reachable_knowledge':len(Ks),'max_min_nonface':local_max,'root_core_sizes':sorted(root_core_sizes)})
            sharp.append(local_max==k if k==q-1 else True)
    # explicit q=2 C analogue not defined; theorem says any minimal nonface among individually resolvable branches must size<=1.
    out={
      'status':'PASS','date':'2026-10-16','q_range':[3,qmax],
      'cases':cases,'case_count':len(cases),'reachable_knowledge_total':total_K,
      'nerve_nodes_checked':total_nodes,'max_min_nonface_seen':max_core,
      'universal_claim_checked_by_proof':'minimal nonface essential branches are fertile; OBS-M27-FERTILE gives <=q-1',
      'sharpness':'C(q,q-1) has root minimal nonface q-1 for every tested q',
      'violations':0
    }
    OUT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2,ensure_ascii=False))
    print('sha256',hashlib.sha256(OUT.read_bytes()).hexdigest())

if __name__=='__main__': run()