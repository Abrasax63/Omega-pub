"""Regression on exploratory train-only fallback; original STRAT-002 is immutable."""
import unittest
from strategic_method_fallback_diagnostic import run
from strategic_methods_executable import tasks
from strategic_method_selection import evaluate

class ExploratoryFallbackTests(unittest.TestCase):
    def test_no_regression_no_forged_certificates_and_only_train_based_switches(self):
        report=run()
        self.assertEqual(report["status"],"POST_RESULT_EXPLORATION_ONLY")
        self.assertEqual(report["case_count"],16)
        self.assertEqual(report["Omega_original_correct"],evaluate()["summary"]["C_omega"]["correct"])
        self.assertEqual(report["Omega_original_calls"],evaluate()["summary"]["C_omega"]["calls"])
        self.assertLessEqual(report["Omega_guarded_calls"],32)
        for r in report["rows"]:
            self.assertLessEqual(r["new_calls"],2)
            self.assertGreaterEqual(r["new_calls"],r["old_calls"])
            if r["new"] is not None:
                self.assertEqual(r["new"],r["truth"])

    def test_specific_failed_first_methods_and_documentary_limit(self):
        data={r["id"]:r for r in run()["rows"]}
        self.assertIsNone(data["M5"]["old"])
        self.assertEqual(data["M5"]["new"],"yes")
        self.assertEqual(data["M5"]["fallback_methods"],["compute"])
        self.assertIsNone(data["P5"]["old"])
        self.assertEqual(data["P5"]["new"],"yes")
        self.assertEqual(data["P5"]["fallback_methods"],["source"])
        self.assertIsNone(data["S4"]["new"])
        self.assertEqual(data["S4"]["new_calls"],1)
        # This diagnostic cannot claim improvement over equally strong
        # subtype-fixed baseline on this deliberately tiny corpus.
        baseline=evaluate()["summary"]["F_subtype_fixed"]
        self.assertLessEqual(data["M5"]["new_calls"],2)
        self.assertEqual(baseline["correct"],15)
        self.assertEqual(run()["Omega_guarded_correct"],baseline["correct"])
        print("STRAT002_FALLBACK_CI_SUMMARY original=%s/%s calls=%s guarded=%s/%s calls=%s strong_fixed=%s/%s calls=%s" % (
            run()["Omega_original_correct"],16,run()["Omega_original_calls"],
            run()["Omega_guarded_correct"],16,run()["Omega_guarded_calls"],
            baseline["correct"],16,baseline["calls"]))

if __name__=="__main__":
    unittest.main()
