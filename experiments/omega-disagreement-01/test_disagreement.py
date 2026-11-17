"""Scientific controls for OMEGA-DISAGREE-01; no holdout used in tests."""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import disagreement_lab as d


def fake_hypothesis():
    a = SimpleNamespace(state_id="s0", output_fun={0: 0, 1: 0})
    z = SimpleNamespace(state_id="s1", output_fun={0: 1, 1: 1})
    a.transitions = {0: a, 1: z}
    z.transitions = {0: a, 1: z}
    return SimpleNamespace(initial_state=a, states=[a, z])


class DisagreementTests(unittest.TestCase):

    def test_prereg_and_baselines_unchanged(self):
        self.assertEqual(d.PREREG, "0019fbb181032944491bcc56a240159da43bb95c")
        self.assertEqual(d.ARMS[:-1], d.r.ARMS)
        self.assertEqual(d.CAPS, (300, 500))
        self.assertEqual(d.c.EQ_LENGTH, 10)
        self.assertEqual(d.c.EQ_ROUND_WORDS, 32)
        self.assertEqual(d.b.version("aalpy"), "1.6.2")

    def test_virtual_mutation_does_not_modify_hypothesis(self):
        h = fake_hypothesis()
        first = h.initial_state
        word = (1, 0, 1)
        original = d.modified_trace(h, word)
        alternative = d.modified_trace(h, word, (first, 1, 2, None))
        self.assertNotEqual(original, alternative)
        self.assertEqual(original, d.modified_trace(h, word))
        self.assertEqual(first.output_fun[1], 0)

    def test_alternatives_rejected_by_paid_observation(self):
        h = fake_hypothesis()
        queries = [{"inputs": [1], "outputs": [0], "phase": "MQ", "charge": 1}]
        variants, proposed = d.admissible_variants(h, queries)
        self.assertGreater(proposed, 0)
        self.assertTrue(variants)
        self.assertTrue(all(d.modified_trace(h, (1,), v) == (0,)
                            for v in variants))

    def test_absence_of_evidence_can_allow_multiple_possibilities(self):
        h = fake_hypothesis()
        variants, proposed = d.admissible_variants(h, [])
        self.assertGreater(len(variants), 1)
        self.assertGreaterEqual(proposed, len(variants))
        self.assertLessEqual(len(variants), 64)

    def test_selection_uses_only_candidate_and_paid_logs(self):
        h = fake_hypothesis()
        fake_sul = SimpleNamespace(queries=[], remaining=500)
        a = d.DisagreementOracle(fake_sul, 31415)
        b = d.DisagreementOracle(fake_sul, 31415)
        a.eq_rounds = b.eq_rounds = 1
        with patch.object(d.b, "exact_equivalence",
                          side_effect=AssertionError("BFS_LEAK")), \\
             patch.object(d.b, "truth_trace",
                          side_effect=AssertionError("TRUTH_LEAK")), \\
             patch.object(d.b, "heldout_score",
                          side_effect=AssertionError("TEST_LEAK")):
            aa = [a.next_word(h) for _ in range(32)]
            bb = [b.next_word(h) for _ in range(32)]
        self.assertEqual(aa, bb)
        self.assertTrue(all(len(word) == 10 for word in aa))
        self.assertTrue(all(set(word) <= {0, 1} for word in aa))
        self.assertLessEqual(a.disagreement_chosen, 32)

    def test_probability_and_bootstrap_definition(self):
        self.assertEqual(d.exact_p(0, 0), 1)
        self.assertEqual(d.exact_p(3, 0), .125)
        self.assertEqual(d.exact_p(0, 3), 1)

    def test_new_cohort_is_structurally_distinct(self):
        previous = d.r.historical_signatures()
        previous.update(x["signature"] for x in d.r.fresh_worlds())
        self.assertEqual(len(previous), 1196)
        worlds = d.fresh_worlds()
        self.assertEqual(len(worlds), 48)
        self.assertEqual([x["size"] for x in worlds], [4]*16+[5]*16+[6]*16)
        for row in worlds:
            self.assertNotIn(row["canonical_signature"], previous)
            self.assertEqual(len(d.c.reachable(row["machine"])), row["size"])
            self.assertTrue(d.c.distinguishable(row["machine"]))

    def test_real_small_sul_smoke_with_exact_evaluator_later(self):
        world = d.c.resilience.cycle_marker_machine(4)
        reserved = d.reserved_words(4, 0)
        result = d.disagreement_evaluate(world, 300, 20261117, reserved)
        training = result["training"]
        ledger = training["ledger"]
        self.assertLessEqual(ledger["spent_symbols"], 300)
        self.assertEqual(sum(x["charge"] for x in ledger["query_log"]),
                         ledger["spent_symbols"])
        self.assertEqual(training["eq_words_tested"],
                         sum(x["phase"] == "EQ" and
                             not x.get("incomplete_due_to_budget")
                             for x in ledger["query_log"]))
        self.assertIn(result["exact_equivalence"]["status"],
                      ("EXACT_EQUIVALENT", "NOT_EQUIVALENT", "NO_HYPOTHESIS"))


if __name__ == "__main__":
    unittest.main()
