# Conditional diagnostic fallback — Omega (2026-11-23)

## Integration boundaries
- **Integrated as an explicit `grade_dev(...,mode="conditional")` option** in the existing SELF-TEACH-05 research harness, isolated experimental branch only.
- **NOT integrated in `main`, hourly autonomous cycles, skill promotion, model weights, or the completed SELF-TEACH-05 blind run.** Legacy `batch` and `isolated` modes remain bit-for-bit behaviorally unchanged. The 24 SELF-TEACH-05 holdout examples are consumed; never replay them as fresh tests.
- The fallback is a software **observer** and cannot teach the LLM without an independent prospective model experiment.

## Exact trigger and bounds
- First execute a batch in the original subprocess and AST sandbox.
- Only if every item is the **same global worker error** (SANDBOX_EXIT_\* or SANDBOX_TIMEOUT_OR_INVALID) run each input individually in separate already restricted workers.
- Never trigger on ordinary bad outputs, per-example exceptions, unsupported/unsafe code, or blank input. Max 12 isolated cases; above this number keep the group error with status `GLOBAL_FAILURE_UNDIAGNOSED_CAP` and do not claim recovery. An isolated worker that also times out remains an error, never a success.
- Return both original batch evidence and isolated observations with worker call counts. No hidden cases, new model calls, model-weight changes, API payment, or external side effects.

## Next experiment (not performed by this PR)
Preregister a **fresh** data cohort with real generated global-failure examples; compare unconditional batch against conditional fallback on actual repairs at equal model-call budget and include normal healthy cases to measure overhead and guard false positives. A software-success CI does not establish learning.

## Training gate
No self-training/promotion until enough independently **verified** code solutions across at least 12 families (24 verified examples as the prior LoRA admission threshold), a genuinely new blind cohort, and a comparison of base vs trained **semantic correctness** separated from format. A loss decrease or green CI is insufficient.
