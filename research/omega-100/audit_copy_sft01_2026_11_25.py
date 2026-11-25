"""Recalculate COPY-SFT01 scores from original ZIPs; print aggregates only."""
import hashlib
import json
from pathlib import Path
import sys
from time import perf_counter
from zipfile import ZipFile

DIGESTS = {
    "train": "fe7b9bb4459b72d42f43dbbbec44c70fa7407f013b76007978b03685b4d96580",
    "test": "766618651007bc3c9dacdab9023fe7fd6762c7ac32b22fdac7285e3723cf4bfe",
    "eval": "686f06d8f01591cecc367efe5bcda7080184f85083c28728f2f304e9c32b5762",
    "adapter": "65b32d1b334e20054f4760a5a54d232795ca3362c58d28c49a971af089e06097",
    "replication": "0ebc596866a09250dd437ad13ba7c25eeb8c9c764e4351ef30ab7f916e1623b4",
    "position": "5fb74c58717e2f9fadbbcbb264340638dff193db448c9d6a752c228bd285d08f",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read(name, member):
    with ZipFile(Path(sys.argv[1]) / (name + ".zip")) as archive:
        return archive.read(member)


def score(name, rows, views, target, group, positional=False):
    reported = json.loads(read(name, "result.json"))["scores"]
    by_id = {(row["view"] if positional else None, row["id"]): row for row in rows}
    assert len(by_id) == len(rows)
    predictions = [json.loads(line) for line in read(name, "predictions.jsonl").splitlines()]
    expected = {
        (arm, view, row["id"])
        for arm in ("base", "lora")
        for view in views
        for row in rows
        if not positional or row["view"] == view
    }
    assert len(predictions) == len(expected)
    assert {(p["arm"], p["view"], p["id"]) for p in predictions} == expected
    scores = {}
    for pred in predictions:
        arm, view = pred["arm"], pred["view"]
        row = by_id[(view if positional else None, pred["id"])]
        key = group(row) if not positional else view
        cell = scores.setdefault(arm, {}).setdefault(view, {}).setdefault(
            key, {"n": 0, "exact": 0, "strict": 0, "input_tokens": 0, "output_tokens": 0, "seconds": 0}
        )
        cell["n"] += 1
        cell["exact"] += pred["raw"].strip() == row[target]
        cell["strict"] += pred["raw"] == row[target]
        for field in ("input_tokens", "output_tokens", "seconds"):
            cell[field] += pred[field]
    for arm, view_scores in scores.items():
        for view, cells in view_scores.items():
            for key, cell in cells.items():
                stored = reported[arm][view] if positional else reported[arm][view][key]
                for field in ("n", "exact", "input_tokens", "output_tokens"):
                    assert cell[field] == stored[field], (name, arm, view, key, field)
                if "strict" in stored:
                    assert cell["strict"] == stored["strict"]
    return scores


def total(scores, arm, view=None):
    return sum(cell["exact"] for name, cells in scores[arm].items()
               if view is None or name == view for cell in cells.values())


start = perf_counter()
for name, sha in DIGESTS.items():
    assert digest((Path(sys.argv[1]) / (name + ".zip")).read_bytes()) == sha
train_bytes, test_bytes = read("train", "data.json"), read("test", "data.json")
train, test = json.loads(train_bytes), json.loads(test_bytes)
first = json.loads(read("eval", "result.json"))
assert digest(train_bytes) == first["train_sha256"]
assert digest(test_bytes) == first["test_sha256"]
assert all(row["label"] == row["packet"] for row in train + test)
manifest = json.loads(read("adapter", "manifest.json"))
for asset, sha in manifest["adapter_sha256"].items():
    assert digest(read("adapter", "adapter/" + asset)) == sha
steps = read("adapter", "steps.jsonl")
assert digest(steps) == manifest["steps_sha256"]
assert len(steps.splitlines()) == manifest["steps"] == first["training_steps"] == 256
first_scores = score("eval", test, ("trained", "paraphrase"), "label", lambda row: row["group"])
rep_bytes = read("replication", "corpus.json")
rep_data = json.loads(rep_bytes)
rep = json.loads(read("replication", "result.json"))
assert digest(rep_bytes) == rep["corpus_sha256"]
train_set, test_set, rep_set = ({r["packet"] for r in train}, {r["packet"] for r in test},
                                {r["seq"] for r in rep_data})
assert len(train_set) == len(train) == 128
assert len(test_set) == len(test) == 144
assert len(rep_set) == len(rep_data) == 64
assert not (train_set & test_set or train_set & rep_set or test_set & rep_set)
rep_scores = score("replication", rep_data, ("brackets", "verbatim"), "seq", lambda row: row["group"])
id_gain = first_scores["lora"]["trained"]["id"]["exact"] - first_scores["base"]["trained"]["id"]["exact"]
first_gate = id_gain >= 8 and all(
    cells["id"]["exact"] >= 61 and cells["length"]["exact"] >= 30
    and cells["alphabet"]["exact"] >= 30
    and cells["singleton"]["exact"] >= first_scores["base"][view]["singleton"]["exact"] - 1
    for view, cells in first_scores["lora"].items()
)
assert first_gate == first["exploratory_gate"] is True
rep_gain = total(rep_scores, "lora") - total(rep_scores, "base")
rep_gate = rep_gain >= 8 and all(
    total(rep_scores, "lora", view) >= 61
    and all(c["exact"] >= 15 and c["exact"] >= rep_scores["base"][view][g]["exact"] - 1
            for g, c in cells.items())
    for view, cells in rep_scores["lora"].items()
)
assert rep_gate == rep["replication_gate"] is False
pos_bytes = read("position", "corpus.json")
assert digest(pos_bytes) == json.loads(read("position", "result.json"))["corpus_sha256"]
pos_scores = score("position", json.loads(pos_bytes), ("copy", "indexed", "spaced"),
                   "gold", None, positional=True)
print(json.dumps({
    "archive_sha256": DIGESTS, "identical_sequences_across_partitions": 0,
    "partition_sizes": [len(train), len(test), len(rep_data)],
    "training": {k: manifest[k] for k in ("model", "revision", "seed", "steps", "weight_delta_L2",
                                          "trainable_parameters", "token_exposures",
                                          "supervised_token_exposures", "seconds")},
    "initial": {"scores": first_scores, "gate": first_gate, "id_gain": id_gain},
    "replication": {"scores": rep_scores, "gate": rep_gate, "gain": rep_gain},
    "position": pos_scores, "audit_seconds": round(perf_counter() - start, 5),
}, indent=2))
