"""Compare identical xtrace and final bytes with different last writers."""
import json
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import sys

from audit_destination_evidence import corroborate, observe
from provenance_cycle import metrics, predict
from provenance_lab import read_program
from provenance_offline import read_cases


def generate(root):
    rows = []
    for name, output, redirect, expected in (
        ("positive", "output", "other", "copie"),
        ("contradiction", "output", "output", "indéterminé"),
        ("distinct", "second-output", "other", "copie"),
    ):
        work = root / name
        work.mkdir()
        (work / "source").write_bytes(b"omega\n")
        script = 'cp source "$1"\nprintf "%s\\n" omega > "$2"\n'
        process = subprocess.run(
            ["bash", "--noprofile", "--norc", "-ex", "-c", script, "fixture", output, redirect],
            cwd=work, env={"PATH": os.defpath, "LC_ALL": "C"},
            capture_output=True, check=True,
        )
        assert (work / output).read_bytes() == b"omega\n"
        assert (work / redirect).read_bytes() == b"omega\n"
        path = root / f"{name}.log"
        path.write_bytes(process.stderr)
        rows.append(dict(journal=path.name, output=output, source=name,
                         expected=expected, truth_source="controlled script redirection",
                         format="bash-step", successful_errexit_step=True,
                         sha256=sha256(process.stderr).hexdigest()))
    assert rows[0]["sha256"] == rows[1]["sha256"]
    (root / "reserved.json").write_text(json.dumps(rows, indent=2) + "\n")


def evaluate(root):
    manifest = root / "reserved.json"
    rows = json.loads(manifest.read_text())
    cases, _ = read_cases(manifest)
    baseline = read_program(root / "base.json")
    proposal = json.loads((root / "proposal.json").read_text())["proposal"]
    reports = observe(root, rows)
    assert all(report["content_matches"] for report in reports.values())
    verdicts = [
        corroborate(predict(case, baseline, proposal), row["source"],
                    row["output"], reports[row["source"]])
        for case, row in zip(cases, rows, strict=True)
    ]
    result = metrics([case["expected"] for case in cases], verdicts)
    assert result == dict(correct_confirmations=2, false_confirmations=1, abstentions=0)
    print(result)


if __name__ == "__main__":
    {"generate": generate, "evaluate": evaluate}[sys.argv[1]](Path(sys.argv[2]))
