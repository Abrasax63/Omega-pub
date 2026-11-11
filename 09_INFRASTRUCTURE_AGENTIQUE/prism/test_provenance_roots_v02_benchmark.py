"""CI-visible summary of the frozen v0.2 ablation: no external model or calls."""
import json
import unittest
from provenance_roots_v02_benchmark import run


class ProvenanceRootsV02ReportTests(unittest.TestCase):
    def test_publish_reproducible_equal_budget_metrics(self):
        report = run()
        self.assertEqual(report["status"], "PUBLIC_REPLAY_NOT_BLIND")
        self.assertEqual(report["model_calls"], 0)
        self.assertEqual(report["new_remote_consultations"], 0)
        self.assertEqual(report["maximum_consultations_per_case"], 2)
        for arm, data in report["summary_12_cases"].items():
            self.assertEqual(data["cases"], 12)
            self.assertLessEqual(data["calls"], 24)
            self.assertEqual(data["confident_wrong"], 0, arm)
        for arm in ("B_v2_fixed", "D_v2_adaptive"):
            self.assertEqual(report["t3_authentic_secondary_same_budget"][arm]["decision"], "yes")
            self.assertEqual(report["d5_forged_root_same_budget"][arm]["decision"], None)
        for arm in ("B_v1_fixed", "D_v1_adaptive"):
            self.assertEqual(report["d5_forged_root_same_budget"][arm]["decision"], "yes")
        # Print compact numbers to the CI log, not a claimed statistical estimate.
        print("PROVENANCE_V02_CI_SUMMARY " + json.dumps({
            "main": report["summary_12_cases"],
            "T3": report["t3_authentic_secondary_same_budget"],
            "D5_spoof": report["d5_forged_root_same_budget"],
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main()
