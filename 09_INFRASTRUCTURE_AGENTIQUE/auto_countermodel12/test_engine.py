#!/usr/bin/env python3
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import engine as e

class AutomaticCountermodel12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.external=e.load_external()

    def test_frozen_new_external_first_twelve_are_pinned(self):
        self.assertEqual(len(self.external),12)
        self.assertEqual(e.blob_sha(e.SAMPLE.read_bytes()),e.SAMPLE_BLOB)
        self.assertEqual(len({e.stable_hash(x["premises"]) for x in self.external}),5)

    def test_generic_monadic_extraction_without_source_id_dispatch(self):
        raw=[
            "All cows are bovines.",
            "Some pets are cows.",
            "If something is a bovine, then it is domesticated.",
            "No domesticated animals are alligators.",
            "Ted is an alligator.",
        ]
        expected=["forall_imp","exists_and","forall_imp","forall_disjoint","fact"]
        out=[e.parse_sentence(x,i) for i,x in enumerate(raw)]
        self.assertEqual([x["kind"] for x in out],expected)
        self.assertEqual(out[0]["a"],"cow")
        self.assertEqual(out[0]["b"],"bovine")
        self.assertEqual(out[1]["a"],"pet")
        self.assertEqual(out[3]["a"],"domesticated animal")
        self.assertEqual(out[0]["source_excerpt"],raw[0])
        self.assertEqual(out[-1]["individual"],"Ted")
        self.assertTrue(all(x["source_sha256"] for x in out))

    def test_actual_replay_finite_countermodel_on_unlisted_predicates(self):
        premises=[
            "All shrubs are plants.",
            "Some decorative plants are shrubs.",
            "No plants are robots.",
            "Iris is a robot.",
        ]
        goal="Iris is a decorative plant."
        result=e.inspect(goal,premises,"NOVEL")
        self.assertTrue(result["formalization_complete"])
        self.assertEqual(result["status"],"FINITE_COUNTERMODEL_FOUND")
        self.assertTrue(result["every_premise_replayed"])
        self.assertTrue(result["goal_false_replayed"])
        self.assertGreater(result["models_checked"],0)
        self.assertFalse(result["scientific_claim_certified"])

    def test_existential_requires_individual_and_counterexample(self):
        premises=["Some pets are cows."]
        goal="All pets are cows."
        result=e.inspect(goal,premises,"EXISTENTIAL")
        self.assertEqual(result["status"],"FINITE_COUNTERMODEL_FOUND")
        self.assertEqual(len(result["domain"]),2)
        self.assertFalse(result["scientific_claim_certified"])

    def test_inconsistent_theory_is_not_certified(self):
        premises=["Ted is an alligator.","Ted is not an alligator."]
        result=e.inspect("Ted is an alligator.",premises,"INCONSISTENT")
        self.assertEqual(result["status"],"UNDETERMINED")
        self.assertEqual(result["reason"],"NO_COUNTERMODEL_IN_FINITE_BOUND")
        self.assertEqual(result["satisfiable_models_seen"],0)

    def test_no_counterexample_in_bound_is_not_a_proof(self):
        result=e.inspect("Ted is a pet.",["Ted is a pet."],"TAUTOLOGICAL")
        self.assertEqual(result["status"],"UNDETERMINED")
        self.assertEqual(result["reason"],"NO_COUNTERMODEL_IN_FINITE_BOUND")
        self.assertFalse(result["scientific_claim_certified"])

    def test_generic_person_implication_negative_conclusion(self):
        clause=e.parse_sentence(
            "If Ted is a cow, then Ted is not a pet.",0)
        self.assertIsNotNone(clause)
        self.assertEqual(clause["kind"],"person_imp")
        self.assertTrue(clause["negative"])
        model={("Ted","cow"):True,("Ted","pet"):False}
        self.assertTrue(e.eval_clause(clause,model,["Ted"]))
        model[("Ted","pet")]=True
        self.assertFalse(e.eval_clause(clause,model,["Ted"]))

    def test_complex_language_refuses_without_silent_dropping(self):
        premises=["All workers who live nearby are employees.",
                  "Ted is a person."]
        r=e.inspect("Ted is an employee.",premises,"COMPLEX")
        self.assertEqual(r["status"],"UNDETERMINED")
        self.assertEqual(r["unformalized_source_indices"],[0])
        self.assertEqual(r["independent_tests_executed"],0)
        self.assertFalse(r["formalization_complete"])

    def test_relation_and_quantifier_not_silently_reinterpreted(self):
        for sentence in [
            "All pets are either cows or alligators.",
            "Some pets love cows.",
            "No pets that are wild are cows.",
            "If a cow is not domesticated, then it is wild.",
            "Ted and Max are pets.",
        ]:
            self.assertIsNone(e.parse_sentence(sentence,0),sentence)

    def test_more_than_two_named_individuals_refused_at_bound(self):
        r=e.inspect("Ada is a pet.",
                    ["Ada is a pet.","Bob is a pet.","Cora is a pet."],"BOUNDED")
        self.assertEqual(r["status"],"UNDETERMINED")
        self.assertEqual(r["reason"],"PREDICATE_OR_DOMAIN_BUDGET_EXCEEDED")

    def test_premise_forgery_breaks_replayed_witness(self):
        premises=["No pets are alligators.","Ted is an alligator."]
        r=e.inspect("Ted is a pet.",premises,"REPLAY")
        self.assertEqual(r["status"],"FINITE_COUNTERMODEL_FOUND")
        assignments={(person,name):bit for person,values in r["witness"].items()
                     for name,bit in values.items()}
        wrong=copy.deepcopy(e.parse_sentence(premises[1],1))
        wrong["predicate"]="pet"
        self.assertFalse(e.eval_clause(wrong,assignments,r["domain"]))

    def test_gold_never_in_solver_signature(self):
        source=self.external[0]
        observation=e.inspect(source["conclusion"],source["premises"],"FREE")
        self.assertNotIn("label",json.dumps(observation,ensure_ascii=False))
        self.assertNotIn("published_label",observation)

    def test_scoring_after_predictions_has_no_auto_promotion(self):
        report=e.run(self.external)
        self.assertEqual(report["cases"],12)
        self.assertEqual(report["distinct_theories"],5)
        self.assertEqual(report["new_scientific_theorems_certified"],0)
        self.assertFalse(report["auto_promotion"])
        self.assertTrue(report["predictions_hash_before_gold"])
        self.assertEqual(report["paid_api_calls"],0)
        self.assertTrue(all(not row["scientific_claim_certified"] for row in report["rows"]))

    def test_changed_sample_or_invalid_gold_label_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"changed.jsonl"
            f.write_bytes(e.SAMPLE.read_bytes()+b"\n")
            with patch.object(e,"SAMPLE",f):
                with self.assertRaisesRegex(e.FormalizationError,"sample changed"):
                    e.load_external()

    def test_cli_report_outside_checkout(self):
        with tempfile.TemporaryDirectory() as tmp:
            outfile=Path(tmp)/"report.json"
            r=subprocess.run([sys.executable,str(e.HERE/"engine.py"),
                              "--output",str(outfile)],
                              text=True,capture_output=True,timeout=50)
            self.assertEqual(r.returncode,0,r.stderr)
            doc=json.loads(outfile.read_text())
            self.assertEqual(doc["cases"],12)
            self.assertIn("FORMALIZATIONS_FROZEN_BEFORE_GOLD_SHA256=",r.stdout)
            self.assertEqual(doc["source_blob"],e.FOLIO_UPSTREAM_BLOB)

if __name__=="__main__":
    unittest.main()
