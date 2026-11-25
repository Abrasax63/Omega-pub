"""Independently replay archived RELIABILITY02 scores. No model calls."""
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

PIN = "c89bee90d9f811437d9735454613c35b4a3c4dc8"
DIGESTS = {
    "rel0.zip": "00631e907c9b29fd3a5469442a83e00d8fdd95a276229155afef88158ee82d92",
    "rel1.zip": "4dfdeca5f5db509239bdc8cec0dd90f2eb52bedaf9c8d305574e974957f42790",
    "rel2.zip": "d4c52ddb006df177164c63a8746f919553b167f864e996ccf301283b904e0214",
    "run2.zip": "47e389a3274953a4fa98a05876c563436fba8668df49e14839cadbf67547d50b",
}
ARMS = ("original", "minimal")
KINDS = ("copy", "membership", "reverse", "select")
WORDS = set("acorn bread cloud dance elm frost glove honey ink jar key leaf moss needle ocean plum quartz rose shell trout urn vase wind yarn".split())


def digest(blob):
    return sha256(blob).hexdigest()


def archive_member(path, member):
    with ZipFile(path) as archive:
        return archive.read(member)


def answer(row):
    items = row["items"]
    return {
        "copy": lambda: f"{items[0]} {items[1]}",
        "reverse": lambda: f"{items[1]} {items[0]}",
        "select": lambda: items[row["pos"] - 1],
        "membership": lambda: "Yes" if row["target"] in set(items) else "No",
    }[row["kind"]]()


def normalize(raw, kind):
    value = raw.strip().removesuffix(".")
    if kind == "membership":
        return value if value in {"Yes", "No"} else None
    pieces = value.split(" ")
    count = 1 if kind == "select" else 2
    return value if len(pieces) == count and set(pieces) <= WORDS else None


def inspect_trace(records, questions):
    seen = {}
    for rec in records:
        key = rec["id"], rec["arm"]
        assert key not in seen and key in questions and rec["revision"] == PIN
        assert digest(questions[key].encode()) == rec["prompt_sha"]
        assert digest(rec["raw"].encode()) == rec["raw_sha"]
        assert 0 < rec["input_tokens"] <= 368 and 0 <= rec["output_tokens"] <= 16
        seen[key] = rec
    assert seen.keys() == questions.keys()
    return seen


def main():
    start = perf_counter()
    for path, expected in DIGESTS.items():
        assert digest(Path(path).read_bytes()) == expected
    raw_labels = archive_member("rel0.zip", "labels.json")
    raw_questions = archive_member("rel1.zip", "questions.json")
    raw_predictions = archive_member("rel2.zip", "reliability-predictions.jsonl")
    manifest = json.loads(archive_member("rel1.zip", "manifest.json"))
    assert manifest == json.loads(archive_member("rel0.zip", "manifest.json"))
    assert manifest["labels_sha"] == digest(raw_labels)
    assert manifest["questions_sha"] == digest(raw_questions)
    assert manifest["revision"] == PIN
    archived = json.loads(archive_member("run2.zip", "reliability-result.json"))
    assert archived["prediction_sha"] == digest(raw_predictions)
    labels = json.loads(raw_labels)
    questions = {(q["id"], q["arm"]): q["prompt"] for q in json.loads(raw_questions)}
    assert len(questions) == len(set(questions.values())) == 512
    assert questions == {(r["id"], arm): r["prompts"][arm] for r in labels for arm in ARMS}
    assert len({r["id"] for r in labels}) == 256
    assert Counter(r["kind"] for r in labels) == dict.fromkeys(KINDS, 64)
    assert all(answer(r) == r["gold"] for r in labels)

    pairs = defaultdict(list)
    for row in labels:
        if row["kind"] == "membership":
            pairs[row["pair"]].append(row)
    assert len(pairs) == 32
    for pair in pairs.values():
        neg, pos = sorted(pair, key=answer)
        assert [answer(neg), answer(pos)] == ["No", "Yes"]
        assert neg["target"] == pos["target"]
        assert sum(a != b for a, b in zip(neg["items"], pos["items"], strict=True)) == 1

    records = [json.loads(x) for x in raw_predictions.splitlines()]
    seen = inspect_trace(records, questions)
    for defective in (records[:-1], records + records[:1]):
        try:
            inspect_trace(defective, questions)
        except AssertionError:
            continue
        raise AssertionError("bad trace admitted")

    stats = {}
    for arm in ARMS:
        stats[arm] = {}
        for kind in KINDS:
            rows = [r for r in labels if r["kind"] == kind]
            raw = {r["id"]: seen[r["id"], arm]["raw"].strip() for r in rows}
            canon = {i: normalize(value, kind) for i, value in raw.items()}
            n = sum(canon[r["id"]] == answer(r) for r in rows)
            strict = sum(raw[r["id"]] == answer(r) for r in rows)
            valid = sum(x is not None for x in canon.values())
            d = dict(strict=strict, normalized=n, format_valid=valid,
                     format_only_rescued=n-strict, wrong_valid=valid-n, invalid=64-valid)
            if kind == "membership":
                d.update(both_pairs=sum(all(canon[r["id"]] == answer(r) for r in pair)
                                        for pair in pairs.values()))
                for value in ("Yes", "No"):
                    d[f"{value.lower()}_correct"] = sum(canon[r["id"]] == answer(r) == value for r in rows)
            assert all(archived["scores"][arm][kind][k] == v for k, v in d.items())
            stats[arm][kind] = d
    tokens = {k: sum(r[k] for r in records) for k in ("input_tokens", "output_tokens")}
    assert all(archived[k] == v for k, v in tokens.items())
    print(json.dumps(dict(scores=stats, generations=len(records), tokens=tokens,
                          historical_inference_seconds=archived["seconds"], local_seconds=perf_counter()-start,
                          archive_sha256=DIGESTS), indent=2))


if __name__ == "__main__":
    main()
