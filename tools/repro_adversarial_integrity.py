"""Adversarial integrity gate for an experimental local scientific cache.

Checks actual bytes for declared input/dependency files and cached result.
Does NOT authenticate the original scientific review; authorization must be
established separately. No automatic reuse or scheduler integration.
"""
import hashlib
from pathlib import Path
from tools.repro_targeted_gate import snapshot


def _hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def capture(script, inputs, dependencies, result_path):
    """Capture a sealed snapshot; caller must keep this record trusted."""
    return {
        "environment": snapshot(script),
        "inputs": {str(Path(p).resolve()): _hash(p) for p in inputs},
        "dependencies": {str(Path(p).resolve()): _hash(p) for p in dependencies},
        "result_path": str(Path(result_path).resolve()),
        "result_sha256": _hash(result_path),
    }


def check(saved, script, inputs, dependencies, result_path):
    """Fail closed for missing, added, or mutated files, including cache output."""
    try:
        current = capture(script, inputs, dependencies, result_path)
        if set(saved) != set(current):
            return False
        return saved == current
    except (OSError, ValueError, TypeError, KeyError):
        return False
