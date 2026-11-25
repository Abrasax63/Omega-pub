"""Rescore HYBRID05 routing and exact outputs from sealed archives."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

FILES = {
    "arm0.zip": "688a4597ee2943f76f257bf06b993d63e5264e08d64577b2d37fbd74811ff178",
    "hybrid-labels.zip": "e59081b0b8855498588d606e37b5aea5500ce6a9d365fd0def325c54023abcb4",
    "hybrid-predictions.zip": "c996350809c07401ba64f328569a3131663630bfe7e88b48d5fcad0c91d2e4a1",
}


def digest(data):
    return sha256(data).hexdigest()


def read(path, name=None):
    with ZipFile(path) as archive:
        return archive.read(name or archive.namelist()[0])


def inspect(records, by_id, revision):
    seen = set()
    confusion = defaultdict(Counter)
    measured = Counter()
    exact = Counter()
    tokens = defaultdict(Counter)
    for r in records:
        ident = r["id"]
        label = by_id[ident]
        kind = label["kind"]
        assert ident not in seen and r["revision"] == revision
        assert digest(label["user"].encode()) == r["user_sha"]
        seen.add(ident)
        raw = r["router"]["raw"].strip().removesuffix(".").lower()
        predicted = raw if raw in {"copy", "reverse", "select", "membership", "unknown"} else "invalid"
        confusion[kind][predicted] += 1
        measured["rule_correct"] += r["route"] == kind
        measured["neural_correct"] += predicted == kind
        if kind == "unknown":
            assert r["direct"] is None and r["adapted"] is None and r["exact"] is None
            measured["rule_abstentions_unknown"] += r["route"] == "unknown"
        else:
            exact[kind] += r["exact"] == label["gold"]
        for arm in ("router", "direct", "adapted"):
            v = r[arm]
            if v is not None:
                assert v["raw_sha"] == digest(v["raw"].encode())
                tokens[arm].update({k: v[k] for k in ("input_tokens", "output_tokens", "seconds")})
    assert seen == by_id.keys()
    return dict(confusion=confusion, counts=measured, exact=exact, cost=tokens)


def main():
    start = perf_counter()
    for file, expected in FILES.items():
        assert digest(Path(file).read_bytes()) == expected
    archived = json.loads(read("arm0.zip"))
    label_bytes = read("hybrid-labels.zip", "labels.json")
    pred_bytes = read("hybrid-predictions.zip")
    manifest = json.loads(read("hybrid-labels.zip", "manifest.json"))
    assert digest(label_bytes) == archived["labels_sha"] == manifest["labels_sha"]
    assert digest(pred_bytes) == archived["prediction_sha"]
    labels = json.loads(label_bytes)
    assert Counter(r["kind"] for r in labels) == dict.fromkeys(("copy","reverse","select","membership","unknown"), 32)
    by_id = {r["id"]: r for r in labels}
    assert len(labels) == len(by_id) == 160
    records = [json.loads(line) for line in pred_bytes.splitlines()]
    result = inspect(records, by_id, manifest["revision"])
    try:
        inspect(records + records[:1], by_id, manifest["revision"])
    except AssertionError:
        pass
    else:
        raise AssertionError("duplicated prediction accepted")
    assert result["confusion"] == archived["neural_router_confusion"]
    assert result["counts"]["rule_correct"] == archived["rule_router_correct"]
    assert result["counts"]["rule_abstentions_unknown"] == archived["rule_abstention"]
    assert result["exact"] == {k: v["exact"]["correct"] for k, v in archived["scores"].items() if v}
    print(json.dumps(dict(**result, archive_sha256=FILES, audit_seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
