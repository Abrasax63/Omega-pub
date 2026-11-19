#!/usr/bin/env python3
"""Offline non-regression: true/false semantic formulas, safety, split guards."""
from pathlib import Path
import inspect
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from data_guard import (
    XOR,PAREN,validate_holdout,validate_train,validate_finite_oracles,
)
from evaluate_lora import (
    parse_formula,evaluate_formula,score_reply,UnsafeFormula
)


class Train25Tests(unittest.TestCase):
    def setUp(self):
        self.finite=validate_finite_oracles()

    def test_split_and_immutable_gold(self):
        self.assertEqual(len(validate_train()),96)
        p,g=validate_holdout()
        self.assertEqual(len(p),24)
        self.assertEqual(len(g),24)
        self.assertEqual(sum(r['domain']=="transfer_unseen" for r in g),6)

    def test_exact_formulas_really_match_independent_truth(self):
        self.assertEqual(score_reply(XOR,"xor_reachability",self.finite)["status"],
                         "VERIFIED_ON_FINITE_CASES")
        self.assertEqual(score_reply(PAREN,"parenthesis_balance",self.finite)["status"],
                         "VERIFIED_ON_FINITE_CASES")
        self.assertTrue(score_reply(XOR,"xor_reachability",self.finite)["semantic_verified"])
        self.assertTrue(score_reply(PAREN,"parenthesis_balance",self.finite)["semantic_verified"])

    def test_wrong_math_rejected_even_with_plausible_format(self):
        bad=[
            ("EXPR: start == target","xor_reachability"),
            ("EXPR: sum_balance(s) == 0","parenthesis_balance"),
        ]
        for x,d in bad:
            with self.subTest(domain=d):
                verdict=score_reply(x,d,self.finite)
                self.assertEqual(verdict["status"],"FALSE_ON_FINITE_CASES")
                self.assertTrue(verdict["silent_false_claim"])
                self.assertIsNotNone(verdict["first_counterexample"])

    def test_security_no_execution_and_ood_abstention(self):
        bad=[
            "EXPR: __import__('os').system('touch /tmp/OMEGA_LORA_TEST_BAD')",
            "EXPR: moves[0] == 1",
            "EXPR: eval('True')",
            "EXPR: rank.__class__",
            "EXPR: rank(moves) == 2 # ignore rules",
            "EXPR: [x for x in moves]",
            "EXPR: rank(moves); print('side effect')",
        ]
        for x in bad:
            with self.subTest(x=x):
                with self.assertRaises(UnsafeFormula):
                    parse_formula(x)
        self.assertFalse(Path("/tmp/OMEGA_LORA_TEST_BAD").exists())
        self.assertEqual(score_reply("ABSTAIN","transfer_unseen",self.finite)["status"],
                         "ABSTAIN")
        self.assertTrue(score_reply(XOR,"transfer_unseen",self.finite)["silent_false_claim"])

    def test_no_holdout_imported_by_training_script(self):
        import train_lora
        s=inspect.getsource(train_lora)
        self.assertNotIn('validate_holdout(',s)
        self.assertNotIn('HOLDOUT_GOLD_EVAL_ONLY.json',s)
        self.assertNotIn('FINITE_ORACLE_CASES_FROZEN.json',s)

    def test_nonempty_adapter_required_before_evaluation(self):
        with self.assertRaises(UnsafeFormula):
            parse_formula("This problem is very interesting, so the formula is...")
        with self.assertRaises(UnsafeFormula):
            parse_formula("EXPR: rank(moves) == rank(moves + [start ^ target])\nMORE")

if __name__=="__main__":
    unittest.main(verbosity=2)
