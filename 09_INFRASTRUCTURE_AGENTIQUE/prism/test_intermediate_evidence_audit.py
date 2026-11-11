"""Independent exact invariants for post-run strategic information audit."""
from fractions import Fraction
import unittest
import json
from intermediate_evidence_audit import audit
from intermediate_evidence_policy import evaluate

class StrategicInformationAuditTests(unittest.TestCase):
    def test_route_has_zero_immediate_truth_information_but_positive_future_value(self):
        r=audit()
        self.assertEqual(r["answer_prior"],"1/2")
        self.assertEqual(set(r["route_conditional_answer_probability"].values()),{"1/2"})
        self.assertEqual(r["probe_immediate_answer_information_bits"],"0")
        self.assertEqual(r["absolute_certification_gain"],14)
        self.assertEqual(r["n_unavoidable_simulated_outages"],4)
        self.assertEqual(r["test_total"],32)
        self.assertEqual(r["fixed_max_route_coverage_under_two_exclusive_specialists"],14)

    def test_strong_adaptive_and_omega_have_identical_realized_traces(self):
        r=audit()
        self.assertTrue(r["paired_C_D_E_identical"])
        self.assertEqual(len(r["scored_cases"]),32)
        s=evaluate()["scores"]
        for arm in ("C_omega","D_certificate","E_strong_conditional"):
            self.assertEqual((s[arm]["correct"],s[arm]["calls"]),(28,64))
        print("STRAT004_THEOREM_AUDIT "+json.dumps({
            "zero_information":r["probe_immediate_answer_information_bits"],
            "gain":r["absolute_certification_gain"],
            "paired_C_D_E_identical":r["paired_C_D_E_identical"],
            "outages":r["n_unavoidable_simulated_outages"],
        },sort_keys=True))

if __name__=="__main__":
    unittest.main()
