# PROPOSAL-01 — exploratory acquisition feasibility, frozen before inference

Purpose: measure whether the actual SFT01 backbone (SmolLM2-135M-Instruct,
revision ee72e5415c002e8fc0566a191a07c0b2b708875a) can invent admissible atomic
graph tasks. This is not the Qwen3B ATOM-08 backbone; do not compare them causally.
No training, no holdout, no replay, no tools offered to the model.
Exactly 32 independent sampled generations with seeds 20261124+i, temperature
0.8, top_p 0.95, max 192 new tokens each, same fixed proposer.PROMPT,
no examples, no repairs, no target answers in prompt. CPU only; two threads.
One execution on creation of the dedicated workflow; no schedule, no
pull_request trigger, no paid API. Record original output, token IDs/count,
prompt hash, seed, exact model revision, latency and all rejection reasons.
Use the existing exact sensor pinned at e68db2c2ca3f14d113fc15f431fac04d5ee7cb30.
Deduplicate by canonical marked graph, count all eight motifs and graph diversity.
Exploratory feasibility signal (not a training authorization): >=16 unique
accepted tasks, >=4 distinct motifs, including >=4 motif-110 examples.
A negative result is useful; no retries or threshold revisions. Even a pass
does not establish that the 256-example quotas can be met, much less learning.
The 32 proposals are development/diagnostic data only. No evaluation corpus
may be inferred from them or supplied to the proposer. A future actual
training cohort requires frozen independent manifests, checks for provenance,
representation family separation, matched optimization budgets, and replay.
Reuse SFT01's pinned stack, not its Python-specific load_train or system prompt.
