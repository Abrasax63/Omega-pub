# NET-IRREG01 — irregular constraints: cache benefit, new branching rejected

Preregistration 33fb6848e2cb436cf3928c60fe7145be05f2d468.
Implementation b330d5073f59121ebdcd41a49d565051270da7b9.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45445989582.
Results verified from CI logs, not independently replayed artifact.

54 new cases, 48 random signed pair constraints and six irregular
positive-OR graphs. Independent reference completed on 49 cases:
24 exhaustive bitset, 19 uncompressed elimination, 6 separate
bounded branching. Five reference limits.

| Branch strategy | Verified | Unverified result | Unresolved | Total visits | Cache hits | Measured branch seconds |
|---|---:|---:|---:|---:|---:|---:|
| Degree + cache (incumbent) |49|1|4|27164|9771|0.860685|
| Degree without cache |47|1|6|33645|0|0.779884|
| Mixed polarity first + cache |49|1|4|31879|12123|0.957725|

The mixed-polarity rule fails the preregistered promotion criterion:
13594 visits versus 9677 on the shared independently verified completed
cases (+40.48%). No observed count discrepancies. Keep incumbent
degree ordering. Cache reduces visits from 6545 to 4384 on paired
verified completed cases (-33.02%) and enables two additional verified
forced-branch completions. It does not demonstrate a wall-time benefit:
the no-cache branch stops on more cases, and total timings differ in
completion; no matched timing claim. With upstream elimination, all
three policies obtain the same 49 verified completions, one unverified
result and four unresolved cases. Cache is useful within the tested
branch solver; system-wide gain is not demonstrated.

All four irregular OR graphs at n=64 or n=128 (edge probabilities
0.15, 0.35) exceed the branch budget and the independent reference
budget. A planted signed 128-variable instance at ratio 2 yields
agreement between branch policies but lacks an independent reference;
do not certify its count. No guessed result on resource exhaustion.
No main change or paid API. No neural training or autonomous discovery.

Next decisive experiment: do not just raise budget. Test a bounded
exact counting strategy specialized to general monotone OR (independent
set counting via graph deletion, separator branching and structural
reductions), compare to incumbent on a fresh held-out cohort plus
these four blocked cases, with independently verified small instances
and explicit verification limits for large cases. Distinguish
general algorithmic improvement from task-specific optimization.
