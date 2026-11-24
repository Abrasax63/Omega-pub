# NET-DECOMP01 — exact component counting and clique compression
Freeze before code. Reuse all 89 NET-REDUCE01 cases with unchanged
generation and independent references. Add 12 fresh small random
mixed constraints (n=10,12,16; four each; some contradictions), brute
reference. Add 9 dense controls, n=24,64,128, each disjoint two
cliques, two cliques sharing one vertex (vertex 0), complete bipartite.
OR=1 relations with seeded coordinate flips, same logical structure.
Independent counts via formulas for independent sets: disjoint
cliques of sizes a,b: (a+1)(b+1); overlapping cliques sizes a,b
including shared vertex: ab+1; bipartite: 2^a+2^b-1.
Pinned count for original x0=1 obtained from conditional analytic
counts with flip correction. Total 110 cases.
Compare existing full reduction+min-fill (same 65536 scope cap),
same with fallback exact component DPLL counting and memoization,
same with fallback plus clique compression. Identical fallback
branch choice (max degree, tie smallest variable), unit propagation,
free-variable multiplicity, exact component multiplication and memo.
Clique shortcut only if every variable has consistent literal
polarity and all distinct pairs occur exactly once; count n+1.
No heuristic approximate count. Max 4096 recursive visits per count
query, max 4096 memo entries and 250000 stored clause slots; skip
cache inserts beyond cap, abort visits without a guessed result.
Not a global RAM/time cap. Measure end-to-end time, fallback calls,
visits, cache hits, component splits, clique hits. Same exact/pinned
counts, no false forced bit. Primary: recover all prior exact results
and three previously unresolved complete OR cases, all 9 structured
dense controls, all completed results agree with independent reference.
Clique shortcut retained only as a restricted optimization if no
correctness regressions and fewer visits on clique cases; compare
against DPLL without shortcut, no universal speed claim. Include
mixed small controls against independent brute. No main changes,
paid API, neural training or autonomous discovery claim.
