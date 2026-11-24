# MEMORY-ARCH01 — compare exact retrieval and reversible equivalence
Frozen before implementation. Reuse committed MEMORY_DAG01_ARCHIVE.json
(11 definitions, 42 evidence), verify original trusted hashes via
memory_dag01.verify. Add synthetic stress library: all reduced primitive
words of length 1..4 (425 maximum; actual 425? use enumerated count),
plus deliberately redundant inverse-pair variants of each word and
the eleven archive expansions. Keep distinct word IDs, original
archive unchanged. No learned operators or full egg implementation:
finite semantic equivalence classes, scoped by domain p and quarantine.
Compare four architectures:
A raw scan: evaluate each eligible definition per full-table query.
B exact associative index: one full permutation signature per eligible
definition and context, bucket containing all words, retrieve shortest
then lexical representative.
C globally merged equivalence classes: collapse words by their full
permutation table on p=5, keep shortest representative only, deliberately
unsafe negative control; rebuild lookup for new p using only representatives.
D context-scoped quotient with reversible archive: retain all words and
class membership, build exact signature per context, index one canonical
representative per class with quarantine-aware selection, keep reverse
mapping for witnesses. B and D may be functionally identical: report
that as result, do not assume D beats B. Compare physical/logical index
counts, not measured RAM. C must never activate.
Contexts p=5,7,11,17,5 (return); quarantine after second context removes
the archive definition SM and all its DAG dependents (synthetic flat
words not claiming those dependencies remain legal). Re-enable only in
a separate explicit revision before last context; no destructive delete.
Each context 40 queries: 20 archived signatures sampled uniformly over
distinct eligible signatures, 10 targets from previously equivalent
words that separate on current prime (if fewer fill with fresh hits),
10 negative full permutation tables not present in eligible library.
Seed 20270104. Dedup within each query class where feasible; record
overlap and actual counts. Independent exhaustive reference using
direct primitive evaluator over eligible archive, exact membership
and shortest lexical eligible word. All returned words must reproduce
full target, no false match. Compare false misses and noncanonical
matches, correctness under quarantine, original evidence replay and
archive digest. Charge one primitive application per word letter per
state for index build and scan (full-table evaluation), and one p-entry
signature comparison/hash lookup per query or candidate; report both
units separately, no conflating. Count rebuilds and storage entries,
report actual wall time descriptively. Include index construction in
cost, break-even queries vs scan; explicitly compare cold and warm
costs. Primary safety D and B zero false misses/false matches, exact
canonical word, quarantine and rollback respected, original archive
unchanged. Utility D >=15% fewer charged primitive applications vs A
including rebuilds, compare against B and report lack of distinction
if any. C is a falsification control, not production proposal.
No main change, no paid API, no neural training, no external backup
claim. Scope finite permutations, full observed tables, synthetic
library, not general mathematical equivalence or partial observations.
