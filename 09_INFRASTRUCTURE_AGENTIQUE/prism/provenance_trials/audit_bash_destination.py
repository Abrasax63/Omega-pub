"""Demonstrate that a Bash cp trace does not establish destination type."""
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys


def generate(root, mode):
    cases = {
        "train": (("train-file", "training-output", False),),
        "reserved": (
            ("positive", "output", False),
            ("contradiction", "output", True),
            ("distinct-positive", "second-output", False),
        ),
    }
    rows = []
    for name, target, directory in cases[mode]:
        work = root / name
        work.mkdir()
        source = work / "source"
        payload = b"Omega controlled provenance test\n"
        source.write_bytes(payload)
        destination = work / target
        if directory:
            destination.mkdir()
        process = subprocess.run(
            ["bash", "--noprofile", "--norc", "-ex", "-c", 'cp source "$1"', "fixture", target],
            cwd=work, env={"PATH": os.defpath, "LC_ALL": "C"},
            capture_output=True, check=True,
        )
        output = destination / source.name if directory else destination
        assert output.is_file() and output.read_bytes() == payload
        assert destination.is_dir() == directory
        log = f"{name}.log"
        (root / log).write_bytes(process.stderr)
        rows.append({
            "journal": log, "output": target, "source": name,
            "truth_source": "controlled fixture and filesystem check",
            "expected": "indéterminé" if directory else "copie",
            "format": "bash-step", "successful_errexit_step": True,
            "sha256": sha256(process.stderr).hexdigest(),
        })
    if mode == "reserved":
        assert rows[0]["sha256"] == rows[1]["sha256"]
    (root / f"{mode}.json").write_text(json.dumps(rows, indent=2) + "\n")


if __name__ == "__main__":
    generate(Path(sys.argv[1]), sys.argv[2])
