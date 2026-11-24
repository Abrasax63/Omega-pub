# TRANSFER-REUSE01 — exact conditional reuse, global utility gates fail

Preregistration 637e5f74c8d274ab5bb5a5791288214baccfcc28.
Implementation 98b6f1e4ead1215641803901c70784dd4a13b1fd.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45481616284.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

18 fresh synthetic graphs in six families, two labelings each,
six queries per labeling, three shuffled repetitions, 324 batch
executions. 216 query instances, 192 independently referenced
(30 batches with all six references), 24 without reference.
3495 exhaustive conditioned checks and budget failure test passed.
No disagreement among completed results or with available reference.
All 108 distinct mathematical queries had completed answers on
both labelings through direct; the logged relabel_consistent_queries
counter alone only counts queries with at least one answer, not
two-label coverage of each transfer arm. Cut membership is held
fixed across relabeling; order recomputed within its sides.
Prefix table is computed without query constraints and checked
unchanged after each completed suffix traversal. Query construction
itself uses the original order. No claim of independent blind test.

| Arm | Verified | Unverified | Unresolved | All reward | Fully referenced batch reward |
|---|---:|---:|---:|---:|---:|
| Direct reduced graph |192|24|0|4.309684|1.137456|
| Fresh compact traversal |179|7|30|30.253502|8.113102|
| Reusable prefix table |185|9|22|22.232185|4.093554|

Reward = wall+.25*CPU+1 per unresolved query, sum of medians.
Primary FAIL: reuse cuts fully referenced batch reward 49.54% vs
fresh, but is 259.89% higher than direct and loses seven verified
answers vs direct. Secondary FAIL: first-repeat global state work
406424 vs 469803 (-13.49%), below 25% threshold; 28 strict fully
verified batches. Matched 28 fully referenced batches where every
arm completes: reuse .043607 vs fresh .065292 (-33.21%) vs direct
.796445 (-94.52%). This selected subset is descriptive, not the
global utility result. Reuse is valuable where representation
fits, but wide frontiers exhaust work budget and lose coverage.
Global 49152 work units per six-query batch, nominal 2 CPU seconds;
DP states and recursive visits differ. No CPU comparison conditional
on equal work units; no physical RAM measurement, no cross-graph
storage. Reference reduced-graph computation shares the elementary
conditioning identity, with separate counting algorithms.
No neural training, no main change, paid API, activation or deletion.

Next discriminant: hybrid reusable batch with preconstruction width
gate, matched direct fallback and optional per-query fallback with
remaining conserved budget; include table storage and load cost,
fresh graphs and adversarial widths. Compare reuse hybrid with
fresh hybrid under identical planning, not against pure DP alone.
Training readiness remains NO-GO for a general campaign; a scoped
pilot requires a clean dataset of verified representation-selection
or construction examples, disjoint held-out tests and a real frozen
model baseline, explicit approval before training.
