"""Stateless, read-only MCP Streamable HTTP adapter for Vercel.

The local stdio gateway remains the source of truth for tool behavior.
Configure OMEGA_GATEWAY_TOKEN before exposing this app publicly.
"""
from __future__ import annotations

import hmac
import json
import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

ROOT = Path(__file__).resolve().parent
GATEWAY_DIR = ROOT / "09_INFRASTRUCTURE_AGENTIQUE" / "gateway"
sys.path.insert(0, str(GATEWAY_DIR))
import server as gateway  # noqa: E402

SERVER_PROTOCOL = "2025-11-25"
SUPPORTED_PROTOCOLS = {SERVER_PROTOCOL, "2025-06-18", "2025-03-26"}
MAX_BODY_BYTES = 256 * 1024
REPO_ROOT = ROOT

app = FastAPI(
    title="Omega-pub read-only MCP gateway",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)


def _jsonrpc_error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {"code": code, "message": message},
    }


def _origin_is_allowed(origin: str | None) -> bool:
    if origin is None:
        return True
    configured = os.environ.get("OMEGA_ALLOWED_ORIGINS", "")
    allowed = {item.strip() for item in configured.split(",") if item.strip()}
    return origin in allowed


def _authorized(request: Request) -> bool:
    expected = os.environ.get("OMEGA_GATEWAY_TOKEN", "")
    supplied = request.headers.get("authorization", "")
    if not expected or not supplied.startswith("Bearer "):
        return False
    candidate = supplied[7:]
    return bool(candidate) and hmac.compare_digest(candidate, expected)


def _validate_tool_arguments(name: str, arguments: Any) -> None:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object")
    allowed = {
        "gateway_status": set(),
        "memory_search": {"question", "role", "max_documents"},
        "memory_get": {"id"},
    }
    if name not in allowed:
        raise ValueError(f"Unknown tool: {name}")
    unexpected = set(arguments) - allowed[name]
    if unexpected:
        raise ValueError("Unexpected tool argument(s): " + ", ".join(sorted(unexpected)))


def _dispatch(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    if method == "initialize":
        params = message.get("params") or {}
        if not isinstance(params, dict):
            return _jsonrpc_error(message.get("id"), -32602, "Invalid initialize params")
        requested = params.get("protocolVersion", SERVER_PROTOCOL)
        if requested not in SUPPORTED_PROTOCOLS:
            requested = SERVER_PROTOCOL
        normalized = dict(message)
        normalized["params"] = {**params, "protocolVersion": requested}
        return gateway.handle_message(REPO_ROOT, normalized)

    if method == "tools/call":
        params = message.get("params") or {}
        if not isinstance(params, dict):
            return _jsonrpc_error(message.get("id"), -32602, "Invalid tools/call params")
        name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            _validate_tool_arguments(name, arguments)
        except ValueError as exc:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                },
            }

    response = gateway.handle_message(REPO_ROOT, message)
    if response and method == "tools/list" and "result" in response:
        read_only_annotations = {
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        }
        for tool in response["result"].get("tools", []):
            tool["annotations"] = dict(read_only_annotations)

    # Report the deployed checkout and actual transport, not local STDIO details.
    if (
        response
        and method == "tools/call"
        and (message.get("params") or {}).get("name") == "gateway_status"
        and "result" in response
    ):
        try:
            content = response["result"]["content"][0]["text"]
            status = json.loads(content)
            status["transport"] = "streamable_http"
            status["mode"] = "read_only_deployed_checkout"
            status.pop("repository_root", None)
            status["repository_root_name"] = REPO_ROOT.name
            response["result"]["content"][0]["text"] = json.dumps(
                status, ensure_ascii=False, indent=2
            )
        except (KeyError, IndexError, TypeError, json.JSONDecodeError):
            pass
    return response


@app.post("/mcp")
async def mcp_endpoint(request: Request) -> Response:
    if not _origin_is_allowed(request.headers.get("origin")):
        return JSONResponse({"error": "Origin not allowed"}, status_code=403)

    if not _authorized(request):
        if not os.environ.get("OMEGA_GATEWAY_TOKEN"):
            return JSONResponse({"error": "Gateway authentication is not configured"}, status_code=503)
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        return JSONResponse({"error": "Content-Type must be application/json"}, status_code=415)

    accept = request.headers.get("accept", "")
    accepted_types = {part.split(";", 1)[0].strip().lower() for part in accept.split(",")}
    if not {"application/json", "text/event-stream"}.issubset(accepted_types):
        return JSONResponse(
            {"error": "Accept must include application/json and text/event-stream"},
            status_code=406,
        )

    try:
        raw = await request.body()
    except Exception:
        return JSONResponse({"error": "Unable to read request body"}, status_code=400)
    if len(raw) > MAX_BODY_BYTES:
        return JSONResponse({"error": "Request body too large"}, status_code=413)
    try:
        message = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse({"error": "Invalid JSON"}, status_code=400)

    if not isinstance(message, dict):
        return JSONResponse({"error": "Exactly one JSON-RPC object is required"}, status_code=400)
    if message.get("jsonrpc") != "2.0" or not isinstance(message.get("method"), str):
        return JSONResponse({"error": "Invalid JSON-RPC request"}, status_code=400)

    method = message["method"]
    if method != "initialize":
        protocol = request.headers.get("mcp-protocol-version")
        if protocol not in SUPPORTED_PROTOCOLS:
            return JSONResponse(
                {"error": "Missing or unsupported MCP-Protocol-Version"},
                status_code=400,
            )

    response = _dispatch(message)
    if response is None:
        return Response(status_code=202)

    return JSONResponse(
        response,
        status_code=200,
        headers={
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )
