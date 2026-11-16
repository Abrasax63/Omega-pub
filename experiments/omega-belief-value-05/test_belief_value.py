"""15 scientific checks for shared-experience successor-belief value learning."""
from __future__ import annotations

import inspect
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import belief_value_lab as b
from mealy_lab import Mealy, digest


def example4():
    return Mealy(
        ((0,1),(0,2),(2,0),(2,3)),
        ((0,0),(1,1),(2,2),(0,1)),
    )


def impossible4():
    m=example4()
    return Mealy(m.transitions,tuple((0,0) for _ in range(4)))


class BeliefValueTests(unittest.TestCase):

    def test_known_4_state_random_family(self):
        m=example4()
        self.assertEqual(m.size,4)
        self.assertEqual(b.category(m),"random4")
        self.assertTrue(b.fully_identifiable(m.checks(),m.size))

    def test_genuine_novel_5_state_families(self):
        for kind in ("perm5","reset5"):
            rng=random.Random(37)
            for _ in range(4):
                m=b.make_machine(rng,kind)
                self.assertEqual(m.size,5)
                self.assertEqual(b.category(m),kind)
                self.assertEqual(len(m.checks()),6)

    def test_canonical_isomorphism_on_5_states(self):
        m=b.make_machine(random.Random(191),"reset5")
        perm=(3,0,4,1,2)
        inv={old:new for new,old in enumerate(perm)}
        change=Mealy(
            tuple(tuple(inv[m.transitions[old][a]]
                        for a in range(2)) for old in perm),
            tuple(m.outputs[old] for old in perm),
        )
        self.assertEqual(m.signature(),change.signature())
        self.assertNotEqual(change.transitions,m.transitions)

    def test_all_cohorts_disjoint_from_previous_five_pilots(self):
        fresh=b.cohorts()
        catalog=(
            b.make_cohorts(),
            b.previous.previous.p.group_machines(),
            b.previous.previous.previous.cohorts(),
            b.previous.previous.machine_groups(),
            b.previous.make_new_cohorts(),
        )
        used={sig for collection in catalog
              for part in collection.values()
              for sig,_ in part["machines"]}
        self.assertEqual(len(used),734)
        for name,seed,count,kind in b.COHORTS:
            row=fresh[name]
            ids=[sig for sig,_ in row["machines"]]
            self.assertEqual(len(ids),count)
            self.assertTrue(all(b.category(m)==kind
                                for _,m in row["machines"]))
            self.assertFalse(set(ids)&used)
            used.update(ids)
        self.assertEqual(len(used),734+sum(x[2] for x in b.COHORTS))

    def test_cohort_generator_exact_replay(self):
        a=b.cohorts()
        c=b.cohorts()
        for name,*_ in b.COHORTS:
            self.assertEqual(
                [s for s,_ in a[name]["machines"]],
                [s for s,_ in c[name]["machines"]],
            )

    def test_successor_partitions_sum_to_one_and_no_secret(self):
        m=example4()
        checks=m.checks()
        for group in ((0,1,2,3),(0,1,2),(0,1)):
            for check in b.choices(group,checks):
                blocks=b.partitions(group,check)
                self.assertEqual(sum(len(x) for x in blocks),len(group))
                self.assertEqual(sum(len(x)/len(group) for x in blocks),1.)
                self.assertTrue(all(len(x)<len(group) for x in blocks))

    def test_value_features_seven_and_zero_for_singletons(self):
        m=example4()
        checks=m.checks()
        x=b.successor_features((0,1),checks,m.size)
        self.assertEqual(len(x),b.VALUE_DIMS)
        self.assertTrue(all(isinstance(v,float) for v in x))
        self.assertEqual(b.successor_features((0,),checks,m.size),
                         (0.,)*b.VALUE_DIMS)

    def test_value_updates_and_cannot_predict_negative_remaining_cost(self):
        m=example4()
        model=b.BeliefValue.blank()
        before=digest(model.weights)
        features=b.successor_features((0,1),m.checks(),m.size)
        model.learn_one(features,3)
        self.assertNotEqual(before,digest(model.weights))
        self.assertEqual(model.updates,1)
        self.assertGreaterEqual(model.predict((0,1),m.checks(),m.size),0)
        model.weights=[-100.]*b.VALUE_DIMS
        self.assertEqual(model.predict((0,1),m.checks(),m.size),0)

    def test_value_policy_has_no_hidden_state_or_oracle_argument(self):
        params=list(inspect.signature(b.value_action).parameters)
        self.assertEqual(params,["group","checks","model"])
        m=example4()
        selected=b.value_action((0,1,2,3),m.checks(),b.BeliefValue.blank())
        self.assertIn(selected,b.choices((0,1,2,3),m.checks()))

    def test_true_trajectory_return_decomposes_into_immediate_and_future(self):
        m=example4()
        collected=b.collect([("fixture",m)],271)
        self.assertEqual(collected["episodes"],4)
        self.assertEqual(collected["impossible"],[])
        for raw in collected["records"]:
            self.assertEqual(raw["total_observed_cost"],
                raw["first_cost"]+raw["observed_continuation_cost"])
            self.assertEqual(raw["total_observed_cost"],
                sum(row["probe_cost"] for row in raw["trajectory"]))
            self.assertEqual(
                [int(v) for v in raw["first_observation"]],
                raw["trajectory"][0]["observable_outputs"],
            )

    def test_abstentions_preserved_and_not_trained_on(self):
        m=impossible4()
        dataset=b.collect([("bad",m),("good",example4())],272)
        self.assertEqual(dataset["impossible"],["bad"])
        self.assertEqual(dataset["episodes"],4)
        trained=b.train_shared(dataset)
        self.assertEqual(trained["baseline"].updates,4)
        self.assertEqual(trained["structured"].updates,4)

    def test_no_exact_oracle_calls_in_collection_or_training(self):
        with patch.object(b,"solve",side_effect=RuntimeError("ORACLE LEAK")):
            dataset=b.collect([("fixture",example4())],272)
            trained=b.train_shared(dataset)
        self.assertEqual(trained["baseline"].updates,4)
        self.assertEqual(trained["structured"].updates,4)

    def test_models_have_exact_same_inputs_and_one_update_per_episode(self):
        dataset=b.collect([("fixture",example4())],273)
        original=digest([{k:v for k,v in row.items() if k!="machine"}
                         for row in dataset["records"]])
        learned=b.train_shared(dataset)
        current=digest([{k:v for k,v in row.items() if k!="machine"}
                        for row in dataset["records"]])
        self.assertEqual(original,current)
        self.assertEqual(learned["baseline"].updates,dataset["episodes"])
        self.assertEqual(learned["structured"].updates,dataset["episodes"])
        self.assertEqual(len(learned["memory"]),dataset["episodes"])
        self.assertEqual(len(learned["audit"]),dataset["episodes"])

    def test_five_state_oracle_replay_and_no_false_identifications(self):
        m=b.make_machine(random.Random(91),"perm5")
        dataset=b.collect([("fixture",example4())],271)
        trained=b.train_shared(dataset)
        before=digest(trained["structured"].weights)
        evaluated=b.evaluate([("new",m),("bad",impossible4())],trained)
        self.assertEqual(evaluated["total"],2)
        self.assertEqual(digest(trained["structured"].weights),before)
        self.assertGreaterEqual(evaluated["impossible"],1)
        for row in evaluated["rows"]:
            if row["identifiable"]:
                for arm in row["arms"].values():
                    self.assertEqual(len(arm["state_costs"]),row["size"])
                    self.assertGreaterEqual(arm["worst_regret_to_oracle"],0)
            else:
                self.assertEqual(row["arms"],{})

    def test_full_preregistered_run_preserves_negative_verdict(self):
        trial=b.conduct()
        self.assertEqual(trial["experiment"],b.EXPERIMENT)
        self.assertEqual(trial["prereg_commit"],b.PREREG_SHA)
        self.assertEqual(trial["seeds"],[271,272,273])
        self.assertEqual(len(trial["repetitions"]),3)
        self.assertFalse(trial["oracle_used_during_training"])
        self.assertTrue(trial["shared_experience_between_learners"])
        self.assertTrue(trial["same_one_update_per_episode"])
        self.assertFalse(trial["language_model_trained"])
        self.assertFalse(trial["main_modified"])
        self.assertEqual(trial["paid_api_calls"],0)
        self.assertFalse(trial["scientific_generalization_proven"])
        self.assertIn(trial["status"],{
            "DESCRIPTIVE_BELIEF_VALUE_TRANSFER",
            "NO_BELIEF_VALUE_STRONG_TRANSFER",
            "INSUFFICIENT_IDENTIFIABLE_CASES",
        })
        for rep in trial["repetitions"]:
            n=rep["shared_training"]["episodes"]
            self.assertEqual(rep["models"]["TOTAL9"]["updates"],n)
            self.assertEqual(rep["models"]["BELIEF_VALUE"]["updates"],n)
            self.assertEqual(rep["memory"]["count"],n)
            for family in ("eval_control4",*b.GROUPS_OF_INTEREST):
                ev=rep["evaluations"][family]
                self.assertEqual(ev["total"],ev["eligible"]+ev["impossible"])


if __name__=="__main__":
    unittest.main()
