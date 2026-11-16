"""Tests of actual sys.setprofile evidence, source ranking and bounded AST edits."""
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from rank_suspects import parse_call_trace,rank_files,test_symbols
from bounded_patch import proposals_for_source,select_candidates,rewrite,MAX_CANDIDATES

HERE=Path(__file__).resolve().parent

class TraceGuidedTests(unittest.TestCase):
    def test_real_child_python_emits_package_call_trace(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            pkg=base/"pkg"
            pkg.mkdir()
            (pkg/"__init__.py").write_text("from .hooks import find_hook\n",encoding="utf8")
            (pkg/"hooks.py").write_text("def find_hook(x):\n    return x + 1\n",encoding="utf8")
            env=dict(os.environ)
            env["OMEGA_TRACE_ROOT"]=str(pkg)
            env["PYTHONPATH"]=str(HERE)+os.pathsep+str(base)
            p=subprocess.run([sys.executable,"-c","import pkg; assert pkg.find_hook(4)==5"],
                             env=env,text=True,capture_output=True,timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            trace=parse_call_trace(p.stderr)
            self.assertTrue(any(x["path"]=="hooks.py" for x in trace))
            source="from pkg import hooks\n\ndef test_find_hook():\n    assert hooks.find_hook(4)==5\n"
            ranked=rank_files(base,"pkg",trace,source,"test_find_hook")
            self.assertEqual(ranked["top3"][0],"pkg/hooks.py")
            self.assertTrue(ranked["ranked"][0]["score"]>0)

    def test_trace_must_not_be_missing_or_ambiguous(self):
        for s in ("","a\nb\n", "OMEGA_CALL_TRACE_V1={}\n"):
            with self.subTest(s=s):
                with self.assertRaises(ValueError):
                    parse_call_trace(s)

    def test_disallow_path_traversal_in_trace(self):
        fake={"schema":"omega-calltrace-v1","files":[{
            "path":"../other.py","total_calls":1,
            "functions":[{"label":"f@1","calls":1}]
        }]}
        with self.assertRaises(ValueError):
            parse_call_trace("OMEGA_CALL_TRACE_V1="+json.dumps(fake))

    def test_test_symbol_matches_import_and_called_method(self):
        text="from cookiecutter import hooks\nclass TestH:\n    def test_find_hook(self):\n        hooks.find_hook('x')\n"
        ev=test_symbols(text,"test_find_hook")
        self.assertIn("find_hook",ev["symbols"])
        self.assertIn("cookiecutter",ev["imports"])

    def test_genuine_two_line_repair_generated_for_one_function(self):
        src=("def f(x):\n"
             "    if x is None:\n"
             "        return None\n"
             "    return x\n")
        p=proposals_for_source(src)
        two=[x for x in p if len(x["lines"])==2]
        self.assertTrue(two)
        self.assertTrue(all(len(x["changes"])==2 for x in two))
        for candidate in two:
            changed=rewrite(src,{x["line"]:x["after"] for x in candidate["changes"]})
            self.assertEqual(len(changed.splitlines()),len(src.splitlines()))
            ast.parse(changed)

    def test_no_cross_function_candidate_even_with_two_lines(self):
        src=("def a(x):\n    if x:\n        return x\n"
             "def b(y):\n    if y:\n        return y\n")
        self.assertTrue(all(len(c["lines"])<=2 for c in proposals_for_source(src)))
        for entry in proposals_for_source(src):
            if len(entry["lines"])==2:
                self.assertTrue(max(entry["lines"])<=3 or min(entry["lines"])>=4)

    def test_patch_does_not_insert_code_or_lines(self):
        s="def f(x):\n    return x\n"
        with self.assertRaises(ValueError):
            rewrite(s,{2:"    return x\n    import os"})
        with self.assertRaises(ValueError):
            rewrite(s,{2:"    return x"})

    def test_rank_is_deterministic_and_no_oracle_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"pkg").mkdir()
            (root/"pkg"/"alpha.py").write_text("def f():\n    pass\n",encoding="utf8")
            (root/"pkg"/"hooks.py").write_text("def find_hook():\n    pass\n",encoding="utf8")
            records=[
                {"path":"alpha.py","total_calls":8,"functions":[{"label":"f@1","calls":8}]},
                {"path":"hooks.py","total_calls":1,"functions":[{"label":"find_hook@1","calls":1}]},
            ]
            test="def test_find_hook():\n    find_hook()\n"
            a=rank_files(root,"pkg",records,test,"test_find_hook")
            b=rank_files(root,"pkg",list(reversed(records)),test,"test_find_hook")
            self.assertEqual(a,b)
            self.assertEqual(a["top3"][0],"pkg/hooks.py")
            self.assertFalse(a["oracle_corrected_source_used"])
            candidates=select_candidates(root,a)
            self.assertLessEqual(candidates["candidate_count"],MAX_CANDIDATES)
            self.assertFalse(candidates["fixed_source_inspected"])

    def test_prioritize_named_function_inside_traced_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"pkg").mkdir()
            source=("def unrelated(x):\n    if x:\n        return x\n    return None\n"
                    "def target(x):\n    if x is None:\n        return None\n    return x\n")
            (root/"pkg"/"f.py").write_text(source,encoding="utf8")
            rank={"status":"RANKED","top3":["pkg/f.py"],
                  "test_evidence":{"symbols":["target"]}}
            data=select_candidates(root,rank)
            self.assertTrue(data["candidates"])
            self.assertEqual(data["candidates"][0]["function_name"],"target")
            self.assertLessEqual(data["candidate_count"],MAX_CANDIDATES)

if __name__=="__main__":
    unittest.main()
