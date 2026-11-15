import copy
import unittest

from gate import ABSTAIN, digest, evaluate, validate_manifest


def fixture():
    manifest = {
        "experiment_id": "DEMO-SYNTHETIC-01",
        "cost_unit": "declared_tool_calls",
        "max_cost_per_case": 2,
        "training_case_ids": ["train-a", "train-b"],
        "training_group_ids": ["train-group-a", "train-group-b"],
        "cost_policy": "no_increase",
        "required_domains": ["provenance", "math"],
        "holdout": [
            {"case_id": "p1", "group_id": "prov-family", "domain": "provenance", "expected": "copie"},
            {"case_id": "p2", "group_id": "prov-family", "domain": "provenance", "expected": "recalcul"},
            {"case_id": "m1", "group_id": "math-family", "domain": "math", "expected": "vrai"},
            {"case_id": "m2", "group_id": "math-family", "domain": "math", "expected": "faux"},
        ],
    }
    observations = {"experiment_id": "DEMO-SYNTHETIC-01", "arms": {
        "baseline": {"source_commit": "synthetic-baseline", "run_url": "https://example.invalid/baseline", "results": [
            {"case_id": "p1", "prediction": "copie", "cost": 1},
            {"case_id": "p2", "prediction": ABSTAIN, "cost": 1},
            {"case_id": "m1", "prediction": "vrai", "cost": 2},
            {"case_id": "m2", "prediction": ABSTAIN, "cost": 1},
        ]},
        "candidate": {"source_commit": "synthetic-candidate", "run_url": "https://example.invalid/candidate", "results": [
            {"case_id": "p1", "prediction": "copie", "cost": 1},
            {"case_id": "p2", "prediction": "recalcul", "cost": 1},
            {"case_id": "m1", "prediction": "vrai", "cost": 2},
            {"case_id": "m2", "prediction": "faux", "cost": 1},
        ]},
    }}
    return manifest, observations


class GateTests(unittest.TestCase):
    def check(self, manifest=None, observations=None):
        m, o = fixture()
        if manifest is not None:
            m = manifest
        if observations is not None:
            o = observations
        return evaluate(m, o, digest(m))

    def test_gain_never_claims_certification(self):
        r = self.check()
        self.assertEqual(r["metrics"]["baseline"]["correct"], 2)
        self.assertEqual(r["metrics"]["candidate"]["correct"], 4)
        self.assertTrue(r["candidate_for_independent_review"])
        self.assertEqual(r["provenance_status"], "UNVERIFIED_EXTERNAL_INPUTS")

    def test_false_confirmation_rejected(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"][3]["prediction"] = "vrai"
        self.assertFalse(self.check(m, o)["candidate_for_independent_review"])

    def test_loss_of_known_correct_rejected(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"][0]["prediction"] = ABSTAIN
        r = self.check(m, o)
        self.assertEqual(r["lost_correct_case_ids"], ["p1"])
        self.assertFalse(r["candidate_for_independent_review"])

    def test_equal_accuracy_with_lower_cost_allowed(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"][1]["prediction"] = ABSTAIN
        o["arms"]["candidate"]["results"][3]["prediction"] = ABSTAIN
        o["arms"]["candidate"]["results"][2]["cost"] = 1
        self.assertTrue(self.check(m, o)["candidate_for_independent_review"])

    def test_equal_accuracy_without_cost_gain_rejected(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"][1]["prediction"] = ABSTAIN
        o["arms"]["candidate"]["results"][3]["prediction"] = ABSTAIN
        self.assertFalse(self.check(m, o)["candidate_for_independent_review"])

    def test_training_holdout_overlap_rejected(self):
        m, _ = fixture()
        m["training_case_ids"].append("p1")
        with self.assertRaisesRegex(ValueError, "overlap"):
            validate_manifest(m)

    def test_duplicate_holdout_rejected(self):
        m, _ = fixture()
        m["holdout"].append(copy.deepcopy(m["holdout"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            validate_manifest(m)

    def test_duplicate_arm_case_rejected(self):
        m, o = fixture()
        o["arms"]["baseline"]["results"].append(copy.deepcopy(o["arms"]["baseline"]["results"][0]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self.check(m, o)

    def test_missing_result_rejected(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"].pop()
        with self.assertRaisesRegex(ValueError, "missing"):
            self.check(m, o)

    def test_budget_overflow_rejected(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"][0]["cost"] = 3
        with self.assertRaisesRegex(ValueError, "outside budget"):
            self.check(m, o)

    def test_boolean_cost_rejected(self):
        m, o = fixture()
        o["arms"]["candidate"]["results"][0]["cost"] = True
        with self.assertRaisesRegex(ValueError, "outside budget"):
            self.check(m, o)

    def test_manifest_mutation_rejected(self):
        m, o = fixture()
        h = digest(m)
        m["max_cost_per_case"] = 3
        with self.assertRaisesRegex(ValueError, "does not match"):
            evaluate(m, o, h)

    def test_mismatched_experiment_id_rejected(self):
        m, o = fixture()
        o["experiment_id"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.check(m, o)

    def test_unknown_gold_rejected(self):
        m, _ = fixture()
        m["holdout"][0]["expected"] = ABSTAIN
        with self.assertRaisesRegex(ValueError, "must be known"):
            validate_manifest(m)

    def test_no_baseline_source_metadata_rejected(self):
        m, o = fixture()
        o["arms"]["baseline"]["run_url"] = ""
        with self.assertRaisesRegex(ValueError, "required"):
            self.check(m, o)


    def test_more_correct_but_more_total_cost_is_rejected(self):
        m, o = fixture()
        # Every case stays within the per-case budget, but aggregate cost rises 5 -> 8.
        for row in o["arms"]["candidate"]["results"]:
            row["cost"] = 2
        result = self.check(m, o)
        self.assertEqual(result["metrics"]["baseline"]["correct"], 2)
        self.assertEqual(result["metrics"]["candidate"]["correct"], 4)
        self.assertEqual(result["metrics"]["baseline"]["cost"], 5)
        self.assertEqual(result["metrics"]["candidate"]["cost"], 8)
        self.assertFalse(result["cost_fair"])
        self.assertFalse(result["candidate_for_independent_review"])

    def test_equal_total_cost_passes_cost_policy(self):
        result = self.check()
        self.assertTrue(result["cost_fair"])
        self.assertTrue(result["candidate_for_independent_review"])

    def test_exact_parity_rejects_cheaper_candidate(self):
        m, o = fixture()
        m["cost_policy"] = "exact_parity"
        o["arms"]["candidate"]["results"][2]["cost"] = 1
        result = self.check(m, o)
        self.assertFalse(result["cost_fair"])
        self.assertFalse(result["candidate_for_independent_review"])

    def test_exact_parity_accepts_equal_cost(self):
        m, o = fixture()
        m["cost_policy"] = "exact_parity"
        self.assertTrue(self.check(m, o)["candidate_for_independent_review"])

    def test_total_budget_rejects_above_cap(self):
        m, o = fixture()
        m["max_total_cost"] = 4
        result = self.check(m, o)
        self.assertFalse(result["total_budget_satisfied"])
        self.assertFalse(result["candidate_for_independent_review"])

    def test_invalid_total_budget_type_rejected(self):
        m, _ = fixture()
        m["max_total_cost"] = True
        with self.assertRaisesRegex(ValueError, "max_total_cost"):
            validate_manifest(m)

    def test_invalid_cost_policy_rejected(self):
        m, _ = fixture()
        m["cost_policy"] = "reward_tuning"
        with self.assertRaisesRegex(ValueError, "cost_policy"):
            validate_manifest(m)

    def test_missing_holdout_group_rejected(self):
        m, _ = fixture()
        del m["holdout"][0]["group_id"]
        with self.assertRaisesRegex(ValueError, "group_id required"):
            validate_manifest(m)

    def test_training_holdout_same_group_rejected(self):
        m, _ = fixture()
        m["training_group_ids"].append("prov-family")
        with self.assertRaisesRegex(ValueError, "overlap by group_id"):
            validate_manifest(m)

    def test_previous_holdout_group_reuse_rejected_when_declared(self):
        m, _ = fixture()
        m["previous_holdout_group_ids"] = ["math-family"]
        with self.assertRaisesRegex(ValueError, "previous holdout groups reused"):
            validate_manifest(m)

    def test_training_group_list_required(self):
        m, _ = fixture()
        del m["training_group_ids"]
        with self.assertRaisesRegex(ValueError, "training_group_ids"):
            validate_manifest(m)

    def test_full_result_deterministic(self):
        self.assertEqual(self.check(), self.check())


if __name__ == "__main__":
    unittest.main()
