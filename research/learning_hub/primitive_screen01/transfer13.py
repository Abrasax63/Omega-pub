"""TRANSFER13: separate transfer-exam design; fixture selftest only.
Generate final exam only after checkpoints are frozen, with evaluator-held seed.
Same project author: not an independently curated examination.
"""
import argparse, hashlib, json, random
from collections import Counter, defaultdict
from pathlib import Path

KINDS=("copy","select","membership","reverse")
# Natural words unlike synthetic training tokens. No overlap with curriculum06 vocabulary.
WORDS="apple anchor almond amber apricot atlas bamboo basket beacon berry birch blade bloom boat bronze button cactus candle cedar chalk cherry chess cloud clover coral crane creek crown crystal daisy dawn delta desert dove drift drum dune eagle elm ember emerald fern finch flame flint forest frost garden glass globe grape grass harbor hazel honey iris ivory jade jasmine jewel kite lake lantern leaf lemon lilac lily linen lotus maple marble melon mint moon moss nectar oak ocean olive onyx opal orchid otter pearl pebble pine plum pond poppy quartz raven reed ridge river robin rose ruby sage sand shell shore silk slate snow solar sparrow spruce star stone storm swan thyme tiger tulip vale violet walnut wave wheat willow wind wren".split()
TEMPLATES={
 "copy":("Repeat the list verbatim: {s}. Return only the listed words, separated by spaces.","Keep all the words in exactly their original order: {s}. No commentary."),
 "select":("Starting with the first item as number one, which word occupies slot {p} in {s}? Give just that word.","Choose entry {p} from this sequence, counting from one: {s}. Respond with the entry alone."),
 "membership":("Among these entries, {s}, is {t} present? Reply only Yes or No.","Check whether {t} occurs as a complete word in the following list: {s}. Give Yes or No."),
 "reverse":("List the words from last to first: {s}. Separate them with spaces.","Read this sequence backwards by word, not by letter: {s}. Return only the reordered words.")
}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,obj):
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode()
    Path(path).write_bytes(raw);return sha(raw)
def truth(k,x,p,t):
    if k=="copy":return " ".join(x)
    if k=="reverse":return " ".join(reversed(x))
    if k=="select":return x[p-1]
    if k=="membership":return "Yes" if t in x else "No"
    raise ValueError("KIND")
def make(seed,form):
    rng=random.Random(seed);rows=[];seen=set()
    # 64 tasks per skill, 32 paired interventions. Equal lengths 2/3 or 4/5.
    for k in KINDS:
        for i in range(32):
            mode=i%2;longer=(i//2)%2
            n=(2+longer) if k in ("copy","reverse") else (4+longer)
            p=(i//4)%4+1 if k=="select" else None
            for _ in range(1000):
                x=rng.sample(WORDS,n);t=None
                if k in ("copy","reverse"):y=x[::-1]
                elif k=="select":
                    y=x.copy();q=rng.choice([j for j in range(n) if j!=p-1]);y[p-1],y[q]=y[q],y[p-1]
                else:
                    t=rng.choice([w for w in WORDS if w not in x]);y=x.copy();y[rng.randrange(n)]=t
                prompts=[TEMPLATES[k][mode].format(s=" ".join(z),p=p,t=t) for z in (x,y)]
                if len(set(prompts))==2 and not set(prompts)&seen:break
            else:raise ValueError("GENERATION")
            seen.update(prompts)
            # Pair direction randomized; pair members may not be presented consecutively.
            for j in rng.sample([0,1],2):
                z=(x,y)[j];rows.append(dict(id=f"{form}-{k}-{i}-{j}",pair=f"{form}-{k}-{i}",kind=k,items=z,position=p,target=t,template=mode,length=n,prompt=prompts[j],gold=truth(k,z,p,t)))
    rng.shuffle(rows);validate(rows);return rows
def validate(rows):
    need(len(rows)==256 and len({r["id"] for r in rows})==len({r["prompt"] for r in rows})==256,"COVERAGE")
    need(Counter(r["kind"] for r in rows)=={k:64 for k in KINDS},"BALANCE")
    g=defaultdict(list)
    for r in rows:
        k=r["kind"];x=r["items"];p=r["position"];t=r["target"]
        need(len(x)==len(set(x))==r["length"] and set(x)<=set(WORDS),"WORDS")
        need(r["gold"]==truth(k,x,p,t) and r["prompt"]==TEMPLATES[k][r["template"]].format(s=" ".join(x),p=p,t=t),"ORACLE")
        g[r["pair"]].append(r)
    for pair in g.values():
        need(len(pair)==2 and pair[0]["kind"]==pair[1]["kind"] and pair[0]["gold"]!=pair[1]["gold"],"PAIR")
        a,b=pair;k=a["kind"];x=a["items"];y=b["items"]
        need(a["template"]==b["template"] and len(x)==len(y),"MATCH")
        if k in ("copy","reverse"):need(x==y[::-1],"ORDER_PAIR")
        elif k=="select":need(a["position"]==b["position"] and sorted(x)==sorted(y) and sum(u!=v for u,v in zip(x,y))==2,"SELECTION_PAIR")
        else:need(a["target"]==b["target"] and {a["gold"],b["gold"]}=={"Yes","No"} and sum(u!=v for u,v in zip(x,y))==1,"MEMBERSHIP_PAIR")
    for k in KINDS:
        z=[r for r in rows if r["kind"]==k]
        need(Counter(r["template"] for r in z)=={0:32,1:32},"TEMPLATE_BALANCE")
        need(sorted(Counter(r["length"] for r in z).values())==[32,32],"LENGTH_BALANCE")
    need(Counter(r["position"] for r in rows if r["kind"]=="select")=={p:16 for p in range(1,5)},"POSITIONS")
def score(rows,predictions):
    validate(rows);idx={r["id"]:r for r in rows};got={}
    for p in predictions:
        need(set(p)=={"id","prompt_sha","raw"} and p["id"] in idx and p["id"] not in got and isinstance(p["raw"],str),"PREDICTION")
        need(p["prompt_sha"]==sha(idx[p["id"]]["prompt"].encode()),"PROMPT_HASH");got[p["id"]]=p["raw"]
    need(set(got)==set(idx),"COVERAGE")
    ok={i:got[i].strip()==r["gold"] for i,r in idx.items()}
    out={}
    for k in KINDS:
        z=[r for r in rows if r["kind"]==k];groups=defaultdict(list)
        for r in z:groups[r["pair"]].append(r)
        d=dict(correct=sum(ok[r["id"]] for r in z),both_pairs=sum(all(ok[r["id"]] for r in pair) for pair in groups.values()))
        d["by_template"]={str(i):sum(ok[r["id"]] for r in z if r["template"]==i) for i in (0,1)}
        d["by_length"]={str(n):sum(ok[r["id"]] for r in z if r["length"]==n) for n in sorted({r["length"] for r in z})}
        if k=="membership":d["by_class"]={v:sum(ok[r["id"]] for r in z if r["gold"]==v) for v in ("Yes","No")}
        if k=="select":d["by_position"]={str(i):sum(ok[r["id"]] for r in z if r["position"]==i) for i in range(1,5)}
        d["qualified"]=d["correct"]>=(61 if k!="reverse" else 58) and d["both_pairs"]>=(29 if k!="reverse" else 27) and min(d["by_template"].values())>=28 and min(d["by_length"].values())>=28
        if k=="membership":d["qualified"] &= min(d["by_class"].values())>=29
        if k=="select":d["qualified"] &= min(d["by_position"].values())>=14
        out[k]=d
    return out
def compare(base,candidate):
    need(set(base)==set(candidate)==set(KINDS),"SKILLS")
    dc={k:candidate[k]["correct"]-base[k]["correct"] for k in KINDS}
    dp={k:candidate[k]["both_pairs"]-base[k]["both_pairs"] for k in KINDS}
    return dict(correct_delta=dc,pair_delta=dp,exploratory_transfer_gain=min(dc.values())>=0 and min(dp.values())>=0 and sum(dc.values())>=8 and sum(dp.values())>=4,all_skills_qualified=all(candidate[k]["qualified"] for k in KINDS),promotion_authorized=False)
def freeze(seed,form,out):
    # Deliberately not exposed by CLI: independent evaluator/release process must invoke.
    rows=make(seed,form);out=Path(out);out.mkdir(exist_ok=False)
    q=[{k:r[k] for k in ("id","prompt")} for r in rows]
    qh=dump(out/"questions.json",q);lh=dump(out/"labels.json",rows)
    dump(out/"manifest.json",dict(form=form,questions_sha256=qh,labels_sha256=lh,scope="same-author separate transfer generator, not independent curator"))
def selftest():
    a=make(42,"fixture-a");b=make(73,"fixture-b")
    need(make(42,"fixture-a")==a,"DETERMINISM")
    def pred(r,raw):return dict(id=r["id"],prompt_sha=sha(r["prompt"].encode()),raw=raw)
    good=[pred(r,r["gold"]) for r in a];g=score(a,good)
    bad=score(a,[pred(r,"Yes") for r in a])
    need(all(d["qualified"] for d in g.values()) and bad["membership"]["correct"]==32 and bad["membership"]["both_pairs"]==0 and not bad["membership"]["qualified"],"CONSTANT")
    need(compare(bad,g)["exploratory_transfer_gain"] and not compare(g,bad)["exploratory_transfer_gain"],"COMPARISON")
    for z in (good[:-1],good+[good[0]],[dict(good[0],prompt_sha="bad")]+good[1:]):
        try:score(a,z)
        except ValueError:pass
        else:raise ValueError("NEGATIVE_CONTROL")
    import curriculum06 as c
    train=c.build("train",20261125);dev=c.build("dev",20261126)
    used={w for r in train+dev for w in r["items"]}|{r["target"] for r in train+dev if r["target"]}
    need(not set(WORDS)&used,"VOCAB_OVERLAP")
    need(not {r["prompt"] for r in a}&{r["prompt"] for r in train+dev},"PROMPT_OVERLAP")
    print(json.dumps(dict(status="TRANSFER13_FIXTURE_OK",tasks_per_form=256,pairs_per_form=128,fixture_form_overlap=len({r["prompt"] for r in a}&{r["prompt"] for r in b}),independent_curator=False,final_exam_generated=False,training_authorized=False)))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest"]);p.parse_args();selftest()
