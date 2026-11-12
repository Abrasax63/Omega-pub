"""OBS04: hostile tests for genuine paired logs, abstention and no gold leakage."""
import json
from pathlib import Path
import tempfile
import unittest
import p5_obs04_claimdb_real_disagreement as m

class ClaimDBRealMethodTests(unittest.TestCase):
    def fixture(self):
        labels=m.LABELS
        gold=[]
        sql=[]
        no=[]
        for i in range(1000):
            truth=labels[i%3]
            gold.append({"claim_id":i,"label":truth,"db_name":"database_"+str(i%10)})
            # Deterministic TEST fixture only, not real model results.
            a=truth if i%4 else labels[(i+1)%3]
            b=truth if i%7 else labels[(i+2)%3]
            sql.append({"claim_id":i,"verdict":b,"to_input_list":[
                {"type":"function_call","name":"execute_sql"},
                {"type":"function_call_output","output":"fake_fixture"}]})
            no.append({"claim_id":i,"verdict":a,"to_input_list":[]})
        return gold,sql,no

    def test_strict_read_and_sha_gate(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"mini.jsonl"
            p.write_text('{"claim_id":0,"verdict":"ENTAILED"}\n')
            with self.assertRaisesRegex(ValueError,"SHA256"):
                m.read_rows(p,"sql")
            rows,metadata=m.read_rows(p,"sql",verify_sha=False)
            self.assertEqual(len(rows),1)
            self.assertEqual(metadata["count"],1)
            p.write_text("version https://git-lfs.github.com/spec/v1\n")
            with self.assertRaisesRegex(ValueError,"LFS_POINTER"):
                m.read_rows(p,"sql",verify_sha=False)

    def test_duplicate_ids_and_invalid_labels_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"mini.jsonl"
            p.write_text('{"claim_id":7,"verdict":"ENTAILED"}\n'
                         '{"claim_id":7,"verdict":"REFUTES"}\n')
            with self.assertRaisesRegex(ValueError,"DUPLICATE_CLAIM_ID"):
                m.read_rows(p,"no_tools",verify_sha=False)
            p.write_text('{"claim_id":"7","verdict":"ENTAILED"}\n')
            with self.assertRaisesRegex(ValueError,"unjoinable"):
                m.read_rows(p,"no_tools",verify_sha=False)
        self.assertIsNone(m.label_strict("UNKNOWN"))
        self.assertIsNone(m.label_strict("ABSTAIN"))
        self.assertIsNone(m.label_strict("SUPPORTS"))
        self.assertEqual(m.label_strict("NOT ENOUGH INFO"),"NOT ENOUGH INFO")

    def test_join_permutation_is_invariant(self):
        g,s,n=self.fixture()
        left=m.evaluate(g,s,n)
        right=m.evaluate(g[::-1],s[::-1],n[::-1])
        self.assertEqual(left,right)
        self.assertEqual(left["valid_paired_verdicts"],1000)
        self.assertEqual(left["status"],m.STATUS)
        self.assertTrue(left["same_model_family_not_independent_provider"])
        self.assertTrue(left["gold_database_not_recomputed"])
        self.assertFalse(left["claims_text_redistributed"])
        self.assertGreater(left["outcome_counts"]["disagreements"],0)

    def test_missing_ids_never_fabricate_pairs(self):
        g,s,n=self.fixture()
        s=s[1:]
        report=m.evaluate(g,s,n)
        self.assertEqual(report["paired_ids"],999)
        self.assertEqual(report["missing_or_extra_ids"]["gold_without_sql"],1)
        self.assertEqual(report["status"],"INCOMPLETE_PAIRED_COVERAGE_PARTIAL")
        with self.assertRaisesRegex(ValueError,"UNJOINABLE"):
            m.evaluate(g,[{"claim_id":2000,"verdict":"ENTAILED"}],n)

    def test_technical_abstention_differs_from_gold_nei(self):
        g,s,n=self.fixture()
        x=m.evaluate(g,s,n)
        self.assertEqual(x["model_policies"]["reject_all"]["abstained"],1000)
        self.assertEqual(x["model_policies"]["reject_all"]["correct_published"],0)
        self.assertEqual(x["model_policies"]["sql_tools"]["abstained"],0)
        self.assertGreater(x["label_distribution"]["NOT ENOUGH INFO"],0)
        self.assertEqual(x["model_policies"]["sql_tools"],
                         x["model_policies"]["prefer_sql_when_disagree"])

    def test_ordinary_policies_are_gold_blind(self):
        g,s,n=self.fixture()
        a=m.evaluate(g,s,n)
        shifted=[dict(row,label=m.LABELS[(m.LABELS.index(row["label"])+1)%3])
                 for row in g]
        b=m.evaluate(shifted,s,n)
        for item1,item2 in zip(a["case_audit"],b["case_audit"]):
            self.assertEqual((item1["no_tools"],item1["sql_tools"],
                              item1["disagrees"]),
                             (item2["no_tools"],item2["sql_tools"],
                              item2["disagrees"]))
        self.assertEqual(a["model_policies"]["reject_all"],
                         b["model_policies"]["reject_all"])
        self.assertNotEqual(a["model_policies"]["sql_tools"]["correct_published"],
                            b["model_policies"]["sql_tools"]["correct_published"])

    def test_sql_tool_event_not_validated_evidence(self):
        r={"to_input_list":[{"type":"function_call"},
                            {"type":"function_call_output"}]}
        self.assertEqual(m.tool_events(r),{
            "logged_calls":1,"logged_outputs":1,"trace_available":True})
        self.assertEqual(m.tool_events({"to_input_list":[]})["logged_calls"],0)
        self.assertFalse(m.tool_events({})["trace_available"])
        self.assertTrue(m.evaluate(*self.fixture())[
            "sql_tool_event_is_not_verified_sql_correctness"])

    def test_unsupported_output_does_not_become_correct_verdict(self):
        g,s,n=self.fixture()
        s[0]["verdict"]="probably ENTAILED"
        r=m.evaluate(g,s,n)
        self.assertEqual(r["outcome_counts"]["invalid_or_missing_verdict"],1)
        self.assertEqual(r["valid_paired_verdicts"],999)
        self.assertIsNone(m.label_strict("probably ENTAILED"))

if __name__=="__main__":
    unittest.main()
