"""Offline tests for OMEGA-PROCEDURE-06; no model/downloads."""
import json
from pathlib import Path
import tempfile
import unittest

from concept_abstraction_lab import check_axioms
import omega_hybrid_procedure06 as m


class FakeClient:
    def __init__(self,inflate=False):
        self.calls=[]
        self.inflate=inflate
    def __call__(self,messages,limit):
        self.calls.append(messages)
        prompt=messages[-1]["content"]
        if "certificate" in prompt and "Apply a mechanical" in prompt:
            out='{"holds":true,"failed_axioms":[],"certificate":{"kind":"partition","blocks":[["v0"],["v1"],["v2"],["v3"],["v4"]]}}'
        else:
            out='{"holds":true,"failed_axioms":[]}'
        measured=len((m.SYSTEM+"\n"+prompt).split())
        if self.inflate and "Apply a mechanical" in prompt:
            measured*=3
        return {"text":out, "usage":{"prompt_tokens":measured,
                 "completion_tokens":25},"time_s":0.02}


class Procedure06Tests(unittest.TestCase):
    def test_manifest_exactly_four_plus_four_no_oracle_leak(self):
        questions,answers=m.make_manifest()
        self.assertEqual((questions,answers),m.make_manifest())
        self.assertEqual(len(questions["questions"]),8)
        self.assertEqual(len(answers["answers"]),8)
        self.assertEqual(sum(a["holds"] for a in answers["answers"]),4)
        self.assertEqual(len({m.isomorphic_key(frozenset(
            map(tuple,q["edges"]))) for q in questions["questions"]}),8)
        self.assertFalse(questions["contains_oracle_answers"])
        self.assertNotIn("oracle_witnesses",json.dumps(questions))
        self.assertNotIn("failed_axioms",json.dumps(questions))
        for q in questions["questions"]:
            self.assertEqual(len(q["nodes"]),5)
            e=frozenset(map(tuple,q["edges"]))
            self.assertTrue(all((x,x) in e for x in m.NODES))
            self.assertTrue(all((b,a) in e for a,b in e))

    def test_two_oracles_agree_exhaustively_on_all_1024_graphs(self):
        for mask in range(1<<len(m.PAIRS)):
            edges=m.relation(mask)
            self.assertEqual(m.independent_clique_check(edges),
                             m.exact_result(edges)["holds"])

    def test_real_transitivity_counterexample_certificate(self):
        q,a=m.make_manifest()
        index=next(i for i,answer in enumerate(a["answers"]) if not answer["holds"])
        edges=frozenset(map(tuple,q["questions"][index]["edges"]))
        triple=a["answers"][index]["oracle_witnesses"]["transitive"]
        cert={"kind":"missing_transitive_edge","triple":triple}
        self.assertTrue(m.check_certificate(cert,edges,False))
        self.assertFalse(m.check_certificate(
            {"kind":"missing_transitive_edge","triple":["v0","v0","v0"]},
            edges,False))
        self.assertFalse(m.check_certificate(
            {"kind":"missing_transitive_edge","triple":["v0","v1","invalid"]},
            edges,False))

    def test_independent_positive_partition_certificate(self):
        q,a=m.make_manifest()
        index=next(i for i,ans in enumerate(a["answers"]) if ans["holds"])
        edges=frozenset(map(tuple,q["questions"][index]["edges"]))
        seen,blocks=set(),[]
        for x in m.NODES:
            if x not in seen:
                comp=[y for y in m.NODES if (x,y) in edges]
                blocks.append(comp)
                seen.update(comp)
        self.assertTrue(m.check_certificate(
            {"kind":"partition","blocks":blocks},edges,True))
        self.assertFalse(m.check_certificate(
            {"kind":"partition","blocks":[list(m.NODES)]},edges,True))
        self.assertFalse(m.check_certificate(
            {"kind":"partition","blocks":[["v0"]]},edges,True))

    def test_correct_label_without_certificate_not_operational(self):
        q,a=m.make_manifest()
        i=next(i for i,ans in enumerate(a["answers"]) if ans["holds"])
        e=frozenset(map(tuple,q["questions"][i]["edges"]))
        answer='{"holds":true,"failed_axioms":[],"certificate":{"kind":"partition","blocks":[["v0"],["v1"],["v2"],["v3"],["v4"]]}}'
        verdict=m.valid_answer(answer,a["answers"][i],"P",e)
        self.assertTrue(verdict["full_axioms_correct"])
        self.assertFalse(verdict["certificate_valid"])
        self.assertEqual(verdict["status"],"CERTIFICATE_INVALID")

    def test_invalid_and_unrecognized_axioms_not_admitted(self):
        q,a=m.make_manifest()
        e=frozenset(map(tuple,q["questions"][0]["edges"]))
        for answer in ('{"holds":true,"failed_axioms":["transitivity"]}',
                       '{"holds":true,"failed_axioms":["transitive"]}',
                       '{"holds":false,"failed_axioms":[]}',
                       '{"holds":"true","failed_axioms":[]}',
                       '{"abstain":true}'):
            verdict=m.valid_answer(answer,a["answers"][0],"D",e)
            self.assertFalse(verdict["full_axioms_correct"])

    def test_model_receives_only_questions_with_no_oracle_witnesses(self):
        q,a=m.make_manifest()
        for item in q["questions"]:
            for arm in m.ARMS:
                prompt=m.task_prompt(item,arm)
                self.assertNotIn("oracle_witnesses",prompt)
                self.assertNotIn('"holds":',prompt)
                self.assertNotIn('"mask":',prompt)

    def test_offline_full_run_never_claims_learning(self):
        with tempfile.TemporaryDirectory() as td:
            fake=FakeClient()
            r=m.run(Path(td),"offline",client=fake,
                    token_counter=lambda s:len(s.split()))
            self.assertEqual(r["model_calls"],24)
            self.assertEqual(len(fake.calls),24)
            self.assertEqual(r["status"],"PRE_REGISTERED_GAIN_NOT_OBSERVED")
            self.assertEqual(r["scientific_skills_certified"],0)
            self.assertFalse(r["model_weights_updated"])
            self.assertFalse(r["gain_criterion_met"])
            self.assertTrue(r["actual_input_budget_comparable"])
            self.assertEqual(r["metrics"]["D"]["full_axioms_correct"],4)
            self.assertEqual(r["metrics"]["R"]["full_axioms_correct"],4)
            self.assertEqual(r["metrics"]["P"]["certificate_valid"],0)
            questions=json.loads((Path(td)/"model_inputs.json").read_text())
            answers=json.loads((Path(td)/"oracle_only.json").read_text())
            self.assertEqual(len(questions["questions"]),8)
            self.assertEqual(len(answers["answers"]),8)
            for call in fake.calls:
                self.assertEqual(len(call),2)
                self.assertNotIn("oracle_witnesses",call[-1]["content"])

    def test_token_usage_imbalance_blocks_gain(self):
        with tempfile.TemporaryDirectory() as td:
            r=m.run(Path(td),"offline",client=FakeClient(inflate=True),
                    token_counter=lambda s:len(s.split()))
            self.assertEqual(r["status"],"INDETERMINATE_BUDGET")
            self.assertFalse(r["gain_criterion_met"])


if __name__=="__main__":
    unittest.main()
