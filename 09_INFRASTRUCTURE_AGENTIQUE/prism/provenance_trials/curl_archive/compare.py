"""Replay the three public diagnostic logs from an input JSON manifest."""
import json
from pathlib import Path
import re
import sys

from provenance_archive import archive_verdict


def compare(output, log, source):
    reads = 1

    def read_recipe(commit, path):
        nonlocal reads
        reads += 1
        return Path(source).read_bytes() if isinstance(source, str) else source

    conditional = archive_verdict(log, output, read_recipe)
    conditional_reads = reads
    reads = 1
    fixed = archive_verdict(log, output, read_recipe)
    return conditional, fixed, conditional_reads, reads


def main(manifest):
    for case in json.loads(Path(manifest).read_text()):
        log = Path(case["journal"]).read_text()
        output = case["output"]
        recipe = case.get("script")
        variants = {"observé": (output, log, recipe)}
        if recipe:
            variants.update({
                "script contradictoire": (output, log, b"wrong recipe"),
                "destination contradictoire": ("/mirror" + output, log, recipe),
                "empreinte contradictoire": (
                    output,
                    re.sub(r"(?<=-DFROM_HASH=)[0-9a-f]{64}", "0" * 64, log),
                    recipe,
                ),
                "vérification absente": (
                    output, log.replace("-- verifying file... done", ""), recipe,
                ),
            })
        for name, args in variants.items():
            print(case["job"], name, *compare(*args))


if __name__ == "__main__":
    main(sys.argv[1])
