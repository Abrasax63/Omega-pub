# PARTITION01 — unique residual jobs and specialist dispatch
Freeze before implementation. Reuse exact independent-set counting,
same graph bitmask, component split, isolated rule, max-degree
branching, structural and width-3 elimination engines. One job per
residual mask; states NEW, WAITING, DONE; dependencies strictly smaller
by population count; duplicate requests attach to existing job.
Depth-first ready scheduling, preserve branch child order; explicit
sum/product/scale recomposition, no tentative counts published.
Two DAG arms: homogeneous branch only; specialist with local
policy (4,8,512) (delay measured in cumulative dependency requests).
Compare to synchronous branch, synchronous fixed local, synchronous
delay512 and prior cooperative shared root race. Identical CPU cap
.5 sec, 4096 requests (including duplicate requests, root and empty
state) or existing visit cap; no extra hardware, no threads. DAG
nodes <=4096, no repeated expansion. Charge registry and scheduling
costs. Three repetitions shuffled; median capped CPU, failure .5.
40 fresh graphs n=16,24,40,56,72 eight previous families, seed
20270117. Independent references as before, limits separated.
Audit exact results, dependency ranks, recomposition, duplicate
completion rejection and fail closed on exhausted budget.
Targeted tests: empty graph, disconnected, diamond/repeated child
dependency, malformed dependency, duplicate completion, budget limit;
explicitly report if no diamond in real cohort. Metrics: unique
expansions, dependency requests, repeated requests, duplicate
completions, engine dispatches, maximum frontier/stack, DAG nodes,
CPU, verified/unverified/unresolved. Distinguish avoided duplicate
requests from counterfactual savings; shared root race may differ in
search path. Safety gate zero duplicate DAG completions and zero
wrong verified results, all invariants checked. Utility gate
specialist DAG >= shared race and fixed local verified completions,
>=15% lower verified capped CPU cost than shared race AND fixed local,
all-case cost <= fixed local, no additional unverified outputs vs
fixed local unless additional verified coverage. Report against
homogeneous DAG and simple branch even if failed. No new learned
policy, true multicore, general solver or runtime integration.
No main change, deletion or paid API. Same generator, coarse timing.
