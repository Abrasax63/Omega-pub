# ARCH-SWITCH01 — mid-resolution architecture transitions with shared residual state
Freeze before implementation. Common task exact independent-set counting
(positive binary OR constraints). Same graph bitmask representation,
component factorization, isolated vertex rule, max-degree branch,
per-task memo and 4096 recursive node cap for all branch-based arms.
Three distinct exact engines: combinatorial deletion recurrence,
structural tree DP / complete multipartite formula, algebraic
binary-factor elimination with greedy min-degree fill order and
maximum induced width 3 (decline before building factors if wider).
Compare 4 arms: fixed branching; fixed elimination (with same width
cap); root-only selection (structural or elimination at original
problem, else fixed branching); dynamic (same selection at root and
on residual subproblems, sharing memo and multiplying/summing results
in original recursion, no restart). All root and residual decisions
use identical structural checks, elimination considered only if
edge count <=2*vertices and >=4 vertices. Dynamic chooses on residual
connected components; log transitions at depth>0, sizes and method.
No learned selection; test whether mid-solve switching actually helps.
Same Linux CPU cap 0.5s per solve plus native node/width caps; three
repetitions shuffled arm order, median capped cost, failure penalty
0.5s, report completion if at least two successful runs. Measure
process time (timer resolution may be coarse), wall time descriptive,
recursive visits, factor assignments, structural calls separately;
do not add these different work units. Charge all selection probes.
40 new graphs: 8 families x n=12,18,24,40,64. Seed 20270105. Tree,
cycle with sparse chords, sparse random, dense random, complete
multipartite, forest plus one universal hub, forest plus two hubs
(with random distinct neighbors), two communities. Random label
permutation. Hub graphs intentionally favorable to structural
transitions; random and community controls. Independent refs:
exhaustive bitset n<=18; larger trees and hub forests exact by
conditioning hub states and independent leaf DP; multipartite closed
form; other graphs original independent bounded reference.
No reference => unverified even on agreement. All outputs validated
against available references; no guessed count on exhaustion.
Primary: dynamic verified completion >= root-only and fixed branch;
>=15% lower total median capped CPU cost on verified subset vs best
of root-only and fixed branch, no additional unverified outputs vs
root-only, zero count discrepancies; at least one genuine depth>0
successful switch on verified case. Also report vs retrospective
per-case best static, all costs and non-hub subgroup, matched completed
cases, time resolution caveat. No holdout tuning or promotion on
failure. Existing engines are inspiration; new common engine is a
controlled prototype, not whole Omega runtime. No main change,
paid API, neural training, or general autonomous reorganization claim.
