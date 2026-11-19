import copy
import json
import tempfile
import unittest
from pathlib import Path
from tools.repro_history_pilot import record_run, find_reusable
from tests.test_repro_fingerprint import sample


class HistoryPilotTests(unittest.TestCase):
    def test_pending_never_reused(self):
        with tempfile.TemporaryDirectory() as d:
            m = sample()
            record_run(d, m, {"answer": 7}, "reviewer-A")
            self.assertIsNone(find_reusable(d, m))

    def test_change_preserves_history_and_forces_new_record(self):
        with tempfile.TemporaryDirectory() as d:
            m = sample()
            first = record_run(d, m, {"answer": 7}, "reviewer-A")
            changed = copy.deepcopy(m)
            changed["dependencies"]["python"] = "3.13"
            second = record_run(d, changed, {"answer": 8}, "reviewer-B")
            self.assertNotEqual(first, second)
            self.assertEqual(len(list(Path(d).glob("*.json"))), 2)
            self.assertNotEqual(json.loads(first.read_text())["fingerprint"],
                                json.loads(second.read_text())["fingerprint"])
            self.assertEqual(json.loads(first.read_text())["manifest"], m)
            self.assertIsNone(find_reusable(d, changed))

    def test_reject_empty_validator(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                record_run(d, sample(), {}, "")


if __name__ == "__main__":
    unittest.main()
