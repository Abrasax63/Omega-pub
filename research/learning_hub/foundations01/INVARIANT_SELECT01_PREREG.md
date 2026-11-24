# INVARIANT-SELECT01 — prospective registry-driven reduction
Sources: LIBSTRUCT01 (run 45418274749), historical Delta gluing source and
BR-R90-02. Implement explicit typed contracts, not LLM retrieval or
automatic proof synthesis. Supported tasks: binary-surjective finite
endofunction census (defect-count sequence and ghost triples), global
distinct-triple transitivity violation census for loopless digraphs,
ordered triple violation census, Rule90 Majority histogram.
Only approved contracts may reduce: state/observation conjugacy,
vertex relabeling for global property, local causal cone without wrap.
Ordered fixed query: direct fallback, never use unmarked orbit.
Wrapped cone: direct fallback. Unknown task, invalid parameters or
attempted forced incompatible reduction: reject. No fallback to guessed
semantics. Each result records contract, source, domain, hypotheses,
raw and representative evaluations, multiplicities where relevant,
and outcome digest. Certificate asserts exact computation under explicit
contract, not authenticity or unrestricted arbitrary Boolean teacher.
New tests: all binary surjective endofunctions n=5; all loopless digraphs
n=4 (global and fixed query); Rule90 N=15 h=0..6 with valid cone,
plus wrapped N=3..7 h=3; compare against independent exhaustive paths.
Measure total runtime incl orbit construction and validation separately;
timings empirical, no required speedup. Primary all exact counts/
histograms match, 0 unsupported/unsafe reductions, all mutation tests
pass. Record negative controls and no promotion to main. CPU only.
