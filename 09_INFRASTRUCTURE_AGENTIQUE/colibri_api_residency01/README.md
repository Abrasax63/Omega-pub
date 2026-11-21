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
