# INVARIANT-SELECT01 — benchmark result (2026-11-24)
Protocol 1fce6034c8ef117908657fb15554c96d3d4ac2db; implementation
3ad21f32aabf5b7e0ce67e9356e21d9c1d37e432.
CI https://github.com/Abrasax63/Omega-pub/actions/runs/45420634839
successful; artifact 14933767801 (SHA256 ZIP
eec0f0d9452e12d2453e77b26d7f477e4c31941e03ec9d57f5c5c7241a3a7c2f).
All 15 task comparisons and eight rejection checks passed (CI assertions).
Delta n5: 93750 ->491 orbit representatives; .198165 s vs 2.369057 s
independent exhaustive reference, orbit construction included. Independent
JavaScript recomputation of orbit coverage and two weighted counts:
93750 covered, 491 representatives, all-horizon exact 36630, hidden
internal defects with all Delta empty 12160; matches direct enumeration
and historical source. Global graph n4: 4096->218, .008681 vs .012393 s.
Ordered triple n4: direct fallback, 4096 evaluations; .004554 vs .008849 s.
Rule90 N15 h2: 32768->128, .000389 vs .044902 s. At h6 no reduction:
32768->32768, .217829 vs .091787 s (slower). Five wrapped-cone cases
correctly use direct fallback. No measured universal speedup: differing
implementations, single CI timing, no separate repeated timing study.
The next correction should distinguish admissibility from profitability
and prefer direct when cone width equals N, then benchmark near boundary.
Selector covers only four typed task contracts; no semantic automatic
search of entire library or proof discovery. No new model training,
main change or promotion. The result digest binds declared outcome and
scope but is not a proof checker or oracle authentication. Comparisons
are in finite domains. Runtime integration still pending.
