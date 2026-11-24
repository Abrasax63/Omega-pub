# NET-DECOMP01 — exact component counting and restricted clique compression

Preregistration efb82d1e1bfe80ec7416f247e46ad5557b3f900d.
Implementation 15481798a01e3cb39e550628e58897314126d427.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45443744256.
Results verified from CI logs, not independent replay of the artifact.

110 cases: previous 89, twelve fresh small mixed instances and nine
structured dense instances with random literal flips. All completed counts
and pinned counts matched reference formulas or independent enumerators.

| Policy | Completed | Resource limit | UNSAT | Total measured seconds |
|---|---:|---:|---:|---:|
| Prior reduction + elimination |101|9|48|1.975365786|
| With exact component DPLL fallback |110|0|48|22.954070855|
| With DPLL and guarded clique formula |110|0|48|6.262212081|

No regression on completed base cases. The fallback recovered all nine
unresolved cases. Both fallback arms used 16 count-query fallbacks.
DPLL had 2314 recursive visits, versus 286 with the clique shortcut;
six component splits each, 19 clique recognitions in the shortcut arm.
No memo hits reported in either arm: no evidence of a benefit from caching
on this corpus. Complete OR cases used 852 vs 6 combined visits.
128-variable complete OR: 129 solutions; 13.96692 s DPLL vs 0.76382 s
with the formula. Overlapping cliques at 128 variables: 4161 solutions;
disjoint cliques: 4225. Complete bipartite 64+64 with literal flips:
36893488147419103231 solutions; approximately 2.6 s in both fallback arms.
All nine new dense cases completed, including overlapping cliques.
The preregistered correctness/completion and clique-visit criteria pass.

Clique formula applies only to a complete graph with a consistent
literal sign for every variable; it counts n+1 assignments. The general
fallback branches exactly, accounts for unconstrained variables and
multiplies disconnected component counts. No arbitrary dense tractability
claim. The benchmark primarily uses structured instances and is not a
representative random hard-CSP sample. Timings are one measured run;
baseline stops earlier on failures, so total times are not directly
comparable at equal completion. Cache benefit not demonstrated; code
retains it experimentally but do not promote it based on this test.
Visit/cache caps are not global memory or runtime limits.

Next decisive test: irregular dense mixed-sign constraints with known
exact small references and bounded larger instances; compare alternative
variable orders and a no-cache ablation. Require zero count regressions
and report abstentions. No main modification, paid API, neural training,
or autonomous learning claim.
