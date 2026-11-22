"""Incremental Omega queue: established solvers, immutable probes, chained state.

This schedules already-specified finite *regression probes*, not autonomous
scientific discovery. New research hypotheses must be separately preregistered.
No LLM, no internet, no repo writes. An external scheduler must persist state.
"""
from __future__ import annotations

import argparse
from itertools import combinations, product
import json
from pathlib import Path
import sys
from time import perf_counter

from fast_cycle import (GENESIS, digest, math_probe, provenance_probe,
                        source_snapshot, write_json)

SCHEMA = 2


def read_catalog(path):
    catalog = json.loads(Path(path).read_text(encoding="utf-8"))
    tasks = catalog.get("tasks") if isinstance(catalog, dict) else None
    if catalog.get("schema") != 1 or not isinstance(tasks, list) or not tasks:
        raise ValueError("Invalid immutable task catalog")
    seen = set()
    for task in tasks:
        if not isinstance(task, dict) or not isinstance(task.get("id"), str):
            raise ValueError("Invalid task record")
        if task["id"] in seen or "/" in task["id"] or ".." in task["id"]:
            raise ValueError("Duplicate or unsafe task id")
        seen.add(task["id"])
        if task.get("kind") not in {"provenance_pilot", "math_smoke", "math_family"}:
            raise ValueError("Unknown adapter")
        if not all(isinstance(task.get(k), str) and task[k] for k in
                   ("question", "hypothesis", "reference", "scope")):
            raise ValueError("Missing preregistration")
        if task["kind"] == "math_family":
            q, n, horizon, limit = (
                task.get("q"), task.get("n"), task.get("horizon"), task.get("max_cases"))
            if not (all(type(x) is int for x in (q, n, horizon, limit))
                    and 3 <= q < n <= 10 and horizon in (2, 3, 4) and 1 <= limit <= 24):
                raise ValueError("Unbounded or invalid math family")
    return catalog


def check_state(state, tasks, results_dir=None):
    if not isinstance(state, dict) or state.get("schema") != SCHEMA:
        raise ValueError("Invalid ledger schema")
    items = state.get("entries")
    if not isinstance(items, list):
        raise ValueError("Missing entries")
    registry = {t["id"]: digest(t) for t in tasks}
    used = set()
    prev = GENESIS
    for e in items:
        if not isinstance(e, dict) or e.get("prev") != prev:
            raise ValueError("Invalid chain link")
        if e.get("hash") != digest({k: v for k, v in e.items() if k != "hash"}):
            raise ValueError("Tampered ledger record")
        tid = e.get("id")
        if tid not in registry or tid in used or e.get("prereg_sha256") != registry[tid]:
            raise ValueError("Changed/unknown preregistration or duplicate")
        if e.get("status") not in ("VERIFIED_FINITE", "REFUTED_FINITE"):
            raise ValueError("Nonterminal status in completed ledger")
        if results_dir is not None:
            file = Path(results_dir) / f"{tid}.json"
            if not file.is_file():
                raise ValueError("Missing archived results for " + tid)
            report = json.loads(file.read_text(encoding="utf-8"))
            if report.get("entry") != e or digest(report.get("result")) != e.get("result_sha256"):
                raise ValueError("Result digest mismatch for " + tid)
        prev = e["hash"]
        used.add(tid)
    return used


def math_family_probe(math_dir, task):
    code_dir = str(Path(math_dir) / "research/code")
    sys.path.insert(0, code_dir)
    try:
        from test_v19_locality_l_plus_1 import coherent, forced_edges
        from audit_v19_shadow_guard import compare

        n, q, horizon, limit = (task["n"], task["q"], task["horizon"],
                                task["max_cases"])
        cycle = tuple(range(q))
        cases = []
        considered = 0
        # Fixed order and a strict per-probe computational budget.
        for leaves in product(range(q), repeat=n - q):
            transformation = (*range(1, q), 0, *leaves)
            considered += 1
            if not coherent(n, forced_edges(transformation)):
                continue
            pairs = [(a, b) for a, b in combinations(range(n), 2) if b >= q]
            for pair in pairs[:2]:
                cases.append((transformation, cycle, pair, horizon))
                if len(cases) >= limit:
                    break
            if len(cases) >= limit:
                break
        if not cases:
            raise ValueError("No coherent cases in preregistered family")
        metrics = compare(cases)
        passed = (metrics["projections"] == 2 * len(cases)
                  and all(metrics[k] == 0 for k in
                          ("new_errors", "old_errors", "locality_errors")))
        return {
            "question": task["question"], "hypothesis": task["hypothesis"],
            "reference": task["reference"], "scope": task["scope"],
            "cases_sha256": digest(cases), "considered_transforms": considered,
            "case_count": len(cases), "metrics": metrics, "passed": passed,
            "novel_scientific_gain": False,
            "classification": "FINITE_REGRESSION_ONLY",
        }
    finally:
        sys.path.remove(code_dir)
        # Avoid accidentally reusing modules from another experimental checkout.
        sys.modules.pop("audit_v19_shadow_guard", None)
        sys.modules.pop("test_v19_locality_l_plus_1", None)


def next_unverified_question(omega_dir):
    """Expose, but do NOT execute or claim completion of, the current Omega100 question."""
    root = Path(omega_dir) / "research/omega-100"
    numbered = sorted(root.glob("[0-9][0-9][0-9].md"))
    if not numbered:
        raise ValueError("Omega100 journal missing")
    last = numbered[-1]
    text = last.read_text(encoding="utf-8")
    # If the heading is absent, do not pretend to have parsed its intent.
    pos = text.lower().rfind("prochain essai")
    return {
        "kind": "PENDING_RESEARCH_QUESTION",
        "from_experiment": int(last.stem),
        "source_digest": digest(text),
        "excerpt": text[pos:pos + 600].strip() if pos >= 0 else None,
        "status": "NOT_EXECUTED_NEEDS_PREREG_AND_DATA",
    }


def run_queue(state_file, output_dir, *, catalog_file, omega_dir, math_dir,
              provenance_dir, bootstrap=False, max_cycles=2):
    catalog = read_catalog(catalog_file)
    tasks = catalog["tasks"]
    state_file, output_dir = Path(state_file), Path(output_dir)
    results_dir = output_dir / "results"
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
    elif bootstrap:
        state = {"schema": SCHEMA, "entries": []}
        # Persist the initial empty ledger even when the first probe blocks.
        write_json(state_file, state)
    else:
        raise FileNotFoundError("Lost/absent durable state; explicit bootstrap required")
    used = check_state(state, tasks, results_dir)
    snapshot = source_snapshot(omega_dir, math_dir, provenance_dir)
    inbox = next_unverified_question(omega_dir)
    selected = [t for t in tasks if t["id"] not in used][:max_cycles]
    attempts, blocked = [], 0
    for task in selected:
        started = perf_counter()
        try:
            if task["kind"] == "provenance_pilot":
                result = provenance_probe(provenance_dir)
            elif task["kind"] == "math_smoke":
                result = math_probe(math_dir)
            else:
                result = math_family_probe(math_dir, task)
            status = "VERIFIED_FINITE" if result["passed"] else "REFUTED_FINITE"
        except Exception as exc:
            result = {"error_type": type(exc).__name__, "error": str(exc)}
            status = "BLOCKED"
        event = {
            "id": task["id"],
            "kind": task["kind"],
            "status": status,
            "prereg_sha256": digest(task),
            "sources": snapshot,
            "result_sha256": digest(result),
            "elapsed_seconds": round(perf_counter() - started, 6),
            "prev": state["entries"][-1]["hash"] if state["entries"] else GENESIS,
        }
        event["hash"] = digest(event)
        attempts.append(event)
        if status == "BLOCKED":
            blocked += 1
            # Do not advance the ledger for an incomplete check.
            write_json(output_dir / "blocked.json", {"entry": event, "result": result})
            break
        state["entries"].append(event)
        # Write ledger first: an interruption produces a fail-closed missing
        # report, never a falsely fresh retry of already completed work.
        write_json(state_file, state)
        write_json(results_dir / f"{task['id']}.json", {"entry": event, "result": result})
    check_state(state, tasks, results_dir)
    done = {e["id"] for e in state["entries"]}
    summary = {
        "probes_attempted": len(attempts),
        "finite_probes_completed": len(attempts) - blocked,
        "blocked": blocked,
        "remaining_preregistered": len(tasks) - len(done),
        "executed_ids": [e["id"] for e in attempts if e["status"] != "BLOCKED"],
        "statuses": [e["status"] for e in attempts],
        "inbox": inbox,
        "scientific_discoveries_claimed": 0,
        "note": "Finite regression queue; fresh hypotheses require preregistration and independent evidence.",
    }
    write_json(output_dir / "summary.json", summary)
    return summary


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ("state", "output-dir", "catalog", "omega-dir", "math-dir", "provenance-dir"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--bootstrap", action="store_true")
    p.add_argument("--max-cycles", type=int, choices=(1, 2), default=2)
    a = p.parse_args()
    result = run_queue(a.state, a.output_dir, catalog_file=a.catalog, omega_dir=a.omega_dir,
                       math_dir=a.math_dir, provenance_dir=a.provenance_dir,
                       bootstrap=a.bootstrap, max_cycles=a.max_cycles)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["blocked"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
