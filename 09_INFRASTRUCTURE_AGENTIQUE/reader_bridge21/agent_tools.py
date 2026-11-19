"""Minimal Omega agent tool registry: bounded, read-only public web research.

No arbitrary URLs or shell command tool. Import this from a controlling
agent, then explicitly dispatch a named operation. Web body is untrusted data.
"""
from __future__ import annotations
import json
from pathlib import Path

from web_access import (
    NetworkPolicyError, run_once, validate_query,
)

ALLOWED_TOOLS = ("search_bibliography", "read_omega_public_math_source")


def dispatch(tool_name: str, args: dict | None = None, *, transport=None) -> dict:
    """One bounded HTTP call, with allowlisted resource and explicit budget.

    A result may inform a candidate bibliography or a human review. It must
    never authorize semantic certification, code modifications or autonomous
    publication. The caller is responsible for retaining results and citations.
    """
    if not isinstance(args,dict):
        raise NetworkPolicyError("REQUIRES_ARGUMENT_OBJECT")
    if tool_name == "search_bibliography":
        if set(args) != {"query"} or not validate_query(args["query"]):
            raise NetworkPolicyError("BAD_BIBLIOGRAPHIC_TOOL_ARGUMENTS")
        result = run_once(transport=transport, query=args["query"], mode="search")
    elif tool_name == "read_omega_public_math_source":
        if args:
            raise NetworkPolicyError("PUBLIC_REPO_READ_TAKES_NO_ARGUMENTS")
        result = run_once(transport=transport, mode="source")
    else:
        raise NetworkPolicyError("UNKNOWN_AGENT_TOOL")
    if result["http_requests_max"] != 1 or result["automatic_scientific_promotions"] != 0:
        raise AssertionError("WEB_TOOL_SECURITY_BUDGET_INVARIANT")
    return {
        "tool": tool_name, "read_only": True,
        "web_content_trust": "UNTRUSTED",
        "max_network_calls": 1,
        "repo_write": False, "theorem_certificate": False,
        "result": result,
    }
