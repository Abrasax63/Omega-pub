"""Tests for multi-site repair, counterexamples and fail-closed neural selection."""
import hashlib
import unittest
from unittest.mock import patch

from multifault import (
    ROOT,EXPERIMENT,MAX_PATCHES,benchmark_sources,enumerate_patches,
    source_from_line_patch,CORRECT,public_suite,discriminant_suite,
    check_public,prepare_tasks,parse_choice,selector_prompt,qwen_choose,
    sha,notes_from_rce,
)
from reference import walks_exact


class MultiFaultTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=benchmark_sources()
        cls.tasks=prepare_tasks()

    def test_five_distinct_benchmark_sources(self):
        self.assertEqual(len(self.data),5)
        self.assertEqual(len({x["sha256"] for x in self.data}),5)
        self.assertEqual([r["audit_mutation_count"] for r in self.data],[1,1,1,1,2])
        self.assertEqual(len({r["audit_fault_lines"][0] for r in self.data[:4]}),4)

    def test_no_fault_location_supplied_to_generator(self):
        for item in self.data:
            hypotheses=enumerate_patches(item["source"])
            self.assertGreater(len(hypotheses),1)
            self.assertLessEqual(len(hypotheses),MAX_PATCHES)
            self.assertTrue(all(x["line"]>=1 for x in hypotheses))
            self.assertTrue(all(x["source"]!=item["source"] for x in hypotheses))

    def test_four_single_faults_repairable_on_strong_public(self):
        for t in self.tasks[:4]:
            with self.subTest(task=t["name"]):
                self.assertTrue(t["fully_public_survivors"])
                self.assertTrue(t["symbolic_full"])
                h=next(x for x in t["all_candidates"] if x["id"]==t["symbolic_full"])
                self.assertTrue(check_public(h["source"],discriminant_suite())["passed"])

    def test_two_fault_negative_control_abstains_from_one_line(self):
        self.assertEqual(self.tasks[4]["name"],"C5")
        self.assertEqual(self.tasks[4]["audit_mutation_count"],2)
        self.assertEqual(self.tasks[4]["fully_public_survivors"],[])
        self.assertIsNone(self.tasks[4]["symbolic_full"])

    def test_intentionally_weak_screen_retains_ambiguity(self):
        ambiguous=sum(len(t["weak_shortlist_ids"])>1 for t in self.tasks[:4])
        self.assertGreaterEqual(ambiguous,2)

    def test_all_candidates_modify_one_detected_line(self):
        for t in self.tasks:
            source=t["source"]
            before=source.splitlines()
            for h in t["all_candidates"]:
                after=h["source"].splitlines()
                changed=[i for i,(a,b) in enumerate(zip(before,after),1) if a!=b]
                self.assertEqual(changed,[h["line"]])
                self.assertEqual(h["source_sha256"],sha(h["source"]))

    def test_oracle_reference_correct_original(self):
        self.assertTrue(check_public(CORRECT,public_suite())["passed"])
        self.assertTrue(check_public(CORRECT,discriminant_suite())["passed"])

    def test_public_oracle_detects_multiple_kinds_of_bug(self):
        for task in self.tasks:
            result=check_public(task["source"],discriminant_suite())
            self.assertFalse(result["passed"],task["name"])
            self.assertIsNotNone(result["counterexample"])

    def test_multi_task_sources_hidden_from_model_except_code(self):
        notes=notes_from_rce(ROOT)
        for t in self.tasks:
            shortlist=[x for x in t["all_candidates"] if x["weak"]["passed"]]
            if not shortlist:
                continue
            p=selector_prompt(t["source"],shortlist,notes["memory"])
            self.assertNotIn("audit_fault_lines",p)
            self.assertNotIn("mutation_count",p)
            self.assertNotIn("reserved_manifest",p)
            self.assertIn("Candidates:",p)

    def test_lexical_rce_and_equal_character_budget(self):
        notes=notes_from_rce(ROOT)
        self.assertEqual(len(notes["memory"]),len(notes["placebo"]))
        self.assertTrue(notes["scientific_source"]["source_blob_sha256"])
        import hashlib
        src=ROOT/notes["scientific_source"]["path"]
        self.assertEqual(hashlib.sha256(src.read_bytes()).hexdigest(),
                         notes["scientific_source"]["source_blob_sha256"])

    def test_model_id_parsing_respects_whitelist_and_prompt(self):
        task=self.tasks[0]
        shortlist=[x for x in task["all_candidates"] if x["weak"]["passed"]]
        notes=notes_from_rce(ROOT)
        p=selector_prompt(task["source"],shortlist,notes["memory"])
        selected=shortlist[0]["id"]
        self.assertEqual(parse_choice(p+selected,p,{x["id"] for x in shortlist}),selected)
        with self.assertRaisesRegex(ValueError,"unambiguous"):
            parse_choice("banner"+p[:30],p,{selected})
        with self.assertRaisesRegex(ValueError,"not in"):
            parse_choice(p+"P99",p,{selected})
        with self.assertRaisesRegex(ValueError,"one exact"):
            parse_choice(p+selected+" "+selected,p,{selected})

    def test_no_silent_neural_fallback(self):
        import types
        task=self.tasks[0]
        shortlist=[x for x in task["all_candidates"] if x["weak"]["passed"]]
        with patch("multifault.subprocess.run",return_value=types.SimpleNamespace(
                returncode=0,stdout="unparseable",stderr="")):
            result=qwen_choose("fake-cli","fake-model",task["source"],
                               shortlist,"fake-placebo","control")
        self.assertTrue(result["called"])
        self.assertEqual(result["status"],"INVALID_ID")
        self.assertNotIn("selected_id",result)

    def test_invalid_one_line_source_change_cannot_pass(self):
        with self.assertRaises(ValueError):
            source_from_line_patch(CORRECT,0,"pass")
        with self.assertRaises((ValueError,SyntaxError)):
            source_from_line_patch(CORRECT,1,"import os")

    def test_benchmark_not_actual_external_blind_dataset(self):
        self.assertTrue(all("audit_fault_lines" in t for t in self.tasks))
        self.assertEqual(EXPERIMENT,"OMEGA-MULTIFAULT-01")


if __name__=="__main__":
    unittest.main()
