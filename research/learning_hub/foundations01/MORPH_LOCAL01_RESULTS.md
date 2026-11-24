# MORPH-LOCAL01 — local selection fails, fixed portfolio headroom small

Preregistration 4e4c8ae2b1bc864fef6c5649643648815829e0f5.
Implementation 96bece49858ceab6631656e7a969f265aa45dd62.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45476146191.
Verified CI logs and artifact metadata, not independently replayed.

32 fresh synthetic graphs, 21 independent references (8 conditioned
leaf DP, 5 bitset, 4 multipartite formula, 3 branch, 1 complement
cliques); 11 reference limits. Three shuffled repeats. No completed
count discrepancy. 304 exhaustive solver checks, 410 conditioning
identities, eligible-node test, cache-choice fixture and fail-closed
test pass. Same 8192 nominal request/visit and .8s CPU caps; these
work units differ, and CPU timer is not a hardware quota.

| Arm | Verified | Unverified | Unresolved | All reward | Verified reward | CPU s |
|---|---:|---:|---:|---:|---:|---:|
| Binary DAG |21|8|3|7.331551|0.484880|3.464242|
| Multi DAG |21|8|3|7.189331|0.437747|3.350818|
| Structural local |21|8|3|7.364239|0.487852|3.491422|
| Cache-aware local |21|8|3|7.369293|0.490985|3.497686|
| Direct |21|8|3|7.280216|0.454122|3.421310|
| Shared partition |21|9|2|5.721989|0.408427|2.973582|

Reward = wall+.25*CPU+1 if unresolved, summed per-case medians.
Primary FAIL. Cache-aware cost +20.21% vs shared partition,
+12.16% vs fixed multi, +0.64% vs structural-only ablation.
No verified recovery beyond fixed controls. Two verified cases select
completed children. First-repeat totals cache-aware 25315 candidate
probes, 45 selected cached children, 30244 requests, 6532 reused
requests, 23657 expansions; structural-only 25395 probes, 31 selected
cached children, 30364 requests, 6553 reused requests, 23763 expansions.
No duplicate expansion or completion accepted; full reachability
audit skipped for 3 unresolved first-repeat cases as in MORPH-DAG01.
Extra unverified completion of shared partition is not a certified gain.

Fixed-arm retrospective oracle verified reward .400126220 vs best
fixed partition .408427200 (only 2.03% headroom); all-arm oracle
.400122123, negligible incremental benefit. Fixed oracle all reward
5.712659475 vs partition 5.721989453 (~0.16% headroom).
Oracle is diagnostic, not a deployable selector. On this cohort
further optimization of choice among these arms is not justified
by the 15% target, even with hindsight. This does not exclude
better solvers, other populations or nonlocal policies.

Recommendation: stop expanding this selector family; retain shared
partition as experimental comparison baseline, not production
promotion. Next distinct hypothesis should reduce intrinsic work,
e.g. exact separator-based decomposition with conditional factor
reuse, tested against the present baseline under matched caps and
stronger independent references. No learned scheduling, new neural
training, main change, paid API, or archive deletion.
