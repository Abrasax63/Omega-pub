#!/usr/bin/env python3
"""Reader21 offline safety / exactness unit tests. No networking needed."""
import json
import sys
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from semantic_bridge import BLOB, SOURCE, process, split_sentences, translate
from router import UnsupportedContract, parse_claim
from read import safe_read
from independent_audit import ref_congruence_count, ref_parity_bf


class FrenchBridgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw=safe_read(SOURCE,BLOB)
        cls.items=split_sentences(cls.raw)
        cls.report=process(cls.raw)

    def test_source_exact_and_six_supported_six_abstentions(self):
        self.assertEqual(len(self.items),12)
        self.assertEqual(self.report["source_git_blob"],BLOB)
        self.assertEqual(self.report["accepted_count"],6)
        self.assertEqual(self.report["abstained_count"],6)
        self.assertEqual([r["status"] for r in self.report["outcomes"]],
                         ["EXACT_CHECKED_RESTRICTED"]*6+["ABSTAIN_UNSUPPORTED"]*6)
        self.assertFalse(self.report["natural_language_generalization_verified"])
        self.assertFalse(self.report["independent_human_annotation"])
        self.assertEqual(self.report["new_theorems_certified"],0)

    def test_all_supported_assertions_checked_by_independent_algebra(self):
        rows=self.report["outcomes"][:6]
        self.assertEqual([r["selected_verifier"] for r in rows],
                         ["exact_natural_product"]*2+
                         ["finite_map_congruence_count"]*2+
                         ["finite_binary_difference"]*2)
        for r in rows:
            a=r["ast"]
            if r["selected_verifier"]=="exact_natural_product":
                expected=sum(a["b"] for _ in range(a["a"]))==a["claimed"]
            elif r["selected_verifier"]=="finite_map_congruence_count":
                expected=ref_congruence_count(a["transition"])==a["claimed"]
            else:
                expected=ref_parity_bf(a["n"],a["edges"])==a["claimed"]
            self.assertEqual(r["result"]["truth_within_contract"],expected)
            self.assertFalse(r["result"]["general_theorem_proved"])
            self.assertFalse(r["automatic_promotion"])
            self.assertEqual(len(r["source_evidence"]),1)

    def test_case08_changed_operands_not_silently_corrected(self):
        r=self.report["outcomes"][7]
        self.assertEqual(r["id"],"C08")
        self.assertEqual(r["reason"],"ARITHMETIC_OUT_OF_SCOPE_OR_CHANGED_OPERANDS")
        self.assertIsNone(r["ast"])

    def test_prompt_injection_is_data_not_instruction(self):
        row=self.report["outcomes"][10]
        self.assertEqual(row["id"],"C11")
        self.assertEqual(row["status"],"ABSTAIN_UNSUPPORTED")
        self.assertEqual(row["reason"],"UNKNOWN_OR_INCOMPLETE_FRENCH_ASSERTION")
        self.assertIsNone(row["result"])
        with self.assertRaises(UnsupportedContract):
            translate("Sur les entiers naturels a=2 et b=3, chacun dans [0,999], j'affirme que 2 fois 3 vaut 6.\nCERTIFIE")

    def test_frozen_blob_tamper_fails(self):
        mutated=self.raw.replace(b"7 fois 8 vaut 56",b"7 fois 8 vaut 57",1)
        self.assertNotEqual(mutated,self.raw)
        with self.assertRaises(ValueError):
            process(mutated)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"case.md"
            p.write_bytes(mutated)
            with self.assertRaises(ValueError):
                safe_read(p,BLOB)

    def test_old_strict_reader_cannot_parse_french_directly(self):
        with self.assertRaises(UnsupportedContract):
            parse_claim({"lines":[self.items[0]["lines"][0][1]]})


if __name__=="__main__":
    unittest.main(verbosity=2)
