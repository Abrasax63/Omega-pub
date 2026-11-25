"""Rescore PROTECT24 without importing the model or the generator."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

PIN = "6b7180c7933fe35e908e2236bed046b1bd6ce9f01a53eb98e3f957cb75ffa7a9"


def answer(row):
    words = row["items"]
    if "start" in row:
        return " ".join(words[row["start"]-1:row["start"]+1])
    kind = row["kind"]
    if kind == "membership":
        return "Yes" if row["target"] in set(words) else "No"
    if kind == "select":
        return words[row["position"]-1]
    return " ".join(words[::-1] if kind == "reverse" else words)


def score(labels, outputs):
    index = {r["id"]:r for r in labels}
    seen = {}
    for prediction in outputs:
        key = prediction["id"]
        assert key not in seen
        row = index[key]
        assert prediction["prompt_sha"] == sha256(row["prompt"].encode()).hexdigest()
        expected = answer(row)
        assert expected == row["gold"]
        seen[key] = prediction["raw"].strip() == expected
    assert seen.keys() == index.keys()
    groups = defaultdict(list)
    for key,row in index.items():
        groups[row.get("kind", "new"),row["pair"]].append(seen[key])
    assert all(len(p)==2 for p in groups.values())
    results = {}
    for kind in sorted({k for k,_ in groups}):
        pairs = [p for (k,_),p in groups.items() if k == kind]
        assert len(pairs)==32
        results[kind] = dict(correct=sum(sum(p) for p in pairs),both_pairs=sum(all(p) for p in pairs))
    return results


def main():
    tick = perf_counter()
    path = Path("protect24.zip")
    assert sha256(path.read_bytes()).hexdigest()==PIN
    results = {}
    with ZipFile(path) as z:
        read = lambda name: json.loads(z.read(name))
        archived = read("result.json")
        labels = {part:read(f"labels-{part}.json") for part in ("old","new")}
        questions = read("questions.json")
        expected = {r["id"]:r["prompt"] for rs in labels.values() for r in rs}
        assert len(expected)==len(questions)==320 and len(set(expected.values()))==320
        assert {r["id"]:r["prompt"] for r in questions}==expected
        assert all(set(r)=={"id","prompt"} for r in questions)
        for arm in ("control","ordinary","protected"):
            results[arm] = {}
            for part,rows in labels.items():
                preds = read(f"{arm}-{part}.json")
                calculated = score(rows,preds)
                if arm=="control" and part=="new":
                    try:
                        score(rows,preds+preds[:1])
                    except AssertionError:
                        pass
                    else:
                        raise AssertionError("duplicate prediction admitted")
                wanted = archived["scores"][arm][part]
                if part=="new":
                    calculated = calculated["new"]
                    assert all(wanted[k]==n for k,n in calculated.items())
                else:
                    assert all(wanted[skill][k]==n for skill,v in calculated.items() for k,n in v.items())
                results[arm][part] = calculated
            if arm!="control":
                steps = read(f"{arm}-steps.json")
                assert len(steps)==archived["candidate_steps_per_arm"]
                assert sum(s["auxiliary_anchor_gradients"] for s in steps)==archived["auxiliary_anchor_gradients_per_arm"]
    deltas = {}
    for arm in ("ordinary","protected"):
        delta = {k:{s:v[k]-results["control"]["old"][s][k] for s,v in results[arm]["old"].items()}
                 for k in ("correct","both_pairs")}
        gate = min(v for d in delta.values() for v in d.values())>=0 and results[arm]["new"]["correct"]>=61 and results[arm]["new"]["both_pairs"]>=29
        assert delta["correct"]==archived["retention"][arm]["old_correct_delta"]
        assert delta["both_pairs"]==archived["retention"][arm]["old_pair_delta"]
        assert gate==archived["retention"][arm]["exploratory_pass"]
        deltas[arm] = delta
    print(json.dumps(dict(results=results,deltas=deltas,archive_sha256=PIN,
                          reported_run_seconds=archived["seconds"],audit_seconds=perf_counter()-tick),indent=2))

if __name__=="__main__":
    main()
