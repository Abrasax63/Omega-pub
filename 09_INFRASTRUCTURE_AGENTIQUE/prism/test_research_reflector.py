"""Fail-closed contracts for reflective hypotheses and nondestructive Omega optimization."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from research_reflector import (STATUS, UnsafeProposal, audit_redundancy, git_blob,
                                overlap, source_anchor, validate_proposal)


def candidate(blob, quote):
    return {
        "id": "OMEGA-HYP-TEMP-001",
        "status": STATUS, "source_root": "omega100",
        "source": {"path": "042.md", "git_blob": blob, "quote": quote},
        "question": "Does the construction preserve evidence?",
        "thesis": "The new interpretation might improve a limited task",
        "limitations": "No understanding or theorem has been verified",
        "representations": [
            {"name": "slots", "mapping": "map words into two slots",
             "preserved": "literal evidence spans",
             "breaks_on": "implicit unanchored slots"},
            {"name": "graph", "mapping": "map cited words to graph edges",
             "preserved": "source identifiers",
             "breaks_on": "competing interpretations"},
        ],
        "test": {
            "premises": "explicit source excerpt and independent labels",
            "baseline": "exact fixed reference",
            "prediction": "fewer errors on fresh examples",
            "counterexample": "ambiguous pair wrongly selected",
            "counterfactual_prediction": "ambiguous evidence must result in abstention",
            "cross_representation_invariant": "slot and graph choices must agree",
            "independent_evidence": "new separately annotated questions",
            "metrics": "TP FP FN abstentions and total compute",
            "failure_criteria": "any false route or repeated heldout",
            "budget": "a maximum of 24 short experiments",
        },
    }


class ReflectorTests(unittest.TestCase):
    def prepare(self, root):
        root = Path(root)
        (root / "omega").mkdir()
        (root / "math").mkdir()
        (root / "provenance").mkdir()
        text = "Original source with an exactly anchored theoretical claim for testing.\n"
        raw = text.encode()
        (root / "omega/042.md").write_bytes(raw)
        return candidate(git_blob(raw), text.strip()), {
            "omega100": root / "omega", "math": root / "math", "provenance": root / "provenance"
        }

    def test_two_representations_are_grounded_but_not_certified(self):
        with TemporaryDirectory() as td:
            p, roots = self.prepare(td)
            result = validate_proposal(p, roots)
            self.assertEqual(result["status"], STATUS)
            self.assertFalse(result["scientific_truth_checked"])
            self.assertFalse(result["can_enter_executed_ledger"])
            self.assertEqual(result["anchor"]["start_line"], 1)

    def test_stale_source_and_invented_quote_fail_closed(self):
        with TemporaryDirectory() as td:
            p, roots = self.prepare(td)
            p["source"]["quote"] = "This allegedly grounded interpretation does not occur in source"
            with self.assertRaises(UnsafeProposal):
                validate_proposal(p, roots)
            p["source"]["quote"] = "Original source with an exactly anchored theoretical claim for testing."
            (roots["omega100"] / "042.md").write_text("changed")
            with self.assertRaisesRegex(UnsafeProposal, "Stale"):
                validate_proposal(p, roots)

    def test_ambiguous_anchors_and_unsafe_paths_fail(self):
        with TemporaryDirectory() as td:
            p, roots = self.prepare(td)
            source = roots["omega100"] / "042.md"
            source.write_text((p["source"]["quote"] + "\n") * 2)
            p["source"]["git_blob"] = git_blob(source.read_bytes())
            with self.assertRaisesRegex(UnsafeProposal, "ambiguous"):
                validate_proposal(p, roots)
            p["source"]["path"] = "../outside.md"
            with self.assertRaises(UnsafeProposal):
                validate_proposal(p, roots)

    def test_missing_falsifier_or_proof_promotion_rejected(self):
        with TemporaryDirectory() as td:
            p, roots = self.prepare(td)
            p["test"]["counterexample"] = ""
            with self.assertRaisesRegex(UnsafeProposal, "contract"):
                validate_proposal(p, roots)
            p["test"]["counterexample"] = "specific contradictory observation"
            p["proof"] = "PROVED BY LLM"
            with self.assertRaisesRegex(UnsafeProposal, "promotion"):
                validate_proposal(p, roots)

    def test_same_words_different_holdout_is_not_exact_duplication(self):
        base = {
            "id": "A", "objective": "Verify exact binary parity on forced graphs",
            "source_revision": "sha1", "input_digest": "x", "oracle_digest": "o",
            "holdout_digest": "h1", "metric_definition": "match", "scope": "S",
            "budget": "10 cases",
        }
        b = dict(base, id="B", holdout_digest="h2")
        result = overlap(base, b)
        self.assertNotEqual(result["relationship"], "EXACT_SAME_CONTRACT_REVIEW_ONLY")
        self.assertFalse(result["automatically_delete"])
        b["holdout_digest"] = "h1"
        self.assertEqual(overlap(base, b)["relationship"], "EXACT_SAME_CONTRACT_REVIEW_ONLY")
        self.assertFalse(overlap(base, b)["automatically_skip_regression"])

    def test_identical_files_never_trigger_deletion(self):
        with TemporaryDirectory() as td:
            p, roots = self.prepare(td)
            for key in ("math", "provenance"):
                (roots[key] / "same.py").write_text("print('same')\n")
            a = audit_redundancy(roots, [
                {"id": "A", "objective": "Check the scientific graph of evidence"},
                {"id": "B", "objective": "Check the scientific graph of evidence"},
            ])
            self.assertGreaterEqual(a["content_duplicate_groups"], 1)
            self.assertGreaterEqual(len(a["potentially_overlapping_job_pairs"]), 1)
            self.assertEqual(a["safe_to_delete_files"], [])
            self.assertEqual(a["safe_to_drop_tests"], [])


if __name__ == "__main__":
    unittest.main()
