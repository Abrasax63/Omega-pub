"""Deterministic USD estimate for the P5 v0.5 private Responses runner.

All input tokens are conservatively priced at NON-CACHED standard rates,
even if the provider later discounts some. This is an estimate, NOT an
OpenAI invoice, a credit balance, nor a guaranteed platform spending limit.
Operator freezes and verifies the model-specific pricing file externally.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json

SOURCE_URL = "https://platform.openai.com/pricing"
EXPECTED_FIELDS = {
    "model", "currency", "processing_mode",
    "input_usd_per_million", "output_usd_per_million",
    "source_url", "checked_at_utc",
}

class CostConfigurationError(ValueError):
    """Refuse unsupported/unverifiable cost estimates."""

def _amount(value, label, *, allow_zero=False):
    if not isinstance(value, str) or not value.strip():
        raise CostConfigurationError(f"{label} must be an explicit decimal string")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise CostConfigurationError(f"invalid {label}") from exc
    if not number.is_finite() or number < 0 or (not allow_zero and number == 0):
        raise CostConfigurationError(f"invalid {label}")
    return number

def validate_pricing(card, model):
    """Validate the operator's frozen, exact-model standard rate quotation."""
    if not isinstance(card, dict) or set(card) != EXPECTED_FIELDS:
        raise CostConfigurationError("pricing fields missing or unexpected")
    if not isinstance(model, str) or not model.strip() or card["model"] != model:
        raise CostConfigurationError("rate card must match exact requested model")
    if card["currency"] != "USD" or card["processing_mode"] != "standard":
        raise CostConfigurationError("only standard USD pricing supported")
    if card["source_url"] != SOURCE_URL:
        raise CostConfigurationError("use the official OpenAI API pricing page")
    ts = card["checked_at_utc"]
    if not isinstance(ts, str) or not ts.endswith("Z"):
        raise CostConfigurationError("rate check must have an explicit UTC timestamp")
    try:
        date = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CostConfigurationError("invalid rate check timestamp") from exc
    if date > datetime.now(timezone.utc):
        raise CostConfigurationError("pricing check timestamp cannot be in the future")
    if (datetime.now(timezone.utc) - date).total_seconds() > 86400 * 7:
        raise CostConfigurationError("rate check older than seven days")
    for key in ("input_usd_per_million", "output_usd_per_million"):
        _amount(card[key], key)
    return card

def price_estimate(input_tokens, output_tokens, card):
    """Quote un-discounted standard model-token USD, no taxes/other charges."""
    if type(input_tokens) is not int or input_tokens < 0:
        raise CostConfigurationError("invalid provider input token usage")
    if type(output_tokens) is not int or output_tokens < 0:
        raise CostConfigurationError("invalid provider output token usage")
    a = _amount(card["input_usd_per_million"], "input price")
    b = _amount(card["output_usd_per_million"], "output price")
    return (a * input_tokens + b * output_tokens) / Decimal(1_000_000)

def calculate_budget(requests, output_cap, card, max_usd):
    """Reserve worst-case output tokens for EVERY scheduled call before create()."""
    limit = _amount(max_usd, "maximum estimated USD budget")
    if type(output_cap) is not int or output_cap <= 0:
        raise CostConfigurationError("invalid output token cap")
    quote = sum(
        (price_estimate(input_count, output_cap, card)
         for input_count in requests), Decimal(0)
    )
    if quote > limit:
        raise CostConfigurationError("96-call maximum token quote exceeds USD budget")
    return {"estimated_upper_usd": str(quote),
            "approved_estimate_budget_usd": str(limit),
            "pricing_sha256": sha256(json.dumps(
                card, sort_keys=True, ensure_ascii=False,
                separators=(",", ":")).encode("utf-8")).hexdigest(),
            "pricing_source_url": card["source_url"],
            "pricing_checked_at_utc": card["checked_at_utc"],
            "estimated_usd_only": True,
            "billed_usd": None}

def per_arm_costs(rows, card):
    """Attribute model-token estimates and measured token counts by arm."""
    groups = {}
    for arm in ("A", "B", "C"):
        subset = [r for r in rows if r["arm"] == arm]
        groups[arm] = {
            "generations": len(subset),
            "measured_input_tokens": sum(r["actual_input_tokens"] for r in subset),
            "measured_output_tokens": sum(r["actual_output_tokens"] for r in subset),
            "estimated_model_usd": str(sum((
                price_estimate(r["actual_input_tokens"], r["actual_output_tokens"], card)
                for r in subset), Decimal(0))),
        }
    return groups
