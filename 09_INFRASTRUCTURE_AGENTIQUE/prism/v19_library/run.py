"""Replay the pinned V19 sources from local Git objects and write a cycle report."""

import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

from verify import search

BRICK = "OBS-V19-LOCAL-L2"
EXPECTED = {3: 12, 4: 456, 5: 12280, 6: 312720}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Choose a new output path.")
    refs = json.loads(Path(__file__).with_name("sources.json").read_text())
    files, sources = {}, {}
    root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
    for label, (commit, path) in refs.items():
        files[label] = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=root)
        sources[label] = {"commit": commit, "path": path, "sha256": sha256(files[label]).hexdigest()}
    index_path = refs["index"][1]
    card_path = refs["card"][1]
    if (any(f"- `{path}`".encode() not in files["inventory"] for path in (index_path, card_path))
            or f"| `{BRICK}` |".encode() not in files["index"]
            or not files["card"].startswith(f"# {BRICK} ".encode())
            or "RECONSTITUTION".encode() not in files["card"]):
        raise SystemExit("The inventory, index and reconstructed card do not match.")

    with TemporaryDirectory() as directory:
        script = Path(directory) / "historical.py"
        script.write_bytes(files["historical_script"])
        run = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=120)
        spec = importlib.util.spec_from_file_location("historical", script)
        historical = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(historical)
        counts, witness, difference = search(historical)

    reproduced = run.returncode == 0 and "GLOBAL_LOCAL_COMPARISONS_TOTAL: 325468" in run.stdout
    verified = witness is None and counts == EXPECTED
    record = {
        "brick": BRICK,
        "sources": sources,
        "historical_status": "DÉMONTRÉ (SQLite, fiche reconstituée)",
        "historical_replay": {
            "python": sys.version.split()[0], "exit_code": run.returncode,
            "stdout": run.stdout, "stderr": run.stderr, "reproduced": reproduced,
        },
        "full_extension_check": {
            "scope": "N <= 6, q >= 3, L in {2,3}, coherent forced constraints",
            "comparisons": counts, "verified_equal_in_scope": verified,
            "locality_counterexample": witness,
            "historical_shadow_discrepancy": difference,
        },
        "general_L_plus_1": "RÉFUTÉ" if witness else "INDÉTERMINÉ — preuve candidate à relire",
    }
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(record, output, ensure_ascii=False, indent=2)
        output.write("\n")
    return 0 if verified and reproduced else 1


if __name__ == "__main__":
    sys.exit(main())
