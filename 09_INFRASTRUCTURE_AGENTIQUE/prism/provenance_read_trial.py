"""Compare raw-log routing with two fixed read orders on controlled CI jobs."""

import json
from pathlib import Path
import sys

from provenance_selection import Piece, select_verdict
from provenance_xtrace import extract, fixed_verdict


def compare(root):
    rows = {}
    for job in ("copy", "compute", "hidden"):
        folder = root / job
        output = "output.txt"
        pieces = [
            Piece("digest.txt", "digest", job, output),
            Piece("execution.txt", "execution", job, output),
        ]

        def read(name):
            if name != "execution.txt":
                (folder / name).read_text()
                return None
            trace = extract((folder / name).read_text(), output)
            return dict(job=job, output=output, complete=trace["complete"],
                        success=True, operation=fixed_verdict(trace))

        verdicts = {
            "omega": select_verdict(pieces, read, job=job, output=output, budget=2),
        }
        for name, order in (("fixed_digest_first", pieces), ("fixed_trace_first", pieces[::-1])):
            reads = []
            for piece in order:
                reads.append(piece.name)
                record = read(piece.name)
                if record is not None:
                    break
            verdicts[name] = {"verdict": record["operation"], "pieces_lues": reads}
        rows[job] = verdicts
    return rows


if __name__ == "__main__":
    print(json.dumps(compare(Path(sys.argv[1])), ensure_ascii=False, indent=2))
