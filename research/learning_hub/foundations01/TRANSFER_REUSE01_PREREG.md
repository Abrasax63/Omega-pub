# TRANSFER-REUSE01 — conditional query reuse and relabeling stress
Freeze before implementation. Test whether the exact boundary vector is
useful as reusable knowledge for different questions on the SAME graph.
18 new graphs n=24,40,56, six families from TRANSFER01 (0,1,4,5,6,7),
seed 20270149. For each original graph choose first half of discovered
BFS order as prefix; choose six fixed suffix queries (unconstrained,
one inclusion, one exclusion, two inclusions, inclusion plus exclusions,
three exclusions). Same mathematical queries under one new random
relabeling (seed 20270150); discover order again but stable partition
by original prefix/suffix membership; not an invariant ordering test.
Compare direct reduced-graph fresh solve, compact fresh full traversal
per query (same discovered order and cut), cached prefix vector with
suffix-only conditioned traversal. No queries supplied to prefix
construction. Reuse prefix exactly once per batch, no persistent
cross-graph cache. Global batch 2 process CPU seconds and 49152
work units for all six queries, recursive visits vs DP state rows not
equivalent. Include planning and all query overhead, no partial count
on limits; completed prior queries retained. Direct per-query timer
remaining batch CPU, stop if exhausted. Three shuffled repetitions.
Independent reference by removing forced selected vertices and their
neighbors plus excluded vertices, then group transfer for structured
graphs, generic stronger_reference for controls; invalid inclusion
constraints exact zero. Audit every completed query across arms and
relabeling and reference where available. For primary compare batches
with all six refs known, cost wall+.25CPU+1 per unresolved query,
sum medians. Reuse must have >= verified query coverage, >=15% lower
verified-batch cost than both direct and fresh, all-batch cost <= both;
no additional unverified outputs unless additional verified coverage.
Secondary exact state-row reduction >=25% vs fresh and at least one
verified batch with strict compression. Report full/partial references,
paired cost, relabeling cost sensitivity, no novel skill or neural
learning claim. Exhaustive n<=4 forced inclusion/exclusion queries
against brute force for all methods; invalid constraints zero; cap
fail-closed; prefix immutable fingerprint; relabel equivalence of
completed answers. No external replication, main change, paid API,
training, promotion or deletion.
