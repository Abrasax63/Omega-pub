# EQUIV-PROCESS01 — verified trace targets and training-interface dry run

Preregistered amendment 4d8a90a0b3c1266593714b2dfe5055e2b6a866fb.
Implementation 1f0e61aae32d145fe464698e492b5bd5aa0b8db6.
CI https://github.com/Abrasax63/Omega-pub/actions/runs/45485447578
freeze 138769479817 and dryrun 138769653570 successful.
Logs checked; artifact metadata obtained, no independent artifact replay.

Recreated all four EQUIV-PILOT01 files exactly (SHA256 match).
208 train/dev trace targets, 1944 bits, all verified by singleton
extension check and blocked-set computation; equality checked against
exact equivalence oracle. Fresh retention: 64 questions/32 pairs,
16 directed membership pairs, 16 Python syntax pairs; balanced.
Syntax validity is not general programming competence. Historical
corpus-wide overlap not audited. No reserved labels delivered to dryrun.
New frozen SHA256:
traces.json b11c2ff75ba4d5abe7c4a83e30a6dfe3e4e5513585df02e79248389db95bdadf
retention-questions.json 21582cb76c2a75a6d19d3486ab46d0c29fbfec0d5d41fbf65ac9b075aca53943
retention-labels.json 47550736816876c27aad82078fac73818a45a1a3c6a21026d9f7e8790820bf91

Actual pinned tokenizer checks: 104 train/dev pairs; 62768 binary
sequence tokens (416 supervised), 69704 auxiliary sequence tokens
(2360 supervised), maximum length 548 including target. Yes/No each
one token; EOS included, prompt loss masked. Counts combine train/dev,
not actual training exposures. All three train objectives process the
same four rows; auxiliary labels contribute only to process arm.
Equal input exposure is not equal supervision.

Gradient fixture (zero logits):
ordinary aux abs gradient 0, positive Yes gradient -.21875,
negative Yes gradient .03125;
contrast aux 0, positive -.5842793, negative .3967793;
process aux .875, positive -.21875, negative .03125.
Pairwise contrast increases pressure in the expected directions.
This verifies objective mechanics, not usefulness on real data.

Tiny randomly initialized Llama + actual PEFT LoRA, one update per
arm, matched 20 input tokens, 512 trainable parameters, frozen base
parameters unchanged. Adapter delta L2 ordinary .0015992503,
contrast .0015997523, process .0015987679. No pretrained Omega
weights loaded, no real training, no semantic gain or retention score.
No persistent trained checkpoint produced by this dry run.

Readiness: corpus, exact trace supervision, tokenizer, causal
alignment and gradient/adapter interface checked. Proceed to prepare
explicitly gated real pilot runner and fresh evaluation/retention
scorer; verify isolated artifact inputs, matched batches, update
counts, saved adapter hashes and baseline scores. Full pretrained
runner/evaluator and retention measurement remain unvalidated.
User approval required before actual weight update; no automatic
training workflow. One seed exploratory, no promotion without
replication and fresh independent holdout. No paid API or main change.
