# MORPH-DAG01 — evolve a single dependency graph without restarting
Freeze before implementation. One original-mask job registry, exact local
specialist engines (4,8,512), .8 process CPU s and 8192 dependency
requests including repeats/root. NEW jobs can be expanded by binary
branching or two-vertex weighted conditioning; WAITING plans immutable,
DONE values immutable. Isolated/component reductions unchanged.
Every child strictly smaller, duplicate child masks aggregated by
integer multiplicity for conditioning. No graph restart, no orphan
pruning, no recomputation of completed jobs. DFS pending stack;
switch decomposition of future NEW jobs after 256 requests (two
vertex conditioning for connected residual >=12 vertices, max degree
>=3, else binary), after 1024 requests return to binary.
Compare fixed binary DAG, fixed two-vertex DAG (same eligibility),
morph DAG, and existing direct/partition-shared from REORG01 with
same nominal caps (requests vs visits, note accounting differences).
This changes expansion of pending jobs, not algebraic rewrite of
already WAITING plans; no multicore or learned policy.
32 fresh graphs seed 20270131 n=20,36,56,72: tree, cycle with chords,
sparse random, dense random, complete multipartite, hub forest,
two communities, and grid with random extra edges (new family,
reference through generic stronger_reference using family index 7).
Three randomized repetitions; reference from RESOURCE-LEARN01.
Reward wall+.25*CPU+1 if unresolved, sum per-case medians.
Primary: morph >= verified coverage of best fixed DAG and direct and
partition, >=15% lower verified reward than best fixed DAG AND best
existing arm, <= best all-case reward of those controls, no extra
unverified unless more verified completions; at least one verified
completed case using both decomposition types. Safety: no duplicate
expansions/completions, no orphan jobs, every completed root has all
reachable dependencies resolved; zero count disagreements.
Tests exhaustive n<=4 all DAG modes; forced morph at low thresholds
with eligibility m>=4 on 12-cycle, all counts match reference;
bad dependency and duplicate completion rejected; budget exhaustion
fails closed. Audit shared weighted children, count reused jobs,
new/old plans, uncompleted jobs and CPU. No external blind, coarse
timing; no paid API, main change, activation, or deletion.
