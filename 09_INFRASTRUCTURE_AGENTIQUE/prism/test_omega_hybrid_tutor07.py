"""Offline checks of OMEGA-TUTOR-07. Models in these tests are FAKE.

The real model can receive only training cases and unlabeled holdout questions.
All truth and certificate validity is computed outside its messages.
"""
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import tempfile
import unittest

from concept_abstraction_lab import check_axioms
import omega_hybrid_tutor07 as t


class FakeModel:
    def __init__(self,huge=False):
        self.calls=[]
        self.huge=huge
    def __call__(self,messages,max_tokens):
        self.calls.append(messages)
        prompt=messages[-1]["content"]
        if "Infer a general procedure" in prompt:
            raw='{"rule":"For a negative case check xy,yz,xz. For a positive case compare every edge to a complete partition."}'
        else:
            raw='{"holds":false,"failed_axioms":["transitive"],"certificate":{"kind":"missing_transitive_edge","triple":["a","b","c"],"premises":{"xy":true,"yz":true,"xz":false}}}'
        n=len((t.SYSTEM+"\n"+prompt).split())
        if self.huge and "A note you composed" in prompt:
            n*=3
        return {"text":raw,"usage":{"prompt_tokens":n,"completion_tokens":34},
                "time_s":.02}


class TeacherTests(unittest.TestCase):
    def test_holdout_is_sealed_balanced_deterministic_and_nonisomorphic(self):
        q,a=t.make_holdout()
        self.assertEqual((q,a),t.make_holdout())
        self.assertEqual(len(q["questions"]),len(a["answers"]))
        self.assertEqual(len(q["questions"]),8)
        self.assertEqual(sum(x["holds"] for x in a["answers"]),4)
        self.assertEqual(len(set(t.iso_key(t.NODES,frozenset(map(tuple,x["edges"])))
                   for x in q["questions"])),8)
        self.assertNotIn("failed_axioms",json.dumps(q))
        self.assertNotIn("oracle_witnesses",json.dumps(q))
        self.assertNotIn("holds",json.dumps(q))
        for row in q["questions"]:
            self.assertEqual(row["nodes"],list(t.NODES))
            graph=frozenset(map(tuple,row["edges"]))
            self.assertTrue(all((x,x) in graph for x in t.NODES))
            self.assertTrue(all((y,x) in graph for x,y in graph))
            self.assertEqual(t.independent_oracle(t.NODES,graph),
                             t.truth_oracle(t.NODES,graph)["holds"])

    def test_two_exact_oracles_agree_on_1024_distinct_six_node_graphs(self):
        pairs=list(combinations(t.NODES,2))
        for mask in range(1024):
            chosen=[e for i,e in enumerate(pairs) if mask & (1<<i)]
            rel=t.graph(t.NODES,chosen)
            self.assertEqual(t.independent_oracle(t.NODES,rel),
                             t.truth_oracle(t.NODES,rel)["holds"])

    def test_training_is_four_node_and_includes_proof_and_refutation(self):
        cases=t.make_training()
        self.assertEqual(len(cases),2)
        self.assertTrue(all(c["nodes"]==list(t.TRAIN_NODES) for c in cases))
        self.assertFalse(t.truth_oracle(t.TRAIN_NODES,
              frozenset(map(tuple,cases[0]["edges"])))["holds"])
        self.assertTrue(t.truth_oracle(t.TRAIN_NODES,
              frozenset(map(tuple,cases[1]["edges"])))["holds"])

    def test_teacher_negative_feedback_checks_three_atomic_premises(self):
        sample=t.make_training()[0]
        feedback=json.loads(t.teacher_feedback(sample,'{"abstain":true}',"T"))
        evidence=feedback["negative_certificate"]
        self.assertEqual(evidence["premises"],
                         {"xy":True,"yz":True,"xz":False})
        self.assertTrue(t.check_certificate(t.TRAIN_NODES,
          frozenset(map(tuple,sample["edges"])),False,evidence)[0])

    def test_teacher_positive_feedback_has_exact_partition(self):
        case=t.make_training()[1]
        report=json.loads(t.teacher_feedback(case,"{}","T"))
        cert=report["positive_certificate"]
        self.assertTrue(t.check_certificate(t.TRAIN_NODES,
          frozenset(map(tuple,case["edges"])),True,cert)[0])

    def test_generic_feedback_hides_ground_truth(self):
        case=t.make_training()[0]
        feedback=t.teacher_feedback(case,'{"abstain":true}',"G")
        self.assertNotIn("ground_truth",feedback)
        self.assertNotIn("triple",feedback)
        self.assertTrue(feedback.endswith("withheld."))

    def test_wrong_atomic_bits_and_wrong_partition_never_pass(self):
        neg=t.make_training()[0]
        edge=frozenset(map(tuple,neg["edges"]))
        triple=t.exact_counterexample(t.TRAIN_NODES,edge)
        correct={"kind":"missing_transitive_edge","triple":triple,
                 "premises":{"xy":True,"yz":True,"xz":False}}
        self.assertTrue(t.check_certificate(t.TRAIN_NODES,edge,False,correct)[0])
        flipped={**correct,"premises":{"xy":True,"yz":False,"xz":False}}
        self.assertEqual(t.check_certificate(t.TRAIN_NODES,edge,False,flipped),
                         (False,False))
        pos=t.make_training()[1]
        self.assertFalse(t.check_certificate(t.TRAIN_NODES,
          frozenset(map(tuple,pos["edges"])),True,
          {"kind":"partition","blocks":[["a","b","c","d"]]} )[0])

    def test_parse_prediction_strict_contract_and_abstention(self):
        sample=t.make_training()[0]
        nodes=tuple(sample["nodes"]);edges=frozenset(map(tuple,sample["edges"]))
        cases=['{"abstain":true}',"not-json",
            '{"holds":false,"failed_axioms":[],"certificate":{}}',
            '{"holds":true,"failed_axioms":[],"certificate":{},"magic":true}',
            '{"holds":"false","failed_axioms":["transitive"],"certificate":{}}']
        for raw in cases:
            self.assertFalse(t.score_raw(raw,nodes,edges)["fully_certified"])
        self.assertEqual(t.score_raw('{"abstain":true}',nodes,edges)["status"],"ABSTAIN")

    def test_mock_full_pipeline_counts_calls_and_preserves_no_certification(self):
        model=FakeModel()
        with tempfile.TemporaryDirectory() as d:
            r=t.run(Path(d),"offline",client=model,
                    token_counter=lambda text:len(text.split()))
            self.assertEqual(r["train_calls"],4)
            self.assertEqual(r["note_calls"],2)
            self.assertEqual(r["evaluation_calls"],24)
            self.assertEqual(len(model.calls),30)
            self.assertEqual(r["status"],"REGISTERED_CONTEXT_GAIN_NOT_OBSERVED")
            self.assertTrue(r["actual_eval_prompts_balanced"])
            self.assertFalse(r["model_weights_updated"])
            self.assertFalse(r["durable_skill_proven"])
            self.assertEqual(r["new_competences_certified"],0)
            q=json.loads((Path(d)/"model_inputs.json").read_text())
            a=json.loads((Path(d)/"oracle_only.json").read_text())
            self.assertEqual(len(q["questions"]),8)
            self.assertEqual(len(a["answers"]),8)
            for call in model.calls:
                text=call[-1]["content"]
                self.assertNotIn("oracle_witnesses",text)
                self.assertNotIn('"has_labels":true',text)
                if "Infer a general procedure" in text:
                    # Regression for the control contamination discovered by
                    # post-hoc inspection of the first REAL TUTOR-07 run.
                    self.assertNotIn("TRAIN_NEG",text)
                    self.assertNotIn("TRAIN_POS",text)
                    self.assertNotIn("positive partition",text.lower())
                    self.assertNotIn("negative 3-edge premise",text.lower())
            self.assertEqual(r["total_cost_training_included"]["D"]["calls"],8)
            self.assertEqual(r["total_cost_training_included"]["G"]["calls"],11)
            self.assertEqual(r["total_cost_training_included"]["T"]["calls"],11)

    def test_unequal_real_model_usage_blocks_gain(self):
        with tempfile.TemporaryDirectory() as d:
            r=t.run(Path(d),"offline",client=FakeModel(huge=True),
                    token_counter=lambda s:len(s.split()))
            self.assertEqual(r["status"],"INDETERMINATE_BUDGET")
            self.assertFalse(r["registered_gain"])


if __name__=="__main__":
    unittest.main()
