# SEPARATOR-EXPLORE01 — late discovery confirmed, global utility gate fails

Preregistration 74c8c03382259c788441d87503cf866c05504a8a.
Implementation d2683f3147a466544bc36cc2923f1513ac85d589.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45478743954.
Results inspected in CI logs; artifact metadata retrieved, not independently replayed.

32 fresh graphs, 27 independent references (20 transfer DP, 6 branch,
1 complement cliques), 5 reference limits. Three shuffled repeats.
All arms solve 27 reference cases; no detected completed-count
discrepancy. 532 exhaustive checks and late-discovery apex fixture,
dense negative, probe caps and fail-closed checks passed.

| Arm | Verified | Unverified | Unresolved | All reward | Verified reward | Structured reward | Control verified reward |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direct |27|3|2|6.106506|.890945|.268619|.622325|
| Shared partition |27|3|2|5.917486|.869364|.290048|.579316|
| Unrestricted factor |27|1|4|7.432686|.913118|.142652|.770466|
| Bounded root veto |27|3|2|5.987853|.772088|.142952|.629136|
| Open16 |27|3|2|6.018193|.778085|.142502|.635582|
| Open128 |27|3|2|6.008943|.776020|.129971|.646048|
| Open128 raw |27|3|2|6.154936|.848655|.143895|.704760|

Reward = wall+.25*CPU+1 per unresolved, sum of case medians.
Primary FAIL: open128 verified reward -10.74% vs shared partition,
-12.90% vs direct, all reward +1.55% vs partition. Secondary FAIL:
four verified completed cases with late discoveries but +.51% verified
reward vs bounded. No novel verified recovery. On 20 structured cases,
open128 improves 55.19% vs partition and 51.62% vs direct; deliberately
structured cohort, subgroup descriptive. On seven verified random
controls, open128 costs 11.52% more than partition.

First-repetition open128: 1138 searches, 1530 component probes, 380
accepted separators, 237 late after negative root, 2394/5910 factor
cache hits. Raw ablation: 7060 probes and 4779 failed; filtered
candidate rule reduced component probes 78.33% and verified reward
8.56% relative to raw. Open16 vs bounded isolates root veto (3 late
verified cases vs 0, .78% higher verified reward); open128 vs open16
isolates budget (.27% lower verified reward). 19/20 structured roots
positive vs 0/11 tested random roots; one random root not tested.
Counts do not establish that every late separator is beneficial.
Apex fixture gives exact positive test of late discovery.

Retrospective fixed oracle .704606 vs best fixed partition .869364
(18.95% headroom), all-arm oracle .695403 vs best tested bounded
.772088 (9.93% headroom). No deployable oracle or learned selector.
Single-process nominal .8 CPU seconds/8192 visits; not strict OS
quota. Same synthetic generator and author; no external replication.

Next distinct hypothesis: estimate usefulness of local separators
using cheap structural evidence and charge discovery relative to
expected saved work, rather than increase exploration caps further.
Before new learning, use stronger diverse controls and measure
whether oracle headroom persists on a fresh cohort. No main change,
paid API, activation or archive deletion.
