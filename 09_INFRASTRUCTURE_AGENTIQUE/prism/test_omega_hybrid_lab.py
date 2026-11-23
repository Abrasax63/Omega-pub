"""Offline tests of Omega's hybrid learning evidence gate. No LLM or Web."""
import json
from hashlib import sha256
from pathlib import Path
import tempfile
import unittest

import omega_hybrid_lab as lab

QUOTE = "An equivalence relation is reflexive, symmetric, and transitive."


def fixture():
    excerpt = "A chapter on relations. " + QUOTE + " These are conditions."
    source = {"source_kind": "web", "page_id": 123,
              "revision_id": 456, "excerpt": excerpt}
    rec = {
        "candidate_id": "test-candidate",
        "record_type": "EDUCATIONAL_RESEARCH_CANDIDATE",
        "sources": [{"page_id": 123, "revision_id": 456,
                     "excerpt_sha256": sha256(excerpt.encode()).hexdigest()}],
        "interpretation_candidate": {
            "concept": "equivalence relation", "definition": QUOTE,
            "source_page_id": 123, "source_kind": "web", "exact_quote": QUOTE,
            "formal_axioms": ["reflexive", "symmetric", "transitive"],
            "positive_edges": [["a", "a"], ["b", "b"], ["c", "c"]],
            "negative_edges": [["a", "b"]],
        },
    }
    return rec, [source]


def answer(value):
    return json.dumps({"holds": value,
                       "failed_axioms": [] if value else ["reflexive"]})


def trial(ident="t1", edges=None, d=False, m=True, n=False, tokens=None):
    return {"id": ident, "edges": edges if edges is not None else
            [["a", "a"], ["b", "b"], ["c", "c"]],
            "outputs": {"D": answer(d), "M": answer(m), "N": answer(n)},
            "prompt_tokens": tokens or {"D": 100, "M": 102, "N": 101}}


class HybridLabTests(unittest.TestCase):
    def test_exact_source_quote_and_matched_digest(self):
        rec, sources = fixture()
        self.assertEqual(lab.source_gate(rec, sources)["status"],
                         "SNAPSHOT_QUOTE_MATCH")

    def test_quote_from_other_source_is_rejected(self):
        rec, sources = fixture()
        rec["interpretation_candidate"]["source_page_id"] = 999
        self.assertEqual(lab.source_gate(rec, sources)["status"], "QUARANTINE")

    def test_primary_and_web_cannot_be_swapped(self):
        rec, sources = fixture()
        rec["interpretation_candidate"]["source_kind"] = "primary"
        self.assertEqual(lab.source_gate(rec, sources)["reason"],
                         "SOURCE_METADATA_NOT_UNIQUE")

    def test_source_hash_tampering_fails_closed(self):
        rec, sources = fixture()
        sources[0]["excerpt"] += " changed"
        self.assertEqual(lab.source_gate(rec, sources)["reason"],
                         "SOURCE_DIGEST_MISMATCH")

    def test_well_formed_but_paraphrased_quote_is_rejected(self):
        rec, sources = fixture()
        rec["interpretation_candidate"]["exact_quote"] = (
            "Relations can be reflexive, symmetric, and transitive in math.")
        self.assertEqual(lab.source_gate(rec, sources)["reason"],
                         "QUOTE_NOT_IN_DECLARED_SOURCE")

    def test_no_source_authenticity_or_semantic_certification_claim(self):
        rec, sources = fixture()
        gate = lab.source_gate(rec, sources)
        bounded = lab.bounded_gate(rec, gate)
        self.assertEqual(bounded["status"], "BOUNDED_FORMAL_PASS")
        self.assertEqual(bounded["free_text_semantics"], "NOT_VERIFIED")
        self.assertFalse(bounded["new_theorem_certified"])
        self.assertEqual(gate["authenticity"], "NOT_INDEPENDENTLY_RETRIEVED")

    def test_false_example_is_rejected_despite_valid_quote(self):
        rec, sources = fixture()
        rec["interpretation_candidate"]["positive_edges"] = [["a", "b"]]
        self.assertEqual(lab.bounded_gate(rec, lab.source_gate(rec,sources))["reason"],
                         "POSITIVE_EXAMPLE_INVALID")

    def test_fake_signature_is_rejected(self):
        rec, sources = fixture()
        rec["interpretation_candidate"]["formal_axioms"] = ["reflexive", "symmetric"]
        self.assertEqual(lab.bounded_gate(rec, lab.source_gate(rec,sources))["reason"],
                         "FORMAL_SIGNATURE_MISMATCH")

    def test_nested_signature_must_not_crash(self):
        rec, sources = fixture()
        rec["interpretation_candidate"]["formal_axioms"] = [["reflexive"], "symmetric", "transitive"]
        self.assertEqual(lab.bounded_gate(rec, lab.source_gate(rec,sources))["reason"],
                         "FORMAL_SIGNATURE_MISMATCH")

    def test_invalid_json_and_explicit_abstentions_separate(self):
        sig = ("reflexive", "symmetric", "transitive")
        self.assertEqual(lab.parse_prediction("{bad", sig)[0], "INVALID")
        self.assertEqual(lab.parse_prediction('{"abstain":true}', sig)[0], "ABSTAIN")
        self.assertEqual(lab.parse_prediction('{"holds":false,"failed_axioms":[]}', sig)[0], "INVALID")

    def test_pairwise_comparison_is_descriptive_not_proof(self):
        packet = {"protocol_frozen": True, "source_disjoint": True,
                  "trials": [trial()]}
        r = lab.evaluate_holdout(packet, ("reflexive", "symmetric", "transitive"))
        self.assertEqual(r["status"], "SCORED_DESCRIPTIVE_ONLY")
        self.assertEqual(r["net_gain"], {"memory_vs_direct": 1, "memory_vs_neutral": 1})
        self.assertFalse(r["statistical_gain_proven"])

    def test_missing_preregistered_split_is_blocked(self):
        packet = {"protocol_frozen": False, "source_disjoint": True,
                  "trials": [trial()]}
        self.assertEqual(lab.evaluate_holdout(packet, ("reflexive",))["status"], "BLOCKED")

    def test_unbalanced_token_count_blocks_claim(self):
        packet = {"protocol_frozen": True, "source_disjoint": True,
                  "trials": [trial(tokens={"D": 100, "M": 150, "N": 100})]}
        self.assertEqual(lab.evaluate_holdout(packet, ("reflexive",))["reason"],
                         "TOKEN_BUDGET_IMBALANCE")

    def test_duplicate_holdouts_are_blocked(self):
        packet = {"protocol_frozen": True, "source_disjoint": True,
                  "trials": [trial(), trial()]}
        self.assertEqual(lab.evaluate_holdout(packet, ("reflexive",))["reason"],
                         "DUPLICATE_OR_INVALID_CASE_ID")

    def test_invalid_output_kept_in_denominator(self):
        row = trial()
        row["outputs"]["M"] = "not-json"
        packet = {"protocol_frozen": True, "source_disjoint": True,
                  "trials": [row]}
        r = lab.evaluate_holdout(packet, ("reflexive", "symmetric", "transitive"))
        self.assertEqual(r["metrics"]["M"]["invalid"], 1)
        self.assertEqual(r["metrics"]["M"]["correct"], 0)

    def test_planner_adapts_to_gate_and_holdout(self):
        rec, sources = fixture()
        self.assertEqual(lab.next_action({"status": "QUARANTINE"}, {})["action"], "RESEARCH")
        sg = lab.source_gate(rec, sources)
        fg = lab.bounded_gate(rec, sg)
        self.assertEqual(lab.next_action(sg, fg)["action"], "PRACTICE")
        evidence = {"status":"SCORED_DESCRIPTIVE_ONLY", "net_gain":
                    {"memory_vs_direct": 2, "memory_vs_neutral": 1}}
        self.assertEqual(lab.next_action(sg, fg, evidence)["action"], "CHALLENGE")

    def test_three_curriculum_policies_deterministic(self):
        pool = [{"id":f"x{i}", "difficulty":i} for i in range(1,6)]
        hist = [{"exercise_id":"x1", "result":"wrong"}]
        self.assertEqual(lab.select_exercise(pool, hist, "progressive")["exercise_id"], "x2")
        self.assertEqual(lab.select_exercise(pool, hist, "adaptive")["exercise_id"], "x2")
        self.assertEqual(lab.select_exercise(pool, hist, "random", 55),
                         lab.select_exercise(pool, hist, "random", 55))

    def test_append_to_existing_chain_no_scientific_promotion(self):
        from incremental_math_library import append_candidate, read_ledger
        with tempfile.TemporaryDirectory() as d:
            record, snaps = fixture()
            ledger = Path(d)/"educational.jsonl"
            episodes = Path(d)/"episodes.jsonl"
            self.assertTrue(append_candidate(ledger, record))
            response = lab.inspect_ledger(ledger, snaps, episodes)
            self.assertFalse(response["training_performed"])
            self.assertEqual(response["scientific_claims_certified"], 0)
            self.assertEqual(len(read_ledger(episodes)), 1)
            # Exact rerun is idempotent.
            lab.inspect_ledger(ledger, snaps, episodes)
            self.assertEqual(len(read_ledger(episodes)), 1)
            # An altered earlier ledger record is not silently accepted.
            ledger.write_text(ledger.read_text().replace("equivalence relation", "partial order"))
            with self.assertRaises(ValueError):
                lab.inspect_ledger(ledger, snaps)


if __name__ == "__main__":
    unittest.main()
