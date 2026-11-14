from itertools import product
import unittest

from v19_library.verify import shadow


class V19LibraryTests(unittest.TestCase):
    def test_disconnected_contradiction(self):
        cycle = (2, 3, 4)
        constraints = [(0, 1, 1), (0, 1, 0)]
        self.assertEqual(shadow(5, constraints, cycle), frozenset())
        self.assertEqual(shadow(5, [], cycle), frozenset(range(8)))

    def test_projection_matches_literal_colorings(self):
        cycle = (0, 2)
        constraints = [(0, 1, 1), (1, 2, 0)]
        expected = {
            sum(colors[v] << i for i, v in enumerate(cycle))
            for colors in product((0, 1), repeat=4)
            if all(colors[u] ^ colors[v] == parity for u, v, parity in constraints)
        }
        self.assertEqual(shadow(4, constraints, cycle), expected)
