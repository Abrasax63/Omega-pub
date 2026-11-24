# MEMORY-ARCH01 — scoped semantic index wins, destructive merge refuted

Preregistration c30e0dcd47bea3ba1cbf2d8da0ef21ff29ee7ecb.
Implementation d496dfbd96e8b9a8dd20193a15978212c2c48327.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45456694021.
Verified job logs, not independent artifact replay.

861 entries: 425 reduced words, 425 inverse-pair redundant variants,
11 archived definitions. Original 42 evidence records replayed at each
context; archive digest unchanged. Context sequence 5,7,11,17,5;
SM and transitive archived dependents quarantined at 11 and 17, explicit
return to original eligibility at 5. Flat synthetic entries do not
inherit provenance dependencies from separately named archive entries.
Four builds and one cache reuse in safe indexed arms.

186 queries rather than intended 200: p=5 has 117 of 120 possible
permutations in the library, so only three distinct negatives exist
per visit instead of ten. Each context has 30 positive queries; total
150 positives, 36 negatives, including 30 deliberately split-equivalence
targets. No within-context duplicate queries.

| Architecture | Exact canonical responses | False misses | Primitive applications including builds | Signature work units |
|---|---:|---:|---:|---:|
| Raw exhaustive scan |186/186|0|6936470|1485050|
| Exact bucket index |186/186|0|160324|36058|
| Global destructive merge (negative control) |127/186|59|34959|10687|
| Scoped reversible quotient |186/186|0|160324|36058|

No false matches or noncanonical responses. Global merge loses 59 of
150 positive queries (13 at p=7,20 at p=11,26 at p=17). This refutes
treating exact finite-domain equivalence as context-independent.
The number of distinct classes changes 117 -> 203 -> 316 -> 333 -> 117.
All archive evidence and original digest preserved. Scoped quotient
and exact index have identical charged evaluation work; quotient adds
a reverse map and cached canonical representatives. No demonstrated
advantage over simple index, nor measured RAM reduction.
97.69% fewer charged primitive applications than exhaustive scan,
including four builds; 97.57% fewer modeled signature units.
For a fresh context, one exhaustive scan costs the same primitive
applications as building the safe index, subsequent queries amortize
construction. Actual timings descriptive (scan .5464 s, index .01405 s,
quotient .01439 s); excludes reference generation and archive verification,
not total deployment cost. Global merge time excludes initial global
construction, so not comparable. Signature unit model is not a CPU
instruction count and omits bucket ranking, storage and hashing overhead.
Both safe index and quotient pass tested safety; quotient passes
utility vs scan, no incremental gain vs index. Prefer simplest exact
bucket index, retain optional reverse map for explanation/audit only.
No claim to implement egg/equality saturation, general mathematical
equivalence, approximate/partial retrieval, learned memory, or new
autonomous competence. Test uses full finite permutation tables and
deliberately redundant synthetic library. Quarantine evaluated by
scoped eligibility, not new independent storage boundary.
Next decisive test: incomplete observations, candidate-set indexing,
explicit ambiguity/abstention, distinguishing queries under budget,
and out-of-library targets. No main changes, physical deletion,
paid API, or activation.
