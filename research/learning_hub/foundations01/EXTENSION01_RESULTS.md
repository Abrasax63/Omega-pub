# EXTENSION01 — negative result and open-world certification boundary
Prospective protocol 1a58532fca3494fd1c9d5f25c6628afe23c28155.
Actual local Python / torch 2.10.0+cpu run on original frozen checkpoints
from COMPOSITION01 artifact 14924271795. Original archive SHA and each
weight hash verified. No gradient or weight update.
Source extension01.py SHA256
6ce325e92ca5f4cdef5a080c641baf37160b0cc83f3e44ff6940ab4b3515928e;
results.json SHA256
649ac1a27b6197f7855d9d61c4b6a0829693c77bd2250d5f5a0b758df2718da9.
Source and raw results retained as local downloadable artifacts,
not uploaded to this commit; independent GitHub replication pending.
584 truth functions at minimal cost <=5; 6709 at cost <=7.
Independent full enumeration including nonminimal subexpressions confirms
all functions and minimal costs. All 576 search traces audited with
ordinary sets instead of bitsets, including evidence replay, transition,
remaining count, confirmation count, accepted rule and graph score.
All three seeds yield identical summary; zero neural signature errors.
Same 48 target rules and graph sets across seeds, not independent samples.

Per seed, 12 tasks per stratum. Cells exact accepted / false accepted / abstain:
| arm | IN | EXT | FAR | NEAR |
|---|---|---|---|---|
| fixed cost5 |12/0/0|0/5/7|0/1/11|0/10/2|
| adaptive cost5->7 |12/0/0|3/5/4|0/5/7|0/10/2|
| expanded cost7 |5/0/7|3/0/9|0/1/11|0/3/9|
| adaptive exact |12/0/0|3/5/4|0/5/7|0/10/2|

Totals exact/false/abstain: fixed 12/16/20; adaptive 15/20/13;
expanded 8/4/36. Adaptive and adaptive exact identical. Preregistered
PASS false for every seed. Adaptive correctly recovers 3/12 EXT,
below >=8; accepts 5/12 FAR and 10/12 NEAR falsely, above <=2.
Adaptive extends for 7 EXT, 11 FAR, 2 NEAR, zero IN. Search work
(candidate-check equivalents, not runtime or actual bitset operations)
fixed 3,597,800, adaptive 3,872,606, expanded 41,361,134.
An accepted NEAR example: teacher FLIP(AND(OR(x0,x2),x3),motif=14);
chosen AND(OR(x0,x2),x3); 252/256 fresh graph predictions correct,
yet wrong function. Queried motifs 38,21,63,15,28,8,11,44,58,34,53,61,0,22,4,2.
A high test accuracy is not proof of exact rule identification.
No neural advantage relative to exact lookup, no invention of operators.

## Mathematical boundary (proved)
Assume a deterministic arbitrary Boolean teacher on six bits, with only
pointwise label access and no restriction on the teacher's function.
There are 64 motifs. After k distinct consistent queries, exactly
2^(64-k) truth tables match those observations. For any unqueried motif,
flipping its bit in any consistent function yields another consistent
function. Adaptive selection does not change the argument because the
alternative returns identical labels on the complete observed transcript.
Consequently 64 distinct labels are necessary in the worst case and
sufficient to identify the truth table exactly on this finite domain.
16 labels leave 2^48 compatible unrestricted tables. Singleton in a
bounded grammar is not a certificate in the unrestricted domain.
This theorem does not apply as a lower bound to a known restricted
teacher class, or to richer observations than pointwise labels.

## Decision
Reject automatic certification from singleton + four checks in open world.
Separate conditional hypothesis (grammar assumption explicit), contradicted
grammar (empty version space), and exhaustive finite-domain certificate.
Do not conflate a truth-table certificate with a compact explanatory
formula, a proof of neural extraction correctness, or broader autonomy.
Keep models unchanged; the next prospective test should measure
information cost, false acceptance and abstention under conditional
vs exhaustive gates on fresh rules, including exceptions.
No main changes, no paid API, no promotion.
