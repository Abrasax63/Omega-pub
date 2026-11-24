# MEMORY-PRUNE01 — reversible pruning, safety tests pass, utility gate fails

Preregistration cc65e2a7c9149b144f889654a95f4c19e073902b.
Implementation 2016ff6268b1adcdc8b82c665252ebb94c42a34a.
Successful separate calibration and evaluation jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45454952753.
Results verified from CI logs, not independent artifact replay.

Archive contains six flat macro definitions and 32 original exact
programs. SHA256 ff40f862fe31049e3c12709e0671489cf477f74871dde5c9958830be80570a45.
Journal head e7fe74e8ace24feb1b01ece2f15b7a4ae7207dcfe9c4f4a3dc2b876db9459d51.
Active manifest only: removed RSM, MS, RS, MR; retained SM and SR.
All original programs replayed, archive unchanged; rollback to full
manifest reproduces exact calibration word/cost outputs; restore
selected manifest. Seven injected integrity faults rejected:
changed definition, missing reference, history tampering, duplicate
active ID, changed solution, wrong predecessor, invalid rollback index.
No physical deletion. Safety gate PASS for tested cases.

24 calibration problems: full 23 solved/27948 capped cost, selected
24/13845, primitives 24/15201. Selection overhead 452392 capped
compositions over 22 evaluations, excludes replay overhead.
48 new holdout problems on p=23,29:
| Arm | Solved | Capped cost | Random subgroup cost |
|---|---:|---:|---:|
| Full |46|60135|28568|
| Selected |48|38716|14949|
| Primitives |48|32746|9381|
| Random subset (SM,RS) |48|35891|16242|
Selected reduces full cost 35.62%, but increases primitive cost 18.23%
and random-subgroup cost 59.35%; utility gate FAIL. Do not activate
selected library; primitive baseline remains preferred on this test.
No promotion, no main changes, no paid API.

Scope: only flat macros with supplied primitives; no transitive learned
dependency DAG, quarantine policy, independent durable backup, malicious
rewrite resistance or integration with research result archives tested.
Archive anchor and journal head must be anchored outside mutable storage
for protection against rewriting the entire chain. CI checkpoint artifact
is subject to retention; source and report committed but permanent
checkpoint archival and restoration from independent backup not tested.
This is a prototype, not a guarantee against losing real research data.
Next: external durable archive, dependency closure, protected scientific
results and counterexamples, reactivation tests on rare or shifted
tasks before any autonomous library-wide policy. Never physically delete
unique scientific results through automated pruning.
