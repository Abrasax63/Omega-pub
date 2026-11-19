#!/usr/bin/env python3
"""Reader15: posthoc Qwen Coder 3B ablation, same source-anchored line selector.

LLM input is untrusted; no source claim can be created from generated text.
No rule promotion, no external paid API.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
import time
import traceback
import urllib.request

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reader_bridge14"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))
from selector import (
    GOLD, MODEL_REVISION, ROOT, build_prompt, evaluate_document,
    parse_selection, proposal_from_lines,
)
from read import packetize, safe_read
from gate import gate
from run_experiment import score, select_packets

MODEL = "Qwen2.5-Coder-3B-Instruct-Q4_K_M"
GGUF_SHA256 = "724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7"
LLAMA_CPP_SHA = "5a4afd80779ba51166b59986e61a0bfbb9e1a4c6"
URL = "http://127.0.0.1:8091/v1/chat/completions"
MAX_NEW_TOKENS = 64


def messages_for(candidates: list[dict]) -> list[dict]:
    return [
        {"role": "system", "content": "Choisis seulement des numéros de lignes. Réponds NONE ou une liste d'entiers séparés par des virgules."},
        {"role": "user", "content": build_prompt(candidates)},
    ]


def call_local(messages: list[dict], timeout: int = 240) -> dict:
    payload = {
        "messages": messages, "max_tokens": MAX_NEW_TOKENS,
        "temperature": 0, "stream": False,
    }
    req = urllib.request.Request(
        URL, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        method="POST", headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read(150000))
    seconds = round(time.perf_counter() - t0, 3)
    if not isinstance(data, dict) or not data.get("choices"):
        raise ValueError("LOCAL_MODEL_MISSING_CHOICES")
    choice = data["choices"][0]
    text = choice["message"]["content"]
    if not isinstance(text, str):
        raise ValueError("LOCAL_MODEL_NON_TEXT")
    return {
        "raw_reply": text, "seconds": seconds,
        "token_usage": data.get("usage"),
        "finish_reason": choice.get("finish_reason"),
        "server_model": data.get("model"),
    }


def evaluate(ref: dict, call=call_local) -> dict:
    """Every number proposed by the model is checked against verified source IDs."""
    report = evaluate_document(ref)  # frozen Reader14 mechanical controls
    candidates = report["candidates"]
    if not candidates:
        report["model_3b"] = {"status": "NO_CANDIDATES", "selected": []}
        return report
    generated = call(messages_for(candidates))
    chosen, invalid = parse_selection(generated["raw_reply"],
                                      {c["line"] for c in candidates})
    result = {
        "status": "REPLY_REJECTED" if invalid else "REPLY_VALID",
        "selected": chosen,
        "selection_error": invalid,
        "messages": messages_for(candidates),
        **generated,
    }
    if invalid is None:
        raw = safe_read(ROOT / ref["path"], ref["blob"])
        source = ROOT / ref["path"]
        proposed = proposal_from_lines(ref, candidates, chosen)
        staged = gate(raw, str(source), proposed, provider="reader15-qwen-coder-3b")
        if staged["rejected_count"] or staged["automatic_promotions"] or staged["horn_rules"]:
            raise AssertionError("MODEL_CITATION_RECONSTRUCTION_OR_CERTIFICATION_ERROR")
        result["accepted_count"] = staged["accepted_count"]
        result["metrics"] = score(
            staged, ref, select_packets(packetize(raw, str(source))),
            raw.decode("utf-8").splitlines()
        )
        result["semantic_fidelity_verified"] = False
        result["mathematical_validity_verified"] = False
    report["model_3b"] = result
    return report


def main():
    arg = argparse.ArgumentParser()
    arg.add_argument("--output", type=Path, required=True)
    args = arg.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "experiment": "OMEGA_READER15_3B_POSTHOC_ABLATION",
        "status": "STARTED", "model": MODEL,
        "gguf_sha256_expected": GGUF_SHA256,
        "llama_cpp_sha_expected": LLAMA_CPP_SHA,
        "original_reader14_0p5b_sha": MODEL_REVISION,
        "same_input_and_prompt_as_reader14": True,
        "causal_attribution_to_size_only": False,
        "dataset_blind": False, "annotation_independent": False,
        "auto_certifications": 0, "auto_horn_rules": 0,
        "paid_api_calls": 0,
        "rows": [],
    }
    error = None
    try:
        for ref in json.loads(GOLD.read_text(encoding="utf-8"))["documents"]:
            row = evaluate(ref)
            report["rows"].append(row)
            print(ref["id"], row["model_3b"]["status"],
                  repr(row["model_3b"].get("raw_reply")), flush=True)
        report["status"] = "FINISHED_REAL_LOCAL_INFERENCE"
    except Exception:
        error = traceback.format_exc()
        report["status"] = "FAILED_NOT_SCIENTIFIC_RESULT"
        report["exception"] = error
    finally:
        args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
        print("REPORT", args.output, report["status"], flush=True)
    if error:
        sys.exit(1)


if __name__ == "__main__":
    main()
