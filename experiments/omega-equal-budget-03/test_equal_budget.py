"""OMEGA-EQUAL-BUDGET-03: twelve fail-closed regression controls."""
from __future__ import annotations

import json
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import equal_budget_lab as e
from mealy_lab import Mealy


def simple():
    return Mealy(((0,1),(1,0)),((0,0),(1,1)))


def impossible():
    return Mealy(((0,0),(1,1)),((0,0),(0,0)))


class EqualBudgetTests(unittest.TestCase):
    def test_cost_families_observations_unchanged(self):
        m=simple()
        c={name:e.priced_checks(m,name) for name in "ABCD"}
        expected={
            "A":[1,1,2,2,2,2],
            "B":[3,1,6,4,4,2],
            "C":[1,3,2,4,4,6],
            "D":[2,2,1,1,1,1],
        }
        for name in "ABCD":
            self.assertEqual([k.cost for k in c[name]],expected[name])
            self.assertEqual([k.values for k in c[name]],
                             [k.values for k in c["A"]])

    def test_selector_interface_does_not_take_hidden_state(self):
        m=simple()
        checks=e.priced_checks(m,"A")
        rng=random.Random(1)
        model=e.p.LinearPolicy.blank()
        action=e.choose_probe((0,1),checks,"ON",model,rng)
        self.assertIn(action.name,("0","1","00","01","10","11"))
        self.assertLessEqual(action.cost,2)

    def test_observed_suffix_return_only_after_complete(self):
        m=simple()
        checks=e.priced_checks(m,"A")
        complete=e.training_episode(m,1,checks,2,"OFF",
                                    e.p.LinearPolicy.blank(),random.Random(9))
        self.assertTrue(complete["complete"])
        self.assertEqual(complete["spent"],sum(x["cost"] for x in complete["steps"]))
        self.assertEqual(complete["updates"],len(complete["examples"]))
        running=0
        for step in reversed(complete["steps"]):
            running+=step["cost"]
            self.assertEqual(step["observed_return_to_go"],running)
        self.assertTrue(all("observed_return_to_go" in x
                            for x in complete["examples"]))

    def test_incomplete_episode_does_not_learn(self):
        m=simple()
        # B has no cheap informative probe if action 1 cannot distinguish:
        # force the original single distinguishable action to be unaffordable.
        checks=tuple(k for k in e.priced_checks(m,"B") if k.name=="0")
        self.assertEqual(checks[0].cost,3)
        result=e.training_episode(m,0,checks,2,"OFF",
                                  e.p.LinearPolicy.blank(),random.Random(6))
        self.assertFalse(result["complete"])
        self.assertEqual(result["updates"],0)
        self.assertNotIn("examples",result)
        self.assertEqual(result["spent"],0)

    def test_training_does_not_call_exact_oracle(self):
        machines=[("two",simple())]*4
        with patch.object(e.p,"solve",side_effect=RuntimeError("LEAK")):
            row=e.train_budgeted(machines,"A",8,"OFF",19)
        self.assertEqual(row["charged_cost"],8)
        self.assertTrue(row["fully_paid"])
        self.assertGreater(row["updates"],0)

    def test_genuine_calibration_filler_paid_not_trained(self):
        m=simple()
        # Budget 3 over repeated 2-state runs: depending on chosen probe,
        # allow all valid combinations and enforce actual ledger identities.
        r=e.train_budgeted([("two",m)]*10,"B",7,"OFF",3)
        self.assertEqual(r["charged_cost"],7)
        self.assertEqual(r["episode_cost_used"]+r["filler_cost"],7)
        self.assertEqual(len(r["calibration"]),r["filler_cost"])
        self.assertTrue(all(c["trained_on_this"] is False for c in r["calibration"]))
        self.assertEqual(r["updates"],len(r["memory"]))

    def test_budget_never_overruns_even_with_partial(self):
        for phase in ("A","B"):
            for budget in (1,2,3,7,11,19):
                data=e.train_budgeted([("two",simple())]*50,phase,budget,
                                      "ON",19)
                self.assertEqual(data["charged_cost"],budget)
                self.assertEqual(data["unspent_due_to_cohort_exhaustion"],0)
                self.assertLessEqual(data["episode_cost_used"],budget)
                self.assertEqual(data["updates"],len(data["memory"]))

    def test_impossible_case_skipped_without_fake_reward(self):
        data=e.train_budgeted([("impossible",impossible())]*2+
                              [("two",simple())]*30,"A",10,"OFF",5)
        self.assertEqual(data["charged_cost"],10)
        self.assertGreaterEqual(data["skipped_nonidentifiable_before_budget_stop"],2)
        self.assertTrue(all(item["complete"] or "observed_return_to_go"
                            not in item["steps"][-1] for item in data["audit"]))

    def test_exact_evaluation_and_abstention(self):
        model=e.p.LinearPolicy.blank()
        mem=[{"features":list(e.p.features((0,1),e.priced_checks(simple(),"A")[0])),
              "observed_return_to_go":1}]
        arms=e.evaluated_arms(model,model,mem,mem)
        r=e.evaluate([("impossible",impossible()),("two",simple())],"C",arms)
        self.assertEqual(r["total"],2)
        self.assertEqual(r["impossible"],1)
        self.assertEqual(r["eligible"],1)
        for item in r["rows"]:
            if item["identifiable"]:
                self.assertTrue(all(x["worst_regret"]>=0
                                    for x in item["arms"].values()))
            else:
                self.assertEqual(item["arms"],{})

    def test_replay_and_weight_hashes_deterministic(self):
        def replay():
            row=e.train_budgeted([("two",simple())]*20,"A",19,"ON",111)
            return row["weights_sha256"],row["memory_sha256"],row["audit_sha256"]
        self.assertEqual(replay(),replay())

    def test_new_splits_disjoint_from_old_three_pilots(self):
        new=e.machine_groups()
        used=set()
        prior=(e.make_cohorts(),e.p.group_machines(),e.previous.cohorts())
        for catalog in prior:
            for part in catalog.values():
                for sig,_ in part["machines"]: used.add(sig)
        self.assertEqual(len(used),362)
        for name,seed,num in e.GROUPS:
            sigs=[sig for sig,_ in new[name]["machines"]]
            self.assertEqual(len(sigs),num)
            self.assertFalse(set(sigs)&used)
            used.update(sigs)
        self.assertEqual(len(used),362+sum(v[2] for v in e.GROUPS))

    def test_full_trial_frozen_budgets_and_no_oracle_training(self):
        r=e.conduct()
        self.assertEqual(r["experiment"],e.EXPERIMENT)
        self.assertEqual(r["prereg_commit"],e.PRE_REG)
        self.assertEqual(r["per_phase_budgets"],[120,240,360])
        self.assertEqual(r["seeds"],[881,882,883])
        self.assertEqual(len(r["observations"]),9)
        self.assertTrue(r["no_optimal_labels_in_train"])
        self.assertFalse(r["language_model_trained"])
        self.assertEqual(r["paid_api_calls"],0)
        self.assertFalse(r["scientific_generalization_proven"])
        for row in r["observations"]:
            self.assertEqual(row["charged_total_cost"]["OFF"],2*row["per_phase_budget"])
            self.assertEqual(row["charged_total_cost"]["ON"],2*row["per_phase_budget"])
            self.assertTrue(row["comparison_valid_at_charged_budget"])
            for arm in ("OFF","ON"):
                for ph in ("A","B"):
                    info=row["train"][arm][ph]
                    self.assertEqual(info["episode_cost_used"]+info["filler_cost"],info["budget"])
            for family in ("C","D"):
                ev=row["evaluation"][family]
                self.assertEqual(ev["total"],28)
                self.assertEqual(ev["total"],ev["eligible"]+ev["impossible"])


if __name__=="__main__":
    unittest.main()
