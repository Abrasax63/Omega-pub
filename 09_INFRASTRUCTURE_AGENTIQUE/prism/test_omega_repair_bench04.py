"""Offline regression for the frozen OMEGA-REPAIR-BENCH-04 comparison."""
import json
import unittest
from tempfile import TemporaryDirectory
from unittest.mock import patch

from omega_repair_bench04 import (
    TASKS, ARMS, ORDERS, audit, parse_edges, all_obligations,
    minimal_exact_repair, feedback, first_prompt, repaired_from, run,
)

class Bench04Tests(unittest.TestCase):
    def test_frozen_new_holdout_and_balanced_order(self):
        self.assertEqual(len(TASKS),6)
        self.assertEqual(len(ORDERS),6)
        self.assertEqual({tuple(v) for v in ORDERS},set(__import__("itertools").permutations(ARMS)))
        self.assertEqual(len({x for t in TASKS for x in t[2]}),24)
        self.assertEqual([t[1] for t in TASKS],
                          ["equivalence","partial_order","preorder",
                           "symmetric","transitive","antisymmetric"])

    def test_oracle_all_reflexive_failures_and_no_silent_accept(self):
        task=TASKS[1]
        raw=json.dumps({"edges":[["b1","b2"],["b2","b3"]]})
        z=audit(raw,task)
        self.assertEqual(len([v for v in z["violations"]
                              if v["axiom"]=="reflexive"]),4)
        self.assertIn({"axiom":"transitive","witness":["b1","b2","b3"]},
                      z["violations"])
        self.assertFalse(z["correct"])

    def test_transitive_complete_obligations_not_just_one_witness(self):
        task=TASKS[4]
        raw=json.dumps({"edges":[["j1","j2"],["j2","j3"],["j3","j4"]]})
        z=audit(raw,task)
        self.assertIn({"axiom":"transitive","witness":["j1","j2","j3"]},
                      z["violations"])
        self.assertIn({"axiom":"transitive","witness":["j2","j3","j4"]},
                      z["violations"])
        self.assertGreaterEqual(len(z["violations"]),2)
        allfeed=feedback("A",z,[])
        onefeed=feedback("S",z,[])
        genfeed=feedback("G",z,[])
        self.assertIn("j2",allfeed)
        self.assertIn("j3",onefeed)
        self.assertNotIn('"witness"',genfeed)

    def test_strict_parsing_and_different_vertex_names(self):
        nodes=TASKS[0][2]
        for bad in ["not a JSON", "{}", '{"edges":[["a1","a2"]]}',
                    '{"edges":[["a1","a2"],["a1","a2"]]}',
                    '{"edges":[["a1","a2"],["x","a2"]]}',
                    '{"edges":[["a1","a2"],["a2","a1"]],"extra":1}']:
            self.assertIsNone(parse_edges(bad,nodes)[0])
        good='{"edges":[["a1","a2"],["a2","a1"]]}'
        self.assertIsNotNone(parse_edges(good,nodes)[0])

    def test_exact_solver_minimum_edits(self):
        t=TASKS[5]
        initial=audit(json.dumps({"edges":[["t1","t2"],["t2","t1"],
                                          ["t3","t4"],["t4","t3"]]}),t)
        res=minimal_exact_repair(initial,t)
        self.assertTrue(res["verified"])
        self.assertEqual(res["edits"],2)
        end=audit(json.dumps({"edges":res["result_edges"]}),t)
        self.assertTrue(end["correct"])

    def test_paired_run_with_faked_language_model_never_confuses_success(self):
        class FakeClient:
            def __init__(self,endpoint):
                self.calls=[]
            def __call__(self,messages,tokens):
                prompt=messages[-1]["content"]
                task=next(t for t in TASKS if
                          ("EXACT universe "+json.dumps(list(t[2]),separators=(",",":")))
                              in prompt)
                nodes=task[2]
                initial=not "Return your corrected relation now." in prompt
                if initial:
                    edges=[[nodes[0],nodes[1]],[nodes[1],nodes[0]],
                           [nodes[2],nodes[3]],[nodes[3],nodes[2]]]
                elif "All current exact counterexamples" in prompt:
                    if task[1]=="equivalence":
                        edges=[[x,x] for x in nodes]+[
                            [nodes[0],nodes[1]],[nodes[1],nodes[0]]]
                    elif task[1] in ("partial_order","preorder"):
                        edges=[[x,x] for x in nodes]+[
                            [nodes[0],nodes[1]],[nodes[0],nodes[2]]]
                    elif task[1]=="symmetric":
                        edges=[[nodes[0],nodes[1]],[nodes[1],nodes[0]]]
                    else:
                        edges=[[nodes[0],nodes[1]],[nodes[0],nodes[2]]]
                else:
                    edges=[[nodes[0],nodes[1]],[nodes[1],nodes[0]],
                           [nodes[2],nodes[3]],[nodes[3],nodes[2]]]
                self.calls.append({"messages":messages})
                return {"text":json.dumps({"edges":edges}),
                        "usage":{"prompt_tokens":100,"completion_tokens":30},
                        "time_s":.01}
        def fake_equalize(endpoint,inputs):
            return inputs,{k:100 for k in inputs},True
        with TemporaryDirectory() as td:
            with patch("omega_repair_bench04.RealClient",FakeClient), \
                 patch("omega_repair_bench04.equalize",fake_equalize):
                z=run(td,"http://fake")
            self.assertEqual(z["stage"],"POINTWISE_GLOBAL_FEEDBACK_GAIN")
            self.assertEqual(z["metrics"]["eligible_errors"],5)
            self.assertEqual(z["metrics"]["G"]["success_by_2"],0)
            self.assertEqual(z["metrics"]["S"]["success_by_2"],0)
            self.assertEqual(z["metrics"]["A"]["success_by_2"],5)
            self.assertTrue(z["registered_gain"])
            self.assertLessEqual(z["model_calls"],42)
            self.assertEqual(json.load(open(td+"/report.json"))["stage"],
                             z["stage"])

if __name__=="__main__":
    unittest.main()
