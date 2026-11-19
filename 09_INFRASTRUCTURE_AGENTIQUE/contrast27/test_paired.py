#!/usr/bin/env python3
"""CONTRAST27: fixed candidate permutations, source hashes, no gold leaking.

All tests are deterministic/offline. They check that source-matching evidence
cannot be faked by always replying A or by manufacturing the gold in prompts.
"""
from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from paired import (
    EXPECTED_PAIRS, manifest,assigned,prompt,
    parse_model_choice,semantic_marker_check,generation,
    directly_score,gated_score,compare,anonymize_reference,
    MODEL_SHA, LLAMA_SHA,
)
from runner import fetch_pinned
from read import blob as git_blob


def task(i=4)->dict:
    return {
        "index":i,"decoy_index":5,
        "source_blob":"a"*40,"source_url":"https://source.example/case",
        "informal_statement_exact":"Let G be a finite group. Prove there exists a unique identity.",
        "own_lean":"theorem candidate {G : Type*} [Group G] : ∃ x : G, x = 1",
        "decoy_lean":"theorem candidate {G : Type*} [Group G] : ∀ x : G, x = 1",
        "reference_lean_sha256":"1"*64,"decoy_source_blob":"b"*40,
    }


def fake(reply:str):
    def call(messages):
        return {
            "raw_reply":reply,"elapsed_seconds":0.0,
            "usage":{"prompt_tokens":100,"completion_tokens":1},
            "finish_reason":"stop","server_model":"synthetic_test_not_real",
        }
    return call


class ContrastiveTests(unittest.TestCase):
    def test_24_indices_precommitted_disjoint_from_proofnet26(self):
        f=manifest()
        self.assertEqual(len(f["source_docs"]),24)
        self.assertEqual(len(f["pairs"]),12)
        self.assertEqual(f["source_commit"],"b7ca411a2abaa6caf3580192b30d865e5bd10bc4")
        old={1,2,3,6,10,22,40,80,120,160,200,240,280,320,350,367}
        self.assertFalse(old & set(f["indices"]))
        self.assertEqual(tuple(map(tuple,f["pairs"])),EXPECTED_PAIRS)

    def test_references_are_unforgeable_git_blobs(self):
        docs=manifest()["source_docs"]
        self.assertEqual(len({x["git_blob"] for x in docs}),24)
        for item in docs:
            self.assertRegex(item["git_blob"],r"^[0-9a-f]{40}$")
            self.assertIn("b7ca411a2abaa6caf3580192b30d865e5bd10bc4",item["source_url"])
            self.assertGreaterEqual(item["bytes"],100)

    def test_reference_anonymization_removes_names_and_sorry_not_logic(self):
        origin=("theorem Artin_exercise_9_1 {G : Type*} [Group G] :\n"
                "  ∃ x : G, x = 1 := by\n  sorry")
        out=anonymize_reference(origin)
        self.assertTrue(out.startswith("theorem candidate {G : Type*}"))
        self.assertIn("∃ x : G",out)
        self.assertNotIn("Artin",out)
        self.assertNotIn("sorry",out)

    def test_option_swap_balanced_per_case(self):
        t=task()
        first,second=assigned(t,0),assigned(t,1)
        self.assertEqual({first["correct_option"],second["correct_option"]},{"A","B"})
        self.assertEqual(first["options"]["A"],second["options"]["B"])
        self.assertEqual(first["options"]["B"],second["options"]["A"])
        self.assertEqual(first["options"][first["correct_option"]],t["own_lean"])
        self.assertEqual(second["options"][second["correct_option"]],t["own_lean"])

    def test_prompt_no_source_or_gold_leakage(self):
        t=task()
        text=json.dumps(prompt(t,0)[0],ensure_ascii=False)
        for secret in ("source.example","a"*40,"proofnet-4","correct_option_for_posthoc"):
            self.assertNotIn(secret,text)
        self.assertIn(t["informal_statement_exact"],text)
        self.assertIn(t["own_lean"],text)
        self.assertIn(t["decoy_lean"],text)

    def test_only_three_exact_valid_response_strings(self):
        for valid in ("A","B","NONE"," A \n"):
            self.assertIn(parse_model_choice(valid),("A","B","NONE"))
        for invalid in ("a","b","Answer A","A or B","A,B","[A]","A.","","C","TRUE"):
            self.assertEqual(parse_model_choice(invalid),"INVALID")

    def test_always_first_response_cannot_pass_consistency_gate(self):
        t=task()
        rows=[generation(t,o,"mock",fake("A")) for o in (0,1)]
        self.assertEqual(sum(x["correct_original_pair"] for x in rows),1)
        # Gates are defined over 24 distinct cases; repeat 24 independent
        # mock cases to test mathematical anti-position-bias invariant.
        full=[]
        for i in range(100,124):
            synthetic=task(i)
            synthetic["decoy_index"]=i+30
            full.extend(generation(synthetic,o,"mock",fake("A")) for o in (0,1))
        gate=gated_score(full)
        self.assertEqual(gate["order_swap_stability"]["accepted"],0)
        self.assertEqual(gate["stability_plus_semantic_markers"]["accepted"],0)

    def test_same_correct_lean_in_both_orders_passes_consistency(self):
        full=[]
        for i in range(100,124):
            t=task(i)
            t["decoy_index"]=i+30
            for order in (0,1):
                correct=assigned(t,order)["correct_option"]
                full.append(generation(t,order,"mock",fake(correct)))
        result=gated_score(full)
        self.assertEqual(result["order_swap_stability"]["accepted"],24)
        self.assertEqual(result["order_swap_stability"]["correct"],24)
        self.assertEqual(result["stability_plus_semantic_markers"]["correct"],24)

    def test_consistent_wrong_lean_can_remain_wrong(self):
        full=[]
        for i in range(100,124):
            t=task(i)
            t["decoy_index"]=i+30
            for order in (0,1):
                correct=assigned(t,order)["correct_option"]
                wrong="B" if correct=="A" else "A"
                full.append(generation(t,order,"mock",fake(wrong)))
        result=gated_score(full)
        self.assertEqual(result["order_swap_stability"]["accepted"],24)
        self.assertEqual(result["order_swap_stability"]["correct"],0)
        self.assertEqual(result["order_swap_stability"]["wrong"],24)
        # Critical: stability is NOT a semantic correctness guarantee.
        self.assertEqual(result["stability_plus_semantic_markers"]["correct"],0)

    def test_iff_marker_warns_if_lean_lacks_iff(self):
        check=semantic_marker_check("A iff B; if and only if A B",
                                    "theorem candidate : A → B")
        self.assertEqual(check["status"],"SUSPECT_MISSING_EXPLICIT_MARKER")
        self.assertIn("MISSING_EXPLICIT_IFF",check["missing"])
        good=semantic_marker_check("A if and only if B",
                                   "theorem candidate : A ↔ B")
        self.assertEqual(good["status"],"NO_EXPLICIT_CONTRADICTION_DETECTED")

    def test_existential_marker_warns_without_exists_or_nonempty(self):
        fail=semantic_marker_check("There exists an element",
                                   "theorem candidate : ∀ x, P x")
        self.assertIn("MISSING_EXPLICIT_EXISTENTIAL_MARKER",fail["missing"])
        ok=semantic_marker_check("There exists an element",
                                 "theorem candidate : ∃ x, P x")
        self.assertEqual(ok["missing"],[])

    def test_numbers_in_original_cannot_be_faked(self):
        check=semantic_marker_check("a group of order 21",
                                    "theorem candidate : card G = 7")
        self.assertIn("MISSING_LITERAL_NUMBER_21",check["missing"])
        good=semantic_marker_check("a group of order 21",
                                   "theorem candidate : card G = 21")
        self.assertEqual(good["missing"],[])

    def test_structural_markers_only_abstain_never_switch_to_other(self):
        t=task()
        t["informal_statement_exact"]="There exists an identity of order 21."
        rows=[generation(t,o,"mock",fake(assigned(t,o)["correct_option"]))
              for o in (0,1)]
        self.assertTrue(all(x["correct_original_pair"] for x in rows))
        self.assertTrue(all(x["marker_check"]["missing"] for x in rows))
        full=[]
        for i in range(100,124):
            synthetic={**t,"index":i,"decoy_index":i+30}
            full.extend(generation(synthetic,o,"mock",fake(assigned(synthetic,o)["correct_option"]))
                        for o in (0,1))
        gated=gated_score(full)
        self.assertEqual(gated["order_swap_stability"]["accepted"],24)
        self.assertEqual(gated["stability_plus_semantic_markers"]["accepted"],0)

    def test_unknown_output_treated_as_no_choice(self):
        t=task()
        answer=generation(t,0,"mock",fake("Here is A."))
        self.assertEqual(answer["parsed_choice"],"INVALID")
        self.assertIsNone(answer["chosen_original_index"])
        self.assertFalse(answer["correct_original_pair"])

    def test_wrong_selected_candidate_is_counted_wrong_not_abstained(self):
        t=task()
        gold=assigned(t,0)["correct_option"]
        wrong="B" if gold=="A" else "A"
        a=generation(t,0,"mock",fake(wrong))
        stats=directly_score([a])
        self.assertEqual(stats["wrong"],1)
        self.assertEqual(stats["correct"],0)
        self.assertEqual(stats["abstained"],0)

    def test_missing_order_invalidates_model_comparison(self):
        t=task()
        rows=[generation(t,0,"mock",fake("NONE")) for _ in range(48)]
        with self.assertRaisesRegex(ValueError,"PAIR_ORIENTATION_COVERAGE_INCOMPLETE"):
            gated_score(rows)

    def test_negative_leakage_of_original_reference_identifier_in_prompt(self):
        t=task()
        t["own_lean"]="theorem proofnet-4 {G : Type*} : True"
        with self.assertRaisesRegex(ValueError,"LABEL_LEAKED"):
            prompt(t,0)

    def test_invalid_origin_and_source_hash_refused(self):
        t=task()
        t["own_lean"]=t["decoy_lean"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_OPTION_CODE"):
            assigned(t,0)

    def test_source_tampering_fails_exact_hash_check_offline(self):
        raw=(b"/-Informal Statement\nA statement.\n-/\n"
             b"theorem X : True := by\n  sorry\n")
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"4.lean"
            path.write_bytes(raw)
            item={"index":4,"git_blob":git_blob(raw)}
            self.assertEqual(fetch_pinned(item,cache_dir=Path(tmp)),raw)
            path.write_bytes(raw+b"\n% poisoned source")
            with self.assertRaisesRegex(ValueError,"UPSTREAM_SOURCE_GIT_HASH_MISMATCH"):
                fetch_pinned(item,cache_dir=Path(tmp))

    def test_real_models_sha_pinned_no_paid_api(self):
        self.assertEqual(len(MODEL_SHA),2)
        self.assertTrue(all(len(x)==64 for x in MODEL_SHA.values()))
        self.assertEqual(LLAMA_SHA,"5a4afd80779ba51166b59986e61a0bfbb9e1a4c6")

    def test_stability_gates_refuse_truncated_predictions(self):
        def truncated(_messages):
            return {"raw_reply":"A","finish_reason":"length",
                    "elapsed_seconds":0.0,"usage":{},"server_model":"mock"}
        with self.assertRaisesRegex(ValueError,"TRUNCATED_MODEL_RESPONSE"):
            generation(task(),0,"mock",truncated)


if __name__=="__main__":
    unittest.main()
