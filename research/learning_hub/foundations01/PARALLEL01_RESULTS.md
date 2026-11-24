# PARALLEL01 — real process overlap, two workers preferable on this runner

Preregistration 5c5a50f2a49a36d87c4255340637060693c308e6.
Implementation 76f85547940fd2f432ac6428e26f0c2d7d26e273.
Successful CI https://github.com/Abrasax63/Omega-pub/actions/runs/45472263546.
Verified CI logs, not independently replayed artifact.

Runner reports four logical CPUs, affinity 0-3, two visible distinct
package/core IDs. Virtual topology is not a guarantee of host physical
cores. CPU quota not exposed at probed paths; initial cpu.stat reports
zero throttling, not a measurement over the entire benchmark.

20 fresh graphs, 9 independent references and 11 reference limits.
Three repetitions. Identical 181 distinct frontier jobs per partition
arm from 187 valid assignments. All completed counts agree with
available references and other completed arms, including leaf counts.
76 exhaustive small-graph partition and fail-closed tests passed;
75 have repeated residual multiplicities. No duplicated frontier jobs,
not a guarantee of no repeated internal residuals between jobs.

| Arm | Verified | Unverified | Unresolved | Sum median wall s | Sum median CPU s |
|---|---:|---:|---:|---:|---:|
| Serial partition |9|7|4|3.008657|3.010190|
| Pool 1 |9|7|4|2.974759|2.980554|
| Pool 2 |9|7|4|1.896827|3.050599|
| Pool 4 |9|7|4|1.877217|3.858776|
| Direct local (different cap) |9|6|5|1.991253|1.990756|

Observed task intervals overlap across distinct PIDs on all 20 cases
with 2 and 4 workers, peak 2 and 4 respectively. These are concurrent
process lifetimes, not proof of simultaneous execution on distinct
physical cores. Full-workload wall time about 1.59x and 1.60x faster
for 2 and 4 workers versus serial partition; CPU +1.34% and +28.19%.
Four versus two saves about 1.03% wall at 26.49% additional CPU.
Median whole-arm wall including pool startup/shutdown: serial 2.989810,
pool1 3.078550, pool2 1.896511, pool4 1.885410. Corresponding medians
of aggregate parent+children CPU: 2.988698, 2.980067, 3.064565,
3.927522 seconds. Direct local not matched-budget: descriptive only.

Primary on 9 jointly verified cases: serial wall .114025, pool1
.118909, pool2 .108732, pool4 .109682 seconds. Speedups 1.049x
and 1.040x for 2 and 4, below 1.25x gate. Paired CPU .114515,
.119580, .119602, .117298 seconds respectively. Primary FAIL.
Most aggregate speedup occurs outside independently verified cases;
no certified general acceleration. Timings are short, 3 repetitions
on one runner, CPU cap may affect visits; not external replication.
Prefer investigating 2 workers on this runner, not automatically
4. Next test: granularity and workload prediction with 1/2 workers,
stronger independent references and explicit measured quota; compare
partition and direct under common aggregate resource budgets.
No main change, paid API, promotion or archive deletion.
