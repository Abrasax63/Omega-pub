#!/usr/bin/env python3
"""Cross-language, label-independent EQ manifest for OBS-COL-09B.

No target transition table and no observed answer is consulted in
generation. Public evaluation words are inherited without changes.
"""
from __future__ import annotations

import hashlib
import itertools
import random
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "obs_col09"
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
from generate_matched_eval import INPUTS, words as evaluation_words_string

EQ_COUNT = 512
SEED = 20261117


def equivalence_words(alphabet, index):
    alphabet = tuple(alphabet)
    if len(alphabet) < 2 or len(set(alphabet)) != len(alphabet):
        raise ValueError("need at least two distinct input symbols")
    seq = [tuple(word) for length in range(1, 5)
           for word in itertools.product(alphabet, repeat=length)]
    seen = set(seq)
    rng = random.Random(SEED + index)
    while len(seq) < EQ_COUNT:
        length = rng.randint(5, 18)
        candidate = tuple(rng.choice(alphabet) for _ in range(length))
        if candidate not in seen:
            seen.add(candidate)
            seq.append(candidate)
    if len(seq) != len(seen) or len(seq) != EQ_COUNT:
        raise AssertionError("invalid equivalence suite")
    return seq


def encode(words):
    return "".join("\t".join(word) + "\n" for word in words).encode("utf-8")


def manifest_hash(content):
    return hashlib.sha256(content).hexdigest()


def read_words(path, expected):
    raw = Path(path).read_bytes()
    values = [tuple(line.split("\t")) for line in raw.decode("utf-8").splitlines()]
    if values != expected:
        raise AssertionError("EQ manifest did not match committed generation rules")
    return values, manifest_hash(raw)


def generate(output_dir):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    manifests = []
    for index, (name, alphabet) in enumerate(INPUTS):
        eq = equivalence_words(alphabet, index)
        ev = evaluation_words_string(alphabet, index)
        if len(ev) != 256 or len(set(ev)) != 256:
            raise AssertionError("unmatched evaluation manifest")
        eq_path = out / (name + ".eq.words")
        ev_path = out / (name + ".words")
        eq_path.write_bytes(encode(eq))
        ev_path.write_bytes(encode(ev))
        manifests.append({
            "fixture": name, "eq_count": len(eq), "eval_count": len(ev),
            "eq_sha256": manifest_hash(encode(eq)),
            "evaluation_sha256": manifest_hash(encode(ev)),
            "eval_eq_fullword_overlap": len(set(eq) & set(ev)),
        })
    return manifests


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: generate_manifests.py <directory>")
    from pprint import pprint
    pprint(generate(sys.argv[1]))


if __name__ == "__main__":
    main()
