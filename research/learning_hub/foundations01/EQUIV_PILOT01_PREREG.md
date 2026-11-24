# EQUIV-PILOT01 — prospective controlled training readiness (no training authorized)

Diagnostic EQUIV-BASE01 holdout consumed by baseline; do not reuse
for promotion. Prepare new paired contrast corpus with shortcut
controls: A,B+,B- all feasible size-two distinct from anchor,
same intersection cardinality with A, same cardinality of blocked
future set in positive AND negative; negative differs by membership.
Thus neither overlap of selected vertices nor number of blocked
vertices can distinguish paired labels. Randomize names/order.
Exact truth by enumeration of future independent sets and separate
blocked-mask oracle. No labels in prompts. Train 12 generator
configurations as BASE01, 8 graphs/configuration (192 examples),
sizes 8,9. Dev 2 configurations, 4 graphs each (16), size 12.
Evaluation 4 distinct configurations, 8 graphs each (64),
sizes 13,14. Fresh seed 20270159. No graph isomorphism across split
sizes or with BASE01 diagnostic n10,11; exact within-split dedup
using WL buckets + isomorphism. Historical corpus not comprehensively
audited; 12 configurations not 12 independent skills. Same author,
public generator, synthetic data, not independently secret.
Separate artifacts train/dev, reserved questions, reserved labels.
Freeze hashes before any model evaluation; no eval invocation here.

Proposed future pilot, requires explicit approval and separate
implementation review: same pinned SmolLM2-135M-Instruct base,
compare frozen model, LoRA ordinary balanced binary loss, LoRA
pairwise contrast loss plus same binary loss, identical examples,
paired batch exposures, update counts and token budgets. Suggested
rank 8 q_proj/v_proj, 2 epochs, 192 optimizer steps (96 pairs x2),
seed 20270160, AdamW LR 1e-4, lambda=.5 contrast term
softplus(1-(logodds_positive-logodds_negative)). Compare class
balance, paired strict success, conditional binary score, raw
generation and cross-view accuracy. No hyperparameter tuning
on holdout. Record adapter SHA256, weight delta, loss, token
exposure, CPU, failures. Retention: separate frozen 32 paired
edge-membership/syntax tasks, verify before launch; no reuse of
consumed holdouts. Require >=10 percentage-point gain vs base on
each view, >=75% strict accuracy, >=20/32 pairs both correct,
>=24/32 per class, <=5 point retention loss, and paired-loss
improvement over ordinary LoRA before claiming benefit of
contrastive objective. Three seeds and independent holdout required
before promotion, no AGI/general learning claim. A single pilot
may be justified with clean data and hypothesis even if base is
weak; no automatic authorization. Need real baseline result,
fresh retention set and verified trainer/evaluator interface
before GO request. No weight update, paid API, main change,
automatic training workflow or promotion in this step.
