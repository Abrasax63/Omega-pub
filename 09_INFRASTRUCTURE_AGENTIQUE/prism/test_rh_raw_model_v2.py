"""New-page RAW-02 no-hints input and frozen run contracts."""
import unittest
from rh_raw_model_v2 import (PROMPTS, FROZEN_PDF_SHA256,
                             FROZEN_MODEL_SHA256)
from rh_raw_model import attest


class RawV2Tests(unittest.TestCase):
    def test_prompt_only_controls_format_not_answer(self):
        for prompt in PROMPTS.values():
            low=prompt.lower()
            for secret in ("riemann", "rubinstein", "inequality (m)",
                           "estimate b", "estimate c", "prime counting", "2n choose n"):
                self.assertNotIn(secret,low)
            self.assertIn("json",low)

    def test_frozen_source_and_model_hashes(self):
        self.assertEqual(len(FROZEN_PDF_SHA256),64)
        self.assertEqual(len(FROZEN_MODEL_SHA256),64)

    def test_schema_mode_does_not_turn_citation_into_proof(self):
        page="A conditional claim is stated, but its proof is not supplied here. The statement is being studied."
        response='{"claims":[{"claim":"Some claim", "status":"unknown", "evidence":"A conditional claim is stated, but its proof is not supplied here."}],"confidence":"low"}'
        verdict=attest(page,response,"source_reading")
        self.assertEqual(verdict["accepted_exact_source_citations"],1)
        self.assertEqual(verdict["semantic_truth"],"NOT_EVALUATED")

    def test_unknown_proof_and_alternative_remain_unverified(self):
        page="The proof of a statement is not shown in this note."
        answer='{"proposal":"Reformulate the idea", "assumptions":"","evidence":"The proof of a statement is not shown in this note.", "limitations":"unverified"}'
        verdict=attest(page,answer,"creative_reinterpretation")
        self.assertEqual(verdict["novelty"],"NOT_EVALUATED")
        self.assertEqual(verdict["mathematical_entailment"],"NOT_EVALUATED")


if __name__=="__main__":
    unittest.main()
