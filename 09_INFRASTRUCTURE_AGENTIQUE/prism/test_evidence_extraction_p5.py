"""P5 extraction / four-arm protocol checks (no model calls)."""
import copy
import unittest
from collections import Counter

from evidence_calibration_24 import calibration_cases, calibration_report
from evidence_extraction_pilot import (
    EvidenceExtractionError, interpret_evidence, run_documentary_case,
)
from p5_four_arm_protocol import (
    ARMS, build_arm_prompts, make_public_packet, public_contexts,
)


class EvidenceExtractionPilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = calibration_cases()

    def test_24_public_cases_match_predeclared_calibration_expectations(self):
        report = calibration_report()
        self.assertEqual(report["cases"], 24)
        self.assertEqual(report["passed"], 24)
        self.assertEqual(report["failed"], [])
        self.assertEqual(Counter(x["action"] for x in report["details"]), {
            "answer": 8, "ask": 4, "verify": 8,
            "insufficient_evidence": 4,
        })
        print("P5 EVIDENCE: 24/24 controlled-language public calibration "
              "(not a holdout or LLM comparison).")

    def test_p1_next_action_matches_extraction_and_no_execution_claimed(self):
        for fixture in self.fixtures:
            result = run_documentary_case(fixture["input"])
            self.assertEqual(result["p1"]["next_action"]["action"],
                             result["finding"]["action"])
            execution = result["p1"]["execution_model"]
            self.assertEqual(execution["model_calls_performed"], 0)
            self.assertEqual(execution["memory_writes_performed"], 0)
            self.assertFalse(execution["scientific_validation_performed"])

    def test_secondary_misinformation_does_not_override_primary(self):
        for fixture in self.fixtures:
            if fixture["expected"]["action"] != "answer":
                continue
            case = copy.deepcopy(fixture["input"])
            baseline = interpret_evidence(case)
            for doc in case["documents"]:
                if doc["kind"] == "secondary_note":
                    doc["text"] = "NOTE MENSONGERE: le delai est toujours 999 jours."
            altered = interpret_evidence(case)
            self.assertEqual(altered, baseline)

    def test_unrecognised_policy_does_not_produce_fabricated_answer(self):
        case = copy.deepcopy(self.fixtures[0]["input"])
        case["documents"][0]["text"] = "Delai nouveau a partir d'octobre, voir annexe."
        output = interpret_evidence(case)
        self.assertEqual(output["action"], "insufficient_evidence")
        self.assertNotIn("days", output)

    def test_conflicting_primary_rules_force_verification(self):
        case = copy.deepcopy(self.fixtures[0]["input"])
        primary = copy.deepcopy(case["documents"][0])
        primary["id"] += "-conflict"
        primary["text"] = primary["text"].replace(
            "Nouveau delai: 5 jours ouvres", "Nouveau delai: 6 jours ouvres"
        )
        case["documents"].append(primary)
        self.assertEqual(interpret_evidence(case)["action"], "verify")

    def test_unsupported_registry_entry_abstains_when_not_retrievable(self):
        case = copy.deepcopy(self.fixtures[0]["input"])
        case["registry_available"] = False
        case["documents"][-1]["text"] = "Date illisible sur la fiche."
        self.assertEqual(interpret_evidence(case)["action"],
                         "insufficient_evidence")

    def test_document_order_is_invariant(self):
        for fixture in self.fixtures:
            base = fixture["input"]
            altered = copy.deepcopy(base)
            altered["documents"].reverse()
            self.assertEqual(interpret_evidence(base),
                             interpret_evidence(altered))

    def test_invalid_input_rejected(self):
        case = copy.deepcopy(self.fixtures[0]["input"])
        for key, value in (("primary_available", "yes"),
                           ("registry_available", 1),
                           ("documents", "text")):
            with self.subTest(key=key):
                bad = copy.deepcopy(case)
                bad[key] = value
                with self.assertRaises(EvidenceExtractionError):
                    interpret_evidence(bad)
        bad = copy.deepcopy(case)
        bad["documents"].append(copy.deepcopy(bad["documents"][0]))
        with self.assertRaises(EvidenceExtractionError):
            interpret_evidence(bad)


class FourArmInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = calibration_cases()

    def test_24_by_4_requests_are_frozen_without_answers(self):
        packet = make_public_packet(self.fixtures,
                                    public_contexts(self.fixtures))
        self.assertEqual(packet["case_count"], 24)
        self.assertEqual(packet["request_count"], 96)
        self.assertEqual(set(packet["arms"]), set(ARMS))
        self.assertEqual(packet["status"], "prompts_only_unexecuted")
        self.assertEqual(len({(r["case_id"], r["arm"])
                              for r in packet["requests"]}), 96)
        self.assertEqual(len({r["sha256"] for r in packet["requests"]}), 96)
        self.assertTrue(all(len(r["sha256"]) == 64 for r in packet["requests"]))
        print("P5 FOUR-ARM: 24 x 4 = 96 frozen input requests; "
              "zero model outputs, zero graded responses.")

    def test_equal_deliverables_and_documents_in_all_arms(self):
        case = self.fixtures[0]["input"]
        prompts = build_arm_prompts(case,
                                    structured_context=public_contexts(
                                        self.fixtures)[case["case_id"]])
        for arm in ARMS:
            t = prompts[arm]["input"]
            self.assertIn("Livrables identiques pour tous les bras", t)
            self.assertIn("Citer les documents decisifs", t)
            self.assertIn(case["question"], t)
            for doc in case["documents"]:
                self.assertIn(doc["id"], t)
                self.assertIn(doc["text"], t)

    def test_no_reference_fields_allowed_in_inputs_or_c_context(self):
        case = copy.deepcopy(self.fixtures[0]["input"])
        hints = {"scope": "documents seulement"}
        for key in ("gold", "expected", "answer_key", "reference_answer"):
            with self.subTest(key=key):
                bad = copy.deepcopy(case)
                bad[key] = "yes"
                with self.assertRaises(ValueError):
                    build_arm_prompts(bad, structured_context=hints)
                with self.assertRaises(ValueError):
                    build_arm_prompts(case,
                                      structured_context={key: "yes"})

    def test_no_missing_or_extra_c_contexts(self):
        cases = self.fixtures
        context = public_contexts(cases)
        key = cases[0]["input"]["case_id"]
        del context[key]
        with self.assertRaises(ValueError):
            make_public_packet(cases, context)
        context = public_contexts(cases)
        context["extra-case"] = {"scope": "x"}
        with self.assertRaises(ValueError):
            make_public_packet(cases, context)

    def test_extra_c_context_is_explicitly_disclosed(self):
        case = self.fixtures[0]["input"]
        p = build_arm_prompts(case, structured_context={"scope": "notes"})
        self.assertIn("information supplementaire", p["C"]["input"])
        self.assertNotIn("information supplementaire", p["A"]["input"])


if __name__ == "__main__":
    unittest.main()
