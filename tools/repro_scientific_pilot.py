"""Pilot: execute an existing Omega-pub scientific script with pinned inputs.

No production scheduler integration. Never certifies mathematical truth.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from tools.repro_history_pilot import record_run, find_reusable


def run_pinned_script(repository_root, script_relative_path, history_dir,
                      reviewer="independent-review-required", timeout=30):
    root = Path(repository_root).resolve()
    script = (root / script_relative_path).resolve()
    if not script.is_relative_to(root) or not script.is_file() or script.suffix != ".py":
        raise ValueError("script must be an existing Python file within repository")
    source = script.read_bytes()
    manifest = {
        "schema_version": 1,
        "result_id": "omega-script:" + script.relative_to(root).as_posix(),
        "code_sha256": hashlib.sha256(source).hexdigest(),
        "data_sha256": hashlib.sha256(b"no-external-inputs-declared").hexdigest(),
        "parameters": {"argv": []},
        "dependencies": {"python": sys.version.split()[0],
                         "sympy": _sympy_version()},
        "execution": {"command": [sys.executable, str(script)], "cwd": str(root),
                      "timeout_seconds": timeout},
    }
    # Never treat a pending record as a scientific cache hit.
    process = subprocess.run([sys.executable, str(script)], cwd=root,
                             capture_output=True, text=True, timeout=timeout,
                             check=False)
    result = {"returncode": process.returncode, "stdout": process.stdout,
              "stderr": process.stderr}
    path = record_run(history_dir, manifest, result, reviewer)
    return path, manifest, result


def _sympy_version():
    try:
        import sympy
        return sympy.__version__
    except ImportError:
        return "NOT_INSTALLED"
