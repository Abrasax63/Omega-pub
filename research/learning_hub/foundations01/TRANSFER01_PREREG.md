# TRANSFER01 — discovered boundary-state representation
Freeze before implementation. Exact independent-set counting.
Discover order from graph only: for each connected component BFS from
min-degree vertex and a farthest vertex, choose order minimizing
maximum live past frontier, deterministic ties. Process components
consecutively. No generator labels. Compare explicit selected-live-
past state DP, compressed future-blocked-mask state DP (same order),
compressed hybrid (if predicted maximum live frontier >12 use original
direct solver with remaining CPU; otherwise compressed DP), generic
min-fill variable elimination hybrid (width>12 or predicted >8192
output rows -> original direct fallback, all planning charged),
existing shared partition, existing direct. Explicit/compact DP
process vertex in chosen order: omit or include if allowed; exact
merge equal states, discard expired boundary information. Compressed
state records only future vertices prohibited by earlier selections.
No state approximation or loss; no learning, no persistent cross-graph
cache. Conditional relations retain exact counts; test reuse of prefix
vector for multiple suffix boundary queries on small graphs.
Global nominal .8 process CPU s including order/planning, 8192 work
units (recursive visits for baselines, processed states for transfer,
output table rows for elimination; not equivalent unit costs).
Pure transfer fails closed at cap; no speculative restart after DP
begins. Hybrid fallback only before table building. CPU remaining
passed to original solver; reject measured total over cap.
40 fresh graphs n=24,40,56,72 10 prior families with new seeds
20270145/20270146; 8 additional wider or non-chain structured cases
at n=40,72: width-5 and width-9 strips, binary tree of cliques linked
by bridges, cycle of width-3 groups (48 total). Independent reference
for chains from transfer oracle, apex via transfer+1, for tree of
cliques via explicit block-tree message DP, cycle via conditioning
first group then transfer; random controls generic reference.
Three shuffled repetitions. Report coverage, wall, CPU, penalized
reward wall+.25*CPU+1 per unresolved, summed case medians, state
counts, merges, widths, fallback, subgroup, oracle headroom.
Primary compressed hybrid >= verified coverage of direct, partition,
generic min-fill hybrid; >=15% lower verified reward than best
of these, all-case reward <= best, no extra unverified unless
higher verified coverage. Secondary compact vs explicit >=15%
lower verified reward, no verified loss, at least one exact merge
of different selected-past states in same blocked state. Report
matched successful costs, pure vs fallback, novel verified recovery.
Exhaustive n<=4 all modes versus brute; conditioned prefix relation
reuse test, compare to brute on n<=6; forced cap failure, width
fallback, validate order and edge constraints. Same synthetic author,
no external replication, CPU timer not strict hardware quota.
No paid API, main change, activation, or archive deletion.
