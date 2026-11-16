"""Post-freeze oracle: score frozen A/B rankings against actual historical code change.

Runs only in a separate CI job after a SHA-256 commitment to rankings. This does
not execute third-party code, test behavioral correctness, or train any model.
"""
from __future__ import annotations
import argparse
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path

from localize import BUGGY_COMMIT, ROOT_PACKAGE, TEST_PATH, sha


def function_diff_targets(buggy: Path, fixed: Path, manifest: dict) -> dict:
    entries = manifest["targets"]
    by_file = {}
    for t in entries:
        by_file.setdefault(t["file"], []).append(t)
    bfiles = set(manifest["source_file_hashes"])
    newfiles = {p.relative_to(fixed).as_posix() for p in
                (fixed / ROOT_PACKAGE).rglob("*.py")}
    affected = set()
    changed = []
    excluded = []
    for rel in sorted(bfiles | newfiles):
        b = buggy / rel
        f = fixed / rel
        if not b.is_file() or not f.is_file():
            excluded.append({"file": rel, "reason": "ADDED_OR_REMOVED_FILE"})
            continue
        before = b.read_text(encoding="utf-8").splitlines()
        after = f.read_text(encoding="utf-8").splitlines()
        if before == after:
            continue
        hunks = 0
        file_affected = set()
        for op,i1,i2,j1,j2 in SequenceMatcher(
                a=before,b=after,autojunk=False).get_opcodes():
            if op == "equal":
                continue
            hunks += 1
            if op == "insert":
                # Insertion between old lines has an ambiguous boundary.
                hits = [t for t in by_file.get(rel, []) if
                        t["line"] < i1+1 <= t["end_line"]]
                if len(hits) != 1:
                    excluded.append({"file": rel, "reason": "INSERT_BOUNDARY_AMBIGUOUS",
                                     "old_line": i1+1})
                    continue
            else:
                hits = [t for t in by_file.get(rel, []) if
                        t["line"] <= i2 and t["end_line"] >= i1+1]
                if not hits:
                    excluded.append({"file": rel, "reason": "CHANGED_OUTSIDE_SCANNED_FUNCTION",
                                     "old_lines": [i1+1, i2]})
                    continue
            file_affected.update(t["key"] for t in hits)
            affected.update(t["key"] for t in hits)
        changed.append({"file": rel, "hunks": hunks,
                        "identified_targets": sorted(file_affected)})
    return {
      "changed_files": changed,
      "unresolved_changes": excluded,
      "oracle_target_keys": sorted(affected),
    }


def evaluate(manifest_bytes: bytes, expected_sha: str,
             buggy: Path, fixed: Path) -> dict:
    if sha(manifest_bytes) != expected_sha:
        raise ValueError("MANIFEST_DRIFT")
    manifest = json.loads(manifest_bytes)
    if manifest.get("status") != "CHOICES_FROZEN" or manifest.get("phase") != "BUGGY_ONLY_TEST_AST_LOCALIZATION":
        raise ValueError("UNFROZEN_LOCALIZATION")
    if manifest["buggy_commit"] != BUGGY_COMMIT:
        raise ValueError("BUGGY_COMMIT_MISMATCH")
    if sha((buggy / TEST_PATH).read_bytes()) != manifest["test_sha256"]:
        raise ValueError("BUGGY_TEST_DRIFT")
    for rel, recorded in manifest["source_file_hashes"].items():
        if sha((buggy / rel).read_bytes()) != recorded:
            raise ValueError("BUGGY_SOURCE_DRIFT:" + rel)
    if len(set(t["key"] for t in manifest["targets"])) != len(manifest["targets"]):
        raise ValueError("DUPLICATE_KEYS")
    oracle = function_diff_targets(buggy, fixed, manifest)
    targets = {t["key"]:t for t in manifest["targets"]}
    keys = oracle["oracle_target_keys"]
    ranks_a = [targets[k]["rank_a"] for k in keys]
    ranks_b = [targets[k]["rank_b"] for k in keys]
    scores = {}
    for name, ranks in (("A_baseline",ranks_a),("B_test_ast",ranks_b)):
        scores[name] = {
          "best_rank": min(ranks) if ranks else None,
          "hit_at_5": bool(ranks and min(ranks) <= 5),
          "hit_at_10": bool(ranks and min(ranks) <= 10),
          "hit_at_20": bool(ranks and min(ranks) <= 20),
          "changed_targets_at_10": sum(r <= 10 for r in ranks),
          "changed_targets_total": len(ranks),
        }
    if not keys:
        result = "ORACLE_OUT_OF_SCOPE"
    elif oracle["unresolved_changes"]:
        result = "ORACLE_PARTIAL_NO_COMPARATIVE_CLAIM"
    else:
        a = scores["A_baseline"]["hit_at_10"]
        b = scores["B_test_ast"]["hit_at_10"]
        result = ("GAIN_LOCAL_UNIQUE_CASE" if b and not a else
                  "REGRESSION_LOCAL_UNIQUE_CASE" if a and not b else
                  "NO_DIFFERENCE")
    return {
      "experiment": "OMEGA-MECHANISM-LOC-01",
      "phase": "ORACLE_REVEALED_AFTER_SHA_FROZEN",
      "status": result,
      "buggy_commit": BUGGY_COMMIT,
      "fixed_commit": "5300b0b490b8db48fac30b5e32164be93dc574b7",
      "frozen_manifest_sha256": expected_sha,
      "target_inventory_size": len(targets),
      "oracle": oracle,
      "scores": scores,
      "same_function_budget": True,
      "primary_budget_per_arm": 10,
      "test_suite_executed": False,
      "historical_reproducer_verified": False,
      "model_called": False,
      "patch_generated": False,
      "repair_correctness": None,
      "independent_blind_generalization_verified": False,
      "main_modified": False,
      "limitations": [
        "Diff-derived AST localization is not a functional repair or a traceback-based causal diagnosis.",
        "One previously selected public historical case provides no generalization estimate.",
        "Fixed source was only accessed after a frozen ranking artifact in a separate job.",
        "Runtime pytest, Python 3.7.3, and historical dependency restoration were not executed.",
      ],
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--buggy-checkout", type=Path, required=True)
    p.add_argument("--fixed-checkout", type=Path, required=True)
    p.add_argument("--frozen-manifest", type=Path, required=True)
    p.add_argument("--expected-sha256", type=str, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = evaluate(args.frozen_manifest.read_bytes(), args.expected_sha256,
                      args.buggy_checkout, args.fixed_checkout)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2,
                                      ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
      "status":result["status"],
      "oracle_targets":len(result["oracle"]["oracle_target_keys"]),
      "unresolved_changes":len(result["oracle"]["unresolved_changes"]),
      "baseline":result["scores"]["A_baseline"],
      "test_ast":result["scores"]["B_test_ast"],
      "result_sha256":sha(args.output.read_bytes()),
    },sort_keys=True))


if __name__=="__main__":
    main()
