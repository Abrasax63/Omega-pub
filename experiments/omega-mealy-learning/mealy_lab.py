"""OMEGA-MEALY-LEARN-01. Exact resettable Mealy state diagnosis with an updating policy.

Scope: known Mealy transition and output table, unknown hidden initial state.
Every probe resets to the same hidden initial state, returns a word of outputs.
This is NOT automata model inference from a black-box unknown machine.

The independent exact oracle comes from PR #76's unchanged benchmark.solve.
Only TRAIN data produces teacher labels or updates. No model/API calls.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import cache
from itertools import permutations, product
from math import inf, sqrt
from pathlib import Path
import hashlib
import json
import random
import sys

P5_DIR = Path(__file__).resolve().parents[1] / "p5-finite-verification"
sys.path.insert(0, str(P5_DIR))
from benchmark import Check, partition, solve  # noqa: E402

EXPERIMENT = "OMEGA-MEALY-LEARN-01"
TRAIN_SEED, VALIDATION_SEED, TEST_SEED = 1307, 1729, 2027
TRAIN_N, VALIDATION_N, TEST_N = 40, 20, 30
NUM_STATES, NUM_INPUTS, NUM_OUTPUTS = 4, 2, 3
PROBES = tuple(word for length in (1, 2)
               for word in product(range(NUM_INPUTS), repeat=length))
LEARNING_RATE, EPOCHS, MEMORY_K = 0.05, 5, 7


def digest(data):
    return hashlib.sha256(json.dumps(
        data, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class Mealy:
    transitions: tuple[tuple[int, ...], ...]
    outputs: tuple[tuple[int, ...], ...]

    def __post_init__(self):
        n = len(self.transitions)
        if n < 2 or len(self.outputs) != n:
            raise ValueError("INVALID_MEALY_STATES")
        if any(len(x) != NUM_INPUTS for x in self.transitions + self.outputs):
            raise ValueError("INVALID_MEALY_ARITY")
        if any(not (0 <= y < n) for row in self.transitions for y in row):
            raise ValueError("INVALID_TRANSITION")
        if any(not (0 <= y < NUM_OUTPUTS) for row in self.outputs for y in row):
            raise ValueError("INVALID_OUTPUT")

    @property
    def size(self):
        return len(self.transitions)

    def observe(self, initial, word):
        if initial not in range(self.size):
            raise ValueError("INVALID_INITIAL_STATE")
        state = initial
        produced = []
        for action in word:
            if action not in range(NUM_INPUTS):
                raise ValueError("INVALID_ACTION")
            produced.append(self.outputs[state][action])
            state = self.transitions[state][action]
        return tuple(produced)

    def checks(self):
        return tuple(Check("".join(map(str, w)), len(w),
                           tuple(self.observe(initial, w)
                                 for initial in range(self.size)))
                     for w in PROBES)

    def signature(self):
        """Canonical under relabeling states, never output/symbol permutations."""
        all_forms = []
        for new_to_old in permutations(range(self.size)):
            old_to_new = {old: new for new, old in enumerate(new_to_old)}
            flat = tuple(
                (old_to_new[self.transitions[old][action]],
                 self.outputs[old][action])
                for old in new_to_old
                for action in range(NUM_INPUTS)
            )
            all_forms.append(flat)
        return digest(min(all_forms))


def random_machine(rng):
    transitions = tuple(tuple(rng.randrange(NUM_STATES)
                              for _ in range(NUM_INPUTS))
                        for _ in range(NUM_STATES))
    outputs = tuple(tuple(rng.randrange(NUM_OUTPUTS)
                          for _ in range(NUM_INPUTS))
                    for _ in range(NUM_STATES))
    return Mealy(transitions, outputs)


def make_cohorts():
    """Predeclared counts. De-duplicate globally by canonical isomorphism."""
    used = set()
    result = {}
    for name, seed, count in (
        ("train", TRAIN_SEED, TRAIN_N),
        ("validation", VALIDATION_SEED, VALIDATION_N),
        ("test", TEST_SEED, TEST_N),
    ):
        rng = random.Random(seed)
        items = []
        collisions = 0
        attempts = 0
        while len(items) < count:
            attempts += 1
            if attempts > 100000:
                raise RuntimeError("MACHINE_SAMPLER_EXHAUSTED")
            machine = random_machine(rng)
            sig = machine.signature()
            if sig in used:
                collisions += 1
                continue
            used.add(sig)
            items.append((sig, machine))
        result[name] = {
            "seed": seed,
            "size": count,
            "attempts": attempts,
            "isomorphism_collisions": collisions,
            "machines": items,
        }
    assert len(used) == TRAIN_N + VALIDATION_N + TEST_N
    return result


def blocks(group, check):
    return tuple(sorted((tuple(v) for v in partition(group, [check]).values())))


def informative(group, checks):
    return tuple(c for c in checks if len(blocks(group, c)) > 1)


def features(group, check):
    """State-name independent, outcome-label independent features of a probe."""
    b = blocks(group, check)
    n = len(group)
    squares = sum(len(k)**2 for k in b)
    biggest = max(map(len, b))
    singles = sum(len(k) == 1 for k in b)
    return (
        1.0 / check.cost,
        (n * n - squares) / (n * n),
        (n - biggest) / n,
        len(b) / n,
        singles / n,
        -check.cost / 2.0,
    )


def dot(weights, vals):
    return sum(w * x for w, x in zip(weights, vals))


def exact_teacher(checks):
    """Independent adapter for TRAIN only. Reused by EVALUATOR on test."""
    @cache
    def value(group):
        if len(group) <= 1:
            return 0
        best = inf
        for c in informative(group, checks):
            candidate = c.cost + max(value(b) for b in blocks(group, c))
            if candidate < best:
                best = candidate
        return best

    def qvalue(group, check):
        if check not in informative(group, checks):
            return inf
        return check.cost + max(value(b) for b in blocks(group, check))

    return value, qvalue


def reachable_beliefs(checks, n):
    """All nontrivial reachable subsets, determined before labeling."""
    seen = set()
    pending = [tuple(range(n))]
    while pending:
        group = pending.pop()
        if group in seen:
            continue
        seen.add(group)
        for c in informative(group, checks):
            pending.extend(b for b in blocks(group, c) if len(b) > 1)
    return tuple(sorted((s for s in seen if len(s) > 1),
                        key=lambda x: (-len(x), x)))


def training_examples(machines):
    """TRAIN source only. An exact Q-label is never produced on test for a policy."""
    examples = []
    train_references = []
    for sig, machine in machines:
        checks = machine.checks()
        value, qvalue = exact_teacher(checks)
        teacher = solve(tuple(range(machine.size)), checks)
        expected = value(tuple(range(machine.size)))
        if (teacher["adaptive"] is None and expected != inf) or (
            teacher["adaptive"] is not None and expected != teacher["adaptive"]
        ):
            raise AssertionError("INDEPENDENT_ORACLE_MISMATCH")
        train_references.append({
            "signature": sig, "exact_worst_cost": (
                None if expected == inf else expected),
        })
        for group in reachable_beliefs(checks, machine.size):
            optimal = value(group)
            if optimal == inf:
                continue
            actions = informative(group, checks)
            labeled = [(c.name, features(group, c), qvalue(group, c) - optimal)
                       for c in actions]
            if len(labeled) >= 2:
                examples.append({
                    "machine_signature": sig,
                    "belief_size": len(group),
                    "actions": labeled,
                })
    return examples, train_references


def initial_weights():
    return (0.0,) * 6


def learn_weights(examples):
    """Deterministic online pairwise ranking: no VALIDATION/TEST teacher calls."""
    weights = list(initial_weights())
    updates = 0
    for _ in range(EPOCHS):
        for item in examples:
            actions = item["actions"]
            best = min(actions, key=lambda x: (x[2], x[0]))
            for other in actions:
                if other[2] <= best[2]:
                    continue
                f_best, f_other = best[1], other[1]
                gap = dot(weights, f_best) - dot(weights, f_other)
                if gap <= 0.02:
                    weights = [w + LEARNING_RATE * (x - y)
                               for w, x, y in zip(weights, f_best, f_other)]
                    updates += 1
    return tuple(round(w, 10) for w in weights), updates


def memory_items(examples):
    return tuple((tuple(feature), float(regret), record["machine_signature"])
                 for record in examples
                 for _, feature, regret in record["actions"])


def select_action(group, checks, arm, weights, memory):
    options = informative(group, checks)
    if not options:
        return None
    if arm == "A_fixed":
        # Static Gini-separated pairs per input-symbol cost
        return min(options, key=lambda c: (
            -(features(group, c)[1] / c.cost), c.cost, c.name))
    if arm == "B_memory":
        if not memory:
            raise ValueError("EMPTY_TRAIN_MEMORY")
        def predicted_regret(c):
            x = features(group, c)
            nearest = sorted((
                (sum((a-b)**2 for a,b in zip(x,vec)), i, regret)
                for i, (vec, regret, _) in enumerate(memory)
            ))[:MEMORY_K]
            return sum(regret for _,_,regret in nearest) / len(nearest)
        return min(options, key=lambda c: (predicted_regret(c), c.cost, c.name))
    if arm == "C_learned":
        return min(options, key=lambda c: (
            -dot(weights, features(group, c)), c.cost, c.name))
    raise ValueError("UNKNOWN_ARM")


def episode(machine, hidden_initial, arm, weights, memory):
    """The policy is never passed hidden_initial; it only receives the belief."""
    checks = machine.checks()
    group = tuple(range(machine.size))
    total = 0
    transcript = []
    while len(group) > 1:
        choice = select_action(group, checks, arm, weights, memory)
        if choice is None:
            return {"success": False, "cost": total,
                    "belief": group, "transcript": transcript}
        before = group
        answer = choice.values[hidden_initial]
        group = tuple(i for i in group if choice.values[i] == answer)
        if not group or len(group) >= len(before):
            raise AssertionError("INVALID_BELIEF_UPDATE")
        total += choice.cost
        transcript.append({
            "action": choice.name,
            "observation": list(answer),
            "candidates_before": list(before),
            "candidates_after": list(group),
            "cost": choice.cost,
        })
    if group != (hidden_initial,):
        raise AssertionError("FALSE_IDENTIFICATION")
    return {"success": True, "cost": total,
            "belief": group, "transcript": transcript}


def evaluate_cohort(machines, arms, *, include_per_machine=True):
    """The oracle is used ONLY in the evaluator and never by test policies."""
    rows = []
    comparable = []
    for sig, machine in machines:
        checks = machine.checks()
        reference = solve(tuple(range(machine.size)), checks)
        eligible = reference["adaptive"] is not None
        row = {
            "signature": sig,
            "identifiable_with_six_probes": eligible,
            "oracle_exact_adaptive_worst_cost": reference["adaptive"],
            "oracle_exact_fixed_worst_cost": reference["fixed"],
            "arms": {},
        }
        if eligible:
            for name, weights, memory in arms:
                episodes = [episode(machine, initial, name, weights, memory)
                            for initial in range(machine.size)]
                if not all(e["success"] for e in episodes):
                    raise AssertionError("IDENTIFIABLE_MACHINE_NOT_SOLVED")
                costs = [e["cost"] for e in episodes]
                row["arms"][name] = {
                    "cost_mean": sum(costs) / machine.size,
                    "cost_worst": max(costs),
                    "costs_each_hidden_state": costs,
                    "all_states_correctly_identified": True,
                    "worst_regret_to_exact": max(costs) - reference["adaptive"],
                }
                if max(costs) < reference["adaptive"]:
                    raise AssertionError("POLICY_BEATS_EXACT_OPTIMUM")
            comparable.append(row)
        else:
            # No hidden initial state can be uniquely recovered with this
            # probe menu; report abstention rather than grading fake successes.
            row["status"] = "IMPOSSIBLE_WITH_FROZEN_PROBE_MENU"
        if include_per_machine:
            rows.append(row)
    if not comparable:
        return {"total": len(machines), "eligible": 0,
                "status": "INSUFFICIENT_IDENTIFIABLE_CASES", "rows": rows}
    count = len(comparable)
    def average(key, name):
        return sum(row["arms"][name][key] for row in comparable) / count
    cost = {name: {
        "mean_symbol_cost": average("cost_mean",name),
        "mean_worst_symbol_cost": average("cost_worst",name),
        "mean_worst_regret_to_exact": average("worst_regret_to_exact",name),
    } for name,_,_ in arms}
    diffs = [
        row["arms"]["C_learned"]["cost_mean"] -
        row["arms"]["B_memory"]["cost_mean"] for row in comparable
    ]
    return {
        "total": len(machines),
        "eligible": count,
        "indeterminate": len(machines)-count,
        "arms": cost,
        "primary_C_minus_B": sum(diffs)/count,
        "secondary_C_minus_A": (
            cost["C_learned"]["mean_symbol_cost"] -
            cost["A_fixed"]["mean_symbol_cost"]),
        "machines_C_better_than_B": sum(d < 0 for d in diffs),
        "machines_C_worse_than_B": sum(d > 0 for d in diffs),
        "machines_C_equal_B": sum(d == 0 for d in diffs),
        "rows": rows,
    }


def report():
    cohorts = make_cohorts()
    train_examples, references = training_examples(cohorts["train"]["machines"])
    weights, updates = learn_weights(train_examples)
    memory = memory_items(train_examples)
    a = ("A_fixed", initial_weights(), ())
    b = ("B_memory", initial_weights(), memory)
    c0 = ("C_learned", initial_weights(), ())
    c = ("C_learned", weights, ())
    # Evaluate TRAIN/VALIDATION only after weights are learned. No tuning.
    train_stats = evaluate_cohort(cohorts["train"]["machines"],(a,b,c))
    valid_stats = evaluate_cohort(cohorts["validation"]["machines"],(a,b,c))
    valid_before = evaluate_cohort(cohorts["validation"]["machines"],(a,b,c0))
    test = evaluate_cohort(cohorts["test"]["machines"],(a,b,c))

    if test["eligible"] == 0:
        conclusion = "INSUFFICIENT_IDENTIFIABLE_CASES"
    elif test["primary_C_minus_B"] < 0:
        conclusion = "DESCRIPTIVE_HOLDOUT_IMPROVEMENT_NOT_PROVEN"
    elif test["primary_C_minus_B"] > 0:
        conclusion = "REGRESSION_VS_MEMORY"
    else:
        conclusion = "NO_LEARNED_POLICY_ADVANTAGE"

    report_data = {
        "experiment": EXPERIMENT,
        "status": conclusion,
        "precommitted_protocol": "PREREG_2026-11-16.md",
        "scientific_scope": "known_4_state_resettable_Mealy_hidden_initial_state",
        "not_automata_model_inference": True,
        "oracle_source": "PR76 experiments/p5-finite-verification/benchmark.py::solve unchanged",
        "probes": ["".join(map(str,w)) for w in PROBES],
        "cost_unit": "input_symbols_in_probe",
        "splits": {
            name: {
                "seed": data["seed"], "size": data["size"],
                "attempts": data["attempts"],
                "isomorphism_collisions": data["isomorphism_collisions"],
                "machine_signatures": [sig for sig,_ in data["machines"]],
                "signature_set_sha256": digest([sig for sig,_ in data["machines"]])
            } for name,data in cohorts.items()
        },
        "training": {
            "examples": len(train_examples),
            "teacher_reference": references,
            "teacher_reference_sha256": digest(references),
            "memory_action_records": len(memory),
            "memory_sha256": digest(memory),
            "learner_epochs": EPOCHS,
            "learner_learning_rate": LEARNING_RATE,
            "weights_initial": initial_weights(),
            "weights_final": weights,
            "weights_initial_sha256": digest(initial_weights()),
            "weights_final_sha256": digest(weights),
            "actual_weight_updates": updates,
            "weights_changed": any(w != 0 for w in weights),
            "method": "supervised_online_pairwise_imitation_of_exact_train_oracle",
        },
        "train_assessment": train_stats,
        "validation_assessment": valid_stats,
        "validation_before_training": {
            "mean_cost_C": valid_before.get("arms",{}).get("C_learned",{}).get("mean_symbol_cost"),
            "valid_machine_count": valid_before["eligible"],
        },
        "test_assessment": test,
        "main_modified": False,
        "api_calls": 0,
        "language_model_training": False,
        "independent_generalization_proven": False,
        "limitations": [
          "The transition/output machine is known; hidden initial state only.",
          "The exact oracle is restricted to six length-one/two reset probes.",
          "The learner imitates oracle-labeled TRAIN cases, not autonomous self-improvement.",
          "B and C use the same TRAIN cases but different inference-time compute.",
          "30 reserved machines do not establish universal performance.",
          "Validation and TEST are disjoint under state-label isomorphism only.",
        ],
    }
    if not report_data["training"]["weights_changed"]:
        raise AssertionError("NO_PARAMETER_UPDATE_OBSERVED")
    ssets=[set(report_data["splits"][n]["machine_signatures"])
           for n in ("train","validation","test")]
    if any(ssets[i] & ssets[j] for i,j in ((0,1),(0,2),(1,2))):
        raise AssertionError("CROSS_SPLIT_LEAK")
    return report_data


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    result=report()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,
                                     ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":result["status"],
        "signatures":{k:v["signature_set_sha256"] for k,v in result["splits"].items()},
        "updated_weights":result["training"]["actual_weight_updates"],
        "train":{k:result["train_assessment"][k] for k in ("total","eligible")},
        "validation":{k:result["validation_assessment"][k] for k in ("total","eligible")},
        "test":{k:result["test_assessment"][k] for k in ("total","eligible","primary_C_minus_B","secondary_C_minus_A")},
        "weights_sha256":result["training"]["weights_final_sha256"],
        "report_sha256":hashlib.sha256(args.output.read_bytes()).hexdigest()
    },sort_keys=True))


if __name__ == "__main__":
    main()
