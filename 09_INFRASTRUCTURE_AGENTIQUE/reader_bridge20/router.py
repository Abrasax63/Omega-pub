#!/usr/bin/env python3
"""Reader20: exact source-bound claim router for three deliberately restricted grammars.

NOT a general natural-language understanding system, not an autonomous theorem
prover. Unknown or incomplete contracts fail closed; source provenance and
arithmetic truth are different properties.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
sys.path.insert(0, str(HERE.parent / "reader_bridge19"))
from read import safe_read, packetize, verify_packets
from exact_c4 import partitions_of_mask, congruent

SOURCE = HERE / "CASES_FROZEN.md"
SOURCE_BLOB = "1d58cc4f5856d9de7402ce5e2b7c3cdbb56f3ccf"
MAX_CONTRACTS = 32
MAX_BYTES_PER_CONTRACT = 4000
MAX_LINES_PER_CONTRACT = 32

HEADER = re.compile(r"## Cas ([0-9]{2})")
ARITH = re.compile(r"(\d+) \* (\d+) = (\d+)")
CONG = re.compile(r"nombre_congruences\(T\) = (\d+)")
PARITY = re.compile(r"deux_colorable = (oui|non)")
NAT_HYP = re.compile(r"a=(\d+); b=(\d+); domaine=N\[0,999\]")
CONG_HYP = re.compile(r"T=\[([0-9,]+)\]; domaine=\{0,\.\.\.,(\d+)\}")
PARITY_HYP = re.compile(r"n=(\d+); differences=\[(.*)\]")
EDGE_LIST = re.compile(r"\(\d+,\d+\)(?:,\(\d+,\d+\))*")


class UnsupportedContract(ValueError):
    pass


def split_cases(raw: bytes) -> list[dict]:
    """Source spans are 1-indexed line coordinates, never LLM-generated."""
    if len(raw) > 150000:
        raise ValueError("SOURCE_TOO_LARGE")
    lines = raw.decode("utf-8").splitlines()
    blocks: list[dict] = []
    active: dict | None = None
    for line_no, line in enumerate(lines, 1):
        matched = HEADER.fullmatch(line)
        if matched:
            if active is not None:
                blocks.append(active)
            active = {"id": "C" + matched.group(1), "heading_line": line_no,
                      "lines": [], "line_numbers": []}
        elif active is not None and line.strip():
            active["lines"].append(line)
            active["line_numbers"].append(line_no)
    if active is not None:
        blocks.append(active)
    if len(blocks) != MAX_CONTRACTS or len({b["id"] for b in blocks}) != len(blocks):
        raise ValueError("FROZEN_CASE_COUNT_OR_DUPLICATE_ID")
    for block in blocks:
        if len(block["lines"]) > MAX_LINES_PER_CONTRACT:
            raise ValueError("OVERSIZED_CONTRACT_LINES")
        if len("\n".join(block["lines"]).encode("utf-8")) > MAX_BYTES_PER_CONTRACT:
            raise ValueError("OVERSIZED_CONTRACT_BYTES")
    return blocks


def parse_claim(block: dict) -> dict:
    lines = block["lines"]
    if len(lines) != 3 or any(not line.startswith(prefix) for line, prefix in zip(
        lines, ("Hypothèses: ", "Énoncé: ", "Limites: ")
    )):
        raise UnsupportedContract("MISSING_FIELDS_OR_EXTRA_SOURCE_INSTRUCTION")
    assumptions = lines[0][len("Hypothèses: "):]
    claim = lines[1][len("Énoncé: "):]
    limits = lines[2][len("Limites: "):]
    options = {
        "exact_natural_product": ARITH.fullmatch(claim),
        "finite_map_congruence_count": CONG.fullmatch(claim),
        "finite_binary_difference": PARITY.fullmatch(claim),
    }
    matched = [name for name, match in options.items() if match]
    if len(matched) != 1:
        raise UnsupportedContract("UNKNOWN_OR_AMBIGUOUS_ASSERTION_FORM")
    family = matched[0]
    if family == "exact_natural_product":
        m = NAT_HYP.fullmatch(assumptions)
        if not m or limits != "entier naturel borné":
            raise UnsupportedContract("ARITHMETIC_HYPOTHESES_OR_LIMITS_MISMATCH")
        a, b = map(int, m.groups())
        cl_a, cl_b, claimed = map(int, options[family].groups())
        if not 0 <= a <= 999 or not 0 <= b <= 999 or (cl_a, cl_b) != (a, b):
            raise UnsupportedContract("ARITHMETIC_OUT_OF_SCOPE_OR_CHANGED_OPERANDS")
        args = {"a": a, "b": b, "claimed": claimed}
    elif family == "finite_map_congruence_count":
        m = CONG_HYP.fullmatch(assumptions)
        if not m or limits != "2<=n<=6; partitions finies":
            raise UnsupportedContract("CONGRUENCE_HYPOTHESES_OR_LIMITS_MISMATCH")
        items, maximum = m.groups()
        if not re.fullmatch(r"\d+(?:,\d+)*", items):
            raise UnsupportedContract("INVALID_FINITE_MAP_ENCODING")
        t = [int(x) for x in items.split(",")]
        n = len(t)
        if not 2 <= n <= 6 or maximum != str(n - 1) or any(v >= n for v in t):
            raise UnsupportedContract("MAP_NOT_TOTAL_ON_DECLARED_FINITE_DOMAIN")
        args = {"transition": t, "claimed": int(options[family].group(1))}
    else:
        m = PARITY_HYP.fullmatch(assumptions)
        if not m or limits != "2<=n<=12; valeurs binaires":
            raise UnsupportedContract("PARITY_HYPOTHESES_OR_LIMITS_MISMATCH")
        n = int(m.group(1))
        edge_text = m.group(2)
        if not 2 <= n <= 12 or (edge_text and not EDGE_LIST.fullmatch(edge_text)):
            raise UnsupportedContract("PARITY_OUT_OF_SCOPE_OR_INVALID_EDGES")
        edges = [
            tuple(map(int, x.split(",")))
            for x in re.findall(r"\((\d+,\d+)\)", edge_text)
        ]
        if len(edges) != len(set(edges)) or any(
            u == v or not 0 <= u < n or not 0 <= v < n for u, v in edges
        ):
            raise UnsupportedContract("PARITY_INVALID_CONSTRAINT")
        args = {"n": n, "edges": edges,
                "claimed": options[family].group(1) == "oui"}
    return {
        "verifier": family,
        "ast": args,
        "assumptions_literal": assumptions,
        "assertion_literal": claim,
        "limits_literal": limits,
    }


def count_congruences(transition: list[int]) -> int:
    """Reuse the independent exact bitset-partition enumerator from Reader19."""
    n = len(transition)
    return sum(
        congruent(part, tuple(transition))
        for part in partitions_of_mask((1 << n) - 1)
    )


def bipartite_bfs(n: int, edges: list[tuple[int, int]]) -> bool:
    graph = [[] for _ in range(n)]
    for u, v in edges:
        graph[u].append(v)
        graph[v].append(u)
    colors = [-1] * n
    for root in range(n):
        if colors[root] >= 0:
            continue
        colors[root] = 0
        queue = [root]
        for at in queue:
            for nxt in graph[at]:
                if colors[nxt] == -1:
                    colors[nxt] = 1 - colors[at]
                    queue.append(nxt)
                elif colors[nxt] == colors[at]:
                    return False
    return True


def evaluate_exact(parsed: dict) -> dict:
    """Verifier selection depends only on claim grammar; no solver hint passed in."""
    family = parsed["verifier"]
    a = parsed["ast"]
    if family == "exact_natural_product":
        computed = a["a"] * a["b"]
        truth = computed == a["claimed"]
    elif family == "finite_map_congruence_count":
        computed = count_congruences(a["transition"])
        truth = computed == a["claimed"]
    elif family == "finite_binary_difference":
        computed = bipartite_bfs(a["n"], a["edges"])
        truth = computed is a["claimed"]
    else:
        raise AssertionError("UNREGISTERED_VERIFIER_NAME")
    return {"truth_within_contract": bool(truth),
            "computed_value": computed,
            "verifier": family,
            "status": "EXACT_CHECKED_RESTRICTED_GRAMMAR",
            "general_theorem_proved": False,
            "semantic_fidelity_general_language": "NOT_TESTED",
            "automatic_scientific_promotion": False}


def evaluate_source(raw: bytes, source_path: str) -> dict:
    """All results cite exact line positions from the immutable source blob."""
    from read import blob
    source_hash = blob(raw)
    inventory = packetize(raw, source_path)
    if verify_packets(raw, inventory):
        raise ValueError("INVALID_SOURCE_PACKET_REPLAY")
    all_lines = raw.decode("utf-8").splitlines()
    lookup = {i: p for p in inventory["packets"]
              for i in range(p["start_line"], p["end_line"] + 1)}
    records = []
    for case in split_cases(raw):
        t0 = time.perf_counter()
        record = {"case_id": case["id"], "heading_line": case["heading_line"],
                  "source_blob": source_hash,
                  "exact_source_lines": case["line_numbers"],
                  "router_status": "ABSTAIN_UNSUPPORTED_CONTRACT",
                  "selected_verifier": None,
                  "exact_result": None,
                  "reject_reason": None,
                  "promotion_allowed": False}
        try:
            parsed = parse_claim(case)
            assert all(n in lookup for n in case["line_numbers"])
            evidence = [
                {
                    "line": n, "literal": all_lines[n - 1],
                    "packet_id": lookup[n]["packet_id"],
                    "source_blob": source_hash,
                    "literal_sha256": hashlib.sha256(
                        all_lines[n-1].encode("utf-8")
                    ).hexdigest(),
                }
                for n in case["line_numbers"]
            ]
            if len({item["packet_id"] for item in evidence}) != 1:
                raise UnsupportedContract("CONTRACT_SPANS_MULTIPLE_UNEXPECTED_PACKETS")
            result = evaluate_exact(parsed)
            record.update({
                "router_status": "ROUTED_EXACT_RESTRICTED",
                "selected_verifier": parsed["verifier"],
                "contract_ast": parsed["ast"],
                "hypotheses": parsed["assumptions_literal"],
                "assertion": parsed["assertion_literal"],
                "limitations": parsed["limits_literal"],
                "evidence": evidence,
                "exact_result": result,
            })
        except UnsupportedContract as exc:
            record["reject_reason"] = str(exc)
        record["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 3)
        records.append(record)
    return {
        "experiment": "OMEGA_READER20_SOURCE_ROUTER_RESTRICTED",
        "source_blob": source_hash,
        "source_path": source_path,
        "total_cases": len(records),
        "route_counts": {name: sum(r["selected_verifier"] == name for r in records)
                         for name in ("exact_natural_product",
                                      "finite_map_congruence_count",
                                      "finite_binary_difference")},
        "routed_count": sum(r["router_status"] == "ROUTED_EXACT_RESTRICTED" for r in records),
        "abstained_count": sum(r["router_status"] == "ABSTAIN_UNSUPPORTED_CONTRACT" for r in records),
        "automatic_scientific_promotions": 0,
        "free_language_understanding_claimed": False,
        "paid_api_calls": 0,
        "decisions": records,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    report = {"run_status": "STARTED"}
    failure = False
    try:
        raw = safe_read(SOURCE, SOURCE_BLOB)
        report = evaluate_source(raw, SOURCE.relative_to(ROOT).as_posix())
        report["run_status"] = "FINISHED_SOURCE_ROUTING"
    except Exception:
        report = {"run_status": "FAILED_NOT_SCIENTIFIC_RESULT",
                  "error": traceback.format_exc()}
        failure = True
    finally:
        opts.output.parent.mkdir(parents=True, exist_ok=True)
        opts.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
        print("READER20", report["run_status"], report.get("route_counts"),
              "routed", report.get("routed_count"), "abstained",
              report.get("abstained_count"), flush=True)
    if failure:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
