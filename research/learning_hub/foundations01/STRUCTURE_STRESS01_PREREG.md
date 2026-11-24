# STRUCTURE-STRESS01 — prospective adversarial audit of frozen learned weights
No training, no selection, no model calls. Use original COMPOSITION01 artifact
14924271795, run 45402569813, verify weight hashes from results.json.
Test all three frozen composition checkpoints; report each independently.
Fresh seed 20261203; 64 complete motif families per regime, 512 graphs.
Regimes: n3 minimal, n8 sparse background (.0), n8 dense background (1.0),
n12 intermediate background (.5), and n12 with targeted reverse-edge
distractors (force yx,zy,zx if not queried). Query distinct endpoints.
For each regime test both output bits against direct independent membership
oracle; also test membership logits separately on all three queries.
For each original graph generate label permutation (global bijection of
12 identifiers), edge-order reversal, and combined permutation/reversal.
Compare exact decisions and max absolute logit differences; all expected
labels unchanged. Record baseline and transformed correctness per motif,
full-family correctness and minimal counterexample (complete edge list,
query, expected and actual), including any membership failure.
Test padding invariance (append 17 masked positions with arbitrary
valid identifiers); compare decisions and logit differences.
Separate exhaustive boundary diagnostic for all 512 directed graphs
with loops on fixed three vertices and all 6 ordered distinct triples
(3072 cases per checkpoint); no assumption of independence.
Primary pass: no exact decision error or transform decision flip on any
checkpoint in above tests. Logit differences are diagnostic only;
label invariance is not necessarily logit invariance. No retraining,
no repair after inspecting tests, no main changes, no promotion.
Vocabulary 12 fixed, distinct triple only; this does not prove unbounded
size, natural language interpretation or autonomous learning.
