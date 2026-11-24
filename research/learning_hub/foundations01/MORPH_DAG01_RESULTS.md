# MORPH-DAG01 — single evolving DAG tested; utility gate fails

Preregistration c1c2120f7e2d57fbb7dc2544968ecfd3f763f584.
Implementation d607b637fda1ea2da76655f5097abbf881c8ee22.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45475543754.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

32 fresh graphs, 21 independent references (8 conditioned leaf DP,
5 bitset, 4 multipartite formula, 3 branching, 1 complement cliques),
11 reference limits. Three randomized repeats. Every arm: 21 verified,
8 unverified, 3 unresolved. No count discrepancies detected.
228 exhaustive checks and forced morph, cap exhaustion, malformed
dependency and duplicate-completion rejection checks passed.

| Arm | All reward | Verified reward | All CPU s |
|---|---:|---:|---:|
| Fixed binary DAG |7.404615|0.592528|3.524293|
| Fixed multi DAG |7.266562|0.530679|3.413990|
| Morph DAG |7.414855|0.587369|3.530695|
| Direct resumable |7.322271|0.548989|3.455158|
| Shared partition |6.858303|0.501522|3.087543|

Reward = wall + .25*CPU + 1 if unresolved, sum of per-case medians.
Primary FAIL. Morph is 0.87% lower verified reward than binary,
10.68% higher than fixed multi, 6.99% higher than direct, 17.12%
higher than shared partition. Four independently verified completed
cases use both expansion types. First repetition: morph 27756 requests,
6136 reused requests, 21569 expansions, 21507 completions, 7011
binary and 593 multi decompositions. No repeated expansion or duplicate
completion accepted. Reachability and completeness audit on completed
roots only, skipped on three unresolved first-repeat cases per DAG arm;
no claim of atomic rollback after asynchronous CPU timeout.

Nominal cap 8192 requests/visits and .8 CPU s, but DAG requests and
recursive visits not identical units. Registry overhead included.
Fixed multi already outperforms morph on verified subset; partition
best in this cohort. No evidence of learning, multicore speedup or
rewriting established WAITING dependencies. Do not promote morph.

Next discriminant: instead of switching at predetermined request counts,
test local structural choice on the same registry (e.g. exact comparison
of candidate child overlaps, weighted child sizes and existing cached
dependencies), include feature/probe cost, compare with fixed multi and
shared partition, fresh cohort. Only pursue learning if oracle headroom
is substantial. No main change, paid API or production activation.
