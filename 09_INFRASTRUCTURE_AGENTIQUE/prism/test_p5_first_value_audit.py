"""Zero-provider regression tests for P5-VALUE-01 exact-vs-model ablation."""
from collections import Counter
import unittest
from p5_first_value_audit import (
    ARMS, CRT_PARAMETERS, DATA_PARAMETERS, DOC_CLAIMS, MODEL_ID,
    cases, reference, exact_verifier, request_for, messages, extract_answer,
    plan_schedule, preflight, verification_policies, summarize,
)

class ValueAuditTests(unittest.TestCase):
    def test_two_independently_implemented_oracles_agree(self):
        rows=cases()
        self.assertEqual(len(rows),18)
        self.assertEqual(Counter(x["kind"] for x in rows),
                         {"crt":6,"data":6,"doc":6})
        for r in rows:
            if r["kind"]=="doc":
                self.assertIsNone(exact_verifier(r))
                self.assertEqual(reference(r),"INDETERMINE")
            else:
                self.assertEqual(reference(r),exact_verifier(r))
        self.assertEqual(len(CRT_PARAMETERS),6)
        self.assertEqual(len(DATA_PARAMETERS),6)
        self.assertEqual(len(DOC_CLAIMS),6)

    def test_same_substantive_inputs_and_no_answer_leak(self):
        for c in cases():
            shared=[request_for(c,a)["input"]["shared"] for a in ARMS]
            self.assertEqual(shared[0],shared[1])
            self.assertEqual(shared[1],shared[2])
            self.assertEqual(len({request_for(c,a)["input"]["strategy"]
                                  for a in ARMS}),3)
            for a in ARMS:
                output=messages(c,a)
                self.assertEqual(len(output),2)
                self.assertNotIn("reference",str(output))
                self.assertNotIn("parameters",str(output))
                self.assertNotIn("answer_key",str(output))
                self.assertNotIn("gold",str(output))
                self.assertIn("Première ligne obligatoire",output[1]["content"])

    def test_new_seed_and_count_54_generations(self):
        s=plan_schedule(cases())
        self.assertEqual(s,plan_schedule(cases()))
        self.assertEqual(len(s),54)
        self.assertEqual(len(set(s)),54)
        self.assertEqual(MODEL_ID,"Qwen/Qwen2.5-0.5B-Instruct")
        p=preflight()
        self.assertEqual(p["model_generations"],0)
        self.assertEqual(p["planned_model_generations"],54)
        self.assertEqual(p["paid_api_calls"],0)
        self.assertFalse(p["private_data_read"])
        self.assertEqual(len(p["public_cases_sha256"]),64)

    def test_parser_accepts_clear_answer_and_rejects_ambiguity(self):
        self.assertEqual(extract_answer("Réponse : 17\nRaisonnement"),"17")
        self.assertEqual(extract_answer("Résultat final : A\nEt voilà."),"A")
        self.assertEqual(extract_answer('La réponse finale est "INDETERMINE".'),"INDETERMINE")
        self.assertEqual(extract_answer("9"),"9")
        self.assertEqual(extract_answer("Réponse: 9\nRéponse finale: 11"),None)
        self.assertIsNone(extract_answer("Je ne sais pas"))
        self.assertIsNone(extract_answer("Réponse : OUI"))
        self.assertIsNone(extract_answer("Le nombre 9 pourrait convenir."))

    def test_adaptive_routing_matches_trivial_type_control(self):
        p=verification_policies(cases())
        self.assertEqual(p["V-all"]["verifier_calls"],18)
        self.assertEqual(p["Omega-route"]["verifier_calls"],12)
        self.assertEqual(p["Type-route"]["verifier_calls"],12)
        self.assertEqual(p["Omega-route"]["predictions"],
                         p["Type-route"]["predictions"])
        for r in p.values():
            self.assertEqual(r["exact_matches"],18)
            self.assertEqual(r["abstentions"],6)
            self.assertEqual(r["model_calls"],0)

    def test_cost_and_checker_grading_requires_all_outputs(self):
        rows=cases()
        sample=[]
        for c in rows:
            for arm in ARMS:
                sample.append({"case_id":c["case_id"],"arm":arm,
                    "parsed":reference(c),"input_tokens":10,"output_tokens":2,
                    "latency_seconds":0.1})
        measures,checked=summarize(sample,rows)
        for arm in ARMS:
            self.assertEqual(measures[arm]["generations"],18)
            self.assertEqual(measures[arm]["strict_exact_matches"],18)
        self.assertEqual(checked["A+V"]["exact_matches"],18)
        self.assertEqual(checked["C+V"]["verifier_calls"],12)

if __name__=="__main__":
    unittest.main()
