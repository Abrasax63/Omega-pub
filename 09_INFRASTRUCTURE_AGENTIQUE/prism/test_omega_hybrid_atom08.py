"""Offline anti-leak and exact-oracle tests for OMEGA-ATOM-08."""
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

import omega_hybrid_atom08 as a


class FakeModel:
    def __init__(self):self.calls=[]
    def __call__(self,messages,max_tokens):
        self.calls.append(messages)
        question=messages[-1]["content"]
        raw=('{"violates":false}' if "three verified membership bits" in question else
             '{"xy":false,"yz":false,"xz":false}')
        return {"text":raw,"usage":{
            "prompt_tokens":len(question.split())+len(messages[0]["content"].split()),
            "completion_tokens":10},"time_s":0.02}


class AtomicTests(unittest.TestCase):
    def test_all_sealed_examples_reproducible(self):
        inp,oracle=a.make_manifest()
        self.assertEqual((inp,oracle),a.make_manifest())
        self.assertEqual(len(inp["graphs"]),12)
        self.assertEqual(len(inp["truth_table_queries"]),8)
        self.assertEqual(len(oracle["graph_answers"]),12)
        self.assertEqual(len(oracle["truth_table_answers"]),8)
        self.assertFalse(inp["answers_included"])
        self.assertNotIn('"violates"',json.dumps(inp["graphs"]))
        self.assertEqual(sum(v["violates"] for v in oracle["truth_table_answers"]),1)
        self.assertEqual({v["violates"] for v in oracle["graph_answers"]},{False,True})
        self.assertEqual(len({v["id"] for v in inp["graphs"]}),12)

    def test_exact_each_of_36_bit_memberships(self):
        inp,oracle=a.make_manifest()
        for case,ans in zip(inp["graphs"],oracle["graph_answers"]):
            self.assertEqual(case["id"],ans["id"])
            s={tuple(p) for p in case["edges"]}
            x,y,z=case["triple"]
            self.assertEqual(ans["bits"],
                {"xy":(x,y) in s,"yz":(y,z) in s,"xz":(x,z) in s})
            self.assertEqual(ans["violates"],a.violates(ans["bits"]))

    def test_all_eight_boolean_patterns_exhaustive(self):
        inp,oracle=a.make_manifest()
        self.assertEqual({tuple(x["bits"][k] for k in a.FIELDS)
                          for x in inp["truth_table_queries"]},
                         {tuple(a.bits(i)[k] for k in a.FIELDS) for i in range(8)})
        for q,ans in zip(inp["truth_table_queries"],oracle["truth_table_answers"]):
            self.assertEqual(ans["violates"],a.violates(q["bits"]))

    def test_list_and_matrix_encode_same_relation(self):
        inp,_=a.make_manifest()
        for case in inp["graphs"]:
            e={tuple(p) for p in case["edges"]}
            matrix=a.matrix_of(case)
            for i,x in enumerate(case["nodes"]):
                for j,y in enumerate(case["nodes"]):
                    self.assertEqual(matrix[i][j],int((x,y) in e))

    def test_different_representations_do_not_contain_oracle_bits(self):
        inp,_=a.make_manifest()
        for graph in inp["graphs"]:
            for arm in a.ARMS:
                s=a.prompt_for_graph(graph,arm)
                self.assertNotIn('"violates":',s)
                self.assertNotIn('"xy":true',s)
                self.assertNotIn('"xy":false',s)
                self.assertIn('"p',s)
                self.assertIn("xy,yz,xz",s)
        self.assertNotIn('"violates":',a.prompt_for_logic(inp["truth_table_queries"][0]))

    def test_strict_json_type_and_excess_field_rejection(self):
        self.assertIsNone(a.score_bits('{"xy":1,"yz":false,"xz":false}'))
        self.assertIsNone(a.score_bits('{"xy":false,"yz":false,"xz":false,"comment":"yes"}'))
        self.assertIsNone(a.score_bits('broken'))
        self.assertIsNone(a.score_logic('{"violates":"false"}'))
        self.assertIsNone(a.score_logic('{"violates":false,"explain":"none"}'))
        self.assertIsNone(a.score_logic('{"abstain":true}'))
        self.assertEqual(a.score_bits('{"xy":true,"yz":false,"xz":false}'),
                         {"xy":True,"yz":False,"xz":False})

    def test_single_atom_implication_is_not_vacuously_satisfied(self):
        self.assertTrue(a.violates({"xy":True,"yz":True,"xz":False}))
        self.assertFalse(a.violates({"xy":False,"yz":True,"xz":False}))
        self.assertFalse(a.violates({"xy":True,"yz":False,"xz":False}))
        self.assertFalse(a.violates({"xy":True,"yz":True,"xz":True}))

    def test_full_mock_execution_does_not_certify_model_knowledge(self):
        client=FakeModel()
        with tempfile.TemporaryDirectory() as td:
            result=a.run(Path(td),"offline",client=client)
            self.assertEqual(result["calls"],32)
            self.assertEqual(len(client.calls),32)
            self.assertEqual(result["status"],"FOUNDATIONAL_GATE_NOT_PASSED")
            self.assertEqual(result["metrics"]["LOGIC"]["correct"],7)
            self.assertFalse(result["metrics"]["LOGIC"]["positive_case_correct"])
            self.assertFalse(result["new_skill_learned"])
            self.assertFalse(result["reading_gate"])
            self.assertFalse(result["logic_gate"])
            self.assertFalse(result["model_weights_updated"])
            self.assertEqual(result["new_competences_certified"],0)
            self.assertEqual(len(json.loads((Path(td)/"model_inputs.json").read_text())["graphs"]),12)
            self.assertEqual(len(json.loads((Path(td)/"oracle_only.json").read_text())["graph_answers"]),12)

    def test_no_schema_permissiveness_for_malicious_edits(self):
        for raw in ('{"xy":[],"yz":false,"xz":false}',
                    '{"xy":"false","yz":false,"xz":false}',
                    '{"xy":false,"yz":false}',
                    '{"xy":false,"yz":false,"xz":false} extra'):
            self.assertIsNone(a.score_bits(raw))

if __name__=="__main__":
    unittest.main()
