#!/usr/bin/env python3
"""External FOLIO holdout for unmodified Omega natural_query08.

NO translation, per-case hardcoding, gold-conditioned selection, neural model,
or training. Raw FOLIO English premises are transported as unverified documents.
The original English conclusion is passed to the exact prior French parser.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import tempfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
ROOT = HERE.parents[1]
INPUT = HERE / "FOLIO_VALIDATION_FIRST30_FROZEN.jsonl"
FOLIO_SAMPLE_BLOB = "7aedc646fb2c3588ebd04335fbf74cb56fb32688"
FOLIO_SOURCE_BLOB = "06244bd10b37eac73cba7aca6c336e96011ace58"
ORIGINAL_TRANSLATOR_BLOB = "385aca9258d69c4545df891a31f1c4ae719a82b8"
ORIGINAL_TRANSLATOR = BASE / "natural_query08" / "translator.py"
ORIGINAL_SOURCE_COMMIT = "5d7bb84c7edab3fb358e057d2807f19cf5cf5e2d"

spec = importlib.util.spec_from_file_location("omega_frozen_natural_query08", ORIGINAL_TRANSLATOR)
if spec is None or spec.loader is None:
    raise RuntimeError("prior natural-query translator is missing")
translator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(translator)

REFERENCE = {"True": "SUPPORTED", "False": "CONTRADICTED", "Uncertain": "ABSTAIN"}


class AuditError(ValueError):
    pass


def blob_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def stable_hash(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def load_frozen() -> list[dict]:
    if not INPUT.is_file() or INPUT.is_symlink():
        raise AuditError("input file missing or symlinked")
    raw = INPUT.read_bytes()
    if blob_sha(raw) != FOLIO_SAMPLE_BLOB:
        raise AuditError("external sample modified")
    if blob_sha(ORIGINAL_TRANSLATOR.read_bytes()) != ORIGINAL_TRANSLATOR_BLOB:
        raise AuditError("parent Omega translator modified: no longer a frozen holdout")
    lines = raw.decode("utf-8").splitlines()
    if len(lines) != 30:
        raise AuditError("sample must contain the first 30 unchanged rows")
    rows = [json.loads(line) for line in lines]
    for item in rows:
        if not isinstance(item["premises"], list) or not all(
            isinstance(p, str) for p in item["premises"]
        ) or not isinstance(item["conclusion"], str):
            raise AuditError("external source row invalid")
        if item.get("label") not in REFERENCE:
            raise AuditError("unknown external label")
    return rows


def prepare_document(root: Path, i: int, original: dict) -> dict:
    """Only a transport header is inserted; original premise lines are unchanged."""
    file = root / ("external-%03d.md" % i)
    identifier = "BR-EXT-FOLIO-%03d" % i
    body = "# %s — unverified FOLIO document transport\n" % identifier
    body += "\n".join(original["premises"]) + "\n"
    file.write_text(body, encoding="utf-8")
    return {"id": identifier, "path": file.name,
            "source_blob": blob_sha(file.read_bytes()),
            "premises": original["premises"]}


def run_external() -> dict:
    start = time.perf_counter()
    samples = load_frozen()
    pending = []
    source_infos = []
    with tempfile.TemporaryDirectory(prefix="omega-folio09-") as temp:
        root = Path(temp)
        for index, original in enumerate(samples, 1):
            # Isolate each benchmark theory in its own transport directory;
            # otherwise discovery would also include earlier benchmark cases.
            case_root = root / ("case-%03d" % index)
            case_root.mkdir()
            transport = prepare_document(case_root, index, original)
            documents = translator.logic.discover((case_root,))
            if list(documents) != [transport["id"]]:
                raise AuditError("external document not ingested faithfully")
            mirrored = documents[transport["id"]]["lines"][1:]
            if mirrored != original["premises"]:
                raise AuditError("external premise changed during transport")
            # Only the independent, pre-existing Omega parser receives the
            # original NATURAL conclusion. No FOL notation nor benchmark label.
            conclusion = original["conclusion"]
            try:
                outcome = translator.answer_text(
                    conclusion, documents=documents, case_id="FOLIO-%03d" % index
                )
            except translator.TranslationError as exc:
                outcome = {
                    "id": "FOLIO-%03d" % index,
                    "verdict": "ABSTAIN",
                    "translation_status": "REJECTED_INPUT_CONTRACT",
                    "reason": type(exc).__name__,
                    "typed_query": None,
                    "source_id": None,
                    "certificate_valid": True,
                    "input_sha256": hashlib.sha256(conclusion.encode("utf-8")).hexdigest(),
                    "source_documents_scanned": len(documents),
                }
            if outcome["verdict"] not in ("SUPPORTED", "CONTRADICTED", "ABSTAIN"):
                raise AuditError("invalid model output")
            pending.append(outcome)
            source_infos.append({
                "case": index, "external_document": transport["id"],
                "premises_count": len(transport["premises"]),
                "source_blob": transport["source_blob"],
                "exact_premises_transport": True,
            })

    # Freeze the choices BEFORE reading any reference labels, while making
    # documentation provenance, error status, and abstentions inspectable.
    predictions = [
        {"id": row["id"], "verdict": row["verdict"],
         "translation_status": row["translation_status"],
         "source_id": row.get("source_id"),
         "certificate_valid": row["certificate_valid"]}
        for row in pending
    ]
    pred_hash = stable_hash(predictions)
    print("PREDICTIONS_BEFORE_GOLD_SHA256=" + pred_hash, flush=True)

    scored = []
    for index, (sample, output, provenance) in enumerate(zip(samples, pending, source_infos), 1):
        reference = REFERENCE[sample["label"]]
        scored.append({
            "id": "FOLIO-%03d" % index,
            "external_row": index, "premises_count": len(sample["premises"]),
            "premises_sha256": stable_hash(sample["premises"]),
            "conclusion_sha256": hashlib.sha256(sample["conclusion"].encode("utf-8")).hexdigest(),
            "conclusion_chars": len(sample["conclusion"]),
            "published_label": sample["label"], "mapped_reference": reference,
            "verdict": output["verdict"], "verdict_correct": output["verdict"] == reference,
            "confident_error": output["verdict"] != "ABSTAIN" and output["verdict"] != reference,
            "status": output["translation_status"], "reason": output.get("reason"),
            "translated": output.get("typed_query") is not None,
            "reasoned": output.get("proof_result") is not None,
            "certificate_valid": output["certificate_valid"],
            "document": provenance, "source_claimed": output.get("source_id"),
        })
    answered = sum(x["verdict"] != "ABSTAIN" for x in scored)
    baseline_correct = sum(x["mapped_reference"] == "ABSTAIN" for x in scored)
    correct = sum(x["verdict_correct"] for x in scored)
    bad = sum(x["confident_error"] for x in scored)
    result = {
        "experiment": "OMEGA-EXTERNAL-FOLIO-HOLDOUT-09",
        "status": "TRANSFER_NOT_DEMONSTRATED" if answered == 0 else (
            "PROMISING_EXTERNAL_RESULT_REQUIRES_INDEPENDENT_REPLICATION" if bad == 0 and
            correct > baseline_correct else "NO_ROBUST_EXTERNAL_GAIN"
        ),
        "source": {
            "repository": "Yale-LILY/FOLIO",
            "upstream_commit": ORIGINAL_SOURCE_COMMIT,
            "upstream_file": "data/v0.0/folio-validation.jsonl",
            "upstream_blob": FOLIO_SOURCE_BLOB,
            "selection": "first 30 validation lines in original order",
            "first_line": 1, "last_line": 30,
            "sample_blob": FOLIO_SAMPLE_BLOB,
            "license": "CC BY-SA 4.0; source credited to Yale-LILY/FOLIO",
            "raw_questions_untranslated": True,
            "raw_premises_unchanged": True,
        },
        "model": {
            "baseline": "Omega PR155 frozen exact French grammar",
            "translator_blob": ORIGINAL_TRANSLATOR_BLOB,
            "model_api_calls": 0, "model_weights_modified": False,
            "runtime_tuning": False, "only_transport_headers_added": True,
        },
        "cases": len(samples),
        "distinct_theory_groups": len(set(stable_hash(x["premises"]) for x in samples)),
        "source_documents_loaded": len(source_infos),
        "input_gold_hidden_until_prediction_hash": True,
        "predictions_sha256_before_gold": pred_hash,
        "label_distribution": dict(Counter(x["label"] for x in samples)),
        "translation_status_distribution": dict(Counter(x["status"] for x in scored)),
        "correct": correct,
        "baseline_always_abstain_correct": baseline_correct,
        "answered": answered,
        "abstained": len(samples) - answered,
        "translated": sum(x["translated"] for x in scored),
        "reasoned": sum(x["reasoned"] for x in scored),
        "false_confident": bad,
        "correct_non_abstain": sum(x["verdict"] != "ABSTAIN" and x["verdict_correct"] for x in scored),
        "invalid_certificates": sum(not x["certificate_valid"] for x in scored),
        "elapsed_seconds": round(time.perf_counter() - start, 3),
        "auto_promotion": False,
        "limitations": [
            "FOLIO v0.0 includes potentially noisy human annotations: mapped published labels are not audited truth",
            "30 consecutive questions share only 10 theories; not statistically independent",
            "Full English free-form text is deliberately outside PR155's French and backtick grammar",
            "No external model, Qwen, new translator, or semantic parser was run",
            "The result tests zero-shot interface transfer, not latent neural scientific ability",
            "An ABSTAIN on published Uncertain is classification agreement, not a new proof",
        ],
        "rows": scored,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run_external()
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        out = args.output.resolve()
        if out.is_relative_to(ROOT):
            parser.error("write report outside repository")
        out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
