import itertools
import unittest

from pilot import SCHEDULE, SOURCE_GRAMMAR, observe, request_params, target_grammar, target_prompt
from score import grade, measurements


class TransferTest(unittest.TestCase):
    def test_source_captures_a_refuted_prediction(self):
        trace = observe("SAME AB BA")
        self.assertEqual(trace["outputs"], [2, 1])
        self.assertTrue(trace["prediction_refuted"])
        self.assertTrue(trace["isolated_order_effect"])
        self.assertEqual(observe("SAME AB XX")["experiments"], 0)

    def test_order_and_limit_exact_witnesses(self):
        self.assertTrue(grade("order", "ORDRE FFG FGF")["success"])
        self.assertTrue(grade("limit", "CHARGE FFFF FFGG")["success"])
        self.assertFalse(grade("order", "ORDRE FFG FFG")["success"])

    def test_no_permutation_can_distinguish_the_limit_case(self):
        words = ["".join(x) for x in itertools.product("FG", repeat=4)]
        for left, right in itertools.combinations(words, 2):
            if left.count("F") == right.count("F"):
                self.assertEqual(measurements("limit", left), measurements("limit", right))
                self.assertTrue(grade("limit", f"ORDRE {left} {right}")["false_order_transfer"])
                self.assertFalse(grade("limit", f"ORDRE {left} {right}")["success"])

    def test_tasks_share_observations_and_arm_order_is_alternated(self):
        trace = observe("SAME AB BA")
        a = target_prompt("task", trace, "memo content")
        b = target_prompt("task", trace, "(emplacement neutre)")
        self.assertEqual(a.replace("memo content", "(emplacement neutre)"), b)
        self.assertEqual([arm for _, arm in SCHEDULE], ["MEMO", "SANS_MEMO", "SANS_MEMO", "MEMO"])

    def test_grammar_keeps_both_hypotheses_and_both_decisions_available(self):
        self.assertIn('("SAME" | "DIFFERENT")', SOURCE_GRAMMAR)
        self.assertIn('[AB]{2,5}', SOURCE_GRAMMAR)
        for case, length in [("order", 3), ("limit", 4)]:
            params = request_params("sys", "problem", 64, target_grammar(case))
            self.assertIn('"NONE" | ("ORDRE" | "CHARGE")', params["grammar"])
            self.assertIn(f"[FG]{{{length}}}", params["grammar"])
            self.assertEqual(params["max_tokens"], 64)
