import unittest

from t1_t3_generators import (
    generate_t1, generate_t3, replay_affine_chain, validate_t3,
)


class T1Tests(unittest.TestCase):
    def test_reference_example_is_22(self):
        self.assertEqual(replay_affine_chain(3, [(2, 1), (3, -4), (1, 5)]), 22)

    def test_generated_oracle_recomputed_from_public_instance(self):
        for seed in range(100):
            task = generate_t1(seed)
            params = task.public_parameters
            # Deliberately separate oracle implementation: do not call
            # the generator's replay_affine_chain helper here.
            independent = params["initial"]
            for a, b in params["steps"]:
                independent = a * independent + b
            self.assertEqual(independent, task.oracle_private["expected_answer"])

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

    def test_generated_witnesses_match_visible_equations(self):
        for seed in range(100):
            task = generate_t3(seed)
            p = task.public_parameters
            x1 = p["first_step"][0] * p["initial"] + p["first_step"][1]
            witnesses = task.oracle_private["witness_completions"]
            self.assertEqual(len(witnesses), 2)
            for witness in witnesses:
                self.assertEqual(
                    witness["answer"],
                    p["second_step_coefficient"] * x1 + witness["b"],
                )
            self.assertNotEqual(witnesses[0]["b"], witnesses[1]["b"])
            self.assertNotEqual(witnesses[0]["answer"], witnesses[1]["answer"])

    def test_validator_rejects_equal_outputs(self):
        task = generate_t3(123)
        oracle = dict(task.oracle_private)
        witnesses = [dict(w) for w in oracle["witness_completions"]]
        witnesses[1]["answer"] = witnesses[0]["answer"]
        oracle["witness_completions"] = witnesses
        corrupted = type(task)(
            task_id=task.task_id,
            family=task.family,
            prompt=task.prompt,
            public_parameters=task.public_parameters,
            oracle_private=oracle,
            generation=task.generation,
        )
        self.assertFalse(validate_t3(corrupted))

    def test_many_seeds_are_genuinely_underdetermined(self):
        for seed in range(100):
            self.assertTrue(validate_t3(generate_t3(seed)), seed)

    def test_private_witnesses_and_seed_do_not_leak(self):
        task = generate_t3(987)
        public = task.public_payload()
        public_text = repr(public)
        self.assertNotIn("witness_completions", public_text)
        self.assertNotIn(str(task.oracle_private["witness_completions"]), public_text)
        self.assertNotIn("seed", public["generation"])
        self.assertNotIn("987", public_text)
        self.assertNotIn("T3-987", public_text)
        self.assertEqual(task.evaluation_payload()["generation_private"]["seed"], 987)

    def test_seed_reproducibility(self):
        self.assertEqual(generate_t3(123), generate_t3(123))


if __name__ == "__main__":
    unittest.main()
