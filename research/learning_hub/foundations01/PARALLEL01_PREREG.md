# PARALLEL01 — actual process parallelism on a common exact partition
Freeze before implementation. Reuse ARCH-LOCAL01 fixed policy (4,8,512)
as leaf solver, CPU .5 s and 4096 visits per leaf. For each graph,
choose four highest-degree vertices (ties index), enumerate independent
assignments on them, remove chosen vertices and their neighbors.
Aggregate identical residual masks with integer multiplicity; each
unique frontier task submitted exactly once. Sum weighted exact counts.
No partial root answer if any leaf unresolved; no cross-leaf internal
memo, so overlapping internal residual calculations remain possible.
Same partition, sorted decreasing residual size then mask, same task
budgets in all arms. Compare serial in-process, persistent process pool
with 1,2,4 worker processes (actual concurrent tasks, no thread claim),
dynamic next-available dispatch by pool, and direct unpartitioned local
solver as descriptive reference only (different aggregate cap).
Measure CPU affinity, logical CPU count, cgroup CPU quota, available
topology if readable, worker PIDs, worker intervals and overlap,
per-case wall time including partition/IPC, sum worker CPU plus parent
CPU, aggregate pool startup/shutdown CPU from RUSAGE_CHILDREN, wall.
Do not infer distinct physical cores from process count. No affinity
pinning; resource quotas and scheduling can constrain gains.
20 fresh graphs: n=32,48,64,72 families 1,2,3,7 from original generator
(cycle/chords, sparse, dense, community), plus n=48 families 0,4,5,6
(tree, multipartite, hub forests), seed 20270119. Three repetitions,
arm order shuffled per rep, case order shared per rep. Per-arm pool
created once per rep, startup and teardown included in total wall and
CPU; per-case times include lazy initial startup if incurred. Fixed
leaf caps and number of leaf jobs imply same aggregate solver budget
across partition arms; worker creation/IPC extra, measure not ignore.
Independent reference from previous suite; no incorrect count or
disagreement among completed arms. Track unverified and unresolved.
Use common cases independently verified and completed by all four
partition arms for paired wall/CPU comparison, report total costs and
coverage too. Primary: 4 workers >=1.25x faster than serial and >=1.25x
faster than one-process pool on sum median paired wall, aggregate
measured paired CPU <=1.25x serial, no verified completion loss,
actual overlap between distinct worker PIDs. Report 2-worker result,
even if 4 fails. If quota <4 or insufficient paired workload, qualify.
Selftests partition identity on exhaustive n<=4 graphs, dedup
multiplicity and no partial publication, actual process execution.
No claim of learned scheduling or unique internal DAG across processes.
Same author synthetic cohort, no main change, paid API, or promotion.
