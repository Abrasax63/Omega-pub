"""No-provider-call tests; imports the pilot but not torch/transformers."""
import unittest
from p5_free_cpu_pilot import (
    PUBLIC_CASES, ARMS, MODEL_ID, MAX_NEW_TOKENS,
    case_request, make_messages, extract_answer, schedule, preflight,
)

class PublicCpuPilotTests(unittest.TestCase):
    def test_real_model_is_not_loaded_by_tests(self):
        import sys
        self.assertNotIn("transformers", sys.modules)
        self.assertNotIn("openai", sys.modules)

    def test_all_eighteen_public_requests_are_equal_information(self):
        self.assertEqual(len(PUBLIC_CASES),6)
        self.assertEqual(MODEL_ID,"Qwen/Qwen2.5-0.5B-Instruct")
        self.assertEqual(MAX_NEW_TOKENS,80)
        for case in PUBLIC_CASES:
            shared = [case_request(case,a)["input"]["shared"] for a in ARMS]
            self.assertEqual(shared[0],shared[1])
            self.assertEqual(shared[1],shared[2])
            self.assertEqual(len(set(case_request(case,a)["input"]["strategy"] for a in ARMS)),3)
            for arm in ARMS:
                msgs=make_messages(case,arm)
                self.assertEqual(len(msgs),2)
                self.assertNotIn("reference_answer",str(msgs))
                self.assertNotIn("correct_answer",str(msgs))
                self.assertNotIn("expected",str(msgs))
                self.assertNotIn("gold",str(msgs))
                self.assertTrue(msgs[1]["content"].endswith("<OUI|NON|A|B|entier>."))

    def test_deterministic_order_and_complete_arm_coverage(self):
        work=schedule()
        self.assertEqual(work,schedule())
        self.assertEqual(len(work),18)
        self.assertEqual(len(set(work)),18)
        for case_index in range(6):
            self.assertEqual({a for i,a in work if i==case_index},set(ARMS))

    def test_conservative_parser_no_response_defaults(self):
        self.assertEqual(extract_answer("explication\nRéponse finale : 8"),"8")
        self.assertEqual(extract_answer("explication\nRéponse finale: non."),"NON")
        self.assertIsNone(extract_answer("Quel est 8 ?"))
        self.assertIsNone(extract_answer("Réponse finale: 8 ou 9"))
        self.assertIsNone(extract_answer(""))

    def test_preflight_zero_paid_no_private_holdout(self):
        report=preflight()
        self.assertEqual(report["status"],"NO_PROVIDER_CALL_PREFLIGHT")
        self.assertEqual(report["planned_local_generations"],18)
        self.assertEqual(report["max_paid_api_calls"],0)
        self.assertFalse(report["private_holdout_accessed"])
        self.assertEqual(len(report["rows"]),18)

if __name__ == "__main__":
    unittest.main()
