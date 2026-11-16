"""Unit/regression tests for the source-backed frozen candidate safety filter."""
import ast
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from openmode_filter import extract_open_call, probe_builtin_open, classify_candidate, audit
from external_real import one_line_change
from blind_scan import sha


class OpenModeFilterTests(unittest.TestCase):
    def test_binary_modes_rejected_by_real_stdlib(self):
        for mode in ("rb", "wb", "rb+", "ab", "xb"):
            source = "def f(path):\n    with open(path, '" + mode + "', encoding='utf-8') as f:\n        pass\n"
            self.assertEqual(extract_open_call(source, 2), (mode, "utf-8"))
            probe = probe_builtin_open(mode, "utf-8")
            self.assertEqual(probe["status"], "RAISED", mode)
            self.assertEqual(probe["exception"], "ValueError", mode)

    def test_text_modes_accepted_by_real_stdlib(self):
        for mode in ("r", "w", "a", "r+", "x"):
            source = "def f(path):\n    with open(path, '" + mode + "', encoding='utf-8') as f:\n        pass\n"
            self.assertEqual(extract_open_call(source, 2), (mode, "utf-8"))
            self.assertEqual(probe_builtin_open(mode, "utf-8")["status"], "OPEN_OK", mode)

    def test_default_text_mode_is_not_binary(self):
        source = "def f(path):\n    with open(path, encoding='utf-8') as f:\n        pass\n"
        self.assertEqual(extract_open_call(source, 2), ("r", "utf-8"))

    def test_nonliteral_mode_is_unknown(self):
        source = "def f(path, mode):\n    with open(path, mode, encoding='utf-8') as f:\n        pass\n"
        self.assertEqual(extract_open_call(source, 2), (None, "UNKNOWN_MODE"))

    def test_rebound_open_is_unknown_not_confident(self):
        source = ("def f(path):\n"
                  "    open = lambda *args, **kwargs: None\n"
                  "    with open(path, 'rb', encoding='utf-8') as f:\n"
                  "        pass\n")
        self.assertEqual(extract_open_call(source, 3), (None, "UNKNOWN_OPEN_BINDING"))

    def test_one_line_patch_hashes_and_source_preservation(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            pkg = root / "scrapy"
            pkg.mkdir()
            path = pkg / "x.py"
            source = "def f(path):\n    with open(path, 'rb') as f:\n        pass\n"
            path.write_text(source, encoding="utf-8")
            line = "    with open(path, 'rb', encoding='latin-1') as f:"
            patched = one_line_change(source, 2, line)
            ast.parse(patched)
            item = {"file": "scrapy/x.py", "line": 2,
                    "old": "    with open(path, 'rb') as f:",
                    "new": line, "buggy_file_sha256": sha(source),
                    "source_sha256": sha(patched)}
            result = classify_candidate(root, item)
            self.assertEqual(result["status"], "REJECT_CERTAIN_BINARY_ENCODING")
            self.assertEqual(result["probe"]["exception"], "ValueError")
            self.assertEqual(path.read_text(encoding="utf-8"), source)

    def test_manifest_drift_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError, "MANIFEST_DRIFT"):
                audit(Path(d), b'{"fake": 1}')

    def test_source_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "scrapy").mkdir()
            (root / "scrapy" / "x.py").write_text(
                "def f():\n    pass\n", encoding="utf-8")
            item = {"file": "scrapy/x.py", "line": 2, "old": "    pass",
                    "new": "    return True", "source_sha256": "0"*64,
                    "buggy_file_sha256": "1"*64}
            with self.assertRaisesRegex(ValueError, "SOURCE_MISMATCH"):
                classify_candidate(root, item)


if __name__ == "__main__":
    unittest.main()
