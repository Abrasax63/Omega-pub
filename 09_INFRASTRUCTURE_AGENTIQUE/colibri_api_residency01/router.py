"""Experimental Colibri-inspired call residency; in-process, opt-in only.

Does NOT alter LLM internal computation. A saved call is a skipped identical
request, not proof that a non-deterministic backend would respond identically.
No persistent cache; metrics include no prompt or key material.
"""
from __future__ import annotations

from concurrent.futures import Future
from copy import deepcopy
from hashlib import sha256
import json
from threading import Lock
from typing import Any, Callable


class CallResidency:
    def __init__(self) -> None:
        self._lock = Lock()
        self._cache: dict[str, Any] = {}
        self._inflight: dict[str, Future] = {}
        self._stats = {"backend_calls": 0, "cache_hits": 0, "inflight_shared": 0, "failures": 0}

    def metrics(self) -> dict[str, int]:
        with self._lock:
            return dict(self._stats)

    @staticmethod
    def _key(tenant: str, credential_scope: str, endpoint: str,
             model_revision: str, payload: dict[str, Any]) -> str:
        record = [tenant, credential_scope, endpoint, model_revision, payload]
        wire = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return sha256(wire.encode("utf-8")).hexdigest()

    def invoke(self, *, tenant: str, credential_scope: str, endpoint: str,
               model_revision: str, payload: dict[str, Any], backend: Callable[[dict[str, Any]], Any],
               replay_approved: bool = False) -> Any:
        """Only replay explicitly approved, non-streaming, non-tool, temperature=0 calls.

        Caller must attest no time-varying data. Revision and authorization
        scope prevent reuse after a model or access-policy change.
        """
        if not isinstance(payload, dict):
            raise ValueError("payload must be a dictionary")
        stable = (replay_approved and payload.get("temperature") == 0
                  and payload.get("stream", False) is False
                  and not payload.get("tools") and not payload.get("tool_choice")
                  and all(isinstance(x, str) and x for x in
                          (tenant, credential_scope, endpoint, model_revision)))
        if not stable:
            with self._lock:
                self._stats["backend_calls"] += 1
            try:
                return backend(deepcopy(payload))
            except Exception:
                with self._lock:
                    self._stats["failures"] += 1
                raise
        key = self._key(tenant, credential_scope, endpoint, model_revision, payload)
        with self._lock:
            if key in self._cache:
                self._stats["cache_hits"] += 1
                return deepcopy(self._cache[key])
            if key in self._inflight:
                fut = self._inflight[key]
                self._stats["inflight_shared"] += 1
                leader = False
            else:
                fut = Future()
                self._inflight[key] = fut
                self._stats["backend_calls"] += 1
                leader = True
        if not leader:
            return deepcopy(fut.result())
        try:
            value = deepcopy(backend(deepcopy(payload)))
            with self._lock:
                self._cache[key] = value
                self._inflight.pop(key, None)
                fut.set_result(value)
            return deepcopy(value)
        except BaseException as exc:
            with self._lock:
                self._stats["failures"] += 1
                self._inflight.pop(key, None)
                fut.set_exception(exc)
            raise
