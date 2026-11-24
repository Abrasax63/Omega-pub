# LIBSTRUCT01 — reuse of historical structures for certification
2026-11-24. Local exact calculations; not prospectively preregistered,
not autonomous discovery. No neural calls. Sources inspected:
- main tree (58 blobs; 59 tree entries), experimental tree 168 blobs,
  migration PR2 tree at 2f71a6b8ed03914c0b5d308520d30e0133d9e9ad (226 blobs),
  reconciliation PR5 tree at 639dc01ca3ea58c61b075adb9a6d860bf41db7bc (102 blobs).
- research/bricks/INDEX_BRIQUES.md in PR2 cites 85 admissible results
  from SQLite v33, historical prose cites 83; not re-audited here.
- DELTA_H_RECOLLEMENT_INTERNE_2026-09-29.md and BR-R90-02_MAJORITY_WALSH.md
  in the experimental branch; library search also located original R90 audit.
Not a complete source-by-source inventory of the private library; indexes,
trees and selected relevant sources only. No status promotion.

## Exact tests
Local source hashes:
symmetry_audit.py 2e171a35732ba7d5048464375bdc25045a19a8394d644aecb9802ce68bfadd9d
rule90_audit.py 80839826f58aa1fa8cb15a43798b061cad4d95f8e1a3ab2e02d6685729a98a6a
Local JSON hashes:
results.json 01864b29cd0d7b1cff9095f4a0e986d73807079e156d288eda44ecb332c9cde8
rule90_results.json 28900ee0c03f4abacd891500629b9ccea7fd89d74513002a2e7f0906ffaf6a27

1. All surjectively two-colored endofunctions n=2,3,4: 8,162,3584 raw;
   3,15,95 classes under state conjugacy and global observation relabeling.
   Compute Q^h and actual R_h via finite product recurrence until repeat;
   compare full defect-count sequence, all-horizon exactness and count of
   spurious triples against representative. Zero mismatches. Weighted counts
   of all-horizon exact: 8,102,1736; with hidden internal defect: 0,12,408.
   These reproduce historical source counts. 3754 -> 113 evaluations of
   invariant property, 96.99% fewer, not measured wall-time gain:
   canonicalization itself costs work. Proof: under bijective s and rho,
   T'=s T s^-1, pi'=rho pi s^-1; T'^h=s T^h s^-1, Q' and R'_h
   are transported by rho, so Q'^h\R'_h and all words are transported.
   Counts and emptiness invariant. Named word queries require transporting
   the word. Historical counterexample A/B same Q and all Delta empty,
   different W3, e.g. 001 absent in A present in B.
2. All 64 loopless digraphs on 3 vertices -> 16 S3 orbits. Property
   'exists a distinct ordered triple violating transitivity' invariant,
   zero mismatches. FIXED ordered query (0,1,2) incorrectly compressed
   by the same orbit key in 8/64 inputs. Witness edges [(0,2),(1,0)]
   vs [(0,1),(1,2)]: same orbit, query false vs true. Do not compress
   arbitrary unknown Boolean teacher with this symmetry. Use a proven
   invariant global property or transform the query jointly. The latter
   does not reduce the 64 distinct ordered six-bit motifs in general.
3. Rule90 on N-cycle, Majority of three sites at site0, times 0..h.
   Local cone width 2h+3; when N>=width, no wrap in cone and unobserved
   initial bits have exactly 2^(N-width) extensions. This proves histogram
   equality with weighted enumeration of local assignments, not itself
   uniformity. Two computational paths (cyclic bit operations vs
   shrinking list) agree for 40 (N,h) with h=0..4,N=2h+3..14.
   161112 full initial configurations ->12704 local assignments,
   exact histograms equal, all uniform in tested scope. N14,h2:
   16384->128. Outside no-wrap domain reject reduction; no general
   uniformity theorem claimed from finite tests.

## Reuse queue
C4/C5 oriented versus dihedral classes: compare oriented-query
equivariance before quotienting; audit PR5 first.
Finite observable futures: use exact residual automata and distinguish
state conjugacy from behavioral equivalence. Affine restrictions:
use proven elimination/kernel invariants with explicit rank and field.
R90 polynomial factorization: separate algebraic proof from local
enumeration. Words: cyclic rotations with phase-sensitive query transport.
Continuous/PDE and operator closure: defer until executable certificate
contracts and source proofs checked; not equivalent to finite tables.
No promotion from index labels.

## Next integration contract
Each candidate compression must declare domain, target property,
action/quotient, proof or exact verification of preservation, coverage
and multiplicities where applicable, and counterexamples to incorrect
scope. Fail closed when property invariance is not established.
CERTGATE01 unrestricted six-bit lower bound remains unchanged.
Current result is experimental instrument selection and validation,
not an automatic integration into runtime or proof discovery.
