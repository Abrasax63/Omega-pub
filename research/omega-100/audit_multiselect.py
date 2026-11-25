"""Rescore completed multiselect predictions without publishing labels."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile


def gold(row):
    s=row["seq"]
    op=row["op"]
    if op=="copy":
        return " ".join(s)
    if op=="single":
        return s[row["p"]-1]
    if op=="index":
        return " ".join(":".join((str(i),a)) for i,a in enumerate(s,1))
    assert op=="multi" and row["p"]!=row["q"]
    return " ".join(s[p-1] for p in (row["p"],row["q"]))


def read(name, expected, *files):
    path=Path(name)
    assert sha256(path.read_bytes()).hexdigest()==expected
    with ZipFile(path) as z:
        return [z.read(f) for f in files]


def main():
    start=perf_counter()
    result, preds=read("multiselect-results.zip","6d8d33f7b9121d34d70174f8b54fdb7902b29383a11729aa60b400cd6cc6afac",
                       "result.json","predictions.jsonl")
    raw,=read("multiselect-test.zip","eae42c9bdb3bc00e9475dc4331f74bdb2697afe612a73d9fa702bb1ee0f06934","data.json")
    result=json.loads(result)
    assert not result["cohort_B_consumed"] and sha256(raw).hexdigest()==result["test_sha256"]
    cases=json.loads(raw)
    rows={r["id"]:r for r in cases}
    assert len(rows)==len(cases)==192
    truth={i:gold(r) for i,r in rows.items()}
    assert all(truth[i]==r["gold"] for i,r in rows.items())
    control={"seq":["X","Y"],"p":1,"q":2,"op":"multi"}
    assert gold(control)!="Y X" and gold(control)!="X X"
    records=[json.loads(l) for l in preds.splitlines()]
    answers={(r["arm"],r["id"]):r["raw"].strip() for r in records}
    assert len(answers)==len(records)==576
    assert answers.keys()=={(a,i) for a in result["scores"] for i in rows}
    assert all(sha256(rows[r["id"]]["prompt"].encode()).hexdigest()==r["prompt_sha256"] for r in records)
    scores={}
    for arm,official in result["scores"].items():
        cells=defaultdict(lambda:defaultdict(list))
        for i,r in rows.items():
            key=f"{r['group']}_{r['op']}{r['view']}"
            cells[key][r["sid"]].append(answers[arm,i]==truth[i])
        scores[arm]={}
        for key,items in cells.items():
            pairs=list(items.values())
            exact=sum(sum(p) for p in pairs)
            n=sum(map(len,pairs))
            pair_correct=sum(all(p) for p in pairs) if "multi" in key or "single" in key else None
            assert (exact,n,pair_correct)==tuple(official[key][x] for x in ("exact","n","pairs"))
            scores[arm][key]=dict(exact=exact,n=n,pairs=pair_correct)
    p,s=scores["parent"],scores["pilot"]
    acquire=all(s[k]["exact"]>=29 and s[k]["pairs"]>=13 and s[k]["exact"]-p[k]["exact"]>=8
                for k in ("short_multi0","short_multi1"))
    retain=(all(s[k]["exact"]>=p[k]["exact"]-1 for k in s if "multi" not in k)
            and all(s[k]["exact"]>=n for k,n in (("short_copy0",15),("short_index0",15),("short_single0",29))))
    assert (acquire,retain,acquire and retain)==tuple(result[k] for k in ("acquisition_gate","retention_gate","gate"))
    lost=[i for i,r in rows.items() if r["group"]=="long" and r["op"]=="index"
          and answers["parent",i]==truth[i] and answers["pilot",i]!=truth[i]]
    rescued=sum(" ".join(answers["pilot",i].split())==truth[i] for i in lost)
    print(json.dumps(dict(scores=scores,acquisition=acquire,retention=retain,
                          long_index_regressions=len(lost),whitespace_only=rescued,
                          seconds=round(perf_counter()-start,6)),indent=2))


if __name__=="__main__":
    main()
