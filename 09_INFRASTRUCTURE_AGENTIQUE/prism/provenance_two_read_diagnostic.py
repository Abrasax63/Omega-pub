import json, sys
from pathlib import Path
from provenance_selection import Piece, select_verdict
from provenance_xtrace import extract, extract_buildkit_copy, fixed_verdict

UNKNOWN = "indéterminé"
for case in json.loads(Path(sys.argv[1]).read_text()):
    job, output = str(case["job"]), case["output"]
    pieces = [Piece("inventory", "inventory", job, output),
              Piece("journal", "execution", job, output),
              Piece("script", "script", job, output)]

    def read(name):
        raw = Path(case[name]).read_text()
        if name != "journal":
            return None
        labels = {fixed_verdict(extractor(raw, output))
                  for extractor in (extract, extract_buildkit_copy)} - {UNKNOWN}
        result = next(iter(labels)) if len(labels) == 1 else UNKNOWN
        return dict(job=job, output=output, complete=result != UNKNOWN,
                    success=True, operation=result)

    omega = select_verdict(pieces, read, job=job, output=output, budget=2)
    order = ["journal"]
    fixed = read("journal")["operation"]
    if fixed == UNKNOWN and case.get("script"):
        read("script")
        order.append("script")
    print(json.dumps({"job":job,"omega":omega,"fixed":fixed,"fixed_reads":order},ensure_ascii=False))
