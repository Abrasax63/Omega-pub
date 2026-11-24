# TRANSFER-HYBRID01 — reusable exact memory with conserved fallback
Freeze before implementation. Six conditional queries per graph; compare
original direct reduced-graph batch, fresh hybrid, reuse hybrid,
serialized reuse hybrid. Same 49152 work-unit and 2 CPU-second total
nominal cap per batch. DP state visits and recursive visits are different
units, CPU measured including order, construction, storage/load. Same
planning in all hybrids: discover order, stable partition prefix/suffix,
compute actual reordered live width. If >12, direct for all queries.
Otherwise fresh builds per query; reuse constructs unconstrained prefix
once, immutable exact counts. Prefix build cap 4096 states and .12 CPU s;
if failure direct for all, all spent charged. DP query trial cap 4096
states and .12 CPU s (or remaining budget); if failure fall back to exact
direct reduced graph with remaining total resources, no partial answer.
Serialized reuse roundtrip canonical JSON bytes once, graph+ordered
prefix/suffix binding SHA256 and payload digest checked, no filesystem
I/O or actual persistent store claim; report bytes and time incl load.
Reject corrupted digest, wrong context, invalid state masks/weights;
trusted producer only, digest not semantic proof or authentication.
Keep earlier answers committed; no answer accepted after elapsed CPU cap.
Direct uses same exact engine and remaining global resources. No claim
fallback guarantees coverage. 24 fresh graphs, n=24,40,56,72, six prior
families 0,1,4,5,6,7, new seed 20270153; two labelings per graph, same
prefix membership and queries mapped across labels, order rediscovered;
three shuffled repeats, 288 query instances, reference by independent
reduced-graph counting as before. Report both-label exact coverage
per arm, matched full batches, all and fully referenced penalized reward,
fallback counts, work spent on abandoned trials, serialization bytes.
Primary reuse hybrid >= direct/fresh hybrid verified coverage and >=15%
lower fully referenced batch reward than both, all reward <= both,
no extra unverified unless additional verified. Secondary serialized
reuse matches in-memory counts/coverage, <=110% verified reward,
at least one useful prefix table reused. Exhaustive n<=4 conditional
queries all modes, forced width and trial cap fallback, malformed
artifact rejection, no discrepancy, no budget overrun accepted.
No learning, no external replication, no main change, paid API,
production activation or archive deletion. Training readiness remains
separate; require frozen model baseline and clean train/holdout corpus,
then explicit approval before updating weights.
