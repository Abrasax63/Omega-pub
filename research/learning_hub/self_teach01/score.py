"""OMEGA-SELF-TEACH-01 blinded scoring; sealed gold only opened AFTER generation."""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import pilot


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def score_arm(rows, gold):
    exact = safe = abstain = silent = full = 0
    per_task = []
    for generated, target in zip(rows, gold):
        require(generated.get("id") == target["id"] and
                generated.get("family") == target["family"],
                "MISALIGNED_TEST_TASKS")
        raw = generated.get("raw")
        require(isinstance(raw, str) and
                sha256(raw.encode()).hexdigest() == generated.get("sha256_raw"),
                "MODEL_OUTPUT_TAMPERED")
        code, status = pilot.inspect_code(raw)
        require(code == generated.get("code") and
                status == generated.get("status"),
                "UNTRUSTED_GENERATED_CODE")
        cases = target["hidden_cases"]
        if code:
            safe += 1
        else:
            abstain += 1
        result = pilot.score_public(code, cases)
        correct = result["correct"]
        exact += correct
        passed = correct == len(cases)
        full += int(passed)
        if code and not passed:
            silent += 1
        per_task.append({"id": target["id"], "family": target["family"],
                         "safe": bool(code), "correct": correct,
                         "total": len(cases), "fully_correct": passed,
                         "raw_sha256": generated["sha256_raw"]})
    return {"tests_exact": exact, "tests_total": sum(len(x["hidden_cases"]) for x in gold),
            "fully_correct": full, "tasks_total": len(gold),
            "safe_programs": safe, "abstentions": abstain,
            "silent_functional_errors": silent, "rows": per_task}


def score_report(report):
    require(report.get("schema") == pilot.SCHEMA, "REPORT_SCHEMA")
    require(report.get("status") == "GENERATED_NOT_SCORED",
            "REPORT_ALREADY_SCORED")
    require(report.get("frozen_git_blob_sha1") == pilot.PINS,
            "FROZEN_SHA_MANIFEST")
    require(report.get("C", {}).get("status") == "TRAINING_NOT_AUTHORIZED" and
            report["C"].get("new_weight_updates") == 0,
            "ILLEGAL_AUTOMATIC_TRAINING")
    require(report.get("sealed_gold_opened_during_generation") is False,
            "SEALED_GOLD_USED_DURING_GENERATION")
    require(report.get("eval_calls_each") == 3 and
            report.get("inference_cap_per_eval_task") == pilot.EVAL_CAP,
            "UNEQUAL_EVAL_CALL_BUDGET")
    learn = report.get("learning", {})
    memory = learn.get("admitted_memory", "")
    require(type(memory) is str and len(memory) <= 240,
            "UNBOUNDED_MEMORY")
    if memory:
        require(learn.get("improvement_on_practice") is True and
                learn.get("revised_correct") == learn.get("revised_total") and
                learn.get("memory_status") == "LIMITED_DEV_VERIFIED_CANDIDATE_LESSON",
                "MEMORY_ADMITTED_WITHOUT_VERIFICATION")
    require(learn.get("test_gold_used_for_selection") is False and
            learn.get("model_parameters_updated") is False,
            "INVALID_LEARNING_PROVENANCE")
    public = pilot.load_frozen("EVAL_PUBLIC_FROZEN.json")["evaluation"]
    sealed = pilot.load_frozen("EVAL_SEALED_FROZEN.json")
    require(sealed.get("schema") == "OMEGA_SELF_TEACH_EVAL_SEALED_01",
            "SEALED_SCHEMA")
    gold = sealed["holdout"]
    require(len(gold) == 3 and len(public) == 3, "SEALED_TASK_COUNT")
    for a, b in zip(public, gold):
        require(a["id"] == b["id"] and a["family"] == b["family"] and
                len(b["hidden_cases"]) == 5, "TEST_ALIGNMENT")
        require(not {x["input"] for x in a["public_examples"]} &
                {x["input"] for x in b["hidden_cases"]}, "PUBLIC_TEST_LEAK")
    A, B = report.get("A", []), report.get("B", [])
    require(len(A) == len(B) == len(gold), "MISSING_EVALUATION_ARM")
    for a in A:
        require(a.get("memory_used") is False, "A_HAS_MEMORY")
    for b in B:
        require(b.get("memory_used") is bool(memory), "B_MEMORY_PROVENANCE")
    score_a = score_arm(A, gold)
    score_b = score_arm(B, gold)
    regressions = sum(x["fully_correct"] and not y["fully_correct"]
                      for x, y in zip(score_a["rows"], score_b["rows"]))
    delta = score_b["tests_exact"] - score_a["tests_exact"]
    status = ("EXPLORATORY_MEMORY_GAIN_NOT_GENERALIZATION"
              if delta > 0 and regressions == 0
              else "NO_POSITIVE_TRANSFER_DEMONSTRATED")
    return {
        "schema": "OMEGA_SELF_TEACH_SCORE_01", "status": status,
        "A": score_a, "B": score_b, "C": report["C"],
        "delta_exact_tests_B_minus_A": delta,
        "A_full_tasks_regressed_in_B": regressions,
        "memory_admitted": bool(memory),
        "self_selected_training_task": learn["self_selected_task"],
        "number_of_model_calls": report["total_model_calls"],
        "wall_seconds": report["elapsed_seconds"],
        "hidden_eval_after_generation_only": True,
        "fresh_holdout_consumed_after_scoring": True,
        "A_B_input_context_equal": False,
        "causal_autonomous_learning_proven": False,
        "generalization_proven": False,
        "main_modified": False,
        "paid_api_calls": 0,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    data = json.loads(args.raw.read_text(encoding="utf-8"))
    result = score_report(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
    print("SELF_TEACH_01_RESULT", result["status"],
          "A", result["A"]["tests_exact"], "B", result["B"]["tests_exact"],
          "of", result["A"]["tests_total"], flush=True)


if __name__ == "__main__":
    main()
