"""Smoke tests for AST proposal grammar; no internet or model required."""
import ast
import unittest
from unittest.mock import patch

from external_real import CASES, find_patches, one_line_change, digest, MAX_CANDIDATES


class ExternalRealSmokeTests(unittest.TestCase):
    def test_three_independent_repos_and_pinned_shas(self):
        self.assertEqual(len(CASES), 3)
        self.assertEqual(len({x["repo"] for x in CASES.values()}), 3)
        for item in CASES.values():
            self.assertEqual(len(item["buggy"]), 40)
            self.assertEqual(len(item["fixed"]), 40)
            self.assertEqual(len(item["buggy_blob"]), 40)

    def test_single_line_patch_rejects_more_changes(self):
        source="def f(x):\n    return x\n"
        self.assertEqual(one_line_change(source,2,"    return x + 1"),
                         "def f(x):\n    return x + 1\n")
        with self.assertRaises((ValueError,SyntaxError)):
            one_line_change(source,1,"import os")
        with self.assertRaises(ValueError):
            one_line_change(source,2,"    return x")

    def test_unbound_file_path_candidates_are_from_arg_names(self):
        source=("def get_write_function(output):\n"
                "    def write(s):\n"
                "        with open(output_path, 'a') as writer:\n"
                "            writer.write(s)\n"
                "    return write\n")
        proposals=find_patches("E1",source)
        self.assertGreaterEqual(len(proposals),2)
        self.assertTrue(any("open(output, 'a')" in p["new"] for p in proposals))
        self.assertTrue(all(p["line"]==3 for p in proposals))

    def test_nested_enumerate_candidates_include_start_relocation(self):
        source=("def tenumerate(iterable, start=0, total=None, tqdm_class=None, **kwargs):\n"
                "    return enumerate(tqdm_class(iterable, start, **kwargs))\n")
        proposals=find_patches("E2",source)
        self.assertGreaterEqual(len(proposals),2)
        self.assertTrue(any("enumerate(tqdm_class(iterable, **kwargs), start)"
                            in p["new"] for p in proposals))

    def test_file_read_candidates_include_utf8(self):
        source=("def generate_context(context_file):\n"
                "    with open(context_file) as handle:\n"
                "        return handle.read()\n")
        proposals=find_patches("E3",source)
        self.assertTrue(any("encoding='utf-8'" in p["new"] for p in proposals))
        self.assertTrue(all(len(p["source"].splitlines())==3 for p in proposals))

    def test_candidates_have_unique_source_hashes(self):
        for case,source in [
            ("E1","def get_write_function(output):\n    with open(foo, 'a') as f:\n        pass\n"),
            ("E2","def tenumerate(a,start=0,tqdm_class=None):\n    return enumerate(tqdm_class(a,start))\n"),
            ("E3","def generate_context(filename):\n    with open(filename) as f:\n        pass\n"),
        ]:
            p=find_patches(case,source)
            self.assertLessEqual(len(p),MAX_CANDIDATES)
            self.assertEqual(len({x["sha256"] for x in p}),len(p))


if __name__=="__main__":
    unittest.main()
