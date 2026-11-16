"""No-network regression tests for OMEGA-SCOPE-METHODS-01."""
import ast
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from method_scope import compare, scan_top_level, scan_methods, _method_fragment
from external_real import CASES, one_line_change


def fixture(root: Path, content: str):
    pkg = root / "scrapy"
    pkg.mkdir()
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "core.py").write_text(content, encoding="utf-8")
    return pkg / "core.py"


class ScopeTests(unittest.TestCase):
    def test_methods_add_only_incremental_candidates(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = fixture(root,
                "class Engine:\n"
                "    def write(self, output):\n"
                "        with open(missing_path, 'a') as stream:\n"
                "            stream.write('ok')\n")
            result = compare(root)
            self.assertEqual(result["comparison_status"], "COVERAGE_INCREASED")
            self.assertEqual(len(result["arm_a_top_level"]["candidates"]), 0)
            extras = result["arm_b_increment_methods"]["candidates"]
            self.assertGreaterEqual(len(extras), 1)
            for candidate in extras:
                self.assertEqual(candidate["line"], 3)
                self.assertEqual(candidate["file"], "scrapy/core.py")
                source = path.read_text(encoding="utf-8")
                patched = one_line_change(source, candidate["line"], candidate["new"])
                self.assertEqual(hashlib.sha256(patched.encode()).hexdigest(),
                                 candidate["source_sha256"])
                ast.parse(patched)
            self.assertNotIn("_BLIND_SCAN", CASES)
            self.assertEqual(path.read_text(encoding="utf-8"),
                "class Engine:\n"
                "    def write(self, output):\n"
                "        with open(missing_path, 'a') as stream:\n"
                "            stream.write('ok')\n")

    def test_existing_top_level_candidates_are_kept(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root,
                "def public(output):\n"
                "    with open(missing_path, 'a') as stream:\n"
                "        stream.write('a')\n"
                "class Engine:\n"
                "    def write(self, output):\n"
                "        with open(missing_path, 'a') as stream:\n"
                "            stream.write('b')\n")
            result = compare(root)
            self.assertGreater(len(result["arm_a_top_level"]["candidates"]), 0)
            self.assertGreater(len(result["arm_b_increment_methods"]["candidates"]), 0)
            self.assertEqual(result["arm_b_total_candidate_count_if_within_budget"],
               len(result["arm_a_top_level"]["candidates"]) +
               len(result["arm_b_increment_methods"]["candidates"]))

    def test_frozen_rules_unchanged_and_no_fixed_access(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root, "def square(x):\n    return x * x\n")
            (root / "fixed").mkdir()
            (root / "fixed" / "secret.py").write_text(
                "class C:\n    def m(self, path):\n"
                "        with open(secret, 'a') as stream:\n"
                "            stream.write('forbidden')\n", encoding="utf-8")
            result = compare(root)
            self.assertEqual(result["comparison_status"], "NO_INCREMENTAL_CANDIDATE")
            self.assertFalse(result["historical_fixed_accessed"])
            self.assertFalse(result["model_called"])
            self.assertIsNone(result["repair_correctness"])
            self.assertEqual(result["arm_b_increment_methods"]["methods_seen"], 0)

    def test_decorated_async_excluded_by_prereg(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root,
                "class C:\n"
                "    @staticmethod\n"
                "    def ignored(path):\n"
                "        with open(bad, 'a') as f:\n"
                "            f.write('x')\n"
                "    async def also_ignored(self, path):\n"
                "        with open(bad, 'a') as f:\n"
                "            f.write('y')\n")
            result = scan_methods(root)
            self.assertEqual(result["decorated_skipped"], 1)
            self.assertEqual(result["async_skipped"], 1)
            self.assertEqual(result["candidates"], [])

    def test_budget_violations_are_not_success(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixture(root,
                "class C:\n"
                "    def m(self, output):\n"
                "        with open(missing, 'a') as stream:\n"
                "            stream.write('x')\n")
            result = compare(root, max_candidates=0)
            self.assertEqual(result["comparison_status"], "BUDGET_EXCEEDED")
            self.assertEqual(result["arm_b_increment_methods"]["status"], "BUDGET_EXCEEDED")
            self.assertEqual(len(result["arm_b_increment_methods"]["candidates"]), 0)

    def test_empty_project_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = compare(Path(tmp))
            self.assertEqual(result["comparison_status"], "SOURCE_UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
