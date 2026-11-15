import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from provenance_cycle import propose
from provenance_lab import UNKNOWN
from provenance_transfer01 import COHORT_B, inspect, run


def frozen():
    baseline = {}
    training = [{
        "complete": True,
        "output": "result.json",
        "writers": [{"command": "cp original.json result.json", "exit_code": 0, "output": "result.json"}],
        "expected": "copie",
    }]
    return propose(training, baseline), baseline


class FrozenTransferTests(unittest.TestCase):
    def test_unique_bash_copy_in_both_arms(self):
        candidate, base = frozen()
        result = inspect("+ cp original.json result.json\n", "result.json", candidate, base)
        self.assertEqual((result["learned"], result["fixed"]), ("copie", "copie"))

    def test_unseen_buildkit_variant_classical_stronger(self):
        candidate, base = frozen()
        log = (
            "#7 0.1 + cp -av src/foo ./\n"
            "#7 0.2 'src/foo' -> 'foo'\n"
            "#7 DONE 0.3s\n"
        )
        result = inspect(log, "foo", candidate, base)
        self.assertEqual((result["learned"], result["fixed"]), (UNKNOWN, "copie"))

    def test_ninja_link_not_silently_reclassified(self):
        candidate, base = frozen()
        result = inspect("[2/2] : && cc -o src/curl ...\n", "src/curl", candidate, base)
        self.assertEqual((result["learned"], result["fixed"]), (UNKNOWN, UNKNOWN))
        self.assertEqual(result["parser"], "unsupported")

    def test_two_writers_force_abstention(self):
        candidate, base = frozen()
        result = inspect(
            "+ cp a result.json\n+ cp b result.json\n",
            "result.json", candidate, base,
        )
        self.assertEqual((result["learned"], result["fixed"]), (UNKNOWN, UNKNOWN))

    def test_two_incompatible_extractors_force_abstention(self):
        candidate, base = frozen()
        log = (
            "+ cp a result.json\n"
            "#7 0.1 + cp -av src/result.json ./\n"
            "#7 0.2 'src/result.json' -> 'result.json'\n"
            "#7 DONE 0.3s\n"
        )
        result = inspect(log, "result.json", candidate, base)
        self.assertEqual(result["parser"], "conflict")

    def test_frozen_job_ids_unique(self):
        ids = [v[1] for v in COHORT_B.values()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_rejects_corrupt_log_before_scoring(self):
        candidate, base = frozen()
        import json
        with TemporaryDirectory() as d:
            root = Path(d)
            (root / "C3.log").write_text("bad", encoding="utf-8")
            cpath = root / "candidate.json"
            bpath = root / "baseline.json"
            cpath.write_text(json.dumps(candidate), encoding="utf-8")
            bpath.write_text(json.dumps([]), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "differs from frozen"):
                run(root, cpath, bpath)


if __name__ == "__main__":
    unittest.main()
