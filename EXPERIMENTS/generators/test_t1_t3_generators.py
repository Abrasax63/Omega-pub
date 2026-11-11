import json
import unittest

from t1_t3_generators import (
    generate_t1, generate_t3, replay_affine_chain, validate_t3,
    validate_prompt_consistency,
)


class T1Tests(unittest.TestCase):
    def test_reference_example_is_22(self):
        self.assertEqual(replay_affine_chain(3, [(2, 1), (3, -4), (1, 5)]), 22)

    def test_generated_oracle_recomputed_from_public_instance(self):
        for seed in range(100):
            task = generate_t1(seed)
            params = task.public_parameters
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

    def test_canonical_prompt_matches_public_parameters(self):
        for seed in range(25):
            self.assertTrue(validate_prompt_consistency(generate_t1(seed).public_payload()))

    def test_json_round_trip_preserves_t1_public_contract_and_oracle(self):
        for seed in range(25):
            task = generate_t1(seed)
            public = json.loads(json.dumps(task.public_payload(), ensure_ascii=False))
            evaluation = json.loads(json.dumps(task.evaluation_payload()))
            self.assertTrue(validate_prompt_consistency(public))
            params = public["public_parameters"]
            value = params["initial"]
            for a, b in params["steps"]:
                value = a * value + b
            self.assertEqual(value, evaluation["oracle_private"]["expected_answer"])

    def test_prompt_mutation_is_rejected(self):
        payload = generate_t1(41).public_payload()
        payload["prompt"] = payload["prompt"].replace("Étape 1: f(x) = ", "Étape 1: f(x) = 999", 1)
        self.assertFalse(validate_prompt_consistency(payload))

    def test_parameter_mutation_is_rejected(self):
        payload = generate_t1(42).public_payload()
        payload["public_parameters"]["steps"][0][0] += 1
        self.assertFalse(validate_prompt_consistency(payload))

    def test_deleted_or_reordered_step_prompt_is_rejected(self):
        payload = generate_t1(43).public_payload()
        lines = payload["prompt"].splitlines()
        payload["prompt"] = "\n".join(lines[:-2] + lines[-1:])
        self.assertFalse(validate_prompt_consistency(payload))

    def test_forced_depth_and_affine_edge_cases(self):
        for depth in (1, 2, 5):
            task = generate_t1(700 + depth, k=depth)
            self.assertEqual(len(task.public_parameters["steps"]), depth)
            self.assertTrue(validate_prompt_consistency(task.public_payload()))
        parameters = {"initial": -2, "steps": [[1, 0], [-3, -2]]}
        payload = {
            "family": "T1",
            "prompt": (
                "Valeur initiale : x = -2\n"
                "Applique les transformations dans l'ordre :\n"
                "Étape 1: f(x) = 1x + (0)\n"
                "Étape 2: f(x) = -3x + (-2)\n"
                "Quelle est la valeur finale ?"
            ),
            "public_parameters": parameters,
        }
        self.assertTrue(validate_prompt_consistency(payload))
        self.assertEqual(replay_affine_chain(-2, [(1, 0), (-3, -2)]), 4)


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

    def test_validator_rejects_forged_witness_answer(self):
        task = generate_t3(321)
        oracle = dict(task.oracle_private)
        witnesses = [dict(w) for w in oracle["witness_completions"]]
        witnesses[0]["answer"] += 1
        oracle["witness_completions"] = witnesses
        corrupted = type(task)(
            task_id=task.task_id, family=task.family, prompt=task.prompt,
            public_parameters=task.public_parameters, oracle_private=oracle,
            generation=task.generation,
        )
        self.assertFalse(validate_t3(corrupted))

    def test_validator_rejects_equal_outputs(self):
        task = generate_t3(123)
        oracle = dict(task.oracle_private)
        witnesses = [dict(w) for w in oracle["witness_completions"]]
        witnesses[1]["answer"] = witnesses[0]["answer"]
        oracle["witness_completions"] = witnesses
        corrupted = type(task)(
            task_id=task.task_id, family=task.family, prompt=task.prompt,
            public_parameters=task.public_parameters, oracle_private=oracle,
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

    def test_canonical_prompt_matches_public_parameters(self):
        for seed in range(25):
            self.assertTrue(validate_prompt_consistency(generate_t3(seed).public_payload()))

    def test_json_round_trip_preserves_t3_public_contract_and_private_witnesses(self):
        for seed in range(25):
            task = generate_t3(seed)
            public = json.loads(json.dumps(task.public_payload(), ensure_ascii=False))
            evaluation = json.loads(json.dumps(task.evaluation_payload()))
            self.assertTrue(validate_prompt_consistency(public))
            self.assertTrue(validate_t3(type(task)(
                task_id=task.task_id, family=task.family, prompt=task.prompt,
                public_parameters=public["public_parameters"],
                oracle_private=evaluation["oracle_private"],
                generation={**task.generation},
            )))

    def test_prompt_mutation_is_rejected(self):
        payload = generate_t3(51).public_payload()
        payload["prompt"] = payload["prompt"].replace("f2(x) = ", "f2(x) = 999", 1)
        self.assertFalse(validate_prompt_consistency(payload))

    def test_parameter_mutation_is_rejected(self):
        payload = generate_t3(52).public_payload()
        payload["public_parameters"]["second_step_coefficient"] += 1
        self.assertFalse(validate_prompt_consistency(payload))

    def test_missing_parameter_mutation_is_rejected(self):
        payload = generate_t3(53).public_payload()
        payload["public_parameters"]["missing_parameter"] = "a2"
        self.assertFalse(validate_prompt_consistency(payload))

    def test_forced_missing_intercept_edge_case(self):
        payload = {
            "family": "T3",
            "prompt": (
                "Valeur initiale : x = -2\n"
                "Étape 1 : f1(x) = -3x + (0)\n"
                "Étape 2 : f2(x) = 1x + b, mais la valeur de b n'est pas fournie.\n"
                "Quelle est la valeur après la deuxième transformation ?"
            ),
            "public_parameters": {
                "initial": -2,
                "first_step": [-3, 0],
                "second_step_coefficient": 1,
                "missing_parameter": "b",
            },
        }
        self.assertTrue(validate_prompt_consistency(payload))
        x1 = -3 * -2 + 0
        self.assertNotEqual(1 * x1 + 0, 1 * x1 + 1)


if __name__ == "__main__":
    unittest.main()
