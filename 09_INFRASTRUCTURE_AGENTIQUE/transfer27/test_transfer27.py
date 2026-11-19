#!/usr/bin/env python3
"""Offline contract and negative controls; synthetic proposals ARE NOT model results."""
import hashlib
import inspect
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))

from data_guard import (
    ARMS,ADAPTER_SHA,load_prompts,load_calibration,load_holdout,
    check_unseen_training_family,mod_orbit_direct,mod_gcd_independent,
    overlap_direct,overlap_limits_independent,read_pinned,
)
from logic import parse_raw_reply,interpret,check_on_cases,InvalidExpression
from infer import (
    FIRST_ST,SECOND_ST,stable_first_digest,build_first,build_second,feedback,
)
from grade import score

MOD="EXPR: (target - start) % gcd(step, modulus) == 0"
INT="EXPR: max(a,c) <= min(b,d)"


class Transfer27Tests(unittest.TestCase):
    def test_frozen_and_unseen_domains(self):
        prompts=load_prompts()
        self.assertEqual(len(prompts),16)
        self.assertEqual(sum(p["domain"]=="unsupported" for p in prompts),4)
        c=load_calibration();h=load_holdout()
        self.assertEqual(len(c["modular"]),24)
        self.assertEqual(len(c["intervals"]),24)
        self.assertEqual(len(h["modular"]),96)
        self.assertEqual(len(h["intervals"]),96)
        self.assertTrue(check_unseen_training_family()["no_literal_family_mentions_found"])
        self.assertLess(max(c["modular"],key=lambda x:x["modulus"])["modulus"],
                        min(h["modular"],key=lambda x:x["modulus"])["modulus"])

    def test_correct_new_formula_matches_two_independent_oracles(self):
        for data in (load_calibration(),load_holdout()):
            for c in data["modular"]:
                truth=mod_orbit_direct(c)
                self.assertEqual(truth,mod_gcd_independent(c))
                self.assertEqual(interpret(parse_raw_reply(MOD,"modular_orbit"),
                                           c,"modular_orbit"),truth)
            for c in data["intervals"]:
                truth=overlap_direct(c)
                self.assertEqual(truth,overlap_limits_independent(c))
                self.assertEqual(interpret(parse_raw_reply(INT,"closed_interval_overlap"),
                                           c,"closed_interval_overlap"),truth)

    def test_invalid_shortcuts_get_genuine_counterexamples(self):
        cases=load_calibration()
        bad1=check_on_cases("EXPR: gcd(step, modulus) == 1",
                            "modular_orbit",cases["modular"])
        bad2=check_on_cases("EXPR: a <= d",
                            "closed_interval_overlap",cases["intervals"])
        self.assertEqual(bad1["status"],"FALSIFIED")
        self.assertEqual(bad2["status"],"FALSIFIED")
        self.assertIsNotNone(bad1["counterexample"])
        self.assertIsNotNone(bad2["counterexample"])
        self.assertEqual(check_on_cases(MOD,"modular_orbit",
                                         cases["modular"])["wrong"],0)

    def test_security_reject_injected_code_and_unsafe_numbers(self):
        bad=[
            "EXPR: __import__('os').system('touch /tmp/TRANSFER27_PWN')",
            "EXPR: start.__class__ == target",
            "EXPR: [i for i in range(4)]",
            "EXPR: gcd(step, modulus); print('not allowed')",
            "EXPR: (target - start) % gcd(step, modulus) == 0 # backdoor",
            "EXPR: gcd(step, modulus) >= 1\nEXPR: True",
            "EXPR: pow(start, target) == 3",
            "EXPR: (target - start) // step == 1",
            "EXPR: start ** 3 == target",
            "EXPR: target == 10000",
            "EXPR: a[0] == c",
        ]
        for raw in bad:
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidExpression):
                    parse_raw_reply(raw,"modular_orbit")
        self.assertFalse(Path("/tmp/TRANSFER27_PWN").exists())
        with self.assertRaises(InvalidExpression):
            parse_raw_reply(MOD,"unsupported")
        self.assertIsNone(parse_raw_reply("ABSTAIN","unsupported"))
        with self.assertRaises(InvalidExpression):
            interpret(parse_raw_reply("EXPR: start % step == 0","modular_orbit"),
                      {"start":0,"target":0,"step":0,"modulus":4},
                      "modular_orbit")

    def test_only_calibration_revealed_during_feedback(self):
        feedback_source=inspect.getsource(feedback)
        infer_src=inspect.getsource(build_first)+inspect.getsource(build_second)
        self.assertNotIn("load_holdout(",infer_src)
        self.assertNotIn("load_holdout(",feedback_source)
        cal=load_calibration()
        result=feedback("modular_orbit","EXPR: start == target",cal)
        self.assertEqual(result["status"],"FALSIFIED")
        self.assertLessEqual(result["oracle_cases_checked"],24)
        self.assertIn("correct:",result["reply"])
        self.assertNotIn("gcd",result["reply"])

    def test_synthetic_positive_and_negative_grader_stages(self):
        # This test uses handcrafted fake responses to audit the scorer,
        # NOT a claim of trained model inference or creativity.
        prompts=load_prompts()
        rows=[]; finals=[]
        for p in prompts:
            for arm in ARMS:
                domain=p["domain"]
                good=("ABSTAIN" if domain=="unsupported" else
                      MOD if domain=="modular_orbit" else INT)
                raw=good if arm=="C_LORA_VERIFIER" else "ABSTAIN"
                stamp=hashlib.sha256(raw.encode("utf-8")).hexdigest()
                base={"id":p["id"],"domain":domain,"arm":arm,
                      "raw":raw,"raw_sha256":stamp,
                      "input_tokens":80,"generated_tokens":20,
                      "wall_seconds":0.02,
                      "trained_adapter_enabled":arm!="A_BASE_NEUTRAL"}
                rows.append(base)
                feedback_status=("NEUTRAL_CONTROL" if arm!="C_LORA_VERIFIER"
                    else "UNSUPPORTED_NO_CHECK" if domain=="unsupported"
                    else "MATCHES_FINITE_CASES")
                finals.append({**base,"first_sha256":stamp,
                    "feedback_status":feedback_status,
                    "verifier_cases_checked":24 if arm=="C_LORA_VERIFIER"
                              and domain!="unsupported" else 0,
                    "verifier_wall_seconds":0.1,
                    "verifier_calibration_summary":None})
        first={"status":FIRST_ST,"generation_calls":48,
               "train26_adapter_sha256":ADAPTER_SHA,
               "calibration_loaded":False,"holdout_loaded":False,
               "stable_first_ideas_sha256":stable_first_digest(rows),
               "ideas":rows}
        second={"status":SECOND_ST,"generation_calls":48,
                "train26_adapter_sha256":ADAPTER_SHA,
                "first_stage_sha256":first["stable_first_ideas_sha256"],
                "holdout_loaded":False,"finals":finals}
        report=score(first,second)
        self.assertEqual(report["strong_reference"]["strong_D_correct_cases"],192)
        self.assertEqual(report["arms"]["C_LORA_VERIFIER"]["final"][
            "verified_math_representations_of_12"],12)
        self.assertEqual(report["arms"]["B_LORA_NEUTRAL"]["final"][
            "verified_math_representations_of_12"],0)
        self.assertEqual(report["status_verdicts"]["feedback_vs_trained"],
                         "VERIFIER_FEEDBACK_GAIN_BOUNDED")
        self.assertEqual(report["model_auto_certifications"],0)
        # Tamper a raw answer: cryptographic provenance must block scoring.
        finals[0]["raw"]="EXPR: start == target"
        with self.assertRaises(ValueError):
            score(first,second)

    def test_incorrect_unsupported_rejected_even_if_syntactically_correct(self):
        c=load_holdout()
        result=check_on_cases("EXPR: start == target","modular_orbit",c["modular"])
        self.assertEqual(result["status"],"FALSIFIED")
        self.assertGreater(result["wrong"],0)
        self.assertTrue(result["counterexample"]["expected"] in (True,False))


if __name__=="__main__":
    unittest.main(verbosity=2)
