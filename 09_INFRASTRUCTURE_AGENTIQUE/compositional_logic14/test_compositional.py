#!/usr/bin/env python3
import base64
import copy
import gzip
import json
import tempfile
import unittest
from pathlib import Path

import finite_logic as l
import runner as r
import ledger


def atom(name,*terms):
    return {"op":"atom","pred":name,"args":list(terms)}

def neg(a):
    return {"op":"not","arg":a}

def every(body,var="x"):
    return {"op":"forall","var":var,"body":body}

def some(body,var="x"):
    return {"op":"exists","var":var,"body":body}

def imply(a,b):
    return {"op":"implies","if":a,"then":b}

def conj(*items):
    return {"op":"and","args":list(items)}

def disj(*items):
    return {"op":"or","args":list(items)}

def sample():
    return {
        "premises":["Every robot is metal or plastic.",
                    "Ada is a robot.",
                    "No robots are animals."],
        "conclusion":"Ada is an animal.",
        "label":"False",
    }

def mock_output():
    source=sample()
    return {"content":json.dumps({
        "clauses":[
            {"source_index":0,"quote":source["premises"][0],"formula":
             every(imply(atom("robot","x"),disj(atom("metal","x"),atom("plastic","x"))))},
            {"source_index":1,"quote":source["premises"][1],"formula":atom("robot","Ada")},
            {"source_index":2,"quote":source["premises"][2],"formula":
             every(imply(atom("robot","x"),neg(atom("animal","x"))))}
        ],
        "goal":atom("animal","Ada"),
        "ideas":["Check whether the disjunction leaves room for a countermodel.",
                 "Look for a robot that is not an animal."],
        "unparsed":[],
    }),"seconds":0.01,"usage":{"completion_tokens":120}}

def checkpoint(path):
    raw=gzip.decompress(base64.b64decode(r.prior.CHECKPOINT.read_text(encoding="utf-8")))
    assert r.sha_text(raw.decode())=="38864b20197b7b2c36f9a65fdffd263c85c4e0d48367a1780475c6cd5b3a23ea"
    path.write_bytes(raw)
    return path

class CompositionalLogic14Tests(unittest.TestCase):

    def test_logical_and_or_not_and_quantifiers_real_countermodel(self):
        result=r.inspect_model(sample(),mock_output(),"SYNTH")
        self.assertEqual(result["decode_status"],"JSON_PARSED")
        self.assertTrue(result["complete_translation"])
        self.assertTrue(result["source_citations_valid"])
        self.assertEqual(result["status"],"CONDITIONAL_FINITE_WITNESS")
        oracle=result["oracle"]
        self.assertEqual(oracle["status"],"FINITE_WITNESS_REPLAYED")
        self.assertTrue(oracle["premises_replayed"] and oracle["goal_false_replayed"])
        self.assertEqual(len(result["free_ideas"]),2)
        self.assertFalse(result["scientific_result_certified"])

    def test_two_distinct_interpreters_agree_for_all_small_boolean_formulas(self):
        cases=[
            neg(atom("pet","Ted")),
            conj(atom("pet","Ted"),atom("cow","Ted")),
            disj(atom("pet","Ted"),atom("cow","Ted")),
            imply(atom("pet","Ted"),atom("cow","Ted")),
            every(imply(atom("pet","x"),atom("cow","x"))),
            some(conj(atom("pet","x"),atom("cow","x"))),
            every(some(atom("loves","x","y"),"y"),"x"),
            neg(some(atom("loves","x","x"),"x")),
        ]
        universe=["Ted","Other"]
        ground_atoms=[("pet",(p,)) for p in universe]+[("cow",(p,)) for p in universe]+[
            ("loves",(a,b)) for a in universe for b in universe]
        import itertools
        for values in itertools.product((False,True),repeat=len(ground_atoms)):
            assignment=dict(zip(ground_atoms,values))
            true_atoms={k for k,v in assignment.items() if v}
            for formula in cases:
                self.assertEqual(l.evaluate(formula,assignment,universe),
                                 l.verify_independently(formula,true_atoms,universe))

    def test_binary_relation_with_nested_quantification(self):
        rule=every(some(atom("likes","x","y"),"y"),"x")
        goal=every(atom("likes","x","x"),"x")
        proof=l.finite_counterexample([rule],goal)
        self.assertEqual(proof["status"],"FINITE_WITNESS_REPLAYED")
        self.assertTrue(proof["goal_false_replayed"])
        self.assertGreaterEqual(len(proof["domain"]),2)

    def test_quantifier_scope_and_predicate_arity_rejected(self):
        with self.assertRaisesRegex(l.LogicError,"FREE_VARIABLE"):
            l.validate(atom("pet","x"))
        with self.assertRaisesRegex(l.LogicError,"ARITY_MISMATCH"):
            meta={"predicates":{},"constants":set(),"nodes":0}
            l.validate(atom("pet","Ted"),metadata=meta)
            l.validate(atom("pet","Ted","Ada"),metadata=meta)
        with self.assertRaisesRegex(l.LogicError,"SHADOWED"):
            l.validate(every(every(atom("cat","x"),"x"),"x"))

    def test_source_quotes_bad_but_ideas_are_not_discarded(self):
        data=json.loads(mock_output()["content"])
        data["clauses"][0]["quote"]="unrelated synthetic evidence"
        out=r.inspect_model(sample(),{"content":json.dumps(data)},"SYNTH")
        self.assertEqual(out["status"],"UNTRUSTED_PROPOSAL_NOT_EXECUTABLE")
        self.assertEqual(len(out["free_ideas"]),2)
        self.assertFalse(out["complete_translation"])
        self.assertFalse(out["scientific_result_certified"])

    def test_missing_premise_never_silently_omitted(self):
        data=json.loads(mock_output()["content"])
        data["clauses"].pop()
        out=r.inspect_model(sample(),{"content":json.dumps(data)},"SYNTH")
        self.assertEqual(out["status"],"UNFORMALIZED_OR_TRUNCATED_BUT_IDEAS_PRESERVED")
        self.assertEqual(out["structured_coverage"],2)
        self.assertIsNone(out["oracle"])

    def test_semantic_fidelity_disagreement_is_alarm_not_certification(self):
        data=json.loads(mock_output()["content"])
        data["clauses"][0]["formula"]=every(
            imply(atom("robot","x"),atom("metal","x")))
        out=r.inspect_model(sample(),{"content":json.dumps(data)},"SYNTH")
        self.assertTrue(out["complete_translation"])
        self.assertGreater(len(out["surface_semantic_alarms"]),0)
        self.assertFalse(out["semantic_fidelity_verified"])

    def test_nonstandard_relations_do_not_execute_arbitrary_code(self):
        for malicious in [{"op":"eval","expr":"open('/etc/passwd').read()"},
                          {"op":"atom","pred":"pet();os.system","args":["x"]},
                          {"op":"atom","pred":"pet","args":["unbound_x"]}]:
            with self.assertRaises(l.LogicError):
                l.validate(malicious)

    def test_no_countermodel_in_bound_does_not_certify(self):
        x=atom("cat","Ada")
        result=l.finite_counterexample([x],x)
        self.assertEqual(result["status"],"UNDETERMINED")
        self.assertEqual(result["reason"],"NO_COUNTEREXAMPLE_WITHIN_FINITE_BOUND")
        self.assertFalse(result["scientific_certification"])

    def test_inconsistent_claims_not_promoted(self):
        x=atom("cat","Ada")
        c=l.finite_counterexample([x,neg(x)],x)
        self.assertEqual(c["status"],"UNDETERMINED")
        self.assertEqual(c["models_satisfying_premises_seen"],0)

    def test_frozen_new_external_sample(self):
        rows=r.load_sample()
        self.assertEqual(len(rows),6)
        self.assertEqual(r.prior.engine.blob_sha(r.INPUT.read_bytes()),r.SAMPLE_BLOB)
        self.assertTrue(all("premises" in x and "conclusion" in x for x in rows))

    def test_no_gold_or_fol_annotations_exposed_to_qwen(self):
        for row in r.load_sample():
            prompt=r.prompt_for(row)
            user=json.loads(prompt[1]["content"])
            self.assertEqual(set(user),{"premises","question"})
            self.assertNotIn('"label"',prompt[1]["content"])
            self.assertNotIn("premises-FOL",prompt[1]["content"])
            self.assertNotIn("conclusion-FOL",prompt[1]["content"])

    def test_resume_real_checkpoint_and_add_six_unverified_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            journal=checkpoint(Path(tmp)/"hypotheses.jsonl")
            def fake(_):
                return {"content":'{"clauses":[],"goal":null,"ideas":["Maybe related","Try a counterexample"]}',
                        "seconds":0.0}
            report=r.evaluate(r.load_sample(),call=fake,ledger_path=journal)
            self.assertEqual(report["cases"],6)
            self.assertEqual(report["transport_successes"],6)
            self.assertEqual(report["json_decoded"],6)
            self.assertEqual(report["free_ideas_preserved"],12)
            self.assertEqual(report["complete_translations"],0)
            self.assertEqual(report["scientific_discoveries_certified"],0)
            self.assertEqual(report["memory"]["events"],18)
            self.assertTrue(report["predictions_sha256_before_gold"])
            self.assertFalse(report["auto_promotion"])
            entries,_=ledger.replay(journal.read_text())
            self.assertEqual(entries[11]["event_hash"],
              "6cd253c378c38bf9be62b25c549cebbb85ebb552502b0dc5da3b3cb5a4225686")

    def test_cannot_write_memory_to_repo(self):
        with self.assertRaisesRegex(r.RunnerError,"outside repo"):
            r.evaluate(r.load_sample(),call=mock_output,ledger_path=r.HERE/"forbidden.jsonl")

if __name__=="__main__":
    unittest.main()
