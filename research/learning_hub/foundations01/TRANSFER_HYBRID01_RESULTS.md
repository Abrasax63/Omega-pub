# TRANSFER-HYBRID01 — coverage restored relative to direct; serialization gate passes

Preregistration 4362ab96656198661e5403cb9f116c9bcae3515f.
Implementation e85f48169d8cc633e6277557c0f80d5325b68f18.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45482083905.
Results inspected in CI logs, artifact metadata retrieved, not independently replayed.

24 fresh synthetic graphs, six families, two labelings each, six
queries per labeling, three shuffled repetitions, four arms:
576 batch executions, 288 distinct query instances per arm.
238 independently referenced instances, 38 fully referenced batches.
4660 exhaustive conditioned checks, forced width and trial fallback,
cap failure, five malformed/context-invalid artifact rejection tests
passed. No completed-count discrepancy detected.

| Arm | Verified | Unverified | Unresolved | All reward | Fully referenced batch reward |
|---|---:|---:|---:|---:|---:|
| Direct reduced graph |236|34|18|33.446934|3.026271|
| Fresh hybrid |236|34|18|32.380610|1.948758|
| Reuse hybrid |236|34|18|32.366757|1.943698|
| Serialized reuse hybrid |236|34|18|32.371607|1.946475|

Reward = wall+.25*CPU+1 per unresolved query, sum of batch medians.
Primary FAIL: reuse reduces fully referenced reward 35.77% vs direct
but only .26% vs fresh hybrid, below 15% gate. Equal coverage, not
all queries solved: two referenced instances and 16 unreferenced
instances unresolved in each arm. All reward -3.23% vs direct.
Secondary PASS: serialized coverage differences zero, exact completed
counts agree, verified reward +.14% vs in-memory reuse, 143 reused
queries in first-repetition totals. 135/144 underlying queries solved
on both labelings, 118/119 referenced underlying queries solved on both,
same all arms. No claim runtime/order invariance.
First repetition: 22/48 width fallbacks, 113 fallback query attempts,
143 DP answers per hybrid. No failed DP trials on this cohort; forced
fallback tested separately. Reuse work 205334 vs fresh 222235
(-7.61%, mixed DP-state and recursive-visit units); DP-specific
prefix+query work 23662 vs fresh 40344 (-41.35%).
Serialized table total 7894 bytes over 26 eligible first-repeat
batches, aggregate serialization CPU .003910 s. In-memory JSON
roundtrip, not disk I/O, persistent store, cross-graph reuse or
cryptographic authentication. Digest/context checks do not prove
mathematical table contents; trusted producer only.
Nominal batch 49152 work units and 2 CPU seconds; units differ,
process timer not hard OS quota; no independent external replication.
Same author/synthetic cohort, prefix membership held across
relabellings. No neural training, main change, activation or deletion.

Training audit: PR #251 remains draft, no current training authorized.
Existing SFT01 infrastructure and Python repair corpus (62 train/12
holdout) are for a different domain; do not treat those examples or
these exact solver traces as a qualified representation-learning
corpus. MEMBERSHIP_SFT01_RESULTS.md reports a real 256-update LoRA
whose 128 evaluation answers are all No, no preregistered gain.
No new frozen-model baseline or disjoint qualified representation
corpus established here. General training NO-GO; prepare a scoped
pilot on exact boundary-state equivalence/conditional transfer with
balanced positive/negative pairs, disjoint graph-isomorphism and
family splits, frozen-model baseline, and explicit approval before
any weight update. Next discriminant: repeated queries per table and
adaptive query-specific resource allocation, compare against strong
fresh hybrid; do not expand the storage layer absent evidence.
