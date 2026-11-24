# INTERACT02 — outcome-dependent expansion vs strong fixed designs
Prospective test of whether adaptation earns its complexity. Same 6-bit
black-box state transition as INTERACT01, nested polynomial spaces
degree 1,2,3 over GF(2). 96 fresh teachers (24 each affine, quadratic,
cubic, quartic), random dense coefficients up to degree 2 and a nonzero
top-degree term for cubic/quartic, half linearly conjugated. Seed
20261129; distinct truth tables; no teacher family provided to learner.
Fixed designs interpolate on all states of weight <= degree, with 20
disjoint random high-weight (>=4) challenge inputs; degrees 1,2,3 use
27,42,62 queries respectively. Adaptive starts at degree 1, fits using
weight <=1, tests 6 fresh high-weight states, expands to degree 2 if
contradicted; fits using additional weight-2 states, tests 6 more fresh
high-weight states if needed; expands degree 3 if contradicted, tests
8 more. All earlier validation observations must remain consistent with
current candidate. Stop early on consistent candidate, never unconditional
certification. If already contradicted at stage start, still consume
stage challenge budget for matched protocol. Maximum 62 queries for
each strategy (fixed low degree uses less); report actual per-task
and total query counts, not equal realized budgets. Shared seeded
challenge order, no teacher information. Evaluate exact truth tables
on all64, 5-step rollouts, incorrect conditional acceptance, refutation.
Primary: adaptive >= fixed cubic on exact in-family recovery, no more
incorrect conditional candidates across ALL 96, >=20% fewer total
queries, no unconditional claims. If fixed lower degree matches quality
at lower cost, prefer it. If primary fails, no promotion. Report
conditional scope and theoretical impossibility of proving arbitrary
unqueried outputs from observations alone. No model weight training,
grammar invention or main change. CPU only.
