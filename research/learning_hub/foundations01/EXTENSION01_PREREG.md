# EXTENSION01 — preregistered bounded language expansion and open-set rejection
Question: can the active rule learner detect a missing hypothesis and
extend its search without falsely certifying unfamiliar rules?
Keep original three frozen membership checkpoints from COMPOSITION01
artifact 14924271795; no gradient, no new learned operator.
Initial grammar DISCOVERY01 (six ordered relation inputs, NOT/AND/OR/XOR,
minimal expression cost <=5). Only permitted extension: cost <=7,
same operators. Generic bounded expansion, not invention of a language.
48 hidden rules, 12 per stratum, deterministic seed 20261205:
IN cost5 support>=3; EXT minimal cost7 support>=4; FAR independently
sampled five-distinct-variable binary expression trees (AND/OR/XOR),
mask outside cost7, support>=4; NEAR one-bit flips of sampled IN
functions outside cost7. All 48 masks distinct. Near misses explicitly
challenge false certification; no exact target or stratum sent to learner.
Pool one graph per motif, n6; fresh test two graphs per motif at n8 and
n12, independent seeds. Same tasks/graphs across all three checkpoint
seeds and all arms. True labels from exact membership and hidden mask.
Arms fixed cost5, adaptive (cost5 until inconsistent, then cost7 filtered
by ALL previous evidence), expanded cost7 from start, adaptive exact
membership reference. 16 label requests maximum, same order tie-break.
Choose maximal version-space split while multiple hypotheses; when
singleton choose next unused example in seeded random order, continue
until budget or inconsistency. Fixed stops on empty; adaptive expands
once on empty, then stops on empty. Accept only singleton with >=4
additional queried labels consistent after last transition to singleton;
otherwise abstain. Report actual queries, transition, ambiguity,
inconsistency, false acceptance, graph accuracy (abstention wrong),
selective accuracy and exact target recovery. No teacher masks in learner.
Primary adaptive neural: each seed >=10/12 IN exact accepted,
>=8/12 EXT exact accepted, <=2/12 false accepts in EACH FAR and NEAR.
Compare expanded and fixed, neural vs exact; report all failures.
No claim of target absence from finite evidence unless version space
empty; nonempty is not proof. Count search cost candidate evaluations,
not runtime equalization. One prospective test, no tuning after results.
All tests bounded six bits and 12 object labels, oracle interface not
security isolation. No paid API, main modification or promotion.
