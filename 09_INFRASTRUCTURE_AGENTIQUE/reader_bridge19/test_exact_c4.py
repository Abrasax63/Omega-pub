#!/usr/bin/env python3
"""Reader19 invariants and mutation checks, independent of historical math code."""
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from exact_c4 import (
    T, PAIRS, TARGETS, TARGET_CLASSES, SOURCE, SOURCE_BLOB,
    analyze, block_lookup, canonical_mask_collection, congruent,
    members, partitions_of_mask, rotated,
)
from read import safe_read


class IndependentFiniteC4Tests(unittest.TestCase):
    def test_source_git_blob_still_matches(self):
        raw = safe_read(SOURCE, SOURCE_BLOB)
        self.assertIn(b"49", raw)
        self.assertIn(b"120", raw)

    def test_all_nine_state_partitions_counted_once(self):
        partitions = list(partitions_of_mask((1 << 9) - 1))
        self.assertEqual(len(partitions), 21147)
        self.assertEqual(len(set(partitions)), 21147)
        for part in partitions[:500]:
            union = 0
            for block in part:
                self.assertEqual(union & block, 0)
                union |= block
            self.assertEqual(union, (1 << 9)-1)

    def test_direct_block_congruence_and_mutation(self):
        discrete = tuple(1 << i for i in range(9))
        indiscrete = ((1 << 9)-1,)
        self.assertTrue(congruent(discrete, T))
        self.assertTrue(congruent(indiscrete, T))
        # States 0 and 1 share a block but their successors 1,2 do not.
        merged = ((1 << 0) | (1 << 1),) + tuple(1 << i for i in range(2,9))
        self.assertFalse(congruent(merged, T))
        self.assertEqual(block_lookup(discrete, 9), tuple(range(9)))
        with self.assertRaises(ValueError):
            block_lookup((1, 1), 9)

    def test_shadow_rotations_are_representation_invariant(self):
        self.assertEqual(len(TARGET_CLASSES), 8)
        for target in TARGETS:
            expected = canonical_mask_collection(set(target))
            for k in range(4):
                transformed = {rotated(m, k) for m in target}
                self.assertEqual(canonical_mask_collection(transformed), expected)
        self.assertEqual(sorted(members(1|4|64)), [0,2,6])

    def test_negative_pair_not_reported_as_valid_quotient(self):
        altered = list(PAIRS)
        altered[0] = (0, 0)
        report = analyze(T, tuple(altered), count_shadows=False)
        self.assertEqual(report["partitions_enumerated"], 21147)
        self.assertEqual(report["eligible"], 0)

    def test_reject_unsupported_state_model(self):
        with self.assertRaisesRegex(ValueError, "FROZEN_9_STATE"):
            analyze((0, 0), PAIRS, count_shadows=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
