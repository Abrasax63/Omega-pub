import json
import tempfile
import unittest
from pathlib import Path

from event_store import (
    EventLedgerError, append_events, lifecycle_events, read_ledger,
    verify_events, GENESIS, _event_hash,
)
from planner import plan_mission
from execution import start_execution, record_perspective, close_execution


class EventLedgerTests(unittest.TestCase):
    def setUp(self):
        self.plan = plan_mission({
            "question": "audit de test",
            "mission_type": "mathematical",
            "mission_id": "P4-TEST-01",
        })
        self.bundle = {
            "context_preparer": "omega-adaptive-prism-rce",
            "context_preparer_version": "0.1.0",
            "mission": {"question": "audit de test"},
            "source_engine": "existing_read_only_rce_gateway",
            "mode": "read_only_local_checkout",
            "limitations": ["Recherche locale uniquement."],
            "packages": [{"role": task["role"], "exact_retrievals": []} for task in self.plan["tasks"]],
            "manifest": {"content_hash": "a" * 64},
        }
        self.run = start_execution(self.plan, self.bundle)
        record_perspective(
            self.run, "refuter", status="completed",
            output="Texte de sortie qui ne doit pas être stocké en clair.",
            evidence_refs=["test:counterexample-1"],
            limitations=["Perspective du même agent principal"],
        )
        close_execution(self.run)

    def _rechain(self, events, previous):
        for event in events:
            event["previous_hash"] = previous
            event["event_hash"] = _event_hash(event)
            previous = event["event_hash"]
        return events

    def test_events_follow_existing_schema_and_are_metadata_only(self):
        events = lifecycle_events(self.plan, self.bundle, self.run)
        self.assertEqual(events[0]["event_type"], "reasoning")
        self.assertEqual(events[1]["event_type"], "context_retrieval")
        self.assertEqual(events[-1]["event_type"], "review")
        self.assertTrue(all(event["epistemic_space"] == "experimental_internal" for event in events))
        self.assertTrue(all("question" not in event for event in events))
        self.assertNotIn("Texte de sortie", json.dumps(events))
        self.assertEqual(verify_events(events)["event_count"], len(events))

    def test_append_and_verify_multiple_batches(self):
        events = lifecycle_events(self.plan, self.bundle, self.run)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            append_events(path, events[:2])
            # A second independently built batch is automatically linked to
            # the persisted tail; no caller-side hash manipulation is needed.
            second = lifecycle_events(self.plan, self.bundle, self.run)[2:]
            second = self._rechain(second, GENESIS)
            append_events(path, second)
            loaded = read_ledger(path)
            self.assertTrue(loaded["valid"])
            self.assertEqual(loaded["event_count"], len(events))

    def test_tampering_is_detected(self):
        events = lifecycle_events(self.plan, self.bundle, self.run)
        events[0]["mission_id"] = "tampered"
        with self.assertRaises(EventLedgerError):
            verify_events(events)

    def test_rejects_mismatched_mission(self):
        bundle = dict(self.bundle)
        bundle["mission"] = {"question": "different"}
        with self.assertRaises(EventLedgerError):
            lifecycle_events(self.plan, bundle, self.run)

    def test_refuses_empty_append_and_broken_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            with self.assertRaises(EventLedgerError):
                append_events(path, [])
            broken = lifecycle_events(self.plan, self.bundle, self.run)
            broken[0]["previous_hash"] = "1" * 64
            broken[0]["event_hash"] = _event_hash(broken[0])
            with self.assertRaises(EventLedgerError):
                append_events(path, broken)


if __name__ == "__main__":
    unittest.main()
