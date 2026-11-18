"""Compare exact-path corroboration with a Bash journal alone."""
import json
from hashlib import sha256
from pathlib import Path
import stat
import sys

from provenance_cycle import metrics, predict
from provenance_lab import read_program
from provenance_offline import read_cases
from provenance_xtrace import fixed_verdict


def observe(root, rows):
    reports = {}
    for row in rows:
        work = root / row["source"]
        target = work / row["output"]
        kind = target.lstat().st_mode
        content_matches = (
            stat.S_ISREG(kind)
            and sha256(target.read_bytes()).digest() == sha256((work / "source").read_bytes()).digest()
        )
        reports[row["source"]] = {
            "case": row["source"], "target": row["output"],
            "content_matches": content_matches,
        }
    return reports


def corroborate(verdict, source, target, report):
    if (
        verdict == "copie" and report
        and (report["case"], report["target"]) == (source, target)
        and report["content_matches"]
    ):
        return "copie"
    return "indéterminé"


def main(root):
    manifest = root / "reserved.json"
    rows = json.loads(manifest.read_text())
    cases, _ = read_cases(manifest)
    baseline = read_program(root / "base.json")
    proposal = json.loads((root / "proposal.json").read_text())["proposal"]
    reports = observe(root, rows)
    serialized = json.dumps(reports, sort_keys=True, indent=2) + "\n"
    (root / "side.json").write_text(serialized)
    expected = [case["expected"] for case in cases]
    fixed = [fixed_verdict(case) for case in cases]
    candidate = [predict(case, baseline, proposal) for case in cases]
    corroborated = [
        corroborate(verdict, row["source"], row["output"], reports.get(row["source"]))
        for verdict, row in zip(candidate, rows, strict=True)
    ]
    assert fixed == candidate
    assert corroborated == expected
    assert corroborate("copie", "contradiction", "output", reports["positive"]) == "indéterminé"
    assert corroborate("copie", "positive", "output", None) == "indéterminé"
    print("journal", metrics(expected, candidate))
    print("journal plus filesystem report", metrics(expected, corroborated))
    print("fixed with same corroboration", metrics(expected, [
        corroborate(verdict, row["source"], row["output"], reports.get(row["source"]))
        for verdict, row in zip(fixed, rows, strict=True)
    ]))


if __name__ == "__main__":
    main(Path(sys.argv[1]))
