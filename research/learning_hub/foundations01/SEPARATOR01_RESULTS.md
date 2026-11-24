# SEPARATOR01 — structural gain, global utility gate fails

Preregistration 1899fa9c9e2dc2220ae29c9f360ac531f69828b7.
Implementation a2a966e7d736fdb9ebb906485bc794b807467484.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45477119611.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

32 synthetic graphs, 20 ordered-block structured graphs and 12 random
controls. 27 independent references: 20 group transfer DP, 6 branching,
1 complement cliques; 5 reference limits. Three shuffled repetitions.
All arms solve all 27 reference cases, no detected completed-count
discrepancies. 228 exhaustive solver checks, 76 transfer checks,
332 forced separator identities; eligibility and fail-closed tests pass.
The solver receives no group labels. Reference DP uses known group
ordering. Same nominal .8 process CPU seconds / 8192 recursive visits,
not identical work units and not strict hardware quota.

| Arm | Verified | Unverified | Unresolved | All reward | Verified reward | Structured reward | Control verified reward |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct |27|3|2|5.730029|1.008176|.394961|.613215|
| Separator conditioning |27|2|3|5.570950|1.005924|.244213|.761710|
| Separator factorization |27|2|3|5.993440|.975956|.224868|.751087|
| Shared partition |27|3|2|5.338650|.919187|.354002|.565185|

Reward = wall+.25*CPU+1 if unresolved, summed per-case medians.
Primary FAIL: factorized verified reward -3.20% vs direct, +6.18%
vs shared partition; all-case reward +12.26% vs partition.
Secondary FAIL: factorized verified reward -2.98% vs conditioning,
below 15% threshold. No novel verified recovery. 27 verified cases
use separators. On structured subset only, factorization reduces
reward by 43.07% vs direct and 36.48% vs partition, 7.92% vs conditioning.
Structured first-repeat visits 7685 vs direct 9256 (-16.97%).
Structured factor reuse 690/2138 factor requests; total first repeat
15259/32959 factor requests. Control verified reward +22.48% vs direct
and +32.89% vs partition. Control subset has 3076 searches and
21149 separator probes for factor arm vs 293 searches and 2655
probes on structured subset. These counts show search overhead and
different search trajectories, not independent causal attribution.
One additional unresolved unverified control relative to partition.

The structured cohort deliberately favors small separators; subgroup
benefit is descriptive, not the preregistered global pass. No claim of
general superiority or learned selection. Direct baseline computes all
connected components before using the first in binary recurrence; older
direct solver finds first only. Shared partition is a separate control.
Do not promote globally or retune on this cohort. Next discriminant:
bounded separator discovery with root structural evidence and a
shared failed-probe budget, no repeated unrestricted searches; compare
root-only vs capped recursive vs no-separator and shared partition
on fresh structured and negative controls; report subgroup and global
costs. No main change, paid API, activation or archive deletion.
