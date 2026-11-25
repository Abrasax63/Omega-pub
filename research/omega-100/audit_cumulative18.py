"""Recompute CUMULATIVE18 retention scores from archived predictions."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path
import sys
from time import perf_counter
from types import SimpleNamespace
from zipfile import ZipFile

# The fixture generator is pure; its other contract needs this constant only.
sys.modules["curriculum06"] = SimpleNamespace(KINDS=("copy","select","membership","reverse"))
import retention15
import transfer13

PIN = "194174f5c62ef93d9f5bc7e2627faf4d0c89640641ed3028c6feb343c866ba8b"
PILOT = "11c5d1fbe92f098096acc1fe0d642676fe4d82d393dd0d0db114cc5a340959a9"


def digest(data):
    return sha256(data).hexdigest()


def answer(row):
    words = row["items"]
    if "start" in row:
        return " ".join(words[row["start"]-1:row["start"]+1])
    k = row["kind"]
    if k == "membership":
        return "Yes" if row["target"] in set(words) else "No"
    if k == "select":
        return words[row["position"] - 1]
    return " ".join(words[::(-1 if k == "reverse" else 1)])


def score(rows, predictions):
    ids = {r["id"]:r for r in rows}
    groups = defaultdict(list)
    seen = set()
    for v in predictions:
        i = v["id"]
        r = ids[i]
        assert i not in seen and v["prompt_sha"] == digest(r["prompt"].encode())
        seen.add(i)
        want = answer(r)
        assert want == r["gold"]
        groups[r.get("kind","new"),r["pair"]].append(v["raw"].strip() == want)
    assert seen == ids.keys() and all(len(p)==2 for p in groups.values())
    out = {}
    for kind in {k for k,_ in groups}:
        pairs = [p for (k,_),p in groups.items() if k == kind]
        out[kind] = dict(correct=sum(sum(p) for p in pairs),both_pairs=sum(all(p) for p in pairs))
    return out


def main():
    start = perf_counter()
    archive = Path("next0.zip")
    pilot = Path("../pilot14/pilot14-adaptive.zip")
    assert digest(archive.read_bytes()) == PIN and digest(pilot.read_bytes()) == PILOT
    old = transfer13.make(2026112518,"retention18-old")
    new = retention15.build("fixture",2026112519)
    assert not {r["prompt"] for r in old} & {r["prompt"] for r in transfer13.make(2026112514,"pilot14")}
    arms = {}
    with ZipFile(archive) as z, ZipFile(pilot) as p:
        prev = p.read("predictions.jsonl")
        reproduced = z.read("reproduced-transfer.jsonl")
        rep = json.loads(z.read("reproduction.json"))
        assert prev == reproduced and digest(reproduced) == rep["original_prediction_sha"] == rep["reproduced_prediction_sha"]
        prior_manifest = json.loads(p.read("manifest.json"))
        assert rep["adapter_sha"] == prior_manifest["candidate_files_sha"]["adapter_model.safetensors"]
        source = json.loads(z.read("result.json"))
        for arm in ("control","shared","new_only","replay"):
            arms[arm] = {}
            for key,rows in (("old",old),("new",new)):
                pred = json.loads(z.read(f"{arm}-{key}.json"))
                sc = score(rows,pred)
                if arm == "control" and key == "new":
                    try:
                        score(rows,pred+pred[:1])
                    except AssertionError:
                        pass
                    else:
                        raise AssertionError("duplicated prediction admitted")
                raw = source["scores"][arm][key]
                expected = ({k:{label:raw[k][label] for label in ("correct","both_pairs")} for k in sc}
                            if key=="old" else {"new":{label:raw[label] for label in ("correct","both_pairs")}})
                assert sc == expected
                arms[arm][key] = sc if key=="old" else sc["new"]
        for a in ("shared","new_only","replay"):
            delta = {q:{k:v[q]-arms["control"]["old"][k][q] for k,v in arms[a]["old"].items()}
                     for q in ("correct","both_pairs")}
            assert delta["correct"] == source["retention"][a]["old_correct_delta"]
            assert delta["both_pairs"] == source["retention"][a]["old_pair_delta"]
            passed = min(delta["correct"].values())>=0 and min(delta["both_pairs"].values())>=0 and arms[a]["new"]["correct"]>=61 and arms[a]["new"]["both_pairs"]>=29
            assert passed == source["retention"][a]["exploratory_pass"]
    print(json.dumps(dict(arms=arms,reproduction_prediction_sha=rep["reproduced_prediction_sha"],
                          archive_sha256=PIN,source_run_seconds=source["seconds"],
                          seconds=perf_counter()-start),indent=2))


if __name__ == "__main__":
    main()
