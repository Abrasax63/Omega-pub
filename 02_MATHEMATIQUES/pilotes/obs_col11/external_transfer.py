#!/usr/bin/env python3
"""OBS-COL-11, preregistered external public transfer without model substitution.

SOURCE truth lives only in AALpy's SUL/evaluator; policies receive the
hypothesis and previous observed prefixes, never the true target graph.
Policy class is IMPORTED UNCHANGED from OBS-COL-10. The source contains
six third-party DOT models frozen before writing this program; incomplete
Moore models are BLOCKED, not secretly repaired or replaced.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path

import pydot
from aalpy.automata import MooreMachine
from aalpy.learning_algs import run_Lstar, run_KV, run_Lsharp

HERE = Path(__file__).resolve().parent
for module in (
    HERE.parent / "obs_col10",
    HERE.parent / "obs_col09_common",
    HERE.parent / "obs_col09",
):
    if str(module) not in sys.path:
        sys.path.insert(0, str(module))
from policy_divergence import AdaptiveEqOracle  # unchanged preregistered policy
from common_eq import SharedWordEquivalenceOracle
from benchmark import PhysicalCounter
from generate_manifests import equivalence_words, encode, manifest_hash
from generate_matched_eval import words as heldout_words

ARMS = ("fixed", "coverage_only", "omega_candidate", "Lstar", "KV")
MAX_RESETS, MAX_SYMBOLS = 10000, 50000
MAX_ROUNDS = 40
LABEL_RE = re.compile(r"^\{\s*(.*?)\s*\|\s*(.*?)\s*\}$")


class ExternallyIncomplete(Exception):
    def __init__(self, message, *, states, alphabet, missing):
        super().__init__(message)
        self.states, self.alphabet, self.missing = states, alphabet, missing


def unquote(text):
    text = str(text)
    return text[1:-1] if len(text) >= 2 and text[0] == '"' and text[-1] == '"' else text


def load_pinned_moore(path, source_sha):
    """Strict pydot adapter. Never invent a missing action or output."""
    data = Path(path).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != source_sha:
        raise AssertionError("external source SHA-256 changed")
    graphs = pydot.graph_from_dot_data(data.decode("utf-8"))
    if len(graphs) != 1:
        raise ValueError("expected one DOT graph")
    graph = graphs[0]
    node_output = {}
    for node in graph.get_nodes():
        name = unquote(node.get_name())
        if name in ("__start0", "\\n", "node", "edge", "graph"):
            continue
        label = unquote(node.get_label())
        match = LABEL_RE.fullmatch(label)
        if match is None:
            raise ValueError("unexpected Moore node label")
        node_output[name] = match.group(2).strip()

    transitions = {node: {} for node in node_output}
    initial = []
    for edge in graph.get_edges():
        src = unquote(edge.get_source())
        dst = unquote(edge.get_destination())
        if src == "__start0":
            initial.append(dst)
            continue
        if src not in transitions or dst not in transitions:
            raise ValueError("undeclared DOT transition")
        label = unquote(edge.get_label()).strip()
        if not label or label in transitions[src]:
            raise ValueError("unlabeled or duplicate DOT action")
        transitions[src][label] = dst
    if len(initial) != 1 or initial[0] not in transitions:
        raise ValueError("expected exactly one declared start state")
    alphabet = sorted({a for t in transitions.values() for a in t})
    if len(alphabet) < 2 or not node_output:
        raise ValueError("invalid alphabet / empty automaton")
    missing = {state: sorted(set(alphabet) - set(links))
               for state, links in transitions.items()
               if set(links) != set(alphabet)}
    if missing:
        raise ExternallyIncomplete(
            "externally published DOT is not input complete",
            states=len(node_output), alphabet=alphabet, missing=missing,
        )
    # The first state in AALpy's from_state_setup is the initial state.
    ordered = [initial[0]] + [n for n in node_output if n != initial[0]]
    setup = {n: (node_output[n], transitions[n]) for n in ordered}
    machine = MooreMachine.from_state_setup(setup)
    if not machine.is_input_complete():
        raise AssertionError("adapted automaton is not input complete")
    return machine, {
        "states": len(node_output),
        "alphabet": alphabet,
        "outputs": len(set(node_output.values())),
        "sha256": digest,
        "missing_transitions": {},
    }


def fit_one(model, arm, name, index):
    """No future test outputs are touched until every fit has ended."""
    alphabet = sorted(model.get_input_alphabet(), key=str)
    eq_candidates = equivalence_words(tuple(map(str, alphabet)), index)
    mapping = {str(a): a for a in alphabet}
    if len(mapping) != len(alphabet):
        raise ValueError("ambiguous input string mapping")
    eq_words = tuple(tuple(mapping[a] for a in word) for word in eq_candidates)
    physical = PhysicalCounter(model, use_p1=(arm == "omega_candidate"))
    policy = arm if arm in ("fixed", "coverage_only", "omega_candidate") else "fixed"
    if arm in ("Lstar", "KV"):
        eq = SharedWordEquivalenceOracle(alphabet, physical, eq_words)
    else:
        eq = AdaptiveEqOracle(alphabet, physical, eq_words, policy=policy)
    runner = {"Lstar": run_Lstar, "KV": run_KV}.get(arm, run_Lsharp)
    started_cpu, started_wall = time.process_time(), time.perf_counter()
    learned, info = runner(
        alphabet, physical, eq, automaton_type="moore",
        max_learning_rounds=MAX_ROUNDS,
        cache_and_non_det_check=False,
        print_level=0,
        return_data=True,
    )
    cpu = time.process_time() - started_cpu
    wall = time.perf_counter() - started_wall
    if physical.physical_resets > MAX_RESETS or physical.physical_symbols > MAX_SYMBOLS:
        raise AssertionError("physical budget overrun without refusal")
    return learned, {
        "model": name, "arm": arm,
        "status": "FIT_FINISHED" if eq.completed_suites >= 1 else "FIT_INDETERMINATE_MAX_ROUNDS",
        "source_states_posthoc": len(model.states),
        "learned_states": len(learned.states),
        "physical_resets": physical.physical_resets,
        "physical_symbols": physical.physical_symbols,
        "physical_trace_sha256": physical.fingerprint(),
        "p1_calls": physical.p1_calls,
        "cpu_seconds": round(cpu, 6),
        "wall_seconds": round(wall, 6),
        "eq_manifest_sha256": manifest_hash(encode(eq_candidates)),
        "eq_rounds": eq.rounds,
        "eq_completed_suites": eq.completed_suites,
        "eq_counterexamples": eq.found_counterexamples,
        "eq_candidate_words_executed": eq.proposed_words,
        "eq_order_sha256": getattr(eq, "order_digest", lambda: None)(),
        "first_eq_proposals": getattr(eq, "first_proposals", []),
        "library_info": info,
        "equivalence_certified": False,
        "omega_superiority_claim": False,
        "_physical": physical,
    }


def run(directory):
    folder = Path(directory)
    lock = json.loads((HERE / "SOURCE_SHA_LOCK.json").read_text())
    source_shas = lock["sha256"]
    expected = ("crossword2x2.dot", "crossword3x3.dot", "register2.dot",
                "register3.dot", "register4.dot", "register5.dot")
    if tuple(source_shas) != expected:
        raise AssertionError("source lock is not the preregistered ordered cohort")
    raw = json.loads((folder / "download_manifest.json").read_text())
    raw_idx = {item["name"]: item for item in raw}
    report = []
    frozen = []
    for index, name in enumerate(expected):
        record = {"model": name, "cohort_index": index,
                  "sha256_preregistered_after_retrieval": source_shas[name]}
        if raw_idx.get(name, {}).get("status") != "DOWNLOADED":
            record.update(status="BLOCKED_DOWNLOAD", reason=raw_idx.get(name, {}).get("reason"))
            report.append(record)
            continue
        if raw_idx[name].get("sha256") != source_shas[name]:
            record.update(status="BLOCKED_SOURCE_CHANGED")
            report.append(record)
            continue
        try:
            # Parse once to screen *only* source-input completeness.
            model, adapter = load_pinned_moore(folder / name, source_shas[name])
        except ExternallyIncomplete as exc:
            record.update(status="BLOCKED_INPUT_INCOMPLETE",
                          states=exc.states, alphabet=exc.alphabet,
                          missing_state_actions=exc.missing)
            report.append(record)
            continue
        except (ValueError, AssertionError, OSError) as exc:
            record.update(status="BLOCKED_PARSE_OR_SOURCE",
                          reason=type(exc).__name__ + ": " + str(exc))
            report.append(record)
            continue
        record.update(status="SOURCE_COMPATIBLE", metadata=adapter, arms={})
        report.append(record)
        for arm in ARMS:
            try:
                # Fresh independent target for every arm.
                target, _ = load_pinned_moore(folder / name, source_shas[name])
                learned, result = fit_one(target, arm, name, index)
                frozen.append((record, arm, target, learned, result))
            except Exception as exc:
                record["arms"][arm] = {
                    "arm": arm, "status": "BLOCKED_LEARNING",
                    "error_type": type(exc).__name__,
                    "error": str(exc)[:350],
                    "scientific_certificate": False,
                }

    # Holdout test answers opened only AFTER all fit policies have terminated.
    for record, arm, target, learned, result in frozen:
        index = record["cohort_index"]
        alphabet = sorted(target.get_input_alphabet(), key=str)
        words = heldout_words(tuple(map(str, alphabet)), index)
        mapping = {str(a): a for a in alphabet}
        count_unseen, err_unseen, err_total = 0, 0, 0
        for word in words:
            translated = tuple(mapping[a] for a in word)
            truth = target.execute_sequence(target.initial_state, translated)[-1]
            predicted = learned.execute_sequence(learned.initial_state, translated)[-1]
            err = int(truth != predicted)
            err_total += err
            if translated not in result["_physical"].observed_prefixes:
                count_unseen += 1
                err_unseen += err
        del result["_physical"]
        result.update(
            heldout_total=256,
            heldout_unseen_count=count_unseen,
            heldout_unseen_errors=err_unseen,
            heldout_errors_total=err_total,
        )
        if result["status"] == "FIT_FINISHED" and count_unseen > 0:
            result["status"] = "EVALUATED_BOUNDED"
        elif count_unseen == 0:
            result["status"] = "EVALUATION_UNSEEN_INDETERMINATE"
        record["arms"][arm] = result

    summary = []
    for record in report:
        if record["status"] != "SOURCE_COMPATIBLE":
            continue
        arms = record["arms"]
        a, b, c = (arms.get(name, {}) for name in ("fixed", "coverage_only", "omega_candidate"))
        if not all(x.get("status") == "EVALUATED_BOUNDED" for x in (a,b,c)):
            verdict = "BLOCKED_OR_INDETERMINATE"
        else:
            metrics = ("heldout_unseen_errors", "physical_resets", "physical_symbols")
            comparisons = {
                "omega_not_worse_than_fixed": all(c[k] <= a[k] for k in metrics),
                "omega_not_worse_than_coverage": all(c[k] <= b[k] for k in metrics),
                "omega_strictly_better_than_fixed": any(c[k] < a[k] for k in metrics),
                "omega_strictly_better_than_coverage": any(c[k] < b[k] for k in metrics),
            }
            verdict = ("LOCAL_PARETO_BOTH" if
                       comparisons["omega_not_worse_than_fixed"] and
                       comparisons["omega_not_worse_than_coverage"] and
                       comparisons["omega_strictly_better_than_fixed"] and
                       comparisons["omega_strictly_better_than_coverage"]
                       else "MIXED_OR_NEGATIVE")
            summary.append({"model": record["model"], "verdict": verdict,
                            "comparisons": comparisons})
            continue
        summary.append({"model": record["model"], "verdict": verdict})
    return {
        "pilot": "OBS-COL-11",
        "preregistered_commit": "6a37ca2e7b10c5222f17dd5058ccf701e15c64e8",
        "source_hash_lock_commit": "8ea4be0fb911df10296ea5d17203dd3c4d827630",
        "status": "PROSPECTIVE_PUBLIC_EXTERNAL_NOT_INDEPENDENT_BLIND",
        "model_calls": 0,
        "policy_source": "inherited unchanged OBS-COL-10, from PR #110",
        "p1_does_not_choose_queries_alone": True,
        "not_independent_private_holdout": True,
        "no_global_superiority_or_certification": True,
        "arms": ARMS,
        "models": report,
        "local_verdicts": summary,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: external_transfer.py downloaded_sources_dir")
    print(json.dumps(run(sys.argv[1]), indent=2, ensure_ascii=False, default=str))
