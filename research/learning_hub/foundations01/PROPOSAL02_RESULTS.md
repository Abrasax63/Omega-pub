# PROPOSAL-02 — actual result (24 November 2026)
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45382645664 : technical success.
Artifact https://github.com/Abrasax63/Omega-pub/actions/runs/45382645664/artifacts/14915191253
source c1f375dda6bb66da3ee6ce7d2ea727718330a434. 32 real generations, frozen
SmolLM2-135M. F 0/16 syntax-valid, G 16/16 valid, 13 unique marked graphs,
12 unique graphs, 3 duplicates. Motifs 000..111: [1,0,2,1,5,0,0,4].
Neither arm meets preregistered feasibility. G syntax validity is enforced.
F/G input tokens 2176/2176, output 484/192, inference 24.477/57.007 s.
G fewer output tokens but more CPU time (implementation recomputes context).
Archive SHA256 8c40d096087c89f87abedf872abf62b1c0cbce379e95fbe6a7883e2b9b9d3498
raw.jsonl SHA256 738638c5d2b4d7c864d7fae5ae7174ad872ee1b86892f2163efeb502a29f962a.
Independent local Python reconstruction from original archive: all 32 raw
hashes, seed pairs, token counts, file hash, valid counts, canonical graph
and marked-graph counts, motif totals agree. Canonical keys used adjacency
strings, independent of original integer-mask keys. No token decoding
authentication beyond archive and execution provenance.

## Post-hoc mechanism, not independent confirmation
All 16 G triples repeat at least one vertex. 15 have x=y or y=z, making
xy AND yz AND NOT xz impossible irrespective of edges. Remaining triple
101 has x=z but is not a violation. G total 73 ones in 144 adjacency bits.
Mean allowed probability mass over 192 choices 0.73249; mean first-choice
mass 0.06058. Grammar is strong intervention, especially at first token.
Uniform independent reference: expected unique 15.9482/16, probability of
zero violations (17/18)^16=0.400703, probability all triples have a
repeated vertex (7/9)^16=0.0179345. These are descriptive post-hoc comparisons,
not preregistered significance tests; zero violations alone is not unusual.
No claim of mathematical incapacity from this single small diagnostic.
No gradients, no training corpus admitted, no holdout. Do not recycle
these cases as independent evidence.

## Decision
PROPOSAL-03 fixes queried triple to ABC to remove triple selection as a
confound; all nine graph bits remain model-chosen. Compare neutral versus
targeted requests and uniform control. Then decide whether useful targeted
exercise production is plausible; supervised atomic training can proceed
as a separate experiment, not a substitute for the self-generated arm.
