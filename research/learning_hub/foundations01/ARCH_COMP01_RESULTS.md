# ARCH-COMP01 — measured tradeoff, no promotion
Protocol 9d305119878f9725b3596ea6686f32ac0218e757; pre-code
cardinality correction 27e532ee5fb954e782e0beb7014ce1ae6502a750
(12 local, 24 each history/mixed/outside; 84 distinct total).
Implementation 264b5e78074bff3917d1cc5b94a4c4db812616b1.
CI https://github.com/Abrasax63/Omega-pub/actions/runs/45439480225
success; results from verified CI logs, not independent artifact replay.
Same 14 Boolean monomial dictionary and XOR composition grammar.
| architecture | exact in-family /60 | wrong conditional /84 | outside rejected /24 | queries | median CPU s |
|---|---:|---:|---:|---:|---:|
| progressive |55|12|17|1644|.003420978|
| flat concurrent |60|3|21|1848|.111800112|
| factorized network |60|3|21|1848|.004321371|
| fixed full basis |60|11|13|1848|.003152224|
Progressive 5 incorrect in-family candidates plus 7 outside. Network and
flat identical query traces and outcomes across all tasks, all three
repetitions. Network/flat outside errors both 3; fixed 11; no universal
certificate. Network 96.13% lower median CPU time than flat, including
flat initialization (~75 ms, one build per 84 tasks); also ~88% lower
than flat after removing median initialization, descriptive only.
Network ~37.1% slower than fixed; same number of queries. Primary
quality and safety pass; cost gate fails. Abstract selection checks
67620 flat vs 1397 network, different primitive operations, not FLOPs.
84 task runs per arm, three deterministic repeats for timings, not
three independent cohorts. The fixed comparator's high-weight-only
challenge set differs from network/flat uniform remaining inputs; the
outside rejection advantage cannot be attributed to the graph itself.
Flat/network equivalence follows from balanced splits on affine GF2
solution sets. Next: isolate query design by crossing basis choice
and challenge distributions, then compare non-linear/non-affine
compositions where factorization and exact flat search may diverge.
This is a bounded history-window function learner, not a recurrent
agent or arbitrary hidden-state inference; catalogue and factor graph
provided by developer, no LLM/weight changes or self-invented architecture.
No main change, no paid API, no automatic integration. Retain network
as an efficient equivalent implementation of flat version-space search,
not a superior general architecture or promotion candidate.
