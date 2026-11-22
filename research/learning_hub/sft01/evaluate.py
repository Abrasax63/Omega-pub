"""Evaluate the trained and base SmolLM2 models on frozen Python tasks.

This script is separate from the trainer and is the ONLY code that imports
holdout gold. Generated code runs only in the existing restricted V1 sandbox.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
import traceback

from data_guard import MODEL, MODEL_REV, SYSTEM, GEN_TOKENS, load_holdout, PINS, SEED

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "learning_lab"))
import prog_reconstruction_pilot as sandbox

def file_sha(path):
    h = sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_generated(raw):
    if not isinstance(raw, str) or len(raw) > sandbox.MAX_CODE_CHARS:
        return None, "FORMAT_SIZE"
    source = raw.strip()
    if source.startswith("~~~"):
        parts = source.split("\n")
        if len(parts) >= 3 and parts[-1].strip() == "~~~":
            source = "\n".join(parts[1:-1]).strip()
    if source.startswith("```"):
        parts = source.split("\n")
        if len(parts) >= 3 and parts[-1].strip() == "```":
            source = "\n".join(parts[1:-1]).strip()
    if not source.startswith("def transform(s):"):
        return None, "NO_COMPLETE_FUNCTION"
    try:
        sandbox.validate_program(source)
    except ValueError as e:
        return None, "SYNTAX_OR_POLICY:" + str(e)
    return source, "SAFE_PYTHON"

def evaluate_generated(item, raw):
    code, state = parse_generated(raw)
    cases = item["hidden_cases"]
    got = (sandbox.execute_student(code, [x["input"] for x in cases])
           if code is not None else [{"error": state} for _ in cases])
    details = [{"input": case["input"], "expected": case["expected"],
                "received": result, "correct": result.get("value") == case["expected"]}
               for case, result in zip(cases, got)]
    count = sum(x["correct"] for x in details)
    return {"id": item["id"], "family": item["family"], "raw_output": raw,
            "raw_sha256": sha256(raw.encode()).hexdigest(),
            "code_status": state, "python_safe": state == "SAFE_PYTHON",
            "correct_hidden": count, "complete_correct": count == len(cases),
            "tests": details}

def infer(model, tokenizer, item):
    import torch
    prompt = tokenizer.apply_chat_template(
        [{"role": "system", "content": SYSTEM},
         {"role": "user", "content": item["prompt"]}],
        tokenize=False, add_generation_prompt=True)
    tokens = tokenizer(prompt, return_tensors="pt", add_special_tokens=False)["input_ids"]
    with torch.no_grad():
        generated = model.generate(
            input_ids=tokens, do_sample=False, max_new_tokens=GEN_TOKENS,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id)
    output = tokenizer.decode(generated[0, tokens.shape[1]:], skip_special_tokens=True)
    return output, int(tokens.shape[1]), int(generated.shape[1] - tokens.shape[1])

def run(train_dir, report_path):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    root = Path(train_dir)
    training = json.loads((root / "train_manifest.json").read_text())
    if (training.get("status") != "ACTUAL_LORA_WEIGHTS_TRAINED" or
        training.get("steps") != 124 or training.get("training_examples") != 62 or
        training.get("source_train_git_blob_sha1") != PINS["TRAIN_FROZEN.json"] or
        training.get("weight_delta_L2", 0) <= 0 or
        training.get("model_revision") != MODEL_REV or
        training.get("holdout_loaded_by_training_script") is not False):
        raise ValueError("TRAINING_MANIFEST_INVALID")
    for name, digest in training["safetensor_sha256"].items():
        if file_sha(root / "adapter" / name) != digest:
            raise ValueError("ADAPTER_CHECKSUM_MISMATCH")
    cases = load_holdout()  # In this job only, AFTER verified training.
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=MODEL_REV, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=MODEL_REV, torch_dtype=torch.float32,
        trust_remote_code=False).to("cpu")
    base.eval()
    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = {"protocol": "OMEGA-PY-SFT-01", "status": "STARTED",
              "source_train_sha1": PINS["TRAIN_FROZEN.json"],
              "source_holdout_sha1": PINS["HOLDOUT_EVAL_ONLY.json"],
              "model_revision": MODEL_REV,
              "real_training_delta_L2": training["weight_delta_L2"],
              "weight_updates_during_evaluation": 0,
              "hidden_cases_seen_by_training": False,
              "before": {"rows": []}, "after": {"rows": []}}
    def save():
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    save()
    for arm in ("before", "after"):
        model = base if arm == "before" else PeftModel.from_pretrained(
            base, str(root / "adapter"), is_trainable=False)
        model.eval()
        begin = time.monotonic()
        for item in cases:
            raw, prompt_n, generated_n = infer(model, tokenizer, item)
            row = evaluate_generated(item, raw)
            row.update({"prompt_tokens": prompt_n, "generated_tokens": generated_n})
            report[arm]["rows"].append(row)
            save()
        report[arm]["seconds"] = round(time.monotonic() - begin, 3)
        report[arm]["syntax_and_policy_valid"] = sum(
            row["python_safe"] for row in report[arm]["rows"])
        report[arm]["fully_correct"] = sum(
            row["complete_correct"] for row in report[arm]["rows"])
        report[arm]["partially_correct_cases"] = sum(
            row["correct_hidden"] for row in report[arm]["rows"])
        report[arm]["input_tokens"] = sum(row["prompt_tokens"] for row in report[arm]["rows"])
        report[arm]["output_tokens"] = sum(row["generated_tokens"] for row in report[arm]["rows"])
        save()
    before, after = report["before"], report["after"]
    report["comparison"] = {
        "same_12_test_prompts": True, "same_generation_budget": True,
        "before_correct": before["fully_correct"],
        "after_correct": after["fully_correct"],
        "delta_correct": after["fully_correct"] - before["fully_correct"],
        "before_safe_python": before["syntax_and_policy_valid"],
        "after_safe_python": after["syntax_and_policy_valid"],
        "regressions": sum(a["complete_correct"] and not b["complete_correct"]
                           for a, b in zip(before["rows"], after["rows"])),
        "new_correct": sum(not a["complete_correct"] and b["complete_correct"]
                            for a, b in zip(before["rows"], after["rows"])),
        "new_independent_model_capability_proven": False,
        "model_wrote_its_own_training_labels": False,
        "holdout_became_consumed_after_scoring": True}
    if (after["fully_correct"] > before["fully_correct"] and
        after["syntax_and_policy_valid"] >= before["syntax_and_policy_valid"]):
        report["status"] = "EXPLORATORY_GAIN_ONLY"
    else:
        report["status"] = "TRAINED_NO_CLEAR_FUNCTIONAL_GAIN"
    save()
    print("OMEGA_PY_SFT01_EVAL", report["status"], "exact",
          before["fully_correct"], after["fully_correct"], "valid",
          before["syntax_and_policy_valid"], after["syntax_and_policy_valid"],
          flush=True)
    return report

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--training-artifact", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    try:
        run(a.training_artifact, a.output)
    except Exception:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        (a.output.parent / "eval_error.json").write_text(
            json.dumps({"status": "INDETERMINATE_TECHNICAL_FAILURE",
                        "traceback": traceback.format_exc()}, indent=2))
        raise

if __name__ == "__main__":
    main()
