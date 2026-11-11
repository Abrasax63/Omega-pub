"""Regression tests for an explicit and falsifiable trust boundary."""
import copy
import unittest

from provenance_benchmark import _read
from provenance_policy import decide as decide_v1
from trusted_receipt_adapter import decide_guarded, TrustedReceiptAdapter


class RootAndNormativeArbitrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = {t["id"]: t for t in _read("tasks")}
        cls.observations = _read("observations")
        cls.t3 = _read("supplement_t3")

    def test_actual_public_conflict_v1_abstains_and_v2_uses_normative_scope(self):
        task = self.t3["task"]
        receipts = self.t3["observations"]
        v1 = decide_v1(task, receipts.__getitem__, budget=2)
        fixed = decide_guarded(task, receipts.__getitem__, budget=2,
                               fixed=True, authority_by_field={"rule":"ietf"})
        omega = decide_guarded(task, receipts.__getitem__, budget=2,
                               authority_by_field={"rule":"ietf"})
        self.assertIsNone(v1["decision"])
        for result in (fixed, omega):
            self.assertEqual(result["decision"], "yes")
            self.assertEqual(result["risk"], "0")
            self.assertLessEqual(len(result["trace"]), 2)
            self.assertEqual(len(result["trace"]), 2)
            self.assertEqual(result["adapter_rejections"][0]["field"], "independence")

    def test_authentic_secondary_can_disagree_with_explicitly_targeted_standard(self):
        task = self.t3["task"]
        observations = copy.deepcopy(self.t3["observations"])
        # The authentic MDN page is a distinct source, not an IETF dependent.
        observations["00-copy"]["independence"] = "mdn"
        no_precedence = decide_guarded(task, observations.__getitem__, budget=2)
        self.assertIsNone(no_precedence["decision"])
        for fixed in (True, False):
            result = decide_guarded(task, observations.__getitem__, budget=2,
                                    fixed=fixed, authority_by_field={"rule":"ietf"})
            self.assertEqual(result["decision"], "yes")
            self.assertEqual(result["adapter_rejections"][0]["reason"],
                             "not_normative_authority")
            self.assertEqual(len(result["trace"]), 2)

    def test_fake_independent_root_must_not_earn_quorum(self):
        task = self.tasks["D5"]
        observations = copy.deepcopy(self.observations["D5"])
        observations["01-copy"]["independence"] = "spoofed-new-root"
        v1 = decide_v1(task, observations.__getitem__, budget=2)
        self.assertEqual(v1["decision"], "yes")  # v1 CERTAINTY ERROR (truth=None)
        for fixed in (True, False):
            v2 = decide_guarded(task, observations.__getitem__, budget=2, fixed=fixed)
            self.assertIsNone(v2["decision"])
            self.assertEqual(len(v2["trace"]), 2)
            self.assertEqual(v2["adapter_rejections"][0],
                             {"check":"01-copy", "reason":"catalog_mismatch",
                              "field":"independence"})

    def test_equally_authoritative_conflicting_references_still_abstain(self):
        task = self.tasks["D4"]
        for fixed in (True, False):
            result = decide_guarded(task, self.observations["D4"].__getitem__,
                                    budget=2, fixed=fixed)
            self.assertIsNone(result["decision"])
            self.assertEqual(result["trace"][-1]["conflicts_after"], ["claim"])

    def test_metadata_validation_is_not_content_authentication(self):
        task = copy.deepcopy(self.tasks["M1"])
        task["checks"] = [task["checks"][1]]
        forged = copy.deepcopy(self.observations["M1"]["01-enum"])
        forged["value"] = True  # genuine item identity, substituted content
        for fixed in (True, False):
            result = decide_guarded(task, lambda _id: forged,
                                    budget=1, fixed=fixed)
            self.assertEqual(result["decision"], "yes")
            # Actual truth for M1 is 'no'; this must remain a visible limitation.
            self.assertNotEqual(result["decision"], _read("answer_key")["M1"]["decision"])
            self.assertEqual(result["adapter_rejections"], [])

    def test_invalid_authority_configuration_rejected_before_observation(self):
        task = self.t3["task"]
        for authority in ({"rule":"mdn"}, {"other":"ietf"},
                          {"rule":"invented"}):
            with self.assertRaises(ValueError):
                TrustedReceiptAdapter(task, lambda k: None, authority)

    def test_both_arms_share_same_ceiling_and_no_stale_fixture_mutation(self):
        for task in self.tasks.values():
            observations = self.observations[task["id"]]
            for fixed in (True, False):
                result = decide_guarded(task, observations.__getitem__,
                                        budget=2, fixed=fixed)
                ids = [step["check"] for step in result["trace"]]
                self.assertLessEqual(len(ids), 2)
                self.assertEqual(len(ids), len(set(ids)))


if __name__ == "__main__":
    unittest.main()
