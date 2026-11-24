# ATOMIC-SFT-PILOT-02 — prospective counterfactual curriculum
Decision after PILOT-01: do not scale training volume or model size yet.
The balanced binary labels made motif 110 half the corpus, so the adapter
collapsed to a single consistent string. This is a demonstrated shortcut,
not proof of its sole cause. Test a new curriculum and compare against
constant controls. Separate from the blocked autonomous three-arm protocol.

Construct families of 8 graphs: choose distinct x,y,z and a background
graph; vary only edges xy,yz,xz through all 8 bit motifs; keep names,
node order, other edges and triple identical within each family.
Train 16 families (8 with 3 nodes, 8 with 4), 128 examples, equal motif
counts. Reject any canonical graph key repeated anywhere across families
or within a family. Same pinned model, fresh LoRA, same seed 20261127,
256 optimizer updates, target-only loss, no grammar during primary
evaluation, same interface and hyperparameters as PILOT-01. Shuffle all
examples each epoch. Match examples and updates, record actual tokens;
do not claim equal token budget. If family construction fails within a
fixed bound, report blocked, do not loosen uniqueness after inspecting
outcomes. Freeze data before training. Never train on previous holdout.

Fresh 8 evaluation families (4 size 5, 4 size 6), 64 graphs, all eight
motifs equally represented, independently seeded by curator; freeze
questions and labels separately. Use two views as before. Compare frozen
base, previous collapsed adapter (negative reference), new adapter.
Primary: strict joint edge-list accuracy >=24/64, >8/64 best constant,
and >=1 correct per motif; also report both class-specific joint,
decision balanced accuracy and matrix transfer. Counterfactual metric:
for each family and each of the three varied edges, compare all four
pairs differing in that bit, require exact joint on both endpoints
(and therefore correct response change). 96 pairs per view, correlated,
not independent. Primary additional threshold >=24/96 exact pairs.
Report fraction of families solved entirely, output distributions and
per-bit sensitivity, all invalid responses counted as failures.
Analytic constant baseline: 8/64 exact joint, 0/96 exact pairs; constant
negative decision 56/64, so raw decision accuracy alone misleading.
Uniform consistent output expected joint 8/64 and 96/64=1.5 exact pairs
under independent draws. No promotion from one seed or without syntax
retention. Change in curriculum combines balancing and counterfactual
pairing: cannot attribute gain causally to either without ablation.
No oracle access during inference, no answers in prompts, no retries,
no paid API or main changes. Implementation and run separate.
