"""Durable dispatch commitments using the existing Omega event ledger."""
from contextlib import contextmanager
import fcntl
from pathlib import Path

from event_store import _reference, append_events, build_event, content_hash, read_ledger


class DispatchError(ValueError):
    """The state of a dispatch prevents sending or analysis."""


class DispatchLedger:
    """One campaign per ledger, with an exclusive lock for each transaction."""

    def __init__(self, path, campaign):
        self.path = Path(path)
        self.campaign = campaign

    @contextmanager
    def _transaction(self):
        # Keep the lock inode stable across appends and process restarts.
        with self.path.with_suffix(self.path.suffix + ".lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            states = {}
            events = read_ledger(self.path)["events"] if self.path.exists() else []
            for event in events:
                if event["mission_id"] != self.campaign or event["actor"]["role"] != "p5_dispatch":
                    raise DispatchError("ledger belongs to a different campaign or workflow")
                ref = event["inputs"][0]
                call_id = ref["ref_id"]
                if event["execution_status"] == "partial" and call_id not in states:
                    states[call_id] = (ref["content_hash"], None)
                elif event["execution_status"] == "completed" and states.get(call_id) == (
                    ref["content_hash"], None
                ):
                    states[call_id] = (ref["content_hash"], event["outputs"][0]["content_hash"])
                else:
                    raise DispatchError("invalid attempt transition")
            yield states

    def _append(self, identity, row=None):
        append_events(self.path, [build_event(
            mission_id=self.campaign, event_type="computation", role="p5_dispatch",
            execution_status="partial" if row is None else "completed",
            inputs=[_reference(identity[-1], "run", content_hash(identity))],
            outputs=[] if row is None else [_reference(identity[-1], "run", content_hash(row))],
        )], durable=True)

    def reserve(self, identity):
        if identity[0] != self.campaign:
            raise DispatchError("attempt belongs to a different campaign")
        with self._transaction() as states:
            pending = sorted(call_id for call_id, (_, result) in states.items() if result is None)
            if pending:
                raise DispatchError(f"unknown outcome for {pending}; automatic sending blocked")
            if identity[-1] in states:
                raise DispatchError("attempt already recorded; automatic resending blocked")
            self._append(identity)

    def finish(self, identity, row):
        with self._transaction() as states:
            if states.get(identity[-1]) != (content_hash(identity), None):
                raise DispatchError("terminal record requires a matching pending attempt")
            self._append(identity, row)

    def verify_results(self, records):
        with self._transaction() as states:
            pending = sorted(call_id for call_id, (_, result) in states.items() if result is None)
            if pending:
                raise DispatchError(f"unknown outcome for {pending}; analysis blocked")
            actual = {row["call_id"]: content_hash(row) for row in records}
            if len(actual) != len(records) or actual != {key: value[1] for key, value in states.items()}:
                raise DispatchError("telemetry differs from durable dispatch commitments")
