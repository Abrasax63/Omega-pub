import unittest
from provenance_ab_evaluation import evaluate


class ProvenanceABTests(unittest.TestCase):
    def test_tool_finds_two_declared_relations_without_false_positive(self):
        result = evaluate()["results"]
        self.assertEqual(result["B_tool"]["true_positive"], 2)
        self.assertEqual(result["B_tool"]["false_positive"], 0)
        self.assertEqual(result["B_tool"]["false_negative"], 0)

    def test_baseline_does_not_claim_extraction(self):
        result = evaluate()["results"]
        self.assertEqual(result["A_baseline"]["true_positive"], 0)
        self.assertEqual(result["A_baseline"]["false_negative"], 2)

    def test_scientific_discovery_not_claimed(self):
        self.assertFalse(evaluate()["scientific_discovery_demonstrated"])


if __name__ == "__main__":
    unittest.main()
