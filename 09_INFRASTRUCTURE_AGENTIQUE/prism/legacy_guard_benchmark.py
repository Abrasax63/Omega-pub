"""Exhaustive, independently checked observer-guard comparison.

The 125 cases are a finite *model* with exact, supplied partition probes.
Calling a probe costs one modeled consultation; all policies are initially
given both exact probe models. The cost of computing the guard is *not*
charged, so the experiment does NOT measure total elapsed/tool cost or
general intelligence gain. No model, source authentication or durable memory.
"""
from itertools import product
from legacy_observer_transfer import partitions, common_refinement, refines
from observer_guard_bridge import inspect_observer_evidence


def _relations(labels):
    return frozenset((i, j) for i in range(len(labels))
                     for j in range(len(labels)) if labels[i] == labels[j])


def independent_125():
    """Separate equivalence-relation representation; no legacy functions."""
    rels = sorted(
        {_relations(p) for p in product(range(3), repeat=3)},
        key=lambda s: (len(s), tuple(sorted(s))),
    )
    assert len(rels) == 5
    naive_correct = guard_correct = fixed_correct = 0
    followups = 0
    for p, a, b in product(rels, repeat=3):
        first = p & a
        full = first & b
        naive_correct += int(first == full)
        need_other = first != full
        followups += need_other
        guard_correct += int((first & b if need_other else first) == full)
        fixed_correct += int((first & b) == full)
    return {
        "cases": 125, "naive_correct": naive_correct,
        "guarded_correct": guard_correct, "fixed_both_correct": fixed_correct,
        "guarded_second_probes": followups,
        "naive_probe_calls": 125, "guarded_probe_calls": 125 + followups,
        "fixed_both_probe_calls": 250,
    }


def run_audit():
    pts = partitions(3)
    assert len(pts) == 5
    result = {
        "cases": 0, "naive_correct": 0, "guarded_correct": 0,
        "fixed_both_correct": 0, "guarded_second_probes": 0,
        "naive_probe_calls": 0, "guarded_probe_calls": 0,
        "fixed_both_probe_calls": 0,
    }
    for start, a, b in product(pts, repeat=3):
        result["cases"] += 1
        after_a = common_refinement(start, a)
        full = common_refinement(after_a, b)
        result["naive_correct"] += int(refines(after_a, full))
        result["naive_probe_calls"] += 1

        spec = {
            "termination": {
                "current_partition": list(after_a),
                "selected_probe_partition": list(a),
                "listed_probe_partitions": [list(a), list(b)],
                "declared_exhaustive": True,
            },
        }
        audit = inspect_observer_evidence(spec)
        decision = audit["termination"]
        other_needed = decision["status"] == "underinformative_relative_to_listed_probes"
        result["guarded_second_probes"] += int(other_needed)
        result["guarded_probe_calls"] += 1 + int(other_needed)
        after_guard = common_refinement(after_a, b) if other_needed else after_a
        result["guarded_correct"] += int(refines(after_guard, full))
        result["fixed_both_probe_calls"] += 2
        result["fixed_both_correct"] += int(
            refines(common_refinement(after_a, b), full))
    reference = independent_125()
    if result != reference:
        raise AssertionError({"primary": result, "independent": reference})
    return {
        "status": "EXHAUSTIVE_FINITE_MODEL_NOT_REAL_TASKS",
        "protocol": "125 ordered triples (start,a,b), one first probe a, conditional b",
        "primary": result,
        "independent_equivalence_relations": reference,
        "limits": [
            "all probe models supplied upfront; authenticity not checked",
            "guard computation cost not charged; only modeled probe consultations",
            "fixed two-probe baseline obtains perfect relative closure",
            "model relative, not universal epistemic closure",
            "no model calls, LLM, unknown-source tests or durable-memory changes",
        ],
    }


if __name__ == "__main__":
    import json
    print("LEGACY_GUARD_AUDIT " + json.dumps(run_audit(), ensure_ascii=False,
                                           sort_keys=True))
