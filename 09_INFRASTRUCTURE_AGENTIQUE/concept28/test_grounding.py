#!/usr/bin/env python3
"""CONCEPT28 frozen rules and cross-language type-grounding safety tests.

These synthetic fixtures are NOT the 24 external holdout theorem statements.
"""
from __future__ import annotations

import inspect
import json
import unittest
from pathlib import Path

from grounding import (
    load_lexicon,load_holdout,grounded_score,baseline_score,
    matching_lexical_terms,judge,choose,one_pair,NEAR,FAR,
    EXPECTED,read_tasks,read_original_statement,
)

class ConceptGroundedExternalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lex=load_lexicon()

    def test_40_rules_and_threshold_are_frozen(self):
        self.assertEqual(len(self.lex["keywords"]),40)
        self.assertEqual(self.lex["decision_threshold"],
                         {"min_best_score":2,"min_margin":2})
        self.assertEqual(self.lex["status"],"FROZEN_BEFORE_UNSEEN_CORPUS_READING")

    def test_24_external_indices_not_from_old_holdouts(self):
        h=load_holdout()
        self.assertEqual(h["n_new_cases"],24)
        self.assertEqual(len(h["docs"]),24)
        ids=[v for pair in EXPECTED for v in pair]
        self.assertEqual([x["index"] for x in h["docs"]],ids)
        old={1,2,3,6,10,22,40,80,120,160,200,240,280,320,350,367,
             4,5,7,8,9,11,12,13,14,15,16,17,18,19,20,21,
             23,24,25,26,27,28,29,30}
        self.assertFalse(set(ids)&old)

    def test_near_far_6_each_independently_reported(self):
        self.assertEqual(len(NEAR),6)
        self.assertEqual(len(FAR),6)
        self.assertEqual(len(EXPECTED),12)

    def test_group_terms_survive_the_naive_baseline(self):
        self.assertIn("group",matching_lexical_terms("A group of order 2"))
        self.assertIn("group",matching_lexical_terms("[Group G]"))

    def test_naive_baseline_splits_camel_case_for_fairness(self):
        score=baseline_score("Linearly independent vectors",
                             "theorem candidate : LinearIndependent K R")
        self.assertIn("independent",score["matched_terms"])
        self.assertGreaterEqual(score["score"],1)

    def test_grounding_vector_space_to_module(self):
        q="Let V be a vector space spanned by vectors"
        lean="theorem candidate [Module K V] : Submodule.span K S = ⊤"
        scored=grounded_score(q,lean,self.lex)
        self.assertIn("VECTOR_SPACE",[x["concept"] for x in scored["matches"]])
        self.assertIn("SPAN",[x["concept"] for x in scored["matches"]])
        self.assertGreaterEqual(scored["score"],5)
        self.assertFalse(scored["alignment_is_a_theorem_proof"])

    def test_grounding_abelian_center_cyclic_to_lean_tokens(self):
        nl="Let G be an abelian group. If the center G is cyclic"
        lean="theorem candidate [CommGroup G] : IsCyclic (center G)"
        scored=grounded_score(nl,lean,self.lex)
        matched={x["concept"] for x in scored["matches"]}
        self.assertIn("GROUP",matched)
        self.assertIn("ABELIAN",matched)
        self.assertIn("CENTER",matched)
        self.assertIn("CYCLIC",matched)

    def test_source_anchored_token_grounding_cannot_fake_math_meaning(self):
        scored=grounded_score("An injective function over a group",
                              "theorem candidate : Injective f",self.lex)
        self.assertIn("INJECTIVE",{x["concept"] for x in scored["matches"]})
        self.assertNotIn("GROUP",{x["concept"] for x in scored["matches"]})
        self.assertFalse(scored["alignment_is_a_theorem_proof"])

    def test_tie_abstains_even_if_both_candidates_match(self):
        result=judge("group with center",
                     {"A":"theorem candidate [Group G] : center G = ⊤",
                      "B":"theorem candidate [Group H] : center H = ⊤"},
                     self.lex,"typed")
        self.assertEqual(result["chosen"],"NONE")

    def test_group_vs_vector_space_provides_a_reproducible_choice(self):
        q="A vector space has a linearly independent basis."
        models={"A":"theorem candidate [Module K V] : LinearIndependent K v",
                "B":"theorem candidate [Group G] : Subgroup.closure S = ⊤"}
        result=judge(q,models,self.lex,"typed")
        self.assertEqual(result["chosen"],"A")
        self.assertIn("VECTOR_SPACE",{
            x["concept"] for x in result["evidence"]["A"]["matches"]})
        reversed_choice=judge(q,{"A":models["B"],"B":models["A"]},
                              self.lex,"typed")
        self.assertEqual(reversed_choice["chosen"],"B")

    def test_no_cues_means_abstain_not_guess(self):
        result=judge("Prove an unknown claim about zeta vectors",
                     {"A":"theorem candidate : P x",
                      "B":"theorem candidate : Q x"},
                     self.lex,"typed")
        self.assertEqual(result["chosen"],"NONE")
        self.assertEqual(result["reason"],"INSUFFICIENT_DISCRIMINATING_EVIDENCE")

    def test_small_margin_means_abstain_not_force_prediction(self):
        scores={"A":{"score":4},"B":{"score":3}}
        out=choose(scores,mode="typed",lexicon=self.lex)
        self.assertEqual(out["chosen"],"NONE")
        out=choose(scores,mode="naive",lexicon=self.lex)
        self.assertEqual(out["chosen"],"A")

    def test_no_lean_source_name_or_correct_label_in_decision(self):
        text=inspect.getsource(judge)
        self.assertNotIn("source_blob",text)
        self.assertNotIn("original_reference",text)
        self.assertNotIn("posthoc",text)
        self.assertNotIn("correct",text)

    def test_frozen_lexicon_does_not_add_hypotheses_or_proof(self):
        self.assertNotIn("model",inspect.getsource(judge))
        self.assertNotIn("source_url",inspect.getsource(grounded_score))
        self.assertTrue(self.lex["no_model"])

    def test_pair_results_are_label_swap_invariant(self):
        group={
            "stratum":"FAR",
            "first":{
                "index":44,"code":"theorem candidate [Group G] : center G = ⊤",
                "nl":"Every group has a center.","source_blob":"a"*40,
                "source_url":"https://example.test/a","lean_original_sha256":"1"*64
            },
            "second":{
                "index":180,"code":"theorem candidate [Module K V] : LinearIndependent K b",
                "nl":"Linearly independent vectors in a vector space.",
                "source_blob":"b"*40,"source_url":"https://example.test/b",
                "lean_original_sha256":"2"*64
            },
        }
        result=one_pair(group,self.lex)
        self.assertEqual(len(result),4)
        for idx in (44,180):
            rows=[x for x in result if x["index"]==idx]
            self.assertEqual(len(rows),2)
            for mode in ("typed","naive"):
                a,b=rows
                self.assertEqual(a["strategies"][mode]["source_selected"],
                                 b["strategies"][mode]["source_selected"])

    def test_invalid_candidate_sets_cannot_be_judged(self):
        with self.assertRaisesRegex(ValueError,"CANDIDATE_LABELS_WRONG"):
            choose({"A":{"score":5},"C":{"score":3}},
                   mode="typed",lexicon=self.lex)

    def test_unknown_mode_is_not_fallback(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_MATCHING_ALGORITHM"):
            judge("group",{"A":"Group","B":"Module"},self.lex,"oracle")

    def test_all_source_hashes_have_proper_fixed_git_identity(self):
        for src in load_holdout()["docs"]:
            self.assertRegex(src["git_blob"],r"^[0-9a-f]{40}$")
            self.assertGreater(src["bytes"],200)
            self.assertIn("b7ca411a2abaa6caf3580192b30d865e5bd10bc4",
                          src["source_url"])

    def test_full_original_proof_is_not_mistaken_for_missing_theorem(self):
        from read import blob as git_blob
        raw=(
            "import Mathlib\n\n"
            "/-Informal Statement\nA group has an identity element.\n-/\n\n"
            "theorem Demo {G : Type*} [Group G] : (1 : G) = 1 := by\n"
            "  rfl\n"
        ).encode("utf8")
        result=read_original_statement(raw,{
            "index":999,"source_url":"synthetic-fixture-not-external",
            "git_blob":git_blob(raw),
        })
        self.assertEqual(result["proof_body_kind"],
                         "COMPLETE_ORIGINAL_PROOF_NOT_IN_CANDIDATE")
        self.assertIn("A group has an identity",result["informal"])
        self.assertIn("(1 : G) = 1",result["code"])
        self.assertNotIn("rfl",result["code"])

    def test_full_proof_parser_does_not_accept_multiple_theorems(self):
        from read import blob as git_blob
        raw=(
            "import Mathlib\n\n"
            "/-Informal Statement\nGroup example.\n-/\n\n"
            "theorem First {G : Type*} [Group G] : True := by\n  trivial\n"
            "theorem Second {G : Type*} [Group G] : True := by\n  trivial\n"
        ).encode("utf8")
        with self.assertRaisesRegex(ValueError,"UNIQUE_NL_AND_THEOREM"):
            read_original_statement(raw,{
                "index":999,"source_url":"synthetic-fixture-not-external",
                "git_blob":git_blob(raw),
            })

    def test_no_annotation_of_negative_equivalence_is_claimed(self):
        v=load_holdout()
        self.assertFalse(v["negative_independent_equivalence_annotation"])

if __name__=="__main__":
    unittest.main()
