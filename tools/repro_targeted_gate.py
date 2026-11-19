"""Cheap same-environment cache gate, not a semantic equivalence checker.

Requires a trusted prior review. Any change to source or declared dependency
versions fails closed. This never validates a changed dependency by itself.
"""
import hashlib
import importlib.metadata
import sys
from pathlib import Path


def snapshot(script):
    script = Path(script)
    return {
        "source_sha256": hashlib.sha256(script.read_bytes()).hexdigest(),
        "python": sys.version.split()[0],
        "sympy": importlib.metadata.version("sympy"),
        "mpmath": importlib.metadata.version("mpmath"),
    }


def eligible_for_reuse(saved, current, reviewed):
    return reviewed is True and saved == current and isinstance(current, dict) and set(current) == {
        "source_sha256", "python", "sympy", "mpmath"
    }
