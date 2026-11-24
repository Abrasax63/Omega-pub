# LLM-PLAN01 — frozen open-weight proposal experiment
Model Qwen/Qwen2.5-0.5B-Instruct CPU, public revision resolved once by
HfApi and recorded before inference; no training, API inference or paid service.
Test 40 fresh French descriptions (8 per class) and two fresh numeric
payloads each; no exact reuse from TOOLROUTE01/SEMANTIC-IR01. Same author,
not externally blind. Compare frozen IR, NB, keyword, and model.
Model is shown five bounded canonical semantic plan descriptions, no
examples or answers. Two distinct option permutations per question;
select maximal next-token logit among single-token A..E, map to plan.
Also record unconstrained top token, candidate logits and token count.
Agreement arm dispatches only if both permutations select same route,
otherwise abstains. Single-order arm as ablation. This is constrained
plan selection, NOT free plan synthesis, self-training or full semantic
verification. Plans independently checked with existing typed guard;
model does not infer free-form operands, adapters fixed. No gold labels
passed into model inference function. Freeze predictions before scoring.
Use independent math verifier from TOOLROUTE01. Strict exact route and
result, 80 tasks /40 distinct decisions; unsupported false dispatch and
supported abstentions separately. Primary agreement arm >=72/80 exact,
>=14/16 composition, zero unsupported dispatch, >=4 more exact than
frozen IR. Oracle must be 80/80. No tuning after results; failure retained.
Record actual model revision, raw scores and full outputs. CPU-only
GitHub Actions, no main merge or runtime activation.
