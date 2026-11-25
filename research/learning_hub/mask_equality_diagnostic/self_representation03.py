"""Reuse SELF-REP01 runner with new disjoint corpus and frozen SELF-REP02 prompt."""
import argparse,inspect
import self_representation as prior
from self_representation02 import prompt as successful_prompt
from position_representation import dump,sha
# Preserve original runner, parse, scoring and cost accounting.
old_corpus=prior.corpus
# Reconstruct function from trusted repository source only; no model output executed.
# Instead of dynamic execution, use explicit corpus implementation.
import random
from collections import Counter
def corpus():
    rng=random.Random(202611250550);alpha=list("ABCDEFGH");rows=[];seen=set()
    excluded={tuple(r["seq"]) for r in old_corpus()}
    for n in (5,7):
        a=rng.sample(alpha,8);b=rng.sample(alpha,8)
        while any(x==y for x,y in zip(a,b)):b=rng.sample(alpha,8)
        pp=list(range(n))*(16//n)+rng.sample(range(n),16%n);rng.shuffle(pp)
        while any(pp[i]==pp[i+8] for i in range(8)):rng.shuffle(pp)
        for i,(x,y) in enumerate(zip(a,b)):
            p,q=pp[i],pp[i+8]
            for attempt in range(1000):
                s=rng.sample([z for z in alpha if z not in (x,y)],n-2)
                s.insert(min(p,q),x if p<q else y);s.insert(max(p,q),y if p<q else x)
                if tuple(s) not in seen|excluded:break
            else:raise RuntimeError("duplicate list")
            seen.add(tuple(s));assert s[p]==x and s[q]==y
            for pos,gold in ((p,x),(q,y)):
                assert s[pos]==gold==dict(enumerate(s,1))[pos+1]
                rows.append(dict(id=sha(dump([s,pos]))[:24],pair=f"{n}-{i}",n=n,seq=s,p=pos+1,gold=gold))
        assert Counter(r["gold"] for r in rows if r["n"]==n)==Counter(alpha*2)
    assert len(rows)==32 and len(seen)==16 and not seen&excluded and len({r["id"] for r in rows})==32
    rng.shuffle(rows);return rows
def reconstruction(seq):return successful_prompt(seq,"B")
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--check",action="store_true");p.add_argument("--output",default="selfrep03");a=p.parse_args()
    if a.check:
        assert prior.parse("1:A 2:B",2)==["A","B"] and prior.parse("1:A 1:B",2) is None
        rows=corpus();print("ORACLE_CHECK",len(rows),sha(dump(rows)))
    else:
        prior.corpus=corpus
        prior.reconstruct_prompt=reconstruction
        prior.run(a.output)
