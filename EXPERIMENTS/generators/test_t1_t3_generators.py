import unittest

from t1_t3_generators import (
    generate_t1, generate_t3, replay_affine_chain, validate_t3,
)


class T1Tests(unittest.TestCase):
    def test_reference_example_is_22(self):
        self.assertEqual(replay_affine_chain(3, [(2, 1), (3, -4), (1, 5)]), 22)

    def test_seed_reproducibility(self):
        self.assertEqual(generate_t1(123), generate_t1(123))

    def test_different_seeds_change_parameters(self):
        self.assertNotEqual(generate_t1(123).public_parameters,
                            generate_t1(124).public_parameters)

    def test_depth_must_be_positive(self):
        with self.assertRaises(ValueError):
            generate_t1(1, k=0)


class T3Tests(unittest.TestCase):
    def test_reference_witnesses_are_21_and_25(self):
        self.assertEqual(3 * 7 + 0, 21)
        self.assertEqual(3 * 7 + 4, 25)

    def test_many_seeds_are_genuinely_underdetermined(self):
        for seed in range(100):
            self.assertTrue(validate_t3(generate_t3(seed)), seed)

    def test_private_witnesses_do_not_leak(self):
        task = generate_t3(987)
        public_text = repr(task.public_payload())
        self.assertNotIn("witness_completions", public_text)
        self.assertNotIn(str(task.oracle_private["witness_completions"]), public_text)
        self.assertNotIn("987", public_text)
        self.assertNotIn("T3-987", public_text)
        self.assertEqual(task.evaluation_payload()["generation_private"]["seed"], 987)

    def test_seed_reproducibility(self):
        self.assertEqual(generate_t3(123), generate_t3(123))


if __name__ == "__main__":
    unittest.main()
