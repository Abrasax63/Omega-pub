"""OBS-COL-11: exact source lock, third-party model grammar and no invented edges."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from external_transfer import (
    load_pinned_moore, ExternallyIncomplete,
    ARMS, fit_one,
)
from generate_manifests import equivalence_words
from policy_divergence import coverage_ranking


HERE = Path(__file__).resolve().parent
SOURCES = Path(os.environ.get("OBS_COL11_SOURCES", "obs_col11_sources"))


class TestExternalTransfer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sources = SOURCES
        cls.lock = json.loads((HERE / "SOURCE_SHA_LOCK.json").read_text())["sha256"]
        if not cls.sources.is_dir():
            raise RuntimeError("frozen sources not downloaded before unit tests")

    def test_six_names_and_external_bytes_match_source_lock(self):
        self.assertEqual(tuple(self.lock), (
            "crossword2x2.dot", "crossword3x3.dot", "register2.dot",
            "register3.dot", "register4.dot", "register5.dot"))
        for name, expected in self.lock.items():
            data = (self.sources / name).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), expected)

    def test_reject_content_changed_after_lock(self):
        name, sha = next(iter(self.lock.items()))
        data = (self.sources / name).read_bytes()
        with tempfile.TemporaryDirectory() as t:
            file = Path(t) / name
            file.write_bytes(data + b"\n")
            with self.assertRaises(AssertionError):
                load_pinned_moore(file, sha)

    def test_incomplete_sources_are_blocked_not_silently_repaired(self):
        for name in ("crossword2x2.dot", "crossword3x3.dot"):
            with self.assertRaises(ExternallyIncomplete) as ctx:
                load_pinned_moore(self.sources / name, self.lock[name])
            self.assertGreater(len(ctx.exception.missing), 0)
            self.assertGreater(ctx.exception.states, 0)

    def test_four_registers_parse_exactly_as_complete_moore(self):
        for width in (2, 3, 4, 5):
            name = f"register{width}.dot"
            model, metadata = load_pinned_moore(self.sources / name, self.lock[name])
            self.assertEqual(len(model.states), 2 ** width)
            self.assertEqual(sorted(model.get_input_alphabet()), ["F", "L", "R"])
            self.assertEqual(metadata["missing_transitions"], {})
            self.assertTrue(model.is_input_complete())

    def test_policy_reuses_prior_candidate_universe_without_state_mutation(self):
        model, _ = load_pinned_moore(self.sources / "register2.dot", self.lock["register2.dot"])
        words = equivalence_words(("F", "L", "R"), 2)
        before = model.current_state
        for memory in (False, True):
            chosen = coverage_ranking(model, words, memory=memory)
            self.assertEqual(len(chosen), len(words))
            self.assertEqual(set(chosen), set(words))
        self.assertIs(model.current_state, before)

    def test_real_lsharp_and_frozen_omega_policy_inherits_actual_p1(self):
        name = "register2.dot"
        for arm in ("fixed", "omega_candidate"):
            source, _ = load_pinned_moore(self.sources / name, self.lock[name])
            model, row = fit_one(source, arm, name, 2)
            self.assertEqual(row["model"], name)
            self.assertGreater(row["physical_resets"], 0)
            self.assertGreaterEqual(len(model.states), 2)
            self.assertFalse(row["equivalence_certified"])
            self.assertFalse(row["omega_superiority_claim"])
            if arm == "omega_candidate":
                self.assertEqual(row["physical_resets"], row["p1_calls"])
            else:
                self.assertEqual(row["p1_calls"], 0)

    def test_five_real_arms_declared_without_pseudo_ttt(self):
        self.assertEqual(ARMS, ("fixed", "coverage_only", "omega_candidate", "Lstar", "KV"))


if __name__ == "__main__":
    unittest.main()
