"""Controlled A/B evaluation for the existing Omega planner.

The cases are synthetic and intentionally contain an independently specified
oracle. This measures declared-relation extraction, not discovery of unknown
causal lineage. No model calls, external writes, or scientific certification.
"""
from planner import plan_mission
from provenance_tool_runner import run_selected_provenance_tool


CASES = (
    {"id": "declared", "dossier": {"evidence": [
        {"id": "raw"}, {"id": "processed", "derived_from": ["raw"]},
    ]}, "expected": {("raw", "processed", "declared_dependency")}},
    {"id": "same-hash", "dossier": {"evidence": [
        {"id": "a", "sha256": "x"}, {"id": "b", "sha256": "x"},
    ]}, "expected": {("a", "b", "same_content_digest")}},
    {"id": "missing-parent", "dossier": {"evidence": [
        {"id": "orphan", "derived_from": ["absent"]},
    ]}, "expected": set()},
)


def relation_keys(outcome):
    if not outcome.get("tool_executed"):
        return set()
    keys = set()
    for row in outcome["result"]["relations"]:
        if row["kind"] == "declared_dependency":
            keys.add((row["from"], row["to"], row["kind"]))
        elif row["kind"] == "same_content_digest":
            members = row["members"]
            if len(members) == 2:
                keys.add((members[0], members[1], row["kind"]))
    return keys


def evaluate(cases=CASES):
    report = {}
    for enabled in (False, True):
        tp = fp = fn = abstentions = 0
        cases_seen = []
        for case in cases:
            plan = plan_mission({"question": "Audit provenance " + case["id"],
                                 "mission_type": "documentary",
                                 "requires_provenance": enabled})
            outcome = run_selected_provenance_tool(plan, case["dossier"])
            actual = relation_keys(outcome)
            expected = case["expected"]
            tp += len(actual & expected)
            fp += len(actual - expected)
            fn += len(expected - actual)
            abstentions += int(not outcome.get("tool_executed") or
                               outcome.get("result", {}).get("status") == "indéterminé")
            cases_seen.append({"case": case["id"], "predicted": len(actual),
                               "true_positive": len(actual & expected),
                               "false_positive": len(actual - expected)})
        report["B_tool" if enabled else "A_baseline"] = {
            "true_positive": tp, "false_positive": fp, "false_negative": fn,
            "abstention_cases": abstentions, "cases": cases_seen,
        }
    return {"evaluation_kind": "synthetic_declared_relations_only",
            "scientific_discovery_demonstrated": False,
            "results": report}


if __name__ == "__main__":
    import json
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))
