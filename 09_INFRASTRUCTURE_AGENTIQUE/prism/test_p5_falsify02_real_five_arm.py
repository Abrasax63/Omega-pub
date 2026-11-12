"""FALSIFY-02 preflight checks. Fake CPU engine here is TEST FIXTURE ONLY."""
import copy
from collections import Counter
from pathlib import Path
import unittest

import p5_falsify02_real_five_arm as m

ROOT=Path(__file__).resolve().parents[2]

class FiveArmActualMechanismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal,cls.test=m.dataset()
        cls.ghost=next(r for r in cls.cal if all(
            tuple(r[k])==v for k,v in m.GHOST.items()))
        cls.one=cls.cal[0]
        cls.req={arm:m.public_request(cls.ghost,arm,ROOT)
                 for arm in m.ARMS}

    def test_40_exact_unique_calibration_and_synthetic_evaluation(self):
        self.assertEqual(len(self.cal),8)
        self.assertEqual(len(self.test),32)
        self.assertEqual(Counter(x["answer"] for x in self.cal),{"A":4,"B":4})
        self.assertEqual(Counter(x["answer"] for x in self.test),{"A":16,"B":16})
        ids=[x["id"] for x in self.cal+self.test]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(all(
            ("A" if m.is_realizable(r) else "B")==r["answer"]
            and m.survivor_certificate(r)["is_possible"]==m.is_realizable(r)
            for r in self.cal+self.test))
        self.assertEqual(len(m._full_universe()),27*6*8)

    def test_actual_internal_gluing_ghost_is_calibration_only(self):
        self.assertEqual(tuple(self.ghost["t"]),(0,2,2))
        self.assertEqual(tuple(self.ghost["pi"]),(0,0,1))
        self.assertEqual(tuple(self.ghost["word"]),(0,0,1))
        self.assertEqual(self.ghost["answer"],"B")
        self.assertEqual(m.survivor_certificate(self.ghost)[
            "prefix_survivor_counts"],[2,1,0])
        self.assertFalse(m.is_realizable(self.ghost))
        self.assertFalse(any(x["id"]==self.ghost["id"] for x in self.test))

    def test_one_shared_model_and_real_p1_and_p2_and_survivor_path(self):
        self.assertEqual(len(m.ARMS),5)
        self.assertEqual(m.MODEL_REVISION,
                         "7ae557604adf67be50417f59c2c2f167def9a775")
        self.assertTrue(m.validate_requests_for_case(self.ghost,self.req))
        self.assertEqual(self.req["direct"]["messages"],
                         self.req["classical_exact"]["messages"])
        self.assertEqual(self.req["omega_no_memory"]["actual_rce_searches"],0)
        self.assertGreater(self.req["omega_no_memory"]["actual_observability_calls"],0)
        self.assertEqual(self.req["omega_no_observability"]["actual_observability_calls"],0)
        self.assertGreater(self.req["omega_no_observability"]["actual_rce_searches"],0)
        self.assertGreater(self.req["omega_full_candidate"]["actual_rce_searches"],0)
        self.assertEqual(self.req["omega_full_candidate"]["actual_observability_calls"],1)
        self.assertEqual(self.req["omega_no_memory"]["planner_version"],"0.1.0")
        self.assertEqual(self.req["omega_full_candidate"]["planner_version"],"0.1.0")

    def test_gold_not_serialized_in_model_prompt(self):
        for arm,request in self.req.items():
            text=" ".join(x["content"] for x in request["messages"])
            self.assertIn("Sur X={0,1,2}",text)
            self.assertNotIn("evaluator_only",text)
            self.assertNotIn('"answer"',text)
            self.assertNotIn('"gold"',text)
        self.assertNotIn("VERIFICATEUR EXACT",
                         str(self.req["omega_no_observability"]["messages"]))
        self.assertIn("VERIFICATEUR EXACT",
                      str(self.req["omega_no_memory"]["messages"]))

    def test_cosmetic_flag_cannot_substitute_actual_mechanism(self):
        altered=copy.deepcopy(self.req)
        altered["omega_full_candidate"]["memory"]=None
        with self.assertRaises(ValueError):
            m.validate_requests_for_case(self.ghost,altered)
        altered=copy.deepcopy(self.req)
        altered["omega_no_memory"]["memory"]={"fake":"memory"}
        with self.assertRaises(ValueError):
            m.validate_requests_for_case(self.ghost,altered)
        altered=copy.deepcopy(self.req)
        altered["omega_no_observability"]["observation_tool"]={"fake":True}
        with self.assertRaises(ValueError):
            m.validate_requests_for_case(self.ghost,altered)

    def test_real_model_preflight_has_no_model_inference(self):
        r=m.preflight(ROOT)
        self.assertEqual(r["status"],"P5_FALSIFY02_PREFLIGHT_NO_MODEL_CALLS")
        self.assertEqual(r["calibration"],8)
        self.assertEqual(r["evaluation"],32)
        self.assertEqual(r["expected_real_cpu_forwards"],200)
        self.assertEqual(r["token_cap"],512)
        self.assertFalse(r["is_blinded_independent_benchmark"])
        self.assertTrue(r["same_A_B_prompt"])

    def test_paper_model_outputs_cannot_be_mistaken_for_actual_qwen_calls(self):
        # Explicit fixture. Test that the classical oracle is genuinely
        # consulted for B, and observed model labels are not gold.
        class Fixture:
            def infer(self,messages):
                return {
                    "model_predicted":"B","input_tokens":70,"output_tokens":1,
                    "inference_seconds":0.1,"logit_a":0.0,"logit_b":1.0,
                    "model_calls":1,
                }
        class FakeBad:
            def infer(self,messages):
                return {
                    "model_predicted":"B","input_tokens":70,"output_tokens":1,
                    "inference_seconds":0.1,"logit_a":0.0,"logit_b":1.0,
                    "model_calls":0,
                }
        pos=next(r for r in self.cal if r["answer"]=="A")
        b=m.invoke_case("classical_exact",pos,ROOT,Fixture())
        a=m.invoke_case("direct",pos,ROOT,Fixture())
        self.assertEqual(a["final_answer"],"B")
        self.assertFalse(a["correct"])
        self.assertEqual(b["final_answer"],"A")
        self.assertTrue(b["correct"])
        self.assertEqual(b["model_answer"],"B")
        self.assertTrue(b["actual_new_experimental_runner"])
        with self.assertRaises(AssertionError):
            m.invoke_case("direct",pos,ROOT,FakeBad())

    def test_no_random_gold_or_calibrated_policy_leak(self):
        bad=dict(self.ghost)
        bad["answer"]="A" # Manipulating stored truth must not alter tool result.
        self.assertFalse(m.is_realizable(bad))
        self.assertFalse(m.survivor_certificate(bad)["is_possible"])
        self.assertEqual(m.public_request_without_tools(bad),
                         m.public_request_without_tools(self.ghost))

if __name__=="__main__":
    unittest.main()
