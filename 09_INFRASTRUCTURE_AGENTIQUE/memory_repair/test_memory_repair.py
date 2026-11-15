"""Pre-inference controls; all test model calls are explicitly mocked."""
from __future__ import annotations
import hashlib
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

from memory_repair import (
    ROOT, ARMS, CALLS_PER_ARM, OUTPUT_TOKENS, CONTEXT_TOKENS,
    MICRO_CASES, RELEVANT_PATH, compile_rce_tests, prompt_first,
    prompt_repair, feedback_of, infer, development, public_check,
)
from reference import walks_exact


class MemoryRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.compiled = compile_rce_tests(ROOT)

    def test_rce_source_is_real_and_sha_bound(self):
        c = self.compiled
        self.assertEqual(c["scientific_source"]["path"], RELEVANT_PATH)
        data = (ROOT / RELEVANT_PATH).read_bytes()
        self.assertEqual(c["scientific_source"]["source_blob_sha256"],
                         hashlib.sha256(data).hexdigest())
        self.assertEqual(c["matched_source_tags"],
                         {"Q^h": True, "exact": True, "squaring": True, "lowbit": True})

    def test_actual_executable_cases_independent_oracle(self):
        c = self.compiled
        self.assertEqual(len(c["checks"]), 4)
        for check in c["checks"]:
            self.assertEqual(check["expected"],
                             walks_exact(check["rows"], check["steps"]))
            self.assertTrue(check["assertion"].startswith("assert q_power("))
        self.assertTrue(any(x["id"] == "branching_union" for x in c["checks"]))

    def test_no_hidden_case_in_test_pack(self):
        pack = self.compiled["executable_assertions"]
        self.assertNotIn("source-seed-", pack)
        self.assertNotIn("heldout", pack.lower())
        self.assertNotIn("secrets", pack)

    def test_matched_character_budget_for_repair_notes(self):
        first = {"source": "def q_power(rows, steps):\n    return rows[:]\n",
                 "development_exception": "ValueError: incorrect result"}
        a = prompt_repair(first, self.compiled, memory=False)
        c = prompt_repair(first, self.compiled, memory=True)
        self.assertEqual(len(a), len(c))
        self.assertNotEqual(a, c)
        self.assertIn(self.compiled["executable_assertions"], c)
        self.assertNotIn(self.compiled["executable_assertions"], a)
        self.assertEqual(a.count("<|im_start|>assistant"), 1)
        self.assertEqual(c.count("<|im_start|>assistant"), 1)

    def test_first_prompt_is_same_between_arms(self):
        self.assertEqual(ARMS, ("feedback_seul", "feedback_plus_contraintes"))
        self.assertEqual(CALLS_PER_ARM, 2)
        self.assertEqual(OUTPUT_TOKENS, 512)
        self.assertEqual(CONTEXT_TOKENS, 3072)
        self.assertNotIn("lowbit", prompt_first().lower())

    def test_failure_witness_public_and_deterministic(self):
        first = {"source": "def q_power(rows, steps):\n    return rows\n",
                 "development": [{
                    "correct": False, "delta_correct": False,
                    "counterexample": {
                        "rows": [2, 1], "steps": 0,
                        "expected": [1, 2], "actual": [2, 1],
                    },
                 }]}
        a = feedback_of(first)
        self.assertIn("PUBLIC", a)
        self.assertIn("expected", a)
        self.assertEqual(a, feedback_of(first))

    def test_cli_error_not_model_success(self):
        fake = types.SimpleNamespace(returncode=2, stdout="", stderr="failed")
        with patch("memory_repair.subprocess.run", return_value=fake):
            result = infer(Path("/tmp/llama"), Path("/tmp/model"),
                           prompt_first(), ARMS[0], 1)
        self.assertEqual(result["status"], "MODEL_CALL_FAILED")
        self.assertIsNone(result["source"])

    def test_accepted_source_is_still_subject_to_development(self):
        fake = types.SimpleNamespace(
            returncode=0,
            stdout="def q_power(rows, steps):\n    return rows[:]\n",
            stderr="",
        )
        with patch("memory_repair.subprocess.run", return_value=fake):
            result = infer(Path("/tmp/llama"), Path("/tmp/model"),
                           prompt_first(), ARMS[0], 1)
        self.assertEqual(result["status"], "SOURCE_AST_VALID")
        with patch("memory_repair.score", return_value=[
            {"correct": False, "delta_correct": False, "counterexample": None}
        ]), patch("memory_repair.public_check", return_value=[
            {"correct": True}
        ]):
            development(result, [], self.compiled)
        self.assertFalse(result["development_correct"])

    def test_micro_checks_execute_through_only_sandbox(self):
        source = "def q_power(rows, steps):\n    return rows\n"
        def fake_executor(source, rows, steps, repeats):
            self.assertEqual(repeats, 1)
            return walks_exact(rows, steps), 101
        with patch("memory_repair.execute", side_effect=fake_executor) as ex:
            results = public_check(source, self.compiled)
        self.assertEqual(ex.call_count, 4)
        self.assertTrue(all(x["correct"] for x in results))

    def test_missing_documentary_tag_must_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "ALGO.md").write_text("hello", encoding="utf-8")
            (root / "ARCHITECTURE.md").write_text("general docs" * 100)
            algo = {
                "path": "ALGO.md", "rank_zero_based": 0,
                "source_blob_sha256": hashlib.sha256(b"hello").hexdigest(),
                "search_sha256": "a" * 64, "line_ranges": [[1, 1]],
                "text": "hello",
            }
            placebo = {
                "path": "ARCHITECTURE.md", "rank_zero_based": 0,
                "source_blob_sha256": "b" * 64,
                "search_sha256": "c" * 64, "line_ranges": [[1, 1]],
                "text": "general docs" * 50,
            }
            with patch("memory_repair._retrieve_one", side_effect=[algo, placebo]):
                with self.assertRaisesRegex(ValueError, "missing RCE scientific tag"):
                    compile_rce_tests(root)


if __name__ == "__main__":
    unittest.main()
