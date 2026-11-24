# SEPARATOR01 — exact conditional component factorization
Freeze before implementation. One original-mask exact recursive engine,
same local specialist policy (4,8,512), global 8192 recursive visits
and .8 process CPU seconds, including separator discovery and factors.
On connected residual >=16 vertices, after existing structural solver
and before width-3 elimination, find small separators by BFS layers
from minimum-degree vertex and a farthest vertex. Only layers of size
1..3 whose removal leaves >=2 components and largest <=80% of residual
size. Choose minimum largest component then separator size then mask.
No supplied separator or family labels at runtime. Compare identical
recursive baseline (no separator), separator conditioning (sum over
independent separator assignments, recurse on full residual), and
separator factorization (sum of products of residual components with
local exact factor memo across assignments; global exact memo retained).
Also compare existing REORG01 shared partition with same nominal caps.
Only one CPU process, no training. Count all probes, visits, factor
requests/hits, accepted separators, maximum component, wall and CPU.
32 new graphs n=24,40,56,72, eight families seed 20270135: five
strip/chain families (cliques linked by bridges, narrow grid strip,
random blocks linked by bridges, alternating small separator groups
and dense blocks, random dense blocks with sparse neighboring links),
three controls (dense random, sparse random, random communities).
Independent transfer DP over known ordered groups for five structured
families (not given to solver); generic stronger_reference for controls.
No reference claims when limit reached. Three shuffled repetitions.
Reward wall+.25*CPU+1 if unresolved, sum per-case medians.
Primary factorized arm >= verified coverage of all controls, >=15%
lower verified reward than no-separator and shared partition, <= their
best all-case reward, no extra unverified unless higher verified
coverage; at least one verified case using separator factors. Secondary
factorized vs conditioning: >=15% lower verified reward without
coverage loss. Report family split, matched cases, CPU overhead,
novel verified resolutions, and reference availability. Exhaustive
n<=4 graph checks (all valid forced separator masks with >=2 components),
transfer reference vs brute force; forced eligible separator on
bridge graph; budget exhaustion fails closed. No main change, paid
API, automatic promotion, or archive deletion. Same author; structured
cohort deliberately favors small separators; not broad generality.
