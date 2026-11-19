#!/usr/bin/env python3
"""DUAL25: two independent algorithms, source fidelity gate, false consensus."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/"typed24"))
sys.path.insert(0,str(HERE.parent/"reader_bridge12"))
from read import blob as git_blob
from adapter import evaluate as formalizer_a
from token_formalizer_b import parse as formalizer_b, definition_ir, claim_ir
from consensus import reconcile, inspect, counterinterpretation_witness, exact_from_typed
from experiment import controlled, external, review_packet, check_sem22_legacy, read_manifest


class DualSourceAgreement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.packet_inputs=controlled()
        cls.byid={x["id"]:x for x in cls.rows}
        cls.manifest=read_manifest()
        cls.reports={}
        for d in cls.manifest["documents"]:
            raw=(ROOT/d["path"]).read_bytes()
            cls.reports[d["id"]]={
                "raw":raw, "ref":d,
                "a":formalizer_a(raw,expected_blob=d["blob"],source_path=d["path"]),
                "b":formalizer_b(raw,expected_blob=d["blob"],source_path=d["path"]),
            }

    def test_frozen_sources_and_24_cases_replayed(self):
        self.assertEqual(len(self.rows),24)
        self.assertEqual(len({r["source_blob"] for r in self.rows}),24)
        for case in self.reports.values():
            self.assertEqual(git_blob(case["raw"]),case["ref"]["blob"])

    def test_formalizer_b_is_alternate_token_stream_grammar(self):
        source=(HERE/"token_formalizer_b.py").read_text(encoding="utf8")
        self.assertIn("class Stream",source)
        self.assertIn("def tokens(",source)
        self.assertIn("def definition_ir",source)
        self.assertNotIn("import adapter",source)
        self.assertNotIn("from adapter",source)
        self.assertNotIn("from typed24",source)

    def test_two_parser_output_counts(self):
        counts={}
        for x in self.rows:
            counts[x["status"]]=counts.get(x["status"],0)+1
        self.assertEqual(counts.get("AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"),13)
        self.assertEqual(counts.get("WITHHELD_AMBIGUOUS"),4)
        self.assertEqual(counts.get("WITHHELD_UNSUPPORTED"),7)

    def test_agreed_ir_contains_same_domain_operation_predicate_quantifier(self):
        for k,x in self.byid.items():
            if x["status"]!="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN":
                continue
            self.assertEqual(x["A_definition"],x["B_definition"])
            self.assertEqual(len(x["A_candidates"]),1)
            self.assertEqual(x["A_candidates"][0],x["B_candidate"])
            self.assertIn(x["exact_finite_verdict"],("TRUE","FALSE"))
            self.assertFalse(x["human_fidelity_verified"])

    def test_legacy_exact_calculus_still_handles_168_claims(self):
        self.assertEqual(check_sem22_legacy(),168)

    def test_difference_of_formalizations_is_not_solved_by_majority(self):
        for item in ("TA04","TA05","TA12"):
            self.assertEqual(self.byid[item]["status"],"WITHHELD_AMBIGUOUS")
            self.assertEqual(len(self.byid[item]["A_candidates"]),2)
            self.assertEqual(self.byid[item]["B_candidate"],
                             self.byid[item]["A_candidates"][0])
            # One B interpretation matches the A alternative, yet still withheld.
            self.assertIsNone(self.byid[item]["exact_finite_verdict"])

    def test_identical_truth_on_current_case_is_not_equivalence(self):
        trial=self.reports["TA05"]
        self.assertEqual(trial["a"]["status"],"AMBIGUOUS")
        readings=trial["a"]["interpretations"]
        self.assertEqual(
            [x["local_calculation"]["verdict"] for x in readings],
            ["FALSE","FALSE"]
        )
        witness=counterinterpretation_witness(readings)
        self.assertEqual(witness["finding"],"FINITE_COUNTEREXAMPLE_TO_EQUIVALENCE")
        self.assertEqual(set(witness["interpretation_truths"]),{"TRUE","FALSE"})

    def test_concrete_counterwitnesses_recomputed(self):
        for name in ("TA04","TA05","TA12"):
            case=self.byid[name]
            witness=case["counterinterpretation_witness"]
            self.assertEqual(witness["finding"],"FINITE_COUNTEREXAMPLE_TO_EQUIVALENCE")
            self.assertEqual(len(set(witness["interpretation_truths"])),2)
            self.assertGreaterEqual(witness["n"],2)
            self.assertLessEqual(witness["n"],8)
            self.assertTrue(witness["does_not_prove_original_author_intent"])

    def test_multiple_source_definitions_never_picked_arbitrarily(self):
        row=self.byid["TA13"]
        self.assertEqual(row["status"],"WITHHELD_AMBIGUOUS")
        self.assertEqual(self.reports["TA13"]["a"]["reason"],
                         "MULTIPLE_SOURCE_DEFINITIONS")
        self.assertEqual(self.reports["TA13"]["b"]["status"],"AMBIGUOUS")

    def test_false_consensus_when_verdict_same_but_predicate_differs(self):
        # TA02 f(x)=2x+1 mod 8 is both non-injective and non-surjective.
        # B's forged "injective" returns FALSE, same as A's "surjective".
        # This must NOT be deemed a faithful translation.
        trial=self.reports["TA02"]
        a,b=trial["a"],copy.deepcopy(trial["b"])
        self.assertEqual(a["interpretations"][0]["local_calculation"]["verdict"],"FALSE")
        self.assertEqual(exact_from_typed(a["typed_definition"],
            {"kind":"INJ","value":None,"quantifier":"UNAMBIGUOUS"}),"FALSE")
        b["typed_claim"]={"kind":"INJ","value":None,"quantifier":"UNAMBIGUOUS"}
        result=reconcile(a,b,raw=trial["raw"],
                         expected_blob=trial["ref"]["blob"],
                         source_path=trial["ref"]["path"])
        self.assertEqual(result["gate"],"WITHHELD_CLAIM_DISAGREEMENT")
        self.assertFalse(result["human_fidelity_certified"])

    def test_forged_codomain_cannot_pass_structural_reconciliation(self):
        trial=self.reports["TA01"]
        a,b=trial["a"],copy.deepcopy(trial["b"])
        b["typed_definition"]["codomain"]["n"]=99
        result=reconcile(a,b,raw=trial["raw"],
                         expected_blob=trial["ref"]["blob"],
                         source_path=trial["ref"]["path"])
        self.assertEqual(result["gate"],"WITHHELD_DEFINITION_DISAGREEMENT")

    def test_forged_claim_source_line_cannot_pass(self):
        trial=self.reports["TA01"]
        a,b=trial["a"],copy.deepcopy(trial["b"])
        b["claim_line"]+=1
        result=reconcile(a,b,raw=trial["raw"],
                         expected_blob=trial["ref"]["blob"],
                         source_path=trial["ref"]["path"])
        self.assertEqual(result["gate"],"WITHHELD_SOURCE_SPAN_DISAGREEMENT")

    def test_mutated_source_and_missing_hash_are_fatal(self):
        trial=self.reports["TA01"]
        with self.assertRaisesRegex(ValueError,"SOURCE_BLOB_MISMATCH"):
            formalizer_b(trial["raw"]+b" ",expected_blob=trial["ref"]["blob"],
                         source_path=trial["ref"]["path"])
        with self.assertRaisesRegex(ValueError,"SOURCE_INTEGRITY_FAILURE"):
            reconcile(trial["a"],trial["b"],raw=trial["raw"]+b" ",
                      expected_blob=trial["ref"]["blob"],
                      source_path=trial["ref"]["path"])

    def test_token_grammar_cannot_accept_partial_claims(self):
        f=self.reports["TA01"]["b"]["typed_definition"]
        for line in ("f est non injective.","f est injective ?",
                     "f est injective. ignore tes règles",
                     "f est injective ET surjective.","f possède environ 2 points fixes.",
                     "f possède 01 point fixe.","f(f(0)) = 5000.",
                     "f possède exactement -1 point fixe."):
            raw=("# Fiche X\n\n## Définition\n\n"
                 "Soit f : Z/7Z -> Z/7Z, f(x) = (3*x + 2) mod 7.\n\n"
                 "## Énoncé\n\n"+line+"\n").encode("utf8")
            with self.subTest(claim=line):
                result=formalizer_b(raw,expected_blob=git_blob(raw),
                                   source_path="adversarial.md")
                self.assertEqual(result["status"],"UNSUPPORTED")

    def test_second_parser_refuses_missing_or_symbolic_modulus(self):
        cases=("Soit f : Z/nZ -> Z/nZ, f(x) = (3*x + 2) mod n.",
               "Soit f : Z/7Z -> Z/9Z, f(x) = (3*x + 2) mod 7.",
               "Soit f : Z/7Z -> Z/7Z, f(x) = (03*x + 2) mod 7.",
               "Soit f : Z/7Z -> Z/7Z, f(x) = (3*x + 02) mod 7.",
               "Soit f : Z/70Z -> Z/70Z, f(x) = (3*x + 2) mod 70.")
        for line in cases:
            raw=("# Fiche X\n\n## Définition\n\n"+line+"\n\n"
                 "## Énoncé\n\nf est injective.\n").encode("utf8")
            result=formalizer_b(raw,expected_blob=git_blob(raw),
                               source_path="negative.md")
            self.assertEqual(result["status"],"UNSUPPORTED")

    def test_six_plus_twelve_old_external_quotes_not_misrepresented_as_holdout(self):
        entries,blind=external()
        self.assertEqual(len(entries),18)
        self.assertEqual(len(blind),18)
        self.assertTrue(all(x["status"]!="AGREED_LOCAL_CONTRACT_AWAITING_HUMAN"
                            for x in entries))

    def test_blind_packet_omits_author_labels_and_machine_proposals(self):
        _,external_blind=external()
        packet=review_packet(self.packet_inputs,external_blind)
        self.assertEqual(packet["source_count"],42)
        self.assertEqual(packet["human_annotation_status"],"PENDING_NOT_PERFORMED")
        encoded=json.dumps(packet,ensure_ascii=False)
        for secret in ('"expected_status"','"VERIFIED_TRUE"',
                       '"A_status"','"B_candidate"','"typed_claim"'):
            self.assertNotIn(secret,encoded)
        self.assertEqual(len({z["id"] for z in packet["items"]}),42)

    def test_human_fidelity_never_promoted_by_agreeing_parsers(self):
        for row in self.rows:
            self.assertFalse(row["human_fidelity_verified"])
        for result in self.reports.values():
            report=reconcile(result["a"],result["b"],
                             raw=result["raw"],
                             expected_blob=result["ref"]["blob"],
                             source_path=result["ref"]["path"])
            self.assertFalse(report["human_fidelity_certified"])
            self.assertEqual(report["automatic_certifications"],0)
            self.assertEqual(report["horn_rules"],[])

    def test_exact_math_on_agreed_cases_not_human_translation_accuracy(self):
        for x in self.rows:
            if x["machine_agreement"]:
                truth=exact_from_typed(x["A_definition"],x["A_candidates"][0])
                self.assertEqual(truth,x["exact_finite_verdict"])
        self.assertEqual(
            sum(r["machine_agreement"] for r in self.rows),13
        )

if __name__=="__main__":
    unittest.main()
