"""Regressions for the V2 reader; no inference and no used holdout replay."""
import json
from pathlib import Path
import sys
import unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import pilot
import reader_v2


class ReaderV2Tests(unittest.TestCase):
    def test_parse_unchanged_good_code(self):
        code="def transform(s):\n    return [s]\n"
        decoded, status=reader_v2.inspect_candidate(json.dumps({"code":code}),pilot.safe)
        self.assertEqual(status,"SAFE_PYTHON_UNCHANGED")
        self.assertEqual(decoded,code)

    def test_recover_real_observed_format(self):
        emitted="def transform(s):\\n    out=[]\\n    for ch in s:\\n        out.append(ch.lower())\\n    return out"
        recovered,status=reader_v2.inspect_candidate(json.dumps({"code":emitted}),pilot.safe)
        self.assertEqual(status,"SAFE_PYTHON_FORMAT_NORMALIZED_NOT_LEARNING")
        self.assertEqual(recovered.count("\n"),4)
        self.assertEqual(pilot.safe.execute_student(recovered,["Ab"])[0].get("value"),
                         ["a","b"])

    def test_preserve_literal_string_backslash_n(self):
        emitted="def transform(s):\\n    return ['\\\\n']"
        recovered,status=reader_v2.inspect_candidate(json.dumps({"code":emitted}),pilot.safe)
        self.assertEqual(status,"SAFE_PYTHON_FORMAT_NORMALIZED_NOT_LEARNING")
        self.assertIn("['\\\\n']",recovered)
        self.assertEqual(pilot.safe.execute_student(recovered,["x"])[0].get("value"),
                         ["\\n"])

    def test_forbidden_code_must_remain_forbidden_after_recovery(self):
        for code in [
            "def transform(s):\\n    return open('passwords')",
            "def transform(s):\\n    return eval(s)",
            "def transform(s):\\n    import os\\n    return []",
            "def transform(s):\\n    return __import__('os')",
        ]:
            with self.subTest(code=code):
                value,status=reader_v2.inspect_candidate(
                    json.dumps({"code":code}),pilot.safe)
                self.assertIsNone(value)
                self.assertNotIn(status,
                                 ("SAFE_PYTHON_UNCHANGED",
                                  "SAFE_PYTHON_FORMAT_NORMALIZED_NOT_LEARNING"))

    def test_fail_closed_on_ambiguous_and_invalid_json(self):
        for code in [
            "def transform(s):\\n    return '''a'''",
            "def transform(s):\\n    return }",
            "def transform(s):\n    return [s]\\n",
            "something else:\\n    return []",
        ]:
            self.assertIsNone(reader_v2.inspect_candidate(
                json.dumps({"code":code}),pilot.safe)[0])
        self.assertIsNone(reader_v2.inspect_candidate("{not json",pilot.safe)[0])

    def test_no_raw_mutation_or_semantic_rewrite(self):
        s="def transform(s):\\n    return [s+'!']"
        raw=json.dumps({"code":s})
        recovered,status=reader_v2.inspect_candidate(raw,pilot.safe)
        self.assertEqual(json.loads(raw)["code"],s)
        self.assertEqual(recovered,"def transform(s):\n    return [s+'!']")
        self.assertEqual(status,"SAFE_PYTHON_FORMAT_NORMALIZED_NOT_LEARNING")

    def test_old_pilot_score_not_reinterpreted(self):
        # This successor adds only an OPTIONAL import, not a patch to pilot.py
        # or score.py. A future runner must explicitly opt in on a fresh cohort.
        original_pilot=(HERE/"pilot.py").read_text()
        original_score=(HERE/"score.py").read_text()
        self.assertNotIn("import reader_v2", original_pilot)
        self.assertNotIn("import reader_v2", original_score)
        self.assertNotIn("reader_v2.inspect_candidate", original_pilot)
        self.assertEqual(len(pilot.PINS),3)


if __name__=="__main__":
    unittest.main()
