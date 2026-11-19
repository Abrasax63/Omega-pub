#!/usr/bin/env python3
"""Test unsafe model outputs, fixed corpus and separate reference solvers."""
import hashlib
import json
import sys
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from dsl import InvalidProposal,parse_proposal,execute_proposal,characteristics
from grade import stack_baseline,cancellation_oracle,cohorts,exhaustive,assess_proposal,grade
from propose import infer_all,MODEL,SCHEDULE

# A deliberately incorrect length-based smoke-test, NEVER a training example.
P={"weights":{"(":0,")":1},
   "predicate":{"op":"gt","left":{"feature":"length"},"right":{"const":5}},
   "idea":"Length-only incorrect smoke test."}


class CreativeModel02Tests(unittest.TestCase):
    def test_safe_ast_works(self):
        parsed=parse_proposal(json.dumps(P))
        self.assertFalse(execute_proposal(parsed,"()")[0])
        self.assertTrue(execute_proposal(parsed,"()"*3)[0])
        self.assertEqual(characteristics("()()()",P["weights"])[1],6)

    def test_injection_and_extra_keys_refused(self):
        bad=[
            "__import__('os').system('ls')",
            json.dumps({**P,"code":"print(1)"}),
            json.dumps({**P,"predicate":{"op":"python","script":"import os"}}),
            json.dumps({**P,"predicate":{"op":"and","args":[]}}),
            json.dumps({**P,"weights":{"(":"a",")":-1}}),
            "not json",
        ]
        for raw in bad:
            with self.subTest(raw=raw[:45]):
                with self.assertRaises(InvalidProposal):
                    parse_proposal(raw)

    def test_two_exact_oracles_exhaustive(self):
        words=list(exhaustive())
        self.assertEqual(len(words),8191)
        for s in words:
            self.assertEqual(stack_baseline(s)[0],cancellation_oracle(s))
        self.assertTrue(cancellation_oracle(""))
        self.assertFalse(cancellation_oracle(")("))

    def test_seeded_reserved_and_metamorphic_groups(self):
        holdout,metamorph=cohorts()
        self.assertEqual(len(holdout),80)
        self.assertEqual(len(metamorph),16)
        self.assertEqual(sum(stack_baseline(x["word"])[0] for x in holdout),40)
        self.assertEqual(sum(stack_baseline(x["word"])[0] for x in metamorph),8)
        self.assertTrue(all(len(x["word"])<=128 for x in holdout+metamorph))

    def test_invalid_model_reply_fails_closed(self):
        holdout,metamorph=cohorts()
        raw="bad_json"
        row={"status":"MODEL_RAW_FROZEN","attempt":1,"seed":11,
             "temperature":0,"raw_reply":raw,
             "raw_sha256":hashlib.sha256(raw.encode()).hexdigest()}
        report=assess_proposal(row,holdout,metamorph,["","()"])
        self.assertEqual(report["status"],"ABSTAIN_INVALID_PROPOSAL")
        self.assertEqual(report["holdout_correct"],0)

    def test_nonadaptive_schedule_and_false_proposal_falsified(self):
        def fake(seed,temperature):
            raw=json.dumps(P)
            return {"raw_reply":raw,"raw_sha256":hashlib.sha256(raw.encode()).hexdigest(),
                    "served_model":"FAKE_ONLY","finish_reason":"stop",
                    "token_usage":{"total_tokens":10}}
        frozen=infer_all(fake)
        self.assertEqual([(r["seed"],r["temperature"]) for r in frozen["proposals"]],
                         list(SCHEDULE))
        self.assertEqual(frozen["model"],MODEL)
        self.assertFalse(frozen["model_saw_holdout_cases"])
        self.assertFalse(frozen["model_saw_candidate_exemplars"])
        graded=grade(frozen)
        self.assertEqual(graded["model_proposals_accepted"],3)
        self.assertEqual(graded["model_proposals_bounded_equivalent"],0)
        self.assertEqual(graded["strong_baseline_correct"],8287)
        self.assertTrue(graded["independent_oracles_agreed"])
        self.assertFalse(graded["general_equivalence_proved"])


if __name__=="__main__":
    unittest.main(verbosity=2)
