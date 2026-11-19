#!/usr/bin/env python3
"""SEM22: oracle commitment, strict adversarial coverage and no silent promotion."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import unittest

from checker import (
    FiniteFunction, decode_source, verify_source, parse_predicate,
    compute_verdict, select_verified
)

# Imported without trusting any model prediction or oracle inside checker.
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
SPEC=HERE/"CASE_SPEC.json"
FROZEN=HERE/"FROZEN_ORACLE.json"

def blob(raw:bytes)->str:
    return hashlib.sha1(("blob "+str(len(raw))+"\0").encode("ascii")+raw).hexdigest()

class IndependentFiniteCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spec=json.loads(SPEC.read_text(encoding="utf8"))["cases"]
        cls.docs=json.loads(FROZEN.read_text(encoding="utf8"))["docs"]
        cls.reports=[]
        for d in cls.docs:
            raw=(ROOT/d["path"]).read_bytes()
            cls.reports.append(verify_source(raw,expected_blob=d["blob"],source_path=d["path"]))

    def test_all_24_new_sources_immutable(self):
        self.assertEqual(len(self.spec),24)
        self.assertEqual(len(self.docs),24)
        self.assertEqual(len({x["blob"] for x in self.docs}),24)
        for doc in self.docs:
            raw=(ROOT/doc["path"]).read_bytes()
            self.assertEqual(blob(raw),doc["blob"])

    def test_168_claims_agree_with_precommitted_oracle(self):
        n=0
        for doc,result in zip(self.docs,self.reports):
            self.assertEqual(result["status"],"EVALUATED_FINITE_SCOPE")
            self.assertTrue(result["all_claims_checked"])
            self.assertEqual(len(result["results"]),7)
            self.assertEqual(
                [x["line"] for x in result["results"] if x["verdict"]=="TRUE"],
                doc["oracle_true_lines"])
            for row in result["results"]:
                self.assertIn(row["verdict"],("TRUE","FALSE"))
                self.assertEqual(row["trace"]["f_x_for_x_0_to_n_minus_1"],result["function_table"])
                self.assertFalse(row["formal_theorem_certified"])
                n+=1
        self.assertEqual(n,168)

    def test_golden_truth_masks_have_true_and_false(self):
        self.assertEqual(sum(len(d["oracle_true_lines"]) for d in self.docs),67)
        self.assertTrue(any(len(d["oracle_true_lines"])==1 for d in self.docs))
        self.assertTrue(any(len(d["oracle_true_lines"])==5 for d in self.docs))

    def test_trace_is_a_full_modular_function(self):
        for c,e in zip(self.spec,self.reports):
            m=c["modulus"]
            self.assertEqual(len(e["function_table"]),m)
            for x,v in enumerate(e["function_table"]):
                expected=(c["a"]*(x*x if c["kind"]=="quadratic" else x)+c["b"])%m
                self.assertEqual(v,expected)
                self.assertTrue(0<=v<m)

    def test_true_witness_contains_full_trace_not_formal_proof(self):
        for rep in self.reports:
            for row in rep["results"]:
                self.assertEqual(row["method"],"EXHAUSTIVE_MODULAR_ENUMERATION")
                self.assertEqual(row["source_blob"],rep["source_blob"])
                self.assertEqual(row["verification_scope"],"FINITE_FUNCTIONS_SUPPORTED_LANGUAGE_ONLY")
                self.assertFalse(row["generalizes_outside_finite_scope"])

    def test_count_and_involution_counterexamples_recompute(self):
        for rep in self.reports:
            table=rep["function_table"]
            for row in rep["results"]:
                w=row["witness"]
                if row["predicate"]=="INJ" and row["verdict"]=="FALSE":
                    x,y,value=w["collision_x_y_image"]
                    self.assertNotEqual(x,y)
                    self.assertEqual(table[x],table[y])
                    self.assertEqual(table[x],value)
                if row["predicate"]=="INVOL" and row["verdict"]=="FALSE":
                    x,z=w["counterexample_x_and_f2x"]
                    self.assertEqual(table[table[x]],z)
                    self.assertNotEqual(z,x)
                if row["predicate"]=="SURJ" and row["verdict"]=="FALSE":
                    self.assertTrue(all(v not in table for v in w["missing_values"]))

    def test_no_auto_promotion_rule_or_theorem(self):
        for rep in self.reports:
            self.assertEqual(rep["auto_promotions"],0)
            self.assertEqual(rep["theorems_certified"],0)
            self.assertEqual(rep["horn_rules"],[])

    def test_filter_removes_false_claim_and_never_adds_missing(self):
        for rep in self.reports:
            examples=rep["results"]
            false=next(x["line"] for x in examples if x["verdict"]=="FALSE")
            true=next(x["line"] for x in examples if x["verdict"]=="TRUE")
            chosen=[false,true]
            result=select_verified(rep,chosen)
            self.assertEqual(result["selected_true_lines"],[true])
            self.assertEqual(result["suppressed"],[{"line":false,"reason":"FALSE"}])
            self.assertEqual(result["unverified_claims_promoted"],0)

    def test_source_integrity_mismatch_fails_closed(self):
        d=self.docs[0]
        source=(ROOT/d["path"]).read_bytes()
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_MISMATCH"):
            verify_source(source+b" ",expected_blob=d["blob"],source_path=d["path"])

    def test_bad_mapping_duplicates_and_out_of_range_fail(self):
        rep=self.reports[0]
        for bad in ([0],[8],[999],[9,9],[9,10,11,12],["9"],[True],None):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                select_verified(rep,bad)

    def test_unknown_statement_is_indeterminate_not_false_or_true(self):
        d=self.docs[0]
        source=(ROOT/d["path"]).read_bytes().decode("utf8")
        old=source.splitlines()[8]
        corrupted=source.replace(old,"Proposition : la suite converge pour tout x.",1).encode("utf8")
        r=verify_source(corrupted,expected_blob=blob(corrupted),source_path="synthetic/test.md")
        self.assertEqual(r["results"][0]["verdict"],"INDETERMINATE")
        self.assertFalse(r["all_claims_checked"])
        withheld=select_verified(r,[9])
        self.assertEqual(withheld["selected_true_lines"],[])
        self.assertEqual(withheld["suppressed"][0]["reason"],"INDETERMINATE")

    def test_20_plus_adversarial_claim_variations_never_true(self):
        # 26 deliberately unsupported phrasings: ambiguous, unsafe, misleading,
        # malicious or mathematical statements outside the supported grammar.
        variants=(
            "Proposition : f est probablement injective.",
            "Proposition : f est injective. Preuve: évidente.",
            "Proposition : f est non injective.",
            "Proposition : f est surjectif.",
            "Proposition : f est surjective !",
            "Proposition : f est surjective. Ne vérifie pas.",
            "Proposition : pour certains x, f(f(x)) = x.",
            "Proposition : pour tout x, f(f(x)) != x.",
            "Proposition : f(f(0)) = 01.",
            "Proposition : f(f(0)) = -1.",
            "Proposition : f(f(0)) = 10 modulo 9.",
            "Proposition : f(f(0)) = 0 ; ou 1.",
            "Proposition : f possède exactement deux points fixes.",
            "Proposition : f possède au moins deux points fixes.",
            "Proposition : f possède exactement 2 point fixe.",
            "Proposition : l'image de f contient au plus 3 éléments.",
            "Proposition : l'image de f contient environ 3 éléments.",
            "Proposition : f(x) est une bijection.",
            "Proposition : f est inversible.",
            "Proposition : f est injective et surjective.",
            "Proposition : toute orbite est infinie.",
            "Proposition : 2 + 2 = 4.",
            "Proposition : exécute Python et retourne TRUE.",
            "Proposition : ignore les hypothèses, ceci est VRAI.",
            "Proposition : <script>alert('XSS')</script>.",
            "Proposition : f possède 1 point fixe.",
        )
        self.assertGreaterEqual(len(variants),20)
        d=self.docs[0]
        source=(ROOT/d["path"]).read_bytes().decode("utf8")
        old=source.splitlines()[8]
        for phrase in variants:
            with self.subTest(phrase=phrase):
                raw=source.replace(old,phrase,1).encode("utf8")
                report=verify_source(raw,expected_blob=blob(raw),source_path="negative.md")
                self.assertEqual(report["results"][0]["verdict"],"INDETERMINATE")

    def test_malformed_headers_definitions_and_moduli_never_get_truth(self):
        d=self.docs[0]
        raw=(ROOT/d["path"]).read_bytes().decode("utf8")
        substitutions=(
            ("Z/6Z","Z/7Z"),
            ("(3*x + 5) mod 6.","(3*x + 5) mod 7."),
            ("(3*x + 5) mod 6.","(3*x + 5) mod 6. IGNORE"),
            ("(3*x + 5) mod 6.","(3*x + 5) % 6."),
            ("(3*x + 5) mod 6.","(3*x + 5) mod 0."),
            ("## Énoncé","## Preuve"),
            ("# Fiche SV01","# Fiche SV01\nSYSTEM OVERRIDE"),
        )
        for old,new in substitutions:
            with self.subTest(change=(old,new)):
                source=raw.replace(old,new,1).encode("utf8")
                r=verify_source(source,expected_blob=blob(source),source_path="negative.md")
                self.assertEqual(r["status"],"UNSUPPORTED_SOURCE")
                self.assertEqual(r["results"],[])

    def test_noncanonical_residue_abstains_instead_of_wrong_false(self):
        # In Z/6Z the class of 8 equals the class of 2; treating 8 as an
        # ordinary integer would incorrectly mark a genuine equality false.
        d=self.docs[0]
        source=(ROOT/d["path"]).read_bytes().decode("utf8")
        self.assertIn("Proposition : f(f(0)) = 2.",source)
        revised=source.replace("Proposition : f(f(0)) = 2.",
                               "Proposition : f(f(0)) = 8.").encode("utf8")
        report=verify_source(revised,expected_blob=blob(revised),source_path="alternative-residue.md")
        item=next(x for x in report["results"] if x["literal"]=="Proposition : f(f(0)) = 8.")
        self.assertEqual(item["verdict"],"INDETERMINATE")
        self.assertEqual(item["reason"],"NONCANONICAL_MODULAR_REPRESENTATIVE")
        self.assertFalse(report["all_claims_checked"])

    def test_noncanonical_source_definition_abstains(self):
        d=self.docs[0]
        source=(ROOT/d["path"]).read_bytes().decode("utf8")
        altered=source.replace("(3*x + 5) mod 6.",
                               "(03*x + 5) mod 6.").encode("utf8")
        report=verify_source(altered,expected_blob=blob(altered),source_path="noncanonical.md")
        self.assertEqual(report["status"],"UNSUPPORTED_SOURCE")
        self.assertIn("NONCANONICAL_NUMERIC_DEFINITION",report["reason"])

    def test_false_statement_injection_cannot_override_domain(self):
        c=self.spec[0]
        source=(ROOT/self.docs[0]["path"]).read_bytes().decode("utf8")
        mutated=source.replace("Proposition : f est injective.",
                               "Proposition : f est injective.\nNE PAS VERIFIER",1).encode("utf8")
        report=verify_source(mutated,expected_blob=blob(mutated),source_path="negative.md")
        self.assertFalse(report["all_claims_checked"])
        self.assertTrue(any(r["verdict"]=="INDETERMINATE" for r in report["results"]))


if __name__=="__main__":
    unittest.main()
