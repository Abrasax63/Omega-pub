"""Exact-source verification memoizer for pinned, pure verifier functions.

No LLM result reuse. Only successful deterministic verifier output is cached.
The verifier revision is part of the key; caller is responsible for pinning
all verifier dependencies and supplying an accurate revision fingerprint.
"""
from collections import OrderedDict
from copy import deepcopy
from hashlib import sha256
import json


class ExactVerifierCache:
    def __init__(self, capacity=128):
        if capacity < 1: raise ValueError("capacity must be positive")
        self._entries = OrderedDict()
        self._capacity = capacity
        self.actual_verifications = 0
        self.hits = 0

    def verify(self, raw, *, expected_blob, source_path,
               verifier_revision, verification_fn):
        if not isinstance(raw, bytes):
            raise TypeError("source must be bytes")
        if any(not isinstance(x, str) or not x for x in
               (expected_blob, source_path, verifier_revision)):
            raise ValueError("missing provenance")
        # No output is used unless ALL relevant inputs match exactly.
        digest = sha256(raw).hexdigest()
        key = (digest, len(raw), expected_blob, source_path, verifier_revision)
        if key in self._entries:
            self.hits += 1
            self._entries.move_to_end(key)
            return deepcopy(self._entries[key])
        self.actual_verifications += 1
        # Preserve original error behavior; errors are never cached.
        result = verification_fn(raw, expected_blob=expected_blob, source_path=source_path)
        # Only JSON-compatible, detached values can be cached.
        frozen = json.loads(json.dumps(result, ensure_ascii=False, allow_nan=False))
        self._entries[key] = frozen
        while len(self._entries) > self._capacity:
            self._entries.popitem(last=False)
        return deepcopy(result)
