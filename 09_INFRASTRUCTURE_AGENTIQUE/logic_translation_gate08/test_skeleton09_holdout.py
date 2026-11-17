import unittest
from translate import blob
from evaluate_skeleton09 import ENGINE, ENGINE_SHA, GOLD, GOLD_SHA, SOURCE, evaluate
from skeleton09 import run, independent_check

class ProspectiveTwoCardTests(unittest.TestCase):
    def test_unmodified_compiled_grammar_and_source_gold(self):
        self.assertEqual(blob(ENGINE.read_bytes()), ENGINE_SHA)
        self.assertEqual(blob(GOLD.read_bytes()), GOLD_SHA)
        self.assertEqual(blob((SOURCE/"BR-AFFINE-GROUP-CORE_BRIQUE.md").read_bytes()),
                         "6838a2e95ab64ae53406e4fc75abc267e4366745")
        self.assertEqual(blob((SOURCE/"BR-ACC-STATE-COMMUTE-01_BRIQUE.md").read_bytes()),
                         "c4c89930f075983e085da5e38c956f12dc61186e")

    def test_raw_citations_and_no_unsafe_claims(self):
        for filename, sha in (
            ("BR-AFFINE-GROUP-CORE_BRIQUE.md", "6838a2e95ab64ae53406e4fc75abc267e4366745"),
            ("BR-ACC-STATE-COMMUTE-01_BRIQUE.md", "c4c89930f075983e085da5e38c956f12dc61186e"),
        ):
            path = SOURCE / filename
            output = run(path, sha)
            self.assertEqual(independent_check(path.read_bytes(), output), [])
            self.assertTrue(output["citations_valid"])
            self.assertEqual(output["horn_rules"], [])
            self.assertTrue(all(item["promotable"] is False for item in output["items"]))

    def test_structural_results_deterministic_and_not_certification(self):
        result = evaluate()
        self.assertEqual(result, evaluate())
        self.assertEqual(result["salient_gold_count"], 12)
        self.assertTrue(result["citations_valid"])
        self.assertEqual(result["automatic_horn_rules"], 0)
        self.assertEqual(result["unsafe_promotion_ids"], [])
        self.assertIn("NOT_SEMANTIC", result["status"])

if __name__ == "__main__":
    unittest.main()
