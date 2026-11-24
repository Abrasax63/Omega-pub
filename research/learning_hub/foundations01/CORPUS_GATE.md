# Corpus gate — preregistration clarification before training
No change to success thresholds or sample sizes in PREREG.md. For atomic
relation tasks only, require exactly half transitivity violations (110);
distribute the remaining half as evenly as possible among the other seven
truth motifs in lexicographic order. This reconciles balanced labels with
coverage of all eight motifs (uniform eight-way sampling would be 7:1).
Record per-motif and per-class scores; a constant false predictor is 50%
on the balanced set. Use canonical graph identity for split isolation and
canonical graph+ordered triple identity for task deduplication. Bound graph
size to 3–6 for the curator; proposer remains limited to 3–4.
The proposer never receives the hidden split; curator supplies packets only
to the offline audit. Separate oracle-supervised and self-generated training
arms, match budgets, audit each against dev and holdout; do not fill the
self-generated arm with curator examples if quotas cannot be met.
Representation-family isolation, unseen sizes, genuine proposal provenance,
training/replay integration and frozen manifests still need separate checks.
No model runs, training, or promotion authorized by this offline patch.
