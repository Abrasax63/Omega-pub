"""Guard RH benchmark against false proof claims and unverified logical shortcuts."""
from copy import deepcopy
import json
from pathlib import Path
import unittest

from riemann_reading_benchmark import boolean_oracle, chebyshev_exact, rules_for


HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / "riemann_reading_cases.json").read_text(encoding="utf-8"))


class RiemannBenchTests(unittest.TestCase):
    def test_horn_consequent_needs_every_premise(self):
        rules = MANIFEST["manual_controlled_rules"]["standard"]
        self.assertEqual(boolean_oracle(["m", "b", "c"], "rh", rules)["verdict"], "ENTAILED")
        for missing in ("m", "b", "c"):
            facts = [x for x in ("m", "b", "c") if x != missing]
            self.assertEqual(boolean_oracle(facts, "rh", rules)["verdict"], "NOT_ENTAILED")

    def test_converse_is_not_inferred(self):
        rules = MANIFEST["manual_controlled_rules"]["standard"]
        self.assertEqual(boolean_oracle(["rh"], "m", rules)["verdict"], "NOT_ENTAILED")

    def test_rule_order_and_controlled_paraphrase_equivalent(self):
        original = rules_for(MANIFEST, "standard")
        reversed_rules = rules_for(MANIFEST, "reverse_order")
        translated = rules_for(MANIFEST, "paraphrase")
        for rules in (original, reversed_rules, translated):
            self.assertEqual(boolean_oracle(["m", "b", "c"], "rh", rules)["verdict"],
                             "ENTAILED")

    def test_reference_is_separate_from_candidate(self):
        assert MANIFEST["distinctions"]["guide_m_status"].startswith("M is required")
        self.assertIn("NOT", MANIFEST["distinctions"]["administrative_node"])
        case = next(c for c in MANIFEST["cases"] if c["id"] == "RH-C03")
        self.assertEqual(case["expect"], "NOT_ENTAILED")
        changed = deepcopy(case)
        changed["expect"] = "ENTAILED"
        derived = boolean_oracle(changed["facts"], changed["goal"],
                                 rules_for(MANIFEST, changed["variant"]))
        self.assertNotEqual(changed["expect"], derived["verdict"])

    def test_chebyshev_example_and_counterexamples(self):
        check = chebyshev_exact(24)
        self.assertEqual(check["finite_violations"], 0)
        self.assertEqual(check["inverse_counterexample"]["n"], 4)
        self.assertEqual(check["inverse_counterexample"]["p"], 2)
        self.assertEqual(check["strict_boundary_counterexample"]["n"], 3)
        self.assertEqual(check["false_strengthening_counterexample"]["n"], 5)
        self.assertEqual(check["inference_to_RH"], "NOT_SUPPORTED_BY_FINITE_CHECKS")

    def test_oracle_fails_closed_on_state_space_overflow(self):
        chain = [{"premises": [f"a{i}"], "conclusion": f"b{i}"} for i in range(9)]
        with self.assertRaises(ValueError):
            boolean_oracle([], "rh", chain)


if __name__ == "__main__":
    unittest.main()
