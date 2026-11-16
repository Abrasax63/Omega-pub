"""Unit tests for LOC03: sealed prospective 2x2 ablation & abstention."""
import ast
from pathlib import Path
import tempfile
import unittest

from loc03 import (CASES,ARMS,SITE_LIMIT,chosen_guard,all_sites,
                   baseline_edits,seal,verify,stage,judge,diff_sites,digest)

class Loc03Tests(unittest.TestCase):
    def test_cases_pre_registered_and_distinct_from_consumed_case(self):
        self.assertEqual(set(CASES),{"tqdm-5","tqdm-8"})
        self.assertEqual(len(ARMS),4)
        self.assertEqual(SITE_LIMIT,10)
        for meta in CASES.values():
            self.assertEqual(len(meta["bug"]),40)
            self.assertEqual(len(meta["fixed"]),40)
            self.assertEqual(len(meta["test_blob"]),40)

    def test_guard_is_generic_and_syntactically_valid(self):
        src="def f(total, scale):\n    total *= scale\n    return total\n"
        nodes=[n for n in ast.walk(ast.parse(src))
               if isinstance(n,ast.AugAssign)]
        guard=chosen_guard(src,nodes,2)
        self.assertEqual(guard["replacement"],"    if total: total *= scale")
        self.assertEqual(guard["rule"],"guard-first-variable")

    def test_guard_rejects_non_statement_and_multiline(self):
        src="def f(a):\n    if a:\n        return a\n"
        nodes=[n for n in ast.walk(ast.parse(src)) if isinstance(n,ast.If)]
        self.assertIsNone(chosen_guard(src,nodes,2))

    def test_broad_ast_site_universe_includes_line_without_patch_rule(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"tqdm").mkdir()
            (root/"tqdm"/"a.py").write_text(
                "def f(x):\n    x *= 4\n    return x\n")
            (root/"tqdm"/"tests").mkdir()
            (root/"tqdm"/"tests"/"test_a.py").write_text("assert False\n")
            sites,sources,nodes=all_sites(root)
            self.assertIn(("tqdm/a.py",2),sites)
            self.assertNotIn(("tqdm/tests/test_a.py",1),sites)
            self.assertEqual(len(sites),len(set(sites)))

    def test_original_grammar_unmodified_g0_edits(self):
        src="def f(p):\n    with open(p) as f:\n        return f.read()\n"
        result=baseline_edits({"tqdm/a.py":src},[("tqdm/a.py",2)])
        self.assertIn(("tqdm/a.py",2),result)
        self.assertEqual(result[("tqdm/a.py",2)]["rule"],"encoding-explicit")

    def test_seal_detects_mutation_and_fixed_leak(self):
        d=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_code_seen":False,
            "budget_sites":10,"case":"tqdm-5"})
        self.assertTrue(verify(d))
        d["budget_sites"]=11
        with self.assertRaises(ValueError): verify(d)
        d=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_code_seen":True,
            "budget_sites":10,"case":"tqdm-5"})
        with self.assertRaises(ValueError): verify(d)

    def test_diff_excludes_test_files_and_counts_old_side_only(self):
        diff=("diff --git a/tqdm/_tqdm.py b/tqdm/_tqdm.py\n"
             "@@ -12,2 +12,3 @@\n-x\n+x\n"
             "@@ -51,0 +53,2 @@\n+insert\n"
             "diff --git a/tqdm/tests/tests_tqdm.py b/tqdm/tests/tests_tqdm.py\n"
             "@@ -5 +5 @@\n-x\n+y\n")
        self.assertEqual(diff_sites(diff),
          {("tqdm/_tqdm.py",12),("tqdm/_tqdm.py",13)})

    def test_four_arm_scoring_and_failure_gates(self):
        row={"path":"tqdm/a.py","line":2}
        frozen=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_code_seen":False,
             "budget_sites":10,"case":"tqdm-5",
             "buggy_pytest_exit":1,"trace_status":"VALID",
             "rankings":{"S":[row],"T":[row]},
             "plans":{a:[dict(row,rank=1,replacement=None)] for a in ARMS}})
        attempts=[{"arm":a,"rank":1,"status":"ABSTAIN_NO_RULE"} for a in ARMS]
        diff="diff --git a/tqdm/a.py b/tqdm/a.py\n@@ -2 +2 @@\n-x\n+y\n"
        valid=judge(frozen,attempts,diff,1,0)
        self.assertEqual(valid["status"],"EVALUATED")
        self.assertTrue(valid["arms"]["S-G0"]["exact_localization_success"])
        self.assertFalse(valid["arms"]["S-G0"]["bounded_repair_success"])
        blocked=judge(frozen,attempts,diff,0,0)
        self.assertEqual(blocked["status"],"BUG_NOT_REPRODUCED")
        self.assertIsNone(blocked["arms"]["T-G1"]["exact_localization_success"])

    def test_stage_does_not_read_fixed_source(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/"tqdm").mkdir()
            src="def f(x):\n    x *= 2\n    return x\n"
            (root/"tqdm"/"a.py").write_text(src)
            from loc03 import one_line
            patched=one_line(src,2,"    if x: x *= 2")
            row={"rank":1,"path":"tqdm/a.py","line":2,
                 "source_sha256":digest(src),"replacement":"    if x: x *= 2",
                 "modified_sha256":digest(patched),"rule":"guard-first-variable"}
            frozen=seal({"phase":"BUGGY_ONLY_FROZEN","fixed_code_seen":False,
                        "budget_sites":10,"case":"tqdm-5",
                        "plans":{a:([row] if a=="T-G1" else []) for a in ARMS}})
            manifest=stage(frozen,root,root/"candidate-out")
            self.assertEqual(len(manifest),1)
            self.assertEqual(manifest[0]["status"],"READY")
            self.assertEqual((root/"tqdm"/"a.py").read_text(),src)

if __name__=="__main__":
    unittest.main()
