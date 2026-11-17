import unittest
from evaluate_holdout import evaluate, HOLD, GOLD, GOLD_BLOB, PARSER, PARSER_BLOB
from fidelity import git_blob, run

class FrozenSemanticFidelityHoldout(unittest.TestCase):
    def test_program_source_and_gold_all_pinned(self):
        self.assertEqual(git_blob(PARSER.read_bytes()), PARSER_BLOB)
        self.assertEqual(git_blob(GOLD.read_bytes()), GOLD_BLOB)
        self.assertEqual(
            git_blob((HOLD/"NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md").read_bytes()),
            "6c482f97345abbb7f3d5bcd5e20da96259b276ce")
        self.assertEqual(
            git_blob((HOLD/"rapport_spectre_defauts_iteration_1.md").read_bytes()),
            "b75f3d610ba73b6c549d212d0606465d9fe947a3")

    def test_technical_safety_does_not_count_as_scientific_success(self):
        r = evaluate()
        self.assertEqual(r["status"], "NOT_EVALUABLE_NO_IN_GRAMMAR_FORMULAS")
        self.assertFalse(r["scientific_success"])
        self.assertEqual(r["heldout_eligible_formulas"], 0)
        self.assertEqual(r["gold_semantically_salient_items"], 16)
        self.assertTrue(r["zero_unreviewed_horn_imports"])

    def test_report_is_reproducible_and_context_is_measured(self):
        one = evaluate()
        self.assertEqual(one, evaluate())
        self.assertEqual(one["document_count"], 2)
        self.assertTrue(all(d["latex_delimiter_lines"] > 0
                            for d in one["per_source"].values()))
        self.assertTrue(one["all_presented_candidates_structurally_verified"])

    def test_no_auto_promotions_from_two_unseen_documents(self):
        sources = [
            ("NOTE_RECHERCHE_V7_POLYNOME_TEMPOREL.md",
             "6c482f97345abbb7f3d5bcd5e20da96259b276ce"),
            ("rapport_spectre_defauts_iteration_1.md",
             "b75f3d610ba73b6c549d212d0606465d9fe947a3"),
        ]
        for file, sha in sources:
            o = run(HOLD/file, sha)
            self.assertEqual(o["horn_rules"], [])
            self.assertEqual(o["automatic_promotions"], 0)
            self.assertTrue(o["checked_all_candidates"])
            self.assertTrue(all(x["promotable"] is False for x in o["candidates"]))

if __name__ == "__main__":
    unittest.main()
