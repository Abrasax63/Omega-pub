"""Re-evaluate archived PILOT14 responses on its public-seed cohort."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

from transfer13 import make

PIN = "c89bee90d9f811437d9735454613c35b4a3c4dc8"
FILES = dict(results="b052cd8ab6f17ce0d508d617358dd38b0a0d83d569bf5e572a7deab976c2e0b8",
             adaptive="11c5d1fbe92f098096acc1fe0d642676fe4d82d393dd0d0db114cc5a340959a9",
             contrastive="6f7f9703065bbeae3d3bca85a9707edb72e141903bcb7c1f625874168bcd6f3a",
             supervised="95ead8fe314b60b604b596596d4c9ad0419c4187722b0d6813a573ff07441d95",
             base="27c982b5bbcee3c62798ec5ad25cd037ea5d0903af03a4d4b492bc91ef24e23a")


def digest(data):
    return sha256(data).hexdigest()


def oracle(r):
    kind, items = r["kind"], r["items"]
    if kind == "select":
        return items[r["position"] - 1]
    if kind == "membership":
        return ("No", "Yes")[r["target"] in set(items)]
    return " ".join(items[::(-1 if kind == "reverse" else 1)])


def calculate(rows, raw):
    seen = {}
    for v in raw:
        i = v["id"]
        assert i in rows and i not in seen and digest(rows[i]["prompt"].encode()) == v["prompt_sha"]
        seen[i] = v["raw"].strip()
    assert seen.keys() == rows.keys()
    by_kind = defaultdict(list)
    pairs = defaultdict(list)
    for ident, row in rows.items():
        want = oracle(row)
        assert want == row["gold"]
        by_kind[row["kind"]].append((row, want, seen[ident] == want))
        pairs[row["pair"]].append(seen[ident] == want)
    assert all(len(p) == 2 for p in pairs.values())
    result = {}
    for k, r in by_kind.items():
        pair_ids = {row["pair"] for row, _, _ in r}
        assert len(r) == 64 and len(pair_ids) == 32
        d = dict(correct=sum(ok for _,_,ok in r), both_pairs=sum(all(pairs[p]) for p in pair_ids))
        for key in ("template", "length", "position"):
            if key != "position" or k == "select":
                d["by_"+key] = {str(v): sum(ok for row,_,ok in r if row[key] == v)
                                 for v in sorted({row[key] for row,_,_ in r})}
        if k == "membership":
            d["by_class"] = {v: sum(ok for _,want,ok in r if want == v) for v in ("Yes","No")}
        low = min([*d["by_length"].values(), *d["by_template"].values()])
        d["qualified"] = d["correct"] >= (58 if k == "reverse" else 61) and d["both_pairs"] >= (27 if k == "reverse" else 29) and low >= 28
        if k == "membership":
            d["qualified"] &= min(d["by_class"].values()) >= 29
        if k == "select":
            d["qualified"] &= min(d["by_position"].values()) >= 14
        result[k] = d
    return result


def main():
    start = perf_counter()
    for key, expected in FILES.items():
        assert digest(Path(f"pilot14-{key}.zip").read_bytes()) == expected
    with ZipFile("pilot14-results.zip") as z:
        published = json.loads(z.read("pilot14-result.json"))
    rows = {r["id"]: r for r in make(2026112514, "pilot14")}
    assert len(rows) == 256
    output, reports = {}, {}
    for arm in ("base", "supervised", "contrastive", "adaptive"):
        with ZipFile(f"pilot14-{arm}.zip") as z:
            m = json.loads(z.read("manifest.json"))
            p = z.read("predictions.jsonl")
        assert m["arm"] == arm and m["revision"] == PIN and digest(p) == m["predictions_sha"]
        assert m["optimizer_updates"] == (0 if arm == "base" else 128)
        raw = [json.loads(x) for x in p.splitlines()]
        result = calculate(rows, raw)
        assert result == published["scores"][arm]
        if arm == "base":
            try:
                calculate(rows, raw + raw[:1])
            except AssertionError:
                pass
            else:
                raise AssertionError("duplicate prediction admitted")
        reports[arm] = m
        output[arm] = dict(scores=result, optimizer_updates=m["optimizer_updates"],
                           transfer_seconds=m["transfer_seconds"],
                           train_and_dev_seconds=m.get("train_and_dev_seconds"))
    assert len({m["budget_file_sha"] for m in reports.values()}) == 1
    assert reports["supervised"]["budget"] == reports["contrastive"]["budget"]
    for key in ("initial_adapter_sha", "frozen_base_sha"):
        assert len({m[key] for arm,m in reports.items() if arm != "base"}) == 1
    for arm in ("supervised", "contrastive", "adaptive"):
        assert reports[arm]["budget"] == published["budgets"][arm]
        scores, base = output[arm]["scores"], output["base"]["scores"]
        counts = [v["correct"] - base[k]["correct"] for k, v in scores.items()]
        pairs = [v["both_pairs"] - base[k]["both_pairs"] for k, v in scores.items()]
        exploratory = min(counts) >= 0 and min(pairs) >= 0 and sum(counts) >= 8 and sum(pairs) >= 4
        assert exploratory == published["comparisons"][arm]["exploratory_transfer_gain"]
    print(json.dumps(dict(arms=output, archive_sha256=FILES, audit_seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
