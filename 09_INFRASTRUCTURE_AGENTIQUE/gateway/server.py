#!/usr/bin/env python3
"""Read-only MCP stdio gateway for an Omega-pub checkout.

Python 3.10+, standard library only. Exposes repository-backed tools and never
writes to the checkout. Run: python server.py --repo /path/to/Omega-pub
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
PROTOTYPE = HERE.parent / "prototype"
sys.path.insert(0, str(PROTOTYPE))
import rce  # noqa: E402

SERVER_NAME = "omega-pub-research-gateway"
SERVER_VERSION = "0.1.0"
PROTOCOL_VERSION = "2024-11-05"
MAX_SOURCE_CHARS = 20000

TOOLS = [
    {
        "name": "gateway_status",
        "description": "Return the local checkout identity, index availability and read-only capabilities. No files are changed.",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "memory_search",
        "description": "Search Omega-pub governance indexes and local repository documents. Results are lexical candidates, not scientific validation.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "question": {"type": "string", "minLength": 2},
                "role": {"type": "string", "enum": sorted(rce.ROLE_GUIDANCE), "default": "researcher"},
                "max_documents": {"type": "integer", "minimum": 1, "maximum": 30, "default": 12},
            },
            "required": ["question"],
            "additionalProperties": False,
        },
    },
    {
        "name": "memory_get",
        "description": "Retrieve one exact ID from the governance indexes and, when a safe local fiche link exists, a bounded excerpt of that fiche.",
        "inputSchema": {
            "type": "object",
            "properties": {"id": {"type": "string", "minLength": 2, "maxLength": 81}},
            "required": ["id"],
            "additionalProperties": False,
        },
    },
]


class GatewayError(Exception):
    pass


def _json_text(value: Any) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}


def _safe_source(root: Path, relative: str) -> Path | None:
    candidate = (root / relative).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file() or candidate.suffix.lower() not in rce.ALLOWED_SUFFIXES:
        return None
    if any(part.casefold() in rce.SKIP_PARTS or part in rce.SKIP_DIRS
           for part in candidate.relative_to(root.resolve()).parts):
        return None
    if candidate.stat().st_size > 1_000_000:
        return None
    return candidate


def gateway_status(root: Path) -> dict[str, Any]:
    return {
        "server": SERVER_NAME,
        "version": SERVER_VERSION,
        "repository_root": root.name,
        "repository_path": str(root),
        "indexes": {
            "global_index_present": (root / rce.INDEX_PATH).is_file(),
            "transversal_register_present": (root / rce.REGISTER_PATH).is_file(),
        },
        "transport": "stdio",
        "mode": "read_only_local_checkout",
        "tools": [tool["name"] for tool in TOOLS],
        "writes_enabled": False,
        "network_access": False,
        "limitations": [
            "Only files present in this local checkout are accessible.",
            "Search is lexical; no semantic or external literature search is performed.",
            "No model orchestration, computation runner, event history or certification service is exposed.",
            "Search matches are documentary candidates, not proof of scientific validity.",
        ],
    }


def memory_search(root: Path, args: dict[str, Any]) -> dict[str, Any]:
    question = args.get("question")
    role = args.get("role", "researcher")
    max_documents = args.get("max_documents", 12)
    if not isinstance(question, str) or len(question.strip()) < 2:
        raise GatewayError("'question' must be a string of at least 2 characters")
    if role not in rce.ROLE_GUIDANCE:
        raise GatewayError("Unknown role")
    if isinstance(max_documents, bool) or not isinstance(max_documents, int) or not 1 <= max_documents <= 30:
        raise GatewayError("'max_documents' must be an integer between 1 and 30")
    return rce.build_context(root, question, role, max_documents)


def memory_get(root: Path, args: dict[str, Any]) -> dict[str, Any]:
    identifier = args.get("id")
    if not isinstance(identifier, str) or not (2 <= len(identifier) <= 81):
        raise GatewayError("'id' must be a string between 2 and 81 characters")
    records = rce.load_registered_results(root)
    matches = [item for item in records if item["id"] == identifier]
    if not matches:
        pending = [item for item in rce.load_pending_items(root) if item["id"] == identifier]
        if pending:
            return {"found": True, "record_type": "pending_migration", "record": pending[0],
                    "warning": "Dossier en attente : statut scientifique non établi, non assimilé à une fiche certifiée."}
        return {"found": False, "id": identifier}
    record = matches[0]
    result: dict[str, Any] = {
        "found": True,
        "record_type": "registered_index_entry",
        "record": record,
        "scientific_validation": "not_performed",
        "warning": "L'entrée d'index ne constitue pas à elle seule une vérification indépendante de la preuve.",
    }
    relative = record.get("source_file")
    if relative:
        source = _safe_source(root, relative)
        if source:
            content = source.read_text(encoding="utf-8", errors="replace")
            raw = content.encode("utf-8")
            result["source"] = {
                "path": relative,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "truncated": len(content) > MAX_SOURCE_CHARS,
                "content": content[:MAX_SOURCE_CHARS],
            }
    return result


def call_tool(root: Path, name: str, args: dict[str, Any]) -> dict[str, Any]:
    if name == "gateway_status":
        return gateway_status(root)
    if name == "memory_search":
        return memory_search(root, args)
    if name == "memory_get":
        return memory_get(root, args)
    raise GatewayError(f"Unknown tool: {name}")


def handle_message(root: Path, message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    request_id = message.get("id")
    if method == "notifications/initialized" or method == "notifications/cancelled":
        return None
    if method == "ping":
        return {"jsonrpc": "2.0", "id": request_id, "result": {}}
    if method == "initialize":
        params = message.get("params") or {}
        requested = params.get("protocolVersion", PROTOCOL_VERSION)
        return {
            "jsonrpc": "2.0", "id": request_id,
            "result": {
                "protocolVersion": requested,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
                "instructions": "Read-only access to the configured local Omega-pub checkout. No tool certifies results or writes repository files.",
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": request_id, "result": {"tools": TOOLS}}
    if method == "tools/call":
        params = message.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            if not isinstance(args, dict):
                raise GatewayError("Tool arguments must be a JSON object")
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": _json_text(call_tool(root, name, args))}
        except (GatewayError, OSError, ValueError) as exc:
            return {"jsonrpc": "2.0", "id": request_id,
                    "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True}}
    if request_id is None:
        return None
    return {"jsonrpc": "2.0", "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Local Omega-pub checkout")
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    if not root.is_dir():
        parser.error(f"Repository path is not a directory: {root}")
    if not (root / rce.INDEX_PATH).is_file() and not (root / rce.REGISTER_PATH).is_file():
        parser.error("No Omega-pub governance index found at the supplied repository path")
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("JSON-RPC message must be an object")
            response = handle_message(root, message)
        except (json.JSONDecodeError, ValueError) as exc:
            response = {"jsonrpc": "2.0", "id": None,
                        "error": {"code": -32700, "message": str(exc)}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
