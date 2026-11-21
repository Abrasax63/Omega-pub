# COLI-API-01 — call residency inspired by Colibri

## Status
**EXPERIMENTAL**. This is an adaptation of the *cache residency concept*, not a fork or integration of Colibri's inference engine. No LLM or paid API is called.

## Mechanism
- In-memory opt-in reuse of byte-equivalent serialized JSON requests and responses; no cross-tenant or cross-credential reuse.
- Same model revision, endpoint, all generation parameters and messages required.
- No reuse by default, for tools, for streaming, or nonzero temperature. Caller must assert request is not time-sensitive.
- Concurrent identical requests share one in-flight backend execution (single-flight).
- Errors are not cached. No prompt or secrets stored in metrics. Cached responses are memory-only and defensively copied.

## Important limitations
- Temperature=0 does not guarantee deterministic LLM answers.
- Returning an old response is only acceptable for tasks where exact replay is approved by the application; do not cache external search, changes of state, live information, privacy-sensitive replies, or any response affected by undisclosed backend state.
- This prototype does **not** measure GPU/CPU operations, inference latency, electricity, number of output tokens or monetary savings. It merely demonstrates how many *backend invocation attempts* are skipped on a synthetic deterministic workload.
- There is no hook into Omega's real API orchestration. Integration must remain opt-in and include a live model A/B test and safeguards.

## Reproduce
In this directory with Python 3.10+:

```sh
python3 -m unittest discover -p 'test_router.py' -v
python3 bench_replay.py
```

Expected synthetic workload: 12 requests, 7 distinct exact request identities; baseline 12 backend attempts, opt-in 7, 5 avoided (41.7%). Both produce identical **mock** outputs. No LLM inference occurs.

Reference: https://github.com/JustVugg/colibri/blob/main/docs/CACHE_ROUTE.md


## COLI-API-02 — passive common-prefix observer
`prefix_observer.py` is an **observe-only** wrapper for local/remote OpenAI-style JSON requests. It forwards the **same original wire bytes** to the transport, once and only once, then returns the original transport response. It does not cache LLM outputs, trim context, change request order or modify the model. It keeps only ephemeral HMAC digests of complete message-boundary prefixes, scoped by tenant, authorization, endpoint, model revision, template revision and the entire non-message request envelope. Memory is bounded. Malformed or unsupported requests pass through untouched. Tests: `test_prefix_observer.py`.

The count of shared message prefixes is **not** a measurement of cached tokens, KV-cache hits or saved FLOPs. Savings require an actual compatible engine with provider-specific cache instrumentation. If the provider renders the same message prefixes differently, even a reported byte match may not result in KV reuse. No guaranteed quality conservation is claimed from backend cache execution without a model A/B.

## COLI-API-03 — reuse pinned deterministic verifier results
`exact_verifier_cache.py` memoizes the result of a **pinned, pure exact verifier** when raw document bytes, expected source Git blob, source path, and source verifier revision all match. It does not cache LLM output. Exceptions remain exceptions and are not cached. A source change, a path change, or a verifier version change invalidates the hit. The cache is in-memory, bounded, and defensive-copies its result. This optimization is valid only if the function and all its dependencies are actually pure and version-pinned.

The experiment imports Omega SEM22's actual `verify_source()` from the independent PR #207 at SHA `38b3f6250429901bb307cbea4d49dbcc9c8f6379` (read-only). No hidden gold labels are used; the test makes 24 synthetic finite-function source documents with seven predicates each. It checks original execution vs cached execution and negative controls on source integrity, version and malformed claims. We do not merge, rewrite or certify SEM22 here.

## Reproduce new gates
```sh
python -m unittest discover -p 'test_prefix_observer.py' -v
python bench_prefix.py
# Following two require the pinned SEM22 checker at /tmp/omega_sem22_checker.py
python -m unittest discover -p 'test_exact_verifier_cache.py' -v
python bench_exact_verifier.py
```

**Not evaluated:** real provider caching, live-model response quality, energy reduction, billing or real wall-clock benefits. These require a prospective end-to-end run with caching off/on and equivalent payloads.
