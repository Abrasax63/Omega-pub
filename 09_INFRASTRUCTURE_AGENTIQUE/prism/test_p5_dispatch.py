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

    def test_rehashed_response_cannot_override_ledger_commitment(self):
        import json
        from event_store import content_hash

        with TemporaryDirectory() as folder:
            ledger = DispatchLedger(Path(folder) / "events.jsonl", "synthetic")
            identity = ("synthetic", "case", "A", 1, "generate", 1, "call-a")
            ledger.reserve(identity)
            ledger.finish_payload(identity, {"call_id": "call-a"}, {"output_text": "original"})
            path = ledger._payload_path(identity)
            wrapper = json.loads(path.read_text(encoding="utf-8"))
            wrapper["payload"]["response"]["output_text"] = "modified"
            wrapper["sha256"] = content_hash(wrapper["payload"])
            path.write_text(json.dumps(wrapper), encoding="utf-8")
            with self.assertRaisesRegex(DispatchError, "ledger commitment"):
                ledger.recover_payload(identity)
