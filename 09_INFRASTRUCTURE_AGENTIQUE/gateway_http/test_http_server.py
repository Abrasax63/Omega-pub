import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import httpx

import app as http_gateway


class HttpGatewayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        gov = self.root / "00_GOUVERNANCE"
        gov.mkdir()
        (gov / "INDEX_GLOBAL.md").write_text(
            "| ID | Domaine | Énoncé / titre | Version | Statut scientifique source | Statut de publication | Fiche |\n"
            "|---|---|---|---|---|---|---|\n"
            "| BR-01 | Mathématiques | Noyau et période | 0.1 | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL | [Fiche](../fiche.md) |\n",
            encoding="utf-8",
        )
        (gov / "REGISTRE_TRANSVERSAL.md").write_text("", encoding="utf-8")
        (self.root / "fiche.md").write_text("# BR-01\nPreuve à auditer.\n", encoding="utf-8")
        self.old_root = http_gateway.REPO_ROOT
        http_gateway.REPO_ROOT = self.root
        self.env = patch.dict(os.environ, {"OMEGA_GATEWAY_TOKEN": "test-secret"}, clear=False)
        self.env.start()
        self.headers = {
            "Authorization": "Bearer test-secret",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

    def tearDown(self):
        self.env.stop()
        http_gateway.REPO_ROOT = self.old_root
        self.temp.cleanup()

    async def _request(self, method, path, headers=None, json_body=None):
        transport = httpx.ASGITransport(app=http_gateway.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.request(method, path, headers=headers, json=json_body)

    def request(self, method, path, headers=None, json_body=None):
        return asyncio.run(self._request(method, path, headers, json_body))

    def post_rpc(self, message, extra_headers=None):
        headers = dict(self.headers)
        if extra_headers:
            headers.update(extra_headers)
        return self.request("POST", "/mcp", headers=headers, json_body=message)

    def test_initialize_negotiates_supported_protocol(self):
        response = self.post_rpc({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}},
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["result"]["protocolVersion"], "2025-11-25")

    def test_tools_list_exposes_only_read_only_tools(self):
        response = self.post_rpc(
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"MCP-Protocol-Version": "2025-11-25"},
        )
        self.assertEqual(response.status_code, 200)
        tools = response.json()["result"]["tools"]
        names = [tool["name"] for tool in tools]
        self.assertEqual(names, ["gateway_status", "memory_search", "memory_get"])
        self.assertFalse(any("write" in name or "delete" in name for name in names))
        self.assertTrue(all(tool["annotations"]["readOnlyHint"] for tool in tools))
        self.assertTrue(all(not tool["annotations"]["destructiveHint"] for tool in tools))

    def test_memory_get_returns_source_without_certifying(self):
        response = self.post_rpc(
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "memory_get", "arguments": {"id": "BR-01"}}},
            {"MCP-Protocol-Version": "2025-11-25"},
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.json()["result"]["content"][0]["text"])
        self.assertTrue(result["found"])
        self.assertEqual(result["scientific_validation"], "not_performed")
        self.assertIn("Preuve à auditer", result["source"]["content"])

    def test_gateway_status_reports_deployed_http_transport_without_local_path(self):
        response = self.post_rpc(
            {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
             "params": {"name": "gateway_status", "arguments": {}}},
            {"MCP-Protocol-Version": "2025-11-25"},
        )
        result = json.loads(response.json()["result"]["content"][0]["text"])
        self.assertEqual(result["transport"], "streamable_http")
        self.assertEqual(result["mode"], "read_only_deployed_checkout")
        self.assertNotIn("repository_root", result)
        self.assertFalse(result["writes_enabled"])

    def test_notifications_return_202_without_body(self):
        response = self.post_rpc(
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"MCP-Protocol-Version": "2025-11-25"},
        )
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response.content, b"")

    def test_authentication_is_required(self):
        response = self.request(
            "POST", "/mcp",
            headers={"Content-Type": "application/json", "Accept": "application/json, text/event-stream"},
            json_body={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        )
        self.assertEqual(response.status_code, 401)

    def test_missing_server_token_fails_closed(self):
        with patch.dict(os.environ, {}, clear=True):
            response = self.request(
                "POST", "/mcp", headers=self.headers,
                json_body={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
            )
        self.assertEqual(response.status_code, 503)

    def test_origin_is_rejected_unless_allowlisted(self):
        message = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
        response = self.post_rpc(message, {"Origin": "https://evil.example"})
        self.assertEqual(response.status_code, 403)
        with patch.dict(os.environ, {"OMEGA_ALLOWED_ORIGINS": "https://client.example"}):
            allowed = self.post_rpc(message, {"Origin": "https://client.example"})
        self.assertEqual(allowed.status_code, 200)

    def test_protocol_header_is_required_after_initialize(self):
        response = self.post_rpc({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(response.status_code, 400)

    def test_unexpected_tool_arguments_are_rejected(self):
        response = self.post_rpc(
            {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
             "params": {"name": "memory_get", "arguments": {"id": "BR-01", "write": True}}},
            {"MCP-Protocol-Version": "2025-11-25"},
        )
        self.assertTrue(response.json()["result"]["isError"])

    def test_get_is_not_supported(self):
        response = self.request("GET", "/mcp", headers={"Accept": "text/event-stream"})
        self.assertEqual(response.status_code, 405)


if __name__ == "__main__":
    unittest.main()
