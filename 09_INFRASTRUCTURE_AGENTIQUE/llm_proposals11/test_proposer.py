import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import ledger
import proposer as p


class LedgerMemoryTests(unittest.TestCase):
    def data(self):
        return {"source_sha256":"a"*64,"question_sha256":"b"*64,
                "raw_generation_sha256":"c"*64,"next_test":"Check an independently evaluated case"}

    def test_append_replay_and_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"ledger.jsonl"
            a=ledger.append(f,"candidate-alpha-01","PROPOSED",self.data())
            self.assertTrue(a["added"])
            again=ledger.append(f,"candidate-alpha-01","PROPOSED",self.data())
            self.assertFalse(again["added"])
            b=ledger.append(f,"candidate-alpha-01","UNDETERMINED",self.data())
            self.assertEqual(b["sequence"],2)
            c=ledger.append(f,"candidate-beta-001","REJECTED_PROVENANCE",self.data())
            self.assertEqual(c["sequence"],3)
            events,latest=ledger.replay(f.read_text(encoding="utf-8"))
            self.assertEqual(len(events),3)
            self.assertEqual(latest["candidate-alpha-01"]["status"],"UNDETERMINED")
            self.assertEqual(ledger.summary(f)["unique_candidates"],2)
            self.assertEqual(events[1]["previous_hash"],events[0]["event_hash"])

    def test_reject_science_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"mem.jsonl"
            with self.assertRaisesRegex(ledger.LedgerError,"cannot be promoted"):
                ledger.append(f,"candidate-0001","VERIFIED",self.data())
            self.assertFalse(f.exists())

    def test_reject_forged_event_and_replayed_or_removed_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"mem.jsonl"
            ledger.append(f,"candidate-0001","PROPOSED",self.data())
            ledger.append(f,"candidate-0002","PROPOSED",self.data())
            lines=f.read_text(encoding="utf-8").splitlines()
            a=json.loads(lines[0]);a["status"]="VERIFIED"
            bad=json.dumps(a)+"\n"+"\n".join(lines[1:])+"\n"
            with self.assertRaises(ledger.LedgerError):
                ledger.replay(bad)
            with self.assertRaises(ledger.LedgerError):
                ledger.replay(lines[1]+"\n")
            with self.assertRaises(ledger.LedgerError):
                ledger.replay(lines[0]+"\n"+lines[0]+"\n")

    def test_reject_provenance_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"mem.jsonl"
            ledger.append(f,"candidate-0001","PROPOSED",self.data())
            changed=dict(self.data(),source_sha256="d"*64)
            with self.assertRaises(ledger.LedgerError):
                ledger.append(f,"candidate-0001","UNDETERMINED",changed)

    def test_no_revive_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"mem.jsonl"
            ledger.append(f,"candidate-0001","REJECTED_PROVENANCE",self.data())
            with self.assertRaises(ledger.LedgerError):
                ledger.append(f,"candidate-0001","UNDETERMINED",self.data())

    def test_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            target=d/"real.jsonl";target.write_text("",encoding="utf-8")
            f=d/"linked.jsonl";f.symlink_to(target)
            with self.assertRaisesRegex(ledger.LedgerError,"symlink"):
                ledger.append(f,"candidate-0001","PROPOSED",self.data())


class NeuralProposalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=p.frozen_cases()

    def fake(self,messages):
        user=json.loads(messages[-1]["content"])
        quote=user["premises"][0]["text"][:max(6,min(35,len(user["premises"][0]["text"])))]
        data={"hypotheses":[{"premise_index":0,"quote":quote,
                             "idea":"Possible interpretation requires a stronger implication.",
                             "test":"Find a model satisfying the first premise but not the conclusion."}]}
        return {"content":json.dumps(data),"seconds":0.01,"usage":{"completion_tokens":42}}

    def test_frozen_external_sample(self):
        self.assertEqual(len(self.cases),6)
        self.assertEqual(p.git_blob(p.INPUT.read_bytes()),p.INPUT_BLOB)
        self.assertEqual(p.git_blob(p.PREV_EXPLORER.read_bytes()),p.PREV_EXPLORER_BLOB)

    def test_prompt_does_not_expose_labels_or_formal_gold(self):
        for row in self.cases:
            prompt=p.prompt_for(row)
            payload=json.loads(prompt[-1]["content"])
            self.assertEqual(set(payload),{"question","premises"})
            self.assertEqual(payload["question"],row["conclusion"])
            self.assertTrue(all(set(x)=={"premise_index","text"} for x in payload["premises"]))
            self.assertNotIn("premises-FOL",prompt[-1]["content"])
            self.assertNotIn("conclusion-FOL",prompt[-1]["content"])
            self.assertNotIn('"label":',prompt[-1]["content"])

    def test_generated_json_and_provenance(self):
        result=p.call_case(self.cases[0],61,call=self.fake)
        self.assertEqual(result["call_status"],"STRUCTURED_GENERATION")
        self.assertEqual(len(result["hypotheses"]),1)
        c=result["hypotheses"][0]
        self.assertEqual(c["status"],"PROPOSED")
        self.assertFalse(c["certified"])
        self.assertFalse(c["independent_oracle_executed"])
        self.assertEqual(c["scientific_verdict"],"UNDETERMINED")

    def test_forged_citation_rejected(self):
        q=self.cases[0]
        bad={"premise_index":0,"quote":"NEVER PRESENT IN SOURCE",
             "idea":"Interpretation requires a test","test":"Try a finite countermodel."}
        c=p.validate_model_candidate(bad,q,"FOLIO-061",0,"0"*64)
        self.assertEqual(c["status"],"REJECTED_PROVENANCE")
        self.assertIn("CITATION_NOT_EXACT",c["errors"])

    def test_unconstrained_scientific_idea_but_hard_transport_budget(self):
        q=self.cases[0]
        response=self.fake(p.prompt_for(q))["content"]
        self.assertEqual(len(p.decode_json(response)),1)
        with self.assertRaises(p.GeneratorError):
            p.decode_json('{"hypotheses":[{}, {}, {}]}')
        with self.assertRaises((ValueError,p.GeneratorError)):
            p.decode_json("Explanation before JSON")

    def test_transport_error_retained_not_model_abstention(self):
        def bad(_messages):
            raise OSError("simulated local server down")
        r=p.call_case(self.cases[0],61,call=bad)
        self.assertEqual(r["call_status"],"GENERATION_OR_TRANSPORT_FAILED")
        self.assertFalse(r["model_called"])

    def test_bad_json_separate_from_model_call_failure(self):
        def bad(_messages):
            return {"content": "not a json response","seconds":0.01}
        r=p.call_case(self.cases[0],61,call=bad)
        self.assertTrue(r["model_called"])
        self.assertEqual(r["call_status"],"INVALID_GENERATED_JSON")
        self.assertEqual(r["hypotheses"],[])

    def test_end_to_end_real_ledger_replay_and_idempotence(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"events.jsonl"
            report=p.evaluate(self.cases,call=self.fake,ledger_path=path)
            self.assertEqual(report["model_transport_success"],6)
            self.assertEqual(report["structured_generations"],6)
            self.assertEqual(report["candidates"],6)
            self.assertEqual(report["provenance_valid_candidates"],6)
            self.assertEqual(report["semantic_tests_executed"],0)
            self.assertEqual(report["verified_scientific_findings"],0)
            self.assertEqual(report["ledger"]["events"],6)
            first_hash=report["ledger"]["head_hash"]
            again=p.evaluate(self.cases,call=self.fake,ledger_path=path)
            self.assertEqual(again["ledger"]["events"],6)
            self.assertEqual(again["ledger"]["head_hash"],first_hash)
            self.assertEqual(len(ledger.replay(path.read_text())[0]),6)
            self.assertEqual(report["paid_api_calls"],0)

    def test_no_writes_to_repository_checkout(self):
        with self.assertRaisesRegex(p.GeneratorError,"outside checkout"):
            p.evaluate(self.cases,call=self.fake,ledger_path=p.HERE/"bad.jsonl")


if __name__=="__main__":
    unittest.main()
