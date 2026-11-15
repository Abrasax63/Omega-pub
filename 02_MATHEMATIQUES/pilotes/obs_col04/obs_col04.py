#!/usr/bin/env python3
"""OBS-COL-04: active finite invariant refutation with real Omega P1/PR23/PR40.

Hypothesis family and query language are known in advance. The true model
is hidden from the planner; this is NOT open-world scientific discovery.
No LLM, API, external agent or durable memory writes are made.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
for path in (
    ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "prism",
    ROOT / "02_MATHEMATIQUES" / "pilotes" / "observabilite_collective",
):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
from action_planning_two_step import plan_with_variable_horizon
from observer_guard_bridge import inspect_observer_evidence
from collective_observability import walsh

ACTIONS = ("pulse", "bind")
TARGETS = (
    (2, 3, 1, 6), (2, 3, 5, 6), (1, 6, 5, 2),
    (1, 6, 2, 2), (0, 3, 2, 6), (0, 3, 5, 6)
)
MAX_NEW_QUERIES = 3


@dataclass(frozen=True, order=True)
class Rule:
    selector: int
    mask0: int
    mask1: int
    bind_mask: int

    def outcome(self, state: int, action: str) -> int:
        if not 0 <= state < 8 or action not in ACTIONS:
            raise ValueError("invalid state/action")
        mask = (self.bind_mask if action == "bind" else
                self.mask1 if (state >> self.selector) & 1 else self.mask0)
        return state ^ mask

    def interaction(self, state: int, action: str):
        delta = state ^ self.outcome(state, action)
        return tuple(i for i in range(3) if delta & (1 << i))


def hypothesis_catalog():
    """Fixed 36-model class; no target label or invariant is supplied."""
    return tuple(Rule(*p) for p in product(range(3), (3, 6), (1, 2, 5), (2, 6)))


def invariant_masks(edges):
    """Find ALL nonzero linear GF(2) invariants of the supplied transitions."""
    return tuple(m for m in range(1, 8)
                 if all(((u ^ v) & m).bit_count() % 2 == 0 for u, v in edges))


def full_invariants(model):
    return invariant_masks(tuple((s, model.outcome(s, a))
                                 for s in range(8) for a in ACTIONS))


def prediction(model, state, action, sensor):
    return (model.outcome(state, action) & sensor).bit_count() % 2


class Oracle:
    """The hidden generator is NEVER passed to the plan or gate."""
    def __init__(self, target):
        self._target = target
        self.queries = []

    def ask(self, state, action, sensor):
        if not 1 <= sensor <= 7:
            raise ValueError("invalid sensor")
        answer = prediction(self._target, state, action, sensor)
        self.queries.append((state, action, sensor, answer))
        return answer


def consistent(model, observations):
    return all(prediction(model, s, a, sensor) == outcome
               for s, a, sensor, outcome in observations)


def decide(model):
    labels = full_invariants(model)
    return ",".join(map(str, labels)) if labels else "none"


def probe_catalog():
    return tuple((s, "pulse", m) for s in range(1, 8) for m in range(1, 8))


def check_id(probe):
    return f"s{probe[0]}-a{probe[1]}-m{probe[2]}"


def make_case(models, observations, case_id):
    if not 1 <= len(models) <= 64:
        raise ValueError("unsupported model family")
    catalog = hypothesis_catalog()
    hypotheses = [{"id": f"h-{catalog.index(r):02d}", "decision": decide(r), "weight": 1}
                  for r in models]
    counts = Counter(h["decision"] for h in hypotheses)
    base_error = len(hypotheses) - max(counts.values())
    scored = []
    for probe in probe_catalog():
        if any(probe == obs[:3] for obs in observations):
            continue
        outputs = [str(prediction(m, *probe)) for m in models]
        groups = defaultdict(Counter)
        for h, outcome in zip(hypotheses, outputs):
            groups[outcome][h["decision"]] += 1
        after = sum(sum(g.values()) - max(g.values()) for g in groups.values())
        cost = 12 * probe[2].bit_count()
        scored.append((-(base_error-after), cost, check_id(probe), probe, outputs))
    scored.sort()
    # Cover all seven probe states before allocating one additional choice.
    selected, covered = [], set()
    for entry in scored:
        if entry[3][0] not in covered:
            selected.append(entry)
            covered.add(entry[3][0])
    for entry in scored:
        if len(selected) >= 8:
            break
        if entry not in selected:
            selected.append(entry)
    checks = []
    for _, cost, name, probe, outputs in selected[:8]:
        checks.append({"id": name, "step": f"Observe state {probe[0]} action {probe[1]} sensor {probe[2]}",
                       "method": "finite_reset_intervention", "action": "verify",
                       "available": True, "cost_milli": cost, "observations": outputs})
    return {"case_id": case_id, "question": "Which linear invariants survive?",
            "mission_type": "mathematical", "uncertainty": "Several models still fit the data",
            "hypotheses": hypotheses, "checks": checks}


def decode_check(name):
    p = name.split("-")
    return (int(p[0][1:]), p[1][1:], int(p[2][1:]))


def independent_two_step_oracle(case, budget_milli=144):
    """Enumerate 0, 1, 2 tests independently of PR23 dynamic programming."""
    h, checks = case["hypotheses"], case["checks"]
    indices = tuple(range(len(h)))

    def err(group):
        labels = Counter(h[i]["decision"] for i in group)
        return len(group) - max(labels.values()) if group else 0

    def parts(group, check_index):
        outcomes = defaultdict(list)
        for i in group:
            outcomes[checks[check_index]["observations"][i]].append(i)
        return tuple(outcomes.values())

    best_loss, best_id = Fraction(err(indices)), None
    for i, check in enumerate(checks):
        cost = check["cost_milli"]
        if cost > budget_milli:
            continue
        loss = Fraction(len(indices) * cost, 1000)
        for branch in parts(indices, i):
            branch_loss = Fraction(err(branch))
            for j, next_check in enumerate(checks):
                next_cost = next_check["cost_milli"]
                if i == j or cost + next_cost > budget_milli:
                    continue
                candidate = Fraction(len(branch) * next_cost, 1000)
                candidate += sum(err(subgroup) for subgroup in parts(branch, j))
                branch_loss = min(branch_loss, candidate)
            loss += branch_loss
        if loss < best_loss:
            best_loss, best_id = loss, check["id"]
    return {"first_check": best_id, "expected_total_loss": str(best_loss / len(h))}


def observer_advisory(case, chosen):
    """PR40 gate is only an advisory on *declared, incomplete* probe models."""
    if not case["checks"]:
        return None
    selected = next((c for c in case["checks"] if c["id"] == chosen), case["checks"][0])
    def partition(outputs):
        labels = {}
        return [labels.setdefault(v, len(labels)) for v in outputs]
    report = inspect_observer_evidence({"termination": {
        "current_partition": [0] * len(case["hypotheses"]),
        "selected_probe_partition": partition(selected["observations"]),
        "listed_probe_partitions": [partition(c["observations"]) for c in case["checks"]],
        "declared_exhaustive": False,
    }})
    if report.get("scientific_certificate_issued") or report.get("source_authenticity_verified"):
        raise AssertionError("gate must not certify an unknown source")
    return report


def initial_data(oracle):
    return [(0, a, m, oracle.ask(0, a, m)) for a in ACTIONS for m in (1, 2, 4)]


def initial_invariants(data):
    edges = []
    for action in ACTIONS:
        pieces = [(sensor, output) for s, a, sensor, output in data
                  if s == 0 and a == action]
        if {m for m, _ in pieces} != {1, 2, 4}:
            raise ValueError("incomplete initial sensors")
        edges.append((0, sum(m for m, value in pieces if value)))
    return invariant_masks(tuple(edges)), tuple(edges)


def initial_walsh(edges, masks):
    out = {}
    for mask in masks:
        coords = tuple(i for i in range(3) if mask & (1 << i))
        coords += tuple(i + 3 for i in range(3) if mask & (1 << i))
        rows = tuple(tuple((s >> i) & 1 for i in range(3)) +
                     tuple((y >> i) & 1 for i in range(3)) for s, y in edges)
        out[str(mask)] = str(walsh(rows, coords))
    return out


def fixed_baseline(target):
    oracle = Oracle(target)
    obs = initial_data(oracle)
    models = tuple(r for r in hypothesis_catalog() if consistent(r, obs))
    probes = []
    for state in (1, 2, 4):
        if len({decide(r) for r in models}) == 1:
            break
        probe = (state, "pulse", 7)
        answer = oracle.ask(*probe)
        obs.append((*probe, answer))
        probes.append({"probe": list(probe), "observation": answer})
        models = tuple(r for r in models if consistent(r, obs))
    return {"extra_probes": probes, "possible_decisions": sorted({decide(r) for r in models}),
            "estimated_milli_cost": sum(12 * x["probe"][2].bit_count() for x in probes)}


def run_episode(target_tuple, index):
    target, oracle = Rule(*target_tuple), Oracle(Rule(*target_tuple))
    observations = initial_data(oracle)
    apparent, initial_edges = initial_invariants(observations)
    walsh_coefficients = initial_walsh(initial_edges, apparent)
    models = tuple(r for r in hypothesis_catalog() if consistent(r, observations))
    starting_models = len(models)
    steps = []
    for iteration in range(MAX_NEW_QUERIES):
        if len({decide(r) for r in models}) == 1:
            break
        case = make_case(models, observations, f"OBS-COL-04-C{index}-Q{iteration}")
        if not case["checks"]:
            break
        # Genuine PR23 exact optimizer + genuine P1 bridge, not a stand-in.
        bridge = plan_with_variable_horizon(case, max_depth=2, max_cost_milli=144)
        policy = bridge["optimization"]
        if bridge["p1"]["next_action"]["action"] != policy["action"]:
            raise AssertionError("P1/action optimizer disagree")
        independent = independent_two_step_oracle(case)
        if Fraction(independent["expected_total_loss"]) != Fraction(policy["expected_total_loss"]):
            raise AssertionError("PR23 differs from independent exhaustive 2-step reference")
        if policy["action"] != "verify":
            steps.append({"status": "abstain", "action": policy["action"],
                          "reference": independent})
            break
        chosen = policy["policy"]["check_id"]
        probe = decode_check(chosen)
        advisory = observer_advisory(case, chosen)
        answer = oracle.ask(*probe)
        observations.append((*probe, answer))
        updated = tuple(r for r in models if consistent(r, observations))
        if not updated:
            raise AssertionError("true model was eliminated from the closed catalog")
        steps.append({"iteration": iteration, "probe": list(probe), "measurement": answer,
                      "survivors_before": len(models), "survivors_after": len(updated),
                      "p1_action": bridge["p1"]["next_action"]["action"],
                      "independent_two_step": independent,
                      "observer_gate_status": advisory.get("termination", {}).get("status")})
        models = updated

    # Separate, visibly marked confirmatory intervention; at most 3 extra probes.
    confirmation = None
    if apparent and len([s for s in steps if "probe" in s]) < MAX_NEW_QUERIES:
        probe = (7, "pulse", apparent[0])
        prior_value = (7 & probe[2]).bit_count() % 2
        forecasts = sorted({prediction(r, *probe) for r in models})
        answer = oracle.ask(*probe)
        observations.append((*probe, answer))
        updated = tuple(r for r in models if consistent(r, observations))
        if not updated:
            raise AssertionError("confirmation excluded hidden rule")
        confirmation = {"probe": list(probe), "measured": answer,
                        "expected_from_initial_claim": prior_value,
                        "counterexample_observed": answer != prior_value,
                        "forecast_before_measurement": forecasts,
                        "universal_proof": False}
        models = updated

    robust = set(range(1, 8))
    for rule in models:
        robust.intersection_update(full_invariants(rule))
    true_invariants = set(full_invariants(target))  # post-hoc scoring only
    state, sequence = 0, []
    for action in ("pulse", "bind", "pulse"):
        nxt = target.outcome(state, action)
        sequence.append({"before": state, "action": action,
                         "active_group": list(target.interaction(state, action)),
                         "after": nxt})
        state = nxt
    action_probes = [s["probe"] for s in steps if "probe" in s]
    if confirmation:
        action_probes.append(confirmation["probe"])
    return {"case_id": f"OBS-COL-04-C{index}", "initial_models": starting_models,
            "initial_apparent_invariants": list(apparent),
            "initial_walsh_pr86": walsh_coefficients,
            "surviving_models": len(models),
            "possible_invariant_decisions": sorted({decide(r) for r in models}),
            "catalog_robust_invariants": sorted(robust),
            "truth_invariants_posthoc": sorted(true_invariants),
            "false_robust_claim": not robust.issubset(true_invariants),
            "direct_falsification": bool(confirmation and confirmation["counterexample_observed"]),
            "steps": steps, "confirmation": confirmation, "changing_groups": sequence,
            "omega_extra_probes": len(action_probes),
            "omega_estimated_milli_cost": sum(12 * m.bit_count() for _, _, m in action_probes),
            "fixed_baseline": fixed_baseline(target),
            "model_calls": 0, "scientifically_certified": False}


def run():
    episodes = [run_episode(target, i + 1) for i, target in enumerate(TARGETS)]
    return {"protocol": "OBS-COL-04", "status": "FINITE_SYNTHETIC_EXPERIMENT",
            "rules_total": len(hypothesis_catalog()), "cases": len(episodes),
            "planner": "Actual PR23/P1 via inherited PR40 branch, no LLM",
            "observer": "Actual PR40 read-only with declared_exhaustive=False",
            "walsh": "Unchanged PR86 source",
            "no_claim_of_open_world_learning": True,
            "model_calls": 0,
            "limitations": "Public authored cases, fixed candidate family, hypothetical costs; no independent holdout, physical experiment or autonomous agent.",
            "results": episodes}


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
