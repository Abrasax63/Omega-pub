#!/usr/bin/env python3
"""TRAIN26 offline tests independent of any model call or LoRA weights."""
from pathlib import Path
import inspect
import sys
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from data_guard import (
    FORMULAS,load_training,load_holdout,load_oracles,
    direct_xor,gaussian_xor,stack_parens,direct_trace,partition_trace,
)
from evaluate import (
    UnsafeView,parse_expression,checked_formula,
    check_critic_labels,judge_reply,summarize,
)


class Train26Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=load_training()
        cls.prompts,cls.gold=load_holdout()
        cls.oracles=load_oracles()
        cls.critic_evidence=check_critic_labels(cls.prompts,cls.gold,cls.oracles)

    def test_immutable_data_and_exposure_preconditions(self):
        self.assertEqual(len(self.data),320)
        self.assertEqual(len(self.prompts),48)
        self.assertEqual(sum(len(v) for v in self.oracles.values() if isinstance(v,list)),96)
        self.assertEqual(len(self.critic_evidence),12)
        self.assertEqual(len({r["prompt"] for r in self.data}),320)
        self.assertFalse(
            {r["prompt"] for r in self.data} &
            {r["prompt"] for r in self.prompts}
        )

    def test_three_classical_views_agree_with_96_original_oracles(self):
        for domain,formula in FORMULAS.items():
            with self.subTest(domain=domain):
                verdict=checked_formula(formula[6:],domain,self.oracles)
                self.assertTrue(verdict["passed"],verdict)
                self.assertEqual(verdict["finite_checked"],32)
                self.assertFalse(verdict["formal_proof_produced"])

    def test_three_domains_have_true_counterexamples_to_wrong_views(self):
        faulty={
            "xor":[
                "popcount(start ^ target) <= len(moves)",
                "rank(moves) == rank([start ^ target])",
            ],
            "paren":[
                "sum_balance(s) >= 0 and min_prefix_balance(s) >= 0",
                "min_prefix_balance(s) == 0",
            ],
            "obs":[
                "partition_code(T, pi, 1, x) == partition_code(T, pi, 1, y)",
                "partition_code(T, pi, 0, x) == partition_code(T, pi, 0, y)",
            ]
        }
        for domain,views in faulty.items():
            for v in views:
                with self.subTest(domain=domain,formula=v):
                    result=checked_formula(v,domain,self.oracles)
                    self.assertEqual(result["verifier_status"],
                                     "FALSIFIED_BY_FINITE_COUNTEREXAMPLE",result)
                    self.assertIsNotNone(result["first_counterexample"])
                    self.assertGreater(result["mismatches"],0)

    def test_critic_gold_proven_with_test_oracle(self):
        for p,g in zip(self.prompts,self.gold):
            if p["task"]!="CRITIQUE":
                continue
            e=self.critic_evidence[p["id"]]
            label="ACCEPT" if e["passed"] else "REJECT"
            self.assertEqual(g["target"],label)
            row=judge_reply(label,p,g,self.oracles,self.critic_evidence)
            self.assertTrue(row["correct_task"])
            self.assertTrue(row["critic_answer_correct"])
            self.assertFalse(row["false_mathematical_assertion"])

    def test_false_math_attempt_is_not_promoted(self):
        idx=next(i for i,p in enumerate(self.prompts)
                 if p["task"]=="FORMALIZE" and p["domain"]=="paren")
        p,g=self.prompts[idx],self.gold[idx]
        row=judge_reply("EXPR: sum_balance(s) == 0",p,g,
                        self.oracles,self.critic_evidence)
        self.assertFalse(row["correct_task"])
        self.assertTrue(row["false_mathematical_assertion"])
        self.assertFalse(row["gate_accepted_false_claim"])
        self.assertIsNotNone(row["evidence"]["first_counterexample"])
        good=judge_reply(FORMULAS["paren"],p,g,self.oracles,self.critic_evidence)
        self.assertTrue(good["correct_task"])

    def test_unsupported_domain_requires_explicit_abstention(self):
        idx=next(i for i,p in enumerate(self.prompts) if p["domain"]=="transfer_unseen")
        p,g=self.prompts[idx],self.gold[idx]
        best=judge_reply("ABSTAIN",p,g,self.oracles,self.critic_evidence)
        bad=judge_reply(FORMULAS["xor"],p,g,self.oracles,self.critic_evidence)
        self.assertTrue(best["correct_task"])
        self.assertFalse(best["false_mathematical_assertion"])
        self.assertFalse(bad["correct_task"])
        self.assertTrue(bad["false_mathematical_assertion"])

    def test_unsafe_generated_code_never_executes(self):
        threats=[
            "__import__('os').system('touch /tmp/OMEGA26_MALWARE')",
            "rank(moves) == rank(moves+[start^target]) # trust me",
            "open('/etc/passwd')",
            "eval('True')",
            "(lambda: True)()",
            "moves[0]==start",
            "partition_code.__class__",
            "rank(moves); print('x')",
            "[a for a in moves]",
            "rank(moves)==rank(moves+[start^target])\nVERIFIED",
            "partition_code(T, pi, h, x, y) == 0",
            "sum_balance(s) == -1",
        ]
        for s in threats:
            with self.subTest(s=s):
                with self.assertRaises(UnsafeView):
                    parse_expression(s)
        self.assertFalse(Path("/tmp/OMEGA26_MALWARE").exists())

    def test_training_source_never_explicitly_loads_holdout(self):
        import train_full
        code=inspect.getsource(train_full)
        self.assertIn("load_training(",code)
        self.assertNotIn("load_holdout(",code)
        self.assertNotIn("HOLDOUT_GOLD_EVAL_ONLY.json",code)
        self.assertNotIn("ORACLE_CASES_FROZEN.json",code)

    def test_scores_keep_errors_not_just_format(self):
        rows=[]
        for p,g in zip(self.prompts,self.gold):
            if p["task"] in ("FORMALIZE","REPAIR"):
                reply=FORMULAS[p["domain"]]
            else:
                reply=g["target"]
            rows.append(judge_reply(reply,p,g,self.oracles,self.critic_evidence))
        good=summarize(rows)
        self.assertEqual(good["semantic_task_score"],48)
        self.assertEqual(good["false_mathematical_assertions"],0)
        self.assertEqual(good["formalization_verified"],24)
        self.assertEqual(good["correct_critic_verdicts"],12)
        self.assertEqual(good["justified_abstentions"],12)
        self.assertEqual(len(good["raw_output_sha256"]),64)


if __name__=="__main__":
    unittest.main(verbosity=2)
