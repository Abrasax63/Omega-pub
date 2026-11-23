"""Offline contract tests for TRANSFER-05; no model download, Web or hidden key leak."""
from pathlib import Path
import json
import tempfile
import unittest

from concept_abstraction_lab import check_axioms
import omega_hybrid_transfer05 as m


class FakeClient:
    def __init__(self):
        self.calls=[]
    def __call__(self,messages,max_tokens):
        self.calls.append({"messages":messages,"max_tokens":max_tokens})
        prompt=messages[-1]["content"]
        raw = ('{"rule":"Always verify every pair of consecutive edges for a required composite."}'
               if "Formulate one transferable" in prompt else
               '{"holds":true,"failed_axioms":[]}')
        return {"text":raw,"usage":{"prompt_tokens":len(
            (m.COMMON_SYSTEM+"\n"+prompt).split()),"completion_tokens":25},
            "time_s":0.05}


class Transfer05Tests(unittest.TestCase):
    def test_frozen_manifest_is_deterministic_and_exactly_balanced(self):
        q,a=m.make_manifest()
        self.assertEqual((q,a),m.make_manifest())
        self.assertEqual(len(q["cases"]),8)
        self.assertEqual(len(a["answers"]),8)
        self.assertEqual(sum(x["holds"] for x in a["answers"]),4)
        self.assertEqual(len(set(x["id"] for x in q["cases"])),8)
        self.assertEqual(len(set(m.orbit(frozenset(map(tuple,x["edges"])))
                                 for x in q["cases"])),8)
        self.assertTrue(q["answers_excluded"])
        self.assertNotIn("oracle_holds",json.dumps(q))
        self.assertNotIn("witnesses",json.dumps(q))
        for entry in q["cases"]:
            self.assertEqual(entry["nodes"],list(m.NODES))
            self.assertTrue(all(p[0]!=p[1] for p in entry["edges"]
                  if p[0]!=p[1]))
            exact=check_axioms(m.NODES,frozenset(map(tuple,entry["edges"])))
            self.assertTrue(exact["reflexive"]["holds"])
            self.assertTrue(exact["symmetric"]["holds"])

    def test_all_negative_cases_differ_only_in_transitivity(self):
        q,a=m.make_manifest()
        for x in a["answers"]:
            self.assertTrue(x["holds"] or x["failed_axioms"]==["transitive"])

    def test_witness_not_leaked_to_generic_training_arm(self):
        g=m.training_prompt("G")
        w=m.training_prompt("W")
        self.assertIn("reason",g)
        self.assertNotIn("aRb AND bRc",g)
        self.assertIn("aRb AND bRc",w)
        self.assertIn("edge a->c is missing",w)
        self.assertNotEqual(g,w)

    def test_wrong_equivalence_boolean_is_counted(self):
        actual={"holds":False,"failed_axioms":["transitive"]}
        r=m.parse_answer('{"holds":true,"failed_axioms":[]}',actual)
        self.assertFalse(r["boolean_correct"])
        self.assertFalse(r["full_axioms_correct"])

    def test_right_boolean_wrong_axioms_rejected_as_full_success(self):
        actual={"holds":False,"failed_axioms":["transitive"]}
        r=m.parse_answer('{"holds":false,"failed_axioms":["symmetric"]}',actual)
        self.assertTrue(r["boolean_correct"])
        self.assertFalse(r["full_axioms_correct"])

    def test_invalid_predictions_never_count(self):
        exact={"holds":True,"failed_axioms":[]}
        for raw in ('{"abstain":true}',"not json",
                    '{"holds":true,"failed_axioms":["transitive"]}',
                    '{"holds":true,"failed_axioms":[],"proof":true}',
                    '{"holds":"true","failed_axioms":[]}'):
            self.assertFalse(m.parse_answer(raw,exact)["full_axioms_correct"])

    def test_rule_parser_fail_closed(self):
        self.assertEqual(m.parse_lesson('{"abstain":true}')[1],"ABSTAIN")
        self.assertEqual(m.parse_lesson('{"rule":42}')[1],"INVALID_LESSON")
        self.assertEqual(m.parse_lesson('{"rule":"short"}')[1],"VALID_LESSON")
        self.assertEqual(m.parse_lesson('{"rule":"ok","proof":true}')[1],"INVALID_LESSON")

    def test_same_model_three_arms_and_two_train_calls(self):
        client=FakeClient()
        with tempfile.TemporaryDirectory() as td:
            r=m.run(Path(td),"offline",injected_client=client,
                    token_counter=lambda x:len(x.split()))
            self.assertEqual(r["stage"],"PRE_REGISTERED_GAIN_NOT_OBSERVED")
            self.assertEqual(r["train_calls"],2)
            self.assertEqual(r["eval_calls"],24)
            self.assertEqual(r["calls"],26)
            self.assertEqual(len(client.calls),26)
            self.assertFalse(r["model_weights_modified"])
            self.assertEqual(r["certified_new_competences"],0)
            self.assertFalse(r["results"]["registered_gain_observed"])
            self.assertTrue(r["results"]["actual_prompts_balanced"])
            self.assertEqual([r["results"]["stats"][x]["full_axioms_correct"]
                              for x in m.ARMS],[4,4,4])
            public=json.loads((Path(td)/"model_inputs.json").read_text())
            secret=json.loads((Path(td)/"oracle_only.json").read_text())
            self.assertNotIn("failed_axioms",json.dumps(public))
            self.assertIn("failed_axioms",json.dumps(secret))
            self.assertEqual(len(r["tasks"]),8)
            # Neither oracle answers nor correctness labels go to the model.
            for c in client.calls:
                content=c["messages"][-1]["content"]
                self.assertNotIn('"oracle_holds"',content)
                self.assertNotIn('"witnesses"',content)
                self.assertNotIn('"mask"',content)
                self.assertEqual(c["max_tokens"],260)

    def test_budget_overrun_rejects_causal_comparison(self):
        class UnequalClient(FakeClient):
            def __call__(self,messages,max_tokens):
                r=super().__call__(messages,max_tokens)
                if len(self.calls)>2 and "Previous self-generated" in messages[-1]["content"]:
                    r["usage"]["prompt_tokens"]=1000
                return r
        c=UnequalClient()
        with tempfile.TemporaryDirectory() as td:
            r=m.run(Path(td),"offline",injected_client=c,
                    token_counter=lambda x:len(x.split()))
            self.assertEqual(r["stage"],"INDETERMINATE_BUDGETS")
            self.assertFalse(r["results"]["registered_gain_observed"])


if __name__=="__main__":
    unittest.main()
