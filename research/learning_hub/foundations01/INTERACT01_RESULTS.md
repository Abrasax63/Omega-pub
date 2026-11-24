# INTERACT01 — results
Preregistration 34e418b40f53b5cfcb06f9ce0680c91a079f2426.
Implementation 3dfec0e59684e99d4118f5ed9187fe42fc5e3d28.
Successful CI: https://github.com/Abrasax63/Omega-pub/actions/runs/45436706383.
72 distinct Boolean vector dynamics, 24 affine, 24 quadratic, 24 cubic;
half each transformed by an invertible linear coordinate map.
Three designs, 22 fitting queries + 8 disjoint validation queries per task.
Rank design: affine 24/24, quadratic 24/24, cubic 0/24 exact;
23 cubic candidates refuted, 1 wrong candidate conditionally accepted.
Passive: affine 3/24, quadratic 7/24, cubic 0/24 exact;
21 affine and 17 quadratic underdetermined.
Fixed weight<=2 basis: affine 24/24, quadratic 24/24, cubic 0/24;
21 cubic refuted, 3 wrong candidates conditionally accepted.
All recovered exact laws match five-step rollouts from all 64 states.
Primary in-family criterion passed; promotion gate failed.
Scores from verified CI logs, not independent artifact replay.
Rank design selects independent feature rows without seeing responses,
so this is informative experimental design, not outcome-adaptive policy.
Known quadratic hypothesis grammar and supplied exact solver; learned
coefficients are new, but no invented grammar, neural training or LLM.
Passive fit requires full quadratic rank even for affine teachers;
not a comparison against every possible passive learner.
Validation cannot prove grammar membership; no unconditional certificates.
Next decisive experiment: budget-matched outcome-dependent hypothesis
expansion, with independent tests against fixed cubic design and passive
exploration. Require actual benefit over fixed design, preserve explicit
conditional statuses, test out-of-family teachers. No activation or main change.
