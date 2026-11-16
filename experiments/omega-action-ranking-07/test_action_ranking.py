"""15 scientific regression controls for OMEGA-ACTION-RANKING-07."""
from __future__ import annotations
from fractions import Fraction
from hashlib import sha256
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import action_ranking_lab as r
from mealy_lab import Mealy,digest


def simple():
    return Mealy(((0,1),(0,2),(1,0),(2,3)),((0,0),(1,1),(2,2),(0,1)))


def indistinguishable():
    x=simple()
    return Mealy(x.transitions,((0,0),)*x.size)


def trained_fixture():
    shared=r.b.collect([("fixture",simple())],271)
    return r.b.train_shared(shared)


class RankingChecks(unittest.TestCase):

    def test_oracles_are_distinct_and_fraction_exact(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        root=tuple(range(machine.size))
        self.assertIsInstance(oracle.optimum(root),Fraction)
        self.assertIsInstance(oracle.uniform(root),Fraction)
        self.assertGreaterEqual(oracle.uniform(root),oracle.optimum(root))

    def test_bellman_qstar_min_equals_exact_optimum_on_reachable_beliefs(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        for group in oracle.reachable_beliefs():
            values=r.q_tables(group,oracle,r.b.BeliefValue.blank())
            self.assertEqual(min(x["Q_exact_mean"] for x in values.values()),
                             oracle.optimum(group))
            for v in values.values():
                self.assertEqual(
                    v["Q_exact_mean"],
                    Fraction(v["action"].cost)+sum(
                        Fraction(len(sub),len(group))*oracle.optimum(sub)
                        for sub in v["successors"]
                    ),
                )

    def test_quniform_uses_uniform_continuation_not_optimal(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        for group in oracle.reachable_beliefs():
            values=r.q_tables(group,oracle,r.b.BeliefValue.blank())
            self.assertEqual(
                sum(v["Q_exact_uniform_continuation"] for v in values.values())/
                len(values),
                oracle.uniform(group),
            )

    def test_rank_actions_matches_old_PR132_policy(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        policy=trained_fixture()["structured"]
        for group in oracle.reachable_beliefs():
            chosen=r.b.value_action(group,machine.checks(),policy)
            diagnostic=r.rank_belief(group,oracle,policy)
            self.assertEqual(diagnostic["learned_action"],chosen.name)
            self.assertEqual(len(diagnostic["actions"]),
                             diagnostic["candidate_count"])

    def test_local_regret_is_exact_fraction_and_nonnegative(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        policy=trained_fixture()["structured"]
        for group in oracle.reachable_beliefs():
            diag=r.rank_belief(group,oracle,policy)
            a=diag["learned_local_one_step_regret_rational"]
            value=Fraction(a["numerator"],a["denominator"])
            self.assertGreaterEqual(value,0)
            self.assertEqual(diag["learned_suboptimal"],value>0)

    def test_equal_qstar_actions_are_not_counted_as_error(self):
        machine=Mealy(((0,1),(1,0)),((0,0),(1,1)))
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        record=r.rank_belief((0,1),oracle,r.b.BeliefValue.blank())
        self.assertFalse(record["learned_suboptimal"])
        self.assertEqual(record["oracle_tie_count"],2)
        self.assertEqual(record["strict_best_vs_next_margin_rational"]["numerator"],1)

    def test_rank_comparisons_come_from_only_known_table_and_weights(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        q=r.q_tables((0,1,2,3),oracle,r.b.BeliefValue.blank())
        for value in q.values():
            self.assertEqual(value["Q_predicted_continuation"],
                             value["action"].cost)
            self.assertGreaterEqual(value["Q_exact_mean"],
                                    Fraction(value["action"].cost))
            self.assertTrue(value["successors"])

    def test_perfect_uniform_policy_runs_without_false_identification(self):
        machine=simple()
        oracle=r.m.ExactMeanAndUniform(machine.checks(),machine.size)
        costs=[]
        for hidden in range(machine.size):
            cost,words=r.replay_uniform_exact(machine,oracle,hidden)
            self.assertGreater(cost,0)
            self.assertTrue(words)
            costs.append(cost)
        self.assertGreaterEqual(Fraction(sum(costs),machine.size),
                                oracle.optimum(tuple(range(machine.size))))

    def test_training_does_not_call_either_oracle(self):
        with patch.object(r.m,"ExactMeanAndUniform",
                          side_effect=RuntimeError("FORBIDDEN_TRAIN_ORACLE")), \
             patch.object(r.b,"solve",
                          side_effect=RuntimeError("FORBIDDEN_MINIMAX_TRAIN")):
            raw=r.b.collect([("fixture",simple())],271)
            model=r.b.train_shared(raw)
        self.assertEqual(model["baseline"].updates,raw["episodes"])
        self.assertEqual(model["structured"].updates,raw["episodes"])

    def test_justified_abstention_has_no_fabricated_regret(self):
        machine=indistinguishable()
        self.assertFalse(r.b.fully_identifiable(machine.checks(),machine.size))
        row=r.evaluate_machine("not-id",machine,trained_fixture())
        self.assertFalse(row["identifiable"])
        self.assertEqual(row["reachable_beliefs"],[])
        self.assertEqual(row["policy_scores"],{})

    def test_replay_means_all_bounded_by_optimum(self):
        machine=simple()
        outcome=r.evaluate_machine("fixture",machine,trained_fixture())
        self.assertTrue(outcome["identifiable"])
        for name,policy in outcome["policy_scores"].items():
            self.assertGreaterEqual(
                policy["regret_to_exact_mean_rational"]["numerator"],0)
            self.assertEqual(len(policy["cost_by_initial"]),machine.size)
            self.assertGreaterEqual(policy["worst_regret_minimax"],0)
        self.assertEqual(
            outcome["policy_scores"]["MEAN_EXACT"]["regret_to_exact_mean_rational"]["numerator"],0)

    def test_all_new_holdout_signatures_disjoint_from_all_prior_seven_pilots(self):
        old,new=r.new_cohorts()
        seen=r.m.old_signatures(old)
        for row in r.m.new_holdouts(old).values():
            seen.update(sig for sig,_ in row["machines"])
        self.assertEqual(len(seen),942)
        for name,seed,count,kind in r.SPLITS:
            sigs=[sig for sig,_ in new[name]["machines"]]
            self.assertEqual(len(sigs),count)
            self.assertEqual(new[name]["family"],kind)
            self.assertTrue(all(r.b.category(machine)==kind
                                for _,machine in new[name]["machines"]))
            self.assertFalse(seen.intersection(sigs))
            seen.update(sigs)
        self.assertEqual(len(seen),942+sum(row[2] for row in r.SPLITS))

    def test_seeded_canonical_machine_generator_replays_exactly(self):
        _,first=r.new_cohorts()
        _,second=r.new_cohorts()
        for name,*_ in r.SPLITS:
            self.assertEqual(
                [sig for sig,_ in first[name]["machines"]],
                [sig for sig,_ in second[name]["machines"]],
            )

    def test_cross_tab_accounting_conserves_all_beliefs(self):
        machine=simple()
        record=r.evaluate_machine("fixture",machine,trained_fixture())
        summary=r.summarize_rows([record])
        matrix=summary["surrogate_x_approximation_matrix"]
        self.assertEqual(
            sum(row["beliefs"] for row in matrix.values()),
            summary["reachable_nontrivial_beliefs"],
        )
        self.assertEqual(
            sum(row["learned_suboptimal_count"] for row in matrix.values()),
            summary["learned_suboptimal_beliefs"],
        )
        self.assertTrue(all(v["count"]>0 for v in summary["by_belief_size"].values()))

    def test_full_trial_respects_frozen_models_and_negative_status(self):
        result=r.conduct()
        self.assertEqual(result["experiment"],r.EXPERIMENT)
        self.assertEqual(result["prereg_commit"],r.PREREG)
        self.assertEqual(result["training_seeds"],[271,272,273])
        self.assertEqual(len(result["repetitions"]),3)
        self.assertFalse(result["main_modified"])
        self.assertFalse(result["language_model_trained"])
        self.assertTrue(result["all_oracles_evaluation_only"])
        self.assertTrue(result["evaluation_weights_unchanged"])
        self.assertIn(result["status"],{
            "TARGET_MISMATCH_OBSERVED_BOTH",
            "TARGET_MISMATCH_OBSERVED_ONE",
            "TARGET_MISMATCH_NOT_OBSERVED",
            "INSUFFICIENT_IDENTIFIABLE_CASES",
        })
        for rep in result["repetitions"]:
            self.assertEqual(rep["training_fingerprints_before"],
                             rep["training_fingerprints_after"])
            for name,seed,count,kind in r.SPLITS:
                ev=rep["evaluations"][name]
                self.assertEqual(ev["summary"]["total"],count)
                self.assertEqual(ev["summary"]["eligible"]+
                                 ev["summary"]["impossible"],count)


if __name__=="__main__":
    unittest.main()
