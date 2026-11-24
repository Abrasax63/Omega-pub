"""Adversarial no-cheating tests for source-literal-only Omega RH inference gate."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from rh_raw_model import PROMPTS, attest, read_raw_page, safe_json


class RawSourceTests(unittest.TestCase):
    SOURCE = (
        "The working paper introduces a conditional estimate of prime sums. "
        "The author takes the proof of the central estimate from a separate "
        "formal development and provides a human explanation of the reduction. "
        "Another elementary bound is proved in the working paper."
    )

    def test_prompt_has_no_answer_key(self):
        for name, text in PROMPTS.items():
            self.assertNotIn("riemann", text.casefold())
            self.assertNotIn("rubinstein", text.casefold())
            self.assertNotIn("main inequality", text.casefold())
            self.assertNotIn("estimate b", text.casefold())
            self.assertNotIn("estimate c", text.casefold())
            self.assertNotIn("m+b+c", text.casefold())
            self.assertIn("source", text.casefold())

    def test_exact_literal_citation_only(self):
        import json
        good = json.dumps({"claims": [
            {"claim": "An estimate is assumed from formal development.",
             "status": "quoted",
             "evidence": "The author takes the proof of the central estimate from a separate formal development"}
        ]})
        checked = attest(self.SOURCE, good, "source_reading")
        self.assertEqual(checked["accepted_exact_source_citations"], 1)
        self.assertEqual(checked["semantic_truth"], "NOT_EVALUATED")
        self.assertEqual(checked["mathematical_entailment"], "NOT_EVALUATED")

    def test_source_paraphrase_is_not_a_citation(self):
        import json
        bad = json.dumps({"claims": [
            {"claim": "A new theorem", "evidence": "The proof is independently established here."},
            {"claim": "Extra", "evidence": ""}
        ]})
        checked = attest(self.SOURCE, bad, "source_reading")
        self.assertEqual(checked["claims_seen"], 2)
        self.assertEqual(checked["accepted_exact_source_citations"], 0)
        self.assertEqual(len(checked["quarantined"]), 2)

    def test_missing_and_broken_json_is_not_rescued(self):
        self.assertIsNone(safe_json("Output: {\"claims\":[]}"))
        checked = attest("abc "*80, "a text answer without machine-readable citations", "source_reading")
        self.assertEqual(checked["syntax"], "INVALID_JSON")
        self.assertEqual(checked["accepted_exact_source_citations"], 0)

    def test_creative_proposal_requires_grounding(self):
        import json
        content = json.dumps({"proposal": "Look for a different reduction",
                              "evidence": "Another elementary bound is proved in the working paper."})
        checked = attest(self.SOURCE, content, "creative_reinterpretation")
        self.assertEqual(checked["accepted_exact_source_citations"], 1)
        self.assertEqual(checked["novelty"], "NOT_EVALUATED")
        content = json.dumps({"proposal": "Proved a theorem", "evidence": "untraceable text"})
        self.assertEqual(attest(self.SOURCE, content,
                                "creative_reinterpretation")["accepted_exact_source_citations"], 0)

    def test_input_page_must_be_real_and_not_silently_shortened(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "raw.txt"
            path.write_text(self.SOURCE)
            text, digest = read_raw_page(path)
            self.assertEqual(text, self.SOURCE)
            self.assertEqual(len(digest), 64)
            path.write_text("tiny")
            with self.assertRaises(ValueError):
                read_raw_page(path)


if __name__ == "__main__":
    unittest.main()
