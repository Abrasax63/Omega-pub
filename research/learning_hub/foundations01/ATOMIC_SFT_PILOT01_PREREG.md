# ATOMIC-SFT-PILOT-01 — supervised feasibility, prospective
Separate from FOUNDATIONS-01 three-arm experiment: autonomous proposal quotas
not met, no substitution of curated data into self-generated arm. Question:
can the proven 135M CPU LoRA backbone acquire atomic relation reading and
local implication from exact supervised examples? This is a one-seed
feasibility pilot only, not an autonomy claim, not general math competence.

Model/revision, pinned dependencies, rank 8, alpha 16, q_proj/v_proj,
AdamW lr 0.0005, two epochs, CPU two threads from SFT01; seed 20261127.
Fresh adapter on frozen base, 128 curated training rows, 256 updates.
No old holdout, no prior adapter; labels from teacher checked by independent
matrix lookup. Graphs of size 3/4 only, 64 rows each. Distinct query vertices,
one canonical graph per row. Each size: half motif 110 and remaining
half evenly divided among seven negative motifs (existing quotas).
Train with edge list only, random fresh node names/order and edge order.
Prompt asks four bits xy,yz,xz,violates in that order, no other text.
Target four ASCII digits; no grammar at evaluation. Loss only target plus EOS,
max context 384, no truncation; fail if budget exceeded. Log per-step loss,
actual token exposures, parameter delta and adapter hashes.

One 64-graph evaluation cohort (32 size 5, 32 size 6), disjoint by vertex
count, never used for selecting training hyperparameters. Balanced motif
quotas per size, one graph per row, independent random seed chosen by
evaluation curator, archive manifest and SHA before training starts.
Training job sees only training data; evaluation job obtains frozen
evaluation data after both base and adapter weights are fixed. No hidden
answers in generation prompts, no tools or retrieval. Evaluate the same
64 graphs in edge-list and matrix forms (paired views, not 128 independent
graphs). Greedy free generation, at most 16 output tokens, exact four-bit
string, invalid outputs in denominator. Measure format, exact three-bit
reading, decision, internal consistency, joint and class-specific joint;
constant negative decision baseline 32/64 per view. Predefined primary
edge-list signal >=7 additional joint successes (>=10 percentage points)
and improvements in both classes; matrix view secondary transfer, no
selection based on it. Report paired before/after counts and inference
costs. No significance or promotion claim. New syntax retention and
three-seed replication are explicitly NOT tested here; remain blockers
for promotion under FOUNDATIONS-01. Any technical failure or zero gain
reported as such. No automatic retry, no main changes, no paid API.
Public generator is inspectable; procedural job isolation is not a
cryptographic guarantee against model pretraining contamination.
