"""Run original vs saved SFT01 LoRA vs fixed symbolic repair on NEW faults.

No optimizer and NO new gradient. Prior model adapter is read from an already
successful, independently verified GitHub Actions run.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "sft01"))
from data_guard import MODEL, MODEL_REV, SYSTEM, GEN_TOKENS, SEED, PINS
import core


def file_hash(path):
    h = sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_adapter(root):
    root = Path(root)
    manifest_path = root / "train_manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if (data.get("status") != "ACTUAL_LORA_WEIGHTS_TRAINED"
            or data.get("model") != MODEL
            or data.get("model_revision") != MODEL_REV
            or data.get("source_train_git_blob_sha1") != PINS["TRAIN_FROZEN.json"]
            or data.get("steps") != 124 or data.get("training_examples") != 62
            or data.get("weight_delta_L2", 0) <= 0
            or data.get("holdout_loaded_by_training_script") is not False):
        raise ValueError("UNTRUSTED_OR_DIFFERENT_ADAPTER")
    hashes = data.get("safetensor_sha256", {})
    if not hashes or not any(x.endswith(".safetensors") for x in hashes):
        raise ValueError("MISSING_TRAINED_WEIGHTS")
    for name, digest in hashes.items():
        if file_hash(root / "adapter" / name) != digest:
            raise ValueError("CHANGED_ADAPTER_WEIGHTS")
    return data


def infer(model, tokenizer, prompt):
    import torch
    text = tokenizer.apply_chat_template(
        [{"role": "system", "content": SYSTEM},
         {"role": "user", "content": prompt}],
        tokenize=False, add_generation_prompt=True)
    tokens = tokenizer(text, add_special_tokens=False,
                       return_tensors="pt")["input_ids"]
    begin = time.monotonic()
    with torch.no_grad():
        generation = model.generate(
            input_ids=tokens, do_sample=False, max_new_tokens=GEN_TOKENS,
            pad_token_id=tokenizer.eos_token_id,
            eos_token_id=tokenizer.eos_token_id)
    elapsed = round(time.monotonic() - begin, 3)
    raw = tokenizer.decode(generation[0, tokens.shape[1]:],
                           skip_special_tokens=True)
    return {"raw": raw, "prompt_tokens": int(tokens.shape[1]),
            "generated_tokens": int(generation.shape[1] - tokens.shape[1]),
            "seconds": elapsed}


def run(adapter_root, output_dir):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from peft import PeftModel

    training = check_adapter(adapter_root)
    cases = core.frozen_cases()  # gold stays in trusted evaluator, not prompts
    public = core.public_only(cases)
    torch.set_num_threads(2)
    torch.manual_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(
        MODEL, revision=MODEL_REV, trust_remote_code=False)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        MODEL, revision=MODEL_REV, torch_dtype=torch.float32,
        trust_remote_code=False).to("cpu")
    base.eval()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction_path = output_dir / "raw_predictions.json"
    predictions = {case["id"]: {} for case in public}

    def save_predictions():
        prediction_path.write_text(
            json.dumps({"protocol": core.PROTOCOL, "source_run": core.SOURCE_RUN,
                        "status": "NO_HIDDEN_SCORES_COLLECTED_YET",
                        "predictions": predictions}, indent=2,
                       ensure_ascii=False) + "\n", encoding="utf-8")

    save_predictions()
    # All base outputs FIRST, no peek at any hidden answers.
    for i, case in enumerate(public):
        predictions[case["id"]]["base"] = infer(base, tokenizer, case["prompt"])
        save_predictions()
        print("SEMANTIC04_BASE_GENERATED", i + 1, len(public), flush=True)

    adapted = PeftModel.from_pretrained(base,
                                       str(Path(adapter_root) / "adapter"),
                                       is_trainable=False)
    adapted.eval()
    for i, case in enumerate(public):
        predictions[case["id"]]["lora"] = infer(
            adapted, tokenizer, case["prompt"])
        save_predictions()
        print("SEMANTIC04_LORA_GENERATED", i + 1, len(public), flush=True)

    for i, case in enumerate(public):
        # This function signature deliberately does not accept hidden cases.
        predictions[case["id"]]["symbolic"] = core.symbolic(
            case["broken"], case["public"])
        save_predictions()
    # Only now do we use the frozen hidden tests to score all 3 arms.
    report = core.score(cases, predictions)
    report.update({
        "adapter_source_run": core.SOURCE_RUN,
        "adapter_training_steps": training["steps"],
        "adapter_weight_delta_L2": training["weight_delta_L2"],
        "adapter_safetensor_hashes": training["safetensor_sha256"],
        "training_this_run": False,
        "model_revision": MODEL_REV,
        "model_inference_temperature": 0,
        "model_max_new_tokens": GEN_TOKENS,
        "symbolic_mutation_catalog_size": len(core.EDITS),
        "training_inputs_not_extended": True,
        "strict_and_permissive_scored_on_same_generation": True,
        "single_pilot_no_generalization_claim": True})
    p = output_dir / "semantic04_report.json"
    p.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                 encoding="utf-8")
    summary = report["summary"]
    print("SEMANTIC04_RESULT", json.dumps({
        "base_strict": summary["base"]["strict"]["exact_programs"],
        "base_permissive": summary["base"]["permissive"]["exact_programs"],
        "lora_strict": summary["lora"]["strict"]["exact_programs"],
        "lora_permissive": summary["lora"]["permissive"]["exact_programs"],
        "symbolic_exact": summary["symbolic"]["strict"]["exact_programs"],
        "n": 12, "new_training_steps": 0}), flush=True)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        run(args.adapter, args.output)
    except Exception:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "technical_failure.json").write_text(
            json.dumps({"status": "TECHNICAL_FAILURE_NO_SCIENTIFIC_CONCLUSION",
                        "traceback": traceback.format_exc()}, indent=2))
        raise


if __name__ == "__main__":
    main()
