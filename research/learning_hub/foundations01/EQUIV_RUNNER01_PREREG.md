# EQUIV-RUNNER01 — end-to-end contract before real training
No pretrained weights loaded or updated in this experiment. Implement
a guarded CLI for the already preregistered four-arm pilot and verify
on randomly initialized miniature Llama/PEFT only. No real training
workflow or automatic dispatch. Require literal explicit authorization
argument for real training; this is a software guard, not proof of
user authorization. Train loads only pinned train/dev/trace artifacts;
manifest hashes compared with frozen constants; reject reserved inputs.
192 paired updates (96 pairs x2), fixed seed, rank8 alpha16 q/v,
AdamW lr1e-4, zero dropout, identical ordered pair exposures, both
binary and auxiliary inputs all trained arms, losses as amendment.
Use causal hidden-state selection before LM head to avoid full-vocab
logits at unsupervised positions; verify equivalence to full logits
and gradients on tiny fixture. Save adapter only, manifest with
base revision, ordered exposure digest, update/token counts, positive
adapter delta, immutable adapter SHA256, base frozen flag and losses.
Inference loads questions only, separate from scorer labels; strict
generation + binary diagnostic on two graph views, retention on two
domains. Score exact paired/class metrics and compare to frozen base;
retention per domain <=5 points loss; record floor effects. C/D vs B
report paired differences, no winner selection on reserved set.
Dry-run exercise identical train loop with tiny random model, 2 pairs
x2 epochs, save/reload adapters and compare logits, raw generation
and scorer contract on tiny fixtures; test corrupted adapter,
wrong hashes, labels in inference and training, missing predictions,
constant classifier. Also check real tokenizer/context sizes for
all frozen questions and retention questions separately (without
pretrained model). Use pinned torch/transformers/peft. A real CPU
runtime estimate cannot be inferred from fixture; do not claim
production readiness or gain. Actual real runner not executed on
pretrained weights; require explicit approval and manual launch
after review. No main change, paid API, promotion or deletion.
