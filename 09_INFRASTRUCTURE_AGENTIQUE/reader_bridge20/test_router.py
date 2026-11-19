#!/usr/bin/env python3
"""Reader20 regression tests: source-origin, independent checks, fail-closed routing."""
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from router import (
    SOURCE, SOURCE_BLOB, split_cases, parse_claim, evaluate_source,
    evaluate_exact, UnsupportedContract,
)
from independent_audit import audit, ref_congruence_count, ref_parity_bf
from read import safe_read


class AutomaticExactRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = safe_read(SOURCE, SOURCE_BLOB)
        cls.blocks = split_cases(cls.raw)
        cls.report = evaluate_source(cls.raw, SOURCE.as_posix())

    def test_all_source_blobs_and_exact_spans(self):
        self.assertEqual(len(self.blocks), 32)
        self.assertEqual(self.report["total_cases"], 32)
        self.assertEqual(len(self.report["decisions"]), 32)
        lines = self.raw.decode("utf-8").splitlines()
        for b in self.blocks:
            self.assertEqual([lines[i-1] for i in b["line_numbers"]], b["lines"])
        for r in self.report["decisions"]:
            self.assertEqual(r["source_blob"], self.report["source_blob"])
            if r["evidence"] if "evidence" in r else False:
                self.assertTrue(all(lines[x["line"]-1] == x["literal"]
                                    for x in r["evidence"]))
                self.assertTrue(all(x["source_blob"] == self.report["source_blob"]
                                    for x in r["evidence"]))
            self.assertFalse(r["promotion_allowed"])

    def test_all_three_routes_selected_without_solver_hint(self):
        self.assertEqual(self.report["route_counts"], {
            "exact_natural_product": 8,
            "finite_map_congruence_count": 8,
            "finite_binary_difference": 8,
        })
        self.assertEqual(self.report["routed_count"], 24)
        self.assertEqual(self.report["abstained_count"], 8)
        self.assertTrue(all(r["selected_verifier"] is None for r in
                            self.report["decisions"][24:]))

    def test_no_unexplained_promotion_and_independent_reference(self):
        final = audit(self.report, self.raw)
        self.assertTrue(final["success"], final)
        self.assertEqual(final["correct_exact_decisions"], 24)
        self.assertEqual(final["unsupported_cases_abstained"], 8)
        self.assertEqual(final["errors"], 0)
        self.assertEqual(final["single_fixed_verifier_baseline_max_correct_route"], 8)
        self.assertEqual(final["scientific_auto_promotions"], 0)
        self.assertFalse(final["source_gold_independent_human"])

    def test_adversarial_injection_not_an_instruction(self):
        control = self.report["decisions"][-1]
        self.assertEqual(control["case_id"], "C32")
        self.assertEqual(control["router_status"], "ABSTAIN_UNSUPPORTED_CONTRACT")
        self.assertIsNone(control["exact_result"])
        self.assertFalse(control["promotion_allowed"])

    def test_source_hash_tamper_fails_closed(self):
        mutated = self.raw.replace(b"29 * 5 = 145", b"29 * 5 = 146", 1)
        self.assertNotEqual(mutated, self.raw)
        with self.assertRaises(ValueError):
            # The source must first pass the frozen blob pin.
            path = HERE / "NO_SUCH_SOURCE"
            safe_read(path, SOURCE_BLOB)

    def test_missing_limits_and_operand_replacement_rejected(self):
        first = self.blocks[0]
        with self.assertRaises(UnsupportedContract):
            parse_claim({**first, "lines": first["lines"][:-1]})
        replaced = list(first["lines"])
        replaced[1] = "Énoncé: 29 * 6 = 145"
        with self.assertRaisesRegex(UnsupportedContract, "CHANGED_OPERANDS"):
            parse_claim({**first, "lines": replaced})

    def test_independent_counterexamples(self):
        self.assertEqual(ref_congruence_count([0, 1]), 2)
        self.assertTrue(ref_parity_bf(3, [(0, 1), (1, 2)]))
        self.assertFalse(ref_parity_bf(3, [(0, 1), (1, 2), (0, 2)]))

    def test_unsupported_math_never_routed(self):
        with self.assertRaisesRegex(UnsupportedContract, "UNKNOWN"):
            parse_claim({
                "lines": ["Hypothèses: a=1; b=2; domaine=N[0,999]",
                          "Énoncé: hypothèse de Riemann est vraie",
                          "Limites: entier naturel borné"]
            })


if __name__ == "__main__":
    unittest.main(verbosity=2)
