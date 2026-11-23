"""Offline guards for the post-hoc formatter; no LLM, no training."""
import json
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import format_audit as a
import pilot


class FormatAuditRegression(unittest.TestCase):
    def test_escaped_delimiters_recovered_narrowly(self):
        source = "def transform(s):\\n    out = []\\n    return out"
        recovered, status = a.decode_line_delimiters_only(source)
        self.assertEqual(status, "FORMAT_RECOVERED_POST_HOC")
        self.assertEqual(recovered, "def transform(s):\n    out = []\n    return out")
        self.assertTrue(pilot.safe.validate_program(recovered))

    def test_preserves_escaped_newline_inside_python_string(self):
        source = "def transform(s):\\n    return ['\\\\n']"
        recovered, status = a.decode_line_delimiters_only(source)
        self.assertEqual(status, "FORMAT_RECOVERED_POST_HOC")
        self.assertIn("['\\\\n']", recovered)
        self.assertEqual(pilot.safe.execute_student(recovered, ["a"])[0]["value"],
                         ["\\n"])

    def test_does_not_rewrite_existing_real_line_breaks(self):
        original = "def transform(s):\n    return [s]"
        self.assertIsNone(a.decode_line_delimiters_only(original)[0])
        self.assertEqual(a.recover_raw(json.dumps({"code": original}))[1],
                         "ORIGINAL_SAFE_NO_CHANGE")

    def test_disallows_invalid_or_ambiguous_inputs(self):
        invalid = [
            "def transform(s):\\n    return open('secret')",
            "def transform(s):\\n    return eval(s)",
            "def transform(s):\\n    import os\\n    return []",
            "def transform(s):\\n    return }",
            "def transform(s):\\n    return '''text'''",
            "other(s):\\n    return []",
        ]
        for s in invalid:
            with self.subTest(s=s):
                self.assertIsNone(a.decode_line_delimiters_only(s)[0])

    def test_invalid_json_fails_closed(self):
        self.assertIsNone(a.recover_raw("not JSON")[0])
        self.assertIsNone(a.recover_raw('{"code": "def transform(s):\\\\n"')[0])

    def test_original_output_never_overwritten(self):
        raw = json.dumps({"code": "def transform(s):\\n    return [s]"})
        source = json.loads(raw)["code"]
        recovered, status = a.recover_raw(raw)
        self.assertEqual(status, "FORMAT_RECOVERED_POST_HOC")
        self.assertEqual(json.loads(raw)["code"], source)
        self.assertNotEqual(recovered, source)

    def test_pins_target_single_archived_run(self):
        self.assertEqual(a.SOURCE_RUN, 45118652661)
        self.assertEqual(len(a.ARCHIVED_RAW_SHA256), 64)
        self.assertEqual(len(a.ARCHIVED_ORIGINAL_SCORE_SHA256), 64)


if __name__ == "__main__":
    unittest.main()
