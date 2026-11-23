"""Minimal execution-gated calling policy for FUTURE fresh Omega evaluations.

NOT the preregistered 18-call ACTIVE-DEBUG01 protocol: that first run has
finished and its six hidden tasks are consumed. This can be used only on new
tasks for a prospective comparison. It does not train model weights, invoke
any paid API, or access evaluator gold.
"""
from __future__ import annotations

import inference

def repair_one(client, public_task):
    """One local model request; second request ONLY if public tests fail.

    client: interface .ask(messages, tag), injected for testability.
    This function has no model connections unless a caller supplies a client.
    A proposed code is admitted only if it passes all public examples in the
    existing AST-restricted Python subprocess sandbox. Hidden correctness is
    not claimed.
    """
    required=("id","prompt","broken","public")
    if (not isinstance(public_task,dict) or
        any(k not in public_task for k in required) or
        not isinstance(public_task["public"],list) or
        len(public_task["public"])!=2):
        raise ValueError("EXPECTED_SANITIZED_PUBLIC_TASK")
    identity=public_task["id"]
    initial=client.ask(inference.messages(public_task["prompt"]),
                       identity+":GATED_INITIAL")
    first=inference.public_feedback(initial,public_task["public"])
    if first.get("correct")==2:
        code,status=inference.parse_code(initial)
        if code is None:
            raise AssertionError("PUBLIC_PASS_WITHOUT_ADMITTED_AST")
        return {"status":"PUBLIC_VALIDATED_FIRST_DRAFT_NOT_HIDDEN_CERTIFIED",
                "code":code,"initial_raw":initial,"revised_raw":None,
                "model_calls_used":1,"revision_skipped":True,
                "hidden_cases_used":0,"public_test_count":2,
                "public_feedback_first":first,"public_feedback_final":first}

    second=client.ask(inference.messages(
        inference.feedback_review_prompt(public_task,initial,first)),
        identity+":GATED_FEEDBACK_REVISION")
    revised=inference.public_feedback(second,public_task["public"])
    code,status=inference.parse_code(second)
    valid=(revised.get("correct")==2 and code is not None)
    return {"status":("PUBLIC_VALIDATED_REVISION_NOT_HIDDEN_CERTIFIED"
                       if valid else "PUBLIC_REPAIR_FAILED_ABSTAIN"),
            "code":code if valid else None,
            "initial_raw":initial,"revised_raw":second,
            "model_calls_used":2,"revision_skipped":False,
            "hidden_cases_used":0,"public_test_count":2,
            "public_feedback_first":first,"public_feedback_final":revised}
