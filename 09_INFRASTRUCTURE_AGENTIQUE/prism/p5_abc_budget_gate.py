"""Strict P5 A/B/C prompt-specific input-token gate.

NO model response generation, no grading, no holdout. The caller must supply
an authentic SDK client, exact model snapshot and caps. Before any model
generation, count all 144 public calibration prompts using the provider's
token-counting endpoint. Fail closed if input counts are missing, inconsistent,
or do not leave the SAME output cap within the SAME per-call total cap.

The returned data remains a PUBLIC CALIBRATION PREFLIGHT, not a benchmark win.
This adapter does not read a key, instantiate a provider or send generations.
"""
from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json

from p5_abc_fair_preflight import ARMS, canonical, preflight


class BudgetGateError(ValueError):
    """Inputs or accounting do not satisfy the preregistered comparison."""


def check_live_budget(packet, token_counter, *, model,
                      total_token_cap, output_token_cap):
    """Count exact input tokens with the provided function.

    token_counter(model=..., instructions=..., input=..., tools=[])
    must perform real provider token counting and return a nonnegative int.

    Under testing a fake function may be injected; those outputs cannot be
    described as provider-verified. No SDK or LLM generation calls occur here.
    """
    if not isinstance(model,str) or not model.strip() or model in (
        "mock","fake","unspecified","unknown","TBD"):
        raise BudgetGateError("exact actual model snapshot required")
    if type(total_token_cap) is not int or type(output_token_cap) is not int:
        raise BudgetGateError("token caps must be integers")
    if not 0 < output_token_cap < total_token_cap:
        raise BudgetGateError("positive output cap must fit in total cap")
    if not callable(token_counter):
        raise BudgetGateError("authentic token-counting function required")

    # If a caller attempts to add oracle fields or privileged C context,
    # reject BEFORE invoking any provider endpoint.
    frozen=preflight()
    if packet.get("status")!="PREFLIGHT_ONLY_P5_LIVE_NOT_RUN":
        raise BudgetGateError("only exact public calibration packet allowed")
    if canonical(packet.get("requests"))!=canonical(frozen["requests"]):
        raise BudgetGateError("requests differ from verified frozen packet")
    counts=[]
    for row in packet["requests"]:
        request=row["request"]
        params={
            "model":model,
            "instructions":request["instructions"],
            "input":json.dumps(request["input"],sort_keys=True,
                               ensure_ascii=False,separators=(",",":")),
            "tools":[],
        }
        used=token_counter(**params)
        if type(used) is not int or used<0:
            raise BudgetGateError("provider input token count missing/invalid")
        if used+output_token_cap>total_token_cap:
            raise BudgetGateError("one prompt exceeds the equal total budget")
        counts.append({
            "case_id":row["case_id"],
            "condition":row["condition"],
            "arm":row["arm"],
            "prompt_sha256":row["prompt_sha256"],
            "input_tokens_counted":used,
            "total_token_cap":total_token_cap,
            "output_token_cap":output_token_cap,
            "tools_allowed":0,
        })
    distribution={}
    for arm in ARMS:
        group=[r["input_tokens_counted"] for r in counts if r["arm"]==arm]
        distribution[arm]={
            "requests":len(group),
            "min_input_tokens":min(group),
            "max_input_tokens":max(group),
            "sum_input_tokens":sum(group),
        }
    return {
        "status":"INPUT_TOKENS_COUNTED_BUT_MODEL_GENERATION_NOT_RUN",
        "calibration_only":True,
        "provider_model":model,
        "real_provider_confirmation":"caller-dependent_unverified_by_this_code",
        "prompt_count":len(counts),
        "token_counting_endpoint_calls":len(counts),
        "actual_model_generation_calls":0,
        "total_token_cap_per_call":total_token_cap,
        "output_token_cap_per_call":output_token_cap,
        "tools_allowed":0,
        "per_arm_distribution":distribution,
        "rows":counts,
    }


def sdk_token_counter(client, *, timeout_seconds=30):
    """Adapt the existing OpenAI Responses input token counting workflow.

    No OPENAI_API_KEY retrieval or implicit SDK client construction occurs.
    The caller's explicitly supplied client handles authentication.
    """
    if not hasattr(client,"with_options"):
        raise BudgetGateError("injected SDK client is required")
    if type(timeout_seconds) not in (int,float) or timeout_seconds<=0:
        raise BudgetGateError("invalid timeout")
    options=client.with_options(max_retries=0,timeout=timeout_seconds)
    api=getattr(getattr(options,"responses",None),"input_tokens",None)
    if api is None or not callable(getattr(api,"count",None)):
        raise BudgetGateError("provider input token count unsupported")

    def count(**params):
        result=api.count(**params)
        value=getattr(result,"input_tokens",None)
        if type(value) is not int or value<0:
            raise BudgetGateError("provider returned no exact input-token count")
        return value
    return count
