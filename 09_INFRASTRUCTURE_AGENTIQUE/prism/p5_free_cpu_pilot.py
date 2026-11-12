"""Public, no-paid-API CPU inference pilot for the Omega P5 A/B/C methods.

This executes a real local open-weight model on a remote GitHub Actions runner.
Only six explicitly public exercises are used, NEVER the P5 private holdout.
No OpenAI API/credentials; no grading of the private P5 benchmark.
The same shared prompt, model and generation cap apply to all three arms.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import argparse
import json
import random
import re
from pathlib import Path
from time import perf_counter

from p5_v05_private_runner import build_triplet

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
MAX_NEW_TOKENS = 80
ORDER_SEED = 20261112
ARMS = ("A", "B", "C")
STATUS = "PUBLIC_CPU_PILOT_NOT_PRIVATE_P5_NOT_INDEPENDENT"
# These public exercises are deliberately elementary calibration only.
# Their answers are in the harness, never sent to the model.
PUBLIC_CASES = (
    ("MATH-01", "mathematical", "NON",
     "Sur X={0,1,2,3}, f est totale, f(0)=1, f(1)=2 et f(2)=3. "
     "La valeur f(3) est inconnue. Toutes les extensions sont-elles "
     "nécessairement injectives ? Réponds OUI ou NON."),
    ("MATH-02", "mathematical", "OUI",
     "Sur X={0,1}, f(0)=1 et f(1)=0. Cette fonction est-elle "
     "injective ? Réponds OUI ou NON."),
    ("CRT-01", "computational", "8",
     "Trouve le plus petit entier x >= 0 qui satisfait x modulo 3 = 2 "
     "et x modulo 5 = 3. Réponds par un nombre entier."),
    ("CRT-02", "computational", "9",
     "Trouve le plus petit entier x >= 0 qui satisfait x modulo 4 = 1 "
     "et x modulo 6 = 3. Réponds par un nombre entier."),
    ("DATA-01", "computational", "B",
     "Groupe A : 9 succès sur 10 en strate 1 et 10 succès sur 100 "
     "en strate 2. Groupe B : 80 succès sur 100 en strate 1 et "
     "0 succès sur 10 en strate 2. Qui a le meilleur taux global, "
     "A ou B ?"),
    ("DATA-02", "computational", "A",
     "Groupe A : 7 succès sur 10 en strate 1 et 2 sur 10 en "
     "strate 2. Groupe B : 1 succès sur 10 en strate 1 et "
     "1 sur 10 en strate 2. Qui a le meilleur taux global, A ou B ?"),
)
FINAL_MARKER = "Réponse finale :"

def case_request(case, arm):
    case_id, mission_type, _gold, question = case
    if arm not in ARMS:
        raise ValueError("invalid arm")
    # Deliberately exclude gold from all model-visible input.
    visible = {
        "case_id": "P5V05-" + case_id,
        "mission_type": mission_type,
        "question": question,
        "documents": [],
    }
    return build_triplet(visible)[arm]

def make_messages(case, arm):
    request = case_request(case, arm)
    payload = json.dumps(request["input"], sort_keys=True,
                         ensure_ascii=False, separators=(",", ":"))
    # Identical suffix for every arm. Only the strategy varies.
    return [
        {"role": "system", "content": request["instructions"]},
        {"role": "user", "content": (
            payload + "\nDonne une justification brève, puis termine "
            "par une ligne : " + FINAL_MARKER + " <OUI|NON|A|B|entier>.")},
    ]

def extract_answer(text):
    # Conservative parser; the absence of a compliant last line is ungraded.
    if not isinstance(text, str):
        return None
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None
    match = re.fullmatch(
        r"Réponse finale\s*:\s*(OUI|NON|A|B|[0-9]+)\s*\.?\s*",
        lines[-1], flags=re.IGNORECASE,
    )
    return match.group(1).upper() if match else None

def schedule():
    rng = random.Random(ORDER_SEED)
    ids = list(range(len(PUBLIC_CASES)))
    rng.shuffle(ids)
    work = []
    for i in ids:
        arms = list(ARMS)
        rng.shuffle(arms)
        work.extend((i, arm) for arm in arms)
    assert len(work) == 18
    return work

def preflight():
    rows = []
    for case in PUBLIC_CASES:
        shared = []
        for arm in ARMS:
            msg = make_messages(case, arm)
            obj = case_request(case, arm)["input"]["shared"]
            shared.append(json.dumps(obj, sort_keys=True, ensure_ascii=False))
            rows.append({
                "case": case[0], "arm": arm,
                "prompt_sha256": sha256(json.dumps(
                    msg, ensure_ascii=False, sort_keys=True
                ).encode("utf-8")).hexdigest(),
            })
            assert case[2] not in json.dumps(obj.get("documents",[]))
        assert len(set(shared)) == 1
    return {
        "status": "NO_PROVIDER_CALL_PREFLIGHT",
        "public_cases": len(PUBLIC_CASES),
        "planned_local_generations": len(rows),
        "arms": list(ARMS), "model": MODEL_ID,
        "max_new_tokens": MAX_NEW_TOKENS,
        "max_paid_api_calls": 0,
        "private_holdout_accessed": False,
        "rows": rows,
    }

def run(output_path):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    torch.set_num_threads(2)
    torch.manual_seed(ORDER_SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, torch_dtype=torch.float32
    ).eval()
    outputs = []
    for index, arm in schedule():
        case = PUBLIC_CASES[index]
        messages = make_messages(case, arm)
        rendered = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([rendered], return_tensors="pt")
        started = perf_counter()
        with torch.inference_mode():
            predictions = model.generate(
                **model_inputs,
                do_sample=False,
                max_new_tokens=MAX_NEW_TOKENS,
                pad_token_id=tokenizer.eos_token_id,
            )
        latency = perf_counter() - started
        input_length = model_inputs["input_ids"].shape[1]
        output_tokens = predictions[0][input_length:]
        text = tokenizer.decode(output_tokens, skip_special_tokens=True)
        answer = extract_answer(text)
        outputs.append({
            "case_id": case[0], "arm": arm,
            "model_output": text,
            "extracted_answer": answer,
            "reference_answer": case[2],
            "strict_match": answer == case[2],
            "input_tokens": int(input_length),
            "output_tokens": int(output_tokens.shape[0]),
            "latency_seconds": round(latency, 3),
            "prompt_sha256": sha256(json.dumps(
                messages, sort_keys=True, ensure_ascii=False,
            ).encode("utf-8")).hexdigest(),
        })
        print("PUBLIC_MODEL_GENERATION case=%s arm=%s match=%s" %
              (case[0], arm, answer == case[2]), flush=True)
    per_arm = {}
    for arm in ARMS:
        rows = [row for row in outputs if row["arm"] == arm]
        per_arm[arm] = {
            "strict_matches": sum(row["strict_match"] for row in rows),
            "cases": len(rows),
            "input_tokens": sum(row["input_tokens"] for row in rows),
            "output_tokens": sum(row["output_tokens"] for row in rows),
            "duration_seconds": round(sum(
                row["latency_seconds"] for row in rows), 3),
        }
    result = {
        "status": STATUS,
        "test_type": "public_illustrative_six_case_pilot",
        "not_private_p5": True, "independent_grading": False,
        "no_paid_api": True, "model_id": MODEL_ID,
        "model_revision": getattr(model.config, "_commit_hash", None),
        "seed": ORDER_SEED, "greedy": True,
        "same_output_cap": MAX_NEW_TOKENS,
        "per_arm": per_arm, "rows": outputs,
        "interpretation": (
            "Exploratory six-case local small-model comparison; "
            "not an independent holdout or GPT-6/Omega proof."),
    }
    dest = Path(output_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(
        result, ensure_ascii=False, indent=2, sort_keys=True
    )+"\n", encoding="utf-8")
    print("P5_PUBLIC_CPU_RESULT "+json.dumps({
        "status": STATUS, "model": MODEL_ID, "per_arm": per_arm
    }, ensure_ascii=False), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--output", default="p5_public_cpu_results.json")
    args = parser.parse_args()
    if args.preflight:
        print(json.dumps(preflight(), ensure_ascii=False, sort_keys=True))
    else:
        run(args.output)

if __name__ == "__main__":
    main()
