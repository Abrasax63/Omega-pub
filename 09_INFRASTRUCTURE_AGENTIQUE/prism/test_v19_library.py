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


class V19PrefixTests(unittest.TestCase):
    def test_identical_short_prefixes_have_different_global_shadows(self):
        from v19_library.prefix import forced_edges, orbit, prefix_shadow

        cycle = (3, 4, 5)
        maps = [(1, 0, 0, 4, 5, 3), (1, 1, 0, 4, 5, 3)]
        for T, expected in zip(maps, ({0, 3, 4, 7}, set(range(8)))):
            with self.subTest(T=T):
                self.assertEqual(orbit(T, 2, 3), [2, 0, 1])
                self.assertEqual(orbit(T, 3, 3), [3, 4, 5])
                forced = forced_edges(dict(enumerate(T)))
                self.assertTrue(shadow(6, forced, ()))
                full = shadow(6, forced + [(2, 3, 0), (0, 4, 0)], cycle)
                self.assertEqual(full, expected)
                self.assertEqual(prefix_shadow(cycle, orbit(T, 2, 4), orbit(T, 3, 4), 2), full)
