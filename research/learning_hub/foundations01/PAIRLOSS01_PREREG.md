# PAIRLOSS01 — prospective paired-objective ablation
After two collapse results and CAPACITY01, test a genuinely different
learning objective, not a repeat of single-example SFT or model sweep.
Hypothesis: a loss sensitive to opposite labels of minimally changed
inputs can counter constant-output collapse. This is not guaranteed.

Use the exact archived MEMBERSHIP-SFT01 training corpus (128 graphs,
64 pairs; SHA256 bd67b38d0eab09654fe8d58eac22b72e3d63a23dc25c961f843cde90926f26d7).
Compare two fresh adapters of pinned 135M, same initialization seed
20261129, rank8 alpha16 q/v, AdamW .0005, 2 CPU threads, same pair order,
128 optimizer steps (64 two-example batches x 2 epochs), same 256
example exposures, same edge-list prompts, Yes/No+EOS target-only CE.
Arm CE: mean target-token cross entropy. Arm PAIR: identical CE plus
softplus(1 - (s_present - s_absent)), where s=logit(Yes)-logit(No)
at last prompt position, coefficient 1. Both labels must roundtrip
single token; otherwise fail closed. Right padding masked. Log CE,
pair loss, margin, total loss, tokens, weight delta and hashes. Matched
updates and exposures, not matched FLOPs claim. Compare only these
arms causally within this pilot, not previous single-example optimizer.
Freeze fresh 64 questions, 32 paired families (16 size5,16 size6),
exclude canonical graph keys of ATOMIC-SFT01, MEMBERSHIP-SFT01 and
CAPACITY01 holdouts, deterministic seed 20261201+i, bounded search.
Opaque question IDs, no labels downloaded by training or inference.
Primary same strict free Yes/No greedy max8 edge-list output; matrix
secondary, prefix and raw first-token probability diagnostic separate.
PAIR must achieve >=48/64, >=20/32 complete pairs, >=20 correct in
each class and >=8 additional correct vs matched CE. Also report
margin contrast, both endpoint changes, token/latency, exact solver
64/64 and constant 32/64. One seed, no retention/promotion. If negative
stop further 135M weight experiments absent a new discriminant; consider
other model family or learned structured encoder with separate
neural-vs-symbolic evaluation. No paid APIs, no main change, no retry.
