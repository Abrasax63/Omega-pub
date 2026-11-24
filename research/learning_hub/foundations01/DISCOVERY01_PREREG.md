# DISCOVERY01 — prospective bounded program induction
Purpose: discover an unknown rule from labeled graph examples, without
supplying target formula, selected relations, or decomposition. This is
symbolic search using learned neural membership, not autonomous invention
of a language or a new neural optimizer.
Input: three distinct named vertices and all six possible directed
non-loop queries between them. Frozen membership from all three
COMPOSITION01 frozen checkpoints (artifact 14924271795, verify ZIP and
individual hashes). Search grammar: six generic Boolean inputs, NOT,
AND, OR, XOR. Enumerate all distinct semantic functions of expression
cost <=5 (leaf cost 1, each operator cost 1), canonical representative
chosen deterministically. Hidden teacher samples 24 distinct cost-5
functions depending on at least 3 inputs (seed 20261204); learner gets
only labels at selected examples, not truth table or expression.
For each task pool 64 graphs, one per six-edge motif, size 6 random
background and query labels. Test each motif on new size 8 and 12 graphs
(two families each); labels exact teacher evaluation. Learner can observe
all pool graphs and neural membership predictions, not motif IDs.
Arms: active version-space query selection maximizing min positive/negative
candidate count, passive random query selection, active exact membership
reference (not neural). Same 12 label budget each; tie-break by seeded
order; select lowest-cost remaining semantic function, abstain if none.
Report discovery exactness on all 64 latent motifs (external scorer),
graph predictions, label queries used, residual version space, number
of tasks with unique semantic rule, all failure cases. No claims of
generalization beyond grammar, 12 identifiers, supplied three-vertex
scope or label oracle. Primary active neural: >=18/24 exact rule
recoveries for each seed and >=90% graph accuracy per seed; compare
passive under equal label budget. If failed, record; no tuning.
Oracle/search code separation at function interface, not secure isolation.
No weight updates, no paid API or main modification.
