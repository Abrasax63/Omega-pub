# SEPARATOR-GATE01 — bounded discovery with structural evidence
Freeze before implementation. Reuse SEPARATOR01 exact solver and factor
identity; compare direct, shared partition, unrestricted factor, root-only
factor, bounded factor. Root-only permits search only on original mask
when connected and eligible. Bounded allows a root search and recursive
searches only after positive root evidence (separator found), at most
16 searches and 128 candidate component probes globally, including
failed probes; no budget replenishment. For each allowed search compute
the same two BFS layer sets, but skip candidate component traversal
unless both prefix and suffix of the corresponding BFS have >=20%
of current vertices. Candidate order by estimated balance, size, mask.
Stop on global probe budget, use best checked valid separator or
fallback exact branching. BFS effort counted separately, CPU includes
all overhead. Negative root evidence disables search for remainder.
This is hand-coded structural gating, not learning. Compare fixed
control and root-only ablation to identify effect. All same nominal
8192 visits and .8 process CPU seconds, 3 shuffled repetitions.
32 fresh graphs n=24,40,56,72 same eight families, seed 20270137.
20 independent ordered-group transfer references and generic stronger
reference for controls. Report references and coverage separately.
Primary bounded >= verified coverage of direct, partition and factor,
>=15% reduction of verified penalized reward vs best direct/partition,
all-case reward <= best direct/partition, no extra unverified outputs
unless higher verified coverage. Secondary retain >=75% of unrestricted
factor improvement over partition on structured subset if positive;
control verified reward <=105% of partition, no verified coverage loss.
Reward wall+.25*CPU+1 per unresolved; median per case. Report probe
counts, root detection cross-tab by generator family (not correctness
labels), novel verified completions, matched costs, retrospective
oracle headroom. Tests exhaustive n<=4, forced structured separator,
dense negative root, budget cap, zero discrepancy and fail closed.
Same author synthetic families deliberately favor small separators;
no external replication, no neural training, no promotion, no main
change, no paid API.
