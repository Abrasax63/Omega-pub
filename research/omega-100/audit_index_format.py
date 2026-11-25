"""Independent exact replay of the archived index-format replication."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile


def expected(seq, pos):
    numeric = list(zip(map(str, range(1,len(seq)+1)),seq,strict=True))
    return {"space":" ".join(" ".join(row) for row in numeric),
            "colon":" ".join(":".join(row) for row in numeric),
            "copy":" ".join(seq),"select":seq[pos-1]}


def main():
    t=perf_counter()
    archive=Path("format-index-repl01.zip")
    assert sha256(archive.read_bytes()).hexdigest()=="94424af7ea4649bfb07ecc69758a2db53afb0db2d4d7b067e87f4333304eb55f"
    with ZipFile(archive) as z:
        official=json.loads(z.read("result.json"))
        raw=z.read("corpus.json")
        assert sha256(raw).hexdigest()==official["corpus_sha256"]
        corpus=json.loads(raw)
        records=[json.loads(line) for line in z.read("predictions.jsonl").splitlines()]
    rows={r["id"]: r for r in corpus}
    oracle={i: expected(r["seq"],r["p"]) for i,r in rows.items()}
    assert len(rows)==len(corpus)==120
    p=expected(("A","B"),1)
    assert p["space"]!=p["colon"]
    assert "2:A 1:B" not in (p["colon"],p["space"])
    results={}
    for arm, published in official["scores"].items():
        d={r["id"]:r for r in records if r["arm"]==arm}
        assert len(d)==120 and d.keys()==rows.keys()
        exact, faithful, colon_as_space=Counter(),Counter(),0
        pair={}
        for i,x in d.items():
            row=rows[i]
            assert sha256(row["prompt"].encode()).hexdigest()==x["prompt_sha256"]
            tgt=oracle[i]
            op=row["op"]
            answer=x["raw"].strip()
            assert row["gold"]==tgt["colon" if op=="example" else op]
            hit=answer==row["gold"]
            exact[op]+=hit
            faithful[op]+=answer in {tgt["colon"],tgt["space"]} if op in ("colon","space","example") else hit
            if op in ("colon","space"):
                pair.setdefault(row["sid"],[]).append(hit)
            colon_as_space+=op=="colon" and answer==tgt["space"]
        assert len(pair)==24 and all(len(h)==2 for h in pair.values())
        n_pairs=sum(all(h) for h in pair.values())
        for op in exact:
            assert exact[op]==published[op]["exact"] and faithful[op]==published[op]["faithful"]
        assert n_pairs==published["format_pairs"]
        results[arm]=dict(exact=dict(exact),faithful=dict(faithful),pairs=n_pairs,colon_as_space=colon_as_space)
    assert len(records)==360
    s=results["pilot"]
    gate=(all(s["exact"][o]>=22 and s["faithful"][o]>=22 for o in ("example","colon","space"))
          and s["pairs"]>=20 and all(s["exact"][o]>=results["parent"]["exact"][o]-1 for o in ("copy","select")))
    assert gate==official["gate"]
    print(json.dumps(dict(scores=results,gate=gate,seconds=round(perf_counter()-t,6)),indent=2))


if __name__=="__main__":
    main()
