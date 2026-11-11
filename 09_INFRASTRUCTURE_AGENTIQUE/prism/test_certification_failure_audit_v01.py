"""Post-run diagnostic tests: error attribution, not benchmark retuning."""
import json
import unittest

from certification_failure_audit_v01 import audit
from certificate_aware_selector_v01 import evaluate


class CertificateFailureAuditTests(unittest.TestCase):
    def test_explanatory_post_result_upper_bound_and_policy_parity(self):
        result=audit()
        scores=evaluate()["scores"]
        self.assertEqual(result["status"],
                         "POST_RESULT_DIAGNOSTIC_NOT_A_PRECOMMITTED_ARM")
        self.assertEqual(len(result["C_abstentions"]),2)
        self.assertEqual(
            result["max_certifiable_by_any_single_method"],23)
        self.assertEqual(
            result["retrospective_total_certified"],23)
        self.assertTrue(result["C_vs_B_all_24_paired_identical"])
        self.assertTrue(result["C_vs_D_all_24_paired_identical"])
        self.assertEqual(scores["C_certificate"]["correct"],22)
        self.assertEqual(scores["B_subtype"]["correct"],22)
        self.assertEqual(scores["D_conditioned"]["correct"],22)
        self.assertTrue(result["no_automatic_claim_of_generalization"])
        print("CERT001_FAILURE_AUDIT "+json.dumps(result,
                                             ensure_ascii=False,sort_keys=True))

    def test_documentary_failure_is_unavailable_and_euler_has_alternative(self):
        result=audit()
        unsolved=result["C_abstentions"]
        self.assertIn("CERT-DOCUMENTATION-header-07",unsolved)
        self.assertFalse(unsolved["CERT-DOCUMENTATION-header-07"]
                         ["certificate_available_among_four_methods"])
        self.assertIn("CERT-MATH-euler-04",unsolved)
        self.assertTrue(unsolved["CERT-MATH-euler-04"]
                        ["certificate_available_among_four_methods"])
        self.assertIn("compute",
                      unsolved["CERT-MATH-euler-04"]["methods_that_can_certify"])


if __name__=="__main__":
    unittest.main()
