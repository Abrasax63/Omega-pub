"""OMEGA-RH-RAW-02: unseen original pages, constrained output syntax only.

Follow-up after RAW-01 format failures. No source-specific semantic hints,
lemmas, claims, dependencies, label sets or prior expected answers passed.
The local model must independently identify the meaning, or abstain.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

from rh_raw_model import read_raw_page, attest

FROZEN_PDF_SHA256 = "667d88b3c375adf0466678094f452ca966aef0f4d368f6340d2bd5328b7fb706"
FROZEN_MODEL_SHA256 = "6eb923e7d26e9cea28811e1a8e852009b21242fb157b26149d3b188f3a8c8653"
MODEL = "Qwen2.5-0.5B-Instruct-Q4_K_M"
PROMPTS = {
 "source_reading": (
   "Read the following page from a mathematical draft. Without outside knowledge "
   "or guessing, identify at most TWO important mathematical statements. "
   "For each, say in ordinary language what is supported, what is uncertain, "
   "and copy one exact continuous quote from the page. "
   "Respond only with JSON: "
   '{"claims":[{"claim":"...","status":"...","evidence":"..."}],'
   '"uncertainties":["..."],"confidence":"low"}' 
   ". If nothing is supported, claims must be an empty list. "
   "Do not infer proof from the mere mention of a theorem."
 ),
 "creative_reinterpretation": (
   "Using only this page, either suggest ONE precise alternative representation "
   "or falsifiable research idea, or abstain. "
   "State assumptions and a counterexample test, and copy one short exact "
   "continuous source quote. Do not claim a new proof or theorem. "
   "Respond only with JSON: "
   '{"proposal":null,"assumptions":"","invariant":"","counterexample_test":"",'
   '"evidence":"","limitations":""}' 
   ". Replace null with a specific proposal only when grounded by the page."
 ),
}


def invoke(text, instruction, endpoint, timeout=180):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Independent scientific reader. Use only the supplied original text."},
            {"role": "user", "content": instruction + "\n\n--- ORIGINAL SOURCE PAGE ---\n" + text + "\n--- END SOURCE ---"},
        ],
        # This constrains JSON syntax, not mathematical semantics.
        "response_format": {"type": "json_object"},
        "temperature": 0, "seed": 721, "max_tokens": 512, "stream": False,
    }
    req = Request(endpoint.rstrip("/") + "/v1/chat/completions",
                  data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"},
                  method="POST")
    before = time.monotonic()
    with urlopen(req, timeout=timeout) as response:
        data = json.load(response)
    return (data["choices"][0]["message"]["content"],
            round(time.monotonic() - before, 3),
            data.get("usage", {}))


def run(page_paths, pdf_sha256, model_sha256, endpoint, output_dir):
    if pdf_sha256 != FROZEN_PDF_SHA256 or model_sha256 != FROZEN_MODEL_SHA256:
        raise ValueError("Source/model changed; cannot compare across pilot versions")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for page_number, page_path in sorted(page_paths.items()):
        raw, page_sha = read_raw_page(page_path)
        for task, prompt in PROMPTS.items():
            answer, seconds, usage = invoke(raw, prompt, endpoint)
            rows.append({
                "page": page_number, "task": task,
                "original_pdf_sha256": pdf_sha256,
                "original_page_sha256": page_sha,
                "model_file_sha256": model_sha256,
                "prompt_sha256": sha256(prompt.encode()).hexdigest(),
                "raw_unedited_model_answer": answer,
                "model_usage": usage, "inference_seconds": seconds,
                "omega_literal_citation_gate": attest(raw, answer, task),
                "semantic_review": "NOT_DONE",
                "candidate_thesis_certified": False,
            })
    report = {
        "benchmark": "OMEGA-RH-RAW-02",
        "status": "RAW_UNPRECHEWED_SCHEMA_CONTROLLED_PENDING_SEMANTIC_REVIEW",
        "reason_for_new_version": "RAW-01 four outputs violated JSON and generation length constraints",
        "source_pages": [4, 5], "new_pages_not_used_in_RAW_01": True,
        "no_semantic_hints": True, "manual_claims_given_to_model": 0,
        "json_mode_changes_only_output_format": True,
        "model_calls": len(rows), "rows": rows,
        "scientific_claims_certified": 0, "understanding_certified": False,
    }
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--page-4",required=True,type=Path)
    p.add_argument("--page-5",required=True,type=Path)
    p.add_argument("--pdf-sha256",required=True)
    p.add_argument("--model-sha256",required=True)
    p.add_argument("--server",default="http://127.0.0.1:8080")
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    result=run({4:a.page_4,5:a.page_5},a.pdf_sha256,a.model_sha256,a.server,a.output)
    print(json.dumps({
        "benchmark":result["benchmark"],"calls":result["model_calls"],
        "valid_json":sum(x["omega_literal_citation_gate"]["syntax"]=="JSON_PARSED"
                         for x in result["rows"]),
        "exact_quotes":sum(x["omega_literal_citation_gate"]["accepted_exact_source_citations"]
                           for x in result["rows"]),
        "semantic_understanding_certified":False,
    }))


if __name__=="__main__":
    main()
