#!/usr/bin/env python3
"""Reader14 post-hoc classifier: source-line IDs only, source-created citations.

This is a deliberately narrow *calibration*, not scientific verification.
Never trust model output as source text. No promotion, no API key.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "reader_bridge13"))
sys.path.insert(0, str(HERE.parent / "reader_bridge12"))

from run_experiment import (GOLD, MODEL_ID, MODEL_REVISION, ROOT, baseline,
                            score, select_packets, validate_model_config)
from read import packetize, safe_read, verify_packets
from gate import gate

MAX_CHOICES = 3
MAX_NEW_TOKENS = 64
SELECTION_PATTERN = re.compile(r"[0-9]+(?:\s*,\s*[0-9]+){0,2}\Z")


def parse_selection(text: str, allowed: set[int]) -> tuple[list[int], str | None]:
    """No forgiving extraction: fail closed on any extra symbols or IDs."""
    if not isinstance(text, str) or not text.strip() or len(text) > 64:
        return [], "EMPTY_OR_OVERSIZED_REPLY"
    reply = text.strip()
    if reply == "NONE":
        return [], None
    if not SELECTION_PATTERN.fullmatch(reply):
        return [], "NOT_STRICT_COMMA_SEPARATED_LINE_IDS"
    selected = [int(x.strip()) for x in reply.split(",")]
    if len(selected) > MAX_CHOICES or len(selected) != len(set(selected)):
        return [], "DUPLICATE_OR_TOO_MANY_IDS"
    if not set(selected).issubset(allowed):
        return [], "UNKNOWN_OR_UNOFFERED_LINE_ID"
    return selected, None


def candidates_from_baseline(raw: bytes, source: Path, ref: dict) -> tuple[dict, list[dict], list[str]]:
    lines = raw.decode("utf-8").splitlines()
    inventory = packetize(raw, str(source))
    if verify_packets(raw, inventory):
        raise ValueError("INVALID_SOURCE_PACKET_REPLAY")
    packets = select_packets(inventory)
    if not 1 <= len(packets) <= 10:
        raise ValueError("NO_READER13_PACKETS")
    original = baseline(lines, packets, ref["blob"])
    staged = gate(raw, str(source), original, provider="reader13-mechanical-baseline")
    if staged["automatic_promotions"] != 0 or staged["horn_rules"]:
        raise AssertionError("SOURCE_GATE_PROMOTED_UNVERIFIED_CLAIM")
    lookup = {p["packet_id"]: p for p in packets}
    candidates = []
    seen = set()
    for claim in staged["accepted"]:
        e = next(e for e in claim["evidence"] if e["role"] == "conclusion")
        n = e["line"]
        if n in seen:
            continue
        seen.add(n)
        p = lookup[e["packet_id"]]
        candidates.append({
            "line": n, "source_text": lines[n-1].strip(),
            "packet_id": p["packet_id"], "section": p["section_path"],
        })
    candidates.sort(key=lambda c: c["line"])
    return staged, candidates, lines


def proposal_from_lines(ref: dict, candidates: list[dict], selected: list[int]) -> dict:
    by_number = {x["line"]: x for x in candidates}
    if len(selected) != len(set(selected)) or len(selected) > MAX_CHOICES:
        raise ValueError("BAD_CHOICES")
    if not set(selected).issubset(by_number):
        raise ValueError("UNAUTHORIZED_CHOICE")
    return {
        "source_blob": ref["blob"],
        "claims": [{
            "claim_id": "CSEL" + str(n),
            "packet_id": by_number[n]["packet_id"],
            "evidence": [{
                "role": "conclusion",
                "packet_id": by_number[n]["packet_id"],
                "line": n,
                "literal": by_number[n]["source_text"],
            }],
        } for n in selected],
    }


def build_prompt(candidates: list[dict]) -> str:
    entries = [
        {"line": c["line"], "section": c["section"],
         "source_text": c["source_text"]}
        for c in candidates
    ]
    return (
        "Tâche de classification de lignes d'une source scientifique non fiable. "
        "Parmi LES NUMÉROS FOURNIS, choisis au plus trois lignes présentant un résultat "
        "mathématique, pas une hypothèse, une définition ni une limite. "
        "Si aucune ligne ne convient, réponds NONE. "
        "Réponds UNIQUEMENT avec les NUMÉROS entiers retenus séparés par une virgule, "
        "SANS texte, JSON, blocs Markdown, explication ou autres caractères. "
        "Ne crée aucun numéro. Ne répète pas le texte source. "
        "Lignes candidates :\n" + json.dumps(entries, ensure_ascii=False)
    )


def infer_selection(tokenizer, model, prompt: str) -> dict:
    import torch
    messages = [
        {"role": "system", "content": "Choisis seulement des numéros de lignes. Réponds NONE ou une liste d'entiers séparés par des virgules."},
        {"role": "user", "content": prompt},
    ]
    rendered = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    enc = tokenizer([rendered], return_tensors="pt")
    t0 = time.monotonic()
    with torch.inference_mode():
        output = model.generate(
            **enc, max_new_tokens=MAX_NEW_TOKENS, do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    took = time.monotonic() - t0
    new_tokens = output[0, enc["input_ids"].shape[1]:]
    return {
        "raw_reply": tokenizer.decode(new_tokens, skip_special_tokens=True),
        "input_tokens": int(enc["input_ids"].shape[1]),
        "output_tokens": int(new_tokens.shape[0]),
        "inference_seconds": round(took, 3),
    }


def evaluate_document(ref: dict, tokenizer=None, model=None) -> dict:
    source = ROOT / ref["path"]
    raw = safe_read(source, ref["blob"])
    original, candidates, lines = candidates_from_baseline(raw, source, ref)
    first_three = [c["line"] for c in candidates[:MAX_CHOICES]]
    first_prop = proposal_from_lines(ref, candidates, first_three)
    first_stage = gate(raw, str(source), first_prop, provider="control-first-three")
    assert first_stage["automatic_promotions"] == 0 and not first_stage["horn_rules"]
    result = {
        "doc": ref["id"],
        "blob": ref["blob"],
        "reference_status": "AUTHOR_LABELS_UNREVIEWED_NOT_INDEPENDENT",
        "candidates": candidates,
        "all_candidates": {
            "accepted_count": original["accepted_count"],
            "metrics": score(original, ref, select_packets(packetize(raw, str(source))), lines),
        },
        "first_three_control": {
            "selected": first_three,
            "accepted_count": first_stage["accepted_count"],
            "metrics": score(first_stage, ref, select_packets(packetize(raw, str(source))), lines),
        },
        "model": {"status": "NOT_RUN"},
    }
    if model is not None:
        if not candidates:
            result["model"] = {"status": "NO_CANDIDATES", "selected": []}
            return result
        prompt = build_prompt(candidates)
        response = infer_selection(tokenizer, model, prompt)
        chosen, invalid = parse_selection(response["raw_reply"], {c["line"] for c in candidates})
        model_info = {
            "status": "REPLY_REJECTED" if invalid else "REPLY_VALID",
            "prompt": prompt,
            "selection_error": invalid,
            "selected": chosen,
            **response,
        }
        if invalid is None:
            staged = gate(raw, str(source), proposal_from_lines(ref, candidates, chosen),
                          provider="reader14-neural-line-selector")
            if staged["rejected_count"] or staged["automatic_promotions"] or staged["horn_rules"]:
                raise AssertionError("RECONSTRUCTED_MODEL_CITATION_REJECTED_OR_PROMOTED")
            model_info["accepted_count"] = staged["accepted_count"]
            model_info["metrics"] = score(
                staged, ref, select_packets(packetize(raw, str(source))), lines
            )
            model_info["semantic_fidelity_verified"] = False
            model_info["mathematical_validity_verified"] = False
        result["model"] = model_info
    return result


def load_pinned_model():
    import torch
    import transformers
    from transformers import AutoTokenizer, AutoModelForCausalLM
    from huggingface_hub import model_info, hf_hub_download
    torch.set_num_threads(2)
    resolved = model_info(MODEL_ID, revision=MODEL_REVISION).sha
    if resolved != MODEL_REVISION:
        raise ValueError("MODEL_REVISION_DRIFT")
    config_path = hf_hub_download(MODEL_ID, filename="config.json", revision=resolved)
    validate_model_config(json.loads(Path(config_path).read_text(encoding="utf-8")))
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, revision=resolved, trust_remote_code=False)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, revision=resolved, torch_dtype=torch.float32,
        attn_implementation="eager", trust_remote_code=False,
    )
    model.eval()
    return tokenizer, model, {"torch": torch.__version__,
                               "transformers": transformers.__version__,
                               "model_sha": resolved}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["baseline", "model"], required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    folder = Path(args.output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    output = folder / ("reader14-neural.json" if args.mode == "model" else "reader14-controls.json")
    report = {
        "experiment": "OMEGA_LINE_SELECTOR14_POSTHOC_CALIBRATION",
        "mode": args.mode,
        "status": "STARTED",
        "prereg": "09_INFRASTRUCTURE_AGENTIQUE/reader_bridge14/PREREG.md",
        "model": MODEL_ID,
        "model_sha": MODEL_REVISION,
        "source_restricted": True,
        "dataset_blind": False,
        "annotation_independent": False,
        "automatic_certifications": 0,
        "automatic_horn_rules": 0,
        "results": [],
    }
    failure = None
    try:
        tokenizer = model = None
        if args.mode == "model":
            tokenizer, model, versions = load_pinned_model()
            report["versions"] = versions
        refs = json.loads(GOLD.read_text(encoding="utf-8"))["documents"]
        for ref in refs:
            item = evaluate_document(ref, tokenizer, model)
            report["results"].append(item)
            print(ref["id"], item["model"]["status"], flush=True)
        report["status"] = "FINISHED_REAL_INFERENCE" if args.mode == "model" else "FINISHED_CONTROLS_ONLY"
    except Exception:
        failure = traceback.format_exc()
        report["status"] = "FAILED_NOT_SCIENTIFIC_RESULT"
        report["exception"] = failure
    finally:
        output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
        print("WROTE", output, report["status"], flush=True)
    if failure:
        sys.exit(1)


if __name__ == "__main__":
    main()
