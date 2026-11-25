"""RETENTION15: new-skill corpus contract and prospective retention scorer.
Offline fixtures only; no model execution, no release or independent exam claim.
"""
import argparse, hashlib, json, random
from collections import Counter, defaultdict
import curriculum06 as c

SIZES={"train":128,"dev":32,"fixture":64}
TEMPLATES={
    "train":("Return words {p} and {q} in that order, separated by a space: {s}.",
             "Copy the two consecutive entries starting at number {p}: {s}."),
    "dev":("Give the adjacent words beginning at position {p}, counting from one: {s}.",
           "From this list, take items {p} then {q}: {s}. Output only those words."),
    "fixture":("Starting at the {ordinal} item, reproduce it and its immediate successor: {s}.",
               "Which consecutive pair begins in slot {p} of {s}? Write the pair only.")
}
ORD=("first","second","third","fourth","fifth")
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()
def words(split):
    # New disjoint synthetic lexicon; no previous training words.
    stem={"train":"zu","dev":"ve","fixture":"xo"}[split]
    return [stem+a+b for a in "bcdfghjklmnpqrst" for b in "aeiou"]
def render(split,x,p,m):
    return TEMPLATES[split][m].format(p=p,q=p+1,s=" ".join(x),ordinal=ORD[p-1])
def build(split,seed):
    rng=random.Random(seed);out=[];seen=set()
    for i in range(SIZES[split]//2):
        # Four-word and five-word lists; all valid start positions balanced within length.
        n=4+(i%2);p=1+(i//2)%(n-1);m=(i//8)%2
        for _ in range(1000):
            x=rng.sample(words(split),n);y=x.copy()
            # Change one targeted word by swapping with an outside word.
            j=p-1+(i//2)%2
            k=rng.choice([a for a in range(n) if a not in (p-1,p)])
            y[j],y[k]=y[k],y[j]
            prompts=[render(split,z,p,m) for z in (x,y)]
            if len(set(prompts))==2 and not set(prompts)&seen:break
        else:raise ValueError("GENERATION")
        seen.update(prompts)
        for a,z in enumerate((x,y)):
            out.append(dict(id=f"{split}-adjacent-{i}-{a}",pair=f"{split}-adjacent-{i}",split=split,items=z,start=p,template=m,prompt=prompts[a],gold=" ".join(z[p-1:p+1])))
    rng.shuffle(out);validate(out,split);return out
def validate(rows,split):
    need(len(rows)==SIZES[split] and len({r["id"] for r in rows})==len({r["prompt"] for r in rows})==len(rows),"COVERAGE")
    g=defaultdict(list)
    for r in rows:
        x=r["items"];p=r["start"]
        need(r["split"]==split and len(x) in (4,5) and len(x)==len(set(x)) and set(x)<=set(words(split)),"LEXICON")
        need(type(p) is int and 1<=p<len(x),"POSITION")
        need(r["gold"]==" ".join(x[p-1:p+1]) and r["prompt"]==render(split,x,p,r["template"]),"ORACLE")
        g[r["pair"]].append(r)
    for z in g.values():
        need(len(z)==2,"PAIR")
        a,b=z;x=a["items"];y=b["items"];p=a["start"]
        need(p==b["start"] and a["template"]==b["template"] and sorted(x)==sorted(y),"MATCH")
        diff={i for i,(u,v) in enumerate(zip(x,y)) if u!=v}
        need(len(diff)==2 and len(diff&{p-1,p})==1 and a["gold"]!=b["gold"],"CONTRAST")
    for n in (4,5):
        counts=Counter(r["start"] for r in rows if len(r["items"])==n)
        need(set(counts)==set(range(1,n)) and max(counts.values())-min(counts.values())<=2,"POSITION_BALANCE")
    need(Counter(r["template"] for r in rows)=={0:len(rows)//2,1:len(rows)//2},"TEMPLATE_BALANCE")
def score(rows,pred,split):
    validate(rows,split);idx={r["id"]:r for r in rows};seen={}
    for p in pred:
        need(set(p)=={"id","prompt_sha","raw"} and p["id"] in idx and p["id"] not in seen and isinstance(p["raw"],str),"TRACE")
        need(p["prompt_sha"]==sha(idx[p["id"]]["prompt"]),"PROMPT_HASH")
        seen[p["id"]]=p["raw"].strip()==idx[p["id"]]["gold"]
    need(set(seen)==set(idx),"MISSING")
    g=defaultdict(list)
    for r in rows:g[r["pair"]].append(seen[r["id"]])
    return dict(correct=sum(seen.values()),both_pairs=sum(all(v) for v in g.values()),total=len(rows),pairs=len(g))
def retention(reference,candidate,new):
    need(set(reference)==set(candidate)==set(c.KINDS),"OLD_SKILLS")
    for m in (reference,candidate):
        for v in m.values():
            need(type(v["correct"]) is int and type(v["both_pairs"]) is int and 0<=v["both_pairs"]<=32 and 2*v["both_pairs"]<=v["correct"]<=32+v["both_pairs"],"OLD_COUNTS")
    need(new["total"]==64 and new["pairs"]==32 and 0<=new["both_pairs"]<=32 and 2*new["both_pairs"]<=new["correct"]<=32+new["both_pairs"],"NEW_COUNTS")
    dc={k:candidate[k]["correct"]-reference[k]["correct"] for k in c.KINDS}
    dp={k:candidate[k]["both_pairs"]-reference[k]["both_pairs"] for k in c.KINDS}
    return dict(old_correct_delta=dc,old_pair_delta=dp,new_skill_threshold=new["correct"]>=61 and new["both_pairs"]>=29,no_observed_regression=min(dc.values())>=0 and min(dp.values())>=0,exploratory_pass=min(dc.values())>=0 and min(dp.values())>=0 and new["correct"]>=61 and new["both_pairs"]>=29,promotion_authorized=False)
def selftest():
    data={s:build(s,20261125+i) for i,s in enumerate(SIZES)}
    need(build("fixture",20261127)==data["fixture"],"DETERMINISM")
    allold=set().union(*(set(c.vocab(s)) for s in c.SPLITS))
    for s in SIZES:
        need(not set(words(s))&allold,"OLD_VOCAB")
        for u in SIZES:
            if s!=u:need(not set(words(s))&set(words(u)),"LEAK")
    z=data["fixture"]
    good=[dict(id=r["id"],prompt_sha=sha(r["prompt"]),raw=r["gold"]) for r in z]
    perfect=score(z,good,"fixture");need(perfect["correct"]==64 and perfect["both_pairs"]==32,"ORACLE")
    # A constant response and a one-word partial response cannot qualify.
    for raw in ("constant",None):
        bad=[dict(id=r["id"],prompt_sha=sha(r["prompt"]),raw=raw if raw is not None else r["gold"].split()[0]) for r in z]
        need(score(z,bad,"fixture")["correct"]==0,"NEGATIVE")
    base={k:dict(correct=32,both_pairs=12) for k in c.KINDS}
    dropped={k:dict(v) for k,v in base.items()};dropped["copy"]["correct"]-=1
    need(retention(base,base,perfect)["exploratory_pass"] and not retention(base,dropped,perfect)["exploratory_pass"],"RETENTION")
    for bad in (good[:-1],good+[good[0]],[dict(good[0],prompt_sha="bad")]+good[1:]):
        try:score(z,bad,"fixture")
        except ValueError:pass
        else:raise ValueError("TRACE_NEGATIVE")
    print(json.dumps(dict(status="RETENTION15_FIXTURE_OK",rows={s:len(z) for s,z in data.items()},paired=True,independent_curator=False,final_exam_generated=False,model_executed=False,training_authorized=False)))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest"]);p.parse_args();selftest()
