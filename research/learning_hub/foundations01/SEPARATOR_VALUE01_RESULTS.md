# SEPARATOR-VALUE01 — exact cheap cuts, cost proxy not validated

Preregistration a5a6bd24c4ca11845e0620172bbca70e1d9bf52b.
Implementation c0b567c78c16d7b73dfd14a464ea7f2058b5853c.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45479362055.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

40 fresh synthetic graphs across ten families. 35 independent references:
24 ordered group transfer, 4 apex transfer, 5 branch, 2 complement
cliques; 5 reference limits. Three shuffled repetitions, 600 solver runs.
All arms 35 verified / 3 unverified / 2 unresolved, no detected count
discrepancy. 380 exhaustive solver checks, 150 BFS cut identities,
positive/negative gate and fail-closed checks passed.

| Arm | All reward | Verified reward | Structured 20 | Random verified 7 | New 8 |
|---|---:|---:|---:|---:|---:|
| Direct |6.289332|1.522212|.352251|.611020|.558941|
| Shared partition |5.907362|1.253265|.289332|.568149|.395785|
| Open128 |5.995131|1.221074|.144880|.617904|.458290|
| Cheap BFS sides |5.963235|1.189087|.130219|.613248|.445619|
| Value-gated |6.024295|1.231983|.144321|.615019|.472643|

Reward = wall+.25*CPU+1 if unresolved, summed case medians.
Primary FAIL: value-gated reward -19.07% vs direct, -1.70% vs
partition, +.89% vs open128, +3.61% vs cheap cut on verified cases.
Secondary FAIL: cheap cut -2.62% vs open128, below 15% gate.
Cheap cut has lowest verified reward, partition lowest all-case
reward. Cheap cut -5.12% verified vs partition,
+0.95% all. No novel verified recovery.
Structured subgroup cheap cut -54.99% vs partition,
-63.03% vs direct. Random verified subset
+7.94% vs partition; new 8 +12.59%.
In particular the new width-8 chain family is slower than partition;
do not infer utility just from the existence of structure.

First-repetition cheap cut eliminates all 1693 candidate component
traversals of open128 (0 vs 1693) but still performs 1438 searches,
80570 BFS vertex visits, 1911 candidate examinations, 485 accepted
cuts. This is a change to the algorithm, not elimination of all
graph traversals; ordinary connected-component checks remain.
Value gate rejects 364 of 645 evaluated cuts and reduces recursive
visits 7.31% vs cheap cut but verified reward worsens.
Gate rejection is proxy-based, not measured counterfactual utility.
No learned decision rule. Exact BFS property: adjacent vertices have
distance difference <=1 from the same BFS origin, so prefix and suffix
separated by a whole layer have no direct edge. Factors may be
disconnected; conditional count identity remains valid.

Retrospective all-arm oracle verified 1.072521 vs cheap 1.189087,
9.80% headroom; fixed oracle 1.081078 vs best fixed
open128 1.221074 (11.46%). Neither reaches 15% on this cohort.
All-case oracle 5.726614 vs partition 5.907362 (~3.06% headroom).
Stop adding heuristic selector layers on this portfolio. Preserve
cheap exact cut as experimental specialist. Next distinct direction:
discover a representation with reusable boundary-state transfer
tables (not supplied group labels), compare with a strong generic
elimination solver and partition, including discovery/setup cost,
using fresh held-out chains, wider separators and random controls.
Do not claim novel mathematics, general learning or production readiness.
Same author, synthetic cohort; nominal .8 CPU s/8192 visits, not strict
hardware quota; no main change, paid API, promotion or deletion.
