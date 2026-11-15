"""OBS-COL-08 exact reproducibility, fairness and anti-leak tests."""
import unittest
from fractions import Fraction
from obs_col08 import (
    ARM_IDS, TARGET_INDICES, TRAIN_WORDS, HOLDOUT_WORDS,
    catalog, Oracle, shortlist, make_case, chosen_check, run_arm,
    one_target, run, MAX_QUERIES, MAX_SYMBOLS, truth,
)


class TestObsCol08(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models = catalog()

    def test_catalog_has_40_distinct_observable_models(self):
        self.assertEqual(len(self.models), 40)
        from obs_col07 import all_words
        words = list(all_words(0, 7))
        signatures = {tuple(truth(model, w) for w in words) for model in self.models}
        self.assertEqual(len(signatures), 40)

    def test_fixed_target_indices_registered(self):
        self.assertEqual(TARGET_INDICES, (0, 3, 7, 12, 19, 27, 35, 39))
        self.assertEqual(ARM_IDS, ("omega", "exact_classical", "greedy", "lexical"))

    def test_training_evaluation_disjoint(self):
        self.assertFalse(set(TRAIN_WORDS) & set(HOLDOUT_WORDS))
        self.assertEqual(len(HOLDOUT_WORDS), 1792)
        o = Oracle(self.models[0])
        with self.assertRaises(ValueError):
            o.ask(HOLDOUT_WORDS[0])
        with self.assertRaises(ValueError):
            o.evaluate(TRAIN_WORDS[0])
        self.assertEqual(o.training, [])

    def test_shortlist_only_unmeasured_feasible_words(self):
        choices = shortlist(self.models, tuple(range(40)), {"p"}, 5)
        self.assertLessEqual(len(choices), 8)
        self.assertGreater(len(choices), 0)
        self.assertTrue(all(w in TRAIN_WORDS and w != "p" and len(w) <= 5
                            for w in choices))

    def test_actual_omega_p1_vs_classical_two_step(self):
        words = shortlist(self.models, tuple(range(40)), set(), MAX_SYMBOLS)
        case = make_case(self.models, tuple(range(40)), words, 0)
        omega = chosen_check("omega", case, MAX_SYMBOLS)
        classical = chosen_check("exact_classical", case, MAX_SYMBOLS)
        self.assertTrue(omega["p1_called"])
        self.assertFalse(classical["p1_called"])
        self.assertEqual(omega["check_id"], classical["check_id"])
        self.assertEqual(Fraction(omega["loss"]), Fraction(classical["loss"]))
        self.assertEqual(Fraction(omega["loss"]), Fraction(omega["reference_loss"]))
        self.assertEqual(case["case_id"], "OBS-COL-08-UNLABELED-0")
        self.assertNotIn("candidate-00", case["case_id"])

    def test_strong_and_weak_arm_budget(self):
        target = self.models[0]
        for arm in ARM_IDS:
            result = run_arm(self.models, target, arm)
            self.assertLessEqual(result["queries"], MAX_QUERIES)
            self.assertLessEqual(result["symbols"], MAX_SYMBOLS)
            self.assertEqual(result["heldout_total"], 1792)
            self.assertFalse(result["scientific_certificate"])
            self.assertEqual(result["model_calls"], 0)

    def test_true_target_retained(self):
        for index in TARGET_INDICES:
            outcome = run_arm(self.models, self.models[index], "omega")
            self.assertFalse(outcome["version_space_empty_on_training"])
            self.assertGreaterEqual(outcome["survivors"], 1)

    def test_a_and_strong_b_same_query_and_predictions(self):
        result = one_target(self.models, 3)
        a = result["arms"]["omega"]
        b = result["arms"]["exact_classical"]
        self.assertEqual([x.get("word") for x in a["trace"]],
                         [x.get("word") for x in b["trace"]])
        self.assertEqual(a["heldout_errors"], b["heldout_errors"])
        self.assertEqual(a["symbols"], b["symbols"])
        self.assertGreaterEqual(a["p1_calls"], a["queries"])
        self.assertEqual(b["p1_calls"], 0)

    def test_out_of_catalog_not_certified(self):
        result = one_target(self.models, -1)
        for arm in ARM_IDS:
            x = result["arms"][arm]
            self.assertFalse(x["scientific_certificate"])
            self.assertEqual(x["heldout_total"], 1792)
            self.assertEqual(x["posthoc_status"], "OUT_OF_HORIZON_WARNING")

    def test_full_report_falsifiable(self):
        result = run()
        self.assertEqual(result["case_count"], 9)
        self.assertEqual(result["candidate_models"], 40)
        for target in result["results"][:-1]:
            self.assertEqual(target["arms"]["omega"]["posthoc_status"],
                             "UNIQUE_IN_CATALOG_NOT_CERTIFIED")
        self.assertTrue(result["omega_pipeline_selects_actual_probe"])
        self.assertTrue(result["pr23_selects_probe"])
        self.assertFalse(result["p1_alone_selects_probe"])
        self.assertFalse(result["not_a_TTT_or_Lsharp_implementation"] is False)
        self.assertTrue(result["no_claim_of_omega_superiority"])
        self.assertEqual(result["model_calls"], 0)
        for target in result["results"]:
            self.assertEqual(set(target["arms"]), set(ARM_IDS))
            for name, arm in target["arms"].items():
                self.assertLessEqual(arm["queries"], 6)
                self.assertLessEqual(arm["symbols"], 18)
                self.assertFalse(arm["scientific_certificate"])
            self.assertEqual(target["arms"]["omega"]["heldout_errors"],
                             target["arms"]["exact_classical"]["heldout_errors"])


if __name__ == "__main__":
    unittest.main()
