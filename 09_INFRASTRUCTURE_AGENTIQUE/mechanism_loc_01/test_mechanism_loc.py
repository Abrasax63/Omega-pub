"""Deterministic no-network regression tests for frozen static localization."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from localize import rank, sha, normalized_tokens
from evaluate_oracle import evaluate


def fixture(tmp: str):
    root=Path(tmp)
    (root/"httpie").mkdir()
    (root/"tests").mkdir()
    (root/"httpie"/"a.py").write_text(
        "def unrelated():\n    return 1\n",encoding="utf-8")
    (root/"httpie"/"downloads.py").write_text(
        "class DownloadManager:\n"
        "    def download(self, url):\n"
        "        return url\n",encoding="utf-8")
    (root/"tests"/"test_downloads.py").write_text(
        "from httpie.downloads import DownloadManager\n"
        "def test_downloads():\n"
        "    DownloadManager().download('https://example.test')\n",encoding="utf-8")
    return root


class LocationUnitTests(unittest.TestCase):
    def test_both_arms_have_same_inventory_and_both_rank(self):
        with tempfile.TemporaryDirectory() as d:
            root=fixture(d)
            out=rank(root)
            self.assertEqual(out["status"],"CHOICES_FROZEN")
            self.assertEqual(len(out["targets"]),2)
            self.assertEqual({t["rank_a"] for t in out["targets"]},{1,2})
            self.assertEqual({t["rank_b"] for t in out["targets"]},{1,2})
            lookup={t["qualname"]:t for t in out["targets"]}
            self.assertEqual(lookup["DownloadManager.download"]["rank_b"],1)
            self.assertEqual(lookup["unrelated"]["rank_a"],1)
            self.assertEqual(out["test_sha256"],
                             sha((root/"tests"/"test_downloads.py").read_bytes()))
            self.assertFalse(out["historic_fixed_accessed"])

    def test_frozen_diff_identifies_modified_method_only(self):
        with tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as f:
            old=fixture(b)
            new=fixture(f)
            (new/"httpie"/"downloads.py").write_text(
                "class DownloadManager:\n"
                "    def download(self, url):\n"
                "        return url + '?ok'\n",encoding="utf-8")
            manifest=rank(old)
            data=(json.dumps(manifest,sort_keys=True)+"\n").encode()
            out=evaluate(data,sha(data),old,new)
            self.assertEqual(out["status"],"NO_DIFFERENCE")
            self.assertEqual(len(out["oracle"]["oracle_target_keys"]),1)
            key=out["oracle"]["oracle_target_keys"][0]
            self.assertIn("DownloadManager.download",key)
            self.assertFalse(out["model_called"])
            self.assertFalse(out["test_suite_executed"])

    def test_bad_manifest_fails_without_peeking_oracle(self):
        with tempfile.TemporaryDirectory() as d:
            root=fixture(d)
            with self.assertRaisesRegex(ValueError,"MANIFEST_DRIFT"):
                evaluate(b'{"status":"CHOICES_FROZEN"}',"0"*64,root,root)

    def test_source_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as b, tempfile.TemporaryDirectory() as f:
            old=fixture(b)
            new=fixture(f)
            manifest=rank(old)
            data=json.dumps(manifest).encode()
            (old/"httpie"/"a.py").write_text("def unrelated():\n    return 2\n")
            with self.assertRaisesRegex(ValueError,"BUGGY_SOURCE_DRIFT"):
                evaluate(data,sha(data),old,new)

    def test_missing_source_is_not_success(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            (root/"httpie").mkdir()
            self.assertEqual(rank(root)["status"],"NO_TEST_SOURCE")

    def test_tokenization_fixed(self):
        self.assertEqual(normalized_tokens("DownloadManager.download_job"),
                         {"downloadmanager","download","job"})


if __name__=="__main__":
    unittest.main()
