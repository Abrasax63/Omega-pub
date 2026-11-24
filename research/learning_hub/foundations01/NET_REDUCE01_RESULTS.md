# NET-REDUCE01 — exact propagation and parity compression
Preregistration 16855eff6e49cd5a6bc0751ae36e4b72a0a7de49.
Implementation 3b3b06bcd3f445b271d569cf656b49f2646eb326.
Verified successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45442659581.
89 cases: original 77 plus 12 structured dense controls.
| policy | exact completed | resource limit | UNSAT | peak planned entries | total seconds |
|---|---:|---:|---:|---:|---:|
| plain |75|14|39|2048|0.779454758|
| unary |80|9|39|8|0.777138178|
| full |86|3|42|8|0.505754637|
All completed exact counts and pinned counts agree with independent
enumeration/transfer/branching or analytic references. No regression
on original completed cases; both original dense cases recovered
(count 1 each, unary sufficient); all nine new XOR cases recovered.
128-variable dense XOR (8128 pair constraints) compresses to one
free variable, count 2, pinned count 1, ~0.10694 s for both queries.
Pinned and contradictory dense XOR controls count 1 and 0 respectively.
All three complete OR=1 graphs (24,64,128) still exceed cap, despite
known analytic counts n+1; no wrong answer emitted. This is an
implementation limitation, not an intractability proof.
Reduction correctness: substitutions pin or identify Boolean roots
with a parity offset, bijective over compatible root assignments;
remaining binary relations encoded by forbidding disallowed pairs.
Preserves isolated variables and counts. Evidence is scoped to
tested constraints; no self-generated relation discovery or training.
Observed total time falls 35.11% relative to plain, but workloads
differ in completion count, timings single run and no universal
speedup claim. Cap covers joint scope cardinality, not aggregate
RAM. Results verified from CI logs, not independent artifact replay.
Primary preregistered gate PASSED. No automatic promotion: next
test should use exact connected-component decomposition and branching
with memoization, plus OR clique compression as a bounded special
case; compare against independent counting baseline and include
adversarial overlapping cliques. Avoid adding a universal heuristic
without a measured benefit. No main change, no paid API, no neural
training.