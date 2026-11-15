"""OBS-COL-09B: reproducibility, real AALpy/P1 oracle and manifest tests."""
import tempfile
import unittest
from pathlib import Path

from common_eq import SharedWordEquivalenceOracle, run_method, run, FIXTURES
from generate_manifests import (
    INPUTS, equivalence_words, generate, read_words, encode, manifest_hash,
)
from benchmark import external_fixture, PhysicalCounter


class TestCommonEq(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.path = Path(cls.tmp.name)
        cls.metadata = generate(cls.path)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_external_target_names_unchanged(self):
        self.assertEqual([n for n, _ in FIXTURES], [n for n, _ in INPUTS])

    def test_512_candidate_words_are_deterministic_and_unique(self):
        for i, (_, alphabet) in enumerate(INPUTS):
            words = equivalence_words(alphabet, i)
            self.assertEqual(len(words), 512)
            self.assertEqual(len(set(words)), 512)
            self.assertEqual(words, equivalence_words(alphabet, i))
            self.assertEqual([len(w) for w in words[:6]], [1, 1, 2, 2, 2, 2])

    def test_manifest_fingerprint_and_eval_separation(self):
        for i, (name, alphabet) in enumerate(INPUTS):
            values = equivalence_words(alphabet, i)
            read, h = read_words(self.path / (name + ".eq.words"), values)
            self.assertEqual(read, values)
            self.assertEqual(h, manifest_hash(encode(values)))
            self.assertEqual(h, self.metadata[i]["eq_sha256"])
            self.assertEqual(self.metadata[i]["eq_count"], 512)
            self.assertEqual(self.metadata[i]["eval_count"], 256)

    def test_wrong_manifest_fails_closed(self):
        name, alpha = INPUTS[0]
        path = self.path / (name + ".eq.words")
        raw = path.read_bytes()
        try:
            path.write_bytes(raw[:-2])
            with self.assertRaises(AssertionError):
                read_words(path, equivalence_words(alpha, 0))
        finally:
            path.write_bytes(raw)

    def test_actual_aalpy_eq_rejects_wrong_hypothesis(self):
        model, _ = external_fixture(*FIXTURES[0])
        # Target itself is exactly equivalent, so fixed suite should find no CEX.
        physical = PhysicalCounter(model, use_p1=False)
        independent_hypothesis, _ = external_fixture(*FIXTURES[0])
        alphabet = sorted(model.get_input_alphabet(), key=str)
        values = equivalence_words(tuple(map(str, alphabet)), 0)
        mapping = {str(x): x for x in alphabet}
        eq = SharedWordEquivalenceOracle(
            alphabet, physical,
            [tuple(mapping[x] for x in word) for word in values],
        )
        self.assertIsNone(eq.find_cex(independent_hypothesis))
        self.assertEqual(eq.completed_suites, 1)
        self.assertEqual(eq.proposed_words, 512)
        self.assertEqual(eq.num_queries, 512)

    def test_real_lsharp_matches_real_lsharp_p1(self):
        name, sha = FIXTURES[0]
        a = run_method(0, name, sha, "Lsharp", self.path)
        b = run_method(0, name, sha, "Lsharp_P1", self.path)
        for key in ("learned_states", "eq_candidates_executed", "physical_resets",
                    "physical_symbols", "physical_trace_sha256", "evaluation_unseen_errors"):
            self.assertEqual(a[key], b[key])
        self.assertEqual(a["p1_calls"], 0)
        self.assertEqual(b["p1_calls"], b["physical_resets"])
        self.assertFalse(a["equivalence_certified"])

    def test_four_algorithms_and_three_external_fixtures(self):
        result = run(self.path)
        self.assertEqual(result["protocol"], "OBS-COL-09B")
        self.assertEqual(len(result["results"]), 12)
        self.assertFalse(result["p1_selects_probes"])
        for item in result["results"]:
            self.assertEqual(item["proposed_eq_words_per_round"], 512)
            self.assertEqual(item["evaluation_count"], 256)
            self.assertTrue(item["evaluation_unseen_count"] > 0)
            self.assertFalse(item["equivalence_certified"])
            self.assertFalse(item["omega_gains_demonstrated"])
            self.assertLessEqual(item["physical_resets"], 10000)
            self.assertLessEqual(item["physical_symbols"], 50000)


if __name__ == "__main__":
    unittest.main()
