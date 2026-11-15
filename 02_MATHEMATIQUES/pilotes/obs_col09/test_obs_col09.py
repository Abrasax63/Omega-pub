"""OBS-COL-09: ensure genuine external baselines, no target leakage, matched P1 gate."""
import unittest
from pathlib import Path
import inspect
from benchmark import (
    FIXTURES, ALGORITHMS, PhysicalCounter, external_fixture,
    evaluation_words, run_algorithm, run, MAX_RESETS, MAX_SYMBOLS,
)
from aalpy.learning_algs import run_Lstar, run_KV, run_Lsharp
from aalpy.SULs import AutomatonSUL


class TestObsCol09(unittest.TestCase):
    def test_real_external_aalpy_algorithms(self):
        self.assertTrue(callable(run_Lstar))
        self.assertTrue(callable(run_KV))
        self.assertTrue(callable(run_Lsharp))
        self.assertTrue(run_Lsharp.__module__.startswith("aalpy."))
        self.assertEqual(ALGORITHMS, ("Lstar", "KV", "Lsharp", "Lsharp_P1"))

    def test_three_pinned_external_moore_files(self):
        self.assertEqual(len(FIXTURES), 3)
        for name, sha in FIXTURES:
            model, source = external_fixture(name, sha)
            self.assertTrue(model.is_input_complete())
            self.assertGreaterEqual(len(model.states), 2)
            self.assertEqual(source["git_blob_sha"], sha)
            self.assertTrue(Path(__file__).parent.joinpath("external_fixtures", name).is_file())

    def test_eval_is_deterministic_and_has_256_distinct_sequences(self):
        for i, (name, sha) in enumerate(FIXTURES):
            model, _ = external_fixture(name, sha)
            alphabet = sorted(model.get_input_alphabet(), key=str)
            words = evaluation_words(alphabet, i)
            self.assertEqual(len(words), 256)
            self.assertEqual(len(set(words)), 256)
            self.assertTrue(all(12 <= len(word) <= 18 for word in words))
            self.assertEqual(words, evaluation_words(alphabet, i))

    def test_matched_java_and_python_eval_input_manifests(self):
        from generate_matched_eval import INPUTS, words
        for index, (filename, alphabet) in enumerate(INPUTS):
            model, _ = external_fixture(*FIXTURES[index])
            self.assertEqual(filename, FIXTURES[index][0])
            self.assertEqual(alphabet, tuple(sorted(model.get_input_alphabet(), key=str)))
            self.assertEqual(words(alphabet, index), evaluation_words(alphabet, index))

    def test_physical_counter_and_true_p1_gate(self):
        name, sha = FIXTURES[0]
        model, _ = external_fixture(name, sha)
        counter = PhysicalCounter(model, use_p1=True)
        counter.pre()
        out = counter.step(sorted(model.get_input_alphabet(), key=str)[0])
        counter.post()
        self.assertIsNotNone(out)
        self.assertEqual(counter.physical_resets, 1)
        self.assertEqual(counter.physical_symbols, 1)
        self.assertEqual(counter.p1_calls, 1)
        self.assertEqual(len(counter.observed_prefixes), 1)

    def test_lsharp_vs_real_p1_gate_same_black_box_trace(self):
        name, sha = FIXTURES[0]
        b = run_algorithm(0, name, sha, "Lsharp")
        o = run_algorithm(0, name, sha, "Lsharp_P1")
        for f in ("learned_states", "physical_symbols", "physical_resets",
                  "physical_trace_sha256", "heldout_errors_unseen",
                  "heldout_unseen_scored"):
            self.assertEqual(b[f], o[f])
        self.assertEqual(b["p1_calls"], 0)
        self.assertEqual(o["p1_calls"], o["physical_resets"])

    def test_full_external_benchmark_has_no_false_claim(self):
        r = run()
        self.assertEqual(r["model_calls"], 0)
        self.assertEqual(r["ttt_status"], "NOT_EXECUTED_IN_THIS_PYTHON_STAGE")
        self.assertFalse(r["p1_selects_queries"])
        self.assertEqual(len(r["results"]), 12)
        for item in r["results"]:
            self.assertLessEqual(item["physical_symbols"], MAX_SYMBOLS)
            self.assertLessEqual(item["physical_resets"], MAX_RESETS)
            self.assertEqual(item["heldout_words_total"], 256)
            self.assertEqual(item["heldout_unseen_scored"] +
                             item["heldout_overlap_seen_during_training"], 256)
            self.assertFalse(item["equivalence_certified"])
            self.assertFalse(item["omega_superiority_demonstrated"])


if __name__ == "__main__":
    unittest.main()
