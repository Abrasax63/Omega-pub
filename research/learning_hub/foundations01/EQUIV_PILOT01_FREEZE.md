# EQUIV-PILOT01 — verified matched-pair corpus freeze

Preregistration 707e81ea12606949b7f0978a84f4f099f6db7acb.
Implementation 55f9420ea825850946a98fadfcd7855bb9bf6e45.
Successful freeze https://github.com/Abrasax63/Omega-pub/actions/runs/45484343717
(job 138765585356); teacher integration and offline hub also green.

192 training, 16 development, 64 reserved examples (136 distinct
graph pairs); 12/2/4 generator configurations. All pairs balanced,
same anchor, graph, set cardinalities, selected overlap and blocked
future cardinality. Positive blocked set equals anchor, negative
differs by membership. Exhaustive extension enumeration agrees
with blocked-mask oracle on all examples. Exact within-split
isomorphism screening; vertex-count ranges disjoint across splits
and BASE01 diagnostic holdout. Twelve generator configurations
are not twelve independent mathematical skills; no historical
corpus-wide contamination audit. Synthetic, public generator,
not externally secret or representative of arbitrary graphs.

Frozen SHA256:
train.json 5dc05b88010d320134f8a9547135875a9c23e5d6bb6b8f7ea896a2820d302947
dev.json cf43023061c3c73f4e83917a98637c9e6a76d66d3380a06adce8b59d9ae5fa6e
questions.json 6c8312439e8106b22c7350a68a5d8c9ce687a03d53702034b9ba0b6cda22c45f
labels.json 886a1d3f860487f4d1bd391e572dc8155d9b269768374422e7157663e9f8f0ae
Artifacts (metadata checked, not independent byte replay):
14964590118 train/dev sha256:547fc3ae98866cb539b7ed8435d2a96b2797a1757b99d89907e80e2a0d7481fd
14964500304 questions/manifest sha256:18cca0a247375131a0cb56b9f4035d1ba2f70dbd87f63593b83817ff3771bdb7
14962268313 labels sha256:daf9707e51cc04b75a76ea27f44a887c2fc12bcb042cd0e7d2df117970138919
Expiry 2027-02-22. Pinned generator retained.

Training readiness: no weight update authorized or started. BASE01
real frozen inference still pending at last inspection. Proposed
matched ordinary/contrastive LoRA design preregistered, but trainer
and evaluator interfaces and independent retention corpus not yet
validated. NO-GO until these and baseline checked; explicit user
approval required. No main change or paid API.
