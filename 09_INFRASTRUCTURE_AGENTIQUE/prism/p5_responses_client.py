"""Responses SDK transport for the P5 harness, with explicit attempt limits."""
import json
from time import perf_counter


def responses_provider(client, *, model, input_reserve):
    """Adapt an injected SDK client. Reserve part of the budget for input."""
    if type(input_reserve) is not int or input_reserve < 1:
        raise ValueError("input_reserve must be a positive integer")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("an explicit model is required")

    def send(arm, attempt, prompt, *, max_tokens, timeout, max_tools):
        max_output = max_tokens - input_reserve
        if max_output <= 0 or timeout <= 0 or max_tools != 0:
            raise ValueError("insufficient budget or unsupported tool policy")
        started = perf_counter()
        response = client.with_options(max_retries=0, timeout=timeout).responses.create(
            model=model, input=json.dumps(prompt, ensure_ascii=False),
            max_output_tokens=max_output, tools=[], store=False,
        )
        return response, perf_counter() - started, 0

    return send
