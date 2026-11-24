# MEMBERSHIP-SFT-01 — prospective elementary skill acquisition
Separate from ATOMIC-SFT-PILOT02. ELEMENTS01 failed both membership and
logic signals. Select edge membership first; do not claim this teaches
logical combination. Use natural language Yes/No rather than digits:
ELEMENTS01 free text often began with these words; exploratory prefix
scores did not establish competence. This changes task and target interface,
so do not causally compare to ATOMIC-SFT-PILOT01.

128 examples (64 pairs) size 4 only, each pair same nodes, order, background
edges, queried distinct x,y; toggle exactly the queried edge. Uniform
balanced answers. Distinct graph canonical keys across all 128 examples;
seeded bounded rejection; fail closed. Independent fresh evaluation 64
examples (32 pairs; 16 size 5, 16 size 6); same rules. Curator freezes
eval seed and file hash before training; trainer downloads only train;
inference receives question packets, never labels; score only after
predictions freeze. No previous holdout used. Use exact direct edge
membership and independent adjacency lookup.
Pinned SmolLM2-135M base, fresh q_proj/v_proj rank8 alpha16 LoRA, no dropout,
seed 20261129, AdamW .0005, two epochs, 256 optimizer steps; max context
384, target-only loss Yes/No plus EOS. Same CPU stack as PILOT01. Archive
step losses, token exposures, weight delta and adapter hashes.
Compare base and trained on identical new packets in two views: edge
lists primary, matrix secondary. Free greedy max 8 tokens, exact "Yes"
or "No" (case sensitive); all invalid wrong. Also prospectively report
anchored Yes/No prefix (case insensitive) on same generations separately;
no rescue of strict score. If tokenizer Yes/No single token roundtrip
passes, also record raw first-token probabilities and binary argmax as
secondary interface diagnostic; no constraint during primary free
generation. No oracle/tool access in inference.
Primary signal: strict edge-list >=48/64 correct, >=20/32 both endpoints
right, each class >=20/32, >=8 more correct than base. Report paired
improvement/worsening, prefix score, valid fraction, all outputs,
conditional probability difference per toggle, matrix transfer and
per-size results. Constant baseline 32/64 and 0/32 pairs; independent
uniform guesses expect 32/64 and 8/32 pairs. Pair members are dependent.
Do not optimize on evaluation results; no automatic retry. Single seed,
no retention claim or promotion. If failed, inspect data/representation
and compare a simple exact algorithm baseline; do not blindly scale.
No paid API or main changes. Implementation and execution separate.
