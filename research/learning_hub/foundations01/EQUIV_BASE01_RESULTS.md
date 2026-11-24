# EQUIV-BASE01 — frozen model diagnostic: constant positive response

Run https://github.com/Abrasax63/Omega-pub/actions/runs/45483683909.
Freeze 138763270411, infer 138763395196, score 138766270399 all
successful. Actual CPU inference of pinned SmolLM2-135M-Instruct.
64 diagnostic questions, two views, 128 predictions.
No weights changed. Results inspected in CI logs; artifact
metadata retrieved, not independently replayed.

| View | Strict correct | Exact valid | Binary argmax correct | Both-pair correct strict / binary |
|---|---:|---:|---:|---:|
| Edges |1/64|2/64|32/64|0/32 / 0/32|
| Matrix |0/64|0/64|32/64|0/32 / 0/32|

All 128 raw outputs begin with Yes. Only two are exactly Yes;
the rest continue a sentence. Binary argmax is at chance
(32/64 each view) and solves no full positive/negative pair.
Positive probability contrasts 13/32 edges, 14/32 matrix;
mean normalized binary probability contrasts -0.00009939
and -0.00030364 respectively. Both views strictly correct 0/64.
No semantic competence demonstrated; failure is not just format.
Input tokens 25454 edges / 27824 matrix; inference times
116.65 /125.43 s. Constant baseline 50%, exact oracle 100%.

This justifies a falsifiable targeted hypothesis, not automatic
training approval. EQUIV-PILOT01 fresh matched-pair corpus frozen
separately (192/16/64); this diagnostic is consumed, not a future
promotion holdout. Next freeze retention controls and validate
trainer/evaluator, matched exposures, actual adapter delta and
pairwise objective in dry-run tests. Require explicit approval
before any training. Prior SFT collapse makes ordinary LoRA
a necessary control rather than assuming contrastive success.
No main change, paid API or deployment.
