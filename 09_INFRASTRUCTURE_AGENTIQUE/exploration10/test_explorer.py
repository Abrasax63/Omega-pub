import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import explorer as e


class ExplorationLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=e.load_sample()

    def test_data_pinned_and_first_30_new_cases(self):
        self.assertEqual(len(self.rows),30)
        self.assertEqual(e.gitblob(e.FROZEN.read_bytes()),e.FROZEN_BLOB)
        self.assertEqual(e.gitblob(e.TRANSLATOR_FILE.read_bytes()),
                         e.FROZEN_TRANSLATOR_BLOB)
        self.assertTrue(all("label" in row for row in self.rows))

    def test_free_generation_multiple_distinct_perspectives(self):
        row=self.rows[0]
        candidates=e.propose(row["conclusion"],row["premises"])
        self.assertGreaterEqual(len(candidates),2)
        self.assertLessEqual(len(candidates),e.BUDGET)
        self.assertGreaterEqual(len({x["perspective"] for x in candidates}),2)
        self.assertEqual(len({x["candidate_id"] for x in candidates}),len(candidates))
        self.assertTrue(all(not c["certified"] for c in candidates))

    def test_all_source_quotes_are_real(self):
        for row in self.rows:
            candidates=e.propose(row["conclusion"],row["premises"])
            for c in candidates:
                self.assertEqual(
                    c["source"]["exact_excerpt"],
                    row["premises"][c["source"]["premise_index"]])
                a=e.critique(c,row["premises"],row["conclusion"])
                self.assertTrue(a["accepted_as_hypothesis"])
                self.assertFalse(a["semantic_truth_verified"])

    def test_forged_citation_rejected(self):
        r=self.rows[0]
        c=copy.deepcopy(e.propose(r["conclusion"],r["premises"])[0])
        c["source"]["exact_excerpt"]="A fabricated theorem says yes."
        a=e.critique(c,r["premises"],r["conclusion"])
        self.assertFalse(a["accepted_as_hypothesis"])
        self.assertIn("FORGED_OR_MISQUOTED_EXCERPT",a["errors"])

    def test_illicit_promotion_rejected(self):
        r=self.rows[1]
        c=copy.deepcopy(e.propose(r["conclusion"],r["premises"])[0])
        c["certified"]=True
        c["scientific_status"]="CERTIFIED"
        a=e.critique(c,r["premises"],r["conclusion"])
        self.assertFalse(a["accepted_as_hypothesis"])
        self.assertIn("ILLEGAL_STATUS_PROMOTION",a["errors"])
        self.assertIn("UNSUPPORTED_CERTIFICATION",a["errors"])

    def test_unexecuted_test_claim_rejected(self):
        row=self.rows[0]
        c=copy.deepcopy(e.propose(row["conclusion"],row["premises"])[0])
        c["test_status"]="SUCCESS"
        self.assertIn("UNEXECUTED_TEST_CLAIMED_AS_DONE",
                      e.critique(c,row["premises"],row["conclusion"])["errors"])

    def test_budget_and_diversity(self):
        row=self.rows[0]
        with self.assertRaises(e.EvidenceError):
            e.propose(row["conclusion"],row["premises"],max_candidates=0)
        with self.assertRaises(e.EvidenceError):
            e.propose(row["conclusion"],row["premises"],max_candidates=99)
        self.assertEqual(len(e.propose(row["conclusion"],row["premises"],1)),1)
        self.assertEqual(len(e.propose(row["conclusion"],row["premises"],2)),2)

    def test_new_case_does_not_auto_promote(self):
        row=self.rows[0]
        state=e.view_case(row["conclusion"],row["premises"],{},case_id="new")
        self.assertEqual(state["strict_verdict"],"ABSTAIN")
        self.assertEqual(state["final_scientific_verdict"],"ABSTAIN")
        self.assertGreater(state["hypotheses_proposed"],0)
        self.assertEqual(state["certified_hypotheses"],0)
        self.assertFalse(state["new_scientific_answer_from_exploration"])
        self.assertEqual(state["independent_semantic_tests_executed"],0)

    def test_modified_external_data_or_parser_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"edited.jsonl"
            p.write_bytes(e.FROZEN.read_bytes()+b"\n")
            with patch.object(e,"FROZEN",p):
                with self.assertRaisesRegex(e.EvidenceError,"sample changed"):
                    e.load_sample()
            q=Path(tmp)/"fake.py"
            q.write_text("this would change the language interface",encoding="utf-8")
            with patch.object(e,"TRANSLATOR_FILE",q):
                with self.assertRaisesRegex(e.EvidenceError,"translator changed"):
                    e.load_sample()

    def test_end_to_end_and_negative_science_result(self):
        r=e.evaluate_external()
        self.assertEqual(r["sample_cases"],30)
        self.assertEqual(r["scientific_answers"],0)
        self.assertEqual(r["scientific_hypotheses_certified"],0)
        self.assertEqual(r["independent_semantic_tests_executed"],0)
        self.assertEqual(r["hypotheses_proposed"],r["hypotheses_provenance_valid"])
        self.assertGreaterEqual(r["hypotheses_proposed"],60)
        self.assertEqual(r["model_calls"],0)
        self.assertEqual(r["status"],"EXPLORATION_ONLY_NO_TRANSFER_PROVEN")
        self.assertTrue(r["predictions_and_hypotheses_sha256_before_gold"])
        self.assertTrue(r["no_automatic_promotion"])
        self.assertEqual(len(r["rows"]),30)

    def test_cli_report_json_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"report.json"
            cmd=[sys.executable,str(e.HERE/"explorer.py"),"--output",str(path)]
            proc=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertTrue(proc.stdout.startswith("PREDICTIONS_AND_HYPOTHESES_BEFORE_GOLD_SHA256="))
            obj=json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(obj["sample_cases"],30)
            self.assertGreater(obj["hypotheses_proposed"],0)

    def test_refuse_in_repository_report_path(self):
        p=e.HERE/"forbidden.json"
        cmd=[sys.executable,str(e.HERE/"explorer.py"),"--output",str(p)]
        result=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
        self.assertNotEqual(result.returncode,0)
        self.assertIn("outside checkout",result.stderr)
        self.assertFalse(p.exists())


if __name__=="__main__":
    unittest.main()
