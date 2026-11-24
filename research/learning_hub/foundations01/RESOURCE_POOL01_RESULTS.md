# RESOURCE-POOL01 — transferable budget passes; scheduler advantage fails

Preregistration cf8cb7b9829d34b052d38c1ae3151dd2f0829964.
Implementation e28db96f775d8eb43251ab5bd0c69273937e0cde.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45473999767.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

32 fresh graphs, 24 independent references (12 conditioned leaf DP,
4 bitset, 4 multipartite formula, 3 branching, 1 complement cliques),
8 reference limits. Three shuffled repeats per arm, median costs.
Global cap 8192 visits and .8 process CPU seconds; CPU timer is not
a strict hardware quota. Static arms partition visit budgets, not CPU.
257 unique frontier tasks across cohort, identical partition arms.
No wrong referenced result or disagreement among completed arms.
76 exhaustive frontier and fail-closed checks; 380 resumable solver
checks; quantum 1 vs 64 deterministic suspension test and exhausted
budget test passed.

| Arm | Verified | Unverified | Unresolved | CPU s | Wall s | All reward | Verified reward |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct resumable |24|6|2|2.428851|2.430416|5.037690|0.455587|
| Direct native |24|6|2|2.418867|2.419304|5.024071|0.446250|
| Equal shares |22|4|6|1.459755|1.459239|7.824207|2.227133|
| Size weighted |23|5|4|1.798947|1.804186|6.254269|1.314685|
| Round robin pooled |24|6|2|2.000440|2.002231|4.502570|0.421995|
| Sequential pooled |24|6|2|2.351906|2.351930|4.940161|0.418946|

Reward = wall + .25*CPU + 1 if unresolved, summed per-case medians.
Primary PASS: verified reward 67.90% below weighted static; one
independently verified recovery where both static shares failed
(n=72 dense graph), also solved by both direct controls. All-case
reward lower than weighted. No novel capability beyond direct.
First-repeat round robin: 549 resumptions, 41359 visits, 250/257
leaf tasks completed; equal: 34687 visits, 243 completed; weighted:
37504 visits, 243 completed. Extra visits buy coverage; no restart.
Secondary scheduling gate FAIL: round robin verified reward about
0.73% higher than sequential pooled. On all 32 cases round robin
reward about 8.86% lower than sequential pooled, but does not pass
the prespecified verified criterion. Against direct native, all-case
reward 10.38% lower and verified reward 5.44% lower; not a separate
preregistered superiority gate. 22 jointly completed verified cases:
round robin reward .0419635 vs direct native .0361807 (about 16%
higher). Most benefit lies in difficult cases, not simple ones.
Retrospective oracle reward 4.168047 all and .403772 verified;
not deployable. Eight graphs lack independent reference.
No training of a scheduler, no actual multicore execution, no
shared internal memo across frontier leaves, no general runtime
integration. No main change, paid API, promotion or deletion.

Next discriminant: preserve pooled budgets, compare cheap direct
probe with resumable fallback to partition on fresh graphs under
one ledger, including cost of abandoned partial work. Test fixed
threshold and simple progress-sensitive policy; preserve exact
verified coverage, compare against direct and sequential pooled.
