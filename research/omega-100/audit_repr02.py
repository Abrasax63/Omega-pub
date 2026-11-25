"""Audit decoded decision invariance under reversal of A/B label codes."""
from collections import Counter
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile


def decision(positive,negative):
    return int(positive>negative)-int(positive<negative)


def main():
    start=perf_counter()
    path=Path("repr02-github.zip")
    assert sha256(path.read_bytes()).hexdigest()=="6f73ba624974c24314ba775de3a0daca3ffb8da4522042a30cc3656bcaa180d1"
    with ZipFile(path) as z:
        raw=z.read("predictions.jsonl")
        official=json.loads(z.read("result.json"))
    assert sha256(raw).hexdigest()==official["predictions_sha256"]
    records=[json.loads(l) for l in raw.splitlines()]
    by={(r["view"],r["mode"],r["id"]):r for r in records}
    ids={r["id"] for r in records}
    views=set(official["scores"])
    modes=("ab_forward","ab_reverse","yesno")
    assert len(by)==len(records)==official["forward_passes"]==384
    assert set(by)=={(v,m,i) for v in views for m in modes for i in ids}
    assert len(ids)==64 and len(views)==2
    assert all(r["revision"]==official["revision"] for r in records)
    assert all(isfinite(r[field]) for r in records for field in ("positive_logit","negative_logit"))
    assert decision(2,1)!=decision(1,2)
    assert decision(2,1)==decision(3,1)
    scores={}
    for view in sorted(views):
        tally=Counter()
        tokens=Counter()
        for i in ids:
            a,b=(by[view,m,i] for m in modes[:2])
            first=(a["positive_symbol"],a["negative_symbol"])
            second=(b["positive_symbol"],b["negative_symbol"])
            assert first==second[::-1] and set(first)=={"A","B"}
            x,y=(decision(r["positive_logit"],r["negative_logit"]) for r in (a,b))
            for rec, d in ((a,x),(b,y)):
                symbol = rec["positive_symbol"] if d>0 else rec["negative_symbol"] if d<0 else "tie"
                tokens[symbol]+=1
            tally["ties" if not x*y else "agrees" if x==y else "changes"]+=1
        scores[view]={**dict(tally),"preferred_tokens":dict(tokens),"quarter_screen":tally["changes"]>=16,
                      "official":official["scores"][view]}
    print(json.dumps(dict(scores=scores,seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
