"""Contract tests: replays cannot be counted as fresh scientific experiments."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from fast_cycle import (GENESIS, digest, pilot, validate_ledger, source_snapshot, TASKS)


class PilotTests(unittest.TestCase):
    def fixture(self, root):
        root = Path(root)
        omega = root / "omega"
        math = root / "math"
        prov = root / "provenance"
        (omega / "research/omega-100").mkdir(parents=True)
        (math / "research/code").mkdir(parents=True)
        (prov / "09_INFRASTRUCTURE_AGENTIQUE/prism").mkdir(parents=True)
        (omega / "research/omega-100/PROGRAMME.md").write_text("program")
        for n in (1, 2):
            (omega / f"research/omega-100/{n:03}.md").write_text(f"{n}")
        (math / "research/code/audit_v19_shadow_guard.py").write_text(
            'def compare(cases):\n'
            '    assert len(cases)==2\n'
            '    return {"projections":4,"new_errors":0,"locality_errors":0}\n')
        (prov / "09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_cycle.py").write_text("""
def propose(train, baseline):
    return {"test":1}
def evaluate_proposal(candidate, baseline, reserved):
    return {"baseline":{"correct_confirmations":0,"false_confirmations":0,"abstentions":4},
            "candidate":{"correct_confirmations":2,"false_confirmations":0,"abstentions":2},
            "recommend_for_review":True}
""")
        (prov / "09_INFRASTRUCTURE_AGENTIQUE/prism/provenance_lab.py").write_text("""
def score(reserved, baseline):
    return {"correct_confirmations":2,"false_confirmations":0,"abstentions":2}
""")
        return omega, math, prov

    def test_two_distinct_probes_and_no_replay(self):
        with TemporaryDirectory() as td:
            omega, math, prov = self.fixture(td)
            state = Path(td) / "state.json"
            out = Path(td) / "results"
            args = dict(omega_dir=omega, math_dir=math, provenance_dir=prov)
            first = pilot(state, out, bootstrap=True, max_cycles=1, **args)
            self.assertEqual((first["completed"], first["remaining"]), (1, 1))
            second = pilot(state, out, max_cycles=1, **args)
            self.assertEqual((second["completed"], second["remaining"]), (1, 0))
            events = json.loads(state.read_text())["entries"]
            self.assertEqual([e["experiment_id"] for e in events], list(TASKS))
            self.assertEqual(events[0]["previous_hash"], GENESIS)
            self.assertEqual(events[1]["previous_hash"], events[0]["event_hash"])
            self.assertEqual(pilot(state, out, **args)["completed"], 0)
            self.assertEqual(len(json.loads(state.read_text())["entries"]), 2)

    def test_missing_ledger_fails_closed(self):
        with TemporaryDirectory() as td:
            omega, math, prov = self.fixture(td)
            with self.assertRaises(FileNotFoundError):
                pilot(Path(td) / "missing.json", Path(td) / "results", omega_dir=omega,
                      math_dir=math, provenance_dir=prov)

    def test_tampering_is_detected(self):
        event = {"experiment_id": TASKS[0], "previous_hash": GENESIS, "status": "VERIFIED_FINITE"}
        event["event_hash"] = digest(event)
        state = {"schema": 1, "entries": [event]}
        validate_ledger(state)
        state["entries"][0]["status"] = "REFUTED_ON_PILOT"
        with self.assertRaises(ValueError):
            validate_ledger(state)

    def test_missing_omega_journal_number_fails_closed(self):
        with TemporaryDirectory() as td:
            omega, math, prov = self.fixture(td)
            (omega / "research/omega-100/002.md").unlink()
            (omega / "research/omega-100/003.md").write_text("3")
            with self.assertRaises(ValueError):
                source_snapshot(omega, math, prov)


if __name__ == "__main__":
    unittest.main()
