"""OBS-COL-06: actual-integrated, deterministic, no-mock tests."""
import unittest
from fractions import Fraction
from obs_col06 import (
    ACTIONS, CATALOG, OUTSIDE, WORLDS, PROBES, RESERVED, INITIAL,
    WorldOracle, trace, candidates_from_observations, make_case,
    markov_conflict, observed_walsh, score_episode, run,
    plan_with_variable_horizon, independent_two_step_oracle,
)


class TestObsCol06(unittest.TestCase):
    def test_candidates_initially_unidentifiable(self):
        for rule in WORLDS:
            obs = [(p, trace(rule, *p)) for p in INITIAL]
            self.assertEqual(set(candidates_from_observations(obs)), set(CATALOG))

    def test_probe_and_reserve_are_disjoint(self):
        self.assertFalse(set(PROBES) & set(RESERVED))
        self.assertFalse(set(INITIAL) & set(RESERVED))
        self.assertEqual(len(PROBES), 8)
        self.assertEqual(len(RESERVED), 6)

    def test_oracle_rejects_reserved_during_learning(self):
        o = WorldOracle("PAIR01")
        with self.assertRaises(ValueError):
            o.query(RESERVED[0])
        with self.assertRaises(ValueError):
            o.evaluate(PROBES[0])

    def test_competing_collective_models(self):
        self.assertNotEqual(trace("PAIR01", 3, ("read",)),
                            trace("TRIPLE012", 3, ("read",)))
        self.assertNotEqual(trace("PAIR02", 5, ("read",)),
                            trace("TRIPLE012", 5, ("read",)))
        self.assertNotEqual(trace("TRIPLE012", 7, ("read",)),
                            trace("MEMORY_SET", 7, ("read",)))

    def test_memory_variants_are_not_preordered_degrees(self):
        self.assertEqual(trace("MEMORY_TOGGLE", 0, ("read",)), (0, 0))
        self.assertEqual(trace("MEMORY_TOGGLE", 0, ("prime", "read")), (0, 0, 8))
        self.assertEqual(trace("MEMORY_TOGGLE", 0, ("prime", "prime", "read")),
                         (0, 0, 0, 0))
        self.assertEqual(trace("MEMORY_SET", 0, ("prime", "prime", "read")),
                         (0, 0, 0, 8))

    def test_outside_is_train_compatible_but_holdout_differs(self):
        for probe in INITIAL + PROBES:
            if probe[0] == 0 and probe[1].count("prime") <= 2:
                self.assertEqual(trace("MEMORY_SET", *probe), trace(OUTSIDE, *probe))
        self.assertNotEqual(trace("MEMORY_SET", *RESERVED[0]),
                            trace(OUTSIDE, *RESERVED[0]))

    def test_markov_conflict_is_direct_observation_witness(self):
        data = [(INITIAL[0], trace("MEMORY_TOGGLE", *INITIAL[0])),
                (PROBES[3], trace("MEMORY_TOGGLE", *PROBES[3]))]
        witness = markov_conflict(data)
        self.assertIsNotNone(witness)
        self.assertEqual(witness["same_visible_input"], 0)
        self.assertEqual(witness["same_action"], "read")
        self.assertNotEqual(witness["witness_a"]["after"], witness["witness_b"]["after"])
        controls = [(p, trace("PAIR01", *p)) for p in INITIAL + PROBES]
        self.assertIsNone(markov_conflict(controls))

    def test_real_p1_and_exact_independent_two_step(self):
        obs = [(p, trace("PAIR01", *p)) for p in INITIAL]
        case = make_case(CATALOG, obs, "test", 0)
        omega = plan_with_variable_horizon(case, max_depth=2, max_cost_milli=60)
        classical = independent_two_step_oracle(case, budget_milli=60)
        self.assertEqual(omega["p1"]["next_action"]["action"], "verify")
        self.assertEqual(Fraction(omega["optimization"]["expected_total_loss"]),
                         Fraction(classical["expected_total_loss"]))

    def test_walsh_coefficients_are_formatted(self):
        obs = [(p, trace("PAIR01", *p)) for p in INITIAL]
        coeff = observed_walsh(obs)
        self.assertEqual(set(coeff), set("0123"))
        self.assertTrue(all(Fraction(value) == 1 for value in coeff.values()))

    def test_postselection_memory_certificate_amendment(self):
        for rule in ("MEMORY_TOGGLE", "MEMORY_SET"):
            episode = score_episode(rule)
            witness = episode["markov_counterexample_training"]
            self.assertIsNotNone(witness)
            self.assertEqual(witness["same_action"], "read")
            self.assertNotEqual(witness["witness_a"]["after"],
                                witness["witness_b"]["after"])
            if rule == "MEMORY_TOGGLE":
                self.assertEqual(episode["post_run_diagnostic"]["status"],
                                 "DIRECT_NONMARKOV_WITNESS")
                self.assertEqual(episode["p1_diagnostic_calls"], 1)
            self.assertLessEqual(episode["active_queries"], 5)

    def test_six_episodes_and_no_false_certificates(self):
        report = run()
        self.assertEqual(report["model_calls"], 0)
        self.assertFalse(report["open_world_discovery"])
        self.assertEqual(len(report["episodes"]), 6)
        for episode, rule in zip(report["episodes"][:5], CATALOG):
            self.assertEqual(episode["status"], "COMPATIBLE_WITH_TESTED_REPRESENTATION")
            self.assertEqual(episode["reported_family_after_heldout_gate"], rule)
            self.assertEqual(episode["heldout_correct"], 6)
            self.assertLessEqual(episode["active_queries"], 5)
            self.assertTrue(episode["all_baseline_scores_equal"])
        outside = report["episodes"][-1]
        self.assertEqual(outside["status"], "OUT_OF_CATALOG_WARNING")
        self.assertIsNone(outside["reported_family_after_heldout_gate"])
        self.assertLess(outside["heldout_correct"], 6)
        self.assertTrue(outside["all_baseline_scores_equal"])


if __name__ == "__main__":
    unittest.main()
