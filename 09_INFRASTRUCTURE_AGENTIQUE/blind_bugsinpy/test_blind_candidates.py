"""Prospective no-fix tests for generic, one-line AST rule grammar."""
import ast
import json
from pathlib import Path
import unittest
from blind_candidates import RULES,LIMIT,one_line,candidate_rules,read_json,HERE

class FreezeTests(unittest.TestCase):
    def test_cohort_frozen_and_no_previous_cases(self):
        x=read_json(HERE/"COHORT_FREEZE.json")
        self.assertEqual(x["experiment_id"],"OMEGA-BUGSINPY-BLIND-01")
        self.assertEqual([(c["project"],c["bug_id"]) for c in x["cases"]],
                         [("PySnooper","1"),("tqdm","2"),("cookiecutter","2")])
        self.assertTrue(all(len(c["buggy_sha"])==40 and len(c["fixed_sha"])==40 for c in x["cases"]))

    def test_grammar_is_finite_general_and_frozen(self):
        self.assertEqual(LIMIT,60)
        self.assertEqual(len(RULES),7)
        self.assertNotIn("pysnooper",str(RULES).lower())
        self.assertNotIn("cookiecutter",str(RULES).lower())

    def test_one_line_exact_and_valid_ast(self):
        src="def f(x):\n    return x\n"
        self.assertEqual(one_line(src,2,"    return x + 1"),"def f(x):\n    return x + 1\n")
        with self.assertRaises(ValueError):
            one_line(src,2,"    return x")
        with self.assertRaises(SyntaxError):
            one_line(src,1,"if 42:")

    def test_generic_encoding_patch(self):
        src="def f(p):\n    with open(p) as f:\n        return f.read()\n"
        edits=candidate_rules(src)
        self.assertTrue(any("encoding='utf-8'" in c["replacement"] for c in edits))
        self.assertTrue(all(c["source_sha256"]!=c["modified_sha256"] for c in edits))

    def test_unbound_open_name_swap_not_injected_fix(self):
        src=("def f(out):\n    def run():\n"
             "        with open(wrong, 'a') as f:\n            pass\n"
             "    return run\n")
        edits=candidate_rules(src)
        self.assertTrue(any("open(out, 'a')" in c["replacement"] for c in edits))

    def test_original_bug_not_known_or_hardcoded(self):
        src=("def enum(items,start):\n"
             "    return enumerate(show(items,start))\n")
        edits=candidate_rules(src)
        self.assertTrue(any("enumerate(show(items), start)" in c["replacement"] for c in edits))
        self.assertFalse(any("fixed_sha" in repr(c) for c in edits))

    def test_source_syntax_never_executes_during_freeze(self):
        source="def broken(:\n  pass\n"
        self.assertEqual(candidate_rules(source),[])
        self.assertFalse(any(c.get("run") for c in candidate_rules(
            "def f(x):\n    if x:\n        return 1\n    return 0\n")))

if __name__=="__main__":
    unittest.main()
