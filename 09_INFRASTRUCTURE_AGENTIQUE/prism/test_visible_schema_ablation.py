"""Audit of the real boundary on claimed conditional planning gains."""
import unittest
import json
from visible_schema_ablation import audit


class VisibleSchemaAblationTests(unittest.TestCase):
    def test_free_schema_exposes_cost_of_opaque_diagnostic(self):
        result=audit()
        self.assertEqual(result["status"],
            "POST_RESULT_ALTERNATIVE_INFORMATION_REGIME_NOT_FAIR_COMPETITOR")
        self.assertEqual((result["visible_schema_correct"],
                          result["visible_schema_abstain"],
                          result["visible_schema_wrong"],
                          result["visible_schema_checks"]), (28,4,0,32))
        self.assertEqual((result["opaque_certificate_correct"],
                          result["opaque_certificate_checks"]), (28,64))
        self.assertEqual(result["potential_cost_savings_if_schema_visible"],32)
        self.assertTrue(result["cannot_compare_as_equal_information"])
        print("STRAT004_TRANSPARENCY_ABLATION "+json.dumps({
            "free_type": "28/32 correct at 32 checks",
            "opaque": "28/32 correct at 64 checks",
            "equal_information_comparison":False,
        },sort_keys=True))

if __name__=="__main__":
    unittest.main()
