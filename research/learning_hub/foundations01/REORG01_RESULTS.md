# REORG01 — reversible switching works, progress gate fails

Preregistration 8e508dc33e53a49f66b6ce3d701c4973b2526d34.
Implementation 77c4c6b70418e144992731ab57c012e4501c5d80.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45474700575.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

32 fresh graphs, 24 independent references, 8 reference limits.
All six tested arms: 24 verified, 6 unverified, 2 unresolved.
No count discrepancy detected. Three randomized repeats.
380 exhaustive checks, 2 forced fallback and 2 fail-closed checks passed.
Common original-mask graph representation and 8192 visit / .8 CPU s cap
for resumable arms; CPU timer not strict hardware quota.

| Arm | All reward | Verified reward | All CPU s |
|---|---:|---:|---:|
| Direct resumable |5.157829|0.477334|2.525627|
| Direct native |5.131492|0.464192|2.504773|
| Partition shared |4.680137|0.431925|2.144355|
| Fixed hybrid shared |5.077708|0.447285|2.463510|
| Fixed hybrid private |5.164006|0.509932|2.527605|
| Adaptive hybrid |5.106770|0.476358|2.484830|
| Retrospective oracle |4.665929|0.418345|2.128564|

Reward = wall + .25*CPU + 1 if unresolved; sums of per-case medians.
Primary FAIL: adaptive gain 0.20% vs direct resumable, 10.29% worse
than partition; no switches on independently verified completed tasks.
Secondary FAIL: fixed shared verified reward 12.29% below private,
below predeclared 15% threshold. Four verified cases with cross hits.
First-repeat fixed shared: 10 switches, 6 fallbacks, 4 partition
successes, 1690 cross-worker cache hits, 39 duplicate completions,
5258 unfinished-leaf visits at abandonment. Private: 10 switches,
7 fallbacks, 3 partition successes, 5985 unfinished-leaf visits.
Adaptive: 5 switches, 4 fallbacks, 1 partition success, 959 cross
hits, 23 duplicate completions; none on independently verified
completed tasks. Cross-hit totals include leaf-to-leaf reuse, not
only information transferred from direct to partition. No claim that
all tentative leaf states survive fallback. Direct stack survives;
completed exact memo survives in shared mode. Duplicate completions
checked for equality, not eliminated. No verified coverage gain.

Partition-only shared is strongest tested fixed method by reward;
retrospective oracle only ~3.14% verified reward improvement over it.
This limits upside of selecting among current arms on this cohort.
Do not retune the threshold against this holdout or promote hybrid.
Next: test genuine repartition of pending dependency graph rather
than competing root decompositions, with unique job ownership and
no abandoned subtree work; compare against partition-only shared
and direct under identical budgets, on different problem families.
No learned scheduling, physical parallelism, main change, paid API,
archive deletion or production integration.
