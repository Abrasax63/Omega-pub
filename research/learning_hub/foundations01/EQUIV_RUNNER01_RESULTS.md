# EQUIV-RUNNER01 — end-to-end miniature fixture passed; real pilot gated

Preregistration 844ea8539fc829375ed0f6a25c13cc0dd9122be5.
Implementation ba13e0e6d07f2d2ee0bffcfb32c9d2720f2e1fc0.
CI https://github.com/Abrasax63/Omega-pub/actions/runs/45486616678
job 138773606314 successful. Logs verified; artifact metadata checked,
not independently replayed.

All frozen corpus, trace and retention hashes reproduced. Pinned real
tokenizer packed all 96 training pairs; all 192 evaluation prompts
(128 equivalence views plus 64 retention questions) fit context,
maximum 733 tokens before generation (limit 1024).
Three objectives executed through the same training loop on a tiny
random Llama/PEFT model (two fixture pairs, two epochs). Each had
4 updates, 80 input/padded tokens, identical exposure SHA256
b352001810157a381fa776440366161448eef99d213757d2b85c9879896bcf1b.
Positive adapter deltas:
ordinary .0073784723; contrast .0074185362; process .0073642178.
Selected-position logits and gradients match full-logit reference
within 1e-6 on fixture. All adapters saved, hash checked, reloaded,
and fixture logits/generation matched. Six invalid inputs rejected.
Scorer exercised all 768 expected prediction records with deliberately
synthetic constant and oracle outputs; these are NOT model accuracy.
All miniature checks passed; no pretrained weights loaded or updated.

Real CLI prepared: three separate LoRA arms, 192 updates each
(576 total), pinned SmolLM2-135M-Instruct; base plus three arms
evaluate on same questions. Explicit authorization argument required
for train; no automatic real training workflow. Literal CLI guard
is not independently authenticated approval. Training inputs must
contain exactly the four expected files; inference and scoring
use separate input sets, but fixture executes in one job; actual
job isolation still must be set up for pilot. Full pretrained
architecture/runtime/memory, artifact dispatch and real scores
not tested. CPU time/quota unknown; use bounded jobs and fail closed.
No paid API intended, but free Actions allowance not verified.
Synthetic data, no historical corpus-wide contamination audit,
retention limited to edge membership and syntax; public holdout
not independently secret. No deployment, main change, promotion
or deletion.

Decision: ready to request authorization for a strictly exploratory
one-seed pilot, subject to read-only resource/dispatch preflight
and explicit separate train/infer/score execution. Not GO for
general training or promotion. Preserve base and prior adapters,
no use of reserved scores for tuning. Stop on artifact mismatch,
nonfinite loss, incomplete budget, or failed checks. Report all
arms including failures. Three seeds and fresh independent
holdout required before promotion.
