# PREREG — OMEGA-TRANSFER-01 (prospective audit of one frozen model output)

Protocol version: 1, frozen before adding the measurement workflow.
**Primary candidate**: exact source emitted by Qwen2.5-Coder-3B Q4_K_M in the previous GitHub Actions run [43693684837](https://github.com/Abrasax63/Omega-pub/actions/runs/43693684837), artifact 14153811333. Source SHA-256 **121e09058b41984199ac870b6250882ffa4eddb5a4344b1fb1cd0d674296de5a**, in `frozen_qwen3b_candidate.py`. This candidate will NEVER be edited based on these outcomes.

## Primary question (falsification first)

Does the *previously generated, unmodified* Qwen program calculate Boolean relation powers exactly and achieve a **meaningful CPU-time advantage** over both strong classical baselines across distinct graph families?

Primary answer is **NO** if any correctness test fails, if the candidate fails a prespecified speed threshold, or if the execution/provenance requirements cannot be verified. A successful workflow itself is not evidence of superiority.

## Fixed test specification

Seed: `OMEGA-TRANSFER-01-FROZEN-2026-11-15`. 8 graph families: directed cycle, empty digraph, complete digraph, sparse random digraph, dense random digraph, functional digraph, bipartite directed graph, and finite-dynamical-system observational projection Q from a randomized T and pi. For each family, evaluate n=12 and n=28 vertices, and exact walk lengths h=1,5,64,192: **64 distinct cases**. Use additional h=0 consistency checks outside the timing denominator. The public source generator will be deterministic and published *after* this preregistration. This is NEW data relative to the previous single 72-state model pilot, but it is synthetic and public: **not an independently sequestered external dataset**.

Holdout access: the candidate is a frozen artifact from a prior real model inference. **No LLM will be invoked during this evaluation**, so it cannot adapt from these reserved cases. No feedback loops or changes to the candidate are allowed after the first run.

## Strong comparators and fairness

Baselines from the audited `variant_factory.py` of PR #84: `square-scan` and `square-lowbit`. These are existing binary-exponentiation algorithms. `linear-scan` is recorded only as a weak sanity comparison; beating it does NOT satisfy the primary criterion.

All arms use exactly the same cases, the same Python 3.12 container, the same single allocated CPU, and seven time measurements per program per case. Randomize the execution order within each measurement round using a fixed RNG. One warm-up per arm/case. Use `time.process_time_ns()` inside the fixed read-only measurement harness, rather than timing the Docker startup. Compute the **median** of the seven CPU measurements. Do not drop outliers or select a favorable repetition. A source SHA-256 mismatch, nonzero process exit, incorrect output, unexpected/duplicate case, or incomplete arm invalidates the run.

Truth: a separately authored set-propagation implementation (`reference.walks_exact`), plus `R_h` / `Delta_h` direct orbit checks for observational-projection cases. The candidate may not modify the reference or scoring code. Input and output hashes recorded.

## Decision rule (predeclared)

For each case, compare candidate median CPU against the **faster** of the two strong binary-exponentiation reference medians (conservative classical benchmark), i.e. speedup = classical_best_time / candidate_time.

To pass to **external review only**, require *all*:
1. Correct `Q^h` output on all 64 cases, including independent `Delta_h` consistency on projection cases; zero false confirmations.
2. Geometric mean speedup across 64 cases at least **1.10**.
3. Each of the eight family medians of speedup at least **1.05**.
4. At least seven of eight family medians greater than 1 (one-sided exact binomial sign test p <= 0.05).
5. No provenance, source mismatch, test omission, budget or execution errors.

A PASS only means **REVIEW_REQUIRED** (not certified; does not merge code). Fail is **NO_DEMONSTRATED_ADVANTAGE**. A missed/failed run is **INVALID_EXPERIMENT**, never a pass.

## Trust limits

- These families are authored in the same repository, not held by an independent custodian. A commit-ordered frozen source is evidence of procedural separation, **not an external scientific holdout**.
- Docker is a bounded container, not a high-assurance kernel sandbox. Only the frozen code already inspected is executed.
- CPU timings are noisy on hosted hardware; exploratory descriptive results must not be promoted as stable. Even passing the rule requires independent reproduction with fresh external data and repeated runs.
- All attempted runs, failures, hashes and refutations must remain visible. Do not retry and cherry-pick the best run.
- No model training, weight modification, live self-programming loop or novel algorithm is claimed by this protocol.
