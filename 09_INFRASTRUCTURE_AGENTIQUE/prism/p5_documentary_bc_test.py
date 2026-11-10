"""Exercise the real SDK with a mocked HTTP transport, without contacting OpenAI."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

import httpx2
from openai import OpenAI

from p5_documentary_bc import inputs_by_arm, run


class DocumentaryBCTest(unittest.TestCase):
    def exercise(self, parent, *, input_count=100, returned_count=100):
        requests = []

        def reply(request):
            path, body = request.url.path, json.loads(request.content)
            requests.append((path, body))
            if path.endswith("/input_tokens"):
                return httpx2.Response(200, json={"object": "response.input_tokens",
                                                  "input_tokens": input_count})
            answer = f"Texte synthétique {len(requests)}."
            return httpx2.Response(200, json={
                "id": f"resp_{len(requests)}", "object": "response", "created_at": 0,
                "model": "synthetic-v1", "status": "completed",
                "usage": {"input_tokens": returned_count, "output_tokens": 10,
                          "total_tokens": returned_count + 10},
                "output": [{"id": "msg_test", "type": "message", "role": "assistant",
                            "status": "completed",
                            "content": [{"type": "output_text", "text": answer, "annotations": []}]}],
            })

        with OpenAI(api_key="fake", base_url="https://simulation.invalid/v1",
                    http_client=httpx2.Client(transport=httpx2.MockTransport(reply))) as client:
            if input_count > 256 or input_count != returned_count:
                with self.assertRaises(ValueError):
                    run(parent, client, model="synthetic-v1", token_cap=384,
                        output_cap=128, simulated=True)
            else:
                run(parent, client, model="synthetic-v1", token_cap=384,
                    output_cap=128, simulated=True)
        return requests

    def test_packet_excludes_key_and_requests_are_stateless(self):
        with TemporaryDirectory() as directory:
            parent = Path(directory) / "run"
            requests = self.exercise(parent)
            self.assertEqual([path for path, _ in requests],
                             ["/v1/responses/input_tokens"] * 2 + ["/v1/responses"] * 2)
            for (_, count), (_, generation) in zip(requests[:2], requests[2:]):
                self.assertEqual(generation, {**count, "store": False, "max_output_tokens": 128})
                self.assertNotIn("conversation", generation)
                self.assertNotIn("previous_response_id", generation)
            packet = json.loads((parent / "grading.json").read_text())
            key = json.loads((parent / "key-private.json").read_text())
            self.assertEqual(set(packet), {"case", "mode", "responses"})
            self.assertEqual(packet["mode"], "simulation")
            self.assertEqual(set(packet["responses"]), {"X", "Y"})
            order = json.loads((parent / "run-private.json").read_text())["run_order"]
            for label, arm in key.items():
                self.assertEqual(packet["responses"][label], f"Texte synthétique {3 + order.index(arm)}.")

    def test_deliverables_are_shared_and_leave_roles_unchanged(self):
        baseline = inputs_by_arm()
        explicit = inputs_by_arm(explicit_deliverables=True)
        common = []
        for arm in ("B", "C"):
            base, roles = baseline[arm].split("\n\nPerspectives :", 1)
            changed, changed_roles = explicit[arm].split("\n\nPerspectives :", 1)
            self.assertEqual(roles, changed_roles)
            self.assertTrue(changed.startswith(base + "\n\nLivrables :"))
            common.append(changed)
        self.assertEqual(*common)

    def test_over_budget_blocks_generation(self):
        with TemporaryDirectory() as directory:
            parent = Path(directory) / "run"
            self.assertEqual(len(self.exercise(parent, input_count=257)), 1)
            self.assertFalse((parent / "grading.json").exists())

    def test_provider_count_mismatch_blocks_grading(self):
        with TemporaryDirectory() as directory:
            parent = Path(directory) / "run"
            self.assertEqual(len(self.exercise(parent, returned_count=101)), 3)
            self.assertFalse((parent / "grading.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
