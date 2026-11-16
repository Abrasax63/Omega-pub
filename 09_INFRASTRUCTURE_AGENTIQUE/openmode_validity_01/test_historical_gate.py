"""No-network semantic gate tests; no Scrapy imports or model calls."""
import hashlib
import re
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from historical_gate import git_blob, upstream_method, semantic_input, gate


class HistoricalGateTests(unittest.TestCase):
    def test_original_function_ast_can_be_extracted_without_importing_scrapy(self):
        text = ("import re\n"
                "class OffsiteMiddleware:\n"
                "    def get_host_regex(self, spider):\n"
                "        return re.compile(r'^(.*\\.)?(scrapytest\\.org)$')\n")
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "offsite.py"
            p.write_text(text, encoding="utf-8")
            fun = upstream_method(p, git_blob(p.read_bytes()))
            self.assertTrue(semantic_input(fun, ["scrapytest.org"])["passed"])

    def test_unverified_original_sha_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "offsite.py"
            p.write_text("class C: pass\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "HISTORICAL_BLOB_DRIFT"):
                upstream_method(p, "0" * 40)

    def test_reproducer_gate_does_not_accept_wrong_buggy_behavior(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "FILTER_REPORT_DRIFT"):
                gate(Path(tmp)/"bad.py", Path(tmp)/"fixed.py", b"{}")

    def test_semantic_missing_none_is_not_historical_reproduction(self):
        def all_ok(_self, spider):
            return re.compile(r"^(.*\\.)?(scrapytest\\.org)$")
        r = semantic_input(all_ok, ["scrapytest.org", None])
        self.assertTrue(r["passed"])
        # Only an original pinned buggy/fixed pair can establish the status,
        # so a passing synthetic fixture is never counted as buggy FAIL.


if __name__ == "__main__":
    unittest.main()
