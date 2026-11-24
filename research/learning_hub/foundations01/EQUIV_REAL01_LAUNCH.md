# EQUIV-REAL01 — authorized launch, one-seed exploratory pilot

User explicitly approved the three-adapter training pilot in chat on
2026-11-24, after EQUIV-RUNNER01 miniature validation. No general
training or deployment authorization. Same frozen corpus, objectives,
seed, model revision, 192 updates per arm, fixed test thresholds.
Separate standard ubuntu-latest public-repository jobs for freeze,
training, baseline inference, adapted inference, scoring. Train only
gets train/dev/trace manifest, inference only questions and its adapter,
scoring only labels and predictions/adapter manifests. Standard CPU
compute free under GitHub public repository policy; account storage
allowance not inspectable here, artifacts retention minimized to one
day, no paid API or larger runner. Artifacts must be archived promptly
if needed; do not claim indefinite persistence. Training job timeout
180 minutes, inference 45, fail-fast false. One shot push gated to
parent 5dea2ea48c6b767f5c5937df1faaa803d8d00e5d and first run attempt, no automatic training on
later commits; no automatic retries. Launcher adds progress logs,
finite adapter delta check, score logging to validated runner.
Matched exposure digest, input/padded tokens, update count and
revision verified before score. Full model runtime/availability
unverified before launch; any failure remains a failure, not a score.
No main change, promotion or overwriting existing adapters.
