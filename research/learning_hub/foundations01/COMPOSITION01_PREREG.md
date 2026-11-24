# COMPOSITION01 — preregistered sequential composition and retention
STRUCTURE01 reproduced in GitHub run 45400141312, all six runs and
all conditioned 100% scores match local results; 13057 parameters.
Next question: can learned membership representations support a new
learned composition without losing the original skill? Do not claim
autonomy or natural language understanding.

Three arms for each seed 11,22,33: frozen conditioned membership
checkpoint + learned head; same checkpoint + fine-tuned membership
and head; fresh randomly initialized conditioned membership + head.
Use exact prior training code to reconstruct checkpoints, verify
prior reproduction accuracy 100% on all four STRUCTURE01 sets and
report weight file hashes vs prior CI. All arms identical head
initialization per seed. Neural inputs: all graph edges, three
queries (xy,yz,xz), three continuous membership logits passed through
sigmoid, then learned MLP 3->32->2. No hard-coded truth table/equality
or Boolean composition in forward. Output labels: whether specified
two-edge path exists (xy AND yz), and whether this triple violates
transitivity (xy AND yz AND NOT xz). Oracle solely data/scoring.
No membership auxiliary loss. Frozen arm is modular retention by
construction, not evidence of continual learning of shared weights.

Training: 256 families of eight graphs per seed, sizes 4..6, varying
only xy,yz,xz through every motif, density uniform .2..8, random
names and order, graph/list representation same as STRUCTURE01.
8 family batches (64 examples), 8 epochs, 256 optimizer updates,
AdamW .003, BCE over both output bits, 2 CPU threads. Same exposures,
batch schedule and head init across arms. No claim matched trainable
parameters or FLOPs (frozen vs fine-tuned). Test: fresh fixed seeds,
64 families each size8 and size12; all eight motifs, no training
sizes. Primary each seed and each size joint >=95%, each motif
>=90% joint, both tasks reported, full family success reported.
Fresh independent membership evaluation: 128 pairs each size8 and
12, distinct seeds from STRUCTURE01 and composition tests; before
and after score, <=2 percentage point accuracy loss for retention,
both-endpoint rates also reported. Scratch initial is not prior skill.
Report all results, including per-motif, learning curves, checkpoint
hashes, weight deltas and CPU time. No exact composition operation
in forward; the representation and query decomposition are supplied
by experimenter, not autonomously discovered. No promotion from this
test; no main modification, no paid APIs, no tuning on test.
