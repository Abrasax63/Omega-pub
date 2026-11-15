#!/usr/bin/env python3
"""OBS-COL-05: finite, capped representation expansion from observed transitions.

Uses real Omega P1 for verification plans, GF(2) ANF for representation search,
and independent held-out states to detect incorrect extrapolation.

Model generator known to the EXPERIMENTER, never passed to the learner.
No claim of open-world model discovery, LLM orchestration or scientific proof.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PRISM = ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "prism"
OBS = ROOT / "02_MATHEMATIQUES" / "pilotes" / "observabilite_collective"
for folder in (PRISM, OBS):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
from planner import plan_mission  # Actual Omega P1, not a mock.
from collective_observability import walsh  # Unchanged source from PR #86.

N = 5
STATES = 1 << N
ACTIONS = ("pulse", "bind")
MAX_DEGREE = 3
TRAIN = tuple(x for x in range(STATES) if x.bit_count() <= MAX_DEGREE)
HELD_OUT = tuple(x for x in range(STATES) if x.bit_count() > MAX_DEGREE)
WORLDS = ("affine", "quadratic", "cubic", "quartic_ood")


def hidden_transition(kind, action, x):
    """Oracle's truth; the learning functions NEVER call this function."""
    if kind not in WORLDS or action not in ACTIONS or not 0 <= x < STATES:
        raise ValueError("invalid hidden-world query")
    b = tuple((x >> i) & 1 for i in range(N))
    if kind == "affine":
        if action == "pulse":
            return x ^ 4 ^ (b[1] << 3)
        return x ^ 16 ^ b[4]
    if action == "pulse":
        out = x ^ ((b[0] & b[1]) << 4) ^ (b[2] << 1)
        if kind == "cubic":
            out = x ^ ((b[0] & b[1]) << 4) ^ (b[1] & b[2] & b[3])
        if kind == "quartic_ood":
            out ^= (b[0] & b[1] & b[2] & b[3]) << 4
        return out
    if kind == "cubic":
        return x ^ ((b[1] & b[3]) << 2) ^ ((b[0] & b[2] & b[4]) << 1) ^ 8
    return x ^ ((b[1] & b[3]) << 2) ^ b[4]


class TransitionOracle:
    def __init__(self, kind):
        if kind not in WORLDS:
            raise ValueError("unknown synthetic world")
        self._kind = kind
        self.calls = []

    def observe(self, action, state):
        # The learner may only ask TRAIN queries; evaluation is separate.
        if action not in ACTIONS or state not in TRAIN:
            raise ValueError("query outside allowed training states")
        value = hidden_transition(self._kind, action, state)
        self.calls.append((action, state, value))
        return value

    def evaluate(self, action, state):
        # Explicit evaluator-only endpoint; never given to fit/choose/plan.
        if action not in ACTIONS or state not in HELD_OUT:
            raise ValueError("evaluation outside held-out states")
        return hidden_transition(self._kind, action, state)


def monomials(degree):
    if not 0 <= degree <= N:
        raise ValueError("invalid polynomial degree")
    return tuple(x for x in range(STATES) if x.bit_count() <= degree)


def feature_row(state, degree):
    masks = monomials(degree)
    return sum(1 << i for i, m in enumerate(masks) if state & m == m)


def rank_gf2(vectors):
    basis = {}
    for raw in vectors:
        v = raw
        while v:
            pivot = v.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = v
                break
            v ^= basis[pivot]
    return len(basis)


def fit_bit(observations, degree, bit):
    """Solve exact linear GF2 equations; return None if INCONSISTENT.

    For rank-deficient data the free parameters are set to zero, without
    falsely claiming uniqueness. Basis pivots use highest set coefficient.
    """
    width = len(monomials(degree))
    mask = (1 << width) - 1
    basis = {}
    for state, output in observations:
        row = feature_row(state, degree) | (((output >> bit) & 1) << width)
        while row & mask:
            pivot = (row & mask).bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
        if (row & mask) == 0 and (row >> width) & 1:
            return None
    coefficients = 0
    for pivot in sorted(basis):
        row = basis[pivot]
        rest = ((row & ((1 << pivot) - 1)) & coefficients).bit_count() & 1
        value = ((row >> width) & 1) ^ rest
        coefficients |= value << pivot
    return {"coefficients": coefficients, "rank": len(basis),
            "unique": len(basis) == width}


def fit_system(observations, degree):
    found = [fit_bit(observations, degree, i) for i in range(N)]
    if any(result is None for result in found):
        return None
    return {"degree": degree, "bits": found,
            "full_rank": all(r["unique"] for r in found)}


def minimal_fit(observations):
    for degree in range(1, MAX_DEGREE + 1):
        fit = fit_system(observations, degree)
        if fit is not None:
            return fit
    return None


def predict(fit, state):
    result = 0
    features = feature_row(state, fit["degree"])
    for bit, sol in enumerate(fit["bits"]):
        result |= ((features & sol["coefficients"]).bit_count() & 1) << bit
    return result


def choose_probe(observations, remaining):
    """Source-independent rank-greedy design under the capped degree-3 grammar.

    This algorithm, NOT Omega P1, selects the probe. It optimizes algebraic
    rank, not expected information under an inferred probabilistic prior.
    """
    current = rank_gf2([feature_row(s, MAX_DEGREE) for s, _ in observations])
    options = []
    for state in remaining:
        new = rank_gf2([feature_row(s, MAX_DEGREE) for s, _ in observations]
                       + [feature_row(state, MAX_DEGREE)])
        options.append((-(new - current), state.bit_count(), state))
    return min(options)[2]


def p1_verify(action, state, prior_degree):
    plan = plan_mission({
        "mission_id": f"OBS-COL-05-{action}-{state}",
        "question": "Vérifier un modèle fini par une transition encore inconnue",
        "mission_type": "exploratory",
        "requires_computation": True,
        "decision_context": {
            "blocking_uncertainty": "Le modèle peut ne pas extrapoler hors observations",
            "verification": f"Intervenir par {action} à l'état {state}",
            "verification_effect": "Un contre-exemple peut exclure le degré courant",
        },
    })
    action_decision = plan["next_action"]
    if action_decision["action"] != "verify":
        raise AssertionError("real P1 did not propose verification")
    if action_decision["next_step"] != f"Intervenir par {action} à l'état {state}":
        raise AssertionError("P1 verification step mismatch")
    return {"p1_called": True, "action": action_decision["action"],
            "prior_degree": prior_degree}


def learn_action(oracle, action):
    observations, promotions, plan_count = [], [], 0
    remaining = list(TRAIN)
    prior_degree = 1
    while remaining:
        state = choose_probe(observations, remaining)
        gate = p1_verify(action, state, prior_degree)
        plan_count += int(gate["p1_called"])
        observations.append((state, oracle.observe(action, state)))
        remaining.remove(state)
        fit = minimal_fit(observations)
        if fit is None:
            return {"status": "OUT_OF_FAMILY_ON_TRAIN", "observations": observations,
                    "p1_calls": plan_count, "promotions": promotions}
        if fit["degree"] > prior_degree:
            promotions.append({"at_state": state, "from_degree": prior_degree,
                               "to_degree": fit["degree"], "observations": len(observations)})
            prior_degree = fit["degree"]
    fitted = minimal_fit(observations)
    if fitted is None:
        raise AssertionError("complete training must be consistent for registered worlds")
    if rank_gf2([feature_row(s, MAX_DEGREE) for s, _ in observations]) != len(monomials(MAX_DEGREE)):
        raise AssertionError("degree-3 feature basis not fully covered")
    return {"status": "FITTED_ON_TRAIN", "fit": fitted,
            "observations": observations, "promotions": promotions,
            "p1_calls": plan_count}


def walsh_observed_invariants(data):
    """Apparent conservation only, relative to observed transition pairs."""
    rows = [tuple((state >> i) & 1 for i in range(N)) +
            tuple((output >> i) & 1 for i in range(N))
            for state, output in data]
    candidates = []
    for mask in range(1, STATES):
        coords = tuple(i for i in range(N) if mask & (1 << i))
        coords += tuple(i + N for i in range(N) if mask & (1 << i))
        if walsh(rows, coords) == 1:
            candidates.append(mask)
    return candidates


def score_world(kind):
    oracle = TransitionOracle(kind)
    learned = {action: learn_action(oracle, action) for action in ACTIONS}
    if any(a["status"] != "FITTED_ON_TRAIN" for a in learned.values()):
        return {"world": kind, "status": "OUT_OF_FAMILY_ON_TRAIN"}
    results, fixed_affine, fixed_cubic = [], [], []
    for action in ACTIONS:
        data = learned[action]["observations"]
        model = learned[action]["fit"]
        affine = fit_system(data, 1)
        cubic = fit_system(data, 3)
        assert cubic is not None and cubic["full_rank"]
        for state in HELD_OUT:
            truth = oracle.evaluate(action, state)
            estimated = predict(model, state)
            results.append({"action": action, "state": state, "actual": truth,
                            "predicted": estimated, "correct": truth == estimated})
            fixed_affine.append(affine is not None and predict(affine, state) == truth)
            fixed_cubic.append(predict(cubic, state) == truth)
    warnings = any(not r["correct"] for r in results)
    # Trace a feedback-coupled sequence only for post-hoc interpretation.
    seq = []
    state = 0
    for action in ("pulse", "bind", "pulse", "bind"):
        after = hidden_transition(kind, action, state)
        seq.append({"input": state, "action": action, "output": after,
                    "changed_group": [i for i in range(N) if ((state ^ after) >> i) & 1]})
        state = after
    n = len(results)
    return {
        "world": kind, "status": "OUT_OF_FAMILY_WARNING" if warnings else "WITHIN_HOLDOUT_CHECKS",
        "inferred_degrees": {a: learned[a]["fit"]["degree"] for a in ACTIONS},
        "promotions": {a: learned[a]["promotions"] for a in ACTIONS},
        "train_observations": {a: len(learned[a]["observations"]) for a in ACTIONS},
        "p1_calls": sum(learned[a]["p1_calls"] for a in ACTIONS),
        "holdout_correct": sum(r["correct"] for r in results),
        "holdout_total": n,
        "affine_baseline_correct": sum(fixed_affine),
        "cubic_baseline_correct": sum(fixed_cubic),
        "heldout_mismatches": [r for r in results if not r["correct"]],
        "observed_linear_invariants": {a: walsh_observed_invariants(learned[a]["observations"]) for a in ACTIONS},
        "group_trace_posthoc": seq,
        "model_calls": 0, "certified_universal_law": False,
    }


def run():
    cases = [score_world(kind) for kind in WORLDS]
    return {
        "experiment": "OBS-COL-05", "status": "FINITE_SYNTHETIC_ALGEBRAIC_REPRESENTATION",
        "prereg": "c9919f2d3468ca4b450d6a1b8ed4844957a5154d",
        "n_bits": N, "states": STATES, "actions": list(ACTIONS),
        "train_states_per_action": len(TRAIN), "holdout_states_per_action": len(HELD_OUT),
        "policy": "classical GF2 rank selection; real Omega P1 validates verification plan",
        "llm_calls": 0, "not_autonomous_open_world_discovery": True,
        "limitations": "Authored worlds, public generator, degree cap fixed by researcher; fixed cubic is strong baseline; no external blind holdout or physical measurements.",
        "cases": cases,
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
