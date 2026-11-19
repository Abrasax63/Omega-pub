#!/usr/bin/env python3
"""Offline post-hoc audit of Omega Reader candidate-recall ceilings.

No model calls, no new scientific proof. Input gold is unreviewed author
annotation and is used only after source-derived candidate sets are computed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reader_bridge14"))
sys.path.insert(0, str(HERE.parent / "reader_bridge13"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))

from run_experiment import GOLD, ROOT, baseline, select_packets
from read import packetize, safe_read, verify_packets
from gate import gate

MAX_CLAIMS_PER_GATE = 32
TOP_K = 3


def conclusions(staged: dict) -> list[int]:
    return sorted({e["line"] for claim in staged["accepted"]
                   for e in claim["evidence"] if e["role"] == "conclusion"})


def expanded_candidates(raw: bytes, source: Path, packets: list[dict]) -> dict:
    """Blind, deterministic source-only generator; reject through existing gate."""
    lines = raw.decode("utf-8").splitlines()
    ids: set[int] = set()
    claims: list[dict] = []
    for p in packets:
        for n in range(p["start_line"], p["end_line"] + 1):
            text = lines[n - 1].strip()
            if n in ids or not 6 <= len(text) <= 500:
                continue
            ids.add(n)
            claims.append({
                "claim_id": "CEXP" + str(n),
                "packet_id": p["packet_id"],
                "evidence": [{
                    "role": "conclusion",
                    "packet_id": p["packet_id"],
                    "line": n,
                    "literal": text,
                }],
            })
    accepted: list[dict] = []
    rejected: list[dict] = []
    for i in range(0, len(claims), MAX_CLAIMS_PER_GATE):
        staged = gate(raw, str(source), {
            "source_blob": packets[0]["source_blob"] if packets else packetize(raw, str(source))["source_blob"],
            "claims": claims[i:i + MAX_CLAIMS_PER_GATE],
        }, provider="reader16-source-only-expanded")
        if staged["automatic_promotions"] or staged["horn_rules"]:
            raise AssertionError("SOURCE_ONLY_GATE_MUST_NOT_PROMOTE")
        accepted.extend(staged["accepted"])
        rejected.extend(staged["rejected"])
    return {
        "lines": conclusions({"accepted": accepted}),
        "generated_line_count": len(claims),
        "accepted_count": len(accepted),
        "rejected_count": len(rejected),
        "rejection_reasons": sorted(set(r["reason"] for r in rejected)),
        "automatic_promotions": 0,
        "horn_rules": [],
    }


def source_policies(source: Path, expected_blob: str) -> dict:
    """Compute all candidate pools without seeing gold/reference labels."""
    raw = safe_read(source, expected_blob)
    inventory = packetize(raw, str(source))
    if verify_packets(raw, inventory):
        raise ValueError("INVALID_IMMUTABLE_SOURCE_PACKET")
    selected = select_packets(inventory)
    original = baseline(raw.decode("utf-8").splitlines(), selected, expected_blob)
    original_gated = gate(raw, str(source), original, provider="reader13-original-mechanical")
    if original_gated["automatic_promotions"] or original_gated["horn_rules"]:
        raise AssertionError("BASELINE_PROMOTION_FORBIDDEN")
    statement_packets = [
        p for p in inventory["packets"] if any(
            "énoncé" in title.casefold() or "enonce" in title.casefold()
            for title in p["section_path"]
        )
    ]
    expanded_same = expanded_candidates(raw, source, selected)
    expanded_all_statements = expanded_candidates(raw, source, statement_packets)
    selected_lines = sorted({
        i for p in selected for i in range(p["start_line"], p["end_line"] + 1)
    })
    result = {
        "source_blob": expected_blob,
        "source_lines": len(raw.decode("utf-8").splitlines()),
        "selected_packet_count": len(selected),
        "all_packet_count": len(inventory["packets"]),
        "statement_packet_count": len(statement_packets),
        "visible_lines": selected_lines,
        "A_original": {
            "lines": conclusions(original_gated),
            "accepted_count": original_gated["accepted_count"],
            "automatic_promotions": 0, "horn_rules": [],
        },
        "B_all_lines_in_reader13_packets": expanded_same,
        "C_all_lines_in_statement_packets": expanded_all_statements,
    }
    result["candidate_sets_sha256"] = hashlib.sha256(json.dumps(
        {k: result[k]["lines"] for k in (
            "A_original", "B_all_lines_in_reader13_packets", "C_all_lines_in_statement_packets"
        )}, sort_keys=True
    ).encode("utf-8")).hexdigest()
    return result


def score_ceiling(blind: dict, reference: dict) -> dict:
    """Gold enters *only here*, never the candidate-generation methods."""
    gold = set(reference["conclusion_lines"])
    visible = set(blind["visible_lines"])
    report = {
        "source": reference["id"],
        "label_provenance": "AUTHOR_LABELS_UNREVIEWED_NOT_INDEPENDENT",
        "gold_lines_total": sorted(gold),
        "gold_lines_visible_by_reader13": sorted(gold & visible),
        "gold_missing_from_selected_packets": sorted(gold - visible),
        "candidate_sets_sha256": blind["candidate_sets_sha256"],
        "selected_packet_count": blind["selected_packet_count"],
        "statement_packet_count": blind["statement_packet_count"],
        "policies": {},
    }
    for key in ("A_original", "B_all_lines_in_reader13_packets",
                "C_all_lines_in_statement_packets"):
        p = blind[key]
        offered = set(p["lines"])
        recoverable = gold & offered
        max_topk = min(TOP_K, len(recoverable))
        report["policies"][key] = {
            "lines_offered": p["lines"],
            "candidate_count": len(offered),
            "gold_offered": sorted(recoverable),
            "gold_missed": sorted(gold - offered),
            "other_candidates_not_marked_gold": sorted(offered - gold),
            "other_candidate_count": len(offered - gold),
            "recall_upper_bound_all_choices_total_gold": (
                round(len(recoverable) / len(gold), 4) if gold else None
            ),
            "oracle_top3_correct_max": max_topk,
            "oracle_top3_recall_bound_total_gold": (
                round(max_topk / len(gold), 4) if gold else None
            ),
            "oracle_top3_recall_bound_reader13_visible": (
                round(min(TOP_K, len(recoverable & visible)) / len(gold & visible), 4)
                if gold & visible else None
            ),
            "automatic_promotions": p["automatic_promotions"],
            "horn_rule_count": len(p["horn_rules"]),
        }
    return report


def build_report(references: dict) -> dict:
    if references["annotation_status"] != "AUTHOR_LABELS_UNREVIEWED_NOT_INDEPENDENT":
        raise ValueError("REFERENCE_STATUS_MISMATCH")
    blind_policies = [
        source_policies(ROOT / r["path"], r["blob"])
        for r in references["documents"]
    ]
    scored = [score_ceiling(blind, r)
              for blind, r in zip(blind_policies, references["documents"])]
    totals = {
        "gold_total": sum(len(x["gold_lines_total"]) for x in scored),
        "gold_visible_reader13": sum(len(x["gold_lines_visible_by_reader13"]) for x in scored),
    }
    for key in ("A_original", "B_all_lines_in_reader13_packets",
                "C_all_lines_in_statement_packets"):
        totals[key] = {
            "offered_count": sum(row["policies"][key]["candidate_count"] for row in scored),
            "gold_recoverable": sum(len(row["policies"][key]["gold_offered"]) for row in scored),
            "max_oracle_top3_correct": sum(row["policies"][key]["oracle_top3_correct_max"] for row in scored),
        }
    return {
        "experiment": "OMEGA_READER16_POSTHOC_CANDIDATE_COVERAGE_AUDIT",
        "scientific_certification": False,
        "no_neural_inference": True,
        "label_status": references["annotation_status"],
        "interpretation": "SOURCE_RETRIEVAL_CEILING_ONLY_NOT_SEMANTIC_ACCURACY",
        "top_k": TOP_K,
        "rows": scored,
        "totals": totals,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    opts = parser.parse_args()
    report = build_report(json.loads(GOLD.read_text(encoding="utf-8")))
    opts.output.parent.mkdir(parents=True, exist_ok=True)
    opts.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["totals"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
