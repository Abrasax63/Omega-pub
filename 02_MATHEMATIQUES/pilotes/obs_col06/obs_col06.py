#!/usr/bin/env python3
"""OBS-COL-06: finite active choice among competing Markov, collective, memory models.

The real Omega PR23 decision policy chooses among probe histories, while
known candidate transducers predict outcomes. The hidden-world label is never
passed to candidate filtering, P1, the PR40 observer gate, or the Walsh audit.
This is a CLOSED-GRAMMAR synthetic study, not autonomous law discovery.
"""
from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
for folder in (
    ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "prism",
    ROOT / "02_MATHEMATIQUES" / "pilotes" / "obs_col04",
    ROOT / "02_MATHEMATIQUES" / "pilotes" / "observabilite_collective",
):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
from action_planning_two_step import plan_with_variable_horizon  # Real PR23 + P1
from planner import plan_mission  # Real P1 for separate falsification probes
from observer_guard_bridge import inspect_observer_evidence  # Real PR40
from obs_col04 import independent_two_step_oracle  # Separate two-step comparator
from collective_observability import walsh  # Identical source from PR86

CATALOG = ("PAIR01", "PAIR02", "TRIPLE012", "MEMORY_TOGGLE", "MEMORY_SET")
OUTSIDE = "OUTSIDE_TERNARY"
WORLDS = CATALOG + (OUTSIDE,)
ACTIONS = ("prime", "read")
INITIAL = ((0, ("read",)), (1, ("read",)))
PROBES = (
    (3, ("read",)), (5, ("read",)), (7, ("read",)),
    (0, ("prime", "read")), (0, ("prime", "prime", "read")),
    (7, ("prime", "read")), (3, ("prime", "read")), (5, ("prime", "read")),
)
RESERVED = (
    (0, ("prime", "prime", "prime", "read")),
    (3, ("prime", "prime", "prime", "read")),
    (7, ("prime", "prime", "prime", "read")),
    (8, ("read",)), (13, ("read",)), (15, ("read",)),
)
MAX_ACTIVE = 5
BUDGET_MILLI = 60


def transition(rule, visible, latent, action):
    """Generator for reproducibility; runtime learner only calls oracle.query."""
    if rule not in WORLDS or action not in ACTIONS or not 0 <= visible < 16:
        raise ValueError("invalid model, action or visible state")
    if action == "prime":
        if rule == "MEMORY_TOGGLE":
            latent = 1 - latent
        elif rule == "MEMORY_SET":
            latent = 1
        elif rule == OUTSIDE:
            latent = (latent + 1) % 3
        return visible, latent

    bits = tuple((visible >> j) & 1 for j in range(4))
    if rule == "PAIR01":
        trigger = bits[0] & bits[1]
    elif rule == "PAIR02":
        trigger = bits[0] & bits[2]
    elif rule == "TRIPLE012":
        trigger = bits[0] & bits[1] & bits[2]
    elif rule == OUTSIDE:
        trigger = int(latent != 0)
    else:
        trigger = latent
    return visible ^ (trigger << 3), latent


def trace(rule, start, sequence):
    if rule not in WORLDS or not 0 <= start < 16:
        raise ValueError("invalid source")
    if not isinstance(sequence, tuple) or not sequence or any(a not in ACTIONS for a in sequence):
        raise ValueError("invalid action sequence")
    visible, latent = start, 0
    history = [visible]
    for action in sequence:
        visible, latent = transition(rule, visible, latent, action)
        history.append(visible)
    return tuple(history)


class WorldOracle:
    """Only this object sees the generating rule; no rule label leaks to planner."""
    def __init__(self, rule):
        if rule not in WORLDS:
            raise ValueError("unknown world")
        self._rule = rule
        self.training_queries = []
        self.heldout_queries = []

    def query(self, probe):
        if probe not in INITIAL and probe not in PROBES:
            raise ValueError("probe not in the prespecified training set")
        outcome = trace(self._rule, *probe)
        self.training_queries.append((probe, outcome))
        return outcome

    def evaluate(self, probe):
        if probe not in RESERVED:
            raise ValueError("not a reserved probe")
        outcome = trace(self._rule, *probe)
        self.heldout_queries.append((probe, outcome))
        return outcome


def render_trace(result):
    return ",".join(map(str, result))


def candidates_from_observations(observations):
    """Reject candidate models by EXACT full observable trace disagreement."""
    return tuple(rule for rule in CATALOG if all(
        trace(rule, *probe) == output for probe, output in observations
    ))


def make_case(candidates, observed, episode, iteration):
    if not candidates:
        raise ValueError("no compatible candidates")
    hypotheses = [{"id": name, "decision": name, "weight": 1} for name in candidates]
    checks = []
    for index, probe in enumerate(PROBES, 1):
        if probe in {p for p, _ in observed}:
            continue
        checks.append({
            "id": f"q{index:02d}",
            "step": f"Reset to {probe[0]}, execute {'+'.join(probe[1])}, observe full trace",
            "method": "controlled_reset_intervention", "action": "verify",
            "available": True, "cost_milli": 10 * len(probe[1]),
            "observations": [render_trace(trace(name, *probe)) for name in candidates],
        })
    return {
        "case_id": f"OBS-COL-06-{episode}-{iteration}",
        "question": "Which observable representation survives actual interventions?",
        "mission_type": "mathematical",
        "uncertainty": "The model family and hidden history are underdetermined",
        "hypotheses": hypotheses, "checks": checks,
    }


def advisory(case, check_id):
    """A PR40 audit is advisory and cannot establish source authenticity."""
    def partition(values):
        seen = {}
        return [seen.setdefault(v, len(seen)) for v in values]

    selected = next(x for x in case["checks"] if x["id"] == check_id)
    evidence = {"termination": {
        "current_partition": [0] * len(case["hypotheses"]),
        "selected_probe_partition": partition(selected["observations"]),
        "listed_probe_partitions": [partition(x["observations"]) for x in case["checks"]],
        "declared_exhaustive": False,
    }}
    result = inspect_observer_evidence(evidence)
    if result["scientific_certificate_issued"] or result["source_authenticity_verified"]:
        raise AssertionError("PR40 gate cannot certify a hidden-world rule")
    return result["termination"]["status"]


def markov_conflict(observations):
    """First direct counterexample to ANY deterministic visible-state Markov map.

    Requires SAME visible source and action but differing measured visible
    successors. This is stronger than disagreement with the 5 candidate rules.
    """
    source = {}
    for probe, history in observations:
        for i, action in enumerate(probe[1]):
            x, y = history[i], history[i + 1]
            key = (x, action)
            witness = {"reset": probe[0], "history": list(probe[1]),
                       "step": i, "before": x, "action": action,
                       "after": y}
            if key in source and source[key]["after"] != y:
                return {"same_visible_input": x, "same_action": action,
                        "witness_a": source[key], "witness_b": witness,
                        "excludes": "all deterministic memoryless visible-state transition rules",
                        "scope": "exact observed deterministic reset experiments"}
            source.setdefault(key, witness)
    return None


def observed_walsh(observations):
    rows = []
    for probe, history in observations:
        for i in range(len(probe[1])):
            x, y = history[i], history[i + 1]
            rows.append(tuple((x >> bit) & 1 for bit in range(4)) +
                        tuple((y >> bit) & 1 for bit in range(4)))
    return {str(bit): str(walsh(rows, (bit, bit + 4))) for bit in range(4)}



def direct_memory_diagnostic(oracle, observations, selected):
    """POST-RUN AMENDMENT: request a non-Markov witness if still absent.

    Costed separately from the exact PR23-vs-classical plan. Only selected
    candidate predictions, not the hidden-world rule, guide the probe.
    """
    if selected not in ("MEMORY_TOGGLE", "MEMORY_SET") or markov_conflict(observations):
        return None
    used = {probe for probe, _ in observations}
    eligible = []
    for index, probe in enumerate(PROBES):
        if probe in used:
            continue
        hypothetical = observations + [(probe, trace(selected, *probe))]
        if markov_conflict(hypothetical):
            eligible.append((10 * len(probe[1]), index, probe))
    if not eligible:
        return {"status": "NO_NONMARKOV_DIAGNOSTIC_IN_PROBE_CATALOG"}
    cost, _, probe = min(eligible)
    plan = plan_mission({
        "question": "Can measured traces refute deterministic visible Markov dynamics?",
        "mission_type": "mathematical",
        "mission_id": "OBS-COL-06-MARKOV-CONFLICT",
        "decision_context": {
            "blocking_uncertainty": "A memory explanation was selected without a direct Markov counterexample",
            "verification": f"Reset {probe[0]}, run {'+'.join(probe[1])}, inspect observable successors",
            "verification_effect": "Two measured successors for the same visible input/action refute deterministic Markov behavior",
        },
    })
    if plan["next_action"]["action"] != "verify":
        raise AssertionError("Omega P1 refused explicit diagnostic verification")
    measured = oracle.query(probe)
    observations.append((probe, measured))
    certificate = markov_conflict(observations)
    return {
        "status": "DIRECT_NONMARKOV_WITNESS" if certificate else "WITNESS_NOT_OBSERVED",
        "probe": [probe[0], list(probe[1])], "measured": list(measured),
        "cost_milli": cost, "p1_called": True,
        "certificate": certificate,
        "not_counted_in_two_step_comparison": True,
    }


def score_episode(world):
    oracle = WorldOracle(world)
    observations = [(probe, oracle.query(probe)) for probe in INITIAL]
    initial_candidates = candidates_from_observations(observations)
    current = initial_candidates
    plans = []
    for iteration in range(MAX_ACTIVE):
        if len(current) <= 1:
            break
        case = make_case(current, observations, world, iteration)
        if not case["checks"]:
            break
        # Calls actual PR23 exact two-step policy and actual Omega P1 bridge.
        selected = plan_with_variable_horizon(
            case, max_depth=2, max_cost_milli=BUDGET_MILLI)
        opt = selected["optimization"]
        p1 = selected["p1"]
        classical = independent_two_step_oracle(case, budget_milli=BUDGET_MILLI)
        if Fraction(classical["expected_total_loss"]) != Fraction(opt["expected_total_loss"]):
            raise AssertionError("PR23 differs from independently enumerated optimum")
        if p1["next_action"]["action"] != opt["action"]:
            raise AssertionError("actual P1 disagrees with optimizer")
        if opt["action"] != "verify":
            plans.append({"status": "abstained", "p1_action": opt["action"],
                          "reference_loss": classical["expected_total_loss"]})
            break
        chosen = opt["policy"]["check_id"]
        choice = next(ch for ch in case["checks"] if ch["id"] == chosen)
        probe = PROBES[int(chosen[1:]) - 1]
        before = len(current)
        warning = advisory(case, chosen)
        actual = oracle.query(probe)
        observations.append((probe, actual))
        current = candidates_from_observations(observations)
        plans.append({
            "status": "measured", "check_id": chosen,
            "probe": [probe[0], list(probe[1])],
            "trace": list(actual), "survivors_before": before,
            "survivors_after": len(current),
            "p1_action": p1["next_action"]["action"],
            "pr40_advisory": warning,
            "pr23_loss": opt["expected_total_loss"],
            "independent_exact_loss": classical["expected_total_loss"],
        })
        if not current:
            break
    # Separate diagnostic; no reserved evidence enters the fit.
    selected_before_diagnostic = current[0] if len(current) == 1 else None
    diagnostic = direct_memory_diagnostic(oracle, observations, selected_before_diagnostic)
    if diagnostic and diagnostic.get("probe"):
        current = candidates_from_observations(observations)
    # Heldout observations are made only AFTER all model/probe decisions.
    selected_rule = current[0] if len(current) == 1 else None
    heldout = []
    for probe in RESERVED:
        prediction = trace(selected_rule, *probe) if selected_rule else None
        actual = oracle.evaluate(probe)
        heldout.append({
            "probe": [probe[0], list(probe[1])], "actual": list(actual),
            "prediction": list(prediction) if prediction is not None else None,
            "correct": prediction == actual if prediction is not None else False,
        })
    known_catalog_result = selected_rule if selected_rule and all(x["correct"] for x in heldout) else None
    status = (
        "OUT_OF_CATALOG_WARNING" if selected_rule is None or any(not x["correct"] for x in heldout)
        else "COMPATIBLE_WITH_TESTED_REPRESENTATION"
    )
    certificate = markov_conflict(observations)
    return {
        "world_for_posthoc_scoring_only": world,
        "initial_candidates": list(initial_candidates),
        "remaining_candidates_after_training": list(current),
        "selected_family": selected_rule,
        "reported_family_after_heldout_gate": known_catalog_result,
        "status": status,
        "training_queries": len(observations),
        "active_queries": len(observations) - len(INITIAL),
        "p1_decision_calls": len(plans),
        "p1_diagnostic_calls": int(bool(diagnostic and diagnostic.get("p1_called"))),
        "post_run_diagnostic": diagnostic,
        "heldout_correct": sum(x["correct"] for x in heldout),
        "heldout_total": len(RESERVED),
        "all_baseline_scores_equal": all(
            x.get("pr23_loss") == x.get("independent_exact_loss")
            for x in plans if x["status"] == "measured"),
        "markov_counterexample_training": certificate,
        "walsh_pr86_training": observed_walsh(observations),
        "plans": plans, "heldout": heldout,
        "llm_calls": 0, "autonomous_scientific_discovery": False,
    }


def run():
    results = [score_episode(world) for world in WORLDS]
    return {
        "protocol": "OBS-COL-06",
        "pre_registered_commit": "4961a9a5a5d81e0eb85d76c71f00893e95a8756e",
        "status": "CALCUL_EXACT_SYNTHETIC_CLOSED_GRAMMAR",
        "competitor": "independent exact two-step enumeration on identical finite candidates",
        "real_omega_p1": True,
        "open_world_discovery": False,
        "no_automatic_certification": True,
        "model_calls": 0,
        "limitations": "Synthetic authored families, oracle reset, fixed probes, posthoc evaluation from same world generator.",
        "episodes": results,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
