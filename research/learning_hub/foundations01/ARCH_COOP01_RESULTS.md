# ARCH-COOP01 — actual sharing, no decisive efficiency gain

Preregistration 0f7715c270076e2990a3fe89a04773aeb0adbd39.
Implementation 9bacaaf92a55d13e5048502297e057234af076ac.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45469740152.
Results verified in CI logs, not independent artifact replay.

32 new graphs, 24 independent references, eight reference limits.
Two resumable workers alternate 32 recursion visits; global 4096
visit cap and 0.5 CPU-second cap. Shared versus separate exact
residual memo, otherwise identical schedule. Not parallel threads.
Three repetitions per graph and arm; no discrepancies in available
reference counts or among completed arms.

| Arm | Verified | Unverified | Unresolved | Verified capped CPU s | All capped CPU s |
|---|---:|---:|---:|---:|---:|
| A only (branch) |24|3|5|0.043931279|2.570930214|
| B only (local) |24|5|3|0.062989036|1.736980788|
| Isolated race |24|5|3|0.091449179|1.786450224|
| Shared race |24|5|3|0.085505624|1.774506838|
| Synchronous delay512 |24|6|2|0.080997578|1.643938936|

All 24 verified cases jointly completed. Shared reduces verified
CPU cost 6.50% vs isolated, all-case cost 0.67%; but costs 94.63%
more than A-only on verified cases. Primary gate FAIL. First
repetition totals shared 22535 visits vs isolated 23598 (-4.50%);
2509 cross-worker memo hits, including 632 on verified completions
and 1362 on unresolved cases; 12 verified cases exhibit sharing.
2141 duplicate completions despite shared memo. Peak stored
entries 2640 vs 2920 isolated. These counts are not CPU instructions.
Shared workers A/B win 5/24 tasks respectively, 3 unresolved.
No improvement in verified coverage. Delay resolves one additional
unverified case; cannot certify it. Timing resolution coarse; tiny
differences are descriptive. Both workers use the same branching
order and B alone can dispatch other engines; high overlap is
expected. No true multi-core concurrency or learned scheduling.

Next discriminant: cooperative work partition, not duplicate root
racing. Maintain unique residual jobs with dependency tracking,
allow specialized workers to claim disjoint ready jobs and return
exact results, count duplicate work and scheduling overhead. Compare
against a single engine and identical partition without specialization
on fresh graphs. No promotion, main change, paid API or archive deletion.
