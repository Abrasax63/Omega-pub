# EQUIV-BASE01 — frozen corpus preparation

Preregistration 3f1bcab7454d71115192b5a789e8555feb58fdd1.
Implementation 68062ea2f69251ca5d55e8a2e86eba6ac23ebd9b.
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45483683909.
Freeze job 138763270411 completed successfully. Inference and scoring
not yet confirmed at the time of this record.

96 train / 16 development / 64 diagnostic holdout examples, from
12 / 2 / 4 distinct generator configurations. 88 graph pairs total.
Balanced labels, both feasible past sets distinct with size two;
same graph and anchor set for each positive/negative pair.
Oracle enumerates all feasible future subsets, checks equality
against blocked-mask identity. Exact NetworkX isomorphism screening
within each split in WL-hash buckets; vertex-count ranges disjoint
across splits. This is not an audit of all historical training data
or all possible semantic similarity. Generator conditions on existence
of positive and negative alternatives; not representative of arbitrary
graphs. Twelve configurations are not twelve independently developed
mathematical skills.

SHA256 of frozen files, from successful freeze log:
- train.json 5aa69513411607ca5cc1bc1be490bebb88109a6d3f3c84b30b1ffcd94506c37e
- dev.json 4a6cfa1674b3874e375486710cca55ce960d83aefcb8934b6dbe0e0da9ea04a1
- labels.json 1855ce3d418c43e9ae9a33dd383c410a72d5a6f90befe7f62092b0f94c3f2e9b
- questions.json 2ed1e948cf9e5a762ce32c3ca78273bd40d000baad9aa3e491bbb38266052d25

Artifact metadata, not independent byte replay:
- equiv-corpus 14963331646 sha256:44d0c3316b6332ae34ae964b25a1bb565b9734341df456b6782c68dd20d25136
- equiv-questions 14963646662 sha256:31fa33ccd5070ab0aa524ce12f108aafeafee18f09a7285b196220952c884745
- equiv-labels 14964310501 sha256:ed4c7c410f5caf6ecd5e0c23bf45ba3dcede991acf6d03c057b38306d05670cf
Metadata expiry 2027-02-22. Deterministic generator and pinned
NetworkX 3.4.2 retained; artifact bytes not yet archived durably.

Baseline: pinned SmolLM2-135M-Instruct, inference only; no adapter,
no training. The baseline diagnostic holdout must not become a
promotion holdout after inspection. Need fresh held-out graphs and
a preregistered, controlled weight-update protocol, including
retention and constant-answer collapse checks, before seeking
explicit authorization. Current status: corpus prepared, baseline
pending, NO-GO for weight update. No main change or paid API.
