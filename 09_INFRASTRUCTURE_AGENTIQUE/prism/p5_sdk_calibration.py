"""Exercise the official SDK against loopback only. No real API key is used."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Event, Thread
import unittest

from openai import APIStatusError, APITimeoutError, DefaultHttpxClient, OpenAI

from p5_calibration import EXPERIMENT, run_arm
from p5_dispatch import DispatchError, DispatchLedger
from p5_responses_client import responses_provider


class SDKCalibration(unittest.TestCase):
    def test_real_sdk_has_no_implicit_retries_and_respects_request_limits(self):
        calls = []
        release = Event()
        mode = "success"

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                request = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                calls.append((self.path, request))
                if mode == "timeout":
                    release.wait(5)
                    return
                if mode == "error":
                    code = 500
                    body = {"error": {"message": "synthetic fault", "type": "server_error"}}
                else:
                    code = 200
                    body = {
                        "id": "resp_synthetic", "object": "response", "created_at": 0,
                        "model": "synthetic-snapshot", "status": "completed",
                        "output": [], "usage": {"input_tokens": 48, "output_tokens": 20,
                                               "total_tokens": 68},
                    }
                payload = json.dumps(body).encode()
                self.send_response(code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):
                pass

        with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server, TemporaryDirectory() as folder:
            thread = Thread(target=server.serve_forever)
            thread.start()
            try:
                url = f"http://127.0.0.1:{server.server_address[1]}/v1"
                with OpenAI(base_url=url, api_key="synthetic-local-only", max_retries=2,
                            http_client=DefaultHttpxClient(trust_env=False, follow_redirects=False)) as client:
                    send = responses_provider(client, model="synthetic-snapshot", input_reserve=128)
                    prompt = {"question": "calibration publique", "perspectives": []}
                    ledger = DispatchLedger(Path(folder) / "success.jsonl", EXPERIMENT)
                    rows = []
                    run_arm("A", prompt, [], send, [], rows, ledger=ledger)
                    ledger.verify_results(rows)
                    self.assertEqual((rows[0]["input_tokens"], rows[0]["output_tokens"]), (48, 20))
                    path, request = calls[0]
                    self.assertEqual(path, "/v1/responses")
                    self.assertEqual(request["max_output_tokens"], 128)
                    self.assertEqual(request["tools"], [])
                    self.assertFalse(request["store"])
                    with self.assertRaisesRegex(ValueError, "insufficient budget"):
                        send("A", 1, prompt, max_tokens=128, timeout=2, max_tools=0)
                    self.assertEqual(len(calls), 1)

                    mode = "error"
                    failed = DispatchLedger(Path(folder) / "failed.jsonl", EXPERIMENT)
                    with self.assertRaises(APIStatusError) as failure:
                        run_arm("A", prompt, [], send, [], [], ledger=failed)
                    self.assertEqual(failure.exception.status_code, 500)
                    with self.assertRaisesRegex(DispatchError, "unknown outcome"):
                        run_arm("A", prompt, [], send, [], [], ledger=failed)
                    self.assertEqual(len(calls), 2)

                    mode = "timeout"
                    with self.assertRaises(APITimeoutError):
                        send("A", 1, prompt, max_tokens=256, timeout=0.2, max_tools=0)
                    self.assertEqual(len(calls), 3)
            finally:
                release.set()
                server.shutdown()
                thread.join()


if __name__ == "__main__":
    unittest.main(verbosity=2)
