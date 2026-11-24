# STRUCTURE01 — prospective small neural structural encoder
Following failed 135M LoRA and 360M zero-shot screening, test a different
representation and inductive bias; do not interpret as a causal
comparison with the language models. Sources:
https://arxiv.org/abs/1905.13211 (algorithmic alignment);
https://proceedings.mlr.press/v198/ibarz22a.html (generalist learner);
https://papers.nips.cc/paper_files/paper/2024/hash/8f395480c04ac6dfb2c2326a639df88e-Abstract-Conference.html
(specialized graph tokenization; different tasks and training regimes).
Test learned edge membership from scratch, not symbolic lookup.
Inputs: list of all directed edges as two one-hot endpoint identities
(vocabulary 12); separate query endpoints in same encoding. No adjacency
lookup, equality-to-query feature, answer, or filtered edge list.
Shared edge MLP, masked max pooling, classifier on pooled feature plus
query. Matched arms: query-conditioned edge MLP receives query vector
on every edge; control receives zero vector there, query available to
same final head. Same shape, parameter count, initial seed, training
data, BCE, AdamW lr .003, 256 updates, batch 16 pairs, three seeds
11,22,33. 2048 fresh train pairs/seed reused twice, node count 4..6,
density .2..8, distinct query endpoints, random node labels, edge order.
Evaluation on independently generated size8 and size12, 128 pairs per
size per seed, plus density .05/.95 stress (64 pairs at size8 for each).
No overlap in graph sizes. Train label exactly toggle queried edge.
Fixed test seeds independent of model initialization. Record accuracy,
both endpoints correct, per-class rates, relabel/reorder invariance
(optional), train/test loss, parameter count, elapsed CPU and weights.
Primary pass: each of 3 seeds conditioned >=90% accuracy and >=80%
both endpoints at each OOD size; compare matched control, report all
seeds and failures. Exact solver 100% reference, constant 50%,0 pairs.
Not a reproduction of cited paper, not general reasoning or natural
language parsing; only structured membership. No paid API/main change.
No tuning after viewing test. If failure, archive; if success, fresh
composition tests (path length2/transitivity) before integration.
