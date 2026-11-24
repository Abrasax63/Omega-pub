# LEARN-POLICY01 — negative learning result
Preregistration 2a5e695186c27d2e260f5cd5a8fd995f9b2aa95d.
Implementation f6e0483c3717ed195e1c889cc32e2c4be8d46fef.
Successful training and separate evaluation jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45449211799.
Verified CI logs, not independent artifact replay.

Frozen exact graph-counting engine, five supplied decision features,
40 Gaussian mutation proposals, scalar cost feedback on 24 graphs.
Training initial/final loss 1866/1866; 109335 recursive visits spent.
Final weights identical to initial (1,0,0,0,0). No retained update.
Checkpoint reloaded in separate evaluation job with source SHA verified.

48 held-out graphs; independent references completed on 37 (16 bitset,
21 independent branching). Eleven reference limits.
| Policy | Verified | Unverified | Unresolved | Total visits | Shared verified visits |
|---|---:|---:|---:|---:|---:|
| Before |35|1|12|67334|6750|
| Min degree |31|0|17|92136|21417|
| Neighbor degree |30|0|18|93740|20012|
| After training |35|1|12|67334|6750|
Shared verified cohort: 30; transfer n>=24 visits before/after 5208/5208.
No count discrepancy on verified completed cases. Primary gate FAIL.
Training cost did not buy any learned gain. No runtime activation.
The optimizer was limited to 40 local mutations around an already strong
heuristic and a supplied feature basis. This does not prove that learning
a better policy is impossible. Do not enlarge training indefinitely
without identifying a signal. Next decisive test: analyze candidate
cost distribution and compare budget-matched randomized restart search
or a deliberately weak initial policy on fresh held-out tasks; separate
recovery of known heuristic from genuine improvement over strong baseline.
No neural weight training, general autonomy, paid API or main change.
