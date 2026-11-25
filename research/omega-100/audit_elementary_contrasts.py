"""Audit paired control and depth diagnostics from two original archives."""
import hashlib
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile


def load(name, sha):
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == sha
    with ZipFile(name) as archive:
        cases = json.loads(archive.read("corpus.json"))
        records = [json.loads(line) for line in archive.read("predictions.jsonl").splitlines()]
        report = json.loads(archive.read("result.json"))
    by_id = {r["id"]: r for r in cases}
    assert len(by_id) == len(cases)
    outputs = {(r["arm"], r["id"]): r["raw"].strip() for r in records}
    arms = set(report["scores"])
    assert len(outputs) == len(records) and outputs.keys() == {(a, i) for a in arms for i in by_id}
    assert all(hashlib.sha256(by_id[r["id"]]["prompt"].encode()).hexdigest() == r["prompt_sha256"]
               for r in records)
    return cases, outputs, report


def pair_metrics(sequence, keep, remove):
    bracketed = "[" + sequence + "]"
    return (keep == remove, keep == remove and keep in {sequence, bracketed},
            keep == bracketed and remove == sequence)


def control():
    cases, outputs, report = load("instruction-control.zip",
                                  "cf869dae3cb6ed5f3ee443968a1247382638bd49b1c58a158071a4e998b99b12")
    by_view = {}
    for row in cases:
        seq = row["seq"]
        expected = {"KEEP": "[" + seq + "]", "REMOVE": seq, "SELECT": seq.split()[row["p"]-1]}
        assert row["gold"] == expected[row["op"]]
        roles = by_view.setdefault(row["view"], {}).setdefault(seq, {})
        assert row["op"] not in roles
        roles[row["op"]] = row["id"], expected[row["op"]]
    summary = {}
    for arm, views in report["scores"].items():
        summary[arm] = {}
        for view, cases in by_view.items():
            assert len(cases) == 16 and all(len(roles) == 3 for roles in cases.values())
            out = [{op: outputs[arm, ident] for op, (ident, gold) in roles.items()}
                   for roles in cases.values()]
            exact = {op: sum(pred[op] == roles[op][1] for pred, roles in zip(out, cases.values(), strict=True))
                     for op in ("KEEP", "REMOVE", "SELECT")}
            assert exact == {op: cell["exact"] for op, cell in views[view]["ops"].items()}
            metrics = [pair_metrics(seq, p["KEEP"], p["REMOVE"]) for seq, p in zip(cases, out, strict=True)]
            equal, literal_collisions, both_exact = map(sum, zip(*metrics))
            summary[arm][view] = dict(n=len(cases), identical=equal, literal_collisions=literal_collisions,
                                      both_exact=both_exact, exact=exact)
    return summary


def depth():
    cases, outputs, report = load("position-depth.zip",
                                  "43e4ddaea6229fb87eb5ffc1eb0f28f9639c45bbe3d380f2a4dd6d627da0356f")
    result = {}
    for arm, views in report["scores"].items():
        result[arm] = {}
        for view, totals in views.items():
            exact = {"short": 0, "early": 0, "late": 0}
            for row in cases:
                if row["view"] != view:
                    continue
                expected = row["seq"][row["p"]-1]
                assert len(row["seq"]) == row["n"] and expected == row["gold"]
                cell = "short" if row["n"] == 4 else "early" if row["p"] <= 4 else "late"
                exact[cell] += outputs[arm, row["id"]] == expected
            assert all(exact[key] == totals[key] for key in exact)
            result[arm][view] = exact
    spaced, indexed = (result["cumulative"][view] for view in ("spaced", "indexed"))
    contrasts = {"length_loss": spaced["short"]-spaced["early"],
                 "depth_loss": spaced["early"]-spaced["late"],
                 "indexed_late_gain": indexed["late"]-spaced["late"]}
    assert contrasts == report["contrasts"]
    return {"scores": result, "contrasts": contrasts}


def main():
    start = perf_counter()
    assert pair_metrics("B X C", "B X C", "B X C") == (True, True, False)
    assert pair_metrics("B X C", "[B X C]", "B X C") == (False, False, True)
    paired = control()
    delta = {v: paired["copy"][v]["identical"] - paired["base"][v]["identical"] for v in paired["base"]}
    print(json.dumps({"instruction": paired, "copy_minus_base_collisions": delta,
                      "descriptive_threshold_met": all(n >= 4 for n in delta.values()),
                      "depth": depth(), "seconds": round(perf_counter()-start, 5)}, indent=2))


if __name__ == "__main__":
    main()
