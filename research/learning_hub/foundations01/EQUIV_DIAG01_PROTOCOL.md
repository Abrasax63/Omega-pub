# EQUIV-DIAG01 — diagnostic isolé avant tout nouvel entraînement

Status: implementation and synthetic core self-test only. No inference, no
weight updates, no promotion. Base: 6fdd50b04d363b20fe2c6f06454045c8ef6cf2e0.
Prior evidence: EQUIV_REAL01_RESULTS.md and MEMBERSHIP_SFT01_RESULTS.md.
The latter already showed constant No after membership SFT; do not simply
repeat that recipe.

## Frozen design
32 distinct uncolored 7-vertex graphs (exact canonicalization by 7! permutations).
Each graph has a feasible pair of past sets with equal blocked masks and a
matched unequal alternative, same mask cardinality and same selected overlap.
Blocked membership uses one blocked and one unblocked vertex on the same graph
and same selected past. Direct adjacency labels cross-checked against independent
singleton feasibility; equality cross-checked via exhaustive future subsets.
Vertex names and presentation order randomized; question order randomized.
7 groups of 64 prompts (448 total per checkpoint):
- membership, edges and matrix (balanced Yes/No);
- two-mask reconstruction, edges and matrix (balanced equal/unequal true masks);
- end-to-end equivalence, edges and matrix;
- equality of two explicitly supplied correct masks (assisted diagnostic).
No labels, scores, IDs, pair indices, model-generated previous answers or
intermediate traces are to be included in prompts. Each prompt starts a fresh
context. Inference runner must consume ONLY the prompt field, preserve exact raw
output and record ID and SHA-256 of the actual prompt. The explicit-mask task is
a separate intervention, not an autonomous equivalence test. All 448 predictions
per arm required, invalid outputs count wrong, no discretionary retries.
Evaluate frozen original base and all three archived REAL01 adapters separately
(1792 responses if all four available). Same base revision, prompt template,
decoding policy and token budget across arms within each task; log model and
adapter digests, input tokens, output tokens, truncation, raw response. Check
context length before running; stop rather than truncate inputs. Do not select
an adapter using this diagnostic. No paid API. No training.

## Gates (prospective, per group)
At least 48/64 exact, 24/32 in each class and 20/32 complete matched pairs.
For reconstruction, both unordered sets must be exact, no duplicates or
unknown names, classes denote the true equal/unequal mask relation.
For binary groups report Yes, No and invalid counts separately; score exact
raw responses, not just binary forced choice. Record binary probability margins
separately if available; not used for these gates.
Interpret each failed prerequisite separately: membership fail suggests a
local relation/format bottleneck; membership pass + reconstruction fail suggests
aggregation/structured output; reconstruction pass + explicit comparison fail
suggests comparison/format; all elementary gates pass + end-to-end fail suggests
composition or representation integration. Multiple failures remain
underdetermined. Assistance changes input difficulty and is not proof of cause.
Compare edges vs matrix separately; do not pool away failures. No competence or
generalization claim from this small diagnostic alone.

## Reproduction
Node 22, no dependencies. Run:
```sh
node research/learning_hub/foundations01/equiv_diag01.cjs selftest
node research/learning_hub/foundations01/equiv_diag01.cjs freeze NEW_NONZERO_UINT32_SEED /path/to/new-dir
node research/learning_hub/foundations01/equiv_diag01.cjs score /path/to/new-dir predictions.json
```
Freeze one fresh seed before model inference; do not use self-test seed.
Separate questions from labels before inference, keep manifests and raw
predictions; do not commit frozen diagnostic labels. Predictions are a JSON
array of {id,raw,prompt_sha256}; score once per arm.
Do not consume reserved CUMULATIVE01 data. Seven-vertex graphs differ in size
from the known EQUIV-PILOT01 and CUMULATIVE01 splits; overlap with other historical
atomic corpora has not been checked. Public generator is not an independently
secret evaluation. This is a small, easier diagnostic, not a new holdout for
promotion. No inference runner integrated; Node CLI filesystem path not tested
in the core self-test, and no CI claimed. Core test executed before commit:
448 prompts, 32 graphs, seven groups, perfect oracle fixture, four constant
controls rejected, three malformed/coverage controls rejected, deterministic
generation, duplicate mask names rejected. No model calls.

## Next decision
Do not train until real diagnostic scores and failures have been reviewed.
Then select the smallest failed operation for a separate preregistration and
use fresh test data plus replay of genuinely validated skills. If no skill
passes, do not describe replay as retention of competence.
