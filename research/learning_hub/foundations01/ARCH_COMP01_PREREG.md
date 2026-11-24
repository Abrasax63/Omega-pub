# ARCH-COMP01 — prospective competing vs factorized architecture
Motivation: OBS-COL-06 PR90 found no advantage over classical planning.
Finite history environment: reset and submit three pairs of binary inputs
(6 bits); oracle emits one bit. No direct hidden-state access. This is
bounded history prediction, NOT arbitrary automata or recurrent training.
Fourteen predefined Boolean monomial atoms: 1,x0,x1,x0*x1 (local);
x2,x3,x4,x5,x2*x3,x4*x5 (history); x0*x2,x1*x4,x0*x5,x1*x3 (cross).
All arms have same XOR-composition grammar (2^14 functions). Three
nonexclusive families plus cross compositions; not invented grammar.
96 fresh truth tables, 24 each local-only, history-only (allow constant),
mixed with nonzero local/history/cross, and out-of-catalogue with
one nonzero absent monomial. Seed 20261201, no duplicate truth tables.
No labels/teacher coefficients sent to learner; evaluator independent
full truth table and Möbius transform checks family.
Four policies:
- progressive nested local -> local+history -> all atoms. Interpolate
  from their low-weight monomial inputs, use disjoint challenges (3,3,8)
  drawn from seeded high-weight (>=3) list. Stop provisionally on agreement.
- concurrent flat: exact bitset version space of ALL 2^14 candidates;
  choose unqueried input with maximum balanced split until unique,
  then 8 fresh random challenge inputs.
- network: exact bipartite feature/constraint factorization over GF2;
  eliminate redundant feature rows, select rank-increasing inputs with
  same seeded tie order as flat. Then same 8 fresh random challenge
  inputs. Equivalent split expected for affine candidate spaces; no
  claim of superior query policy. Network is a bounded algebraic graph,
  not free self-reorganization or a trained neural network.
- fixed full basis: interpolate using all 14 monomial inputs, then
  8 high-weight challenges (same seeded order as progressive).
All have at most 28 oracle calls (progressive 14+14, others 14+8),
NOT equal realized budgets: report actual counts and quality. Also
compare flat/network/fixed at identical max 22 and same exact grammar.
Independent full-table reconstruction and evaluation of all 64 inputs,
four history-shift predictions with exogenous next input pairs (all
4^4 sequences for each initial history if candidate accepted; full-table
equality logically implies this, no redundant rollout enumeration).
Primary network: 72/72 in-family exact, no more wrong conditional
acceptances than best full-space comparator, and >=20% reduction
in actual query count OR >=20% end-to-end median CPU time vs BOTH
flat and fixed full design (single process, 3 repetitions, include
initialization allocated across tasks, no target generation time).
Report initialization, per-policy total, per-rep values; no universal
speed claim. Flat/network route parity on same queries is explicit
negative control; no unconditional certificates from partial observations.
If no win, do not promote; archive negative evidence. No LLM, no paid
API, no main change. Teacher design, atoms and graph are developer-
supplied; no evidence of autonomous invention or general intelligence.
