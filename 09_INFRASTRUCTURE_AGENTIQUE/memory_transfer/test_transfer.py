"""No-network controls for OMEGA-TRANSFER-01; no model is invoked here."""
import unittest

from transfer import (
    EXPERIMENT, MONO, TARGETS, check_public, digest, discriminant_suite,
    experiment, form_notes, learn_one, prepare_candidates, reserved_inputs,
    result_for_id, train_bank, training_ids,
)


class MemoryTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidates = prepare_candidates()
        cls.learned = train_bank(cls.candidates)

    def test_four_leave_one_fault_type_out_folds_and_negative_control(self):
        self.assertEqual(tuple(self.candidates), TARGETS)
        for target in TARGETS:
            ids = training_ids(target)
            self.assertNotIn(target, ids)
            self.assertEqual(len(ids), 4 if target == "C5" else 3)
            note = form_notes(target, self.learned, "COMMON_RCE_NOTE")
            self.assertEqual(note["lesson_ids"], ids)
            self.assertEqual(len(note["memory"]), len(note["control"]))
            self.assertNotEqual(note["memory"], note["control"])
            self.assertNotIn("Prior " + target + ":", note["memory"])

    def test_all_training_rules_are_verified_on_strong_public_suite(self):
        strong = discriminant_suite()
        for ident in MONO:
            row = self.learned[ident]
            self.assertEqual(row["verified_public_cases"], len(strong))
            self.assertTrue(row["candidate_source_sha256"])
            self.assertGreaterEqual(row["oracle_cases_checked"], len(strong))

    def test_reserved_inputs_are_seeded_and_not_in_public_suites(self):
        a = reserved_inputs(616161)
        b = reserved_inputs(616161)
        c = reserved_inputs(616162)
        self.assertEqual(digest(a), digest(b))
        self.assertNotEqual(digest(a), digest(c))
        self.assertEqual(len(a), 28)
        public = {(tuple(x["rows"]), x["steps"])
                  for x in __import__("transfer").public_suite() + discriminant_suite()}
        self.assertTrue(all((tuple(x["rows"]), x["steps"]) not in public for x in a))
        self.assertTrue(any(x["steps"] == 0 for x in a))

    def test_negative_two_fault_case_has_no_single_line_strong_repair(self):
        task = self.candidates["C5"]
        self.assertGreater(len(task["shortlist"]), 0)
        self.assertFalse(any(check_public(c["source"], discriminant_suite())["passed"]
                             for c in task["shortlist"]))

    def test_invalid_id_is_not_silently_replaced(self):
        item = result_for_id(self.candidates["C1"], "P99",
                             reserved_inputs(12345), discriminant_suite())
        self.assertFalse(item["correct"])
        self.assertEqual(item["status"], "INVALID_ID")

    def test_full_offline_pipeline_with_fixed_choices_is_not_model_result(self):
        seen = []
        def fake(source, shortlist, note, arm):
            seen.append((arm, note))
            # Controlled stub is not a Qwen call; this test claims no neural gain.
            return {"called": False, "status": "VALID_ID",
                    "selected_id": shortlist[0]["id"]}
        result = experiment(fake, reserve_seed=900900)
        self.assertEqual(result["experiment"], EXPERIMENT)
        self.assertEqual(len(result["evaluations"]), 5)
        self.assertEqual(len(seen), 10)
        self.assertEqual(result["model_calls_attempted"], 0)
        self.assertEqual(result["comparison"]["memory_minus_control_correct"], 0)
        self.assertFalse(result["comparison"]["token_count_parity_confirmed"])
        self.assertFalse(result["comparison"]["novel_general_intelligence_demonstrated"])
        self.assertFalse(result["automatic_core_promotion"])
        for task in result["evaluations"]:
            self.assertEqual(task["outcomes"]["memory"]["selected_id"],
                             task["outcomes"]["control"]["selected_id"])
            self.assertNotIn(task["task"], task["training_tasks"])
            self.assertEqual(len(task["call_order"]), 2)
        self.assertFalse(result["evaluations"][-1]["outcomes"]["first_weak"]["correct"])


if __name__ == "__main__":
    unittest.main()
