#!/usr/bin/env python3
"""Independent finite C4 witness replay using subset-bitmask partitions.

Not a proof of global minimality or of source natural-language semantics.
Does not import the historical quotient/constraint/rotation implementation.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import sys
from typing import Iterator

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from read import safe_read

SOURCE = ROOT / "02_MATHEMATIQUES/defauts_recollement/AUDIT_QUOTIENTS_TEMOIN9_C4_L2_2026-11-04.md"
SOURCE_BLOB = "44f08ebe3e99ef97af8b16c98167b5f64383ce45"

T = (1, 2, 3, 0, 8, 7, 6, 2, 0)
PAIRS = ((0, 1), (0, 2), (1, 8), (0, 7),
         (0, 6), (4, 5), (1, 4), (0, 4))
TARGETS = (
    (0, 7, 8, 15), (0, 5, 10, 15), (2, 7, 8, 13),
    (1, 6, 9, 14), (0, 3, 4, 7, 8, 11, 12, 15),
    (0, 1, 4, 5, 10, 11, 14, 15),
    (4, 5, 6, 7, 8, 9, 10, 11),
    (2, 3, 6, 7, 8, 9, 12, 13),
)
EXPECTED_SIZES = {5: 1, 6: 2, 7: 3, 8: 2, 9: 1}


def members(bits: int) -> Iterator[int]:
    while bits:
        low = bits & -bits
        yield low.bit_length() - 1
        bits ^= low


def partitions_of_mask(remaining: int) -> Iterator[tuple[int, ...]]:
    """Every set partition once via the block containing its least element."""
    if remaining == 0:
        yield ()
        return
    anchor = remaining & -remaining
    others = remaining ^ anchor
    subset = others
    while True:
        block = anchor | subset
        for tail in partitions_of_mask(remaining ^ block):
            yield (block,) + tail
        if subset == 0:
            break
        subset = (subset - 1) & others


def block_lookup(partition: tuple[int, ...], n: int) -> tuple[int, ...]:
    lookup = [-1] * n
    for label, bits in enumerate(partition):
        for element in members(bits):
            if lookup[element] >= 0:
                raise ValueError("OVERLAPPING_PARTITION")
            lookup[element] = label
    if -1 in lookup:
        raise ValueError("INCOMPLETE_PARTITION")
    return tuple(lookup)


def congruent(partition: tuple[int, ...], transition: tuple[int, ...]) -> bool:
    idx = block_lookup(partition, len(transition))
    for block in partition:
        image_labels = {idx[transition[s]] for s in members(block)}
        if len(image_labels) != 1:
            return False
    return True


def quotient_map(partition: tuple[int, ...], transition: tuple[int, ...]) -> tuple[int, ...]:
    idx = block_lookup(partition, len(transition))
    return tuple(idx[transition[next(members(block))]] for block in partition)


def forced_constraints(q: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    edges = []
    for x, y in combinations(range(len(q)), 2):
        # Forced inequivalence: shared successor OR swapped successors.
        if q[x] == q[y] or (q[x] == y and q[y] == x):
            edges.append((x, y))
    return tuple(edges)


def constraints_consistent(q: tuple[int, ...]) -> bool:
    if max(Counter(q).values(), default=0) > 2:
        return False
    adjacency = [[] for _ in q]
    for x, y in forced_constraints(q):
        adjacency[x].append(y)
        adjacency[y].append(x)
    colors: list[int | None] = [None] * len(q)
    for root in range(len(q)):
        if colors[root] is not None:
            continue
        colors[root] = 0
        stack = [root]
        while stack:
            at = stack.pop()
            for nxt in adjacency[at]:
                if colors[nxt] is None:
                    colors[nxt] = 1 - colors[at]
                    stack.append(nxt)
                elif colors[nxt] == colors[at]:
                    return False
    return True


def admissible_quotient(partition: tuple[int, ...], transition: tuple[int, ...],
                        pairs: tuple[tuple[int, int], ...]):
    idx = block_lookup(partition, len(transition))
    cycle = tuple(idx[i] for i in range(4))
    if len(set(cycle)) != 4:
        return None
    moved_pairs = tuple((idx[x], idx[y]) for x, y in pairs)
    if any(x == y for x, y in moved_pairs):
        return None
    q = quotient_map(partition, transition)
    if not constraints_consistent(q):
        return None
    return q, moved_pairs, cycle


def rotated(mask: int, k: int) -> int:
    k %= 4
    return ((mask << k) | (mask >> (4-k))) & 15


def canonical_mask_collection(shadow: set[int] | tuple[int, ...]) -> tuple[int, ...]:
    return min(tuple(sorted(rotated(m, k) for m in shadow)) for k in range(4))


TARGET_CLASSES = {canonical_mask_collection(set(shadow)) for shadow in TARGETS}


def calculate_shadow(q: tuple[int, ...], x: int, y: int,
                     cycle: tuple[int, int, int, int]) -> set[int]:
    edges = forced_constraints(q)
    result = set()
    for bits in range(1 << len(q)):
        def color(s: int) -> int:
            return (bits >> s) & 1
        if any(color(u) == color(v) for u, v in edges):
            continue
        if color(x) != color(y) or color(q[x]) != color(q[y]):
            continue
        projected = sum(color(cycle[k]) << k for k in range(4))
        result.add(projected)
    return result


def classes_of_pairs(q: tuple[int, ...], pairs: tuple[tuple[int, int], ...],
                     cycle: tuple[int, int, int, int]) -> set[tuple[int, ...]]:
    return {canonical_mask_collection(calculate_shadow(q, x, y, cycle))
            for x, y in pairs}


def analyze(transition: tuple[int, ...], pairs=PAIRS,
            count_shadows: bool = True) -> dict:
    n = len(transition)
    if n != 9 or len(pairs) != 8 or any(not 0 <= v < n for v in transition):
        raise ValueError("ONLY_FROZEN_9_STATE_MODEL_SUPPORTED")
    checked = 0
    congruences = []
    eligible_sizes = Counter()
    preserving = []
    for partition in partitions_of_mask((1 << n) - 1):
        checked += 1
        if not congruent(partition, transition):
            continue
        congruences.append(partition)
        qdata = admissible_quotient(partition, transition, pairs)
        if qdata is None:
            continue
        q, pairs_q, cycle = qdata
        eligible_sizes[len(q)] += 1
        if count_shadows:
            if TARGET_CLASSES <= classes_of_pairs(q, pairs_q, cycle):
                preserving.append({
                    "size": len(q),
                    "partition_blocks_masks": list(partition),
                    "discrete": all(block.bit_count() == 1 for block in partition),
                })
    stable = json.dumps(sorted(congruences), separators=(",", ":"))
    return {
        "partitions_enumerated": checked,
        "congruences": len(congruences),
        "eligible": sum(eligible_sizes.values()),
        "size_distribution": dict(sorted(eligible_sizes.items())),
        "preserve_all_eight_target_classes": len(preserving) if count_shadows else None,
        "preserving_quotients": preserving,
        "partition_set_sha256": hashlib.sha256(stable.encode("utf-8")).hexdigest(),
    }


def verify_relabelings(transition=T, pairs=PAIRS) -> dict:
    """Transport source labels rather than infer shadows from textual names."""
    base = classes_of_pairs(transition, pairs, (0, 1, 2, 3))
    results = []
    for permutation in permutations(range(4, 9)):
        renamed = list(range(9))
        for i, target in enumerate(permutation):
            renamed[i+4] = target
        mapped = [None] * 9
        for original_state in range(9):
            mapped[renamed[original_state]] = renamed[transition[original_state]]
        changed_pairs = tuple((renamed[x], renamed[y]) for x, y in pairs)
        observed = classes_of_pairs(tuple(mapped), changed_pairs, (0, 1, 2, 3))
        if observed != base:
            results.append(permutation)
    return {
        "renamings_tested": 120,
        "all_classes_invariant": not results,
        "noninvariant_permutations": results,
        "baseline_classes": len(base),
    }


def exact_audit() -> dict:
    raw = safe_read(SOURCE, SOURCE_BLOB)
    assert len(raw) > 2000
    output = analyze(T, PAIRS)
    renamings = verify_relabelings()
    # Negative controls must change a property; otherwise checker may be constant.
    altered = list(PAIRS)
    altered[0] = (0, 0)
    invalid_pairs = analyze(T, tuple(altered), count_shadows=False)
    mutated = list(T)
    mutated[8] = 8
    invalid_transition = analyze(tuple(mutated), PAIRS, count_shadows=False)
    oracle_matches = (
        output["partitions_enumerated"] == 21147 and
        output["congruences"] == 49 and
        output["eligible"] == 9 and
        output["size_distribution"] == EXPECTED_SIZES and
        output["preserve_all_eight_target_classes"] == 1 and
        output["preserving_quotients"][0]["discrete"] and
        renamings["renamings_tested"] == 120 and
        renamings["all_classes_invariant"] and
        renamings["baseline_classes"] == 8
    )
    controls_discriminate = (
        invalid_pairs["eligible"] != output["eligible"] and
        invalid_transition["congruences"] != output["congruences"]
    )
    return {
        "experiment": "OMEGA_READER19_INDEPENDENT_FINITE_C4_REPLAY",
        "source_git_blob": SOURCE_BLOB,
        "baseline_not_imported": True,
        "algorithm": "MASK_SET_PARTITION_ENUMERATION_THEN_DIRECT_IMAGE_TEST",
        "known_claims_tested_posthoc": True,
        "source_mathematical_truth_generalized": False,
        "external_mathematical_review": False,
        "lean_certification": False,
        "scientific_autopromotion": False,
        "paid_api_calls": 0,
        "exact": output,
        "renamings": renamings,
        "negative_controls": {
            "invalid_pair_eligible": invalid_pairs["eligible"],
            "mutated_transition_congruences": invalid_transition["congruences"],
            "both_discriminating": controls_discriminate,
        },
        "status": "REPLICATION_EXACT_FINITE" if oracle_matches and controls_discriminate
                  else "DISAGREEMENT_OR_NON_DISCRIMINATING_CHECK",
    }


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--output", type=Path, required=True)
    args = arg.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = exact_audit()
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("READER19", report["status"], "congruences",
          report["exact"]["congruences"], "eligible", report["exact"]["eligible"],
          "preserving", report["exact"]["preserve_all_eight_target_classes"],
          "renamings", report["renamings"]["all_classes_invariant"])
    if report["status"] != "REPLICATION_EXACT_FINITE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
