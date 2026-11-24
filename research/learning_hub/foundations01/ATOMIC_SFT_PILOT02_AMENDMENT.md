# ATOMIC-SFT-PILOT-02 — feasibility amendment, before any model execution
Original registration remains immutable. CI 45386227747 failed before
training. Exact enumeration in PR #251 comment 7130427742 proves at most
four disjoint three-node families under the original graph-isomorphism
constraint. Replace eight 3-node plus eight 4-node families by sixteen
4-node families; 128 graphs, 16 examples per motif, all unique graph keys.
The independent witness in the comment exhibits 16 disjoint 4-node
families. The generator still uses seeded bounded random construction and
fails closed; no fallback to relaxed uniqueness. Evaluation sizes 5/6,
thresholds and budget unchanged. No result or training claimed.
This changes size distribution relative to PILOT-01, so comparison is
not causal isolation of pairing/balance. A matched four-node balanced
unpaired arm is needed if the counterfactual approach is promising.
Prioritize ELEMENTS-01 diagnostic before launching PILOT-02.
