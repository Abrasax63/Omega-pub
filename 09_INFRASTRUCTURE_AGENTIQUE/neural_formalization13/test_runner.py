#!/usr/bin/env python3
import base64
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import runner as r
import ledger


def sample_case():
    return {"premises":["No robots are pets.","Ada is a robot."],
            "conclusion":"Ada is a pet.","label":"False"}


def valid_generation():
    return {"content":json.dumps({
        "clauses":[
            {"source_index":0,"quote":"No robots are pets.",
             "kind":"forall_disjoint","a":"robot","b":"pet"},
            {"source_index":1,"quote":"Ada is a robot.",
             "kind":"fact","individual":"Ada","predicate":"robot","negative":False}
        ],
        "goal":{"kind":"fact","individual":"Ada","predicate":"pet","negative":False},
        "notes":"Check whether a robotic pet model exists, not assume an answer."
    }),"seconds":0.01,"usage":{"completion_tokens":60}}


def checkpoint(path):
    source=r.CHECKPOINT.read_text(encoding="utf-8")
    content=gzip.decompress(base64.b64decode(source))
    assert r.sha_text(content.decode("utf-8")) == (
        "38864b20197b7b2c36f9a65fdffd263c85c4e0d48367a1780475c6cd5b3a23ea")
    path.write_bytes(content)
    return path


class NeuralFormalization13Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases=r.frozen_cases()

    def test_new_external_file_pinned(self):
        self.assertEqual(len(self.cases),6)
        self.assertEqual(r.engine.blob_sha(r.INPUT.read_bytes()),r.FROZEN_BLOB)
        self.assertEqual(r.engine.blob_sha(r.ENGINE_PATH.read_bytes()),r.ENGINE_BLOB)

    def test_prompt_does_not_expose_gold_or_formal_annotations(self):
        for row in self.cases:
            x=r.prompt_for(row)
            user=json.loads(x[-1]["content"])
            self.assertEqual(set(user),{"premises","question"})
            self.assertTrue(all(set(v)=={"source_index","text"}
                                for v in user["premises"]))
            self.assertNotIn("premises-FOL",x[-1]["content"])
            self.assertNotIn("conclusion-FOL",x[-1]["content"])
            self.assertNotIn('"label":',x[-1]["content"])

    def test_actual_finite_countermodel_from_machine_ast(self):
        result=r.inspect_generated(sample_case(),valid_generation())
        self.assertTrue(result["complete_translation"])
        self.assertTrue(result["valid_json"])
        self.assertTrue(result["source_quotes_valid"])
        self.assertEqual(result["status"],"FINITE_COUNTERMODEL_CONDITIONAL_TO_LLM_AST")
        self.assertTrue(result["finite_oracle"]["every_premise_replayed"])
        self.assertTrue(result["finite_oracle"]["goal_false_replayed"])
        self.assertFalse(result["scientific_claim_certified"])
        self.assertFalse(result["semantic_translation_verified"])

    def test_incomplete_logic_never_ignores_unformalized_sentence(self):
        data=json.loads(valid_generation()["content"])
        data["clauses"].pop()
        result=r.inspect_generated(sample_case(),{"content":json.dumps(data)})
        self.assertFalse(result["complete_translation"])
        self.assertIsNone(result["finite_oracle"])
        self.assertEqual(result["reason"],"UNFORMALIZED_SOURCE_OR_GOAL")

    def test_forged_quote_fails_closed(self):
        data=json.loads(valid_generation()["content"])
        data["clauses"][0]["quote"]="this is a fabricated quote"
        result=r.inspect_generated(sample_case(),{"content":json.dumps(data)})
        self.assertFalse(result["source_quotes_valid"])
        self.assertFalse(result["complete_translation"])
        self.assertIn("INVALID_GENERATED_FORMALIZATION",result["reason"])

    def test_untrusted_source_index_refused(self):
        data=json.loads(valid_generation()["content"])
        data["clauses"][0]["source_index"]=8
        result=r.inspect_generated(sample_case(),{"content":json.dumps(data)})
        self.assertFalse(result["complete_translation"])

    def test_wrong_semantics_remains_unverified(self):
        data=json.loads(valid_generation()["content"])
        data["clauses"][0]["a"]="chair"
        # Citation remains exact, but its formalization is semantically wrong.
        result=r.inspect_generated(sample_case(),{"content":json.dumps(data)})
        self.assertTrue(result["complete_translation"])
        self.assertFalse(result["semantic_translation_verified"])
        self.assertFalse(result["scientific_claim_certified"])

    def test_unparsable_json_never_claims_abstention_science(self):
        out=r.inspect_generated(sample_case(),{"content":"not JSON"})
        self.assertFalse(out["valid_json"])
        self.assertEqual(out["status"],"UNDETERMINED")
        self.assertFalse(out["scientific_claim_certified"])

    def test_wrong_clause_type_rejected_not_executed(self):
        data=json.loads(valid_generation()["content"])
        data["clauses"][1]["kind"]="call_shell"
        result=r.inspect_generated(sample_case(),{"content":json.dumps(data)})
        self.assertFalse(result["complete_translation"])
        self.assertIsNone(result["finite_oracle"])

    def test_no_silent_inference_from_partial_source(self):
        source=sample_case()
        source["premises"].append("The robot has an unreported battery issue.")
        result=r.inspect_generated(source,valid_generation())
        self.assertFalse(result["complete_translation"])
        self.assertIsNone(result["finite_oracle"])

    def test_existing_qwen_memory_resume_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"missing.jsonl"
            def mock(_):return {"content":'{"clauses":[],"goal":null}'}
            with self.assertRaisesRegex(r.CandidateError,"resume previously"):
                r.evaluate(self.cases,call=mock,ledger_path=p)

    def test_resume_memory_and_append_six_actual_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            file=checkpoint(Path(tmp)/"memory.jsonl")
            def mock(_):
                return {"content":'{"clauses":[],"goal":null,"notes":"outside safe grammar"}',
                        "seconds":0.0}
            result=r.evaluate(self.cases,call=mock,ledger_path=file)
            self.assertEqual(result["model_transport_succeeded"],6)
            self.assertEqual(result["valid_json"],6)
            self.assertEqual(result["complete_model_formalizations"],0)
            self.assertEqual(result["memory"]["events"],18)
            self.assertEqual(result["scientific_discoveries_certified"],0)
            self.assertEqual(result["paid_api_calls"],0)
            self.assertFalse(result["auto_promotion"])
            events,latest=ledger.replay(file.read_text(encoding="utf-8"))
            self.assertEqual(len(events),18)
            self.assertEqual(events[11]["event_hash"],
                "6cd253c378c38bf9be62b25c549cebbb85ebb552502b0dc5da3b3cb5a4225686")
            self.assertTrue(all(x["status"]=="PROPOSED" for x in events[12:]))

    def test_gold_is_irrelevant_to_same_model_candidates(self):
        a=r.inspect_generated(sample_case(),valid_generation())
        wrong=sample_case();wrong["label"]="True"
        b=r.inspect_generated(wrong,valid_generation())
        self.assertEqual(a,b)

    def test_unsupported_class_name_refused(self):
        data=json.loads(valid_generation()["content"])
        data["goal"]["predicate"]="robot; execute"
        result=r.inspect_generated(sample_case(),{"content":json.dumps(data)})
        self.assertFalse(result["complete_translation"])

if __name__=="__main__":
    unittest.main()
