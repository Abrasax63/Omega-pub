import unittest
from read import blob, run
from gate import gate
from test_bridge import V7, sample_v7_model_answer
from evaluate_holdout import HOLD, CASES, evaluate
from pathlib import Path

HERE=Path(__file__).resolve().parent

class InlineContextTests(unittest.TestCase):
    def test_reader_did_not_change(self):
        self.assertEqual(blob((HERE/"read.py").read_bytes()),
                         "c4540abb6fd5f38bff74d3ee8ffa723976604ce6")

    def test_pinned_delta_inline_proof_is_blocked(self):
        file=HOLD/CASES[1][1]
        sha=CASES[1][2]
        doc=run(file,sha)
        packet=next(p for p in doc["packets"] if p["start_line"]<=56<=p["end_line"])
        original=file.read_text(encoding="utf-8").splitlines()[55]
        data={"source_blob":sha,"claims":[{
            "claim_id":"C1","packet_id":packet["packet_id"],
            "evidence":[{"role":"conclusion","packet_id":packet["packet_id"],
                         "line":56,"literal":original[:100]}]
        }]}
        out=gate(file.read_bytes(),file.as_posix(),data)
        self.assertEqual(out["accepted_count"],0)
        self.assertEqual(out["rejected"][0]["reason"],
                         "INLINE_PROOF_REFUTATION_OR_COUNTEREXAMPLE")

    def test_positive_fixture_is_still_review_only(self):
        out=gate(V7.read_bytes(),V7.as_posix(),sample_v7_model_answer())
        self.assertEqual(out["accepted_count"],1)
        self.assertEqual(out["horn_rules"],[])
        self.assertEqual(out["accepted"][0]["verdict"],"INDETERMINATE")

    def test_recorded_holdout_replay(self):
        result=evaluate()
        self.assertEqual(result["context_protection_gate"],"BLOCKED")
        self.assertFalse(result["proof_statement_allowed_as_quarantined_conclusion_evidence"])
        self.assertEqual(result["actual_language_model_calls"],0)
        self.assertFalse(result["pre_registered_display_math_in_each_source"])

if __name__=="__main__":
    unittest.main()
