"""RELATION19: controlled instruction-switch diagnostic.
Same ordered list within each pair, only requested operation/position changes.
Public same-author fixture, not independent qualification. No training.
"""
import argparse,hashlib,json,random
from collections import Counter,defaultdict
from pathlib import Path
import curriculum06 as c
import transfer13 as x

SEED=2026112519
WORDS="acorn agate anvil arrow attic badger barley basil beach beech beetle bison braid brook broom brush buckle cabin camel canary canyon carpet carrot cellar chest cider citrus cliff clove cocoa comet copper cotton cougar cypress dahlia daisy2 dandelion dolphin donkey dragon easel earth ebony egret elder falcon feather fennel fig flannel flute fox garland gecko ginger glacier goblet granite heron holly horse hyacinth indigo island jackal juniper kettle koala lamb larch lichen lime lizard lobster locket magpie mango meadow mirror monkey muffin mushroom myrtle nickel nutmeg octopus onion orange osprey panda parrot peach pencil pepper pigeon pitcher platypus pollen pumpkin radish reindeer ribbon saffron salmon satin scorpion seagull sesame shrimp silver snail spruce2 squash stork sugar summit sunflower tablet teak thistle tomato topaz trout turtle velvet viper weasel whale willow2 zebra".split()
# Exclude any accidental overlap with earlier transfer vocabulary.
WORDS=[w for w in WORDS if w not in x.WORDS and w.isalpha()]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(s):return hashlib.sha256(s.encode()).hexdigest()
def prompt(k,items,operation,template):
    s=" ".join(items)
    if k=="position":
        return (f"From the list {s}, output only item {operation}, counting from one." if template==0 else f"List: {s}. Which word is at position {operation}? Reply with one word.")
    if template==0:return f"List: {s}. Output its words in {operation} order, separated by spaces."
    return f"For {s}, write the words {'from first to last' if operation=='original' else 'from last to first'}. No other text."
def oracle(k,items,op):
    return items[op-1] if k=="position" else " ".join(items if op=="original" else items[::-1])
def build(seed=SEED):
    rng=random.Random(seed);rows=[];seen=set()
    for k in ("position","direction"):
        for i in range(32):
            template=i%2;n=4 if k=="position" else 2+(i//2)%2
            # Eight distinct ordered position pairs, each used four times.
            first=(i//2)%4+1;offset=1+(i//8)%2
            ops=[first,(first-1+offset)%4+1] if k=="position" else ["original","reverse"]
            for _ in range(1000):
                items=rng.sample(WORDS,n);ps=[prompt(k,items,op,template) for op in ops]
                if not set(ps)&seen:break
            else:raise ValueError("GENERATION")
            seen.update(ps)
            for j,op in enumerate(ops):
                rows.append(dict(id=f"relation19-{k}-{i}-{j}",pair=f"{k}-{i}",kind=k,items=items,op=op,template=template,prompt=ps[j],gold=oracle(k,items,op)))
    rng.shuffle(rows);validate(rows);return rows
def validate(rows):
    need(len(rows)==128 and len({r["id"] for r in rows})==len({r["prompt"] for r in rows})==128,"COVERAGE")
    need(Counter(r["kind"] for r in rows)=={"position":64,"direction":64},"BALANCE")
    g=defaultdict(list)
    for r in rows:
        need(len(set(r["items"]))==len(r["items"]) and set(r["items"])<=set(WORDS),"ITEMS")
        need(r["prompt"]==prompt(r["kind"],r["items"],r["op"],r["template"]) and r["gold"]==oracle(r["kind"],r["items"],r["op"]),"ORACLE")
        g[r["pair"]].append(r)
    for z in g.values():
        need(len(z)==2,"PAIR")
        a,b=z;need(a["kind"]==b["kind"] and a["items"]==b["items"] and a["template"]==b["template"] and a["op"]!=b["op"] and a["gold"]!=b["gold"],"INSTRUCTION_SWITCH")
    need(Counter(r["op"] for r in rows if r["kind"]=="position")=={i:16 for i in range(1,5)},"POSITIONS")
    need(Counter(r["op"] for r in rows if r["kind"]=="direction")=={"original":32,"reverse":32},"DIRECTION")
def score(rows,pred):
    validate(rows);idx={r["id"]:r for r in rows};got={}
    for p in pred:
        need(set(p)=={"id","prompt_sha","raw"} and p["id"] in idx and p["id"] not in got and isinstance(p["raw"],str),"TRACE")
        need(p["prompt_sha"]==digest(idx[p["id"]]["prompt"]),"HASH")
        got[p["id"]]=p["raw"].strip()
    need(set(got)==set(idx),"MISSING")
    result={}
    for k in ("position","direction"):
        z=[r for r in rows if r["kind"]==k];g=defaultdict(list)
        for r in z:g[r["pair"]].append(r)
        ok=lambda r:got[r["id"]]==r["gold"]
        result[k]=dict(correct=sum(ok(r) for r in z),both_pairs=sum(all(ok(r) for r in v) for v in g.values()),identical_response_pairs=sum(got[v[0]["id"]]==got[v[1]["id"]] for v in g.values()),foil_errors=sum(got[a["id"]]==b["gold"] for v in g.values() for a,b in (v,v[::-1])),by_operation={str(op):sum(ok(r) for r in z if r["op"]==op) for op in sorted({r["op"] for r in z})})
    return result
def selftest():
    rows=build();need(rows==build(),"DETERMINISM")
    def preds(fn):return [dict(id=r["id"],prompt_sha=digest(r["prompt"]),raw=fn(r)) for r in rows]
    good=score(rows,preds(lambda r:r["gold"]))
    need(all(v["correct"]==64 and v["both_pairs"]==32 for v in good.values()),"ORACLE")
    bad=score(rows,preds(lambda r:r["items"][0] if r["kind"]=="position" else " ".join(r["items"])))
    need(bad["position"]["correct"]==16 and bad["direction"]["correct"]==32 and all(v["both_pairs"]==0 and v["identical_response_pairs"]==32 for v in bad.values()),"INVARIANT_NEGATIVE")
    need(not set(WORDS)&set(x.WORDS) and not set(WORDS)&set().union(*(set(c.vocab(s)) for s in c.SPLITS)),"VOCAB")
    print("RELATION19 offline oracle and instruction-insensitive controls passed")
def baseline(out):
    import torch
    from transformers import AutoTokenizer,AutoModelForCausalLM
    selftest();rows=build();torch.set_num_threads(2)
    tok=AutoTokenizer.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False)
    model=AutoModelForCausalLM.from_pretrained(c.MODEL,revision=c.REV,trust_remote_code=False,torch_dtype=torch.float32);model.eval()
    need(model.config._commit_hash==c.REV,"MODEL_PIN")
    out=Path(out);out.mkdir(exist_ok=False);pred=[]
    for i,r in enumerate(rows):
        q=r["prompt"];txt=tok.apply_chat_template([{"role":"user","content":q}],tokenize=False,add_generation_prompt=True)
        inp=tok(txt,return_tensors="pt",add_special_tokens=False);n=inp["input_ids"].shape[1]
        with torch.inference_mode():ids=model.generate(**inp,do_sample=False,max_new_tokens=16,pad_token_id=tok.eos_token_id,use_cache=False)[0,n:].tolist()
        pred.append(dict(id=r["id"],prompt_sha=digest(q),raw=tok.decode(ids,skip_special_tokens=True,clean_up_tokenization_spaces=False)))
        if (i+1)%32==0:print("RELATION19",i+1,"/128",flush=True)
    (out/"predictions.json").write_text(json.dumps(pred,indent=2))
    report=dict(status="FROZEN_BASE_INSTRUCTION_SWITCH",model=c.MODEL,revision=c.REV,score=score(rows,pred),optimizer_updates=0,independent_curator=False,promotion_authorized=False)
    (out/"result.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("cmd",choices=["selftest","baseline"]);p.add_argument("--out");a=p.parse_args()
    if a.cmd=="selftest":selftest()
    else:baseline(a.out)
