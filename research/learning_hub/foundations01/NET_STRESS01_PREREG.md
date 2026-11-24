# NET-STRESS01 — nonlinear relational constraint network and scaling
Extend ARCH-COMP01's exact factorized network from affine GF2 observations
to general finite Boolean relations on pairs. This is a new bounded
symbolic inference prototype, not neural learning or self-generated rules.
Each world provides labeled variables and local observations (XOR, AND,
OR, implication, unary pins); infer exact compatible assignment count
and number with variable 0=1; predict a bit only when forced. Use exact
factor variable elimination, with min-fill ordering vs fixed numerical
ordering. Same constraints, no teacher labels or planted assignment
passed to inference. Budget: at most 2^16 entries in any single factor;
reject before allocating above limit, never guess on resource limit.
Record peak table entries, elimination width, time, exact/unknown status.
Independent references: exhaustive enumeration n=8,12,16 (12 cases
each: four paths, four rings, four sparse random graphs); independently
implemented path/ring transfer matrix for n=32,64,128 (8 each, balanced
path/ring, random label permutation); grid row transfer for side 4,6,8
(4 each, random label permutation). All planted observations generated
from random assignment, with deliberate contradictions on alternating
cases by adding opposite unary pins (trivial contradiction control);
additional nonlocal contradiction cycle of XOR equalities plus odd
parity at n=8,32,128 (all local factors satisfiable). Dense complete
graphs n=18,24, mixed AND/XOR, planted, cap stress: expected abstention
unless exact elimination finishes; independent reference not required
on cap abstentions. Seed 20261207; no tuning on output.
Reference counts including forced-bit query must agree for every
completed case, no false forced bits, no invalid allocations, reject
nonlocal contradictions exactly. Require min-fill complete all path,
ring and grid cases within budget; compare fixed order and direct
small enumeration. Report exact sizes, actual timing and cap failure,
no speedup claim outside measured environment. A single run timing,
not statistical benchmark. No main change, paid API, or autonomous
runtime activation. No claim of arbitrary nonlinear learning.
