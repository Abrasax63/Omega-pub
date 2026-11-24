# LEARN-POLICY02 — positive learning control, no superiority over strong baseline
Preregistration 38e7d053e00ee22e3d3e7ca8125685b9b645a965.
Implementation 2a135461003c424b8459f596b126ba23a7154920.
Successful train and separate evaluation jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45449842503.
Results checked in CI logs, not independently replayed artifacts.

Same exact solver as POLICY01, three weak initial weight vectors, 40
mutations per optimizer, 24 training graphs. Random search receives same
number of candidates, not identical realized training compute.
All three hill policies retain changed weights (10,11,4 accepted updates).
Training costs min 4835->1990; neighbor 4332->1950; zero 2773->1924.

48 fresh holdout graphs, 36 independent references (16 exhaustive,20
branch), 12 reference limits. No verified count discrepancy.
| Policy | Verified | Unverified | Unresolved |
|---|---:|---:|---:|
| Strong degree |36|1|11|
| Minimum degree start |31|0|17|
| Minimum degree hill |35|0|13|
| Minimum degree random |35|0|13|
| Neighbor start |30|0|18|
| Neighbor hill |36|0|12|
| Neighbor random |34|0|14|
| Zero start |34|1|13|
| Zero hill |35|0|13|
| Zero random |36|1|11|

Paired verified visits reductions hill vs own start: 66.58%,62.25%,
25.06%, all pass. On n>=24 paired transfer subsets: 7567/24040,
5708/15722,8648/11621 visits respectively.
Hill vs random reductions 6.48%,6.03%,-8.41%, none reach 15%.
Hill vs strong: -20.03%,-9.53%,-10.02%, none pass.
Primary positive control PASS; random superiority FAIL; strong
superiority FAIL. Persistent learned decision parameters transfer
within supplied graph-counting domain; no new operator, LLM skill,
autonomous grammar discovery or improvement over strong incumbent.
Same author and generator, three different starts not independent
replications of each start. No runtime integration or main change.
Next: avoid further tuning these five weights without evidence of
headroom. Test learning a context-dependent policy against strong
fixed degree and equal-budget random search, on genuinely different
graph families and blinded evaluation. Keep strong incumbent in use.
