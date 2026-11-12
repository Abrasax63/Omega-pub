"""OBS-02: exact noisy evidence, correlated verifier failures, archived real model errors.

The 96 Qwen choices are from P5-ACTIVE-01. Probe errors are SIMULATED.
This is an exploratory replay, NOT a new holdout or real faulty-provider study.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

from planner import plan_mission

STATUS = "EXACT_NOISY_PROVENANCE_WITH_REAL_MODEL_OUTPUTS_SYNTHETIC_TOOL_FAULTS"
TOOLS = ("SHARED_B", "SHARED_A", "INDEPENDENT", "GOLD")
COST = {"SHARED_B": F(3, 100), "SHARED_A": F(4, 100),
        "INDEPENDENT": F(8, 100), "GOLD": F(80, 100)}
STATES = tuple(product(range(2), repeat=4))  # C,Z,D,M
POLICIES = ("no_probe", "fixed_shared_pair_correct", "fixed_shared_pair_naive",
            "fixed_shared_independent", "myopic_voi", "entropy_micro",
            "exact_bayes_dp", "omega_provenance_candidate")
MAX_TOOLS = 2
ABSTAIN = F(1, 20)
KINDS = ("MUL", "CRT", "RATE", "INJ")


def prior(p):
    """Weights C~Bernoulli(p), Z,D,M independent Bernoulli(1/4)."""
    if not F(0) <= p <= F(1):
        raise ValueError("invalid model prior")
    values = []
    for c, z, d, m in STATES:
        w = p if c else 1-p
        for b in (z, d, m):
            w *= F(1, 4) if b else F(3, 4)
        values.append(w)
    assert sum(values) == 1
    return tuple(values)


def tool_output(state, tool):
    c, z, d, m = state
    if tool in ("SHARED_A", "SHARED_B"):
        return c ^ z
    if tool == "INDEPENDENT":
        return "?" if m else c ^ d
    if tool == "GOLD":
        return c
    raise ValueError("unknown tool")


def bayes_update(belief, tool, outcome):
    """Filter joint microstate witnesses; no false certainty from noisy claims."""
    if tool not in TOOLS:
        raise ValueError("unknown tool")
    if len(belief) != len(STATES) or sum(belief) != 1:
        raise ValueError("non-normalized belief")
    weights = [w if tool_output(s, tool) == outcome else F(0)
               for s, w in zip(STATES, belief)]
    normalizer = sum(weights)
    if not normalizer:
        raise ValueError("contradictory measurements: no joint microstate witness")
    return tuple(w/normalizer for w in weights), normalizer


def branches(belief, tool):
    values = sorted({tool_output(s, tool) for s, w in zip(STATES, belief)
                     if w > 0}, key=str)
    return {o: bayes_update(belief, tool, o) for o in values}


def prob_correct(belief):
    return sum((w for s, w in zip(STATES, belief) if s[0]), F(0))


def terminal(belief):
    p = prob_correct(belief)
    values = {"ABSTAIN": ABSTAIN, "ACCEPT_MODEL": 3*p-2, "FLIP_MODEL": 1-3*p}
    names = ("ABSTAIN", "ACCEPT_MODEL", "FLIP_MODEL")
    action = max(names, key=lambda a: (values[a], -names.index(a)))
    return action, values[action]


def expectation(belief, tool, continuation):
    return -COST[tool] + sum((mass*continuation(post)
                              for post, mass in branches(belief, tool).values()), F(0))


@lru_cache(maxsize=None)
def dp(belief, available, budget):
    """Standard exact finite-state Bayesian Bellman recursion, ties STOP."""
    best = ("STOP", None)
    value = terminal(belief)[1]
    if budget:
        for tool in available:
            remaining = tuple(x for x in available if x != tool)
            future = expectation(belief, tool,
                     lambda post: dp(post, remaining, budget-1)[1])
            if future > value:
                best, value = ("PROBE", tool), future
    return best, value


def independent_tree_value(belief, budget=2):
    """Independent exhaustive two-level contingent policy enumeration; no dp()."""
    if budget not in (0, 1, 2):
        raise ValueError("tree horizon outside 0..2")
    best = terminal(belief)[1]
    if budget == 0:
        return best
    for first in TOOLS:
        possibilities = branches(belief, first)
        alternatives = ("STOP",) + tuple(x for x in TOOLS if x != first) \
                       if budget == 2 else ("STOP",)
        for contingent in product(alternatives, repeat=len(possibilities)):
            value = -COST[first]
            for (observed, (post, probability)), action in zip(
                    possibilities.items(), contingent):
                if action == "STOP":
                    payoff = terminal(post)[1]
                else:
                    payoff = -COST[action] + sum((
                        mass*terminal(next_belief)[1]
                        for next_belief, mass in branches(post, action).values()
                    ), F(0))
                value += probability*payoff
            if value > best:
                best = value
    return best


def micro_entropy(belief, tool):
    """Observed-outcome entropy about whole microstate, not the target C."""
    from math import log2
    probs = [float(mass) for _, mass in branches(belief, tool).values()]
    return -sum(p*log2(p) for p in probs if p > 0)


def naive_update(p, observed):
    """INTENTIONALLY WRONG: double-count perfectly correlated witness copies."""
    a = F(3, 4) if observed == 1 else F(1, 4)
    b = F(1, 4) if observed == 1 else F(3, 4)
    return p*a/(p*a+(1-p)*b)


class Controller:
    """Decision interface contains belief and ONLY its chosen probe outcomes."""
    def __init__(self, policy, p):
        if policy not in POLICIES:
            raise ValueError("unknown policy")
        self.name = policy
        self.belief = prior(p)
        self.naive_p = p
        self.used = []
        self.observations = []
        self.planner_version = None
        if policy == "omega_provenance_candidate":
            plan = plan_mission({
                "question": "Choisir des preuves complémentaires sans doubler "
                            "un témoin à cause commune.",
                "mission_type": "exploratory",
                "decision_context": {
                    "blocking_uncertainty": "Fiabilité des vérifications et cause commune inconnues",
                    "verification": "Sonder un instrument payé et observer seulement sa réponse",
                    "verification_effect": "Conserver uniquement les micro-états compatibles",
                },
            })
            if plan["next_action"]["action"] != "verify":
                raise AssertionError("P1 did not plan verification")
            self.planner_version = plan["planner_version"]

    def choose(self):
        remaining = tuple(x for x in TOOLS if x not in self.used)
        if (not remaining or len(self.used) >= MAX_TOOLS
                or self.name == "no_probe"):
            return None
        if self.name in ("fixed_shared_pair_correct", "fixed_shared_pair_naive"):
            return ("SHARED_B", "SHARED_A")[len(self.used)]
        if self.name == "fixed_shared_independent":
            return ("SHARED_B", "INDEPENDENT")[len(self.used)]
        if self.name in ("exact_bayes_dp", "omega_provenance_candidate"):
            action, value = dp(self.belief, remaining, MAX_TOOLS-len(self.used))
            return action[1] if action[0] == "PROBE" else None
        if self.name == "myopic_voi":
            current = terminal(self.belief)[1]
            candidate = max(remaining, key=lambda tool: (
                expectation(self.belief, tool, lambda b: terminal(b)[1]),
                -TOOLS.index(tool)))
            future = expectation(self.belief, candidate, lambda b: terminal(b)[1])
            return candidate if future > current else None
        if self.name == "entropy_micro":
            return max(remaining, key=lambda t: (
                micro_entropy(self.belief, t), -TOOLS.index(t)))
        raise AssertionError("not implemented")

    def observe(self, tool, outcome):
        if tool not in TOOLS or tool in self.used or len(self.used) >= MAX_TOOLS:
            raise ValueError("invalid, repeated or over-budget probe")
        before = self.belief
        updated, mass = bayes_update(before, tool, outcome)
        self.belief = updated
        self.used.append(tool)
        if self.name == "fixed_shared_pair_naive":
            self.naive_p = naive_update(self.naive_p, outcome)
        posterior = prob_correct(updated)
        self.observations.append({
            "tool": tool, "observed": outcome,
            "probability_of_observation": str(mass),
            "support_before": sum(w > 0 for w in before),
            "support_after": sum(w > 0 for w in updated),
            "posterior_true_model_correct": str(posterior),
            "both_correctness_hypotheses_possible": 0 < posterior < 1,
            "provenance": ("SHARED_LATENT_Z" if tool.startswith("SHARED")
                           else "INDEPENDENT_D_M" if tool == "INDEPENDENT"
                           else "EXACT_REFERENCE"),
        })

    def final_decision(self):
        if self.name == "fixed_shared_pair_naive":
            p = self.naive_p
            options = {"ABSTAIN": ABSTAIN,
                       "ACCEPT_MODEL": 3*p-2, "FLIP_MODEL": 1-3*p}
            names = ("ABSTAIN", "ACCEPT_MODEL", "FLIP_MODEL")
            return max(names, key=lambda a: (options[a], -names.index(a)))
        return terminal(self.belief)[0]


def _fault(case_id, name):
    h = sha256(f"P5OBS02|{case_id}|{name}".encode("utf-8")).digest()
    return int.from_bytes(h[:8], "big") % 4 == 0


def replay_one(policy, row, p):
    ctrl = Controller(policy, p)
    c = int(row["answer"] == row["gold_posthoc_only"])
    evaluator_hidden_state = (c,
        int(_fault(row["question_id"], "Z")),
        int(_fault(row["question_id"], "D")),
        int(_fault(row["question_id"], "M")))
    while True:
        tool = ctrl.choose()  # no true C, Z, D, M passed to selector
        if tool is None:
            break
        output = tool_output(evaluator_hidden_state, tool)
        ctrl.observe(tool, output)  # reveal only the chosen instrument's output
    decision = ctrl.final_decision()
    right = (decision != "ABSTAIN") and (
        (decision == "ACCEPT_MODEL") == bool(c))
    reward = ABSTAIN if decision == "ABSTAIN" else F(1) if right else F(-2)
    spent = sum((COST[t] for t in ctrl.used), F(0))
    return {
        "case_id": row["question_id"], "kind": row["kind"],
        "final_decision": decision, "correct_final": bool(right),
        "wrong_final": decision != "ABSTAIN" and not right,
        "net": str(reward-spent), "paid_cost": str(spent),
        "used_tools": list(ctrl.used), "observations": ctrl.observations,
        "joint_p_correct_after_probing": str(prob_correct(ctrl.belief)),
        "incorrect_naive_p_correct": str(ctrl.naive_p)
                                    if policy == "fixed_shared_pair_naive" else None,
        "evaluator_only": {"actual_model_correct": bool(c),
            "simulated_tool_faults_Z_D_M": list(evaluator_hidden_state[1:])},
        "planner_version": ctrl.planner_version,
    }


def _load_public_snapshot(input_path):
    """Read 96 earlier Qwen answers; stable small zlib/base64 archival subset."""
    import base64, zlib
    encoded = Path(input_path).read_text(encoding="utf-8").strip()
    raw = zlib.decompress(base64.b64decode(encoded))
    if sha256(raw).hexdigest() != (
            "35d100beafc5f46dd2b4e971a20e44e671410df6fe284c3ddc53278d86d0311c"):
        raise ValueError("archived real-model snapshot changed")
    table = json.loads(raw.decode("utf-8"))
    fields = ("question_id", "kind", "model", "split", "answer", "gold_posthoc_only")
    rows = [dict(zip(fields, record)) for record in table]
    if (len(rows) != 96 or len(set((r["model"],r["question_id"])
                                  for r in rows)) != 96):
        raise ValueError("invalid 96 Qwen source rows")
    if (any(r["kind"] not in KINDS or r["answer"] not in ("A","B")
            or r["gold_posthoc_only"] not in ("A","B") for r in rows)):
        raise ValueError("invalid model labels")
    return rows


def run(input_path):
    rows = _load_public_snapshot(input_path)
    training = [r for r in rows if r["split"] == "calibration"]
    test = [r for r in rows if r["split"] == "test"]
    if len(training) != 32 or len(test) != 64:
        raise ValueError("bad source split")
    priors = {}
    for kind in KINDS:
        c = [r for r in training if r["kind"] == kind]
        if len(c) != 8:
            raise ValueError("expected eight calibration labels per kind")
        priors[kind] = F(1+sum(r["answer"] == r["gold_posthoc_only"]
                             for r in c), 10)
    crosschecked = {}
    for kind, p in priors.items():
        belief = prior(p)
        bellman = dp(belief, TOOLS, MAX_TOOLS)[1]
        tree = independent_tree_value(belief, MAX_TOOLS)
        if bellman != tree:
            raise AssertionError("Bellman/tree mismatch")
        crosschecked[kind] = {"prior_correct": str(p),
                             "exact_dp": str(bellman),
                             "independent_tree": str(tree)}
    policies = {}
    for name in POLICIES:
        traces = [replay_one(name, r, priors[r["kind"]]) for r in test]
        total = sum((F(r["net"]) for r in traces), F(0))
        policies[name] = {
            "realized_total_net": str(total),
            "realized_total_net_float": float(total),
            "correct_published": sum(x["correct_final"] for x in traces),
            "wrong_published": sum(x["wrong_final"] for x in traces),
            "abstained": sum(x["final_decision"] == "ABSTAIN" for x in traces),
            "checks": sum(len(x["used_tools"]) for x in traces),
            "unknown_events": sum(y["observed"] == "?" for x in traces
                                  for y in x["observations"]),
            "tool_counts": dict(Counter(t for x in traces for t in x["used_tools"])),
            "traces": traces,
        }
    a, b = (policies[n]["traces"] for n in
            ("exact_bayes_dp", "omega_provenance_candidate"))
    if any(x["used_tools"] != y["used_tools"] or
           x["final_decision"] != y["final_decision"] for x,y in zip(a,b)):
        raise AssertionError("candidate differs from the classical exact DP")

    start = prior(F(1, 2))
    first, mass = bayes_update(start, "SHARED_B", 1)
    twice, conditional = bayes_update(first, "SHARED_A", 1)
    if twice != first or conditional != 1:
        raise AssertionError("duplicate instrument falsely gained evidence")
    contradiction = False
    try:
        bayes_update(first, "SHARED_A", 0)
    except ValueError:
        contradiction = True
    if not contradiction:
        raise AssertionError("impossible joint witness was accepted")
    return {
        "protocol": "P5-OBS-02", "status": STATUS,
        "source": "P5-ACTIVE-01 GitHub run 43214660818 artifact 13943231674",
        "source_real_Qwen_answers": 96,
        "test_real_Qwen_answers": 64,
        "new_LLM_generations": 0, "paid_api_calls": 0,
        "instrument_faults_are_artificial": True,
        "calibration_priors": {k:str(v) for k,v in priors.items()},
        "independent_calculation": crosschecked,
        "same_source_duplicates_add_zero_information": True,
        "impossible_same_source_contradiction_refused": contradiction,
        "policies": policies,
        "limitations": [
            "Earlier already-analyzed Qwen data: exploratory replay, not a new blinded holdout",
            "Verifier corruption and inconclusive events SIMULATED via SHA256, not measured provider errors",
            "Assumed probability 1/4 per latent noise mechanism, not learned from data",
            "Standard exact POMDP DP is identical to Omega candidate by construction",
            "Naive policy is deliberately mis-specified and may win some realized samples",
            "No active scientific library, P1 performs a static plan only",
            "Only 64 real model errors, no independent generalization claim",
        ],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = run(args.input)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,sort_keys=True,
                            ensure_ascii=False)+"\n",encoding="utf-8")
    print("OBS02_REPLAY_RESULT", json.dumps({
        "status": result["status"], "real_cases": result["test_real_Qwen_answers"],
        "dp_crosscheck": result["independent_calculation"],
        "policies": {k:{f:v[f] for f in (
            "realized_total_net_float","correct_published","wrong_published",
            "abstained","checks","unknown_events")} for k,v in result["policies"].items()},
        "duplicate_adds_no_info": result["same_source_duplicates_add_zero_information"],
    },sort_keys=True,ensure_ascii=False))


if __name__ == "__main__":
    main()
