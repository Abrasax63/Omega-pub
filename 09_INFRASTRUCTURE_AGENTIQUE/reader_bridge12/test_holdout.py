import unittest
from pathlib import Path
from read import blob, run
from evaluate_holdout import evaluate, HOLD, CASES, HERE

PINNED_READER_BLOB="c4540abb6fd5f38bff74d3ee8ffa723976604ce6"
PINNED_GATE_BLOB="d21513bb088669274d8cb6b4b07291d682a6da5a"
PINNED_MODEL_BLOB="870293844b837f1a43a1e0d6002cd4f5c7c41699"
PINNED_PIPELINE_BLOB="a39e9e9bec9e0b6f781f99e34c23836829f0b8d4"


class FirstUnseenSourceReaderTest(unittest.TestCase):
    def test_models_and_reader_unchanged_since_source_selection(self):
        self.assertEqual(blob((HERE/"read.py").read_bytes()), PINNED_READER_BLOB)
        self.assertEqual(blob((HERE/"gate.py").read_bytes()), PINNED_GATE_BLOB)
        self.assertEqual(blob((HERE/"model.py").read_bytes()), PINNED_MODEL_BLOB)
        self.assertEqual(blob((HERE/"pipeline.py").read_bytes()), PINNED_PIPELINE_BLOB)

    def test_both_source_blobs_and_citations(self):
        for ident,name,sha in CASES:
            p=HOLD/name
            self.assertEqual(blob(p.read_bytes()),sha)
            d=run(p,sha)
            self.assertGreater(d["stats"]["packet_count"],0)
            self.assertTrue(d["source_citations_valid"])

    def test_original_holdout_report_is_deterministic_and_no_model_was_called(self):
        a=evaluate()
        self.assertEqual(a,evaluate())
        self.assertEqual(a["source_count"],2)
        self.assertEqual(a["actual_language_model_calls"],0)
        self.assertFalse(a["automatic_semantic_reading_demonstrated"])
        self.assertTrue(a["all_source_spans_valid"])
        self.assertTrue(a["no_horn_rule_injection"])
        self.assertEqual(a["scientific_verdict"],"INDETERMINATE_NOT_SEMANTICALLY_CHECKED")

    def test_inline_proof_probe_is_reported_honestly(self):
        r=evaluate()
        self.assertIn(r["context_protection_gate"],
                      ("DEFECT_INLINE_PROOF_NOT_BLOCKED","BLOCKED"))
        self.assertIsInstance(r["proof_statement_allowed_as_quarantined_conclusion_evidence"], bool)


if __name__=="__main__":
    unittest.main()
