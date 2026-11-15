# Omega: real open-weight model proposing executable code (pilot)

Status: EXPERIMENTAL. This is not proof of improved intelligence or a secure generalized programming agent.

## Architecture

- Real model: Qwen2.5-Coder-1.5B-Instruct-GGUF Q4_K_M, run on a public GitHub Actions CPU runner using pinned llama.cpp commit 5a4afd80779ba51166b59986e61a0bfbb9e1a4c6. There is no paid API, GitHub Models, or smartphone GPU.
- Weights: official Qwen GGUF file, SHA-256 cc324af070c2ecbfd324a30884d2f951a7ff756aba85cb811a6ec436933bb046. Verified on download.
- Proposals: two real model prompts requesting one Python function q_power(rows, steps). The model generates executable source code, rather than choosing from the four preset templates of PR #84. Full candidate and its SHA-256 are retained for audit.
- Static gate: a restrictive Python AST syntax validator rejects imports, nested functions, arbitrary external calls, direct dunder attributes and globals. This is only a first filter and cannot be relied upon as a security sandbox.
- Isolation: candidates run in disposable Docker containers with network disabled, root filesystem read-only, non-root UID, dropped capabilities, no new privileges, CPU/memory/process limits, timeout and no repository or secret mounts. Docker shares the host kernel and is not a security proof against deliberately malicious programs.
- Verification: independent Boolean matrix power reference from reference.py, direct trajectory computation for Delta_h, and unchanged evaluation gate from PR #83.
- Comparators: both linear-scan and strong classical binary exponentiation square-scan. Improvements against the weak baseline alone prove nothing new.
- Reserved cases: three fresh random seed families are generated and hashed BEFORE the first inference. Those cases and labels are NOT shown to model. Candidates are selected using only three public training families, and the reserved evaluation occurs at most once after selection.

## Evidence and reproducibility

Workflow: .github/workflows/omega-open-model-sandbox.yml.
Main code: model_proposal.py, sandbox_runner.py, model_pilot.py.
The job compiles and tests Python, downloads and checks the model file, builds the pinned CPU inference binary, makes two inference calls, tests proposed source in Docker, records every result and archives model-result.json.

Any model failure is reported, never replaced with a fake template claim. Invalid code is a negative result. A successful CI run indicates pipeline execution only.

## Limits

- Ephemeral held-out groups are not a truly independent external preregistration. The manifest hash is printed before inference but the same workflow controls it.
- The runtime metric is host wall time including Docker startup and noise. Neither code-size nor time changes alone prove greater reasoning ability.
- Small 1.5B models often produce code with errors. Zero valid candidates is a valid scientific outcome.
- The Docker image is logged with digest but is not yet pinned for future runs.
- This is a two-attempt, single-task experiment. Broader transfer, adversarial safety, statistical significance and independent provenance still need external testing.
- No merge, no automatic scientific status promotion, no rights to change main or other PRs.


## Verified empirical results on 2026-11-15

- First Qwen2.5-Coder-1.5B attempt: run 43692466252, Python unit tests passed and two true model responses were executed, but both were incorrect or crashed. NO_VALID_MODEL_CANDIDATE.
- Second 1.5B attempt with revised task specification and public training feedback: run 43693100005, two model responses crashed (integer used as iterable), no holdout opened. NO_VALID_MODEL_CANDIDATE.
- Qwen2.5-Coder-3B Q4_K_M: run 43693684837, downloaded weights SHA-256 724fb256bec1ff062b2f65e4569e871ad2e95ab2a3989723d1769c54294730b7, two successful model calls. Both responses were BYTE-IDENTICAL code despite different runtimes. The generated algorithm is a standard linear Boolean matrix-power iteration; the generated source is not a new discovery.
- The 3B model correctly computed Q^h and Delta_h on all three synthetic withheld cases. Its holdout cost was 820446 microseconds including container startup, versus 855601 for naive linear-scan and 791506 for strong classical square-scan. The gate returns REVIEW_REQUIRED relative to the naive baseline, but REJECTED against square-scan.
- The two identical source code proposals had training costs of 7493942 and 876911 microseconds on the same public development families. This huge discrepancy illustrates why single-run container wall-time comparison is unfit for a fine-grained speed claim. It is NOT a measured eightfold algorithmic improvement.
- The evaluator only produced a non-certifying in-run SHA commitment of the reserved manifest. No external replication, randomized crossed order, or independently established confidence interval was performed.
- Subsequent changes add AST-semantic deduplication and a guard against evaluating identical code twice. These changes do not retroactively modify the original run. The expensive LLM workflow is now manual-only to avoid repeated downloads and non-independent reuse of held-out groups.

**Scientific status: correct model-generated program on a tiny synthetic task, but no demonstrated superiority over classical exponentiation or specific cognitive self-improvement of Omega.**
