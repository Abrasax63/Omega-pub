import itertools
import unittest

from reference import observed_relation, walks_exact, actual_h_relation, delta
from variant_factory import choose, generate


class VariantSearchTests(unittest.TestCase):
    def test_exact_against_set_reference_exhaustive_small(self):
        for states in (1, 2, 3):
            for transition in itertools.product(range(states), repeat=states):
                for coloring in itertools.product((0, 1), repeat=states):
                    q = observed_relation(transition, coloring, 2)
                    for h in range(7):
                        gold = walks_exact(q, h)
                        for name, variant in generate().items():
                            scope = {}
                            exec(compile(variant['source'], name, 'exec'), scope)
                            got = scope['q_power'](q, h)
                            self.assertEqual(got, gold, (name, states, transition, coloring, h))
                            self.assertEqual(delta(transition, coloring, 2, h, got),
                                             delta(transition, coloring, 2, h, gold))

    def test_output_true_orbit_relation_is_subset_of_q_walks(self):
        transition, coloring = (1, 2, 2), (0, 1, 0)
        q = observed_relation(transition, coloring, 2)
        for h in range(15):
            true = actual_h_relation(transition, coloring, 2, h)
            reachable = walks_exact(q, h)
            self.assertTrue(all((a & ~b) == 0 for a, b in zip(true, reachable)))

    def test_generates_four_distinct_executable_programs(self):
        variants = generate()
        self.assertEqual(len(variants), 4)
        self.assertEqual(len({x['sha256'] for x in variants.values()}), 4)
        self.assertTrue(all('def q_power' in x['source'] for x in variants.values()))

    def test_selects_lowest_cost_correct_candidate(self):
        scores = {'a': {'correct': True, 'errors': 0, 'cpu_us_total': 10},
                  'b': {'correct': True, 'errors': 0, 'cpu_us_total': 5},
                  'c': {'correct': False, 'errors': 1, 'cpu_us_total': 1}}
        self.assertEqual(choose(scores), 'b')
        self.assertIsNone(choose({'a': scores['c']}))

    def test_bad_steps_rejected(self):
        for name, value in generate().items():
            scope = {}
            exec(compile(value['source'], name, 'exec'), scope)
            with self.assertRaises(ValueError):
                scope['q_power']([1], -1)


if __name__ == '__main__':
    unittest.main()
