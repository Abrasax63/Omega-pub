import unittest

from bridge import assess, load_bridge
from evaluate import evaluate as evaluate_v1
from evaluate_scope_v2 import (
    GOLD, GOLD_SHA, INPUT, INPUT_SHA, RULE_PATH, RULE_SHA,
    evaluate, frozen,
)
from oracle import exact_boolean_verdict


class SourceScopeRepairTests(unittest.TestCase):
    def test_scope_v2_guard_and_old_manifest_preserved(self):
        docs, by_source = load_bridge(rule_path=RULE_PATH, expected_rule_blob=RULE_SHA)
        cases = {q["id"]: q for q in frozen(INPUT, INPUT_SHA)["queries"]}
        self.assertEqual(len(cases), 16)
        self.assertEqual(len(frozen(GOLD, GOLD_SHA)["targets"]), 16)
        for id in ("Q15", "Q16"):
            ans = assess(cases[id], docs, by_source)
            self.assertEqual(ans["verdict"], "ABSTAIN")
            self.assertIn("reference_model", ans["missing_assumptions"])
            self.assertEqual(exact_boolean_verdict(cases[id], by_source["BR-DESC-01"])["verdict"],
                             "ABSTAIN")

    def test_scope_guard_not_applied_when_model_is_stated(self):
        docs, rules = load_bridge(rule_path=RULE_PATH, expected_rule_blob=RULE_SHA)
        cases = {q["id"]: q for q in frozen(INPUT, INPUT_SHA)["queries"]}
        self.assertEqual(assess(cases["Q04"], docs, rules)["verdict"], "SUPPORTED")
        self.assertEqual(assess(cases["Q05"], docs, rules)["verdict"], "CONTRADICTED")
        self.assertEqual(assess(cases["Q06"], docs, rules)["verdict"], "ABSTAIN")

    def test_full_posthoc_conformance_and_independent_oracle(self):
        report = evaluate()
        self.assertEqual(report, evaluate())
        self.assertEqual(report["count"], 16)
        self.assertEqual(report["matching_gold_and_independent_oracle"], 16)
        self.assertTrue(report["reference_model_guard_cases_abstain"])
        self.assertTrue(report["posthoc_safety_criterion"])

    def test_historical_v1_results_reproducible_and_unmodified(self):
        previous = evaluate_v1()
        self.assertEqual(previous["cases"], 14)
        self.assertEqual(previous["correct"], 14)
        self.assertTrue(previous["independent_boolean_oracle_agrees"])


if __name__ == "__main__":
    unittest.main()
