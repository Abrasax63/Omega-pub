# LEARN-POLICY02 — positive control for reward-only learning
Reuse unchanged solve/reference/cohort from LEARN-POLICY01 at frozen
commit 6088a0067d849f5081ff985fbee9a7725f76fe8f. Train on original 24
training graphs; fresh held-out seed 20261215, 48 graphs as before
(16,20,24,32,48,64; four random densities, four community variants).
Three weak initial policies: minimum degree, neighbor degree, zero
vector (index tie). For each, 40 Gaussian proposals (sigma .65) with
strict improvement acceptance, compared to 40 independent Gaussian
proposals centered on zero (sigma .65), keep best including start.
Seed 20261216+start index; paired noise draws between methods.
Strong fixed max-degree policy is a separate benchmark, not supplied
as candidate in training. Reward only capped visits, count validation
separate. Same 41 evaluations per arm including initial; report actual
training visits, accepted updates and frozen weights. Reload checkpoint
in separate job, source hashes checked, no holdout feedback.
Primary positive control: >=2 of 3 hill-climb policies reduce paired
verified holdout visits by >=20% vs their own start, no fewer verified
completions or extra unverified outputs; all verified counts exact.
Compare hill-climb to random search and strong incumbent separately,
using paired verified intersections and completion. Claim advantage
over random or strong only if >=15% visit reduction and no worse
verified completion/unverified output in >=2 of 3 comparisons.
No candidate selection on holdout. Independent reference may abstain.
This is parameter learning for a supplied exact solver, not autonomous
mathematical discovery, LLM training or Omega runtime integration.
No main change or paid API. Same author/generator, not external blind.
