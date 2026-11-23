"""Bounded, fail-closed diagnostic fallback for Omega's restricted Python sandbox.

This module cannot select training examples, access a holdout, call a model,
grant permissions, or update weights. It is ONLY an observation mechanism.
"""
from __future__ import annotations

MAX_ISOLATED_CASES = 12
SCHEMA = "OMEGA_CONDITIONAL_FALLBACK_V1"

def _global_worker_failure(observations):
    """Recognize ONLY failures of the entire sandbox worker, not student logic."""
    if not observations:
        return False
    first=observations[0]
    if not isinstance(first,dict) or set(first)!={"error"}:
        return False
    error=first["error"]
    if not isinstance(error,str):
        return False
    if not (error.startswith("SANDBOX_EXIT_") or
            error=="SANDBOX_TIMEOUT_OR_INVALID"):
        return False
    return all(isinstance(x,dict) and x==first for x in observations)

def evaluate(execute_student,code,inputs,*,max_isolated_cases=MAX_ISOLATED_CASES):
    """Return original batch observations unless a global worker failure occurs.

    The caller supplies already bounded input strings and an unchanged
    sandbox executor. If a batch fails globally, isolate at most 12 examples.
    Never reinterpret non-global errors as global, or silently claim success.
    """
    if not isinstance(inputs,list) or len(inputs)>48:
        raise ValueError("BAD_INPUT_BATCH")
    if not isinstance(max_isolated_cases,int) or isinstance(max_isolated_cases,bool) or not 1<=max_isolated_cases<=MAX_ISOLATED_CASES:
        raise ValueError("UNBOUNDED_ISOLATION_LIMIT")
    if code is None:
        return {"schema":SCHEMA,"status":"NO_SAFE_CODE","triggered":False,
                "batch_observations":None,
                "observations":[{"error":"NO_SAFE_CODE"} for _ in inputs],
                "worker_calls":0,"isolation_executions":0,
                "max_isolated_cases":max_isolated_cases}
    if not inputs:
        return {"schema":SCHEMA,"status":"EMPTY_INPUT","triggered":False,
                "batch_observations":[],
                "observations":[],
                "worker_calls":0,"isolation_executions":0,
                "max_isolated_cases":max_isolated_cases}
    original=execute_student(code,inputs)
    if not isinstance(original,list) or len(original)!=len(inputs):
        # A malformed test runner response is not a student failure.
        raise ValueError("EXECUTOR_CONTRACT_BROKEN")
    if not _global_worker_failure(original):
        return {"schema":SCHEMA,"status":"BATCH_ACCEPTED","triggered":False,
                "batch_observations":original,"observations":original,
                "worker_calls":1,"isolation_executions":0,
                "max_isolated_cases":max_isolated_cases}
    if len(inputs)>max_isolated_cases:
        return {"schema":SCHEMA,"status":"GLOBAL_FAILURE_UNDIAGNOSED_CAP",
                "triggered":False,"batch_observations":original,
                "observations":original,"worker_calls":1,
                "isolation_executions":0,
                "max_isolated_cases":max_isolated_cases}
    distinct=[]
    for raw in inputs:
        one=execute_student(code,[raw])
        if not isinstance(one,list) or len(one)!=1:
            raise ValueError("ISOLATED_EXECUTOR_CONTRACT_BROKEN")
        distinct.append(one[0])
    return {"schema":SCHEMA,"status":"GLOBAL_FAILURE_ISOLATED",
            "triggered":True,"batch_observations":original,
            "observations":distinct,"worker_calls":1+len(inputs),
            "isolation_executions":len(inputs),
            "max_isolated_cases":max_isolated_cases}
