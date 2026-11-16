"""OMEGA-ONPOLICY-CONTINUATION-08: real own-decision returns, new held-out systems.

Known Mealy machine, hidden initial state. Reuses unmodified PR132 value
regression, PR133 exact Fraction oracle and PR134 exact Q ranking.
Training never calls an oracle or uses labels for unchosen actions.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "omega-action-ranking-07"))
import action_ranking_lab as ranking  # noqa: E402
from mealy_lab import digest  # noqa: E402

b = ranking.b
m = ranking.m
EXPERIMENT = "OMEGA-ONPOLICY-CONTINUATION-08"
PREREG = "2fee9541c64ad379060f1a27fceaf8c0e8d87b3a"
EPSILON = 0.20
SEEDS = (361, 362, 363)
SPLITS = (
    ("eval_random4", 25117, 26, "random4"),
    ("eval_perm5", 25118, 30, "perm5"),
    ("eval_reset5", 25119, 30, "reset5"),
)
RESERVED = ("eval_perm5", "eval_reset5")
TOL = 1e-10
POLICIES = (
    "MEAN_EXACT", "UNIFORM_EXACT_GREEDY",
    "FIXED", "MEMORY", "TOTAL9", "UNIFORM_VALUE", "SELF_VALUE",
)


def make_holdouts(old_cohorts=None):
    """Disallow all 1,026 previous canonical signatures and new overlaps."""
    if old_cohorts is None:
        old_cohorts = b.cohorts()
    used = set(m.old_signatures(old_cohorts))
    for part in m.new_holdouts(old_cohorts).values():
        used.update(sig for sig, _ in part["machines"])
    _, prior_07 = ranking.new_cohorts()
    for part in prior_07.values():
        used.update(sig for sig, _ in part["machines"])
    if len(used) != 1026:
        raise AssertionError("HISTORICAL_COHORT_RECONCILIATION_FAILED")
    result = {}
    for name, seed, count, kind in SPLITS:
        rng = random.Random(seed)
        draws = duplicates = 0
        selected = []
        while len(selected) < count:
            draws += 1
            if draws > 100000:
                raise RuntimeError("UNIQUE_MACHINE_EXHAUSTION")
            machine = b.make_machine(rng, kind)
            if b.category(machine) != kind:
                raise AssertionError("WRONG_STRUCTURAL_FAMILY")
            sig = machine.signature()
            if sig in used:
                duplicates += 1
                continue
            used.add(sig)
            selected.append((sig, machine))
        result[name] = dict(
            seed=seed, family=kind, size=len(selected),
            draws=draws, isomorphic_collisions=duplicates, machines=selected,
        )
    if len(used) != 1026 + sum(x[2] for x in SPLITS):
        raise AssertionError("DUPLICATED_NEW_MACHINE")
    return result


def choose_behavior(belief, checks, model, rng):
    """Only current known machine partitions, value weights and RNG."""
    actions = b.choices(belief, checks)
    if not actions:
        return None, False
    if rng.random() < EPSILON:
        return rng.choice(actions), True
    return b.value_action(belief, checks, model), False


def simulate_own_episode(machine, hidden, model, rng):
    """World alone uses hidden index, never the policy selector.

    Weights remain constant throughout the whole episode. The only update is
    performed by the caller AFTER identification and actual cost observation.
    """
    checks = machine.checks()
    if not b.fully_identifiable(checks, machine.size):
        raise ValueError("TRAINING_MACHINE_NOT_IDENTIFIABLE")
    group = tuple(range(machine.size))
    steps = []
    total = 0
    while len(group) > 1:
        action, exploratory = choose_behavior(group, checks, model, rng)
        if action is None:
            raise AssertionError("NO_INFORMATIVE_ACTION")
        previous = group
        observed = action.values[hidden]
        group = tuple(s for s in group if action.values[s] == observed)
        if not group or len(group) >= len(previous):
            raise AssertionError("BAD_STATE_FILTER")
        total += action.cost
        steps.append(dict(
            probe=action.name, cost=action.cost,
            exploratory=exploratory,
            observed_outputs=list(observed),
            belief_before=list(previous), belief_after=list(group),
        ))
    if group != (hidden,):
        raise AssertionError("INCORRECT_STATE_IDENTIFICATION")
    if not steps or total != sum(z["cost"] for z in steps):
        raise AssertionError("INVALID_OBSERVED_COST")
    first = steps[0]
    remainder = total - first["cost"]
    if remainder < 0:
        raise AssertionError("NEGATIVE_TRUE_REMAINDER")
    return dict(
        cost_total=total, first_probe=first["probe"],
        first_cost=first["cost"], first_observation=first["observed_outputs"],
        successor_belief=first["belief_after"],
        observed_continuation_cost=remainder,
        trajectory=steps,
    )


def train_self(machines, seed):
    """True own-policy sample, ONE real continuation update per episode."""
    rng = random.Random(seed + 40000)
    model = b.BeliefValue.blank()
    records = []
    impossible = []
    probe_cost = probe_count = explores = useful_features = 0
    for sig, machine in machines:
        if b.category(machine) != "random4":
            raise AssertionError("TRAIN_CLASS_MISMATCH")
        checks = machine.checks()
        if not b.fully_identifiable(checks, machine.size):
            impossible.append(sig)
            continue
        for hidden in range(machine.size):
            current_weights = digest(model.weights)
            episode = simulate_own_episode(machine, hidden, model, rng)
            posterior = tuple(episode["successor_belief"])
            vec = b.successor_features(posterior, checks, machine.size)
            if any(x != 0 for x in vec):
                useful_features += 1
            model.learn_one(vec, episode["observed_continuation_cost"])
            probe_cost += episode["cost_total"]
            probe_count += len(episode["trajectory"])
            explores += sum(x["exploratory"] for x in episode["trajectory"])
            records.append(dict(
                machine_signature=sig,
                hidden_for_audit_only=hidden,
                model_weights_before_episode=current_weights,
                model_weights_after_episode=digest(model.weights),
                feature_vector=list(vec),
                first_probe=episode["first_probe"],
                first_observation=episode["first_observation"],
                first_cost=episode["first_cost"],
                successor_belief=episode["successor_belief"],
                actual_continuation_cost=episode["observed_continuation_cost"],
                total_cost=episode["cost_total"],
                trajectory=episode["trajectory"],
            ))
    if not records or len(records) != model.updates:
        raise AssertionError("MODEL_UPDATE_COUNT_INCONSISTENT")
    if probe_cost != sum(row["total_cost"] for row in records):
        raise AssertionError("UNACCOUNTED_PROBE_COST")
    return dict(
        model=model, impossible=impossible,
        episodes=len(records), observed_labels=len(records),
        informative_successor_labels=useful_features,
        cost_spent=probe_cost, probes_executed=probe_count,
        exploration_actions=explores,
        records=records,
        records_sha256=digest(records),
        weights_sha256=digest(model.weights),
    )


def action_diagnostics(machine, oracle, uniform, own):
    """All reachable beliefs, exact local regret Q*(action)-V*(belief)."""
    complete = []
    for group in oracle.reachable_beliefs():
        row = {"belief":list(group), "size":len(group)}
        optimal = oracle.optimum(group)
        for name, model in (("UNIFORM_VALUE", uniform), ("SELF_VALUE", own)):
            action = b.value_action(group, oracle.checks, model)
            q = oracle.opt_q(group, action)
            regret = q - optimal
            if regret < 0:
                raise AssertionError("LOCALLY_BEATS_EXACT_MEAN")
            row[name] = dict(
                probe=action.name, local_regret=m.fr(regret),
                under_optimality=bool(regret > 0),
            )
        complete.append(row)
    return complete


def evaluate_machine(signature, machine, models):
    """Only this routine uses rational exact and minimax oracles."""
    checks = machine.checks()
    eligible = b.fully_identifiable(checks, machine.size)
    row = dict(signature=signature, states=machine.size,
               identifiable=eligible, policies={}, beliefs=[])
    if not eligible:
        row["status"] = "ABSTENTION_JUSTIFIEE"
        return row
    oracle = m.ExactMeanAndUniform(checks, machine.size)
    initial = tuple(range(machine.size))
    optimum = oracle.optimum(initial)
    old_minimax = b.solve(initial, checks)["adaptive"]
    if old_minimax is None:
        raise AssertionError("EXACT_MINIMAX_MISSING")
    value_uniform = models["UNIFORM_VALUE"]
    value_self = models["SELF_VALUE"]
    row["beliefs"] = action_diagnostics(machine, oracle, value_uniform, value_self)
    replay = {
        "MEAN_EXACT": oracle.actual_optimal_costs(),
        "UNIFORM_EXACT_GREEDY": [
            ranking.replay_uniform_exact(machine, oracle, hidden)[0]
            for hidden in range(machine.size)
        ],
        "UNIFORM_VALUE": [
            b.run_value_episode(machine, hidden, value_uniform)["cost"]
            for hidden in range(machine.size)
        ],
        "SELF_VALUE": [
            b.run_value_episode(machine, hidden, value_self)["cost"]
            for hidden in range(machine.size)
        ],
    }
    for label, arm in (
        ("FIXED","fixed"),("MEMORY","memory"),("TOTAL9","learned")
    ):
        replay[label] = [
            b.run_episode(
                machine, checks, hidden, arm,
                weights=models["TOTAL9"].weights,
                memory=models["MEMORY"],
                log=False,
            )["total_cost"]
            for hidden in range(machine.size)
        ]
    for label, costs in replay.items():
        if len(costs) != machine.size:
            raise AssertionError("MISSING_INITIAL_STATE")
        value = Fraction(sum(costs), machine.size)
        regret = value - optimum
        if regret < 0:
            raise AssertionError("POLICY_BEATS_EXACT_MEAN")
        worst = max(costs)
        if worst < old_minimax:
            raise AssertionError("POLICY_BEATS_EXACT_MINIMAX")
        row["policies"][label] = dict(
            cost_by_state=costs, mean_cost=m.fr(value),
            exact_mean_regret=m.fr(regret),
            worst_cost=worst, worst_minimax_regret=worst-old_minimax,
        )
    row["exact_optimum"] = m.fr(optimum)
    row["old_minimax_worst"] = old_minimax
    return row


def summarize(rows):
    valid = [r for r in rows if r["identifiable"]]
    basic = dict(total=len(rows), eligible=len(valid),
                 impossible=len(rows)-len(valid))
    if not valid:
        return basic
    beliefs = [x for item in valid for x in item["beliefs"]]
    n = len(beliefs)
    basic.update(
        beliefs=n,
        local_underopt_count={
            arm:sum(z[arm]["under_optimality"] for z in beliefs)
            for arm in ("UNIFORM_VALUE","SELF_VALUE")
        },
        local_underopt_rate={
            arm:sum(z[arm]["under_optimality"] for z in beliefs)/n
            for arm in ("UNIFORM_VALUE","SELF_VALUE")
        },
        mean_local_regret={
            arm:sum(z[arm]["local_regret"]["decimal"] for z in beliefs)/n
            for arm in ("UNIFORM_VALUE","SELF_VALUE")
        },
        mean_cost={
            arm:sum(x["policies"][arm]["mean_cost"]["decimal"] for x in valid)
                /len(valid)
            for arm in POLICIES
        },
        mean_regret={
            arm:sum(x["policies"][arm]["exact_mean_regret"]["decimal"]
                    for x in valid)/len(valid)
            for arm in POLICIES
        },
    )
    return basic


def aggregate(reps, name):
    sub = [r["evaluations"][name]["summary"] for r in reps]
    if len(set((x["total"],x["eligible"]) for x in sub)) != 1:
        raise AssertionError("COHORT_DRIFT")
    first = sub[0]
    if not first["eligible"]:
        return dict(total=first["total"],eligible=0,
                    impossible=first["impossible"])
    n = sum(x["beliefs"] for x in sub)
    return dict(
        total=first["total"],eligible=first["eligible"],
        impossible=first["impossible"],
        beliefs_including_seed_repeats=n,
        unique_beliefs_per_cohort=first["beliefs"],
        mean_cost={
            arm:sum(s["mean_cost"][arm] for s in sub)/len(sub)
            for arm in POLICIES
        },
        mean_regret={
            arm:sum(s["mean_regret"][arm] for s in sub)/len(sub)
            for arm in POLICIES
        },
        local_underopt_rate={
            arm:sum(s["local_underopt_count"][arm] for s in sub)/n
            for arm in ("UNIFORM_VALUE","SELF_VALUE")
        },
        mean_local_regret={
            arm:sum(s["mean_local_regret"][arm] for s in sub)/len(sub)
            for arm in ("UNIFORM_VALUE","SELF_VALUE")
        },
    )


def conduct():
    old = b.cohorts()
    cohorts = make_holdouts(old)
    reps = []
    for seed in SEEDS:
        # Frozen PR132 uniform data collector and exact same train instances.
        uniform_stream = b.collect(old["train_random4"]["machines"], seed)
        uniform_training = b.train_shared(uniform_stream)
        own_training = train_self(old["train_random4"]["machines"], seed)
        if not (uniform_stream["episodes"] == own_training["episodes"] ==
                uniform_training["structured"].updates ==
                own_training["model"].updates):
            raise AssertionError("UNMATCHED_EPISODES_AND_UPDATES")
        if uniform_stream["impossible"] != own_training["impossible"]:
            raise AssertionError("DIFFERENT_TRAIN_COHORT_FILTERS")
        models = {
            "UNIFORM_VALUE":uniform_training["structured"],
            "SELF_VALUE":own_training["model"],
            "MEMORY":uniform_training["memory"],
            "TOTAL9":uniform_training["baseline"],
        }
        fingerprints = {
            x:digest(y.weights) for x,y in models.items()
            if x != "MEMORY"
        }
        fingerprints["MEMORY"] = digest(models["MEMORY"])
        evaluations = {}
        for name,*_ in SPLITS:
            rows = [
                evaluate_machine(sig, machine, models)
                for sig, machine in cohorts[name]["machines"]
            ]
            evaluations[name] = dict(summary=summarize(rows),rows=rows)
        after = {
            x:digest(y.weights) for x,y in models.items()
            if x != "MEMORY"
        }
        after["MEMORY"] = digest(models["MEMORY"])
        if fingerprints != after:
            raise AssertionError("TEST_LEAKED_INTO_TRAINED_PARAMETERS")
        reps.append(dict(
            seed=seed,
            training_uniform=dict(
                episodes=uniform_stream["episodes"],
                cost_spent=uniform_stream["real_probe_cost"],
                probes_executed=uniform_stream["real_probe_count"],
                observations_sha256=uniform_training["audit_sha256"],
                informative_successor_labels=sum(
                    any(b.successor_features(
                        record["after"],record["machine"].checks(),
                        record["machine"].size
                    )) for record in uniform_stream["records"]
                ),
            ),
            training_self={k:v for k,v in own_training.items() if k!="model"},
            model_sha_before=fingerprints,model_sha_after=after,
            model_weights={
                "UNIFORM_VALUE":list(models["UNIFORM_VALUE"].weights),
                "SELF_VALUE":list(models["SELF_VALUE"].weights),
                "TOTAL9":list(models["TOTAL9"].weights),
            },
            evaluations=evaluations,
        ))
    summaries={name:aggregate(reps,name) for name,*_ in SPLITS}
    if any(summaries[name]["eligible"] == 0 for name in RESERVED):
        status="INSUFFICIENT_IDENTIFIABLE_CASES"
        passes=0
    else:
        passes=sum(
            all(summaries[name]["mean_cost"]["SELF_VALUE"] <
                summaries[name]["mean_cost"][comp]-TOL
                for comp in ("UNIFORM_VALUE","FIXED","MEMORY"))
            for name in RESERVED
        )
        status=("DESCRIPTIVE_SELF_CONTINUATION_ADVANTAGE"
                if passes==2 else "NO_SELF_CONTINUATION_ADVANTAGE")
    manifest={
        name:dict(
            seed=entry["seed"],kind=entry["family"],size=entry["size"],
            draws=entry["draws"],
            isomorphic_collisions=entry["isomorphic_collisions"],
            signatures=[sig for sig,_ in entry["machines"]],
            signatures_sha256=digest([sig for sig,_ in entry["machines"]]),
        ) for name,entry in cohorts.items()
    }
    report=dict(
        experiment=EXPERIMENT,prereg_commit=PREREG,
        status=status,strong_families_passed=passes,
        training_seed_list=list(SEEDS),epsilon=EPSILON,
        learner_architecture="unchanged_PR132_7_parameter_BeliefValue",
        same_training_cases_and_label_count=True,
        equal_train_cost_claim=False,
        no_oracle_training=True,
        exact_mean_oracle_evaluation_only=True,
        model_unchanged_during_evaluation=True,
        main_modified=False,language_model_trained=False,
        paid_api_calls=0,scientific_generalization_proven=False,
        splits=manifest,repetitions=reps,aggregate=summaries,
        limitations=[
            "Known transition/output model, hidden initial state only.",
            "Training and evaluation are on four/five-state six-probe resettable systems.",
            "ON uses epsilon=0.2 during training and greedy epsilon=0 in evaluation.",
            "ON versus uniform changes trajectory distribution, not a single isolated mechanism.",
            "Equal number of episodes and labels, unequal information content and actual probe costs.",
            "Some training posteriors are singleton: zero features imply no weight effect.",
            "Three training seeds share heldout machines; not independent replications.",
            "Exact mean oracle is evaluation only and not an optimal-action teacher.",
            "This is not language model training or autonomous code modification.",
        ],
    )
    if any(
        x["training_uniform"]["episodes"] != x["training_self"]["episodes"]
        for x in reps
    ):
        raise AssertionError("UNEQUAL_TRAINING_EPISODE_COUNT")
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",required=True,type=Path)
    args=parser.parse_args()
    report=conduct()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(report,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()
    args.output.write_bytes(raw)
    print(json.dumps(dict(
        experiment=EXPERIMENT,status=report["status"],
        strong_families_passed=report["strong_families_passed"],
        summary={
            name:dict(
                identifiable=entry["eligible"],
                mean_cost=entry.get("mean_cost"),
                local_underopt_rate=entry.get("local_underopt_rate"),
            ) for name,entry in report["aggregate"].items()
        },
        train={
            x["seed"]:dict(
                episodes=x["training_self"]["episodes"],
                uniform_cost=x["training_uniform"]["cost_spent"],
                self_cost=x["training_self"]["cost_spent"],
                nonzero_labels_uniform=x["training_uniform"]["informative_successor_labels"],
                nonzero_labels_self=x["training_self"]["informative_successor_labels"],
            ) for x in report["repetitions"]
        },
        report_sha256=sha256(raw).hexdigest()
    ),sort_keys=True))


if __name__=="__main__":
    main()
