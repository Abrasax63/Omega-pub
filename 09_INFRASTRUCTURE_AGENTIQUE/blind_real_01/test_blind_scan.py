"""No-network local regression tests for the bounded blind source probe."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from blind_scan import candidate_manifest, MAX_CASE_CANDIDATES
from external_real import CASES


class BlindScanTests(unittest.TestCase):
    def test_generic_pattern_candidates_on_unseen_function(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "fastapi"
            p.mkdir()
            (p / "core.py").write_text(
                "def fresh(output):\n"
                "    with open(missing_path, 'a') as f:\n"
                "        f.write('x')\n", encoding="utf-8")
            r = candidate_manifest(Path(tmp))
            self.assertEqual(r["status"], "CANDIDATES_UNTESTED")
            self.assertGreaterEqual(len(r["candidates"]), 2)
            self.assertTrue(all(c["file"] == "fastapi/core.py" for c in r["candidates"]))
            self.assertTrue(any("open(output, 'a')" in c["new"] for c in r["candidates"]))
            self.assertNotIn("_BLIND_SCAN", CASES)

    def test_absence_of_matching_rule_is_negative_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "fastapi"
            p.mkdir()
            (p / "simple.py").write_text(
                "def square(x):\n    return x*x\n", encoding="utf-8")
            r = candidate_manifest(Path(tmp))
            self.assertEqual(r["status"], "NO_CANDIDATE")
            self.assertEqual(r["candidates"], [])

    def test_never_inspects_fixed_directory_and_never_changes_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fastapi").mkdir()
            (root / "fixed").mkdir()
            source = "def square(x):\n    return x*x\n"
            (root / "fastapi" / "core.py").write_text(source, encoding="utf-8")
            (root / "fixed" / "secret.py").write_text(
                "def patch():\n    return open(foo, 'a')\n", encoding="utf-8")
            r = candidate_manifest(root)
            self.assertEqual(r["scanned_files"], 1)
            self.assertEqual((root / "fastapi" / "core.py").read_text(), source)
            self.assertEqual(r["status"], "NO_CANDIDATE")

    def test_bound_is_enforced_as_failed_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "fastapi").mkdir()
            (root / "fastapi" / "core.py").write_text(
                "def copy(output):\n"
                "    with open(foo, 'a') as f:\n"
                "        f.write('x')\n", encoding="utf-8")
            r = candidate_manifest(root, max_candidates=0)
            self.assertEqual(r["status"], "BUDGET_EXCEEDED")
            self.assertEqual(len(r["candidates"]), 0)
            self.assertGreaterEqual(r["total_seen_at_least"], 1)

    def test_default_budget_remains_fixed(self):
        self.assertEqual(MAX_CASE_CANDIDATES, 60)


if __name__ == "__main__":
    unittest.main()
