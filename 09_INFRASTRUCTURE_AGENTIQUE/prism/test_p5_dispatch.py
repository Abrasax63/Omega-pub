from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from p5_dispatch import DispatchError, DispatchLedger


class DispatchLedgerTests(unittest.TestCase):
    def test_pending_survives_reopen_and_completed_commit_rejects_tampering(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "events.jsonl"
            identity = ("synthetic", "case", "A", 1, "generate", 1, "call-a")
            ledger = DispatchLedger(path, "synthetic")
            ledger.reserve(identity)
            reopened = DispatchLedger(path, "synthetic")
            with self.assertRaisesRegex(DispatchError, "unknown outcome"):
                reopened.reserve(identity)
            with self.assertRaisesRegex(DispatchError, "unknown outcome"):
                reopened.verify_results([])
            record = {"call_id": "call-a", "status": "completed"}
            reopened.finish(identity, record)
            ledger.verify_results([record])
            with self.assertRaisesRegex(DispatchError, "already recorded"):
                ledger.reserve(identity)
            with self.assertRaisesRegex(DispatchError, "differs"):
                ledger.verify_results([{**record, "status": "failed"}])
