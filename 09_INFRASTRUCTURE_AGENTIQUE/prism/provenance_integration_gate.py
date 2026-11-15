"""Conservative integration gate for RCE evidence and provenance-lab verdicts.

No network access, no write to scientific records, no certification.
The gate never interprets identical content hashes as independent execution.
"""
from __future__ import annotations

from collections import Counter

UNKNOWN = "indéterminé"


def assess_evidence(dossier: dict) -> dict:
    """Return a traceable decision; refuse to infer independence from text alone."""
    items = dossier.get("evidence", [])
    if not isinstance(items, list) or not items:
        return {"verdict": UNKNOWN, "reason": "missing_evidence", "origins": []}
    if any(not isinstance(item, dict) or not item.get("run_id")
           or not item.get("artifact_id") or not item.get("source_uri")
           for item in items):
        return {"verdict": UNKNOWN, "reason": "unresolved_origin", "origins": []}
    runs = sorted({str(item["run_id"]) for item in items})
    if any(item.get("verified_execution") is not True for item in items):
        return {"verdict": UNKNOWN, "reason": "execution_not_verified", "origins": runs}
    if dossier.get("scientific_status") not in {"DÉMONTRÉ", "CALCUL EXACT", "EXPÉRIMENTAL", "INDÉTERMINÉ"}:
        return {"verdict": UNKNOWN, "reason": "unresolved_scientific_status", "origins": runs}
    if len(runs) < 2:
        return {"verdict": "same_execution", "reason": "single_run_id", "origins": runs}
    # Distinct run IDs are necessary but not sufficient: copied inputs, reruns
    # and shared upstream computations may make executions dependent.
    if not dossier.get("independence_attested"):
        return {"verdict": UNKNOWN, "reason": "independence_not_attested", "origins": runs}
    if not dossier.get("independence_evidence_uri"):
        return {"verdict": UNKNOWN, "reason": "missing_independence_proof", "origins": runs}
    return {"verdict": "distinct_attested_runs", "reason": "attested_not_certified", "origins": runs}
