# EQUIV-CUMULATIVE01 — prospective curriculum, no weight update

Written while EQUIV-REAL01 evaluation is incomplete. No adapter selected.
Do not change or reuse REAL01 reserved evaluation to tune the next model.
First obtain complete real scores and independent post-audit, archive
adapters and predictions. If no arm passes the preregistered acquisition
gate, no "learned checkpoint" exists; investigate weak elementary
relations instead of presenting continued training as consolidation.
A partial gain may motivate a separately approved exploratory diagnostic,
not promotion. If eligible, select by development-only metric using
a separate development set; REAL01 holdout is diagnostic evidence,
not a model-selection score. Freeze selection rule before inspecting
development predictions, require explicit user approval for new training.

Proposed stage 2: directional singleton witness. Given feasible past
sets A,B and future vertex v, determine whether v can be added to A
but not B. Matched positive/negative examples on identical graph,
same A,B (equal-sized feasible sets, equal blocked-set cardinality);
positive v in blocked(B) minus blocked(A), negative v in blocked(A)
minus blocked(B). This teaches a composable operation, not just more
examples of the original equality label. Verify with singleton
independence and direct adjacency separately. Fresh retention probes
of the old equivalence relation, same overlap and blocked cardinality
in positive and negative alternative, plus original retention domains
on newly generated questions before a real follow-up.

Freeze only: train 48 pairs (96 examples), dev 8 pairs (16 examples),
test 32 pairs (64 examples); old equivalence retention 32 pairs
(64 examples). New train n15/16, dev n17, test/retention n18/19.
Disjoint from all prior EQUIV-PILOT01 and BASE01 graph sizes.
Exact graph-isomorphism dedup via WL buckets + isomorphism across
all generated graphs; fresh seed 20270165; matched density configs
train .25,.45,.65 x .1,.3 internal; dev .35,.55; test .2,.4,.6,.8;
retention uses same held-out density settings but distinct graphs.
Random names and order, no labels/trace in question packets. Verify
per-class and pair balance, singleton witnesses, exact equivalence
via exhaustive future subsets, prompt hash separation, report
rejection attempts. Train/dev versus questions versus labels separate
artifacts; freeze SHA256. No inference or training on these reserved
questions. Corpus synthetic, not externally secret, not historical
contamination audit.

Future conditional comparison (separate preregistration before
training): same base, selected objective, adapter rank and fixed seed.
A existing checkpoint untouched; B continue on new exercises alone;
C continue with mixed old/new replay; D cold start on the exact stage2
mixed stream (same incremental budget); E cold start on both stages
at equal total exposure (strong full-compute baseline). Match B/C/D
optimizer updates and padded token budget by predeclared batching,
report new vs replay exposures separately (C has fewer new examples,
an intentional allocation difference). B/D additional new-only
control if isolating replay from initialization; E must match
old+new total exposure, not merely incremental compute. Reset
optimizer identically for all continuation arms; preserve original
weights and adapters. Compare new skill and old skill jointly,
new holdout and fresh retention, strict class-balanced pair accuracy,
binary diagnostic, cross-view generalization, time/token cost. Require
>=75% strict new accuracy and >=20/32 complete pairs per view,
old equivalence decline <=5 pp relative to incoming checkpoint on
same fresh retention set, report floor effect; no claim consolidation
if starting skill unvalidated. No repeated tuning on test; replicate
across seeds and independent fresh holdout before promotion.
Current work only corpus and protocol preparation, no API paid,
main changes, launch or adapter selection.
