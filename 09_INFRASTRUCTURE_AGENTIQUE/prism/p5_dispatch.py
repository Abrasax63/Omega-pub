"""Durable dispatch commitments using the existing Omega event ledger."""
from contextlib import contextmanager
import fcntl
import json
import os
from tempfile import NamedTemporaryFile
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
                identity_hash = ref["content_hash"]
                state = states.get(call_id)
                outputs = event["outputs"]
                if event["execution_status"] == "partial" and state is None and not outputs:
                    states[call_id] = (identity_hash, None, None)
                elif (event["execution_status"] == "partial" and outputs
                      and state == (identity_hash, None, None)):
                    states[call_id] = (identity_hash, None, outputs[0]["content_hash"])
                elif (event["execution_status"] == "completed" and state is not None
                      and state[:2] == (identity_hash, None)):
                    states[call_id] = (identity_hash, outputs[0]["content_hash"], state[2])
                else:
                    raise DispatchError("invalid attempt transition")
            yield states

    def _append(self, identity, row=None, *, payload_hash=None):
        digest = content_hash(row) if row is not None else payload_hash
        append_events(self.path, [build_event(
            mission_id=self.campaign, event_type="computation", role="p5_dispatch",
            execution_status="partial" if row is None else "completed",
            inputs=[_reference(identity[-1], "run", content_hash(identity))],
            outputs=[_reference(identity[-1], "run", digest)]
            if digest is not None else [],
        )], durable=True)

    def reserve(self, identity):
        if identity[0] != self.campaign:
            raise DispatchError("attempt belongs to a different campaign")
        with self._transaction() as states:
            pending = sorted(call_id for call_id, (_, result, _) in states.items() if result is None)
            if pending:
                raise DispatchError(f"unknown outcome for {pending}; automatic sending blocked")
            if identity[-1] in states:
                raise DispatchError("attempt already recorded; automatic resending blocked")
            self._append(identity)

    def finish(self, identity, row):
        with self._transaction() as states:
            if states.get(identity[-1]) != (content_hash(identity), None, None):
                raise DispatchError("terminal record requires a matching pending attempt")
            self._append(identity, row)

    def _payload_path(self, identity):
        return self.path.with_name(f"{self.path.name}.{content_hash(identity)}.json")

    def _read_payload(self, identity):
        try:
            with self._payload_path(identity).open(encoding="utf-8") as handle:
                wrapper = json.load(handle)
            payload = wrapper["payload"]
            if wrapper["sha256"] != content_hash(payload):
                raise DispatchError("stored payload hash mismatch")
            if payload["identity"] != list(identity) or payload["row"]["call_id"] != identity[-1]:
                raise DispatchError("stored payload identity mismatch")
            return payload
        except (ValueError, KeyError, TypeError) as exc:
            if isinstance(exc, DispatchError):
                raise
            raise DispatchError("invalid stored payload") from exc

    def finish_payload(self, identity, row, response):
        payload = {"identity": list(identity), "row": row, "response": response}
        target = self._payload_path(identity)
        with self._transaction() as states:
            if states.get(identity[-1]) != (content_hash(identity), None, None) or target.exists():
                raise DispatchError("payload requires a matching pending attempt with no payload")
            payload_hash = content_hash(payload)
            self._append(identity, payload_hash=payload_hash)
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent) as handle:
                # Write to an uncommitted temporary file, then publish it atomically.
                json.dump({"payload": payload, "sha256": payload_hash}, handle,
                          ensure_ascii=False, allow_nan=False)
                handle.flush()
                os.fsync(handle.fileno())
                os.link(handle.name, target)
                directory = os.open(target.parent, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(directory)
                finally:
                    os.close(directory)
            self._append(identity, row)

    def recover_payload(self, identity):
        with self._transaction() as states:
            state = states.get(identity[-1])
            if state is None:
                return None
            if state[0] != content_hash(identity):
                raise DispatchError("attempt identity changed")
            try:
                payload = self._read_payload(identity)
            except FileNotFoundError:
                if state[1] is not None:
                    raise DispatchError("committed payload is missing")
                raise DispatchError("unknown outcome; no durable payload") from None
            if state[2] != content_hash(payload):
                raise DispatchError("stored payload differs from its ledger commitment")
            row = payload["row"]
            if state[1] is None:
                self._append(identity, row)
            elif state[1] != content_hash(row):
                raise DispatchError("stored telemetry differs from its commitment")
            return payload

    def verify_results(self, records):
        with self._transaction() as states:
            pending = sorted(call_id for call_id, (_, result, _) in states.items() if result is None)
            if pending:
                raise DispatchError(f"unknown outcome for {pending}; analysis blocked")
            actual = {row["call_id"]: content_hash(row) for row in records}
            if len(actual) != len(records) or actual != {key: value[1] for key, value in states.items()}:
                raise DispatchError("telemetry differs from durable dispatch commitments")
