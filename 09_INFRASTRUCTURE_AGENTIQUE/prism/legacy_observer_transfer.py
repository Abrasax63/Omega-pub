#!/usr/bin/env python3
"""Experimental Omega archival transfer: exact finite observer audits.

Provenance: Omega W04 (2026-08-10), W06/I1 (2026-08-12).
The tests are about known, exact partitions, not unknown sources or LLM accuracy.
Neither this module nor its score can certify a scientific claim or a source.
"""
from __future__ import annotations

import argparse
import itertools
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Sequence, Tuple

Partition = Tuple[int, ...]


def canonicalize(labels: Sequence[object]) -> Partition:
    ids = {}
    result = []
    for item in labels:
        if item not in ids:
            ids[item] = len(ids)
        result.append(ids[item])
    return tuple(result)


def partitions(n: int) -> Tuple[Partition, ...]:
    """Restricted-growth strings (all set partitions, each counted once)."""
    if n <= 0:
        raise ValueError("n must be positive")
    def walk(a: Partition, maximum: int):
        if len(a) == n:
            yield a
        else:
            for label in range(maximum + 2):
                yield from walk(a + (label,), max(maximum, label))
    return tuple(walk((0,), 0))


def common_refinement(p: Partition, q: Partition) -> Partition:
    if len(p) != len(q) or not p:
        raise ValueError("partitions must cover the same nonempty space")
    return canonicalize(tuple(zip(p, q)))


def refines(fine: Partition, coarse: Partition) -> bool:
    if len(fine) != len(coarse):
        raise ValueError("incompatible spaces")
    return all(fine[i] != fine[j] or coarse[i] == coarse[j]
               for i in range(len(fine)) for j in range(i + 1, len(fine)))


def block_count(p: Partition) -> int:
    return len(set(p))


@dataclass(frozen=True)
class RepresentationGate:
    decision: str
    current_blocks: int
    target_blocks: int
    joint_blocks: int
    capacity: int
    why: str


def reconfiguration_gate(current: Partition, target: Partition, capacity: int) -> RepresentationGate:
    """The task target is the exact required-answer partition; no learned priors.

    `replace` permits dropping a distinction from the *working representation*;
    it never authorizes deletion of evidence or provenance in durable memory.
    """
    if capacity <= 0 or len(current) != len(target) or not current:
        raise ValueError("invalid task or capacity")
    k, g = block_count(current), block_count(target)
    joint = block_count(common_refinement(current, target))
    if g > capacity:
        decision, why = "infeasible", "The target itself exceeds capacity."
    elif refines(current, target) and k <= capacity:
        decision, why = "keep", "Current representation already supports the new task."
    elif joint <= capacity:
        decision, why = "refine", "The joint refinement fits capacity."
    else:
        decision, why = "replace", "Monotone refinement cannot fit; nonmonotone replacement can."
    return RepresentationGate(decision, k, g, joint, capacity, why)


def terminal_probe_guard(current: Partition, selected: Partition,
                         available: Sequence[Partition]) -> dict:
    """Only a relative closure check against the supplied exact probe models.

    It CANNOT validate probe authenticity, identify unknown probes, or establish
    that the source labels in the observations are correct.
    """
    if not available:
        raise ValueError("at least one exact probe partition is required")
    if any(len(q) != len(current) for q in (*available, selected)):
        raise ValueError("incompatible spaces")
    if common_refinement(current, selected) != canonicalize(current):
        return {"status": "not_terminal", "candidate_probe_indexes": []}
    candidates = [i for i, q in enumerate(available)
                  if common_refinement(current, q) != canonicalize(current)]
    return {"status": "underinformative" if candidates else "closed_relative_to_listed_probes",
            "candidate_probe_indexes": candidates}


def run_closed_world_audit(n: int = 3) -> dict:
    """Exhaustive legacy W04 protocol: 2 probe partitions, 1-probe policies,
    each initial partition. First fixed point stops the policy (no auto-check).
    """
    pts = partitions(n)
    idx = {p: i for i, p in enumerate(pts)}
    totals = {"cases": 0, "terminal_underinformative": 0,
              "nontrivial_cycles": 0, "repaired_with_one_extra_probe": 0,
              "fixed_two_probes_full": 0}
    witness = None
    for a, b in itertools.product(pts, repeat=2):
        full = common_refinement(a, b)
        for policy in itertools.product((0, 1), repeat=len(pts)):
            for start in pts:
                totals["cases"] += 1
                current = start
                visited = set()
                while True:
                    if current in visited:
                        totals["nontrivial_cycles"] += 1
                        raise AssertionError("monotone refinement cannot cycle")
                    visited.add(current)
                    chosen = (a, b)[policy[idx[current]]]
                    next_p = common_refinement(current, chosen)
                    if next_p == current:
                        break
                    current = next_p
                alert = terminal_probe_guard(current, chosen, (a, b))
                is_trap = not refines(current, full)
                if is_trap:
                    totals["terminal_underinformative"] += 1
                    assert alert["status"] == "underinformative"
                    assert len(alert["candidate_probe_indexes"]) == 1
                    other = (a, b)[alert["candidate_probe_indexes"][0]]
                    assert refines(common_refinement(current, other), full)
                    totals["repaired_with_one_extra_probe"] += 1
                    if witness is None:
                        witness = {"probe_a": a, "probe_b": b, "start": start,
                                   "policy": policy, "terminal": current,
                                   "other_probe_index": alert["candidate_probe_indexes"][0]}
                else:
                    assert alert["status"] == "closed_relative_to_listed_probes"
                # Strong fair baseline when both exact probes are known, at cost 2.
                if refines(common_refinement(common_refinement(start, a), b), full):
                    totals["fixed_two_probes_full"] += 1
    return {"scope": "public exhaustive finite model, not model/LLM validation",
            "n": n, "probe_count": 2, "partitions": len(pts),
            "policies": 2 ** len(pts), "results": totals, "first_witness": witness}


def demo_task_switch() -> dict:
    g1 = (0, 0, 1, 1)
    g2 = (0, 1, 0, 1)
    transitions = [reconfiguration_gate(a, b, 2).decision
                   for a, b in itertools.product((p for p in partitions(4) if block_count(p) == 2), repeat=2)]
    return {"initial": g1, "new_task": g2, "capacity": 2,
            "example": asdict(reconfiguration_gate(g1, g2, 2)),
            "all_pairs_of_2_block_partitions": len(transitions),
            "decisions": {k: transitions.count(k) for k in sorted(set(transitions))}}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"w04": run_closed_world_audit(), "w06": demo_task_switch(),
              "limitations": ["no real LLM or oracle grading", "no source-authenticity check",
                              "probe semantics assumed exact", "fixed two-probe oracle also achieves full closure",
                              "not a causal advantage over optimal adaptive baselines"]}
    if args.output:
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()