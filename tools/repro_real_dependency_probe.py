"""Trace imports used by Omega's real symbolic script.

Diagnostic only: import tracing is not a complete dependency inventory.
Dynamic files, subprocesses and network reads require separate instrumentation.
"""
import importlib.metadata as metadata
import json
import runpy
import sys
from pathlib import Path
from tools.repro_wallclock_benchmark import SCRIPT


def inspect():
    before = set(sys.modules)
    runpy.run_path(str(SCRIPT), run_name="__main__")
    loaded = set(sys.modules) - before
    imported = sorted({name.split(".")[0] for name in loaded})
    declared = []
    for name in ("sympy", "mpmath"):
        try:
            declared.append({"distribution": name, "version": metadata.version(name),
                             "runtime_import_observed": name in imported})
        except metadata.PackageNotFoundError:
            declared.append({"distribution": name, "missing": True})
    return {"script": str(SCRIPT), "runtime_new_import_roots": imported,
            "distributions_of_interest": declared,
            "scope": "runtime imports in this process only; not full file dependency discovery"}


if __name__ == "__main__":
    print("OMEGA_IMPORT_TRACE=" + json.dumps(inspect(), sort_keys=True))
