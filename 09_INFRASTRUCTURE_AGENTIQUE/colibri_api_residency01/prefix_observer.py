"""Passive Colibri-inspired prefix analysis. No change to model requests or responses."""
import hashlib
import hmac
import json
import secrets
from collections import OrderedDict
from threading import Lock


def _wire(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


class PrefixObserver:
    def __init__(self, max_entries=128, max_bytes=262144):
        if max_entries < 1 or max_bytes < 1:
            raise ValueError("limits must be positive")
        self._secret = secrets.token_bytes(32)
        self._seen = OrderedDict()
        self._max_entries, self._max_bytes = max_entries, max_bytes
        self._lock = Lock()
        self._stats = dict(requests=0, shared_prefix_requests=0,
                           matched_prefix_message_bytes=0, skipped=0)

    def stats(self):
        with self._lock:
            return dict(self._stats)

    def _observe(self, body, tenant, authorization_scope, endpoint,
                 model_revision, template_revision):
        if not isinstance(body, bytes) or len(body) > self._max_bytes:
            raise ValueError("bad body")
        if any(not isinstance(x, str) or not x for x in
               (tenant, authorization_scope, endpoint, model_revision, template_revision)):
            raise ValueError("bad scope")
        data = json.loads(body)
        if not isinstance(data, dict):
            raise ValueError("bad JSON object")
        msgs = data.get("messages")
        if not isinstance(msgs, list) or not msgs or not all(
            isinstance(m, dict) and isinstance(m.get("role"), str)
            and isinstance(m.get("content"), str) for m in msgs
        ):
            raise ValueError("unsupported messages")
        scope = _wire([tenant, authorization_scope, endpoint,
                       model_revision, template_revision,
                       {k: v for k,v in data.items() if k != "messages"}])
        prefixes = []
        for idx in range(1, len(msgs) + 1):
            val = _wire(msgs[:idx])
            digest = hmac.new(self._secret, scope + b"\0" + val, hashlib.sha256).digest()
            prefixes.append((digest, len(val)))
        matched = 0
        with self._lock:
            self._stats["requests"] += 1
            for digest, length in prefixes:
                if digest in self._seen:
                    matched = max(matched, length)
                    self._seen.move_to_end(digest)
                else:
                    self._seen[digest] = length
            if matched:
                self._stats["shared_prefix_requests"] += 1
                self._stats["matched_prefix_message_bytes"] += matched
            while len(self._seen) > self._max_entries:
                self._seen.popitem(last=False)

    def forward(self, body, transport, *, tenant, authorization_scope, endpoint,
                model_revision, template_revision):
        """Telemetry fail-open; call transport ONCE with original body bytes."""
        try:
            self._observe(body, tenant, authorization_scope, endpoint,
                          model_revision, template_revision)
        except Exception:
            with self._lock:
                self._stats["skipped"] += 1
        return transport(body)
