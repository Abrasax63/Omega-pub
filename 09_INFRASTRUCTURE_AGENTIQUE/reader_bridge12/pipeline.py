#!/usr/bin/env python3
"""Omega 12 read -> optional untrusted proposer -> quarantine -> manual verifier.

No output is promoted to the historical rule library. With --run-known-v11
the existing finite oracle is run ONLY against its prior human contract, and
its output is explicitly not credited to the proposal model.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from read import run as read_document
from gate import gate

ROOT = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
V7_BLOB = "6c482f97345abbb7f3d5bcd5e20da96259b276ce"


def pipeline(source: Path, sha: str, *, model_json: dict | None = None,
             provider: str = "none", approved_manual_v11: bool = False) -> dict:
    doc = read_document(source, sha)
    raw = source.read_bytes()
    if model_json is None:
        model_json = {"source_blob": sha, "claims": []}
    staged = gate(raw, source.as_posix(), model_json, provider=provider)
    if staged["automatic_promotions"] or staged["horn_rules"]:
        raise ValueError("unexpected external rule promotion")
    manual_check = {
        "status": "NOT_REQUESTED", "relation_to_model_proposals": "NONE",
    }
    if approved_manual_v11:
        if sha != V7_BLOB:
            raise ValueError("known V11 verifier restricted to its pinned V7 source")
        # Trusted module lives in the same repository, not an arbitrary path.
        import sys
        sys.path.insert(0, str(ROOT / "09_INFRASTRUCTURE_AGENTIQUE/semantic_fidelity10"))
        from finite_oracle11 import evaluate_exact
        original = evaluate_exact()
        manual_check = {
            "status": "REPLAYED_HUMAN_APPROVED_FINITE_CONTRACT",
            "relation_to_model_proposals": "NONE_AUTOMATIC_MAPPING",
            "finite_test_success": original["finite_test_success"],
            "source_to_claim_status": original["source_to_claim_status"],
            "mathematical_mismatch_count": original["mathematical_mismatch_count"],
            "counterexample_controls": len(original["deliberately_false_claims_refuted"]),
            "number_of_total_maps_checked": original["number_of_total_maps_checked"],
            "source_git_blob": original["source_git_blob"],
        }
    return {
        "engine": "OMEGA_READER_VERIFIER_BRIDGE12_READONLY",
        "source_path": source.as_posix(), "source_blob": sha,
        "inventory": doc["stats"],
        "packets": doc["packets"],
        "quarantine": staged,
        "manual_known_oracle": manual_check,
        "final_verdict": "INDETERMINATE_REQUIRES_SEMANTIC_REVIEW",
        "asserted_theorems": [], "published_horn_rules": [],
        "auto_certifications": 0,
    }


def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--source", type=Path, required=True)
    cli.add_argument("--source-blob", required=True)
    cli.add_argument("--mode", choices=("inventory", "fixture", "ollama"),
                     default="inventory")
    cli.add_argument("--model-json", type=Path)
    cli.add_argument("--local-model")
    cli.add_argument("--run-known-v11", action="store_true")
    cli.add_argument("--output", type=Path)
    a = cli.parse_args()
    if a.mode == "fixture":
        if a.model_json is None or a.model_json.stat().st_size > 100000:
            cli.error("fixture mode requires a JSON file <= 100kB")
        model_data = json.loads(a.model_json.read_text(encoding="utf-8"))
    elif a.mode == "ollama":
        if not a.local_model:
            cli.error("ollama mode requires --local-model")
        from model import ollama_generate
        doc = read_document(a.source, a.source_blob)
        model_data = ollama_generate(doc["packets"][:10], a.source_blob, a.local_model)
    else:
        if a.model_json or a.local_model:
            cli.error("inventory mode has no model input")
        model_data = None
    result = pipeline(a.source, a.source_blob, model_json=model_data,
                      provider=a.mode, approved_manual_v11=a.run_known_v11)
    serialized = json.dumps(result, ensure_ascii=False, indent=2)+"\n"
    if a.output:
        dest = a.output.resolve()
        if dest.is_relative_to(ROOT):
            cli.error("output file must be outside repository")
        dest.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
