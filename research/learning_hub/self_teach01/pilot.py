"""OMEGA-SELF-TEACH-01. Real local Qwen interface, bounded curriculum and A/B candidates.

Never imports sealed evaluation data. Model cannot run programs or write to Git.
All generated code is tested through the existing restricted Python sandbox (#232).
"""
from __future__ import annotations
import argparse
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "learning_lab"))
import prog_reconstruction_pilot as safe

PINS = {
    "TRAIN_FROZEN.json": "e315498e1be93e5f057aa62495f464a5b84f0998",
    "EVAL_PUBLIC_FROZEN.json": "5c842ebbefe3b42d053d03918fea8156f00aa3e8",
    "EVAL_SEALED_FROZEN.json": "e3dbc45c2bf35cb0557837fd42fe030306f60730",
}
EVAL_CAP = 660
LESSON_CAP = 160
SCHEMA = "OMEGA_SELF_TEACH_RAW_01"


def git_blob(raw: bytes) -> str:
    return sha1(b"blob " + str(len(raw)).encode() + b"\x00" + raw).hexdigest()


def load_frozen(name: str) -> dict:
    if name not in PINS:
        raise ValueError("UNKNOWN_FROZEN_FILE")
    p = HERE / name
    raw = p.read_bytes()
    if len(raw) > 60000 or git_blob(raw) != PINS[name]:
        raise ValueError("FROZEN_DATA_TAMPERED")
    return json.loads(raw)


def public_contract() -> tuple[list, list]:
    train = load_frozen("TRAIN_FROZEN.json")
    eval_public = load_frozen("EVAL_PUBLIC_FROZEN.json")
    if train.get("schema") != "OMEGA_SELF_TEACH_TRAIN_01":
        raise ValueError("TRAIN_SCHEMA")
    if eval_public.get("schema") != "OMEGA_SELF_TEACH_EVAL_PUBLIC_01":
        raise ValueError("EVAL_SCHEMA")
    t, e = train["train"], eval_public["evaluation"]
    if len(t) != 2 or len(e) != 3:
        raise ValueError("COHORT_SIZE")
    families = [x["family"] for x in t+e]
    ids = [x["id"] for x in t+e]
    if len(set(families)) != 5 or len(set(ids)) != 5:
        raise ValueError("TRAIN_EVAL_OVERLAP")
    for task in t+e:
        if len(task["public_examples"]) < 2 or not task["goal"]:
            raise ValueError("PUBLIC_CASES_INCOMPLETE")
    for task in t:
        if len(task["development_cases"]) < 5:
            raise ValueError("DEVELOPMENT_INCOMPLETE")
        if set(x["input"] for x in task["public_examples"]) & set(
                x["input"] for x in task["development_cases"]):
            raise ValueError("TRAIN_DEV_OVERLAP")
    return t, e


def inspect_code(raw: str) -> tuple[str | None, str]:
    code = safe.parse_code(raw)
    if code is None:
        return None, "INVALID_JSON_OR_CODE"
    try:
        safe.validate_program(code)
    except ValueError as exc:
        return None, "UNSAFE_OR_INVALID_CODE:" + str(exc)
    return code, "SAFE_PYTHON"


def score_public(code: str | None, cases: list) -> dict:
    outputs = (safe.execute_student(code, [x["input"] for x in cases])
               if code is not None else [{"error": "NO_CODE"} for _ in cases])
    rows = []
    for case, actual in zip(cases, outputs):
        rows.append({
            "input": case["input"], "expected": case["expected"],
            "received": actual, "correct": actual.get("value") == case["expected"]
        })
    return {"correct": sum(x["correct"] for x in rows), "total": len(rows),
            "rows": rows}


def prompt_for(task, memory=None) -> str:
    prompt = ("Reconstruct the requested Python string function using only the goal "
              "and the public examples. Return a JSON object with key 'code' "
              "containing exactly one complete def transform(s): returning a list "
              "of strings. No imports, network, files or extra code.\nGOAL: " +
              task["goal"] + "\nEXAMPLES: " +
              json.dumps(task["public_examples"], ensure_ascii=False))
    if memory:
        prompt += ("\nVERIFIED PRACTICE NOTE (limited practice cases; not a proof "
                   "of transfer): " + memory)
    return prompt


def generate(client, task, tag, memory=None) -> dict:
    raw = client(
        [{"role": "system", "content": safe.SYSTEM},
         {"role": "user", "content": prompt_for(task, memory)}],
        EVAL_CAP, tag)
    code, status = inspect_code(raw)
    return {"id": task["id"], "family": task["family"],
            "raw": raw, "code": code, "status": status,
            "sha256_raw": sha256(raw.encode()).hexdigest(),
            "memory_used": bool(memory)}


def build_memory(client, train: list) -> tuple[dict, dict]:
    # The learning policy selects the weakest of two initial, model-produced attempts.
    attempts = []
    for item in train:
        proposed = generate(client, item, "train:" + item["id"] + ":initial")
        dev = score_public(proposed["code"], item["development_cases"])
        attempts.append({"candidate": proposed, "dev": dev})
    selected_index = min(range(len(train)),
                         key=lambda i: (attempts[i]["dev"]["correct"] /
                                        attempts[i]["dev"]["total"], train[i]["id"]))
    item, previous = train[selected_index], attempts[selected_index]
    feedback = [x for x in previous["dev"]["rows"] if not x["correct"]][:3]
    repair_prompt = (
        prompt_for(item) + "\nPREVIOUS CODE: " +
        json.dumps(previous["candidate"]["code"]) +
        "\nDEVELOPMENT FEEDBACK: " + json.dumps(feedback) +
        "\nReturn the COMPLETE corrected function as a JSON 'code' field.")
    corrected_raw = client(
        [{"role": "system", "content": safe.SYSTEM},
         {"role": "user", "content": repair_prompt}],
        EVAL_CAP, "train:" + item["id"] + ":repair")
    corrected_code, corrected_status = inspect_code(corrected_raw)
    corrected_dev = score_public(corrected_code, item["development_cases"])
    improved = (corrected_code is not None and
                corrected_dev["correct"] == corrected_dev["total"] and
                corrected_dev["correct"] > previous["dev"]["correct"])
    memory = ""
    lesson_raw = None
    if improved:
        lesson_raw = client(
            [{"role": "system", "content": safe.SYSTEM},
             {"role": "user", "content":
              "Based only on this verified practice experience, give a concise "
              "reusable programming lesson, no code or specific algorithm. "
              "Respond JSON {'lesson': string, max 240 characters}. "
              "The local tests are limited, not proof of general correctness. "
              "Goal: " + item["goal"] + "\nVerified code: " + corrected_code +
              "\nTest result: " + str(corrected_dev["correct"]) + "/" +
              str(corrected_dev["total"])}],
            LESSON_CAP, "train:" + item["id"] + ":lesson")
        obj = safe.parse_json(lesson_raw)
        candidate_lesson = obj.get("lesson") if obj else None
        if isinstance(candidate_lesson, str) and 8 <= len(candidate_lesson) <= 240:
            memory = candidate_lesson
    learning = {
        "attempts": [{"id": t["id"], "initial_correct": a["dev"]["correct"],
                      "initial_total": a["dev"]["total"], "initial_code": a["candidate"]["code"]}
                     for t, a in zip(train, attempts)],
        "self_selected_task": item["id"],
        "selection_policy": "LOWEST_INITIAL_DEVELOPMENT_SCORE",
        "revised_code": corrected_code,
        "revised_status": corrected_status,
        "revised_correct": corrected_dev["correct"],
        "revised_total": corrected_dev["total"],
        "improvement_on_practice": improved,
        "lesson_raw": lesson_raw,
        "admitted_memory": memory,
        "memory_status": ("LIMITED_DEV_VERIFIED_CANDIDATE_LESSON" if memory
                          else "NO_ADMISSIBLE_MEMORY"),
        "test_gold_used_for_selection": False,
        "model_parameters_updated": False,
    }
    return learning, {"train_llm_calls": len(attempts) + 1 + (1 if improved else 0)}


def run(client) -> dict:
    train, evaluation = public_contract()
    t = time.monotonic()
    # No sealed dataset import, access or scoring in this module.
    direct = [generate(client, item, "A:" + item["id"]) for item in evaluation]
    learning, train_usage = build_memory(client, train)
    memory = learning["admitted_memory"]
    remembered = [generate(client, item, "B:" + item["id"], memory)
                  for item in evaluation]
    call_log = getattr(client, "call_log", None)
    return {
        "schema": SCHEMA, "status": "GENERATED_NOT_SCORED",
        "frozen_git_blob_sha1": PINS, "model": safe.MODEL,
        "inference_cap_per_eval_task": EVAL_CAP,
        "A": direct, "B": remembered, "learning": learning,
        "C": {"status": "TRAINING_NOT_AUTHORIZED",
              "reason": "INSUFFICIENT_INDEPENDENT_VERIFIED_SAMPLES_AND_FRESH_HOLDOUT",
              "new_weight_updates": 0},
        "train_usage": train_usage,
        "eval_calls_each": len(evaluation),
        "total_model_calls": (len(call_log) if call_log is not None else None),
        "client_call_log": call_log,
        "elapsed_seconds": round(time.monotonic()-t, 3),
        "paid_api_calls": 0,
        "sealed_gold_opened_during_generation": False,
        "main_modified": False,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    report = run(safe.Client(args.server))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n",
                           encoding="utf-8")
    print("SELF_TEACH_01_GENERATED", report["learning"]["memory_status"],
          "calls", report["total_model_calls"], flush=True)


if __name__ == "__main__":
    main()
