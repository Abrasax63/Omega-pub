# SEPARATOR-VALUE01 — cheap exact BFS cuts and cost-sensitive activation
Freeze before implementation. New hypothesis: BFS layers already certify
that prefix and suffix have no cross edges; use those two sides directly
as factors (they need not be connected), avoiding candidate component
traversal. Compare direct, shared partition, previous open128, cheap cut
(no value gate), cheap cut plus value gate. All same nominal 8192
recursive visits and .8 process CPU seconds. All discovery included.
Cheap cut: two BFS origins as before; width 1..3, prefix/suffix each
>=20% of residual size. Choose minimum max side size, then width, then
mask. Use exact conditional sum of products with local factor memo.
No component probes to select cuts; count BFS vertices, candidates,
factor requests, reuse. Value gate (hand-designed, not learned): skip
search if average degree > 8 or residual size<16; after candidate
discovery enumerate unique residual factor masks across separator
assignments, score uncached work sum(1+2**ceil(size/4)) plus number
of factor requests; compare to same proxy for max-degree binary
branch (two distinct children, count request costs). Accept if cut
score <= .75*branch score. Existing exact memo recognized in both.
Charge all feature and score work; no speculative solves. Up to
128 searches per root problem, no permanent root veto. All new arms
check correctness of BFS partition by construction; verify no cross
edges in tests; no runtime family labels.
Fresh 40 graphs n=24,40,56,72 seed 20270141: prior 5 structured
and 3 random families plus two new controls per size: chain of groups
of width 8 with sparse random intergroup edges (known transfer DP),
and universal apex over chain of 4-cliques (transfer+1 reference).
Groups not passed to solver. Use same cohort seed for old families;
new controls separate seed 20270142. Three shuffled repetitions.
Primary predesignated value gate >= verified coverage of direct,
partition and open128, >=15% lower verified reward than best of
these and all-case reward <= best, no extra unverified unless
greater verified coverage. Secondary cheap cut vs open128:
>=15% lower verified reward, no verified loss; value gate vs cheap
cut measured separately. Report by family, all/verified reward,
retrospective fixed and all-arm oracle, novel verified completions.
Reward wall+.25*CPU+1 if unresolved, sum medians. Exhaustive n<=4
BFS cut identity on every connected graph with valid layers (including
relaxed width/balance solely in test), forced positive/negative gate
fixtures, cap failure. No external replication; nominal CPU not hard
OS quota, same author synthetic cohort; not autonomous learning.
No main change, paid API, promotion or deletion.
