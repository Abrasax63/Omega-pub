"""Loopback-only P5 fault injection. Run on a checkout with PRs #20 and #21."""
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Event, Thread
from unittest.mock import patch
from urllib.request import Request, urlopen

from p5_calibration import (
    EXPERIMENT, checked_analysis, exercise, run_arm, simulated_provider,
)
from p5_dispatch import DispatchError, DispatchLedger


def http_provider(port, arm, attempt, prompt, *, max_tokens, timeout, max_tools):
    payload = dict(arm=arm, attempt=attempt, prompt=prompt, max_tokens=max_tokens,
                   timeout=timeout, max_tools=max_tools)
    request = Request(f"http://127.0.0.1:{port}/simulate", json.dumps(payload).encode(),
                      {"Content-Type": "application/json"})
    with urlopen(request, timeout=timeout) as response:
        return json.load(response)


def worker(port, path, action):
    ledger = DispatchLedger(path, EXPERIMENT)

    def send(*args, **kwargs):
        response = http_provider(port, *args, **kwargs)
        if action == "crash":
            os._exit(77)
        return response

    try:
        run_arm("C", {"question": "P5 crash fixture", "perspectives": []}, [],
                send, [], [], ledger=ledger)
    except DispatchError as exc:
        if action != "resume" or "unknown outcome" not in str(exc):
            raise
        return 78
    return 0


def main():
    calls = []
    hold = Event()
    release = Event()

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self):
            args = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            calls.append((args["arm"], args["attempt"], args["max_tokens"], args["timeout"]))
            if hold.is_set():
                release.wait(5)
                return
            body = json.dumps(simulated_provider(**args)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            pass

    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server, TemporaryDirectory() as folder:
        thread = Thread(target=server.serve_forever)
        thread.start()
        try:
            port = server.server_address[1]
            report = exercise(partial(http_provider, port))
            c_calls = [call for call in calls[:4] if call[0] == "C"]
            assert c_calls == [("C", 1, 256, 2.0), ("C", 2, 188, 1.75)], c_calls
            path = Path(folder) / "crash.jsonl"
            command = [sys.executable, __file__, str(port), str(path)]
            before = len(calls)
            crash_exit = subprocess.run(command + ["crash"], timeout=10).returncode
            assert crash_exit == 77
            assert calls[before:] == [("C", 1, 256, 2.0)]
            resume_exit = subprocess.run(command + ["resume"], timeout=10).returncode
            assert resume_exit == 78
            assert len(calls) == before + 1
            ledger = DispatchLedger(path, EXPERIMENT)
            with patch("analysis.load_blind_key") as load_key:
                try:
                    checked_analysis([], [], None, None, None, None, ledger=ledger)
                except DispatchError as exc:
                    assert "unknown outcome" in str(exc)
                else:
                    raise AssertionError("uncertain attempt was accepted")
                load_key.assert_not_called()

            hold.set()
            try:
                http_provider(port, "A", 1, {"perspectives": []},
                              max_tokens=256, timeout=0.2, max_tools=0)
            except TimeoutError:
                pass
            else:
                raise AssertionError("client accepted a response beyond its timeout")
            assert calls[-1] == ("A", 1, 256, 0.2)
            print(json.dumps({"checks": report["checks"], "crash_exit": crash_exit, "resume_exit": resume_exit,
                              "server_saw_one_crash_request": True, "timeout_enforced": True},
                             sort_keys=True))
        finally:
            release.set()
            server.shutdown()
            thread.join()


if __name__ == "__main__":
    if len(sys.argv) == 4:
        raise SystemExit(worker(int(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]))
    main()
