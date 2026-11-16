"""Fifteen reproducible, fail-closed controls for OMEGA-CALIBRATION-06."""
from __future__ import annotations
from fractions import Fraction
from functools import cache
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import mean_calibration_lab as m
from mealy_lab import Mealy, digest


def two_state():
    return Mealy(((0,1),(1,0)),((0,0),(1,1)))


def known_identifiable_random4():
    return Mealy(
        ((0,1),(0,2),(1,0),(2,3)),
        ((0,0),(1,1),(2,2),(0,1)),
    )


def known_impossible():
    a=known_identifiable_random4()
    return Mealy(a.transitions,((0,0),)*4)


def identifiable_five(kind,seed):
    rng=random.Random(seed)
    for _ in range(100):
        x=m.b.make_machine(rng,kind)
        if m.b.fully_identifiable(x.checks(),x.size):
            return x
    raise AssertionError("NO_ADMISSIBLE_FIVE_STATE_FIXTURE")


class CalibrationControls(unittest.TestCase):

    def test_two_state_exact_mean_and_uniform_are_distinct(self):
        machine=two_state()
        oracle=m.ExactMeanAndUniform(machine.checks(),machine.size)
        full=(0,1)
        self.assertEqual(oracle.optimum(full),Fraction(1))
        # All six actions informative, two cost 1 and four cost 2.
        self.assertEqual(oracle.uniform(full),Fraction(5,3))
        self.assertEqual(oracle.actual_optimal_costs(),[1,1])

    def test_fractional_oracle_bellman_optimality_for_three_states(self):
        machine=Mealy(((0,1),(1,2),(2,0)),((0,0),(1,1),(2,2)))
        checks=machine.checks()
        oracle=m.ExactMeanAndUniform(checks,machine.size)
        @cache
        def independently_bellman(group):
            if len(group)<=1:
                return Fraction(0)
            candidates=[]
            for action in checks:
                blocks={}
                for state in group:
                    blocks.setdefault(action.values[state],[]).append(state)
                if len(blocks)<=1:
                    continue
                candidates.append(
                    Fraction(action.cost) +
                    sum(Fraction(len(part),len(group))*
                        independently_bellman(tuple(part))
                        for part in blocks.values())
                )
            return min(candidates)
        for subset in ((0,1),(0,2),(1,2),(0,1,2)):
            self.assertEqual(oracle.optimum(subset),
                             independently_bellman(subset))

    def test_old_minimax_is_distinct_and_bounded_by_exact_mean(self):
        machine=known_identifiable_random4()
        oracle=m.ExactMeanAndUniform(machine.checks(),machine.size)
        exact=m.b.solve(tuple(range(machine.size)),machine.checks())
        self.assertLessEqual(oracle.optimum(tuple(range(machine.size))),
                             exact["adaptive"])
        self.assertGreaterEqual(max(oracle.actual_optimal_costs()),
                                exact["adaptive"])

    def test_reachable_beliefs_are_unique_and_strictly_descending(self):
        machine=known_identifiable_random4()
        oracle=m.ExactMeanAndUniform(machine.checks(),4)
        states=oracle.reachable_beliefs()
        self.assertEqual(len(states),len(set(states)))
        self.assertIn((0,1,2,3),states)
        self.assertTrue(all(2<=len(s)<=4 for s in states))
        for belief in states:
            for action in oracle.actions(belief):
                subgroups=oracle.blocks(belief,action)
                self.assertEqual(sum(len(x) for x in subgroups),len(belief))
                self.assertTrue(all(len(x)<len(belief) for x in subgroups))

    def test_exact_uniform_value_uses_uniform_actions_not_optimum(self):
        machine=known_identifiable_random4()
        oracle=m.ExactMeanAndUniform(machine.checks(),4)
        full=(0,1,2,3)
        actions=oracle.actions(full)
        q=[
            Fraction(a.cost)+sum(
                Fraction(len(sub),len(full))*oracle.uniform(sub)
                for sub in oracle.blocks(full,a)
            )
            for a in actions
        ]
        self.assertEqual(oracle.uniform(full),sum(q)/len(actions))
        self.assertGreaterEqual(oracle.uniform(full),oracle.optimum(full))

    def test_impossible_machine_abstains_and_has_no_fake_calibration(self):
        impossible=known_impossible()
        self.assertFalse(m.b.fully_identifiable(impossible.checks(),4))
        source=m.b.collect([("train",known_identifiable_random4())],271)
        model=m.b.train_shared(source)
        assessment=m.evaluate_one_cohort([("bad",impossible)],model)
        self.assertEqual(assessment["eligible"],0)
        self.assertEqual(assessment["impossible"],1)
        self.assertIsNone(assessment["rows"][0]["calibration"])
        self.assertEqual(assessment["rows"][0]["decisions"],{})

    def test_training_is_original_PR132_code_without_oracle(self):
        fixture=known_identifiable_random4()
        with patch.object(m.b,"solve",side_effect=RuntimeError("ORACLE LEAK")), \
             patch.object(m,"ExactMeanAndUniform",
                          side_effect=RuntimeError("CALIBRATION LEAK")):
            rows=m.b.collect([("train",fixture)],271)
            learned=m.b.train_shared(rows)
        self.assertEqual(rows["episodes"],4)
        self.assertEqual(learned["baseline"].updates,4)
        self.assertEqual(learned["structured"].updates,4)
        self.assertEqual(len(learned["memory"]),4)

    def test_seven_feature_predictions_are_not_oracle_values(self):
        fixture=known_identifiable_random4()
        model=m.b.BeliefValue.blank()
        group=(0,1,2,3)
        value=model.predict(group,fixture.checks(),4)
        self.assertEqual(value,0.0)
        real_oracle=m.ExactMeanAndUniform(fixture.checks(),4)
        self.assertGreater(real_oracle.uniform(group),0)
        self.assertGreater(real_oracle.optimum(group),0)

    def test_train_and_holdouts_are_nonisomorphic_and_structurally_new(self):
        old=m.b.cohorts()
        new=m.new_holdouts(old)
        used=m.old_signatures(old)
        self.assertEqual(len(used),858)
        for name,seed,count,kind in m.SPLITS:
            sigs=[sig for sig,_ in new[name]["machines"]]
            self.assertEqual(len(sigs),count)
            self.assertFalse(used & set(sigs))
            self.assertEqual(len(sigs),len(set(sigs)))
            self.assertTrue(all(m.b.category(machine)==kind
                                for _,machine in new[name]["machines"]))
            used.update(sigs)
        self.assertEqual(len(used),858+sum(x[2] for x in m.SPLITS))

    def test_machine_generation_replay_by_seed(self):
        old=m.b.cohorts()
        x=m.new_holdouts(old)
        y=m.new_holdouts(old)
        for name, *_ in m.SPLITS:
            self.assertEqual(
                [s for s,_ in x[name]["machines"]],
                [s for s,_ in y[name]["machines"]]
            )

    def test_uniform_test_rollout_returns_only_real_observations(self):
        machine=identifiable_five("perm5",41)
        for hidden in range(machine.size):
            steps,total=m.uniform_episode(machine,hidden,random.Random(44321))
            self.assertEqual(total,sum(s["cost"] for s in steps))
            self.assertEqual(steps[-1]["belief_after"],[hidden])
            running=0
            for step in reversed(steps):
                running+=step["cost"]
                self.assertEqual(step["observed_return_to_go"],running)

    def test_realized_calibration_and_exact_dp_on_new_five_state_case(self):
        machine=identifiable_five("reset5",41)
        source=m.b.collect([("train",known_identifiable_random4())],271)
        trained=m.b.train_shared(source)
        before=digest(trained["structured"].weights)
        row=m.evaluate_one_cohort([("five",machine)],trained)
        self.assertEqual(row["eligible"],1)
        self.assertEqual(digest(trained["structured"].weights),before)
        c=row["rows"][0]["calibration"]
        self.assertGreater(c["reachable_nontrivial_beliefs"],0)
        self.assertEqual(len(c["heldout_real_observations"]),5)
        for item in c["per_belief"]:
            self.assertGreater(item["V_uniform_rational"]["numerator"],0)

    def test_every_policy_mean_cost_is_at_least_exact_optimum(self):
        machine=identifiable_five("perm5",81)
        source=m.b.collect([("train",known_identifiable_random4())],271)
        trained=m.b.train_shared(source)
        cohort=m.evaluate_one_cohort([("new5",machine)],trained)
        row=cohort["rows"][0]
        optimum=Fraction(
            row["oracle_exact_mean"]["numerator"],
            row["oracle_exact_mean"]["denominator"],
        )
        for arm in row["decisions"].values():
            self.assertGreaterEqual(
                Fraction(sum(arm["cost_per_hidden_initial"]),machine.size),
                optimum,
            )
            self.assertGreaterEqual(
                arm["mean_regret_to_exact"]["numerator"],0)

    def test_no_updates_on_reserved_evaluation(self):
        source=m.b.collect([("train",known_identifiable_random4())],272)
        trained=m.b.train_shared(source)
        before=(digest(trained["baseline"].weights),
                digest(trained["structured"].weights),
                digest(trained["memory"]))
        m.evaluate_one_cohort(
            [("holdout",identifiable_five("reset5",61))],trained
        )
        after=(digest(trained["baseline"].weights),
               digest(trained["structured"].weights),
               digest(trained["memory"]))
        self.assertEqual(before,after)

    def test_full_preregistered_trial_and_negative_outcome_preservation(self):
        r=m.conduct()
        self.assertEqual(r["prereg_commit"],m.PREREG)
        self.assertEqual(r["experiment"],m.EXPERIMENT)
        self.assertEqual(r["training_seeds"],[271,272,273])
        self.assertEqual(len(r["repetitions"]),3)
        self.assertFalse(r["oracle_used_for_training"])
        self.assertTrue(r["exact_mean_oracle_rational"])
        self.assertTrue(r["uniform_policy_calibration_oracle_rational"])
        self.assertFalse(r["model_updated_during_evaluation"])
        self.assertFalse(r["scientific_generalization_proven"])
        self.assertEqual(r["paid_api_calls"],0)
        self.assertFalse(r["main_modified"])
        self.assertIn(r["status"],{
            "DESCRIPTIVE_CALIBRATED_MEAN_GAIN",
            "NO_CALIBRATED_MEAN_GAIN",
            "INSUFFICIENT_IDENTIFIABLE_CASES",
        })
        for rep in r["repetitions"]:
            self.assertEqual(rep["training_weights_sha"],
                             rep["evaluation_weights_sha"])
            for name,_,n,_ in m.SPLITS:
                ev=rep["evaluations"][name]
                self.assertEqual(ev["total"],n)
                self.assertEqual(ev["eligible"]+ev["impossible"],n)


if __name__=="__main__":
    unittest.main()
