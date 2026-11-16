"""Sixteen rigorous regression checks for OMEGA-ONPOLICY-CONTINUATION-08."""
from __future__ import annotations

from fractions import Fraction
import inspect
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import onpolicy_lab as o
from mealy_lab import Mealy,digest


def known4():
    return Mealy(
        ((0,1),(0,2),(1,0),(2,3)),
        ((0,0),(1,1),(2,2),(0,1)),
    )


def impossible4():
    x=known4()
    return Mealy(x.transitions,((0,0),)*4)


class OnPolicyTests(unittest.TestCase):

    def test_frozen_historical_1026_signatures_and_new_no_overlap(self):
        old=o.b.cohorts()
        fresh=o.make_holdouts(old)
        used=o.m.old_signatures(old)
        for group in o.m.new_holdouts(old).values():
            used.update(sig for sig,_ in group["machines"])
        _,pilot07=o.ranking.new_cohorts()
        for group in pilot07.values():
            used.update(sig for sig,_ in group["machines"])
        self.assertEqual(len(used),1026)
        for name,seed,count,family in o.SPLITS:
            sigs=[sig for sig,_ in fresh[name]["machines"]]
            self.assertEqual(len(sigs),count)
            self.assertFalse(set(sigs)&used)
            self.assertEqual(len(set(sigs)),count)
            used.update(sigs)
        self.assertEqual(len(used),1026+sum(x[2] for x in o.SPLITS))

    def test_three_new_structure_families_and_state_counts(self):
        groups=o.make_holdouts()
        for name,seed,count,kind in o.SPLITS:
            n=4 if kind=="random4" else 5
            self.assertTrue(all(
                model.size==n and o.b.category(model)==kind
                for _,model in groups[name]["machines"]
            ))

    def test_seeded_holdout_replay_signatures_identical(self):
        first=o.make_holdouts()
        second=o.make_holdouts()
        for name,*_ in o.SPLITS:
            self.assertEqual(
                [s for s,_ in first[name]["machines"]],
                [s for s,_ in second[name]["machines"]],
            )

    def test_selector_never_accepts_hidden_state(self):
        self.assertEqual(
            list(inspect.signature(o.choose_behavior).parameters),
            ["belief","checks","model","rng"],
        )
        self.assertNotIn("hidden",str(inspect.signature(o.choose_behavior)))

    def test_explicit_epsilon_exploration_and_greedy_selection(self):
        machine=known4()
        group=tuple(range(4))
        checks=machine.checks()
        model=o.b.BeliefValue.blank()
        rng=random.Random(17)
        with patch.object(rng,"random",return_value=0.01):
            chosen,explore=o.choose_behavior(group,checks,model,rng)
        self.assertTrue(explore)
        self.assertIn(chosen,o.b.choices(group,checks))
        with patch.object(rng,"random",return_value=0.91):
            action,explore=o.choose_behavior(group,checks,model,rng)
        self.assertFalse(explore)
        self.assertEqual(action.name,o.b.value_action(group,checks,model).name)

    def test_world_responds_correctly_without_false_identification(self):
        machine=known4()
        model=o.b.BeliefValue.blank()
        for hidden in range(machine.size):
            ep=o.simulate_own_episode(machine,hidden,model,random.Random(123))
            self.assertEqual(ep["cost_total"],
                sum(s["cost"] for s in ep["trajectory"]))
            self.assertEqual(ep["trajectory"][-1]["belief_after"],[hidden])
            self.assertEqual(ep["cost_total"],
                ep["first_cost"]+ep["observed_continuation_cost"])
            for s in ep["trajectory"]:
                self.assertEqual(tuple(s["observed_outputs"]),
                    next(c for c in machine.checks()
                         if c.name==s["probe"]).values[hidden])

    def test_exactly_one_update_per_own_episode(self):
        row=o.train_self([("fixture",known4())],361)
        self.assertEqual(row["episodes"],4)
        self.assertEqual(row["observed_labels"],4)
        self.assertEqual(row["model"].updates,4)
        self.assertEqual(len(row["records"]),4)
        self.assertEqual(row["cost_spent"],
                         sum(x["total_cost"] for x in row["records"]))

    def test_real_suffix_label_and_posterior_features_only(self):
        trained=o.train_self([("fixture",known4())],362)
        for item in trained["records"]:
            self.assertEqual(
                item["total_cost"],
                item["first_cost"]+item["actual_continuation_cost"],
            )
            checks=known4().checks()
            expected=o.b.successor_features(
                item["successor_belief"],checks,4
            )
            self.assertEqual(item["feature_vector"],list(expected))
            self.assertEqual(item["first_observation"],
                             item["trajectory"][0]["observed_outputs"])
            self.assertGreaterEqual(item["actual_continuation_cost"],0)

    def test_model_weights_are_frozen_during_full_episode(self):
        model=o.b.BeliefValue.blank()
        machine=known4()
        hashes=[]
        original=o.choose_behavior
        def wrap(group,checks,current_model,rng):
            hashes.append(digest(current_model.weights))
            return original(group,checks,current_model,rng)
        with patch.object(o,"choose_behavior",side_effect=wrap):
            o.simulate_own_episode(machine,2,model,random.Random(3))
        self.assertTrue(hashes)
        self.assertEqual(len(set(hashes)),1)
        self.assertEqual(model.updates,0)

    def test_no_mean_or_minimax_oracle_during_own_training(self):
        with patch.object(o.m,"ExactMeanAndUniform",
                          side_effect=RuntimeError("ORACLE LEAK")),\
             patch.object(o.b,"solve",side_effect=RuntimeError("MINIMAX LEAK")):
            t=o.train_self([("fixture",known4())],361)
            uniform=o.b.collect([("fixture",known4())],361)
            ref=o.b.train_shared(uniform)
        self.assertEqual(t["model"].updates,4)
        self.assertEqual(ref["structured"].updates,4)

    def test_nonidentifiable_cases_not_silently_replaced(self):
        cohort=[("bad",impossible4()),("good",known4())]
        t=o.train_self(cohort,362)
        self.assertEqual(t["impossible"],["bad"])
        self.assertEqual(t["episodes"],4)
        models={
            "UNIFORM_VALUE":o.b.BeliefValue.blank(),
            "SELF_VALUE":t["model"],
            "TOTAL9":o.b.LinearPolicy.blank(),
            "MEMORY":[{"features":list(o.b.features((0,1),known4().checks()[0])),
                       "observed_return_to_go":1}],
        }
        row=o.evaluate_machine("bad",impossible4(),models)
        self.assertFalse(row["identifiable"])
        self.assertEqual(row["policies"],{})
        self.assertEqual(row["beliefs"],[])

    def test_off_and_on_count_equal_on_same_machine_and_hidden_starts(self):
        fixture=[("fixture",known4())]
        uniform=o.b.collect(fixture,361)
        own=o.train_self(fixture,361)
        self.assertEqual(uniform["episodes"],own["episodes"])
        self.assertEqual(uniform["episodes"],4)
        self.assertEqual([x["hidden_for_audit_only"]
                          for x in own["records"]],[0,1,2,3])

    def test_exact_mean_regrets_and_local_action_costs_nonnegative(self):
        machine=known4()
        uniform=o.b.collect([("fixture",machine)],361)
        trained=o.b.train_shared(uniform)
        own=o.train_self([("fixture",machine)],361)
        models={
            "UNIFORM_VALUE":trained["structured"],
            "SELF_VALUE":own["model"],
            "TOTAL9":trained["baseline"],
            "MEMORY":trained["memory"],
        }
        row=o.evaluate_machine("fixture",machine,models)
        self.assertTrue(row["identifiable"])
        opt=Fraction(row["exact_optimum"]["numerator"],
                     row["exact_optimum"]["denominator"])
        for arm,v in row["policies"].items():
            mean=Fraction(sum(v["cost_by_state"]),machine.size)
            self.assertGreaterEqual(mean,opt)
            self.assertGreaterEqual(v["worst_minimax_regret"],0)
        for group in row["beliefs"]:
            for name in ("UNIFORM_VALUE","SELF_VALUE"):
                self.assertGreaterEqual(
                    group[name]["local_regret"]["numerator"],0)

    def test_evaluate_never_changes_trained_models(self):
        machine=known4()
        shared=o.b.collect([("fixture",machine)],363)
        uniform=o.b.train_shared(shared)
        own=o.train_self([("fixture",machine)],363)
        models={
            "UNIFORM_VALUE":uniform["structured"],
            "SELF_VALUE":own["model"],
            "TOTAL9":uniform["baseline"],
            "MEMORY":uniform["memory"],
        }
        before=[digest(models[a].weights) for a in ("UNIFORM_VALUE","SELF_VALUE","TOTAL9")]
        o.evaluate_machine("fixture",machine,models)
        after=[digest(models[a].weights) for a in ("UNIFORM_VALUE","SELF_VALUE","TOTAL9")]
        self.assertEqual(before,after)

    def test_deterministic_own_training_and_observed_record_hash(self):
        one=o.train_self([("fixture",known4())],361)
        two=o.train_self([("fixture",known4())],361)
        self.assertEqual(one["records_sha256"],two["records_sha256"])
        self.assertEqual(one["weights_sha256"],two["weights_sha256"])
        self.assertEqual(one["exploration_actions"],two["exploration_actions"])

    def test_complete_fixed_protocol_and_negative_results_unchanged(self):
        r=o.conduct()
        self.assertEqual(r["experiment"],o.EXPERIMENT)
        self.assertEqual(r["prereg_commit"],o.PREREG)
        self.assertEqual(r["training_seed_list"],[361,362,363])
        self.assertEqual(len(r["repetitions"]),3)
        self.assertEqual(len(r["splits"]),3)
        self.assertEqual(r["epsilon"],0.20)
        self.assertTrue(r["same_training_cases_and_label_count"])
        self.assertFalse(r["equal_train_cost_claim"])
        self.assertTrue(r["no_oracle_training"])
        self.assertTrue(r["model_unchanged_during_evaluation"])
        self.assertFalse(r["scientific_generalization_proven"])
        self.assertFalse(r["main_modified"])
        self.assertEqual(r["paid_api_calls"],0)
        self.assertIn(r["status"],{
            "DESCRIPTIVE_SELF_CONTINUATION_ADVANTAGE",
            "NO_SELF_CONTINUATION_ADVANTAGE",
            "INSUFFICIENT_IDENTIFIABLE_CASES",
        })
        for rep in r["repetitions"]:
            self.assertEqual(rep["model_sha_before"],rep["model_sha_after"])
            self.assertEqual(rep["training_uniform"]["episodes"],
                             rep["training_self"]["episodes"])
            self.assertGreater(rep["training_uniform"]["cost_spent"],0)
            self.assertGreater(rep["training_self"]["cost_spent"],0)
            for name,_,num,_ in o.SPLITS:
                s=rep["evaluations"][name]["summary"]
                self.assertEqual(s["total"],num)
                self.assertEqual(s["eligible"]+s["impossible"],num)


if __name__=="__main__":
    unittest.main()
