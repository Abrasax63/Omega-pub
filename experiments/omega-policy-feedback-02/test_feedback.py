"""Twelve scientific non-regression tests for online/offline policy comparison."""
import json
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import feedback_lab as f
import plasticity_lab as p
from mealy_lab import Mealy, digest


def two_state():
    return Mealy(((0,1),(1,0)),((0,0),(1,1)))


def unknown():
    return Mealy(((0,0),(1,1)),((0,0),(0,0)))


class FeedbackTests(unittest.TestCase):
    def test_price_A_B_Aprime_is_predeclared(self):
        m=two_state()
        costs={phase:[v.cost for v in f.costs(m,phase)]
               for phase in ("A","B","Aprime")}
        self.assertEqual(costs["A"],[1,1,2,2,2,2])
        self.assertEqual(costs["Aprime"],costs["A"])
        self.assertEqual(costs["B"],[3,1,6,4,4,2])
        for a,b in zip(f.costs(m,"A"),f.costs(m,"B")):
            self.assertEqual(a.values,b.values)

    def test_known_hidden_state_not_a_selector_argument(self):
        m=two_state()
        rng=f.BehaviorRNG(99)
        rng._omega_weights=tuple(p.LinearPolicy.blank().weights)
        for initial in (0,1):
            outcome=f.collect_one(m,initial,f.costs(m,"A"),"ON",rng)
            self.assertTrue(outcome["success"])
            self.assertEqual(outcome["identified_state"],initial)
            self.assertEqual(outcome["total_cost"],sum(
                s["cost"] for s in outcome["steps"]))

    def test_off_and_on_different_behavior_reachable(self):
        m=two_state()
        selected=[]
        def trace_choice(group,checks,arm,**kwargs):
            selected.append((group,arm,kwargs.get("weights")))
            return p.choices(group,checks)[0]
        rng=f.BehaviorRNG(7)
        rng.random=lambda:1.0
        rng._omega_weights=(0.9,)*p.FEATURE_COUNT
        with patch.object(f.old,"choose",side_effect=trace_choice):
            result=f.collect_one(m,1,f.costs(m,"A"),"ON",rng)
        self.assertTrue(result["success"])
        self.assertTrue(selected)
        self.assertEqual(selected[0][1],"learned")
        self.assertEqual(selected[0][2],[0.9]*p.FEATURE_COUNT)

    def test_genuine_observed_return_label(self):
        m=two_state()
        rng=f.BehaviorRNG(11)
        r=f.collect_one(m,0,f.costs(m,"B"),"OFF",rng)
        self.assertTrue(r["success"])
        remainder=0
        for step in reversed(r["steps"]):
            remainder+=step["cost"]
            self.assertEqual(step["observed_return_to_go"],remainder)
            self.assertNotIn("oracle",step)
        self.assertEqual(remainder,r["total_cost"])

    def test_impossible_cases_in_denominator(self):
        policy_a=p.LinearPolicy.blank()
        policy_b=p.LinearPolicy.blank()
        result=f.collect([("impossible",unknown())],"A",
                         (f.BehaviorRNG(5),f.BehaviorRNG(1005)),
                         policy_a,policy_b,[])
        self.assertEqual(result["machines"],1)
        self.assertEqual(result["eligible"],0)
        self.assertEqual(result["impossible"],1)
        self.assertEqual(result["arms"]["OFF"]["episodes"],0)
        self.assertEqual(result["arms"]["ON"]["episodes"],0)

    def test_training_does_not_consult_exact_oracle(self):
        off=p.LinearPolicy.blank()
        on=p.LinearPolicy.blank()
        memory=[]
        with patch.object(f.old,"solve",side_effect=RuntimeError("ORACLE LEAK")):
            row=f.collect([("two-state",two_state())],"A",
                          (f.BehaviorRNG(3),f.BehaviorRNG(10003)),
                          off,on,memory)
        self.assertEqual(row["arms"]["OFF"]["episodes"],2)
        self.assertEqual(row["arms"]["ON"]["episodes"],2)
        self.assertGreater(off.updates,0)
        self.assertGreater(on.updates,0)

    def test_memory_only_off_observed_examples(self):
        off=p.LinearPolicy.blank()
        on=p.LinearPolicy.blank()
        memory=[]
        r=f.collect([("two-state",two_state())],"A",
                    (f.BehaviorRNG(9),f.BehaviorRNG(1009)),
                    off,on,memory)
        n=r["arms"]["OFF"]["decisions"]
        self.assertEqual(len(memory),n)
        self.assertEqual(off.updates,n)
        self.assertEqual(on.updates,r["arms"]["ON"]["decisions"])
        self.assertTrue(all("observed_return_to_go" in ex for ex in memory))

    def test_equal_training_episodes_not_claimed_equal_symbol_costs(self):
        off=p.LinearPolicy.blank()
        on=p.LinearPolicy.blank()
        memory=[]
        r=f.collect([("two-state",two_state())],"B",
                    (f.BehaviorRNG(1),f.BehaviorRNG(10001)),
                    off,on,memory)
        self.assertEqual(r["arms"]["OFF"]["episodes"],
                         r["arms"]["ON"]["episodes"])
        for arm in ("OFF","ON"):
            self.assertGreater(r["arms"][arm]["probe_cost"],0)

    def test_test_oracle_is_evaluator_only_and_minimax_bound(self):
        m=two_state()
        off=p.LinearPolicy.blank()
        on=p.LinearPolicy.blank()
        mem=[{"features":p.features((0,1),f.costs(m,"A")[0]),
              "observed_return_to_go":1}]
        v=f.evaluate([("test",m)],"A",off,on,mem)
        self.assertEqual(v["eligible"],1)
        self.assertEqual(v["total"],1)
        for arm in v["rows"][0]["arms"].values():
            self.assertGreaterEqual(arm["worst_regret"],0)

    def test_isomorphism_is_global_against_prior_127_128(self):
        splits=f.cohorts()
        earlier=p.group_machines()
        used={sig for entry in earlier.values() for sig,_ in entry["machines"]}
        from mealy_lab import make_cohorts
        used.update(sig for entry in make_cohorts().values()
                    for sig,_ in entry["machines"])
        for name,seed,count in f.GROUPS:
            sigs=[sig for sig,_ in splits[name]["machines"]]
            self.assertEqual(len(sigs),count)
            self.assertFalse(set(sigs)&used)
            used.update(sigs)
        self.assertEqual(len(used),90+148+sum(x[2] for x in f.GROUPS))

    def test_seeded_replay_same_data_and_updates(self):
        def run():
            off=p.LinearPolicy.blank()
            on=p.LinearPolicy.blank()
            memory=[]
            d=f.collect([("two-state",two_state())],"A",
                        (f.BehaviorRNG(19),f.BehaviorRNG(10019)),
                        off,on,memory)
            return d["arms"]["OFF"]["records_sha256"], d["arms"]["ON"]["records_sha256"],off.snapshot(),on.snapshot()
        self.assertEqual(run(),run())

    def test_complete_trial_three_seeds_checkpoint_contrast(self):
        d=f.conduct()
        self.assertEqual(d["experiment"],f.EXPERIMENT)
        self.assertEqual(d["prereg_commit"],
                         "3a88640aa947ec7f1de829d8d601578d8eb3263d")
        self.assertEqual(len(d["repetitions"]),3)
        self.assertEqual(d["primary_sample_points"],9)
        for record in d["repetitions"]:
            self.assertEqual([c["after_training_machines"]
                              for c in record["checkpoints_Aprime"]],[0,8,16])
            self.assertEqual(record["actual_training_episode_count"]["OFF"],
                             record["actual_training_episode_count"]["ON"])
            for cp in record["checkpoints_Aprime"]:
                self.assertEqual(cp["evaluation"]["total"],24)
                self.assertEqual(cp["evaluation"]["eligible"]+
                                 cp["evaluation"]["impossible"],24)
        self.assertFalse(d["learner_trained_on_oracle"])
        self.assertFalse(d["scientific_generalization_proven"])
        self.assertFalse(d["main_modified"])


if __name__=="__main__":
    unittest.main()
