"""Recalculate RETENTION17 budget deltas and inspect archived pair schedules."""
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from zipfile import ZipFile

DIGEST = "4ed255ebb09080af1cd50c451a6886089de162b8ae62477b0073a5b1cf691491"


def validate(pairs):
    assert len(pairs) == 64 and all(len(p) == 2 and p[0] != p[1] for p in pairs)
    counts = Counter(tuple(p) for p in pairs)
    assert len(counts) == 64
    return counts


def main():
    start = perf_counter()
    file = Path("part1.zip")
    assert sha256(file.read_bytes()).hexdigest() == DIGEST
    with ZipFile(file) as archive:
        data = json.loads(archive.read("retention17.json"))
    ref = validate(data["plans"]["new_only"])
    cand = validate(data["plans"]["replay"])
    try:
        validate(data["plans"]["replay"][:-1] + data["plans"]["replay"][:1])
    except AssertionError:
        pass
    else:
        raise AssertionError("duplicate pair accepted")
    removed = sum((ref-cand).values())
    added = sum((cand-ref).values())
    assert removed == added == data["replay_pairs"]
    assert added / len(ref) == data["replay_fraction"]
    spread = {}
    for key, ref_tokens in data["reference"].items():
        cand_tokens = data["candidate"][key]
        spread[key] = (max(ref_tokens, cand_tokens)-min(ref_tokens, cand_tokens)) / min(ref_tokens, cand_tokens)
        assert abs(spread[key] - data["relative_spread"][key]) < 1e-12
    print(json.dumps(dict(reference_pairs=len(ref), candidate_pairs=len(cand),
                          removed=removed, added=added, relative_spread=spread,
                          archive_sha256=DIGEST, seconds=perf_counter()-start), indent=2))


if __name__ == "__main__":
    main()
