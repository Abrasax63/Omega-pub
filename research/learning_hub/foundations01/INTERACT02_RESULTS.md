# INTERACT02 — decision: do not promote
Pre-registration 22b0e43d73aa0688411cb458a60d9c1c1dbac3ff.
First run 45437222959 failed during aggregation (zero-count key lost);
minimal correction d8b345e8e6698c20232ffceae0495a86b2bee05e retained
zeros, without altering experiment or threshold.
Successful run https://github.com/Abrasax63/Omega-pub/actions/runs/45437319592.
Verified CI log results, no local artifact replay.
96 new teachers, 24 each of degrees 1..4 (degree independently checked),
half linearly conjugated. Four methods share maximum 62 queries;
actual queries differ. Exact table recovery / incorrect conditional
candidate / total queries:
fixed1 24/96 / 0 / 2592
fixed2 48/96 / 1 / 4032
fixed3 72/96 / 0 / 5952
adaptive 72/96 / 1 / 4076
All exact table recoveries pass all 64 five-step rollouts.
Adaptive saves 31.5188% queries relative to fixed3, exact in-family
recovery 72/72 for both. Adaptive rejects 23/24 quartic teachers vs
24/24 fixed3; one quartic teacher prematurely accepted at degree2
after 34 queries. Gate FAIL: accuracy and cost conditions met, safety
condition not met. Retain fixed3 as reference; do not integrate the
adaptive policy. All candidate statuses conditional, including fixed3;
finite sampled agreement cannot certify membership in unknown family.
Fixed3 has 62 observations and cannot prove arbitrary behavior on
the remaining two states. This is outcome-triggered degree expansion
within developer-defined nested grammar, not autonomous invention of
representation, neural learning or general scientific competence.
No main change or paid API.
