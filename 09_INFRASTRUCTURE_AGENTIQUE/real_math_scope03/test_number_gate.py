import unittest
from engine import evaluate_case, verify_sources
from evaluate import frozen, INPUT, INPUT_SHA, run as baseline_run
from evaluate_adversarial import load, INPUT as ADV_INPUT, IN_BLOB, run as adversarial_run


class PosthocNumberGateRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.notes = verify_sources()
        cls.normal = {c["id"]: c for c in frozen(INPUT, INPUT_SHA)["cases"]}
        cls.adversarial = {c["id"]: c for c in load(ADV_INPUT, IN_BLOB)["cases"]}

    def test_previous_24_cases_have_no_regression(self):
        report = baseline_run()
        self.assertEqual(report["engine_metrics"]["correct"], 24)
        self.assertEqual(report["engine_metrics"]["confident_errors"], 0)
        self.assertTrue(report["finite_checks_passed"])

    def test_posthoc_bad_numbers_now_abstain_not_false_contradiction(self):
        for id in ("A02", "A04"):
            self.assertEqual(evaluate_case(self.adversarial[id], self.notes)["verdict"],
                             "ABSTAIN")
        self.assertEqual(evaluate_case(self.adversarial["A08"], self.notes)["verdict"],
                         "ABSTAIN")

    def test_safety_metric_not_misrepresented_as_holdout(self):
        report = adversarial_run()
        self.assertTrue(report["engine_source_changed"])
        self.assertEqual(report["status"], "POSTHOC_SAFETY_PATCH_REPLAY_NOT_HOLDOUT")
        self.assertEqual(report["confident_errors"], [])
        self.assertFalse(report["preregistered_transfer_criterion_met"])


if __name__ == "__main__":
    unittest.main()
