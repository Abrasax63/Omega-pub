import base64
import copy
import gzip
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import runner as m
import ledger


def atom(pred,x="Ada"):
    return {"op":"atom","pred":pred,"args":[x]}

def neg(x):
    return {"op":"not","arg":x}

def sample():
    return {"premises":["No robots are pets.","Ada is a robot."],
            "conclusion":"Ada is a pet.","label":"False"}

def candidate():
    return {"clauses":[
        {"source_index":0,"quote":"No robots are pets.",
         "formula":{"op":"forall","var":"x","body":{"op":"implies",
            "if":atom("robot","x"),"then":neg(atom("pet","x"))}}},
        {"source_index":1,"quote":"Ada is a robot.","formula":atom("robot")}
    ],"goal":atom("pet"),
    "ideas":["Try an actual countermodel","Check whether robot implies non-pet"],
    "unparsed":[]}

def restore(path):
    source=m.BASE/"llm_proposals11"/"LEDGER_CHECKPOINT_2026-11-17.jsonl.gz.b64"
    content=gzip.decompress(base64.b64decode(source.read_text(encoding="utf-8")))
    path.write_bytes(content)
    return path


class MultiFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=m.load_frozen()

    def test_frozen_external_samples_unchanged(self):
        self.assertEqual(len(self.rows),6)
        self.assertEqual(m.old.prior.engine.blob_sha(m.INPUT.read_bytes()),m.FROZEN_BLOB)

    def test_json_schema_is_server_requested_not_implied(self):
        self.assertEqual(m.CANDIDATE_SCHEMA["properties"]["candidates"]["maxItems"],2)
        self.assertEqual(m.CANDIDATE_SCHEMA["type"],"object")
        self.assertEqual(m.MAX_TOKENS,1600)
        self.assertTrue(m.prompt_for(sample())[-1]["content"].startswith("{"))

    def test_two_independent_readings_preserved(self):
        first=candidate()
        second=copy.deepcopy(first)
        second["ideas"]=["Question whether all robots are nonpets"]
        second["clauses"][0]["formula"]={"op":"not","arg":atom("robot","x")}
        response={"content":json.dumps({"candidates":[first,second]}),
                  "finish_reason":"stop","usage":{"completion_tokens":120}}
        out=m.inspect(sample(),response,"SYNTH")
        self.assertTrue(out["json_valid"])
        self.assertEqual(out["candidate_count"],2)
        self.assertEqual(len(out["candidates"][0]["ideas"]),2)
        self.assertEqual(len(out["candidates"][1]["ideas"]),1)
        self.assertEqual(out["candidates"][0]["status"],"CONDITIONAL_FINITE_WITNESS")
        self.assertEqual(out["candidates"][1]["status"],"CANDIDATE_RETAINED_FOR_REVIEW")
        self.assertNotEqual(out["candidates"][0]["candidate_id"],out["candidates"][1]["candidate_id"])
        self.assertFalse(out["scientific_certification"])

    def test_exact_citation_and_actual_replayed_finite_witness(self):
        response={"content":json.dumps({"candidates":[candidate()]})}
        result=m.inspect(sample(),response,"SYNTH-2")
        self.assertEqual(result["source_citations_valid_candidates"],1)
        self.assertEqual(result["complete_formalizations"],1)
        self.assertEqual(result["finite_witnesses"],1)
        witness=result["candidates"][0]["oracle"]
        self.assertEqual(witness["status"],"FINITE_WITNESS_REPLAYED")
        self.assertTrue(witness["premises_replayed"])
        self.assertTrue(witness["goal_false_replayed"])
        self.assertFalse(result["candidates"][0]["semantic_fidelity_verified"])

    def test_forged_source_quote_does_not_delete_free_idea(self):
        c=candidate()
        c["clauses"][0]["quote"]="No unicorns are pets."
        out=m.inspect(sample(),{"content":json.dumps({"candidates":[c]})},"FAKE")
        self.assertEqual(out["complete_formalizations"],0)
        self.assertEqual(out["source_citations_valid_candidates"],0)
        self.assertEqual(out["candidates"][0]["ideas"],c["ideas"])
        self.assertTrue(any("QUOTE_NOT_EXACT" in z["errors"] for z in out["candidates"][0]["premises"]))

    def test_negation_removed_refused_before_oracle(self):
        c=candidate()
        c["clauses"][0]["formula"]={"op":"forall","var":"x","body":{"op":"implies",
            "if":atom("robot","x"),"then":atom("pet","x")}}
        x=m.inspect(sample(),{"content":json.dumps({"candidates":[c]})},"LOSS")
        self.assertEqual(x["complete_formalizations"],0)
        self.assertTrue(x["candidates"][0]["scope_alarms"])
        self.assertIsNone(x["candidates"][0]["oracle"])

    def test_or_and_quantifier_scope_are_visible(self):
        c=m.audit_candidate(
            {"premises":["All cats are either fast or calm."],"conclusion":"Ada is a cat."},
            {"clauses":[{"source_index":0,"quote":"All cats are either fast or calm.",
                         "formula":{"op":"forall","var":"x","body":{"op":"implies",
                            "if":atom("cat","x"),"then":atom("calm","x")}}}],
             "goal":atom("cat"),"ideas":["Explore both disjuncts"],"unparsed":[]},
            "TEST",0)
        self.assertFalse(c["structure_complete"])
        self.assertIn("SOURCE_DISJUNCTION_SCOPE_RISK",
                      [z["alarm"] for z in c["scope_alarms"]])
        self.assertEqual(c["ideas"],["Explore both disjuncts"])

    def test_incomplete_source_keeps_partial_formalization(self):
        c=candidate()
        c["clauses"].pop()
        c["unparsed"]=[1]
        out=m.inspect(sample(),{"content":json.dumps({"candidates":[c]})},"MISS")
        self.assertEqual(out["complete_formalizations"],0)
        self.assertEqual(out["candidates"][0]["source_coverage"],1)
        self.assertEqual(out["candidates"][0]["unparsed_indices"],[1])
        self.assertIsNone(out["candidates"][0]["oracle"])

    def test_invalid_json_and_limit_finish_are_logged(self):
        fail=m.inspect(sample(),{"content":'{"candidates":[','finish_reason':'length'},"TRUNC")
        self.assertFalse(fail["json_valid"])
        self.assertIsNotNone(fail["error"])
        self.assertEqual(fail["finish_reason"],"length")

    def test_excessive_count_schema_refused_client_side(self):
        c=candidate()
        with self.assertRaises(m.CandidateError):
            m.decode(json.dumps({"candidates":[c,c,c]}))

    def test_gold_and_official_fol_not_in_model_prompt(self):
        for row in self.rows:
            p=m.prompt_for(row)
            data=json.loads(p[-1]["content"])
            self.assertEqual(set(data),{"premises","question"})
            self.assertNotIn('"_FOL"',p[-1]["content"])
            self.assertNotIn('"label":',p[-1]["content"])
            self.assertEqual(data["question"],row["conclusion"])

    def test_memory_resumed_and_no_evidence_promotion(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=restore(Path(tmp)/"history.jsonl")
            def fake(messages):
                return {"content":json.dumps({"candidates":[candidate()]}),
                        "finish_reason":"stop","seconds":0.01,
                        "usage":{"completion_tokens":30}}
            doc=m.evaluate(self.rows,call=fake,ledger_path=p)
            self.assertEqual(doc["memory"]["events"],18)
            self.assertEqual(doc["new_scientific_discoveries_certified"],0)
            self.assertEqual(doc["local_model_calls_requested"],6)
            self.assertEqual(doc["paid_api_calls"],0)
            self.assertTrue(all(x["proposal"]["candidate_count"]==1 for x in doc["rows"]))
            self.assertFalse(any(x["proposal"]["scientific_certification"] for x in doc["rows"]))

    def test_checkout_memory_write_disallowed(self):
        with self.assertRaisesRegex(m.CandidateError,"OUTSIDE_REPO"):
            m.evaluate(self.rows,ledger_path=m.HERE/"memory.jsonl")

if __name__=="__main__":
    unittest.main()
