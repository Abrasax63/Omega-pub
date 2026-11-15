"""Replay EXACTLY the archived three Qwen proposals after an infrastructure repair.

No model is called. No new proposal or evaluation example is introduced.
Original attempts are preserved, including the first failed harness launch.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess

from model_proposal import semantic_fingerprint
from opt02_generator import make_training, training_run, MODEL_HASH

ORIGINAL_RUN = "https://github.com/Abrasax63/Omega-pub/actions/runs/43746056945"
ORIGINAL_ARTIFACT_SHA256 = "35e5818fcccc239e38e315d164ce0938047e5909190b7b33403251dfd1b66a04"
ORIGINAL_CANDIDATE_SHA256 = "46ddcea87b8640eae0d1757312f034d0d0ebe5db5c814264bf75751e08e0af77"


def replay(original_json, output_dir):
    raw = original_json.read_bytes()
    if sha256(raw).hexdigest() != ORIGINAL_ARTIFACT_SHA256:
        raise ValueError("archived model generation JSON changed")
    before = json.loads(raw)
    if before.get("model_attempts") != 3 or before.get("model_weight_sha256") != MODEL_HASH:
        raise ValueError("original generation budget or model differs")
    if before.get("external_corpus_opened") is not False:
        raise ValueError("prior holdout was opened; replay forbidden")
    candidates = before.get("attempts", [])
    if len(candidates) != 3 or any(a.get("model_exit") != 0 for a in candidates):
        raise ValueError("expected exactly three successful original inference calls")
    sources = [item.get("source") for item in candidates]
    if any(not isinstance(s, str) or sha256(s.encode()).hexdigest() != ORIGINAL_CANDIDATE_SHA256
           for s in sources):
        raise ValueError("original source not identical among the three attempts")
    if len({semantic_fingerprint(s) for s in sources}) != 1:
        raise ValueError("ambiguous different candidates in archive")
    if subprocess.run(["docker","info"],capture_output=True,timeout=10).returncode:
        raise RuntimeError("Docker unavailable; do not execute on host")
    result = training_run(sources[0],make_training())
    outcome = dict(before)
    outcome["original_scientific_status"] = before["status"]
    outcome["original_run"] = ORIGINAL_RUN
    outcome["original_artifact_sha256"] = ORIGINAL_ARTIFACT_SHA256
    outcome["replay_type"] = "INFRASTRUCTURE_ONLY_PERMISSION_REPAIR_NO_NEW_INFERENCE"
    outcome["replay_training"] = result
    outcome["original_attempts_preserved"] = candidates
    # Never rewrite or hide the original failures.
    if result["errors"]:
        outcome["status"] = "REPLAY_CANDIDATE_INCORRECT"
        outcome["winner_source_sha256"] = None
    else:
        outcome["status"] = "CHAMPION_READY_FOR_SEPARATE_EVALUATOR"
        outcome["winner_source_sha256"] = ORIGINAL_CANDIDATE_SHA256
        outcome["winner_semantic_sha256"] = semantic_fingerprint(sources[0])
    output_dir.mkdir(parents=True, exist_ok=True)
    if not result["errors"]:
        (output_dir / "champion.py").write_text(sources[0], encoding="utf-8")
    (output_dir / "generation.json").write_text(
        json.dumps(outcome, indent=2, ensure_ascii=False, sort_keys=True)+"\n",
        encoding="utf-8")
    print(json.dumps({"original_run":ORIGINAL_RUN,"source_sha256":ORIGINAL_CANDIDATE_SHA256,
                      "training_errors":result["errors"],"training_cases":result["n_training"],
                      "status":outcome["status"],"model_calls_added":0},indent=2))
    return outcome


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--original-json",type=Path,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    replay(args.original_json,args.output_dir)


if __name__=="__main__":
    main()
