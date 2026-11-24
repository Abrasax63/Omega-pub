"""Bounded Omega pilot: reuse existing provenance and V19 verifiers, never promote results.

Two distinct, preregistered falsification probes. An external scheduler must
supply a durable ledger on every invocation. No LLM, no network, no repo writes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from time import perf_counter

VERSION = 1
GENESIS = "0" * 64
TASKS = ("PROV-COPY-SCOPE-V1", "V19-C5-LEAVES-N8-V1")


def digest(obj):
    raw = json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_ledger(state):
    if not isinstance(state, dict) or state.get("schema") != VERSION:
        raise ValueError("Unknown ledger schema")
    entries = state.get("entries")
    if not isinstance(entries, list):
        raise ValueError("Missing ledger entries")
    prev, used = GENESIS, set()
    for event in entries:
        if not isinstance(event, dict) or event.get("previous_hash") != prev:
            raise ValueError("Broken ledger chain")
        if event.get("event_hash") != digest({k: v for k, v in event.items() if k != "event_hash"}):
            raise ValueError("Tampered ledger entry")
        if event.get("experiment_id") in used or event.get("experiment_id") not in TASKS:
            raise ValueError("Unknown or duplicate experiment")
        used.add(event["experiment_id"])
        prev = event["event_hash"]


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def source_snapshot(omega_dir, math_dir, provenance_dir):
    # These are interfaces developed BEFORE this pilot; fail closed on missing files.
    required = (
        Path(omega_dir) / "research/omega-100/PROGRAMME.md",
        Path(math_dir) / "research/code/audit_v19_shadow_guard.py",
        Path(provenance_dir) / "09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_cycle.py",
    )
    for file in required:
        if not file.is_file():
            raise FileNotFoundError(f"Missing pre-existing Omega component: {file}")
    numbered = sorted((Path(omega_dir) / "research/omega-100").glob("[0-9][0-9][0-9].md"))
    if not numbered:
        raise ValueError("Omega 100 journal is empty")
    ids = [int(p.stem) for p in numbered]
    if ids != list(range(1, max(ids) + 1)):
        raise ValueError("Gap in Omega 100 experiment journal")
    return {"omega100_last": max(ids), "omega100_digest": digest(numbered[-1].read_text(encoding="utf-8")),
            "math_guard_digest": hashlib.sha256(required[1].read_bytes()).hexdigest(),
            "provenance_cycle_digest": hashlib.sha256(required[2].read_bytes()).hexdigest()}


def provenance_probe(provenance_dir):
    """Test command-signature generalization with separated synthetic controls."""
    prism = str(Path(provenance_dir) / "09_INFRASTRUCTURE_AGENTIQUE/prism")
    sys.path.insert(0, prism)
    try:
        from provenance_cycle import evaluate_proposal, propose
        from provenance_lab import score
        def trace(command, expected="copie", complete=True, writers=None):
            return {"complete": complete, "output": "result.txt",
                    "writers": [{"command": command, "output": "result.txt", "exit_code": 0}]
                    if writers is None else writers, "expected": expected}
        # Preregistered training and reserved records have different observations.
        training = [trace("cp -v training_a.txt result.txt")]
        reserved = [trace("cp -v reserved_b.txt result.txt"),
                    trace("cp -v reserved_c.txt result.txt"),
                    trace("cp -v partial.txt result.txt", complete=False),
                    trace("cp -v ambiguous.txt result.txt", writers=[
                        {"command": "cp -v one.txt result.txt", "output": "result.txt", "exit_code": 0},
                        {"command": "cp -v two.txt result.txt", "output": "result.txt", "exit_code": 0}])]
        baseline = {}
        candidate = propose(training, baseline)
        comparison = evaluate_proposal(candidate, baseline, reserved)
        # The fixed hand-coded cp rule is an independent control, not an Omega gain.
        fixed = score(reserved, {("cp", "-v"): "copie"})
        pass_criteria = (comparison["candidate"]["false_confirmations"] == 0
                         and comparison["candidate"]["correct_confirmations"] == 2
                         and comparison["candidate"] == fixed)
        return {"question": "Does a cp -v prefix generalize without confirming incomplete/multiple-writer traces?",
                "hypothesis": "Two confirmations, no false confirmation on the reserved synthetic cases",
                "reference": "Empty declarative rules; fixed cp -v rule as control",
                "train_sha256": digest(training), "reserved_inputs_sha256": digest([{k: v for k, v in x.items() if k != "expected"} for x in reserved]),
                "training_count": len(training), "reserved_count": len(reserved),
                "baseline": comparison["baseline"], "candidate": comparison["candidate"],
                "fixed_rule": fixed, "recommend_for_review": comparison["recommend_for_review"],
                "novel_scientific_gain": False, "passed": pass_criteria,
                "scope": "synthetic traces only; no external generalization demonstrated"}
    finally:
        sys.path.remove(prism)


def math_probe(math_dir):
    """Use the pre-existing V19 projector and exhaustive oracle on a C5+leaves family."""
    code_dir = str(Path(math_dir) / "research/code")
    sys.path.insert(0, code_dir)
    try:
        from audit_v19_shadow_guard import compare
        transformation = (1, 2, 3, 4, 0, 1, 2, 3)  # C5 + three leaves, eight states
        cycle = (0, 1, 2, 3, 4)
        cases = [(transformation, cycle, (5, 7), 2),
                 (transformation, cycle, (6, 7), 3)]
        comparison = compare(cases)  # both full and local, independent exact oracle
        passed = (comparison["projections"] == 4
                  and comparison["new_errors"] == 0
                  and comparison["locality_errors"] == 0)
        return {"question": "Does the guarded V19 shadow agree with exhaustive projection on two C5+leaves cases?",
                "hypothesis": "Zero guarded/oracle and local/global divergences across four projections",
                "reference": "exhaustive_shadow in pre-existing audit_v19_shadow_guard.py",
                "cases_sha256": digest(cases), "case_count": len(cases),
                "metrics": comparison, "passed": passed,
                "novel_scientific_gain": False,
                "scope": "two finite eight-state cases; neither proof nor universal result"}
    finally:
        sys.path.remove(code_dir)


def pilot(state_file, output_dir, *, omega_dir, math_dir, provenance_dir, bootstrap=False, max_cycles=2):
    state_file, output_dir = Path(state_file), Path(output_dir)
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
    elif bootstrap:
        state = {"schema": VERSION, "entries": []}
    else:
        raise FileNotFoundError("No durable state: fail closed (explicit bootstrap required)")
    validate_ledger(state)
    sources = source_snapshot(omega_dir, math_dir, provenance_dir)
    performed = []
    remaining = [task for task in TASKS if task not in {e["experiment_id"] for e in state["entries"]}]
    for experiment_id in remaining[:max_cycles]:
        started = perf_counter()
        try:
            result = (provenance_probe(provenance_dir) if experiment_id == TASKS[0]
                      else math_probe(math_dir))
            status = "VERIFIED_FINITE" if result["passed"] else "REFUTED_ON_PILOT"
        except Exception as exc:
            # Blocked tasks do not become completed ledger entries; retry is safe.
            result = {"error_type": type(exc).__name__, "error": str(exc), "scope": "not executed to completion"}
            status = "BLOCKED"
        event = {"experiment_id": experiment_id, "status": status,
                 "sources": sources, "result_sha256": digest(result),
                 "elapsed_seconds": round(perf_counter() - started, 6),
                 "previous_hash": state["entries"][-1]["event_hash"] if state["entries"] else GENESIS}
        event["event_hash"] = digest(event)
        write_json(output_dir / f"{experiment_id}.json", {"event": event, "result": result})
        performed.append(event)
        if status != "BLOCKED":
            state["entries"].append(event)
            validate_ledger(state)
            write_json(state_file, state)
        else:
            break
    summary = {"source_snapshot": sources, "new_experiments": len(performed),
               "completed": sum(e["status"] != "BLOCKED" for e in performed),
               "blocked": sum(e["status"] == "BLOCKED" for e in performed),
               "remaining": len(TASKS) - len(state["entries"]),
               "statuses": [e["status"] for e in performed],
               "note": "Tests are bounded pilot falsifications, NOT independent research discoveries."}
    write_json(output_dir / "summary.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--omega-dir", type=Path, required=True)
    parser.add_argument("--math-dir", type=Path, required=True)
    parser.add_argument("--provenance-dir", type=Path, required=True)
    parser.add_argument("--bootstrap", action="store_true")
    parser.add_argument("--max-cycles", type=int, choices=(1, 2), default=2)
    a = parser.parse_args()
    outcome = pilot(a.state, a.output_dir, omega_dir=a.omega_dir, math_dir=a.math_dir,
                    provenance_dir=a.provenance_dir, bootstrap=a.bootstrap, max_cycles=a.max_cycles)
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True))
    if outcome["blocked"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
