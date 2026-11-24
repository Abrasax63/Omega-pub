# PARTITION01 — unique residual jobs, no duplicate completion, utility gate fails

Preregistration 0df26e7ebdade5335b553f460fbf4e67783fdb17.
Implementation a6a0480b12f4cf3ec10be2cacde136a3157ec0fe.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45471445396.
Verified CI logs, not independent artifact replay.

40 fresh graphs up to 72 vertices, six arms, three shuffled repetitions.
30 independent references (8 bitset, 12 conditioned leaf DP, 6 branch,
4 multipartite formula); 10 reference limits. No disagreement among
completed counts or with available references. Six targeted selftests
pass: empty, disconnected, shared diamond registry fixture, malformed
dependency, duplicate completion, budget exhaustion.

| Arm | Verified | Unverified | Unresolved | Verified capped CPU s | All capped CPU s |
|---|---:|---:|---:|---:|---:|
| DAG branch |29|5|6|0.551343469|3.121344783|
| DAG specialist |30|7|3|0.161987897|2.427863320|
| Synchronous branch |29|5|6|0.521835612|3.060816012|
| Synchronous local |30|7|3|0.141997468|2.363421184|
| Delay512 |30|8|2|0.168771621|2.291327000|
| Shared root race |30|6|4|0.166762312|2.589929558|

First repetition totals: specialist DAG 19956 requests, 4273 repeated
requests, 15635 unique expansions, 15571 completed jobs, zero duplicate
completions. 34/40 cases contain repeated requests; registry shares
these jobs rather than re-expanding them. Shared root race 2894 duplicate
completions, 30388 visits, 3505 cross hits. These counters are not
equivalent work units or direct counterfactual savings.
Specialist DAG reduces verified capped cost 2.86% vs shared race,
increases it 14.08% vs synchronous local. All-case cost 2.73% higher
than local and 6.26% lower than shared race. Primary utility FAIL;
safety PASS on tested invariants. On 29 jointly verified completed
cases, specialist DAG .036987663s, local .026998429s, branch
.021835612s. Registry introduces overhead. Homogeneous DAG reproduces
branch coverage and request/visit count (36132) but costs more.
Delay512 has one additional unverified completion vs specialist DAG;
not a certified accuracy gain.

No true parallelism: depth-first single-process job registry; no
concurrent worker ownership, work stealing or multicore scheduler
yet. Same generator, fixed policy, coarse CPU timing, no external
blind replication. The diamond is a synthetic dependency fixture,
not a count of diamond-shaped motifs on the real cohort.
Next: bounded ready-queue with explicit ownership and task granularity,
compare single-worker overhead then process-based parallel execution
under measured CPU affinity/quota, wall and aggregate CPU budgets.
Do not assume performance from absence of duplicates.
No main change, paid API, archive deletion or promotion.
