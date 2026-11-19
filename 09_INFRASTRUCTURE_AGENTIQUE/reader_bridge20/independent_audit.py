#!/usr/bin/env python3
"""Reader20 post-decision audit with algebraically independent reference oracles.

The router output is frozen to SHA-256 *before* reference formulas are applied.
The auditor does not import any Router20 proof functions or old R19 oracles.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
from itertools import product

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "CASES_FROZEN.md"
ROUTER_NAMES = ("exact_natural_product", "finite_map_congruence_count",
                "finite_binary_difference")


def restricted_growth(n: int):
    labels = [0] * n
    def go(i, largest):
        if i == n:
            yield tuple(labels)
            return
        for x in range(largest + 2):
            labels[i] = x
            yield from go(i + 1, max(largest, x))
    yield from go(1, 0)


def ref_congruence_count(transition: list[int]) -> int:
    size = len(transition)
    count = 0
    for partition in restricted_growth(size):
        seen = {}
        consistent = True
        for i, label in enumerate(partition):
            successor_block = partition[transition[i]]
            if label in seen and seen[label] != successor_block:
                consistent = False
                break
            seen[label] = successor_block
        count += int(consistent)
    return count


def ref_parity_bf(n: int, edges: list[tuple[int, int]]) -> bool:
    return any(
        all(bits[u] != bits[v] for u, v in edges)
        for bits in product((0, 1), repeat=n)
    )


def split_reference_cases(text: str) -> dict[str, list[str]]:
    groups = re.split(r"(?m)^## Cas (\d\d)\s*$", text)
    if len(groups) != 65:
        raise ValueError("REFERENCE_CASE_SPLIT_FAILED")
    cases = {}
    for i in range(1, len(groups), 2):
        n = int(groups[i])
        cases[f"C{n:02d}"] = groups[i+1].splitlines()
    return cases


def independent_reference(cid: str, source_lines: list[str]) -> tuple[str, bool]:
    """Independent grammar match: no model-output route hint is examined."""
    body = "\n".join(source_lines)
    if cid > "C24":
        raise ValueError("NEGATIVE_CASE_REQUIRES_ABSTENTION")
    if "nombre_congruences(T)" in body:
        match = re.search(r"T=\[([0-9,]+)\]", body)
        target = re.search(r"nombre_congruences\(T\) = (\d+)", body)
        if not match or not target:
            raise ValueError("REFERENCE_CONGRUENCE_DATA_MISSING")
        t = [int(x) for x in match.group(1).split(",")]
        truth = ref_congruence_count(t) == int(target.group(1))
        return "finite_map_congruence_count", truth
    if "deux_colorable" in body:
        match = re.search(r"n=(\d+); differences=\[([^\]]*)\]", body)
        target = re.search(r"deux_colorable = (oui|non)", body)
        if not match or not target:
            raise ValueError("REFERENCE_PARITY_DATA_MISSING")
        n = int(match.group(1))
        pairs = [(int(a), int(b)) for a, b in re.findall(r"\((\d+),(\d+)\)", match.group(2))]
        answer = ref_parity_bf(n, pairs)
        return "finite_binary_difference", answer == (target.group(1) == "oui")
    hypothesis = re.search(r"a=(\d+); b=(\d+)", body)
    target = re.search(r"Énoncé: (\d+) \* (\d+) = (\d+)", body)
    if not hypothesis or not target:
        raise ValueError("REFERENCE_MULTIPLICATION_DATA_MISSING")
    a, b = map(int, hypothesis.groups())
    x, y, claimed = map(int, target.groups())
    if (x, y) != (a, b):
        raise ValueError("REFERENCE_OPERANDS_DIFFER")
    # Independent repeated addition, not operator multiplication.
    reference = sum(b for _ in range(a))
    return "exact_natural_product", reference == claimed


def audit(published_report: dict, raw: bytes) -> dict:
    choices = published_report["decisions"]
    if len(choices) != 32:
        raise ValueError("NOT_THE_FROZEN_32_DECISIONS")
    # Freeze the meaningful decisions, excluding wall-clock timing jitter.
    # Identical scientific decisions across machines must have the same hash.
    stable = [
        {k: row.get(k) for k in (
            "case_id", "source_blob", "router_status", "selected_verifier",
            "contract_ast", "exact_result", "reject_reason", "evidence",
            "promotion_allowed"
        )} for row in choices
    ]
    raw_json = json.dumps(stable, sort_keys=True, ensure_ascii=False)
    decisions_sha256_before_gold = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()
    source_cases = split_reference_cases(raw.decode("utf-8"))
    good_routing = good_verdict = abstentions = silent_errors = 0
    positives = 0
    observations = []
    routes = {x: 0 for x in ROUTER_NAMES}
    for record in choices:
        cid = record["case_id"]
        if cid not in source_cases:
            raise ValueError("CASE_ID_NOT_IN_PINNED_SOURCE")
        if cid <= "C24":
            expected_verifier, expected_truth = independent_reference(cid, source_cases[cid])
            actual = record["exact_result"]
            correct_route = (
                record["router_status"] == "ROUTED_EXACT_RESTRICTED"
                and record["selected_verifier"] == expected_verifier
                and actual is not None
            )
            correct_truth = (
                correct_route and
                actual["status"] == "EXACT_CHECKED_RESTRICTED_GRAMMAR" and
                actual["truth_within_contract"] is expected_truth and
                not actual["general_theorem_proved"] and
                not record["promotion_allowed"]
            )
            good_routing += int(correct_route)
            good_verdict += int(correct_truth)
            positives += int(expected_truth)
            routes[expected_verifier] += 1
            silent_errors += int(not correct_truth)
            observations.append({
                "id": cid, "expected_verifier": expected_verifier,
                "routed_correctly": correct_route,
                "correct_exact_decision": correct_truth,
                "expected_truth": expected_truth,
            })
        else:
            passed = (
                record["router_status"] == "ABSTAIN_UNSUPPORTED_CONTRACT"
                and record["selected_verifier"] is None
                and record["exact_result"] is None
                and not record["promotion_allowed"]
            )
            abstentions += int(passed)
            silent_errors += int(not passed)
            observations.append({"id": cid, "negative_rejected": passed,
                                 "reason": record["reject_reason"]})
    perfect = (good_routing == 24 and good_verdict == 24
               and abstentions == 8 and silent_errors == 0
               and routes == {key: 8 for key in ROUTER_NAMES})
    return {
        "experiment": "OMEGA_READER20_INDEPENDENT_POST_DECISION_AUDIT",
        "decisions_sha256_before_reference_comparison": decisions_sha256_before_gold,
        "routed_correctly": good_routing,
        "correct_exact_decisions": good_verdict,
        "unsupported_cases_abstained": abstentions,
        "errors": silent_errors,
        "true_propositions": positives,
        "false_propositions": 24 - positives,
        "expected_routes_by_family": routes,
        "single_fixed_verifier_baseline_max_correct_route": max(routes.values()),
        "evidence_type": "RESTRICTED_SYNTAX_AND_FINITE_EXACT_ORACLES",
        "source_gold_independent_human": False,
        "new_general_mathematical_theorem": False,
        "model_weights_modified": False,
        "scientific_auto_promotions": 0,
        "success": perfect,
        "cases": observations,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--router-output", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = SOURCE.read_bytes()
    report = json.loads(args.router_output.read_text(encoding="utf-8"))
    result = audit(report, source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    print("AUDIT", result["success"], "routed", result["routed_correctly"],
          "exact", result["correct_exact_decisions"], "abstained",
          result["unsupported_cases_abstained"], "errors", result["errors"])
    if not result["success"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
