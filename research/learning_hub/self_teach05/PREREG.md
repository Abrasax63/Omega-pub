# SELF-TEACH-05 — preregistration, baseline batched vs isolated diagnostic

Date: 2026-11-23. Parent: `60d78953073724d499dbf6a703cf01ad0ebc5154` (PR #246; previous holdout consumed). Status **PREREGISTERED ONLY**, before new engine, model calls, or scoring.

## Hypothesis and falsification
When one generated Python program fails on one example or loops, the existing group grader can mark ALL development cases with the same sandbox exit. Does **isolating every example for diagnostic feedback** improve repair over the current **batched feedback**, with a single shared initial generation and equal model-call/token caps?

Four **entirely new** synthetic Python string tasks F1–F4 each with two public, eight development, six sealed cases. Families are distinct from prior runs; expected outputs produced by four independent deterministic reference functions BEFORE the engine. Total 32 development examples and 24 sealed test cases. The reference functions are not sent to the model or included in the generator. Data are frozen by this commit's Git blob SHA and checked at execution. The sealed cases are used only AFTER all outputs for both arms are stored and hashed.

## Paired randomized? NO — Deterministic paired initial, not randomized
For each task generate one model answer `INIT`. The two treatment arms start from **identical raw model bytes**:
- `BATCH`: legacy one-process call on all eight cases; show up to three failures chosen by fixed (length,input) order, even if the group exit masks detail.
- `ISOLATED`: run the same safe code separately on each development input in a fresh worker with the **same per-worker restrictions** as the existing sandbox; show up to three **actual individual failures** chosen by same order.
- At most **2 revision calls per arm**. Same prompt prefix/instruction, same token limit per model generation, same examples, model, parameters and sandbox. Only diagnostics differ. Retain the most correct prior revision using **individual evaluation as a common scorer for both arms**, on all 8 dev inputs. No hidden data for selection.
- Keep individual observation statuses even if a worker exceeds CPU or fails, never impute a group failure as 8 distinct defects. Track both group/individual observations and elapsed seconds/call counts. Unsafe output cannot replace the safe best.
- Evaluate final chosen BATCH/ISOLATED and original INIT on the same 24 held-out cases, once. Both models never read or query sealed cases.

## Acceptance before inference
1. Safe AST; source/gold separation; trace with raw outputs and SHA; no paid API; no writing main; no LoRA; no automatic merge.
2. **Adopt isolated feedback only if** ISOLATED improves on BATCH by **at least 2/24** hidden exact cases **and** no initially fully correct task is degraded, while the safe-code validity is no worse, AND any negative control demonstrates the masking defect is correctly diagnosed. Cost of independent tests reported, not assumed equal.
3. If not: `NO_VERIFIED_ISOLATED_FEEDBACK_GAIN`. Positive on just 4 synthetic tasks is **exploratory** and NOT evidence of long-term autonomous learning, weight updates, or AGI.
4. First sealed score consumes this cohort permanently. Never rerun as independent. CI success != learning proof.

## Model/cost settings
Qwen2.5-3B-Instruct Q4_K_M (SHA256 9c9f56a391a3abbd5b89d0245bf6106081bcc3173119d4229235dd9d23253f94), llama.cpp CPU localhost, existing safe executor. **4 initial + at most 16 repair generations = 20 calls**, cap 660 output tokens each. No gradient, no paid calls, nor changes to `main`.

Specific negative control: a syntactically safe function loops on one development input but returns correctly on another. The batched test marks both failed on timeout; separate tests distinguish them. This fixture is ONLY a software test, not model training.

