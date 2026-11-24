# LEARN-CONTEXT01 — negative contextual selection result
Preregistration 88980d9bef013ec16135e72bd01d9e1275bd2e3a.
Implementation 824574587195977856226366daae6a8631b38f7a.
Successful separate train/evaluate jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45450845776.
Results verified in CI logs, not independent artifact replay.

48 training and 48 fresh test graphs from eight supplied families.
Seven frozen candidate policies; nearest-neighbor selector k=5
trained on normalized costs, no family label given to selector.
Training 313176 visits. Best fixed training arm: max degree.
Independent references available for 32 holdout graphs (16 bitset,
16 separate branching); 16 reference limits.

| Policy | Verified | Unverified | Unresolved | Verified-subset capped cost | All capped cost |
|---|---:|---:|---:|---:|---:|
| Fixed max degree |31|8|9|10862|58549|
| Learned context |31|8|9|10886|57664|
| Retrospective oracle |31|8|9|10789|55658|

Verified-subset cost gain learned vs fixed -0.221%; oracle headroom
only 0.672%. On the 31 jointly verified completions, visits 6789 vs
6765. For n>=24 verified subset both cost 9583. Learned selects
max degree on 42/48 tasks; hill_min 4, hill_neighbor 1, hill_zero 1.
Learned beats all five random and all five shuffled selectors on
verified-subset capped cost, but not the strong fixed baseline.
Descriptive end-to-end measured solver + selection seconds .738846
vs .651639 for fixed; training cost not included. No speed claim.
Primary gate FAIL. Even oracle cannot achieve 15% on this verified
subset with this portfolio. All-case capped gain 1.51% learned,
4.94% oracle; unverified counts cannot certify correctness.
No discrepancies on verified completed cases.
Do not promote selector or repeat tuning same portfolio. The
limitation is portfolio headroom on this test, not proof that
contextual learning is impossible. Next test should compare
genuinely different exact algorithms (e.g. elimination vs branching
vs graph reductions), with independent references, fresh tasks and
explicit overhead budgets. Freeze algorithms before learning,
establish oracle headroom before investing in selector training.
No neural training, new mathematical operator discovery, main
modification or runtime activation. No paid API.
