# MORPH-LOCAL01 — local cost-aware expansion, cache ablation
Freeze before implementation. Reuse MORPH-DAG01 registry, exact engines,
same graph masks, immutable established plans, same 8192 request / .8
CPU-second caps. Compare binary, fixed multi, local structural, local
cache-aware, direct, shared partition. No new solver or neural training.
At connected residual size>=12 and max degree>=3, evaluate five plans:
binary on each of top 3 degree vertices and two-vertex conditioning
on top1+top2 and top1+top3 (ties index). Exact child masks with integer
multiplicity; costs count unique children, not multiplicities.
Score = sum(1 + 2**ceil(child_size/4)) for unknown child jobs;
known completed child costs 1 in cache-aware only, pending child uses
unknown cost; structural ablation ignores cache. Choose min score,
tie fewer child requests then candidate order. All candidate construction
charged; no speculative solves. At ineligible nodes preserve binary
max degree. Shared exact registry unaffected. Separate probe count,
chosen binary/multi, chosen cached children; no rewriting old plans.
32 fresh graphs n=20,36,56,72 same eight families as MORPH-DAG01,
seed 20270133; three shuffled repeats, stronger_reference with f6
generic mapping. Reward wall+.25*CPU+1 if unresolved, summed medians.
Primary cache-aware >= verified coverage of every control and >=15%
lower verified reward than best of binary/multi/direct/partition AND
structural ablation, <= best all-case reward of those, no extra
unverified unless higher verified coverage; at least one verified
case selecting a completed child. Report retrospective oracle headroom
among fixed arms and all arms, matched costs, new verified recoveries,
and exact work counters. Safety zero discrepancies; completed root
audit, no duplicate accepted expansion or completion; timeout audit
limited as before. Selftests n<=4 exhaustive, conditioned child identity
on all n<=4 graphs for every pair, forced eligible test n=12,
cache changes decision on constructed candidate fixture, cap failure.
No holdout tuning, same synthetic author/generator; request vs visit
units not identical, timer not hardware quota. No main change, paid
API, promotion or archive deletion.
