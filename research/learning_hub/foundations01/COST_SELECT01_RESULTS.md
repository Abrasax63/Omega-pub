# COST-SELECT01 result
Run https://github.com/Abrasax63/Omega-pub/actions/runs/45422364070
completed successfully. Frozen OLS coefficients [1.6283681137786727,
-0.7115813554058925,-0.6031863093416728]. 22 calibration cases, 28
disjoint holdout cases, five paired timing repeats per admissible method.
Independent circular-list reference: 28/28 exact, zero unsafe choices.
Sum of holdout per-case median solve seconds:
direct .148958667; always-valid .080754691; simple .079682682;
learned .080788230; posthoc fastest .079560541.
Regrets respectively 1.872268,1.015009,1.001535,1.015431,1.
Learned fails strict preregistered aggregate comparison with always-valid;
preferred simple (slack>=2), learned not promoted. Simple saves ~46.5%
of aggregate measured median cost versus direct, ~1.37% versus learned;
small differences are not statistically established. One environment,
small grid, no cross-family or hardware claim. No neural weight updates.
Integration: cost_policy01 wraps original typed validity guard, keeps
all other contracts unchanged, never forces an inadmissible reduction.
Historical benchmark functions unchanged. A fresh policy regression
suite checks entire allowed R90 grid and selected exact boundaries.
This is experimental integration only, not autonomous runtime activation.
