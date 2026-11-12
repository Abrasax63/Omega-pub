"""P5-EVID-04 tests: real annotations versus actual executable evidence."""
import json
from pathlib import Path
import sqlite3
from hashlib import sha256
from tempfile import TemporaryDirectory
import unittest

import p5_evid04_claimdb_adapter as a

class ClaimDBEvidenceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample=a._load_sample()

    def test_pinned_corpus_and_pre_registered_balanced_strata(self):
        sample=self.sample
        self.assertEqual(sample["source"]["commit"],a.SOURCE_COMMIT)
        self.assertEqual(sample["source"]["git_blob_sha"],a.SOURCE_BLOB)
        self.assertEqual(sample["source"]["license"],"CC-BY-SA-4.0")
        self.assertEqual(sample["selection"]["selected_count"],36)
        self.assertEqual(sample["selection"]["total_source_records"],1000)
        self.assertEqual(len(sample["cases"]),36)
        self.assertEqual(len({r["claim_id"] for r in sample["cases"]}),36)
        self.assertEqual(len({(r["db_name"],r["bird_id"])
                              for r in sample["cases"]}),36)
        counts=a.audit()
        self.assertEqual(counts["annotated_classes"],{
            "ENTAILED":12,"CONTRADICTED":12,"NOT ENOUGH INFO":12})
        self.assertEqual(counts["nei_subtypes"],{
            "OUT-OF-SCHEMA":4,"COUNTERFACTUAL":4,"SUBJECTIVE":4})
        self.assertEqual(counts["underlying_databases"],11)

    def test_predictions_must_not_see_annotation_labels(self):
        for row in self.sample["cases"]:
            view=a.policy_input(row)
            self.assertEqual(set(view),{
                "claim_id","bird_id","db_name","claim","extra_info"})
            self.assertNotIn("annotated_label_evaluator_only",view)
            self.assertNotIn("annotated_category_evaluator_only",view)
            decision=a.decide_without_db(view)
            self.assertEqual(decision["action"],"ABSTAIN_MISSING_EVIDENCE")
            self.assertIsNone(decision["calculated_label"])
            with self.assertRaises(ValueError):
                a.decide_without_db(view,receipt={
                    "label":row["annotated_label_evaluator_only"],
                    "verified":True})
            with self.assertRaises(ValueError):
                a.decide_without_db(dict(view,
                    annotated_label_evaluator_only="ENTAILED"))

    def test_dataset_nei_different_from_missing_evidence_abstain(self):
        audit=a.audit()
        self.assertEqual(audit["abstain_missing_evidence"],36)
        self.assertEqual(audit["annotated_classes"]["NOT ENOUGH INFO"],12)
        self.assertEqual(audit["actual_sql_queries_executed_on_claimdb_databases"],0)
        self.assertEqual(audit["reproduced_independent_verdicts"],0)
        self.assertFalse(audit["has_source_db_rows"])
        self.assertTrue(audit["claimdb_nei_is_not_policy_abstention"])

    def _with_db(self):
        context=TemporaryDirectory()
        p=Path(context.name)/"small_fixture.sqlite"
        conn=sqlite3.connect(p)
        conn.execute("CREATE TABLE sample(value INTEGER)")
        conn.executemany("INSERT INTO sample(value) VALUES (?)",[(1,),(2,),(3,)])
        conn.commit()
        conn.close()
        return context,p,sha256(p.read_bytes()).hexdigest()

    def test_actual_read_only_two_query_sql_agreement_not_two_providers(self):
        ctxt,p,digest=self._with_db()
        with ctxt:
            case=a.policy_input(self.sample["cases"][0])
            r=a.execute_sql_witness(case,p,digest,
                "SELECT COUNT(*) = 3 FROM sample",
                "SELECT SUM(value) = 6 FROM sample")
            self.assertEqual(r["calculated_label"],"ENTAILED")
            self.assertEqual(r["independent_method_count"],2)
            self.assertEqual(r["independent_provider_count"],1)
            self.assertEqual(r["db_sha256"],digest)
            self.assertEqual(r["status"],
                "EXECUTED_SQL_AGREEMENT_SINGLE_DB_PROVIDER")

    def test_contradiction_or_changed_snapshot_refused(self):
        ctxt,p,digest=self._with_db()
        with ctxt:
            case=a.policy_input(self.sample["cases"][0])
            r=a.execute_sql_witness(case,p,digest,
                "SELECT COUNT(*) = 3 FROM sample",
                "SELECT COUNT(*) = 5 FROM sample")
            self.assertEqual(r["status"],"CONTRADICTORY_SQL_WITNESSES")
            self.assertIsNone(r["calculated_label"])
            with self.assertRaises(ValueError):
                a.execute_sql_witness(case,p,"f"*64,
                    "SELECT COUNT(*) = 3 FROM sample",
                    "SELECT SUM(value) = 6 FROM sample")
            with self.assertRaises(ValueError):
                a.execute_sql_witness(case,p,digest,
                    "SELECT COUNT(*) = 3 FROM sample",
                    "SELECT COUNT(*) = 3 FROM sample")

    def test_no_shortcuts_no_ddl_no_non_boolean_query(self):
        ctxt,p,digest=self._with_db()
        with ctxt:
            case=a.policy_input(self.sample["cases"][0])
            for invalid in ("UPDATE sample SET value = 2",
                            "SELECT 1; SELECT 2",
                            "PRAGMA table_info(sample)",
                            "SELECT value FROM sample",
                            "SELECT NULL FROM sample"):
                with self.assertRaises(ValueError):
                    a.execute_sql_witness(case,p,digest,invalid,
                        "SELECT COUNT(*) = 3 FROM sample")
            with self.assertRaises(ValueError):
                a.execute_sql_witness(dict(case,
                    annotated_label_evaluator_only="ENTAILED"),
                    p,digest,"SELECT COUNT(*) = 3 FROM sample",
                    "SELECT SUM(value) = 6 FROM sample")

    def test_original_source_reproduction_must_verify_git_blob(self):
        with TemporaryDirectory() as name:
            bad=Path(name)/"test-public.jsonl"
            bad.write_text('{"claim_id":1}\n',encoding="utf-8")
            with self.assertRaises(ValueError):
                a.source_reproduction(bad)
            self.assertEqual(a._source_git_blob_sha(b"abc"),
                             "f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")

    def test_sample_has_no_sql_tables_or_executed_result(self):
        for row in self.sample["cases"]:
            self.assertEqual(row["independent_source_count"],0)
            self.assertEqual(row["observed_evidence_records"],0)
            self.assertFalse(any(k in row for k in
                 ("sql","database_rows","computed_result","witness","source_table")))

if __name__=="__main__":
    unittest.main()
