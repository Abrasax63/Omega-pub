# PROPOSAL-02 — compact representation diagnostic, prospective
Compare frozen SmolLM2-135M on two arms with identical prompt, 16 fresh paired
seeds 20261125+i, temperature 0.8, no feedback, no worked examples or labels.
Graph universe fixed to three nodes A,B,C. Model chooses all nine adjacency
bits (row-major) and all three query indices (0,1,2; repeats allowed).
Output contract exactly 12 ASCII characters: nine bits followed by three
indices, no separators. F: free generation, at most 32 output tokens.
G: grammar-only constrained decoding: 12 successive digit choices, first
nine restricted to 0/1, last three restricted to 0/1/2; verify tokenizer
roundtrip for each single digit; sample solely from model probabilities
renormalized over permitted next digits. No oracle access during generation.
No guarantee of mathematical variety: teacher labels only after generation.
Record all raw outputs, seeds, generated token IDs, prompt hash, times,
constraints and model revision. Exact same compact decoder for both arms;
deduplicate via existing marked-graph key, preserve original outputs.
Primary diagnostic per arm: valid count, unique marked graphs, unique
graphs, eight motif counts, rejection reasons, token cost; report class
imbalance and the difference in unique tasks. Exploratory feasibility:
>=8 unique tasks, >=4 represented motifs including >=2 violations.
G syntax validity alone is mechanically imposed and is not learning.
F is intrinsic compact-output feasibility; G is assisted generation.
Both arms may fail diversity; no retry or threshold revision.
These samples are diagnostic, not training or evaluation data. No gradients,
no promotion, no paid API. No comparison to PROPOSAL-01 as causal effect
because prompt, graph universe, sampling budget and format differ.
Implementation and execution remain separate from this preregistration.
