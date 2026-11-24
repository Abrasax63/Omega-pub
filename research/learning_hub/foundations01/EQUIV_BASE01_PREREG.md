# EQUIV-BASE01 — frozen corpus and real untrained-model baseline
No weight updates. Scope: two feasible past independent sets A,B have
identical admissible future independent sets iff their future blocked
vertex masks are equal (singletons distinguish unequal masks).
Paired positive/negative examples on same graph and same A, both
alternatives distinct from A, equal cardinality 2. Graph input only,
no computed blocked masks or answer in questions. Two views: edge
list and adjacency matrix; random vertex ordering and vertex names.
12 training generator configurations: cross-edge probabilities
.25,.45,.65 x internal past/future probabilities .0,.25 (2x2).
Four graphs per configuration, 96 labeled examples. Dev two distinct
configurations (cross .35,.55; internal .10,.35), four graphs each,
16 examples. Holdout four distinct configurations (cross .2,.4,.6,.8,
internal .15,.40), eight graphs each, 64 examples. Train n=6..8
(past >=4); dev n=9; holdout n=10..11. Thus no cross-split graph
isomorphism even ignoring vertex partition; exact NetworkX
isomorphism dedup within each split, including same n. Family labels
are generator configurations, not 12 distinct mathematical skills.
Rejection sample until feasible pair exists; report attempts. Independent
truth via exhaustive feasible future subsets, compare mask equality.
Require at least 24 examples across 12 train configs, balanced labels,
unique graph and pair IDs, no label leakage in question payload, exact
reference agreement. Freeze dataset SHA256 before inference in
separate job. Train/dev artifacts separate from public holdout questions
and evaluation labels; inference downloads questions only. Public
repo means not an externally secret holdout. Real baseline pinned
SmolLM2-135M-Instruct revision ee72e5415c002e8fc0566a191a07c0b2b708875a,
CPU float32, deterministic, no tool or demonstration, 8 generated tokens.
Record exact raw output, strict Yes/No, candidate next-token
probability if both single-token, paired correctness, per-class,
both-view accuracy, constant-response collapse, hashes, tokens/time.
Scorer checks all 128 records and prompt hashes. Baselines constant
(50%, zero both-pair), exact oracle 100%. No training or automatic GO.
Baseline consumes holdout for diagnostics; any later training
evaluation must freeze fresh unseen families/sizes, not reuse this
holdout for promotion. Pilot design later must compare frozen model,
matched training controls, paired contrast and retention, with explicit
approval before updating weights. Same author, synthetic source,
no external replication, no main change, paid API or activation.
