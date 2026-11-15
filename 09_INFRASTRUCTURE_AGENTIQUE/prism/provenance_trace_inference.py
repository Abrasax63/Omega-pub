"""Conservative trace-level provenance inference.

Input consists of raw, line-oriented, *synthetic* execution traces. Only
explicit COPY src -> dst records constitute observed lineage. Shared hashes,
timestamps, and job/run IDs are insufficient for causal independence.
"""
import re

COPY = re.compile(r"^COPY\s+([A-Za-z0-9_.-]+)\s+->\s+([A-Za-z0-9_.-]+)$")


def infer_from_trace(raw):
    if not isinstance(raw, str):
        raise TypeError("raw trace must be text")
    relations, errors = [], []
    for line_number, line in enumerate(raw.splitlines(), 1):
        line = line.strip()
        if not line.startswith("COPY "):
            continue
        match = COPY.fullmatch(line)
        if not match:
            errors.append({"line": line_number, "reason": "malformed_copy"})
            continue
        src, dst = match.groups()
        if src == dst:
            errors.append({"line": line_number, "reason": "self_copy"})
            continue
        relations.append({"from": src, "to": dst, "kind": "observed_copy",
                          "line": line_number, "status": "trace_observation"})
    return {"relations": relations, "errors": errors,
            "scientific_certification": False,
            "causal_independence": "indéterminé"}


def evaluate_blind_traces(cases):
    """Case oracle is accessed only after inference; report case-wise metrics."""
    results = []
    for case in cases:
        prediction = infer_from_trace(case["raw"])
        actual = {(r["from"], r["to"]) for r in prediction["relations"]}
        expected = set(map(tuple, case["oracle"]))
        results.append({"case_id": case["id"], "true_positive": len(actual & expected),
                        "false_positive": len(actual - expected),
                        "false_negative": len(expected - actual),
                        "abstained": not actual, "trace_errors": len(prediction["errors"])})
    return {"kind": "synthetic_trace_holdout", "results": results,
            "totals": {key: sum(row[key] for row in results)
                       for key in ("true_positive", "false_positive", "false_negative")},
            "real_world_generalization": "indéterminé"}
