# LEARN-CONTEXT01 — learn context-dependent selection, frozen solver
Question: does learning which of a supplied portfolio to use beat the
strong fixed max-degree heuristic, not merely weak initial policies?
Freeze before implementation. Import solve/reference from learn_policy01
unchanged; 4096 visits per solver run. Portfolio: fixed max-degree,
min-degree, neighbor-degree, zero, and three retained hill policies
from POLICY02 (exact weights from verified train log). 7 options.
New graphs: 48 training, 48 holdout, each 8 at n=12,16,20,24,32,48
(training), n=16,20,24,32,48,64 (holdout), one per family per size:
Erdos-Renyi p=.12,.35; two-community; preferential attachment;
random geometric; perturbed grid; near bipartite; hub-and-spokes with
extra edges. Seeds 20261218 and 20261219. Different sizes and graphs,
same author/generator, not external blind. No family labels available
to selector. Features from input only: density, degree coefficient
of variation, triangle clustering, leaf fraction, max-degree fraction,
size. Learn regression of normalized capped cost per portfolio arm
using nearest-neighbor local averaging; k=5, standardized on training
features (zero variance replaced by 1), tie fixed portfolio order.
Training observes all arms' scalar costs only (separate count checks).
Strong comparator fixed max-degree; best global fixed arm chosen on
training only; uniform random selection with 5 fixed seeds; cost-aware
non-contextual fixed mixture not needed as best global arm dominates
in training expected loss. Also compare identical nearest-neighbor
learner with shuffled feature-cost associations (5 seeds, same labels
and budget). No test feedback. Persist training features, scales, costs
and engine hash, reload in separate job. Oracle portfolio lower bound
computed retrospectively on holdout, NOT executable selector.
Count cost = visits if completed else 4097. Primary on independently
verified holdout reference subset: >=15% lower total capped cost vs
max-degree AND best fixed training arm, >= as many verified completions,
no incorrect verified counts, no more unverified outputs than strong.
Secondary compare random and shuffled controls; report all costs,
paired exact visits, larger-size transfer, selector time and training
cost; if oracle headroom <15% no learning claim even if training gain.
Reference from unchanged core, explicit reference limits. One run,
no general speed or autonomous operator discovery claim. No main
changes or paid API. No holdout-based selection or retry.
