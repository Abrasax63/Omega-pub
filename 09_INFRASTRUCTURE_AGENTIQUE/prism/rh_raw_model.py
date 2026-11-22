"""OMEGA-RH-RAW-01: run a real local CPU model on untouched PDF page text.

No M/B/C annotations, expected dependencies, answer keys, or prepared semantic
features are supplied to inference. The model gets only the original extracted
page and generic research-reader instructions. Omega post-checks literal quotes,
never certifies mathematical meaning. Outputs require separate blind human review.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from urllib.request import Request, urlopen
from urllib.error import URLError

BENCHMARK_ID = "OMEGA-RH-RAW-01"
MODEL = "Qwen2.5-0.5B-Instruct-Q4_K_M"
MAX_BYTES = 18000
PROMPTS = {
    "source_reading": (
        "Read the scientific source independently. Identify its main claims, "
        "what is actually established in this document, and any assumptions, "
        "quoted results, incomplete proofs, or limitations that matter. "
        "Do not use knowledge outside the source. Do not guess. "
        "Return only a JSON object with fields "
        "'claims' (array of objects with 'claim', 'status', 'evidence'), "
        "'uncertainties' (array of strings), and 'confidence' (low/medium/high). "
        "Each evidence value must be a continuous verbatim quote from the text. "
        "If nothing is supported, return empty claims."
    ),
    "creative_reinterpretation": (
        "Read the scientific source independently and try an alternative way "
        "to represent or test one mathematical idea. Suggest one precise, "
        "falsifiable hypothesis or structural reformulation. "
        "Do not claim a new theorem or proof. Return only a JSON object "
        "with fields 'proposal', 'assumptions', 'invariant', 'counterexample_test', "
        "'evidence', 'limitations'. The evidence must be one continuous "
        "verbatim excerpt from the source. If you cannot find a meaningful "
        "candidate, set proposal to null. "
        "Do not use prior solved examples or any expected answers."
    ),
}


def read_raw_page(path):
    path = Path(path)
    if not path.is_file() or path.is_symlink():
        raise ValueError("Raw PDF text is missing or symlinked")
    raw = path.read_bytes()
    if not 200 <= len(raw) <= MAX_BYTES:
        raise ValueError("Unusually short/long original source page; cannot silently trim")
    text = raw.decode("utf-8")
    if not text.strip() or "\x00" in text:
        raise ValueError("Nontext or empty source")
    return text, sha256(raw).hexdigest()


def call_server(base_url, page_text, instruction, timeout=180):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You are an independent scientific reader. No other source or annotations are available."},
            {"role": "user", "content": instruction + "\n\n--- ORIGINAL SOURCE PAGE ---\n" + page_text + "\n--- END ORIGINAL SOURCE PAGE ---"},
        ],
        "temperature": 0,
        "max_tokens": 384,
        "seed": 721,
        "stream": False,
    }
    req = Request(base_url.rstrip("/") + "/v1/chat/completions",
                  data=json.dumps(payload).encode("utf-8"),
                  headers={"Content-Type": "application/json"}, method="POST")
    started = time.monotonic()
    with urlopen(req, timeout=timeout) as response:
        answer = json.load(response)
    content = answer["choices"][0]["message"]["content"]
    if not isinstance(content, str):
        raise ValueError("Model returned non-text content")
    return content, round(time.monotonic() - started, 3), answer.get("usage", {})


def safe_json(text):
    # Accept only the whole JSON object; no extraction of 'good bits' from
    # unverifiable surrounding reasoning or extraneous content.
    try:
        obj = json.loads(text.strip())
        return obj if isinstance(obj, dict) else None
    except (ValueError, TypeError):
        return None


def attest(raw_text, model_output, task):
    """Citation validity is mechanical, NOT a semantic truth judgement."""
    obj = safe_json(model_output)
    if obj is None:
        return {
            "syntax": "INVALID_JSON", "claims_seen": 0,
            "accepted_exact_source_citations": 0,
            "quarantined": [],
            "semantic_truth": "NOT_EVALUATED",
            "next_step": "BLIND_HUMAN_REVIEW",
        }
    if task == "source_reading":
        claims = obj.get("claims")
        if not isinstance(claims, list) or len(claims) > 20:
            return {"syntax": "INVALID_CLAIM_STRUCTURE", "semantic_truth": "NOT_EVALUATED",
                    "accepted_exact_source_citations": 0, "claims_seen": 0, "quarantined": []}
        items = [{"claim": x.get("claim"), "evidence": x.get("evidence")}
                 for x in claims if isinstance(x, dict)]
    else:
        items = [{"claim": obj.get("proposal"), "evidence": obj.get("evidence")}]
    accepted, rejected = [], []
    for claim in items:
        quote = claim.get("evidence")
        title = claim.get("claim")
        ok = isinstance(quote, str) and len(quote.strip()) >= 18 and quote in raw_text
        if not isinstance(title, str) or not title.strip():
            ok = False
        if ok:
            accepted.append({"claim": title[:1500],
                             "source_quote_sha256": sha256(quote.encode("utf-8")).hexdigest(),
                             "quote_length": len(quote)})
        else:
            rejected.append({"reason": "NO_UNIQUE_LITERAL_SOURCE_QUOTE_OR_EMPTY_CLAIM",
                             "claim_preview": title[:100] if isinstance(title, str) else None})
    return {
        "syntax": "JSON_PARSED",
        "claims_seen": len(items),
        "accepted_exact_source_citations": len(accepted),
        "quarantined": rejected,
        "accepted_source_attribution_only": accepted,
        "semantic_truth": "NOT_EVALUATED",
        "mathematical_entailment": "NOT_EVALUATED",
        "novelty": "NOT_EVALUATED",
        "next_step": "BLIND_HUMAN_REVIEW",
    }


def execute(page_paths, pdf_sha256, base_url, output_dir):
    if not re.fullmatch(r"[0-9a-f]{64}", pdf_sha256):
        raise ValueError("Source PDF fingerprint must be a SHA-256")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cases = []
    for page_number, path in sorted(page_paths.items()):
        source, source_hash = read_raw_page(path)
        for task, instruction in PROMPTS.items():
            output, seconds, usage = call_server(base_url, source, instruction)
            guard = attest(source, output, task)
            item = {
                "page": page_number, "task": task,
                "source_pdf_sha256": pdf_sha256,
                "source_page_sha256": source_hash,
                "source_characters": len(source),
                "instructions_sha256": sha256(instruction.encode()).hexdigest(),
                "model": MODEL, "model_output": output,
                "tokens": usage, "inference_seconds": seconds,
                "omega_postcheck": guard,
                "gold_visible_to_model": False,
                "semantic_gold": "UNAVAILABLE_FOR_MODEL",
                "status": "RAW_UNASSISTED_GENERATION_AWAITING_SEMANTIC_REVIEW",
            }
            cases.append(item)
    result = {
        "benchmark": BENCHMARK_ID,
        "status": "RAW_MODEL_INFERENCE_COMPLETED_NOT_SEMANTICALLY_CERTIFIED",
        "source_pdf_sha256": pdf_sha256,
        "model_calls": len(cases),
        "model": MODEL,
        "prompt_is_topic_agnostic": True,
        "annotations_supplied_to_model": 0,
        "preparsed_dependencies_supplied_to_model": 0,
        "omega_verification": "LITERAL_QUOTE_ONLY_NO_SEMANTIC_CERTIFICATION",
        "model_output_and_attestations": cases,
        "scientific_discoveries": 0,
        "proof_of_RH": False,
        "human_blind_semantic_review_required": True,
    }
    (out / "report.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--page-2", type=Path, required=True)
    p.add_argument("--page-3", type=Path, required=True)
    p.add_argument("--pdf-sha256", required=True)
    p.add_argument("--server", default="http://127.0.0.1:8080")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = execute({2: args.page_2, 3: args.page_3}, args.pdf_sha256,
                     args.server, args.output)
    print(json.dumps({
        "status": result["status"], "calls": result["model_calls"],
        "pages": [2, 3], "model": result["model"],
        "citations_accepted": sum(x["omega_postcheck"]["accepted_exact_source_citations"]
                                  for x in result["model_output_and_attestations"]),
        "semantic_understanding_certified": False,
    }))


if __name__ == "__main__":
    main()
