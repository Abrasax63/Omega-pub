# ATOMIC-SFT-PILOT-01 — supplemental diagnostics, before any evaluation score
The actual workflow 45384124691 has frozen its train/eval/question artifacts
and passed 42 offline tests. Independently downloaded train artifact
14915342313, verified SHA256 fc48c56bd5b504720779513f0f841ad17d0545b9f8757cae5a23b36a7213f1c9,
128 labels checked by direct membership, 128 unique graphs by independent
adjacency-string canonicalization, 64 positive, 64 negative, 128 unique IDs.
No evaluation artifact opened in this audit.

Important limitation of the preregistered primary joint threshold:
because exactly half the evaluation examples have motif 110, the constant
four-bit prediction 1101 achieves 32/64 exact joint, reading and decision
scores in each view, while remaining internally consistent. It has zero
joint accuracy on negatives. Uniform draw among the eight logically
consistent four-bit outputs expects 8/64 joint and 32/64 decision; expected
reading is 8/64 and consistency 64/64. Uniform draw among all sixteen strings
expects 4/64 joint. No claim of learning based on format/consistency alone.
The registered >=7 gain over base and both-class improvement remain unchanged.
Report independently as supplemental diagnostics:
- joint vs constant 1101, exact absolute scores and macro-average over motifs;
- fraction of valid outputs and joint accuracy conditional on valid output;
- distinct output strings and prediction frequency, per view;
- same graph correct in both representations, and paired improvement/worsening;
- per-size breakdown and mismatch between reading and decision.
A preregistered gain below the strongest constant predictor may still be
evidence of some task-specific supervised adaptation, but is insufficient
on its own for a claim of structural reasoning. Do not promote.
This diagnostic does not alter the running workflow, datasets or verdict.
It is a prospective analysis note after corpus freeze but before inference.
