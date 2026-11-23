"""Offline fail-closed regression for the preregistered REAL-03 experiment."""
import json
import unittest
from unittest.mock import patch
from tempfile import TemporaryDirectory

from omega_repair_real03 import (
    NODES_TO_TASKS, AXIOM_MAP, evaluate, parse_relation, feedback,
    initial_prompt, same_or_changed, run, SYSTEM
)

class Real03Contracts(unittest.TestCase):
    def test_frozen_four_new_tasks(self):
        self.assertEqual(len(NODES_TO_TASKS),4)
        self.assertEqual([t[1] for t in NODES_TO_TASKS],
                         ["partial_order","symmetric","transitive","antisymmetric"])
        self.assertEqual(len(set(x for t in NODES_TO_TASKS for x in t[2])),16)

    def test_missing_reflexive_vertex_detected_without_solver_edit(self):
        n=("p","q","r","s")
        raw=json.dumps({"edges":[["p","p"],["q","q"],
                                 ["p","q"],["q","p"]]})
        out=evaluate(raw,n,AXIOM_MAP["partial_order"])
        self.assertFalse(out["math_correct"])
        self.assertEqual(out["first_witness"]["axiom"],"reflexive")
        self.assertEqual(out["first_witness"]["witness"],["r","r"])

    def test_transitivity_and_antisymmetry_are_checked_exactly(self):
        n=("p","q","r","s")
        trans=evaluate('{"edges":[["p","q"],["q","r"]]}',
                       n,("transitive",))
        self.assertEqual(trans["first_witness"]["axiom"],"transitive")
        self.assertEqual(trans["first_witness"]["witness"],["p","q","r"])
        anti=evaluate('{"edges":[["p","q"],["q","p"]]}',
                      n,("antisymmetric",))
        self.assertEqual(anti["first_witness"]["axiom"],"antisymmetric")

    def test_format_violations_never_become_repair_opportunities(self):
        n=("p","q","r","s")
        for raw in ('bad_json','{"abstain":true}',
                    '{"edges":[["p","q"],["p","q"]]}',
                    '{"edges":[["p","x"],["q","p"]]}',
                    '{"edges":[["p","p"],["q","q"]]}'):
            out=evaluate(raw,n,("reflexive",))
            self.assertFalse(out["format_ok"])
            self.assertIsNone(out["math_correct"])

    def test_repair_arms_share_initial_candidate_no_solution_supplied(self):
        task=NODES_TO_TASKS[0]
        initial=evaluate('{"edges":[["p","q"],["q","r"]]}',
                         task[2],AXIOM_MAP[task[1]])
        witness=feedback(task,initial,"W")
        generic=feedback(task,initial,"G")
        self.assertIn("counterexample witness",witness)
        self.assertIn('["p","q"]',witness)
        self.assertIn("withheld",generic)
        self.assertNotIn("counterexample witness",generic)
        self.assertIn("No corrected edge set is supplied",witness)
        self.assertIn("No corrected edge set is supplied",generic)

    def test_edit_distance_counts_pair_changes_not_text_changes(self):
        n=("p","q","r","s")
        a=evaluate('{"edges":[["p","q"],["q","r"]]}',n,("transitive",))
        b=evaluate('{"edges":[["p","q"],["q","r"],["p","r"]]}',
                   n,("transitive",))
        self.assertEqual(same_or_changed(a,b),
                         {"changed":True,"edit_distance":1})

    def test_full_mocked_run_counts_and_no_causal_claim_without_controls(self):
        class ScriptedClient:
            def __init__(self,endpoint):
                self.calls=[]
                self.idx=0
            def __call__(self,messages,tokens):
                user=messages[-1]["content"]
                # The same intentionally malformed model-generated specimen
                # on every task, used ONLY in offline software tests.
                nodes=NODES_TO_TASKS[self.idx][2]
                if "Repair your own relation once" not in user:
                    n=nodes
                    raw=json.dumps({"edges":[[n[0],n[1]],[n[1],n[2]],
                                              [n[1],n[0]]]})
                elif "counterexample witness" in user:
                    n=nodes
                    target=NODES_TO_TASKS[self.idx][1]
                    edges = ([[x,x] for x in n]
                             +[[n[0],n[1]],[n[0],n[2]]]
                             if target=="partial_order" else
                             [[n[0],n[1]],[n[1],n[0]]]
                             if target=="symmetric" else
                             [[n[0],n[1]],[n[0],n[2]]])
                    raw=json.dumps({"edges":edges})
                else:
                    n=nodes
                    raw=json.dumps({"edges":[[n[0],n[1]],[n[1],n[2]],
                                              [n[1],n[0]]]})
                self.calls.append(messages)
                if "Repair your own relation once" in user and len(self.calls)%3==0:
                    self.idx+=1
                elif "Repair your own relation once" in user and len(self.calls)%3==2:
                    pass
                return {"text":raw,"usage":{"prompt_tokens":123,
                                  "completion_tokens":20},"time_s":.1}
        # Avoid real network tokenization and use a mocked equalizer.
        def fake_equalize(endpoint,prompts):
            return prompts,{"W":100,"G":100},True
        with TemporaryDirectory() as tmp:
            with patch("omega_repair_real03.RealClient",ScriptedClient), \
                 patch("omega_repair_real03.equalize",fake_equalize):
                out=run(tmp,"http://127.0.0.1:8080")
            self.assertEqual(out["model_calls"],12)
            self.assertEqual(out["counts"]["repair_opportunities"],4)
            self.assertEqual(out["counts"]["W_success"],4)
            self.assertEqual(out["counts"]["G_success"],0)
            self.assertTrue(out["criterion_met"])
            self.assertEqual(len(json.load(open(tmp+"/report.json"))["tasks"]),4)

if __name__=="__main__":
    unittest.main()
