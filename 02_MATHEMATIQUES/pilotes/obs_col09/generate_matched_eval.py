#!/usr/bin/env python3
"""Generate the EXACT public test sequences also used by the AALpy experiment.

No hidden target graph or measured outputs are consulted. This is a
test-INPUT manifest only; tests are never fed to learning or EQ oracles.
"""
import random
import sys
from pathlib import Path

INPUTS = (
    ("Angluin_Moore.dot", ("a", "b")),
    ("coffee_moore.dot", ("button", "coin")),
    ("mooreModel.dot", ("0", "1")),
)
def words(alphabet, index):
    rng = random.Random(20261116 + index)
    selected = set()
    while len(selected) < 256:
        length = rng.randint(12, 18)
        selected.add(tuple(rng.choice(alphabet) for _ in range(length)))
    return sorted(selected, key=lambda x: (len(x), x))

def main(where):
    where.mkdir(parents=True, exist_ok=True)
    for i, (name, alphabet) in enumerate(INPUTS):
        batch = words(alphabet, i)
        filename = where / (name + ".words")
        filename.write_text("".join("\t".join(w) + "\n" for w in batch),
                            encoding="utf8")
        assert len(batch) == 256 and len(set(batch)) == 256
        print("test input manifest", filename, len(batch))

if __name__ == "__main__":
    main(Path(sys.argv[1]))
