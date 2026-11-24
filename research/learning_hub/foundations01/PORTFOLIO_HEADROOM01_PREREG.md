# PORTFOLIO-HEADROOM01 — measure algorithmic complementarity before learning
Freeze protocol before code. Common task: exact count of assignments to
positive binary OR constraints (independent sets of a simple graph).
No new trained selector. Compare unchanged existing engines:
A full unary/parity preprocessing + min-fill elimination (net_reduce01);
B same plus component DPLL/clique fallback (net_decomp01 incumbent);
C graph deletion branching max degree (learn_policy01).
D new bounded graph structural reduction (forest DP and complete
multipartite component formula, otherwise use C). D is a candidate
algorithm, not learned; do not attribute its gains to learning.
All methods get same 0.5 CPU-second cap per solve via Linux ITIMER_PROF,
retain existing scope/visit/cache caps (not equivalent operation budgets).
Include graph-to-constraint conversion and preprocessing in timing,
exclude generation/reference. Three repetitions, rotated shuffled arm
order, record actual CPU times, median capped loss per case (failure
cost 0.5 s); verify deterministic counts unless timeout; count successful
in >=2 repetitions as completed. No speculative answers.
48 new graphs, 8 families x 6 sizes n=12,16,20,32,48,64:
random tree, perturbed grid, sparse random, dense random, two-community,
complete multipartite, forest of trees, random near-bipartite.
Seed 20261221, permuted labels, distinct labeled graphs.
References: exhaustive bitset n<=20; independent tree DP/analytic
multipartite formulas on larger structured cases; otherwise original
independent bounded branching reference. If no reference, explicit
unverified; agreement is not certification.
Primary headroom gate: retrospectively best median capped CPU cost per
verified-reference case vs best single fixed engine chosen retrospectively
on that same subset >=15% reduction, and oracle verified completions
>= best fixed. Additionally report vs incumbent B, completion counts,
per-family wins, actual median successful times, timing sensitivity
across repetitions, reference limits. Oracle is unattainable lookahead,
NOT learning. If headroom fails, stop selector training on this
portfolio. If it passes, only justify future fresh prospective selection
test; do not promote any algorithm from this pilot. No main changes,
paid API, neural training or claim of general autonomous learning.
