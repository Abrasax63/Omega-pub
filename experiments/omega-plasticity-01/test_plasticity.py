"""No-network regression tests, independent of scientific holdout outcomes."""
from __future__ import annotations
from copy import deepcopy
from math import isclose
from pathlib import Path
import random
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import plasticity_lab as p
from mealy_lab import Mealy


def distinguishable():
    return Mealy(((0, 1), (1, 0)), ((0, 0), (1, 1)))


def indistinguishable():
    return Mealy(((0, 0), (1, 1)), ((0, 0), (0, 0)))


class PlasticityRegressionTests(unittest.TestCase):

    def test_environment_A_B_Aprime_costs(self):
        m=distinguishable()
        a=p.checks_for(m,p.A_COSTS)
        b=p.checks_for(m,p.B_COSTS)
        self.assertEqual([c.cost for c in a],[1,1,2,2,2,2])
        self.assertEqual([c.cost for c in b],[3,3,1,1,1,1])
        self.assertEqual([c.values for c in a],[c.values for c in b])
        self.assertEqual(p.A_COSTS,(1,2))

    def test_known_machine_and_hidden_start_not_passed_to_policy(self):
        m=distinguishable()
        c=p.checks_for(m,p.A_COSTS)
        for initial in (0,1):
            r=p.run_episode(m,c,initial,"fixed")
            self.assertTrue(r["success"])
            self.assertEqual(r["remaining"],[initial])
            self.assertEqual(r["total_cost"],sum(t["cost"] for t in r["decisions"]))

    def test_abstention_if_indistinguishable(self):
        m=indistinguishable()
        checks=p.checks_for(m,p.A_COSTS)
        self.assertFalse(p.fully_identifiable(checks,m.size))
        self.assertFalse(p.run_episode(m,checks,0,"fixed")["success"])
        c=p.collect_phase([("impossible",m)],p.A_COSTS,"train",random.Random(4))
        self.assertEqual(c["eligible"],0)
        self.assertEqual(c["impossible"],1)
        self.assertFalse(c["examples"])
        self.assertEqual(c["episodes"][0]["status"],"IMPOSSIBLE_WITH_SIX_PROBES")

    def test_one_probe_reveals_hidden_state(self):
        m=distinguishable()
        for initial in (0,1):
            response=p.run_episode(m,p.checks_for(m,p.A_COSTS),
                                   initial,"fixed")
            self.assertTrue(response["success"])
            self.assertLessEqual(response["total_cost"],2)

    def test_observed_return_to_go_not_teacher_labels(self):
        sample=p.collect_phase([("example",distinguishable())],
                               p.B_COSTS,"train_B",random.Random(22))
        self.assertEqual(sample["eligible"],1)
        self.assertEqual(len(sample["episodes"]),2)
        expected=[]
        for e in sample["episodes"]:
            total=0
            for step in reversed(e["observed_decisions"]):
                total += step["cost"]
                self.assertEqual(step["observed_return_to_go"],total)
                self.assertGreaterEqual(total,step["cost"])
                expected.append(step["observed_return_to_go"])
        self.assertEqual(sorted(expected),
                         sorted(x["observed_return_to_go"]
                                for x in sample["examples"]))
        self.assertTrue(all("oracle" not in str(x).lower()
                            for x in sample["examples"]))

    def test_collect_never_calls_exact_oracle(self):
        # Fail loudly if even an accidental training call resolves the oracle.
        with patch.object(p,"solve",side_effect=RuntimeError("LEAK")):
            data=p.collect_phase([("example",distinguishable())],
                                 p.A_COSTS,"A",random.Random(7))
            model=p.LinearPolicy.blank().learn(data["examples"])
            self.assertGreater(model.updates,0)

    def test_feature_dimensions_and_cost_awareness(self):
        m=distinguishable()
        group=(0,1)
        x=p.features(group,p.checks_for(m,p.A_COSTS)[0])
        y=p.features(group,p.checks_for(m,p.B_COSTS)[0])
        self.assertEqual(len(x),p.FEATURE_COUNT)
        self.assertEqual(len(y),p.FEATURE_COUNT)
        self.assertNotEqual(x,y)
        self.assertTrue(all(isinstance(v,float) for v in x))

    def test_real_weight_update_for_observed_cost(self):
        m=distinguishable()
        data=p.collect_phase([("x",m)],p.A_COSTS,"A",random.Random(17))
        policy=p.LinearPolicy.blank()
        before=policy.snapshot()
        policy.learn(data["examples"])
        after=policy.snapshot()
        self.assertGreater(after["updates"],0)
        self.assertNotEqual(before["weights_sha256"],after["weights_sha256"])

    def test_memory_and_learner_observe_exact_same_examples(self):
        data=p.collect_phase([("x",distinguishable())],
                             p.A_COSTS,"A",random.Random(6))
        memory=deepcopy(data["examples"])
        source=p.digest(memory)
        policy=p.LinearPolicy.blank().learn(data["examples"])
        self.assertEqual(p.digest(memory),source)
        self.assertEqual(len(memory),policy.updates)
        choice=p.choose((0,1),p.checks_for(distinguishable(),p.A_COSTS),
                        "memory",memory=memory)
        self.assertIsNotNone(choice)

    def test_same_relearn_feedback_different_initial_parameters(self):
        data=p.collect_phase([("x",distinguishable())],
                             p.A_COSTS,"A",random.Random(28))
        warm=p.LinearPolicy.blank().learn(data["examples"])
        cold=p.LinearPolicy.blank()
        count=len(data["examples"])
        warm.learn(data["examples"])
        cold.learn(data["examples"])
        self.assertEqual(warm.updates,2*count)
        self.assertEqual(cold.updates,count)

    def test_evaluate_is_read_only(self):
        data=p.collect_phase([("x",distinguishable())],
                             p.A_COSTS,"A",random.Random(5))
        policy=p.LinearPolicy.blank().learn(data["examples"])
        before=deepcopy(policy.snapshot())
        memory=deepcopy(data["examples"])
        result=p.evaluate([("x",distinguishable())],p.A_COSTS,
                          p._policies(policy,memory,p.LinearPolicy.blank()))
        self.assertEqual(result["total"],1)
        self.assertEqual(result["eligible"],1)
        self.assertEqual(before,policy.snapshot())
        self.assertTrue(all(value["worst_regret"]>=0
                            for value in result["rows"][0]["arms"].values()))

    def test_evaluation_oracle_rejects_false_minimax_success(self):
        m=distinguishable()
        r=p.evaluate([("x",m)],p.B_COSTS,
                     {"FIXED":("fixed",None,None)})
        self.assertEqual(r["eligible"],1)
        self.assertEqual(r["rows"][0]["oracle_worst"],1)
        self.assertGreaterEqual(r["rows"][0]["arms"]["FIXED"]["cost_worst"],1)

    def test_frozen_cohorts_disjoint_including_previous_pilot(self):
        groups=p.group_machines()
        from mealy_lab import make_cohorts
        old={s for part in make_cohorts().values()
             for s,_ in part["machines"]}
        seen=old.copy()
        for name,seed,count in p.GROUPS:
            sigs=[s for s,_ in groups[name]["machines"]]
            self.assertEqual(len(sigs),count)
            self.assertEqual(len(sigs),len(set(sigs)))
            self.assertFalse(set(sigs)&seen)
            seen.update(sigs)
        self.assertEqual(len(seen),90+sum(x[2] for x in p.GROUPS))

    def test_deterministic_replay_and_primary_no_leak(self):
        a=p.collect_phase([("x",distinguishable())],
                          p.A_COSTS,"A",random.Random(19))
        b=p.collect_phase([("x",distinguishable())],
                          p.A_COSTS,"A",random.Random(19))
        self.assertEqual(a["examples_sha256"],b["examples_sha256"])
        self.assertEqual(a["episodes_sha256"],b["episodes_sha256"])
        self.assertEqual(len(a["examples"]),len(b["examples"]))

    def test_full_aba_stops_and_preserves_historical_results(self):
        r=p.conduct()
        self.assertEqual(r["experiment"],"OMEGA-PLASTICITY-01")
        self.assertEqual(len(r["data_splits"]),6)
        self.assertEqual([r["data_splits"][n]["size"] for n,_,_ in p.GROUPS],
                         [36,36,16,18,18,24])
        self.assertEqual([x["relearn_machines"] for x in r["relearn_checkpoints"]],
                         [0,8,16])
        self.assertTrue(r["learned_parameters_changed"])
        self.assertFalse(r["training_uses_oracle"])
        self.assertFalse(r["scientific_generalization_proven"])
        self.assertEqual(r["api_calls"],0)
        self.assertFalse(r["main_modified"])
        for tag in ("evaluation_A_after_A","evaluation_A_after_B",
                    "evaluation_B_after_B"):
            v=r[tag]
            self.assertEqual(v["total"],v["eligible"]+v["impossible"])
        for checkpoint in r["relearn_checkpoints"]:
            self.assertEqual(checkpoint["evaluation"]["total"],24)
        if r["primary_WARM_minus_COLD_mean_over_Aprime_checkpoints"] is not None:
            self.assertIn(r["status"],{
                "DESCRIPTIVE_RELEARNING_ADVANTAGE",
                "NO_RELEARNING_ADVANTAGE","RELEARNING_REGRESSION",
            })


if __name__ == "__main__":
    unittest.main()
