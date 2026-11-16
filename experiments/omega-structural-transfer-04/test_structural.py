"""Fifteen no-network scientific controls for OMEGA-STRUCTURAL-TRANSFER-04."""
from __future__ import annotations

import inspect
import random
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import structural_lab as s
from mealy_lab import Mealy, digest
from plasticity_lab import LinearPolicy, fully_identifiable


def identifiable():
    # Input 0 non-bijective and nonconstant, input 1 permutation.
    # Output-0 sequence alone has only 3 values; two-symbol tests complete it.
    return Mealy(
        ((0,0),(1,1),(1,2),(2,3)),
        ((0,0),(1,1),(2,2),(0,1)),
    )


def impossible():
    m=identifiable()
    return Mealy(m.transitions,tuple((0,0) for _ in range(4)))


class StructuralTransferControls(unittest.TestCase):

    def test_family_generators_have_predeclared_transition_structure(self):
        for name in ("random_restricted","permutation","reset_cycle"):
            rng=random.Random(772)
            for _ in range(6):
                machine=s.generate_machine(rng,name)
                self.assertEqual(machine.size,4)
                self.assertEqual(s.structure_kind(machine),name)

    def test_structural_families_cannot_overlap(self):
        a=s.generate_machine(random.Random(101),"random_restricted")
        b=s.generate_machine(random.Random(102),"permutation")
        c=s.generate_machine(random.Random(103),"reset_cycle")
        self.assertFalse(all(s.is_permutation(s.column(a,axis))
                             for axis in (0,1)))
        self.assertTrue(all(s.is_permutation(s.column(b,axis))
                            for axis in (0,1)))
        self.assertTrue(s.is_reset(s.column(c,0)))
        self.assertTrue(s.is_cycle4(s.column(c,1)))
        self.assertNotEqual(s.structure_kind(a),s.structure_kind(b))
        self.assertNotEqual(s.structure_kind(b),s.structure_kind(c))

    def test_canonical_signature_under_state_relabeling(self):
        m=s.generate_machine(random.Random(58),"reset_cycle")
        perm=(2,0,3,1)
        inverse={old:new for new,old in enumerate(perm)}
        changed=Mealy(tuple(tuple(inverse[m.transitions[old][i]]
                                  for i in range(2)) for old in perm),
                      tuple(m.outputs[old] for old in perm))
        self.assertEqual(m.signature(),changed.signature())

    def test_no_machine_reused_from_previous_four_pilots(self):
        new=s.make_new_cohorts()
        prior=(s.make_cohorts(),
               s.previous.p.group_machines(),
               s.previous.previous.cohorts(),
               s.previous.machine_groups())
        known={sig for catalog in prior for item in catalog.values()
               for sig,_ in item["machines"]}
        self.assertEqual(len(known),594)
        for name,seed,n,kind in s.GROUPS:
            signatures=[sig for sig,_ in new[name]["machines"]]
            self.assertEqual(len(signatures),n)
            self.assertEqual(new[name]["family"],kind)
            self.assertFalse(set(signatures) & known)
            known.update(signatures)
        self.assertEqual(len(known),594+sum(row[2] for row in s.GROUPS))

    def test_fixed_split_replays_byte_identical_signatures(self):
        a=s.make_new_cohorts()
        b=s.make_new_cohorts()
        for name,seed,count,kind in s.GROUPS:
            sig_a=[sig for sig,_ in a[name]["machines"]]
            sig_b=[sig for sig,_ in b[name]["machines"]]
            self.assertEqual(sig_a,sig_b)
            self.assertEqual(len(sig_a),count)

    def test_indistinguishable_machine_kept_as_abstention(self):
        m=impossible()
        self.assertEqual(s.structure_kind(m),"random_restricted")
        self.assertFalse(fully_identifiable(m.checks(),m.size))
        good=identifiable()
        self.assertTrue(fully_identifiable(good.checks(),good.size))
        t=s.train_seed([("bad",m),("good",good)],171)
        self.assertEqual(t["train_impossible_signatures"],["bad"])
        self.assertEqual(t["train_identifiable"],1)
        self.assertEqual(t["same_completed_episode_count"],4)

    def test_reset_probes_identify_correct_initial_state(self):
        m=identifiable()
        for hidden in range(4):
            for arm in ("OFF","ON"):
                ep=s.trajectory(m,hidden,arm,[0.0]*9,random.Random(29))
                self.assertTrue(ep["correct"])
                self.assertLessEqual(ep["total_cost"],6)
                self.assertEqual(ep["total_cost"],
                                 sum(step["probe_cost"] for step in ep["steps"]))
                self.assertEqual(ep["steps"][-1]["hypotheses_after"],[hidden])

    def test_selector_never_receives_true_hidden_state(self):
        params=list(inspect.signature(s.action_for_training).parameters)
        self.assertEqual(params,["group","checks","arm","weights","rng"])
        self.assertNotIn("secret_state",params)
        self.assertNotIn("hidden_initial",params)

    def test_no_oracle_used_during_training(self):
        with patch.object(s.previous.p,"solve",
                          side_effect=RuntimeError("ORACLE_LEAK")):
            t=s.train_seed([("fixture",identifiable())],172)
        self.assertEqual(t["same_completed_episode_count"],4)
        self.assertEqual(t["same_per_arm_charge"],24)

    def test_one_observed_return_label_per_completed_episode(self):
        t=s.train_seed([("fixture",identifiable())],173)
        for arm in ("OFF","ON"):
            self.assertEqual(t["ledgers"][arm]["training_labels"],4)
            self.assertEqual(t["parameters"][arm]["updates"],4)
            self.assertEqual(len(t["memories"][arm]["examples"]),4)
            for row in t["records"]:
                episode=row["arms"][arm]
                self.assertEqual(episode["observed_total_cost"],sum(
                    step["probe_cost"] for step in episode["actual_trajectory"]
                ))
                self.assertEqual(t["memories"][arm]["examples"][
                    row["true_initial_state_for_audit_only"]
                ]["observed_return_to_go"],episode["observed_total_cost"])

    def test_calibration_is_real_and_never_trains(self):
        t=s.train_seed([("fixture",identifiable())],171)
        for arm in ("ON","OFF"):
            ledger=t["ledgers"][arm]
            self.assertEqual(ledger["charged_cost"],24)
            self.assertEqual(ledger["charged_cost"],
                             ledger["productive_cost"]+ledger["filler_cost"])
            self.assertEqual(ledger["filler_cost"],
                             ledger["calibration_probe_count"])
            for row in t["records"]:
                x=row["arms"][arm]
                self.assertEqual(x["observed_total_cost"]+len(x["calibration"]),6)
                self.assertTrue(all(not p["used_for_learning"]
                                    for p in x["calibration"]))
                self.assertTrue(all(p["cost"]==1 for p in x["calibration"]))

    def test_equal_billed_cost_identical_episode_and_label_counts(self):
        t=s.train_seed([("m1",identifiable()),("m2",identifiable())],171)
        off,on=t["ledgers"]["OFF"],t["ledgers"]["ON"]
        self.assertEqual(off["charged_cost"],on["charged_cost"])
        self.assertEqual(off["charged_cost"],48)
        self.assertEqual(off["completed_episodes"],on["completed_episodes"])
        self.assertEqual(off["training_labels"],on["training_labels"])
        self.assertEqual(off["training_labels"],8)

    def test_seed_replay_training_records_and_parameters(self):
        def run(seed):
            t=s.train_seed([("fixture",identifiable())],seed)
            return (t["records_sha256"],
                    t["parameters"]["OFF"]["final_weights_sha256"],
                    t["parameters"]["ON"]["final_weights_sha256"])
        self.assertEqual(run(171),run(171))

    def test_exact_evaluation_is_read_only(self):
        m=identifiable()
        t=s.train_seed([("fixture",m)],171)
        before=digest(t)
        cohort={
            "control_random":{"machines":[("fixture",m)]},
            "holdout_perm":{"machines":[("fixture",m)]},
            "holdout_reset_cycle":{"machines":[("fixture",m)]},
        }
        evaluations=s.evaluate_seed(cohort,t)
        self.assertEqual(digest(t),before)
        for results in evaluations.values():
            self.assertEqual(results["eligible"],1)
            self.assertEqual(results["total"],1)
            for arm in results["rows"][0]["arms"].values():
                self.assertGreaterEqual(arm["worst_regret"],0)

    def test_full_preregistered_experiment_never_promotes_automatically(self):
        r=s.conduct()
        self.assertEqual(r["experiment"],s.EXPERIMENT)
        self.assertEqual(r["prereg_commit"],s.PREREG_SHA)
        self.assertEqual(r["seeds"],[171,172,173])
        self.assertFalse(r["scientific_generalization_proven"])
        self.assertFalse(r["language_model_trained"])
        self.assertFalse(r["main_modified"])
        self.assertEqual(r["paid_api_calls"],0)
        self.assertEqual(r["status"],
            "DESCRIPTIVE_STRONG_BASELINE_TRANSFER"
            if r["structural_family_gates_passed"]==2
            else "NO_STRONG_BASELINE_TRANSFER")
        for one in r["repetitions"]:
            train=one["training"]
            assert train["same_per_arm_charge"]==6*train["same_completed_episode_count"]
            for arm in ("OFF","ON"):
                self.assertEqual(train["ledgers"][arm]["training_labels"],
                                 train["same_completed_episode_count"])
            for family in ("holdout_perm","holdout_reset_cycle"):
                ev=one["evaluations"][family]
                self.assertEqual(ev["total"],28)
                self.assertEqual(ev["total"],ev["eligible"]+ev["impossible"])


if __name__=="__main__":
    unittest.main()
