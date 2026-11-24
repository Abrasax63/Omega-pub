# ARCH-SWITCH01 — mid-resolution switching: one new exact completion, overhead on easy tasks

Preregistration bbe9f024c050c467d1b857a9b758158c8f28eee3.
Implementation a40d718b900fe5f3f346e46c953c016f1f1c4c28.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45457744458.
Results verified in job logs, not independent replay of downloaded artifact.

40 graphs, eight families, four engines, three repetitions (480 solves).
35 independent references: 16 bitset, 9 conditioned leaf DP, 7 branching,
3 multipartite formula. Five reference limits. No disagreement on any
completed counts, including all independently referenced completions.

| Engine | Verified | Unverified | Unresolved | Verified capped CPU seconds | All capped CPU seconds |
|---|---:|---:|---:|---:|---:|
| Fixed branch |34|3|3|0.523990097|1.542981002|
| Fixed elimination width <=3 |20|0|20|7.526153840|10.026153840|
| Root-only selection |34|3|3|0.530170977|1.550604928|
| Dynamic residual switching |35|3|2|0.303258435|1.337257926|

Primary gate PASS: dynamic reduces verified capped cost 42.13% vs
best static branch, preserves all verified completions and adds one
dense random n=64 exact completion (median 0.212975s versus all three
static engines failing). Retrospective per-case static oracle verified
34, capped cost 0.521132828s. 20 verified completed cases have a
successful depth>0 dispatch. Dynamic first-repetition totals (including
unresolved cases): 2289 residual dispatches, 6410 recursive visits,
718167 factor lookups, 4455 structural and 3111 elimination probes;
fixed branch 21773 visits. These units must not be added or equated.

Critical caveat: on 34 jointly verified completed cases, dynamic
0.090283143s vs fixed branch 0.023990097s and root 0.030170977s
(about 3.76x branch cost). The primary gain is driven by the single
additional difficult completion and the predeclared failure penalty,
not a general speedup. All-case capped gain vs branch 13.33%.
CPU measurements for very short tasks are coarse; some zero medians.
Three repeats show same general aggregate outcome, not independent
replications. Fixed elimination width cap 3 is restrictive; this
does not establish superiority to stronger general-purpose solvers.
The switch dispatch is hand-coded; no autonomous discovery,
learning, architecture rewriting or whole Omega runtime integration.

Next decisive control: adaptive switch gating / budget-aware dispatch
against fixed branch and a strong root-only baseline with wider
elimination where feasible. Require preserving difficult completion
while reducing common-case overhead; fresh holdout and cost of probes
included. Keep existing prototype experimental. No paid API,
main modification, or scientific archive deletion.
