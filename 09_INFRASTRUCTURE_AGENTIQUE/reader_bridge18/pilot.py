#!/usr/bin/env python3
"""Reader18: heading-agnostic balanced retrieval + independent exact toy oracle.

Source-only evidence is not semantic truth. Any generated model text is data,
never an instruction or a mathematical proof. No paid API, no promotions.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict
import hashlib
import json
from pathlib import Path
import random
import re
import sys
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE.parent / "reader_bridge17"))
sys.path.insert(0, str(HERE.parent / "reader_bridge16"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))

from experiment import (strict_line_ids, prompt_for, call_local,
                        MAX_NEW_TOKENS, MAX_SELECTED, MAX_CANDIDATES, MODEL,
                        GGUF_SHA256, LLAMA_CPP_SHA)
from audit import expanded_candidates
from read import packetize, safe_read, verify_packets
from gate import gate

MANIFEST = HERE / "SOURCES_FROZEN.json"
STATEMENT_TERMS = (
    "énoncé", "enonce", "proposition", "théorème", "theoreme",
    "résultat", "resultat", "lemme", "corollaire",
)
TOY_SEED = 20261119
TOY_COUNT = 8
ARITHMETIC = re.compile(
    r"^Résultat\s*:\s*(\d{1,3})\s*\*\s*(\d{1,3})\s*=\s*(\d{1,6})$",
    re.I,
)


def load_manifest() -> list[dict]:
    info = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if info["source_labels"] != "NOT_AVAILABLE" or info["independent_human_annotations"]:
        raise ValueError("HUMAN_LABELS_UNEXPECTED_IN_MODEL_INPUT")
    docs = info["documents"]
    if len(docs) != 3 or len({d["blob"] for d in docs}) != 3:
        raise ValueError("COHORT_MUST_BE_THREE_UNIQUE_GIT_BLOBS")
    for d in docs:
        path = Path(d["path"])
        if path.is_absolute() or ".." in path.parts or path.suffix != ".md":
            raise ValueError("UNSAFE_SOURCE_PATH")
        raw = safe_read(ROOT / path, d["blob"])
        if len(raw) != d["bytes"]:
            raise ValueError("FROZEN_SOURCE_SIZE_DRIFT")
    return docs


def section_for_packet(packet: dict) -> str:
    headings = packet["section_path"]
    # Level 2 section is the research unit to cover, independent of its title.
    # packetize emits heading path, not levels; use second path entry.
    if len(headings) >= 2:
        return " | ".join(headings[:2])
    return headings[0] if headings else "__UNHEADED__"


def round_robin_by_section(candidates: list[dict], cap: int) -> list[dict]:
    grouped: dict[str, list[dict]] = OrderedDict()
    for row in candidates:
        grouped.setdefault(row["section"], []).append(row)
    buckets = list(grouped.values())
    selected = []
    offset = 0
    while len(selected) < cap and any(offset < len(bucket) for bucket in buckets):
        for bucket in buckets:
            if offset < len(bucket):
                selected.append(bucket[offset])
                if len(selected) >= cap:
                    break
        offset += 1
    return selected


def number_sections(candidates: list[dict]) -> int:
    return len({x["section"] for x in candidates})


def source_policies(d: dict) -> dict:
    """Generate candidate pools with no reference labels or language model."""
    path = ROOT / d["path"]
    raw = safe_read(path, d["blob"])
    lines = raw.decode("utf-8").splitlines()
    inventory = packetize(raw, str(path))
    if verify_packets(raw, inventory):
        raise ValueError("READER12_SOURCE_PACKET_REPLAY_FAILED")
    packets = inventory["packets"]
    by_line: dict[int, dict] = {}
    for packet in packets:
        for n in range(packet["start_line"], packet["end_line"] + 1):
            by_line[n] = packet
    d_packets = [
        p for p in packets if any(
            term in title.casefold()
            for title in p["section_path"] for term in STATEMENT_TERMS
        )
    ]
    e_packets = [p for p in packets if p["context_status"] != "BLOCKED_SOURCE_CONTEXT"]
    d_staged = expanded_candidates(raw, path, d_packets)
    e_staged = expanded_candidates(raw, path, e_packets)
    def materialize(nums: list[int]) -> list[dict]:
        return [
            {"line": n, "source_text": lines[n-1].strip(),
             "packet_id": by_line[n]["packet_id"],
             "section": section_for_packet(by_line[n]),
            } for n in nums
        ]
    d_candidates = materialize(d_staged["lines"])
    e_candidates = materialize(e_staged["lines"])
    d_first = d_candidates[:MAX_CANDIDATES]
    e_first = e_candidates[:MAX_CANDIDATES]
    e_balanced = round_robin_by_section(e_candidates, MAX_CANDIDATES)
    policies = {
        "D_title_bound_first12": {
            "pool": d_candidates, "submitted": d_first,
            "strategy": "OLD_READER17_D_FIRST12",
        },
        "E_headings_agnostic_first12": {
            "pool": e_candidates, "submitted": e_first,
            "strategy": "CONTROL_E_FIRST12",
        },
        "E_headings_agnostic_balanced12": {
            "pool": e_candidates, "submitted": e_balanced,
            "strategy": "NEW_E_ROUND_ROBIN_LEVEL2",
        },
    }
    result = {
        "doc_id": d["id"], "blob": d["blob"],
        "source_path": d["path"],
        "total_packets": len(packets),
        "eligible_source_packets": len(e_packets),
        "title_only_source_packets": len(d_packets),
        "policies": {},
    }
    for name, obj in policies.items():
        pool = obj["pool"]
        submitted = obj["submitted"]
        result["policies"][name] = {
            "strategy": obj["strategy"],
            "total_candidates_after_gate": len(pool),
            "total_sections_after_gate": number_sections(pool),
            "submitted_count": len(submitted),
            "submitted_sections": number_sections(submitted),
            "submitted_source_characters": sum(len(c["source_text"]) for c in submitted),
            "truncated_count": max(0, len(pool)-len(submitted)),
            "submitted": submitted,
            "model": {"status": "NOT_RUN"},
        }
    diversity_first = result["policies"]["E_headings_agnostic_first12"]["submitted_sections"]
    diversity_balanced = result["policies"]["E_headings_agnostic_balanced12"]["submitted_sections"]
    result["balanced_section_coverage_delta"] = diversity_balanced - diversity_first
    result["balanced_is_no_worse_than_first12"] = diversity_balanced >= diversity_first
    return result


def exact_arithmetic_oracle(source_literal: str) -> dict:
    """Independent of model/source labels; only exact natural-number multiplication."""
    if not isinstance(source_literal, str):
        return {"status": "NOT_APPLICABLE"}
    match = ARITHMETIC.fullmatch(source_literal.strip())
    if not match:
        return {"status": "NOT_APPLICABLE"}
    a, b, c = (int(n) for n in match.groups())
    if any(n > 999 for n in (a, b)):
        return {"status": "NOT_APPLICABLE"}
    valid = (a * b == c)
    return {
        "status": "ARITHMETIC_IDENTITY_TRUE" if valid else "ARITHMETIC_IDENTITY_FALSE",
        "a": a, "b": b, "claimed": c,
        "exact_value": a * b,
        "limited_grammar": "NATURAL_MULTIPLICATION_ONLY_NOT_GENERAL_THEOREM",
    }


def synthetic_arithmetic(seed: int = TOY_SEED) -> list[dict]:
    """Construct 4 exact and 4 deliberately wrong equations; not model labels."""
    rng = random.Random(seed)
    rows = []
    for i in range(TOY_COUNT):
        a = rng.randint(2, 99)
        b = rng.randint(2, 99)
        delta = 0 if i % 2 == 0 else rng.choice((-7, -3, -1, 1, 2, 5))
        claimed = a * b + delta
        if claimed < 0:
            raise AssertionError("IMPOSSIBLE_NEGATIVE_SYNTHETIC_TARGET")
        rows.append({
            "case_id": "TOY-" + str(i+1).zfill(2),
            "source_literal": f"Résultat : {a} * {b} = {claimed}",
            "expected_truth": i % 2 == 0,
        })
    return rows


def audit_toy_oracle() -> dict:
    tests = synthetic_arithmetic()
    details = []
    for t in tests:
        verdict = exact_arithmetic_oracle(t["source_literal"])
        expected = "ARITHMETIC_IDENTITY_TRUE" if t["expected_truth"] else "ARITHMETIC_IDENTITY_FALSE"
        details.append({
            "case_id": t["case_id"],
            "source_literal": t["source_literal"],
            "expected_status": expected,
            "observed_status": verdict["status"],
            "consistent": verdict["status"] == expected,
        })
    negatives = [
        "Preuve : 7 * 8 = 56", "Résultat : -1 * 2 = -2",
        "Résultat : 7 / 3 = 2", "Résultat : 7 * 4 = 28; voir preuve",
        "Résultat : 1000 * 2 = 2000", "Résultat : x * y = z",
    ]
    control_results = [exact_arithmetic_oracle(t)["status"] for t in negatives]
    if any(x != "NOT_APPLICABLE" for x in control_results):
        raise AssertionError("UNSUPPORTED_ARITHMETIC_PASSED_ORACLE")
    return {
        "toy_seed": TOY_SEED,
        "cases": len(details),
        "correct": sum(t["consistent"] for t in details),
        "false_equalities_detected": sum(
            t["observed_status"] == "ARITHMETIC_IDENTITY_FALSE" for t in details
        ),
        "negative_controls_not_applicable": len(control_results),
        "human_independent_review": False,
        "model_output_independence": True,
        "scope": "TOY_EXACT_MULTIPLICATION_ONLY",
        "rows": details,
    }


def grounded_claims(d: dict, candidates: list[dict], ids: list[int]) -> dict:
    by_line = {c["line"]: c for c in candidates}
    if len(ids) > MAX_SELECTED or len(ids) != len(set(ids)) or not set(ids).issubset(by_line):
        raise ValueError("UNAUTHORIZED_ID_OR_OVERFLOW")
    return {
        "source_blob": d["blob"],
        "claims": [{
            "claim_id": "COV" + str(n),
            "packet_id": by_line[n]["packet_id"],
            "evidence": [{
                "role": "conclusion", "packet_id": by_line[n]["packet_id"],
                "line": n, "literal": by_line[n]["source_text"],
            }],
        } for n in ids],
    }


def evaluate_model(d: dict, pools: dict, caller) -> None:
    raw = safe_read(ROOT / d["path"], d["blob"])
    # Only D and balanced E consume Qwen. Same prompt and max source candidate count.
    for policy in ("D_title_bound_first12", "E_headings_agnostic_balanced12"):
        row = pools["policies"][policy]
        offered = row["submitted"]
        if not offered:
            row["model"] = {"status": "NO_CANDIDATES", "selected": []}
            continue
        response = caller(prompt_for(offered))
        ids, error = strict_line_ids(response["raw_reply"],
                                     {x["line"] for x in offered})
        model = {
            "status": "INVALID_REPLY" if error else "VALID_REPLY",
            "selected": ids, "parse_failure": error, **response,
        }
        if error is None:
            staged = gate(raw, str(ROOT / d["path"]), grounded_claims(d, offered, ids),
                          provider="reader18-source-only-model-classification")
            if staged["rejected_count"] or staged["automatic_promotions"] or staged["horn_rules"]:
                raise AssertionError("SOURCE_CITATION_NOT_GROUNDED_OR_UNSAFE_PROMOTION")
            model["source_citations_admitted"] = staged["accepted_count"]
            model["mathematical_certifications"] = 0
            model["semantic_accuracy_verified"] = False
            model["source_literal_oracle"] = [
                {"line": x["line"], "status": exact_arithmetic_oracle(x["source_text"])["status"]}
                for x in offered if x["line"] in ids
            ]
        row["model"] = model


def build_report(documents: list[dict], caller=None) -> dict:
    items = []
    for d in documents:
        obj = source_policies(d)
        if caller is not None:
            evaluate_model(d, obj, caller)
        items.append(obj)
    toy = audit_toy_oracle()
    deltas = [item["balanced_section_coverage_delta"] for item in items]
    return {
        "experiment": "OMEGA_READER18_BALANCED_RETRIEVAL_AND_TOY_ORACLE",
        "mode": "MODEL" if caller else "OFFLINE",
        "source_labels_available": False,
        "model_calls_made": sum(
            item["policies"][policy]["model"]["status"] not in ("NOT_RUN", "NO_CANDIDATES")
            for item in items for policy in ("D_title_bound_first12", "E_headings_agnostic_balanced12")
        ),
        "cost_equalized": False,
        "human_independent_annotations": False,
        "scientific_claims_certified": 0,
        "horn_rules": 0,
        "paid_api_calls": 0,
        "H1_all_nonnegative": all(d >= 0 for d in deltas),
        "H1_one_improved": any(d > 0 for d in deltas),
        "H1_status": "PASS_ON_SECTION_COVERAGE_ONLY" if all(d>=0 for d in deltas) and any(d>0 for d in deltas)
                     else "NOT_CONFIRMED_OR_REFUTED_ON_THIS_COHORT",
        "H2_status": "PASS_TOY_ARITHMETIC_ONLY" if toy["correct"] == TOY_COUNT else "FAILED",
        "arithmetic_oracle": toy,
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("offline", "model"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "experiment": "OMEGA_READER18_BALANCED_RETRIEVAL_AND_TOY_ORACLE",
        "run_status": "STARTED",
        "scientific_claims_certified": 0,
        "horn_rules": 0, "paid_api_calls": 0, "error": None,
    }
    failed = False
    try:
        report = build_report(load_manifest(), caller=call_local if args.mode == "model" else None)
        report["run_status"] = "FINISHED_REAL_INFERENCE" if args.mode == "model" else "FINISHED_OFFLINE"
    except Exception:
        report["run_status"] = "FAILED_NOT_SCIENTIFIC_RESULT"
        report["error"] = traceback.format_exc()
        failed = True
    finally:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        print("REPORT", args.output, report["run_status"], flush=True)
        if "items" in report:
            for row in report["items"]:
                print(row["doc_id"], "balanced_delta", row["balanced_section_coverage_delta"],
                      {k: {"pool": v["total_candidates_after_gate"],
                           "sections": v["submitted_sections"],
                           "model": v["model"]["status"]}
                       for k, v in row["policies"].items()}, flush=True)
            print("H1", report["H1_status"], "H2", report["H2_status"], flush=True)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
