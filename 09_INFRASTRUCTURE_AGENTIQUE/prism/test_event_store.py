import json
import tempfile
import unittest
from pathlib import Path

from event_store import (
    EventLedgerError, append_events, build_event, lifecycle_events,
    read_ledger, verify_events, GENESIS,
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
            "mission": {"question": "audit de test"},
            "source_engine": "existing_read_only_rce_gateway",
            "mode": "read_only_local_checkout",
            "packages": [{"role": task["role"]} for task in self.plan["tasks"]],
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

    def test_lifecycle_events_are_metadata_only_and_hash_chained(self):
        events = lifecycle_events(self.plan, self.bundle, self.run)
        self.assertEqual(events[0]["event_type"], "mission_planned")
        self.assertEqual(events[1]["event_type"], "context_prepared")
        self.assertEqual(events[-1]["event_type"], "execution_closed")
        self.assertTrue(all("question" not in event["payload"] for event in events))
        self.assertTrue(all("output" not in event["payload"] for event in events))
        self.assertEqual(verify_events(events)["event_count"], len(events))
        self.assertNotIn("Texte de sortie", json.dumps(events))

    def test_append_and_verify_across_multiple_batches(self):
        events = lifecycle_events(self.plan, self.bundle, self.run)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            first = events[:2]
            append_events(path, first)
            previous = verify_events(first)["last_hash"]
            rest = events[2:]
            # Rechain second batch to the first persisted event.
            rest[0]["previous_hash"] = previous
            from event_store import _event_hash
            rest[0]["event_hash"] = _event_hash(rest[0])
            for i in range(1, len(rest)):
                rest[i]["previous_hash"] = rest[i-1]["event_hash"]
                rest[i]["event_hash"] = _event_hash(rest[i])
            append_events(path, rest)
            loaded = read_ledger(path)
            self.assertTrue(loaded["valid"])
            self.assertEqual(loaded["event_count"], len(events))

    def test_tampering_is_detected(self):
        events = lifecycle_events(self.plan, self.bundle, self.run)
        events[0]["payload"]["plan_hash"] = "f" * 64
        with self.assertRaises(EventLedgerError):
            verify_events(events)

    def test_rejects_raw_content_and_secret_fields(self):
        with self.assertRaises(EventLedgerError):
            build_event("perspective_recorded", {"output": "private text"})
        with self.assertRaises(EventLedgerError):
            build_event("mission_planned", {"api_key": "never"})

    def test_rejects_mission_mismatch(self):
        bundle = dict(self.bundle)
        bundle["mission"] = {"question": "different"}
        with self.assertRaises(EventLedgerError):
            lifecycle_events(self.plan, bundle, self.run)

    def test_refuses_empty_append_and_broken_previous_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            with self.assertRaises(EventLedgerError):
                append_events(path, [])
            bad = build_event("mission_planned", {"plan_hash": "a" * 64}, previous_hash="1" * 64)
            with self.assertRaises(EventLedgerError):
                append_events(path, [bad])


if __name__ == "__main__":
    unittest.main()
