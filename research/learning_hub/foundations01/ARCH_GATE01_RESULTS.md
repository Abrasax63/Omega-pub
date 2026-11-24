# ARCH-GATE01 — learned delayed dispatch, contextual gate fails overall

Preregistration 0617288ffb370134950542063ad6a5b24b3430ca.
Implementation fcf43817bf8b3de2d8775cd90d1c284cf6a946d6.
Successful training and separate evaluation jobs:
https://github.com/Abrasax63/Omega-pub/actions/runs/45468336816.
Results verified in CI logs, not independently replayed artifacts.

32 training graphs; five candidate thresholds, two repetitions (320 runs).
Global threshold learned: 512 recursive visits. Density-specific
thresholds: 512 for density >=.25, never (4097) otherwise.
Training costs summed over two groups: 1.234859 always, 1.213958
global, 1.189394 contextual (mean capped CPU seconds per case summed).

32 fresh test graphs, 25 independent references, seven reference limits.
Three repetitions per unique policy; identical policies share runs.
| Policy | Verified | Unverified | Unresolved | Verified capped CPU s | All capped CPU s |
|---|---:|---:|---:|---:|---:|
| Always |25|6|1|0.201995946|1.180959897|
| 32 visits |25|6|1|0.195672173|1.178616624|
| 128 visits |25|6|1|0.191669724|1.172666870|
| 512 visits (learned global) |25|6|1|0.178993512|1.151962684|
| Never |24|3|5|0.517999548|2.524999158|
| Root only |24|3|5|0.520998661|2.529997864|
| Learned density gate |25|3|4|0.173995589|2.180995199|

No mismatches on completed referenced cases. Density gate preserves
every verified completion of always, 3 verified cases with residual
dispatch; reduces verified capped cost 13.86% vs always and 2.79% vs
global (both below required 15%). On 24 jointly verified completed
cases, contextual .039997256 s, global .044995179 s, always
.065004578 s, branch .017999548 s; contextual 2.22x branch (required
<=1.5x). Contextual all-case cost 89.33% above global and three fewer
unverified outputs with three more unresolved cases; these outputs
cannot be credited as independently exact. Primary gate FAIL.
Global delay reduces verified capped cost 11.39% and all-case cost
2.46% relative to always, preserving completion totals. This is a
modest prospective benefit in this run, not a certified general
speedup or a promotion. CPU measurement resolution is coarse.
Two fixed groups were developer-defined, thresholds learned by finite
grid search, exact residual dispatch priority and solver code remain
fixed. No independent neural training or autonomous architecture
invention. No main change, paid API, or activation.

Next discriminating test: local residual-state dispatch with cheap
structural features and a learned action cost model, preserving shared
memo. Separate structural and elimination decisions; charge probe
costs; use counterfactual local training or matched end-to-end search
and independent holdout, compare with simple delayed global policy.
Avoid treating whole-graph density as sufficient or increasing
complexity without a measured benefit.
