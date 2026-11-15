"""Adversarial, fully synthetic unit tests, NOT a blinded holdout."""
import copy
import unittest

from lineage_pilot import (UNKNOWN, SAME, DISTINCT, assess,
                           fixed_digest, fixed_run_id, next_verification,
                           compare_synthetic)


def calc(id, run, digest="same"):
    return dict(id=id, kind="recompute", parents=[], run_id=run,
                result_digest=digest, attested=True)


def mirror(id, parent, run, digest="same", attested=True):
    return dict(id=id, kind="copy", parents=[parent], run_id=run,
                result_digest=digest, attested=attested)


def bundle(nodes, *outputs):
    return {"nodes": nodes, "outputs": list(outputs)}


class LineagePilotTests(unittest.TestCase):
    def test_independent_executions_identical_digest(self):
        b = bundle([calc("a", "r1"), calc("b", "r2")], "a", "b")
        self.assertEqual(assess(b), DISTINCT)
        self.assertEqual(fixed_digest(b), SAME)

    def test_two_mirrors_same_root_new_job_ids(self):
        b = bundle([calc("root", "r1"), mirror("a", "root", "job-a"),
                    mirror("b", "root", "job-b")], "a", "b")
        self.assertEqual(assess(b), SAME)
        self.assertEqual(fixed_run_id(b), DISTINCT)
        self.assertEqual(next_verification(b), "chercher_une_execution_distincte")

    def test_changed_format_is_not_independent_execution(self):
        b = bundle([calc("root", "r1"), mirror("a", "root", "j1", "sha-a"),
                    mirror("b", "root", "j2", "sha-b")], "a", "b")
        self.assertEqual(assess(b), SAME)
        self.assertEqual(fixed_digest(b), DISTINCT)

    def test_missing_parent_must_abstain(self):
        b = bundle([mirror("a", "missing", "j1"), calc("b", "r2")], "a", "b")
        self.assertEqual(assess(b), UNKNOWN)

    def test_fake_attestation_must_abstain(self):
        b = bundle([calc("a", "r1"), mirror("b", "a", "j2", attested=False)], "a", "b")
        self.assertEqual(assess(b), UNKNOWN)

    def test_cycles_and_ambiguous_copies_abstain(self):
        b = bundle([mirror("a", "b", "j1"), mirror("b", "a", "j2")], "a", "b")
        self.assertEqual(assess(b), UNKNOWN)
        b["nodes"][0]["parents"] = ["b", "c"]
        self.assertEqual(assess(b), UNKNOWN)

    def test_inconsistent_independent_results_cannot_reproduce(self):
        b = bundle([calc("a", "r1", "sha1"), calc("b", "r2", "sha2")], "a", "b")
        self.assertEqual(assess(b), UNKNOWN)

    def test_duplicate_ids_and_outputs_abstain(self):
        b = bundle([calc("a", "r1"), calc("a", "r2")], "a", "a")
        self.assertEqual(assess(b), UNKNOWN)
        b["outputs"] = ["a", "b"]
        self.assertEqual(assess(b), UNKNOWN)

    def test_invalid_kind_or_parent_in_recompute(self):
        b = bundle([calc("a", "r1"), calc("b", "r2")], "a", "b")
        b["nodes"][0]["parents"] = ["b"]
        self.assertEqual(assess(b), UNKNOWN)

    def test_permutation_and_copy_depth_invariance(self):
        b = bundle([calc("root", "r1"), mirror("first", "root", "j1"),
                    mirror("second", "first", "j2")], "first", "second")
        self.assertEqual(assess(b), SAME)
        altered = copy.deepcopy(b)
        altered["nodes"].reverse()
        self.assertEqual(assess(altered), SAME)

    def test_synthetic_comparison_and_next_verification(self):
        cases = [
            {"bundle": bundle([calc("a", "r1"), calc("b", "r2")], "a", "b"), "expected": DISTINCT},
            {"bundle": bundle([calc("r", "origin"), mirror("a", "r", "j1"), mirror("b", "r", "j2")], "a", "b"), "expected": SAME},
            {"bundle": bundle([calc("r", "origin"), mirror("a", "r", "j1", "sha1"), mirror("b", "r", "j2", "sha2")], "a", "b"), "expected": SAME},
            {"bundle": bundle([mirror("a", "missing", "j1"), calc("b", "r2")], "a", "b"), "expected": UNKNOWN},
            {"bundle": bundle([calc("a", "r1", "sha1"), calc("b", "r2", "sha2")], "a", "b"), "expected": UNKNOWN},
        ]
        scores = compare_synthetic(cases)
        self.assertEqual(scores["lineage"].get("correct"), 5)
        self.assertGreater(scores["digest"].get("wrong_non_abstaining", 0), 0)
        self.assertGreater(scores["run_id"].get("wrong_non_abstaining", 0), 0)
        self.assertEqual(next_verification(cases[0]["bundle"]), "faire_revue_independante_du_contenu_scientifique")


if __name__ == "__main__":
    unittest.main()
