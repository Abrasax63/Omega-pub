import json
import tempfile
import unittest
from pathlib import Path

import server


class GatewayTests(unittest.TestCase):
    def make_repo(self, root: Path):
        gov = root / "00_GOUVERNANCE"
        gov.mkdir()
        (gov / "INDEX_GLOBAL.md").write_text(
            "| ID | Domaine | Énoncé / titre | Version | Statut scientifique source | Statut de publication | Fiche |\n"
            "|---|---|---|---|---|---|---|\n"
            "| BR-01 | Mathématiques | Noyau et période | 0.1 | DÉMONTRÉ (fiche interne) | EXPÉRIMENTAL | [Fiche](../fiche.md) |\n",
            encoding="utf-8")
        (gov / "REGISTRE_TRANSVERSAL.md").write_text("", encoding="utf-8")
        (root / "fiche.md").write_text("# BR-01\nPreuve à auditer.\n", encoding="utf-8")

    def test_status_is_explicitly_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            status = server.gateway_status(root)
            self.assertFalse(status["writes_enabled"])
            self.assertEqual(status["mode"], "read_only_local_checkout")
            self.assertIn("memory_search", status["tools"])

    def test_memory_get_returns_index_and_source_without_certifying(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            result = server.memory_get(root, {"id": "BR-01"})
            self.assertTrue(result["found"])
            self.assertEqual(result["record"]["publication_status"], "EXPÉRIMENTAL")
            self.assertEqual(result["scientific_validation"], "not_performed")
            self.assertIn("Preuve à auditer", result["source"]["content"])

    def test_memory_search_uses_existing_rce(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            result = server.memory_search(root, {"question": "noyau période", "role": "refuter"})
            self.assertEqual(result["manifest"]["mode"], "read_only_local_checkout")
            self.assertEqual(result["mission"]["role"], "refuter")

    def test_pending_item_is_not_treated_as_registered(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            (root / "00_GOUVERNANCE/REGISTRE_TRANSVERSAL.md").write_text(
                "| Identifiants / dossier | Domaine | État documentaire | Condition avant inscription comme fiche |\n"
                "|---|---|---|---|\n"
                "| CL-DYN-01 à CL-DYN-04 | Mathématiques | Sources à retrouver | Auditer les preuves |\n",
                encoding="utf-8")
            result = server.memory_get(root, {"id": "CL-DYN-01 à CL-DYN-04"})
            self.assertEqual(result["record_type"], "pending_migration")
            self.assertIn("NON ÉTABLI", result["record"]["scientific_status_source"])

    def test_mcp_initialize_and_tools_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            init = server.handle_message(root, {
                "jsonrpc": "2.0", "id": 1, "method": "initialize",
                "params": {"protocolVersion": server.PROTOCOL_VERSION}
            })
            self.assertEqual(init["result"]["serverInfo"]["name"], server.SERVER_NAME)
            listed = server.handle_message(root, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
            names = [tool["name"] for tool in listed["result"]["tools"]]
            self.assertEqual(names, ["gateway_status", "memory_search", "memory_get"])

    def test_unknown_tool_is_reported_as_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_repo(root)
            response = server.handle_message(root, {
                "jsonrpc": "2.0", "id": 3, "method": "tools/call",
                "params": {"name": "write_memory", "arguments": {}}
            })
            self.assertTrue(response["result"]["isError"])


if __name__ == "__main__":
    unittest.main()
