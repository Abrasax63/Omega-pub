"""OMEGA-PLASTICITY-01: observed-return learning over resettable known Mealy machines.

A -> B -> A' changes only the exogenous cost of a probe (not the automaton).
The learner never receives optimal actions, Q values, or hidden initial states.
The unchanged PR76 oracle is used only inside evaluate(), not while training.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import math
import random
import sys

MEALY_DIR = Path(__file__).resolve().parents[1] / "omega-mealy-learning"
sys.path.insert(0, str(MEALY_DIR))
from mealy_lab import (Mealy, Check, PROBES, random_machine,
                       make_cohorts as prior_cohorts, digest, solve)  # noqa: E402

EXPERIMENT = "OMEGA-PLASTICITY-01"
GROUPS = (
    ("train_A", 3017, 36),
    ("train_B", 4017, 36),
    ("relearn_A", 5017, 16),
    ("eval_A", 6017, 18),
    ("eval_B", 7017, 18),
    ("eval_Aprime", 8017, 24),
)
BEHAVIOR_SEED = 19001
LEARNING_RATE = 0.025
MEMORY_K = 7
FEATURE_COUNT = 9
A_COSTS = (1, 2)
B_COSTS = (3, 1)
CHECKPOINTS = (0, 8, 16)


def group_machines():
    previous = prior_cohorts()
    seen = {signature for group in previous.values()
            for signature, _ in group["machines"]}
    result = {}
    for name, seed, count in GROUPS:
        rng = random.Random(seed)
        machines = []
        attempts = collisions = 0
        while len(machines) < count:
            attempts += 1
            if attempts > 100000:
                raise RuntimeError("SAMPLER_EXHAUSTED")
            machine = random_machine(rng)
            sig = machine.signature()
            if sig in seen:
                collisions += 1
                continue
            seen.add(sig)
            machines.append((sig, machine))
        result[name] = dict(seed=seed, size=count, attempts=attempts,
                            collisions=collisions, machines=machines)
    assert len(seen) == 90 + sum(g[2] for g in GROUPS)
    return result


def checks_for(machine, costs):
    if costs not in (A_COSTS, B_COSTS):
        raise ValueError("INVALID_ENVIRONMENT_COSTS")
    return tuple(Check(c.name, costs[c.cost - 1], c.values)
                 for c in machine.checks())


def fully_identifiable(checks, count):
    patterns = [tuple(check.values[initial] for check in checks)
                for initial in range(count)]
    return len(set(patterns)) == count


def outcome_blocks(group, check):
    parts = {}
    for state in group:
        parts.setdefault(check.values[state], []).append(state)
    return tuple(tuple(v) for v in parts.values())


def choices(group, checks):
    return tuple(check for check in checks
                 if len(outcome_blocks(group, check)) > 1)


def features(group, check):
    blocks = outcome_blocks(group, check)
    n = len(group)
    gini = (n*n - sum(len(b)**2 for b in blocks)) / (n*n)
    reduction = (n - max(len(b) for b in blocks)) / n
    singletons = sum(len(b) == 1 for b in blocks) / n
    return (
        1.0,                             # intercept
        check.cost / 3.0,                # variable cost environment
        gini,
        reduction,
        singletons,
        float(len(check.name) == 2),    # length 2 probe
        gini / check.cost,
        1.0 / n,
        check.cost * gini / 3.0,
    )


def score(weights, vector):
    return sum(w*x for w, x in zip(weights, vector))


@dataclass
class LinearPolicy:
    weights: list[float]
    updates: int = 0

    @classmethod
    def blank(cls):
        return cls([0.0]*FEATURE_COUNT)

    def learn(self, observations):
        for item in observations:
            x = item["features"]
            y = float(item["observed_return_to_go"])
            residual = min(10.0, max(-10.0, y - score(self.weights, x)))
            for i in range(FEATURE_COUNT):
                self.weights[i] += LEARNING_RATE * residual * x[i]
            self.updates += 1
        if any(not math.isfinite(w) for w in self.weights):
            raise AssertionError("NONFINITE_TRAINING_WEIGHTS")
        return self

    def snapshot(self):
        return dict(weights=list(self.weights), updates=self.updates,
                    weights_sha256=digest(self.weights))


def estimate_memory(feat, memory):
    if not memory:
        raise ValueError("MEMORY_NOT_TRAINED")
    nearest = sorted((
        (sum((a-b)**2 for a,b in zip(feat, item["features"])), i,
         item["observed_return_to_go"])
        for i, item in enumerate(memory)
    ))[:MEMORY_K]
    return sum(val for _,_,val in nearest) / len(nearest)


def choose(group, checks, arm, weights=None, memory=None, rng=None):
    """No hidden state, no oracle, no future observation in this interface."""
    available = choices(group, checks)
    if not available:
        return None
    if arm == "explore":
        if rng is None:
            raise ValueError("EXPLORATION_RNG_REQUIRED")
        return rng.choice(available)
    if arm == "fixed":
        return min(available, key=lambda c: (
            -(features(group, c)[2]/c.cost), c.cost, c.name))
    if arm == "memory":
        return min(available, key=lambda c: (
            estimate_memory(features(group, c), memory), c.cost, c.name))
    if arm == "learned":
        return min(available, key=lambda c: (
            score(weights, features(group, c)), c.cost, c.name))
    raise ValueError("UNKNOWN_POLICY")


def run_episode(machine, checks, hidden_initial, arm, *,
                rng=None, weights=None, memory=None, log=True):
    """Simulated world holds hidden_initial. Selector sees only belief + table."""
    group = tuple(range(machine.size))
    history = []
    cumulative = 0
    while len(group) > 1:
        selected = choose(group, checks, arm, weights=weights,
                          memory=memory, rng=rng)
        if selected is None:
            return dict(success=False, total_cost=cumulative,
                        remaining=list(group), decisions=history)
        belief = group
        observation = selected.values[hidden_initial]
        group = tuple(s for s in group
                      if selected.values[s] == observation)
        if not group or len(group) >= len(belief):
            raise AssertionError("INVALID_OBSERVATION_PARTITION")
        cumulative += selected.cost
        if log:
            history.append(dict(
                action=selected.name,
                cost=selected.cost,
                features=features(belief, selected),
                belief_before=list(belief),
                observation=list(observation),
                belief_after=list(group),
            ))
    if group != (hidden_initial,):
        raise AssertionError("FALSE_IDENTIFICATION")
    return dict(success=True, total_cost=cumulative,
                remaining=list(group), decisions=history)


def collect_phase(machines, costs, phase, rng):
    """Only real trajectory outcomes become targets. No use of solve() here."""
    items = []
    episodes = []
    eligible = impossible = 0
    for sig, machine in machines:
        checks = checks_for(machine, costs)
        if not fully_identifiable(checks, machine.size):
            impossible += 1
            episodes.append(dict(signature=sig, phase=phase,
                                 status="IMPOSSIBLE_WITH_SIX_PROBES"))
            continue
        eligible += 1
        for hidden in range(machine.size):
            episode = run_episode(machine, checks, hidden, "explore", rng=rng)
            if not episode["success"]:
                raise AssertionError("EXPLORATION_FAILED_ON_IDENTIFIABLE_MACHINE")
            steps = episode["decisions"]
            remaining = 0
            for decision in reversed(steps):
                remaining += decision["cost"]
                decision["observed_return_to_go"] = remaining
            for decision in steps:
                items.append({
                    "phase": phase,
                    "signature": sig,
                    "action": decision["action"],
                    "features": decision["features"],
                    "observed_return_to_go": decision["observed_return_to_go"],
                })
            episodes.append(dict(
                signature=sig, phase=phase, status="IDENTIFIED",
                episode_cost=episode["total_cost"],
                observed_decisions=steps,
                # The evaluator's hidden index is not a training feature.
                result_state=episode["remaining"][0],
            ))
    return dict(phase=phase, machines=len(machines), eligible=eligible,
                impossible=impossible, episodes=episodes, examples=items,
                examples_sha256=digest(items),
                episodes_sha256=digest(episodes))


def evaluate(machines, costs, policies):
    """Exact PR76 oracle and hidden states used for scoring ONLY, never learning."""
    result = []
    eligible = 0
    for sig, machine in machines:
        checks = checks_for(machine, costs)
        exact = solve(tuple(range(machine.size)), checks)
        visible = fully_identifiable(checks, machine.size)
        if visible != (exact["adaptive"] is not None):
            raise AssertionError("ORACLE_IDENTIFIABILITY_MISMATCH")
        row = dict(signature=sig, identifiable=visible,
                   oracle_worst=exact["adaptive"], arms={})
        if visible:
            eligible += 1
            for name, (arm, weights, memory) in policies.items():
                outcomes = [run_episode(machine, checks, s, arm,
                                        weights=weights, memory=memory,
                                        log=False) for s in range(machine.size)]
                if not all(e["success"] for e in outcomes):
                    raise AssertionError("FALSELY_ABSTAINED")
                costs_observed = [e["total_cost"] for e in outcomes]
                worst = max(costs_observed)
                if worst < exact["adaptive"]:
                    raise AssertionError("POLICY_BEATS_MINIMAX_ORACLE")
                row["arms"][name] = dict(
                    cost_mean=sum(costs_observed)/machine.size,
                    cost_worst=worst,
                    cost_per_state=costs_observed,
                    worst_regret=worst-exact["adaptive"],
                )
        else:
            row["status"] = "PROVEN_INDISTINGUISHABLE"
        result.append(row)
    means = {}
    if eligible:
        for name in policies:
            active = [r["arms"][name] for r in result if r["identifiable"]]
            means[name] = dict(
                mean_cost=sum(v["cost_mean"] for v in active)/eligible,
                mean_worst=sum(v["cost_worst"] for v in active)/eligible,
                mean_worst_regret=sum(v["worst_regret"] for v in active)/eligible,
            )
    return dict(total=len(machines), eligible=eligible,
                impossible=len(machines)-eligible,
                mean_by_policy=means, rows=result)


def _policies(warm, memory, cold=None):
    policies = {
        "FIXED": ("fixed", None, None),
        "MEMORY": ("memory", None, memory),
        "WARM": ("learned", list(warm.weights), None),
    }
    if cold is not None:
        policies["COLD"] = ("learned", list(cold.weights), None)
    return policies


def _mean(report, arm):
    return report["mean_by_policy"][arm]["mean_cost"]


def conduct():
    cohorts = group_machines()
    rng = random.Random(BEHAVIOR_SEED)
    warm = LinearPolicy.blank()
    cold = LinearPolicy.blank()
    memory = []
    initial_snapshot = warm.snapshot()

    train_A = collect_phase(cohorts["train_A"]["machines"], A_COSTS, "train_A", rng)
    memory.extend(train_A["examples"])
    warm.learn(train_A["examples"])
    after_A = warm.snapshot()
    eval_A_after_A = evaluate(cohorts["eval_A"]["machines"], A_COSTS,
                             _policies(warm, memory))

    train_B = collect_phase(cohorts["train_B"]["machines"], B_COSTS, "train_B", rng)
    memory.extend(train_B["examples"])
    warm.learn(train_B["examples"])
    after_B = warm.snapshot()
    eval_A_after_B = evaluate(cohorts["eval_A"]["machines"], A_COSTS,
                             _policies(warm, memory))
    eval_B_after_B = evaluate(cohorts["eval_B"]["machines"], B_COSTS,
                             _policies(warm, memory))

    relearn = collect_phase(cohorts["relearn_A"]["machines"],
                            A_COSTS, "relearn_A", rng)
    # Both receive exact same observations, with no access to held-out answers.
    initial_examples = relearn["examples"]
    by_machine = {}
    for item in initial_examples:
        by_machine.setdefault(item["signature"], []).append(item)
    ordered = [sig for sig, _ in cohorts["relearn_A"]["machines"]]

    checkpoints = []
    for count in CHECKPOINTS:
        if count:
            previous = CHECKPOINTS[CHECKPOINTS.index(count)-1]
            new = [item for sig in ordered[previous:count]
                   for item in by_machine.get(sig, [])]
            warm.learn(new)
            cold.learn(new)
            memory.extend(new)
        validation = evaluate(cohorts["eval_Aprime"]["machines"], A_COSTS,
                              _policies(warm, memory, cold))
        checkpoints.append(dict(
            relearn_machines=count,
            seen_relearn_examples=sum(len(by_machine.get(sig,[]))
                                     for sig in ordered[:count]),
            warm=warm.snapshot(), cold=cold.snapshot(),
            memory_records=len(memory),
            evaluation=validation,
        ))
    if checkpoints[-1]["seen_relearn_examples"] != len(initial_examples):
        raise AssertionError("EXAMPLES_LOST_ON_RELEARN")

    all_evaluations = (eval_A_after_A, eval_A_after_B, eval_B_after_B)
    if any(r["eligible"] == 0 for r in all_evaluations) or any(
            r["evaluation"]["eligible"] == 0 for r in checkpoints):
        status = "INSUFFICIENT_IDENTIFIABLE_CASES"
        primary = retention = plasticity = None
    else:
        primary = sum(
            _mean(row["evaluation"], "WARM") - _mean(row["evaluation"], "COLD")
            for row in checkpoints
        )/len(checkpoints)
        retention = _mean(eval_A_after_B,"WARM") - _mean(eval_A_after_A,"WARM")
        plasticity = (_mean(checkpoints[-1]["evaluation"], "WARM") -
                      _mean(checkpoints[0]["evaluation"], "WARM"))
        status = ("DESCRIPTIVE_RELEARNING_ADVANTAGE" if primary < 0
                  else "RELEARNING_REGRESSION" if primary > 0
                  else "NO_RELEARNING_ADVANTAGE")

    groups = {}
    for name, info in cohorts.items():
        sigs = [s for s,_ in info["machines"]]
        groups[name] = dict(seed=info["seed"], size=info["size"],
                            attempts=info["attempts"], collisions=info["collisions"],
                            signatures=sigs, signature_sha256=digest(sigs))
    phases = {
        "train_A": train_A,
        "train_B": train_B,
        "relearn_A": relearn,
    }
    result = dict(
        experiment=EXPERIMENT,
        status=status,
        prereg_commit="a97fff4b57bebb01ed28c412d05f1e66a9e2cb9f",
        behavior_seed=BEHAVIOR_SEED,
        phase_costs=dict(A=list(A_COSTS), B=list(B_COSTS), A_prime=list(A_COSTS)),
        information_constraint="known_Mealy_unknown_initial_state_no_optimal_labels_in_training",
        data_splits=groups,
        training_logs=phases,
        snapshots=dict(initial=initial_snapshot, after_A=after_A, after_B=after_B),
        evaluation_A_after_A=eval_A_after_A,
        evaluation_A_after_B=eval_A_after_B,
        evaluation_B_after_B=eval_B_after_B,
        relearn_checkpoints=checkpoints,
        primary_WARM_minus_COLD_mean_over_Aprime_checkpoints=primary,
        retention_delta_A_after_B_minus_A_after_A=retention,
        plasticity_delta_Aprime_after_16_minus_0=plasticity,
        full_observation_total=sum(len(x["examples"]) for x in phases.values()),
        training_uses_oracle=False,
        learned_parameters_changed=(warm.updates > 0 and
                                    warm.snapshot()["weights_sha256"] !=
                                    initial_snapshot["weights_sha256"]),
        model_training="linear_observed_return_regression_only",
        language_model_trained=False,
        cost_matching="same_probes_same_logged_relearn_experience_not_equal_prior_history_or_CPU",
        api_calls=0,
        main_modified=False,
        scientific_generalization_proven=False,
        limitations=[
            "All transition and output tables are supplied; only starting state unknown.",
            "Results apply to a restricted menu of six reset probes.",
            "Cost shift B is exogenous and synthetic, not a changed Mealy transition rule.",
            "Warm has A+B prior data but cold has none; A' marginal experience is identical.",
            "Full oracle is evaluation-only and checks worst-case bounds, not average optimality.",
            "No neural language model is trained and no autonomous code change occurs.",
            "One preregistered holdout is descriptive, not a replicated scientific effect.",
        ],
    )
    if not result["learned_parameters_changed"] or cold.updates <= 0:
        raise AssertionError("NO_REAL_LEARNING_UPDATE")
    signatures = [set(x["signatures"]) for x in groups.values()]
    for i in range(len(signatures)):
        for j in range(i):
            if signatures[i] & signatures[j]:
                raise AssertionError("CROSS_SPLIT_ISOMORPHISM_LEAK")
    if any(x["eligible"] + x["impossible"] != x["machines"]
           for x in phases.values()):
        raise AssertionError("DROPPED_TRAIN_CASES")
    return result


def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args=p.parse_args()
    report=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,sort_keys=True,indent=2,
                                     ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "experiment":EXPERIMENT,
        "status":report["status"],
        "primary_warm_minus_cold":report["primary_WARM_minus_COLD_mean_over_Aprime_checkpoints"],
        "retention_delta":report["retention_delta_A_after_B_minus_A_after_A"],
        "plasticity_delta":report["plasticity_delta_Aprime_after_16_minus_0"],
        "A_evaluable":report["evaluation_A_after_A"]["eligible"],
        "B_evaluable":report["evaluation_B_after_B"]["eligible"],
        "Aprime_evaluable":report["relearn_checkpoints"][0]["evaluation"]["eligible"],
        "warm_updates":report["relearn_checkpoints"][-1]["warm"]["updates"],
        "cold_updates":report["relearn_checkpoints"][-1]["cold"]["updates"],
        "report_sha256":sha256(args.output.read_bytes()).hexdigest(),
    },sort_keys=True))


if __name__=="__main__":
    main()
