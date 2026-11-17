import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

import countermodel_review as c
import proposer as p

class PosthocCountermodelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=p.frozen_cases()

    def test_two_actual_countermodels_satisfy_all_source_clauses(self):
        report=c.run()
        self.assertEqual(report["semantic_tests_executed"],2)
        self.assertEqual(report["new_proven_scientific_theorems"],0)
        self.assertEqual([x["external_row"] for x in report["cases"]],[62,64])
        self.assertTrue(all(x["all_manually_encoded_premises_satisfied"]
                            for x in report["cases"]))
        self.assertTrue(all(x["candidate_claim_false_in_model"] for x in report["cases"]))
        self.assertTrue(all(x["posthoc"] and not x["statistical_holdout"]
                            for x in report["cases"]))

    def test_mike_f1_unjustified_as_reverse_implication(self):
        model=c.case62()
        self.assertTrue(all(c.satisfies(model["witness"],x) for x in model["clauses"]))
        self.assertFalse(c.pred(model["witness"],"Mike","f1"))
        model["witness"]["Mike"]["f1"]=True
        with self.assertRaisesRegex(ValueError,"does not refute"):
            c.audit_case(model,self.rows)

    def test_ted_can_be_pet_without_being_cow(self):
        model=c.case64()
        self.assertTrue(all(c.satisfies(model["witness"],x) for x in model["clauses"]))
        self.assertTrue(c.pred(model["witness"],"Ted","pet"))
        self.assertFalse(c.pred(model["witness"],"Ted","cow"))
        self.assertTrue(c.pred(model["witness"],"Another","cow"))
        # Removing the other cow witness destroys the existential source fact.
        model["witness"]["Another"]["cow"]=False
        with self.assertRaisesRegex(ValueError,"violates at least one premise"):
            c.audit_case(model,self.rows)

    def test_forged_source_mapping_is_detected(self):
        source=c.case64()
        source["clauses"][0]["source_index"]=4
        with self.assertRaisesRegex(ValueError,"index must be exact"):
            c.audit_case(source,self.rows)

    def test_syntactic_clause_verifier_rejects_unknown_rule(self):
        with self.assertRaisesRegex(ValueError,"unsupported explicit audit"):
            c.satisfies({"Ted":{}},{"kind":"magic"})

    def test_versioned_memory_checkpoint_restores_exact_12_model_events(self):
        import base64
        import gzip
        import hashlib
        import ledger
        checkpoint=p.HERE/"LEDGER_CHECKPOINT_2026-11-17.jsonl.gz.b64"
        raw=gzip.decompress(base64.b64decode(checkpoint.read_text(encoding="utf-8")))
        self.assertEqual(hashlib.sha256(raw).hexdigest(),
                         "38864b20197b7b2c36f9a65fdffd263c85c4e0d48367a1780475c6cd5b3a23ea")
        events,latest=ledger.replay(raw.decode("utf-8"))
        self.assertEqual(len(events),12)
        self.assertEqual(len(latest),12)
        self.assertEqual(events[-1]["event_hash"],
                         "6cd253c378c38bf9be62b25c549cebbb85ebb552502b0dc5da3b3cb5a4225686")
        self.assertTrue(all(x["status"]=="PROPOSED" for x in events))

    def test_posthoc_cli_json(self):
        result=subprocess.run([sys.executable,str(p.HERE/"countermodel_review.py")],
                              text=True,capture_output=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
        report=json.loads(result.stdout)
        self.assertEqual(report["semantic_tests_executed"],2)
        self.assertEqual(report["status"],
                         "TWO_MODEL_PROPOSALS_REFUTED_UNDER_MANUAL_TRANSLATION")

if __name__=="__main__":
    unittest.main()
