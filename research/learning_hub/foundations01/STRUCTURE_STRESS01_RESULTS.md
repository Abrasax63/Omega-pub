# STRUCTURE-STRESS01 — local original checkpoint audit
Protocol 9517c78642d4da563ef99b33be3b59ed49b853e9. Downloaded original
COMPOSITION01 artifact 14924271795, archive SHA256
866102f8fefaa169fc2a099ea01cfbe64b96eb39ab8f8f82cb69dc66d30d2671 verified.
All 3 frozen state_dict file hashes checked against archived results.json;
loaded using torch.load(weights_only=True), CPU torch 2.10.0, 2 threads.
Zero training or weight updates. Independent direct edge membership oracle.
Five regimes with 512 graphs each, 5 modes (original, random bijective
renaming, edge order reversal, both, extra masked padding). Additionally
512 graphs on fixed three vertices x 6 ordered distinct triples=3072
cases per checkpoint, original only. Across all 3 checkpoints:
47616/47616 correct joint path/violation predictions;
142848/142848 individual membership decisions; 0 composition flips,
0 membership flips. No counterexample. Maximum absolute logit change
0.6619434356689453 (composition), 8.761204719543457 (membership).
Pass on all preregistered decision criteria, not numerical invariance.
Repeated transformations and seeds are correlated, not independent draws.
Bounded label vocabulary 12, query decomposition supplied, no natural
language or autonomous skill discovery tested. No proof for arbitrary
graphs. Local audit code and results retained; not a new CI run.
Next discriminant: train a task-selector/composer on multiple primitives,
hold out an entire composition rule, compare learned discovery vs
human-supplied decomposition. No promotion or main modifications.
