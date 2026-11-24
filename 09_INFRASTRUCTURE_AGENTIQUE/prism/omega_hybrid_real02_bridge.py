"""Fail-closed adapter: actual REAL-02 report -> hybrid D/M/N exact scorer.

No network/model calls. Old reports stay unchanged; compare on fresh holdouts
only. Split attestation is not independent evidence of blindness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
from omega_hybrid_lab import evaluate_holdout
from omega_memory_real02 import TARGETS


def score_real02(report: dict, frozen_split_sha256: str) -> dict:
    blocked = {"status": "BLOCKED", "scientific_claims_certified": 0,
               "new_competence_demonstrated": False}
    if not isinstance(report, dict) or not isinstance(frozen_split_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", frozen_split_sha256):
        return {**blocked, "reason": "MISSING_FROZEN_SPLIT_ID"}
    if report.get("stage") != "EVALUATED" or (report.get("memory") or {}).get("status") != "COMPLETE":
        return {**blocked, "reason": "NO_COMPLETED_REAL02_MODEL_EVALUATION"}
    fidelity = report.get("bounded_fidelity") or {}
    target = fidelity.get("target")
    if fidelity.get("bounded_pass") is not True or target not in TARGETS:
        return {**blocked, "reason": "BOUNDED_FIDELITY_NOT_VALIDATED"}
    if not isinstance(report.get("candidate_id_reloaded"), str) or not report["candidate_id_reloaded"]:
        return {**blocked, "reason": "NO_PERSISTED_MEMORY_RELOAD"}
    source = report.get("source") or {}
    if not isinstance(source.get("source_sha256"), str) or not re.fullmatch(r"[0-9a-f]{64}", source["source_sha256"]):
        return {**blocked, "reason": "SOURCE_HASH_NOT_ARCHIVED"}
    tasks = report["memory"].get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 4:
        return {**blocked, "reason": "UNEXPECTED_REAL02_HOLDOUT_SIZE"}
    converted = []
    for i, t in enumerate(tasks):
        arms = t.get("arms") if isinstance(t, dict) else None
        if not isinstance(arms, dict) or set(arms) != {"D", "M", "N"}:
            return {**blocked, "reason": "MISSING_REAL_MODEL_ARM"}
        outputs, tokens = {}, {}
        for arm in ("D", "M", "N"):
            item = arms[arm]
            if not isinstance(item, dict) or not isinstance(item.get("usage"), dict):
                return {**blocked, "reason": "MISSING_REAL_TOKEN_ACCOUNTING"}
            outputs[arm] = item.get("raw")
            tokens[arm] = item["usage"].get("prompt_tokens")
        converted.append({"id": str(t.get("id", i)), "edges": t.get("edges"),
                          "outputs": outputs, "prompt_tokens": tokens})
    scored = evaluate_holdout({"protocol_frozen": True, "source_disjoint": True,
                               "trials": converted}, TARGETS[target])
    if scored.get("status") != "SCORED_DESCRIPTIVE_ONLY":
        return {**blocked, "reason": "RECALCULATION_BLOCKED", "detail": scored}
    if any(row["oracle_boolean_truth"] is not t.get("oracle_holds")
           for row, t in zip(scored["cases"], tasks)):
        return {**blocked, "reason": "ORACLE_TRUTH_MISMATCH"}
    return {"status": "REAL02_RESCORING_COMPLETE_DESCRIPTIVE_ONLY",
            "frozen_split_sha256": frozen_split_sha256,
            "split_independence": "DECLARED_NOT_EXTERNALLY_VERIFIED",
            "candidate_id_reloaded": report["candidate_id_reloaded"],
            "score": scored, "scientific_claims_certified": 0,
            "new_competence_demonstrated": False,
            "model_weights_updated": False}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, required=True,
                    help="Full REAL-02 report.json; not a prefilled example")
    ap.add_argument("--frozen-split-sha256", required=True,
                    help="Pre-run independently retained SHA-256 of the holdout manifest")
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    original = json.loads(args.report.read_text(encoding="utf-8"))
    score = score_real02(original, args.frozen_split_sha256)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(score, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": score["status"], "reason": score.get("reason"),
                      "scientific_claims_certified": 0}))


if __name__ == "__main__":
    main()
