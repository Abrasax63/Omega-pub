"""Deterministic tests: no Qwen or Docker needed in unit-test phase."""
import types
import unittest
from unittest.mock import patch

from memory_ablation import (
    ROOT, ARM_ORDER, MAX_NOTES_CHARS, RELEVANT_PATH, PLACEBO_PATH,
    BASE_PROMPT, build_prompt, retrieve_contexts, _manifest,
    _all_correct, infer, sha,
)
from runner import graph_case


class CausalContextAblationTests(unittest.TestCase):
    def test_real_rce_retrieves_prior_documents(self):
        c = retrieve_contexts(ROOT)
        self.assertEqual(c["relevant"]["path"], RELEVANT_PATH)
        self.assertEqual(c["placebo"]["path"], PLACEBO_PATH)
        self.assertEqual(len(c["relevant"]["text"]), c["matched_characters"])
        self.assertEqual(len(c["placebo"]["text"]), c["matched_characters"])
        self.assertTrue(180 <= c["matched_characters"] <= MAX_NOTES_CHARS)
        self.assertEqual(len(c["relevant"]["source_blob_sha256"]), 64)

    def test_matched_context_lengths_and_nonoverlap(self):
        c = retrieve_contexts(ROOT)
        p = {arm: build_prompt(arm, c) for arm in ARM_ORDER}
        self.assertEqual(len(p["memoire_rce"]), len(p["placebo_rce"]))
        self.assertNotEqual(sha(p["memoire_rce"]), sha(p["placebo_rce"]))
        self.assertNotIn(c["relevant"]["text"], p["sans_memoire"])
        self.assertNotIn(c["relevant"]["text"], p["placebo_rce"])
        self.assertIn(c["relevant"]["text"], p["memoire_rce"])
        self.assertIn(c["placebo"]["text"], p["placebo_rce"])

    def test_qwen_role_markers_not_broken(self):
        c = retrieve_contexts(ROOT)
        for arm in ARM_ORDER:
            p = build_prompt(arm, c)
            self.assertEqual(p.count("<|im_start|>system"), 1)
            self.assertEqual(p.count("<|im_start|>user"), 1)
            self.assertEqual(p.count("<|im_start|>assistant"), 1)
            self.assertEqual(p.count("<|im_end|>"), 2)

    def test_unknown_arm_rejected(self):
        with self.assertRaises(ValueError):
            build_prompt("unknown", {"placebo": {}, "relevant": {}})

    def test_duplicate_heldout_group_rejected(self):
        case = graph_case(1191)
        with self.assertRaises(ValueError):
            _manifest([case, case])

    def test_ast_generated_source_parsed_without_inference(self):
        code = (
            "def q_power(rows, steps):\n"
            "    return [1 << i for i in range(len(rows))]\n"
        )
        fake = types.SimpleNamespace(returncode=0, stdout=code, stderr="")
        with patch("memory_ablation.subprocess.run", return_value=fake) as call:
            result = infer("fake-llama", "fake-model", "sans_memoire", BASE_PROMPT)
        self.assertTrue(call.called)
        self.assertEqual(result["status"], "SOURCE_VALID_AST")
        self.assertEqual(result["source"], code)
        self.assertEqual(len(result["semantic_sha256"]), 64)

    def test_model_cli_error_not_faked_as_candidate(self):
        fake = types.SimpleNamespace(returncode=1, stdout="", stderr="failed")
        with patch("memory_ablation.subprocess.run", return_value=fake):
            result = infer("fake-llama", "fake-model", "memoire_rce", BASE_PROMPT)
        self.assertEqual(result["status"], "MODEL_CALL_FAILED")
        self.assertIsNone(result["source"])

    def test_no_false_correctness_without_all_refs(self):
        self.assertFalse(_all_correct([]))
        self.assertFalse(_all_correct([{"correct": True, "delta_correct": False}]))
        self.assertTrue(_all_correct([{"correct": True, "delta_correct": True}]))


if __name__ == "__main__":
    unittest.main()
