# TRANSFER01 — exact boundary quotient and hybrid utility gates pass

Preregistration 8165d1ce60f032115f454247c7c93a3eb6a775ca.
Implementation a9d0a002600da78b92f1906c212de6de45e5e906.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45480260971.
Artifact 14960123659, SHA-256
100c98baaf8bc0fb0ae93b5325d0c79397acc3cb46ca95e58ac1c2a5fd4204d8.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

48 fresh synthetic graphs, 43 independently computed references
(24 group transfer, 4 apex transfer, 5 branch, 2 complement cliques,
4 wide transfer, 2 tree-block DP, 2 cycle transfer); 5 reference limits.
Three shuffled repetitions, 864 solver runs. 456 exhaustive checks,
253 conditional prefix queries against brute force, 7 fixtures with
strict quotient compression, cap failure and width fallback tests
passed. Conditional tests actually cover n<=4, not an additional
n=5,6 cohort. No completed-count discrepancy detected.

| Arm | Verified | Unverified | Unresolved | All reward | Verified reward |
|---|---:|---:|---:|---:|---:|
| Explicit frontier |35|0|13|13.171509|8.122581|
| Compact blocked future |38|1|9|9.145173|5.096170|
| Compact hybrid |43|3|2|5.161719|.469500|
| Min-fill elimination hybrid |43|3|2|5.481181|.783935|
| Shared partition |43|3|2|6.396243|2.526417|
| Direct |43|3|2|7.304398|2.602830|

Reward = wall+.25*CPU+1 if unresolved, sum of medians.
Primary PASS: hybrid verified reward -81.96% vs direct, -81.42%
vs partition, -40.11% vs min-fill hybrid. All-case reward -5.83%
vs min-fill hybrid, -19.30% vs partition. Equal verified/unverified
coverage. No verified completion unavailable to all controls.
Secondary PASS: compact verified reward -37.26% vs explicit,
38 vs 35 verified completions; 7 strict quotient fixtures.
On 35 common verified completions, compact .030429 vs explicit
.046449 (-34.49%); hybrid .032463, elimination .303580,
partition 1.423548, direct 1.570343. Joint subset descriptive.
Pure compact can fail on wide/dense graphs. Hybrid chooses fallback
before table construction on 14/48 cases, 9/43 verified; 34 verified
cases use transfer without fallback. Elimination fallback 10/48.
First-repeat explicit/compact work 132110/103649 states over all
cases (different completion counts); hybrid 14305 state rows and
25328 recursive fallback visits. Do not equate work units.
On 72-vertex width-9 strip, hybrid reward .004999 vs direct
.588785, partition .703837, min-fill .029829; pure explicit hits
work cap. Independent ordered-group reference agrees. This is
one synthetic case, not a universal speedup.
Hybrid has no coverage advantage over the strongest controls but
cost gain meets preregistered gate.

Exact invariant: two feasible past assignments forbidding the same
future vertices have identical admissible future independent sets.
Summing multiplicities is lossless for this objective; not equivalence
for arbitrary queries about the past. Prefix table answers multiple
fixed feasible suffix queries in small tests. No cross-graph transfer
or learned policy demonstrated. The order is discovered from BFS,
threshold 12 is hand-coded; no group labels provided to solver.
Min-fill baseline is a bounded Python implementation, not a claim
of superiority to optimized external solvers. CPU timer .8 s is not
a hard OS quota; 8192 cap units differ by engine.
Same author and synthetic generator; no external replication.
Retrospective all-arm oracle verified .414975 vs hybrid .469500
(11.61% headroom). All reward oracle 3.044584 includes favorable
failed-run timings, not a practical solver. No main change, paid API,
production activation or deletion.

Next: stress exact quotient across graph relabelings, wider and
adversarial boundaries, multiple conditioned queries and memory
use; compare fixed ordering and frontier ordering under matched CPU
budgets. Evaluate reusable relation storage separately from single
count speed, and avoid learning a selector unless further held-out
headroom is demonstrated.
