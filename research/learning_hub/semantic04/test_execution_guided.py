"""Offline adversarial regression tests for the execution-guided repairer.

All test programs are engineering fixtures, not a novel blinded benchmark.
The original SEMANTIC04 holdout has already been consumed.
"""
import inspect
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import core
import execution_guided as eg


class GuidedRepairTests(unittest.TestCase):
    def setUp(self):
        self.for_code=(
            "def transform(s):\n"
            "    out = []\n"
            "    for c in s:\n"
            "        if c in 'ab':\n"
            "            out.append(c.upper())\n"
            "    return out\n"
        )

    def test_second_in_edit_is_generated_not_just_for_loop_keyword(self):
        source=self.for_code
        variants=eg.candidate_codes(source)
        target=source.replace("if c in 'ab':","if c not in 'ab':")
        self.assertIn(target,[x["code"] for x in variants])
        self.assertNotIn("for c not in s:",[x["code"] for x in variants])

    def test_public_correct_second_in_edit_found(self):
        expected=[
            {"input":"abc","output":["C"]},
            {"input":"baac","output":["C"]},
        ]
        variants,_=eg.collect_agreeing(self.for_code,expected)
        target=self.for_code.replace("if c in 'ab':","if c not in 'ab':")
        self.assertIn(target,[x["code"] for x in variants])

    def test_frozen_semantic04_missed_case_now_in_candidate_search(self):
        # Post-hoc check on an ALREADY CONSUMED cohort, not independent
        # evidence of transfer to new programming tasks.
        rows=core.frozen_cases()
        case=next(x for x in rows if x["id"]==
                  "SEM04-even_distinct_lower-reversed_membership")
        matches,_=eg.collect_agreeing(case["broken_source"],
                                      case["public_examples"])
        self.assertTrue(any(core.grade(x["code"],case["hidden_cases"])
                            ["all_correct"] for x in matches))

    def test_ambiguity_requires_new_oracle_not_hidden_answer(self):
        source=("def transform(s):\n"
                "    out = []\n"
                "    for c in s:\n"
                "        out.append(c)\n"
                "    return out\n")
        visible=[{"input":"a","output":["a"]}]
        state=eg.resolve(source,visible)
        self.assertEqual(state["status"],"NEEDS_ORACLE_RESPONSE")
        self.assertIsNone(state["selected_code"])
        self.assertEqual(state["hidden_tests_seen"],0)
        self.assertFalse(state["suggested_probe"]["oracle_answer_provided"])
        self.assertIn(state["suggested_probe"]["proposed_input"],eg.PROBE_INPUTS)

    def test_oracle_feedback_is_external_and_really_new(self):
        old=[{"input":"a","output":["a"]}]
        self.assertEqual(len(eg.extend_public(old,"ab",["a","b"])),2)
        with self.assertRaisesRegex(ValueError,"REUSED_PROBE"):
            eg.extend_public(old,"a",["a"])
        self.assertEqual(len(old),1)

    def test_no_model_calls_weights_or_hidden_oracles_in_module(self):
        src=(Path(__file__).resolve().parent/"execution_guided.py").read_text()
        self.assertNotIn("load_holdout(",src)
        self.assertNotIn("reference_code_eval_only",src)
        self.assertNotIn("train_lora(",src)
        self.assertNotIn("torch.optim",src)
        self.assertNotIn("from transformers",src)
        self.assertNotIn("from peft",src)

    def test_rejects_untrusted_model_imports(self):
        source=self.for_code
        text="def transform(s):\n    return [__import__('os').system('id')]\n"
        state=eg.resolve(source,[{"input":"c","output":["C"]}],model_text=text)
        self.assertEqual(state["seed_count"],1)
        self.assertFalse(state["scientific_proof"])

    def test_bad_public_observations_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_PUBLIC"):
            eg.resolve(self.for_code,[{"input":3,"output":[]}])
        with self.assertRaisesRegex(ValueError,"INVALID_PUBLIC"):
            eg.resolve(self.for_code,[])

    def test_candidate_budget_strict(self):
        with self.assertRaisesRegex(ValueError,"INVALID_EDIT_BUDGET"):
            eg.candidate_codes(self.for_code,limit=0)
        with self.assertRaisesRegex(ValueError,"INVALID_EDIT_BUDGET"):
            eg.candidate_codes(self.for_code,limit=eg.MAX_CANDIDATES+1)
        self.assertLessEqual(len(eg.candidate_codes(self.for_code,limit=3)),3)

    def test_candidate_safety_ast_enforced(self):
        variants=eg.candidate_codes(self.for_code)
        self.assertTrue(all(core.sandbox.validate_program(x["code"]) for x in variants))
        self.assertEqual(len({x["sha256"] for x in variants}),len(variants))

    def test_symbolic_priority_not_degraded_by_untrusted_model_seed(self):
        source=self.for_code
        gold=source.replace("if c in 'ab':","if c not in 'ab':")
        public=[{"input":"abc","output":["C"]},
                {"input":"baac","output":["C"]}]
        poisoned_model=("def transform(s):\n"
                        "    out = []\n"
                        "    for c in s:\n"
                        "        out.append(c.upper())\n"
                        "    return out\n")
        initial=eg.resolve_guarded(source,public)
        with_model=eg.resolve_guarded(source,public,model_text=poisoned_model)
        self.assertEqual(initial["selected_code"],gold)
        self.assertEqual(with_model["selected_code"],gold)
        self.assertTrue(with_model["protected_symbolic_choice"])
        self.assertFalse(with_model["model_seed_considered"])

    def test_guarded_hybrid_does_not_use_model_to_break_ambiguity(self):
        source=("def transform(s):\n"
                "    out = []\n"
                "    for c in s:\n"
                "        out.append(c)\n"
                "    return out\n")
        public=[{"input":"a","output":["a"]}]
        status=eg.resolve_guarded(source,public,model_text=source)
        self.assertEqual(status["status"],"NEEDS_ORACLE_RESPONSE")
        self.assertFalse(status["model_seed_considered"])
        self.assertEqual(status["hidden_tests_seen"],0)

    def test_no_causal_claim_from_public_match(self):
        source=self.for_code
        public=[{"input":"abc","output":["C"]}]
        result=eg.resolve(source,public)
        self.assertIn(result["status"],(
            "NEEDS_ORACLE_RESPONSE","UNIQUE_PUBLIC_CANDIDATE_NEEDS_INDEPENDENT_TEST",
            "AMBIGUOUS_CANDIDATES_NO_PROBE_FOUND"))
        self.assertFalse(result["scientific_proof"])
        self.assertEqual(result["hidden_tests_seen"],0)
        self.assertEqual(result["training_steps"],0)


if __name__=="__main__":
    unittest.main()
